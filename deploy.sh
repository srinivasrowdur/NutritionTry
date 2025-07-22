#!/bin/bash

# PDF Chat API Docker Deployment Script

set -e

echo "🚀 PDF Chat API Docker Deployment"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY:"
    echo "OPENAI_API_KEY=your_openai_api_key_here"
    exit 1
fi

# Check if PDF folder exists
if [ ! -d "pdf" ]; then
    echo "📁 Creating pdf folder..."
    mkdir -p pdf
    echo "✅ PDF folder created. Please add your PDF files to the pdf/ folder."
fi

# Check if processed folder exists
if [ ! -d "pdf/processed" ]; then
    echo "📁 Creating pdf/processed folder..."
    mkdir -p pdf/processed
fi

# Load environment variables
source .env

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not found in .env file!"
    exit 1
fi

echo "✅ Environment variables loaded"
echo "✅ PDF folders ready"

# Build the Docker image
echo "🔨 Building Docker image..."
docker compose build

# Stop existing containers if running
echo "🛑 Stopping existing containers..."
docker compose down

# Start the services
echo "🚀 Starting PDF Chat API..."
docker compose up -d

# Wait for the service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 10

# Check if the service is healthy
echo "🏥 Checking service health..."
if curl -f http://localhost:8001/status > /dev/null 2>&1; then
    echo "✅ Service is healthy!"
    echo ""
    echo "🎉 PDF Chat API is now running!"
    echo "=================================="
    echo "🌐 API URL: http://localhost:8001"
    echo "📖 API Docs: http://localhost:8001/docs"
    echo "📋 Alternative Docs: http://localhost:8001/redoc"
    echo ""
    echo "📁 PDF Management:"
    echo "   • Add new PDFs to: ./pdf/"
    echo "   • Processed PDFs in: ./pdf/processed/"
    echo ""
    echo "🔧 Useful commands:"
    echo "   • View logs: docker compose logs -f"
    echo "   • Stop service: docker compose down"
    echo "   • Restart service: docker compose restart"
    echo "   • Rebuild: docker compose up --build"
echo ""
echo "📁 Files:"
echo "   • appapi.py - Main FastAPI application"
echo "   • app.py - Command-line chat interface"
else
    echo "❌ Service health check failed!"
    echo "📋 Checking logs..."
    docker compose logs
    exit 1
fi 