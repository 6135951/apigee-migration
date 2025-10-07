# Apigee Migration Tool - Docker Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### One-Command Setup
```bash
chmod +x setup.sh
./setup.sh
```

## 🔧 Manual Setup

### 1. Clone and Configure
```bash
# Copy environment file
cp .env.example .env

# Update .env file with your API keys
nano .env
```

### 2. Required Environment Variables
Update these in your `.env` file:

#### Essential Keys
```env
# LLM Integration (Required for AI features)
OPENAI_API_KEY=sk-your-openai-key-here

# OR use individual API keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=your-google-key

# Database Security
MONGO_ROOT_PASSWORD=secure_password_here
REDIS_PASSWORD=secure_redis_password
```

### 3. Start Services
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   MongoDB       │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Database)    │
│   Port: 3000    │    │   Port: 8001    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                         ┌─────────────────┐
                         │   Redis         │
                         │   (Cache)       │
                         │   Port: 6379    │
                         └─────────────────┘
```

## 🎛️ Service Management

### Start/Stop Services
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend
```

### View Status
```bash
# Check service status
docker-compose ps

# View resource usage
docker-compose top

# View logs
docker-compose logs -f backend
```

### Database Management
```bash
# Connect to MongoDB
docker-compose exec mongodb mongosh -u apigee_admin -p

# Backup database
docker-compose exec mongodb mongodump --out /tmp/backup

# View database logs
docker-compose logs mongodb
```

## 🔐 Security Best Practices

### 1. Environment Variables
- Never commit `.env` files to git
- Use strong passwords (min 16 characters)
- Rotate API keys regularly
- Use different credentials for each environment

### 2. API Key Management
```env
# Option 1: Use Emergent Universal Key (Recommended)
OPENAI_API_KEY=sk-your-openai-key-here

# Option 2: Individual API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-gemini-key
```

### 3. Database Security
```env
# Use strong MongoDB credentials
MONGO_ROOT_USERNAME=apigee_admin
MONGO_ROOT_PASSWORD=StrongPassword123!@#

# Enable authentication
MONGO_DATABASE=apigee_migration_db
```

## 🌐 Production Deployment

### 1. Enable Production Profile
```bash
# Start with production configuration
docker-compose --profile production up -d
```

### 2. SSL Configuration
```bash
# Add SSL certificates
mkdir -p docker/ssl
cp your-cert.pem docker/ssl/
cp your-key.pem docker/ssl/
```

### 3. Environment Variables for Production
```env
ENVIRONMENT=production
LOG_LEVEL=WARN
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
```

## 📊 Monitoring & Logs

### View Real-time Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Health Checks
```bash
# Check API health
curl http://localhost:8001/api/

# Check frontend
curl http://localhost:3000

# Check MongoDB
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

### Performance Monitoring
```bash
# Resource usage
docker stats

# Service status
docker-compose ps
```

## 🔧 Development Mode

### Enable Hot Reload
```env
# In .env file
HOT_RELOAD=true
DEBUG=true
```

### Mount Source Code
```bash
# For development with live code changes
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8001

# Kill the process or change ports in .env
FRONTEND_PORT=3001
BACKEND_PORT=8002
```

#### 2. MongoDB Connection Issues
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Verify credentials in .env
# Restart MongoDB
docker-compose restart mongodb
```

#### 3. API Key Issues
```bash
# Verify API key in .env
echo $OPENAI_API_KEY

# Check backend logs
docker-compose logs backend | grep -i "key\|auth\|error"
```

#### 4. Memory Issues
```bash
# Increase Docker memory limit
# Check resource usage
docker system df
docker system prune -a
```

### Reset Everything
```bash
# Complete reset (deletes all data)
docker-compose down -v
docker system prune -a
./setup.sh
```

## 📚 API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8001/docs
- **API Schema**: http://localhost:8001/redoc

## 🔄 Updates

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose build
docker-compose up -d
```

### Update Dependencies
```bash
# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

## 📝 Configuration Reference

### Complete .env Template
See `.env.example` for all available configuration options including:
- Database settings
- API integrations
- Security configuration
- Monitoring setup
- Cloud service integration