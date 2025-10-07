#!/bin/bash
set -e

# AWS Secrets Manager Docker Setup
# This script fetches secrets from AWS and starts the application

echo "🔐 Setting up Apigee Migration Tool with AWS Secrets Manager..."

# Configuration
AWS_SECRET_NAME="${AWS_SECRET_NAME:-apigee-migration-tool/secrets}"
AWS_REGION="${AWS_REGION:-us-east-1}"
ENV_FILE=".env"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   pip install awscli"
    echo "   aws configure"
    exit 1
fi

# Verify AWS credentials
echo "🔍 Verifying AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run: aws configure"
    exit 1
fi

echo "✅ AWS credentials verified"

# Fetch secrets using AWS CLI
echo "📡 Fetching secrets from AWS Secrets Manager..."
if ! secret_json=$(aws secretsmanager get-secret-value \
    --secret-id "$AWS_SECRET_NAME" \
    --region "$AWS_REGION" \
    --query SecretString \
    --output text 2>/dev/null); then
    echo "❌ Failed to fetch secret '$AWS_SECRET_NAME'"
    echo "🔧 Troubleshooting:"
    echo "   1. Verify secret exists: aws secretsmanager list-secrets --region $AWS_REGION"
    echo "   2. Check IAM permissions for SecretsManager:GetSecretValue"
    echo "   3. Verify secret name: $AWS_SECRET_NAME"
    exit 1
fi

# Parse JSON secrets and create .env file
echo "📝 Creating environment file..."
cat > "$ENV_FILE" << 'EOF'
# =============================================================================
# Apigee Migration Tool - Environment from AWS Secrets Manager
# =============================================================================
ENVIRONMENT=production
LOG_LEVEL=INFO

# Port Configuration
FRONTEND_PORT=3000
BACKEND_PORT=8001
MONGO_PORT=27017
REDIS_PORT=6379

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Frontend Configuration
REACT_APP_BACKEND_URL=https://api.yourdomain.com
EOF

# Extract secrets from JSON and append to .env
echo "$secret_json" | python3 -c "
import json, sys
secrets = json.load(sys.stdin)
for key, value in secrets.items():
    print(f'{key}={value}')
" >> "$ENV_FILE"

echo "✅ Environment file created with AWS secrets"

# Show which variables were configured (without values)
echo "📋 Configured variables:"
grep -E '^[A-Z_]+=' "$ENV_FILE" | cut -d'=' -f1 | sed 's/^/   - /'

# Start the application
echo ""
echo "🚀 Starting Apigee Migration Tool..."
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Test the deployment
echo "🧪 Testing deployment..."
if curl -f http://localhost:8001/api/ &> /dev/null; then
    echo "✅ Backend is responding"
else
    echo "❌ Backend is not responding"
fi

if curl -f http://localhost:3000 &> /dev/null; then
    echo "✅ Frontend is responding"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 Deployment completed!"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8001"
echo "   Logs: docker-compose logs -f"