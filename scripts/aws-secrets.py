#!/usr/bin/env python3
"""
AWS Secrets Manager Integration for Apigee Migration Tool
Fetches secrets from AWS Secrets Manager and populates environment variables
"""

import boto3
import json
import os
import sys
from botocore.exceptions import ClientError, NoCredentialsError

class AWSSecretsManager:
    def __init__(self, region_name='us-east-1'):
        """Initialize AWS Secrets Manager client"""
        try:
            self.client = boto3.client('secretsmanager', region_name=region_name)
        except NoCredentialsError:
            print("❌ AWS credentials not found. Configure using AWS CLI or environment variables.")
            sys.exit(1)
    
    def get_secret(self, secret_name):
        """Retrieve secret from AWS Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_value = response['SecretString']
            return json.loads(secret_value) if secret_value.startswith('{') else secret_value
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                print(f"❌ Secret '{secret_name}' not found in AWS Secrets Manager")
            elif error_code == 'InvalidRequestException':
                print(f"❌ Invalid request for secret '{secret_name}'")
            elif error_code == 'InvalidParameterException':
                print(f"❌ Invalid parameter for secret '{secret_name}'")
            else:
                print(f"❌ Error retrieving secret '{secret_name}': {e}")
            return None
    
    def create_env_file(self, secret_name, env_file='.env'):
        """Create .env file from AWS Secrets Manager"""
        print(f"📡 Fetching secrets from AWS Secrets Manager: {secret_name}")
        
        secrets = self.get_secret(secret_name)
        if not secrets:
            return False
        
        # Handle both individual secrets and JSON objects
        if isinstance(secrets, dict):
            env_vars = secrets
        else:
            # If it's a single secret, assume it's the LLM key
            env_vars = {'EMERGENT_LLM_KEY': secrets}
        
        # Write to .env file
        with open(env_file, 'w') as f:
            f.write("# =============================================================================\n")
            f.write("# Environment variables from AWS Secrets Manager\n")
            f.write("# =============================================================================\n\n")
            
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Environment variables written to {env_file}")
        print(f"📝 Variables: {', '.join(env_vars.keys())}")
        return True

def main():
    """Main function to fetch secrets and create .env file"""
    # Configuration
    SECRET_NAME = os.environ.get('AWS_SECRET_NAME', 'apigee-migration-tool/secrets')
    REGION = os.environ.get('AWS_REGION', 'us-east-1')
    ENV_FILE = os.environ.get('ENV_FILE', '.env')
    
    print("🔐 AWS Secrets Manager Integration")
    print(f"   Secret Name: {SECRET_NAME}")
    print(f"   Region: {REGION}")
    print(f"   Output File: {ENV_FILE}")
    print()
    
    # Initialize secrets manager
    secrets_manager = AWSSecretsManager(region_name=REGION)
    
    # Create .env file from secrets
    if secrets_manager.create_env_file(SECRET_NAME, ENV_FILE):
        print("\n🎉 Successfully configured environment variables from AWS Secrets Manager")
        print("\n🚀 You can now start the application:")
        print("   docker-compose up -d")
    else:
        print("\n❌ Failed to retrieve secrets from AWS Secrets Manager")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify AWS credentials: aws sts get-caller-identity")
        print("   2. Check secret exists: aws secretsmanager describe-secret --secret-id", SECRET_NAME)
        print("   3. Verify IAM permissions for SecretsManager:GetSecretValue")
        sys.exit(1)

if __name__ == "__main__":
    main()