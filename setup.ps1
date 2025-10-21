Write-Host "AI Portfolio Platform - Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python not found. Please install Python 3.12+" -ForegroundColor Red
    exit 1
}

# Step 1: Create directory structure
Write-Host ""
Write-Host "Creating directory structure..." -ForegroundColor Yellow

$directories = @(
    "backend\app\core",
    "backend\app\models",
    "backend\app\services",
    "backend\app\api",
    "backend\app\middleware",
    "backend\app\utils",
    "backend\tests",
    "backend\scripts",
    "backend\logs",
    "frontend\src\lib",
    "frontend\src\routes",
    "frontend\static",
    "docs",
    ".github\workflows"
)

foreach ($dir in $directories) {
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
    Write-Host " Created: $dir" -ForegroundColor Green
}

# Step 2: Create __init__.py files
Write-Host ""
Write-Host "Creating Python package files..." -ForegroundColor Yellow

$initFiles = @(
    "backend\app\__init__.py",
    "backend\app\core\__init__.py",
    "backend\app\models\__init__.py",
    "backend\app\services\__init__.py",
    "backend\app\api\__init__.py",
    "backend\app\middleware\__init__.py",
    "backend\app\utils\__init__.py",
    "backend\tests\__init__.py"
)

foreach ($file in $initFiles) {
    New-Item -Path $file -ItemType File -Force | Out-Null
    Write-Host "Created: $file" -ForegroundColor Green
}

# Step 3: Create virtual environment
Write-Host ""
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
Set-Location backend
python -m venv venv
Write-Host "Virtual environment created" -ForegroundColor Green

# Step 4: Activate virtual environment and install dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "(This may take a few minutes)" -ForegroundColor Gray

& .\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip --quiet

# Install production dependencies
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt --quiet
    Write-Host "Production dependencies installed" -ForegroundColor Green
} else {
    Write-Host "requirements.txt not found - skipping" -ForegroundColor Yellow
}

# Install development dependencies
if (Test-Path "requirements-dev.txt") {
    pip install -r requirements-dev.txt --quiet
    Write-Host "Development dependencies installed" -ForegroundColor Green
} else {
    Write-Host "requirements-dev.txt not found - skipping" -ForegroundColor Yellow
}

# Step 5: Create .env from template
Write-Host ""
Write-Host "Setting up environment configuration..." -ForegroundColor Yellow

if (Test-Path ".env.example") {
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env from template" -ForegroundColor Green
        Write-Host " Please edit .env with your API keys!" -ForegroundColor Yellow
    } else {
        Write-Host ".env already exists - skipping" -ForegroundColor Yellow
    }
} else {
    Write-Host ".env.example not found - skipping" -ForegroundColor Yellow
}

# Step 6: Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Python Version:" -ForegroundColor Cyan
python --version

Write-Host ""
Write-Host "Installed Packages:" -ForegroundColor Cyan
pip list | Select-String -Pattern "fastapi|openai|pymongo|qdrant"

# Final instructions
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Edit backend\.env with your API keys" -ForegroundColor White
Write-Host "  2. Get OpenAI API key: https://platform.openai.com/api-keys" -ForegroundColor White
Write-Host "  3. Set up MongoDB Atlas: https://cloud.mongodb.com" -ForegroundColor White
Write-Host "  4. Set up Qdrant Cloud: https://cloud.qdrant.io" -ForegroundColor White
Write-Host ""
Write-Host "To start development:" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "Documentation: docs\ARCHITECTURE.md" -ForegroundColor Cyan
Write-Host ""

Set-Location ..