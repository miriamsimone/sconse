#!/bin/bash

# AI Microservice Setup Script

echo "🐳 Setting up AI Microservice with Docker"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY (required)"
    echo "   - ANTHROPIC_API_KEY (optional)"
    echo "   - BRAVE_API_KEY (optional)"
    echo ""
    echo "   Then run this script again."
    exit 0
fi

# Build and start the service
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting AI Microservice..."
docker-compose up -d

echo "⏳ Waiting for service to start..."
sleep 10

# Test the service
echo "🧪 Testing service..."
python3 ../test_docker_music_generation.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Service is running at: http://localhost:8000"
echo "API docs available at: http://localhost:8000/docs"
echo ""
echo "To stop the service: docker-compose down"
echo "To view logs: docker-compose logs -f"
echo "To rebuild: docker-compose up --build"
