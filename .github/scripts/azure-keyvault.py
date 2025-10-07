#!/usr/bin/env python3
"""
Azure Key Vault Integration for Apigee Migration Tool
"""

import os
import sys
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential

class AzureKeyVaultManager:
    def __init__(self, vault_url):
        """Initialize Azure Key Vault client"""
        self.vault_url = vault_url
        
        # Try different authentication methods
        try:
            # Method 1: Default credential (works with managed identity, Azure CLI, etc.)
            self.credential = DefaultAzureCredential()
            self.client = SecretClient(vault_url=vault_url, credential=self.credential)
        except Exception as e:
            print(f"❌ Failed to authenticate with Azure Key Vault: {e}")
            sys.exit(1)
    
    def get_secret(self, secret_name):
        """Get secret from Azure Key Vault"""
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            print(f"❌ Failed to get secret '{secret_name}': {e}")
            return None
    
    def create_env_file(self, secret_names, env_file='.env'):
        """Create .env file from Azure Key Vault secrets"""
        print(f"📡 Fetching secrets from Azure Key Vault: {self.vault_url}")
        
        env_vars = {}
        for secret_name in secret_names:
            value = self.get_secret(secret_name)
            if value:
                env_vars[secret_name.upper().replace('-', '_')] = value
        
        if not env_vars:
            print("❌ No secrets retrieved")
            return False
        
        # Write to .env file
        with open(env_file, 'w') as f:
            f.write("# =============================================================================\n")
            f.write("# Environment variables from Azure Key Vault\n")
            f.write("# =============================================================================\n\n")
            
            # Add base configuration
            base_config = {
                'ENVIRONMENT': 'production',
                'LOG_LEVEL': 'INFO',
                'FRONTEND_PORT': '3000',
                'BACKEND_PORT': '8001',
                'CORS_ORIGINS': 'https://yourdomain.com',
                'REACT_APP_BACKEND_URL': 'https://api.yourdomain.com'
            }
            
            for key, value in base_config.items():
                f.write(f"{key}={value}\n")
            
            f.write("\n# Secrets from Azure Key Vault\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Environment variables written to {env_file}")
        print(f"📝 Variables: {', '.join(env_vars.keys())}")
        return True

def main():
    """Main function"""
    # Configuration
    VAULT_URL = os.environ.get('AZURE_VAULT_URL', 'https://your-vault.vault.azure.net/')
    SECRET_NAMES = [
        'emergent-llm-key',
        'mongo-root-password', 
        'jwt-secret',
        'openai-api-key',
        'anthropic-api-key'
    ]
    
    print("🔐 Azure Key Vault Integration")
    print(f"   Vault URL: {VAULT_URL}")
    print(f"   Secrets: {', '.join(SECRET_NAMES)}")
    print()
    
    # Initialize Key Vault manager
    kv_manager = AzureKeyVaultManager(VAULT_URL)
    
    # Create .env file from secrets
    if kv_manager.create_env_file(SECRET_NAMES):
        print("\n🎉 Successfully configured environment variables from Azure Key Vault")
        print("\n🚀 You can now start the application:")
        print("   docker-compose up -d")
    else:
        print("\n❌ Failed to retrieve secrets from Azure Key Vault")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify Azure authentication: az account show")
        print("   2. Check Key Vault permissions")
        print("   3. Verify secret names exist in Key Vault")
        sys.exit(1)

if __name__ == "__main__":
    main()