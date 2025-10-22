import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque

from fastapi import Request, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.utils.logger import logger


class CostLimiter:
    """
    Multi-tier cost limiting system
    
    Tier 1: Session rate limits (in-memory)
    Tier 2: Daily limits (MongoDB)
    Tier 3: Monthly hard cap (MongoDB)
    """
    
    def __init__(self):
        """Initialize cost limiter"""
        # Tier 1: Session tracking (in-memory)
        self.session_requests: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.session_costs: Dict[str, float] = defaultdict(float)
        
        # Cleanup tracking
        self.last_cleanup = time.time()
        self.cleanup_interval = 3600  # 1 hour
        
        # Rate limits from config
        self.session_limit = settings.RATE_LIMIT_SESSION
        self.daily_limit = settings.RATE_LIMIT_DAILY
        self.monthly_limit = settings.RATE_LIMIT_MONTHLY
        
        logger.info(
            f"CostLimiter initialized - "
            f"Session: {self.session_limit}, "
            f"Daily: {self.daily_limit}, "
            f"Monthly: {self.monthly_limit}"
        )
    
    def _cleanup_old_sessions(self):
        """Remove expired session data (hourly cleanup)"""
        current_time = time.time()
        
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - 3600
        expired_sessions = []
        
        for session_id, requests in self.session_requests.items():
            if requests and requests[-1][0] < cutoff_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.session_requests[session_id]
            if session_id in self.session_costs:
                del self.session_costs[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        self.last_cleanup = current_time
    
    def _check_session_limit(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Check Tier 1: Session rate limit"""
        current_time = time.time()
        requests = self.session_requests[session_id]
        
        # Remove requests older than 1 hour
        while requests and current_time - requests[0][0] > 3600:
            requests.popleft()
        
        # Check if limit exceeded
        if len(requests) >= self.session_limit:
            oldest_request = requests[0][0]
            wait_time = int(3600 - (current_time - oldest_request))
            
            return False, (
                f"Rate limit exceeded. You've made {len(requests)} requests "
                f"in the last hour. Please try again in {wait_time // 60} minutes."
            )
        
        return True, None
    
    async def _check_daily_limit(
        self,
        portfolio_id: str,
        db_client: AsyncIOMotorClient
    ) -> Tuple[bool, Optional[str], int]:
        """Check Tier 2: Daily limit"""
        try:
            today = datetime.utcnow().date()
            usage_collection = db_client[settings.MONGODB_DB_NAME]["api_usage"]
            
            usage_doc = await usage_collection.find_one({
                "portfolio_id": portfolio_id,
                "date": today.isoformat()
            })
            
            current_count = usage_doc["request_count"] if usage_doc else 0
            
            if current_count >= self.daily_limit:
                return False, (
                    f"Daily limit reached ({current_count}/{self.daily_limit} requests). "
                    "Please try again tomorrow."
                ), current_count
            
            return True, None, current_count
            
        except Exception as e:
            logger.error(f"Failed to check daily limit: {e}")
            return True, None, 0
    
    async def _check_monthly_limit(
        self,
        portfolio_id: str,
        db_client: AsyncIOMotorClient
    ) -> Tuple[bool, Optional[str], int]:
        """Check Tier 3: Monthly hard cap"""
        try:
            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            usage_collection = db_client[settings.MONGODB_DB_NAME]["api_usage"]
            
            # Aggregate monthly total
            pipeline = [
                {
                    "$match": {
                        "portfolio_id": portfolio_id,
                        "date": {"$gte": month_start.date().isoformat()}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$request_count"}
                    }
                }
            ]
            
            cursor = usage_collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            current_count = result[0]["total"] if result else 0
            
            if current_count >= self.monthly_limit:
                return False, (
                    f"Monthly limit reached ({current_count}/{self.monthly_limit} requests). "
                    "Limit resets on the 1st of next month."
                ), current_count
            
            return True, None, current_count
            
        except Exception as e:
            logger.error(f"Failed to check monthly limit: {e}")
            return True, None, 0
    
    async def check_limits(
        self,
        session_id: str,
        portfolio_id: str,
        db_client: Optional[AsyncIOMotorClient] = None
    ) -> Dict:
        """Check all three tiers of limits"""
        self._cleanup_old_sessions()
        
        # Tier 1: Session limit
        session_allowed, session_error = self._check_session_limit(session_id)
        
        if not session_allowed:
            logger.warning(f"Session limit hit for {session_id}")
            return {
                "allowed": False,
                "tier": "session",
                "error": session_error,
                "limit": self.session_limit
            }
        
        # Tier 2 & 3: Database checks
        if db_client:
            # Check daily limit
            daily_allowed, daily_error, daily_count = await self._check_daily_limit(
                portfolio_id, db_client
            )
            
            if not daily_allowed:
                logger.warning(f"Daily limit hit for portfolio {portfolio_id}")
                return {
                    "allowed": False,
                    "tier": "daily",
                    "error": daily_error,
                    "limit": self.daily_limit,
                    "current": daily_count
                }
            
            # Check monthly limit
            monthly_allowed, monthly_error, monthly_count = await self._check_monthly_limit(
                portfolio_id, db_client
            )
            
            if not monthly_allowed:
                logger.warning(f"Monthly limit hit for portfolio {portfolio_id}")
                return {
                    "allowed": False,
                    "tier": "monthly",
                    "error": monthly_error,
                    "limit": self.monthly_limit,
                    "current": monthly_count
                }
        
        return {
            "allowed": True,
            "tier": None,
            "error": None
        }
    
    def record_request(self, session_id: str, cost: float = 0.0):
        """Record a request for session tracking"""
        current_time = time.time()
        self.session_requests[session_id].append((current_time, cost))
        self.session_costs[session_id] += cost
        
        logger.debug(f"Recorded request for {session_id}: ${cost:.6f}")
    
    async def track_usage(
        self,
        portfolio_id: str,
        cost: float,
        tokens: int,
        db_client: AsyncIOMotorClient
    ):
        """Track usage in MongoDB for daily/monthly limits"""
        try:
            today = datetime.utcnow().date()
            usage_collection = db_client[settings.MONGODB_DB_NAME]["api_usage"]
            
            await usage_collection.update_one(
                {
                    "portfolio_id": portfolio_id,
                    "date": today.isoformat()
                },
                {
                    "$inc": {
                        "request_count": 1,
                        "total_cost": cost,
                        "total_tokens": tokens
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            logger.debug(f"Tracked usage for {portfolio_id}: ${cost:.6f}, {tokens} tokens")
            
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics for a session"""
        requests = self.session_requests.get(session_id, deque())
        total_cost = self.session_costs.get(session_id, 0.0)
        
        return {
            "session_id": session_id,
            "request_count": len(requests),
            "limit": self.session_limit,
            "remaining": self.session_limit - len(requests),
            "total_cost": total_cost
        }


# Singleton instance
_cost_limiter = None


def get_cost_limiter() -> CostLimiter:
    """Get or create CostLimiter singleton"""
    global _cost_limiter
    if _cost_limiter is None:
        _cost_limiter = CostLimiter()
    return _cost_limiter