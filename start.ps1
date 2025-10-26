# FitFusion AI Assistant - Docker Setup Script
# PowerShell script for Windows

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "FitFusion AI Assistant - Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ .env file created!" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  IMPORTANT: Please edit .env and add your GOOGLE_API_KEY" -ForegroundColor Yellow
        Write-Host "   1. Open .env file in a text editor" -ForegroundColor Yellow
        Write-Host "   2. Replace 'your_api_key_here' with your actual API key" -ForegroundColor Yellow
        Write-Host "   3. Save and close the file" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Get your API key from: https://makersuite.google.com/app/apikey" -ForegroundColor Cyan
        Write-Host ""
        
        $response = Read-Host "Have you added your API key? (y/n)"
        if ($response -ne "y") {
            Write-Host "Please add your API key to .env and run this script again." -ForegroundColor Red
            exit
        }
    } else {
        Write-Host "❌ .env.example not found!" -ForegroundColor Red
        exit
    }
}

Write-Host "✅ Environment file found!" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Cyan
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not running"
    }
    Write-Host "✅ Docker is running!" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running or not installed!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "Building Docker image..." -ForegroundColor Cyan
docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image built successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to build Docker image!" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Starting FitFusion AI Assistant..." -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Application will be available at: http://localhost:8501" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

docker-compose up
