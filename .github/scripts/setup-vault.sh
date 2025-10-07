#!/bin/bash
set -e

# HashiCorp Vault Integration for Apigee Migration Tool
# Fetches secrets from Vault and creates environment configuration

echo "🔐 Setting up with HashiCorp Vault..."

# Configuration
VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
VAULT_PATH="${VAULT_PATH:-secret/apigee-migration-tool}"
ENV_FILE=".env"

# Check if vault CLI is available
if ! command -v vault &> /dev/null; then
    echo "❌ Vault CLI not found. Please install HashiCorp Vault CLI"
    exit 1
fi

# Check Vault authentication
if ! vault auth -method=token &> /dev/null; then
    echo "❌ Vault authentication failed. Please authenticate:"
    echo "   vault auth -method=userpass username=myuser"
    echo "   # or"
    echo "   vault auth -method=token"
    exit 1
fi

echo "✅ Vault authentication successful"

# Fetch secrets from Vault
echo "📡 Fetching secrets from Vault path: $VAULT_PATH"

# Create base .env file
cat > "$ENV_FILE" << EOF
# =============================================================================
# Apigee Migration Tool - Environment from HashiCorp Vault
# =============================================================================
ENVIRONMENT=production
LOG_LEVEL=INFO
FRONTEND_PORT=3000
BACKEND_PORT=8001
CORS_ORIGINS=https://yourdomain.com
REACT_APP_BACKEND_URL=https://api.yourdomain.com

EOF

# Fetch and append secrets
vault kv get -format=json "$VAULT_PATH" | jq -r '.data.data | to_entries[] | "\(.key)=\(.value)"' >> "$ENV_FILE"

echo "✅ Secrets retrieved from Vault"
echo "📋 Starting application with Vault secrets..."

# Start application
docker-compose up -d

echo "🎉 Application started with HashiCorp Vault secrets!"