"""
Configuration file for test scripts
Provides centralized configuration for all test scripts
"""

import os
import sys

# Default configuration
DEFAULT_CONFIG = {
    'base_url': 'http://localhost:3000',
    'backend_port': 8001,
    'frontend_port': 3000,
    'api_timeout': 30,
    'large_file_timeout': 120,
    'max_file_size_mb': 100,
    'max_swagger_file_size_mb': 10
}

class TestConfig:
    """Test configuration manager"""
    
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self._load_from_environment()
        self._load_from_args()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mappings = {
            'TEST_BASE_URL': 'base_url',
            'TEST_BACKEND_PORT': 'backend_port',
            'TEST_FRONTEND_PORT': 'frontend_port',
            'TEST_API_TIMEOUT': 'api_timeout',
            'TEST_MAX_FILE_SIZE_MB': 'max_file_size_mb'
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value:
                if config_key in ['backend_port', 'frontend_port', 'api_timeout', 'large_file_timeout', 'max_file_size_mb', 'max_swagger_file_size_mb']:
                    self.config[config_key] = int(env_value)
                else:
                    self.config[config_key] = env_value
    
    def _load_from_args(self):
        """Load base URL from command line arguments if provided"""
        if len(sys.argv) > 1:
            self.config['base_url'] = sys.argv[1]
    
    @property
    def base_url(self):
        return self.config['base_url']
    
    @property
    def api_url(self):
        return f"{self.config['base_url']}/api"
    
    @property
    def backend_port(self):
        return self.config['backend_port']
    
    @property
    def frontend_port(self):
        return self.config['frontend_port']
    
    @property
    def api_timeout(self):
        return self.config['api_timeout']
    
    @property
    def large_file_timeout(self):
        return self.config['large_file_timeout']
    
    @property
    def max_file_size_mb(self):
        return self.config['max_file_size_mb']
    
    @property
    def max_swagger_file_size_mb(self):
        return self.config['max_swagger_file_size_mb']
    
    def get_backend_url(self):
        """Get direct backend URL"""
        return f"http://localhost:{self.backend_port}"
    
    def get_frontend_url(self):
        """Get direct frontend URL"""  
        return f"http://localhost:{self.frontend_port}"
    
    def __str__(self):
        return f"TestConfig(base_url='{self.base_url}', backend_port={self.backend_port}, frontend_port={self.frontend_port})"

# Global configuration instance
config = TestConfig()

# For backward compatibility
def get_base_url():
    """Get the base URL for tests"""
    return config.base_url

def get_api_url():
    """Get the API URL for tests"""
    return config.api_url