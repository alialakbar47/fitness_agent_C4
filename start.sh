#!/bin/bash
# FitFusion AI Assistant - Docker Setup Script
# Bash script for Linux/Mac

echo "=================================="
echo "FitFusion AI Assistant - Setup"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo ""
    echo "Creating .env file from template..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env file created!"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env and add your GOOGLE_API_KEY"
        echo "   1. Open .env file in a text editor"
        echo "   2. Replace 'your_api_key_here' with your actual API key"
        echo "   3. Save and close the file"
        echo ""
        echo "Get your API key from: https://makersuite.google.com/app/apikey"
        echo ""
        
        read -p "Have you added your API key? (y/n) " response
        if [ "$response" != "y" ]; then
            echo "Please add your API key to .env and run this script again."
            exit 1
        fi
    else
        echo "❌ .env.example not found!"
        exit 1
    fi
fi

echo "✅ Environment file found!"
echo ""

# Check if Docker is running
echo "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running or not installed!"
    echo "Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running!"
echo ""

# Build Docker image
echo "Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
else
    echo "❌ Failed to build Docker image!"
    exit 1
fi

echo ""
echo "Starting FitFusion AI Assistant..."
echo ""
echo "🌐 Application will be available at: http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""

docker-compose up
