# 🔐 API Keys and Security Configuration Guide

## 📋 API Key Requirements

### 1. Primary LLM Integration (ChatGPT 4.1)

The application uses **ChatGPT 4.1** for AI-powered policy analysis and conversion. You have two options:

#### Primary Option: OpenAI API Key (Current Implementation)
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```
- **Direct OpenAI integration** for ChatGPT models
- **Full control** over API usage and billing
- **Industry standard** implementation

**How to get your OpenAI API key:**
1. Visit https://platform.openai.com/account/api-keys
2. Click "Create new secret key"
3. Copy and use in your .env file

#### Alternative: Other Provider Keys
```env
# Other LLM providers (if needed)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Anthropic (for Claude, if needed)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Google (for Gemini, if needed)
GOOGLE_API_KEY=your-google-api-key-here
```

### 2. How to Get API Keys

#### OpenAI API Key Setup (Primary Method)
1. Visit https://platform.openai.com/account/api-keys
2. Sign up/login to your OpenAI account
3. Click "Create new secret key"
4. Copy the key starting with `sk-`
5. Add to `.env`: `OPENAI_API_KEY=sk-your-openai-key-here`

#### OpenAI API Key (Alternative)
1. Visit https://platform.openai.com/
2. Sign up/login to your account
3. Go to API Keys section
4. Create new key for ChatGPT 4.1
5. Copy key starting with `sk-proj-`

#### MongoDB Setup
```env
MONGO_ROOT_USERNAME=apigee_admin
MONGO_ROOT_PASSWORD=YourSecurePassword123!
MONGO_DATABASE=apigee_migration_db
```

## 🔒 Security Best Practices

### 1. Environment Variable Security
```bash
# Create .env file with proper permissions
cp .env.example .env
chmod 600 .env  # Only owner can read/write
```

### 2. Strong Password Requirements
```env
# MongoDB password (16+ characters, mixed case, numbers, symbols)
MONGO_ROOT_PASSWORD=SecureMongo2024!@#$

# Redis password
REDIS_PASSWORD=SecureRedis2024!@#$

# JWT secret (32+ characters)
JWT_SECRET=your-32-plus-character-jwt-secret-key-here
```

### 3. API Key Rotation
- Rotate API keys every 90 days
- Use different keys for development/production
- Monitor API key usage and costs

### 4. Network Security
```env
# Restrict CORS origins in production
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Use HTTPS in production
REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

## 🚀 Quick Setup Commands

### 1. Complete Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

### 2. Production Setup
```bash
# Set production environment
sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/' .env

# Start with production profile
docker-compose --profile production up -d
```

## 🧪 Testing API Keys

### Test Emergent Key
```bash
# Test backend with your key
curl -X POST http://localhost:8001/api/test-llm \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### Test Individual Keys
```bash
# Test OpenAI directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

## 📊 Cost Management

### Monitor API Usage
- Set up billing alerts in OpenAI/Anthropic/Google dashboards
- Monitor usage in application logs
- Use rate limiting to control costs

### Cost-Effective Settings
```env
# Limit AI processing
MAX_POLICIES_PER_REQUEST=10
AI_TIMEOUT_SECONDS=30
ENABLE_CACHING=true
```

## 🔧 Configuration Validation

The application will validate your configuration on startup:

### Required Keys Check
- ✅ OPENAI_API_KEY for AI analysis features
- ✅ MONGO_ROOT_PASSWORD
- ✅ Database connection
- ✅ CORS origins

### Health Check Endpoints
- **API Health**: http://localhost:8001/api/health
- **Database Health**: http://localhost:8001/api/db-health
- **LLM Integration**: http://localhost:8001/api/llm-health

## 🚨 Troubleshooting

### Common Issues

#### 1. API Key Not Working
```bash
# Check key format
echo $OPENAI_API_KEY | grep "sk-"

# Check backend logs
docker-compose logs backend | grep -i "unauthorized\|forbidden\|key"
```

#### 2. Database Connection Issues
```bash
# Check MongoDB credentials
docker-compose logs mongodb | grep -i "auth\|error"

# Test connection
docker-compose exec backend python -c "
import os
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
print('MongoDB connection:', client.admin.command('ismaster'))
"
```

#### 3. CORS Issues
```bash
# Check CORS configuration
echo $CORS_ORIGINS

# Update for your domain
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## 📈 Production Checklist

### Security
- [ ] Strong passwords for all services
- [ ] API keys properly secured
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Environment variables secured

### Monitoring
- [ ] Health checks enabled
- [ ] Logging configured
- [ ] Metrics collection setup
- [ ] Error tracking (Sentry)
- [ ] API usage monitoring

### Performance
- [ ] Redis caching enabled
- [ ] Database indexes created
- [ ] Resource limits set
- [ ] Auto-scaling configured

### Backup
- [ ] Database backups scheduled
- [ ] Configuration backed up
- [ ] SSL certificates secured
- [ ] Recovery procedures tested

## 📞 Support

For API key issues:
- **OpenAI**: Check OpenAI dashboard
- **Database**: Check MongoDB logs
- **Application**: Check application logs with `docker-compose logs`