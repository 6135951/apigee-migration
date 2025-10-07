#!/bin/bash
set -e

# Apigee Migration Tool - Setup Script
# This script sets up the Docker environment for local development

echo "🚀 Setting up Apigee Migration Tool for Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your actual API keys and credentials."
    echo ""
    echo "🔑 IMPORTANT: Update the following in your .env file:"
    echo "   - EMERGENT_LLM_KEY (or individual API keys)"
    echo "   - MONGO_ROOT_PASSWORD"
    echo "   - REDIS_PASSWORD"
    echo "   - Other API keys as needed"
    echo ""
    read -p "Press Enter to continue after updating .env file..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p docker/ssl
mkdir -p backend/logs
mkdir -p data/mongodb
mkdir -p data/redis

# Pull required Docker images
echo "📦 Pulling Docker images..."
docker-compose pull

# Build custom images
echo "🔨 Building custom images..."
docker-compose build

# Create and start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8001"
echo "MongoDB: localhost:27017"

# Test API endpoint
if curl -f http://localhost:8001/api/ &> /dev/null; then
    echo "✅ Backend API is responding"
else
    echo "❌ Backend API is not responding"
fi

# Test frontend
if curl -f http://localhost:3000 &> /dev/null; then
    echo "✅ Frontend is responding"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8001"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "🛠️  Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose pull && docker-compose up -d"
echo ""
echo "📊 Monitor services:"
echo "   docker-compose ps"
echo "   docker-compose top"