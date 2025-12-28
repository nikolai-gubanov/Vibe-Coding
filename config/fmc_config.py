"""
Configuration management for Cisco FMC API automation.
Loads settings from environment variables with validation.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FMCConfig:
    """FMC Configuration settings."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.host = os.getenv('FMC_HOST')
        self.username = os.getenv('FMC_USERNAME')
        self.password = os.getenv('FMC_PASSWORD')
        self.verify_ssl = os.getenv('FMC_VERIFY_SSL', 'true').lower() == 'true'
        self.ca_cert = os.getenv('FMC_CA_CERT')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '100'))
        self.api_timeout = int(os.getenv('API_TIMEOUT', '30'))
        
        # Validate required settings
        self._validate()
    
    def _validate(self):
        """Validate required configuration parameters."""
        if not self.host:
            raise ValueError("FMC_HOST is required in environment variables")
        if not self.username:
            raise ValueError("FMC_USERNAME is required in environment variables")
        if not self.password:
            raise ValueError("FMC_PASSWORD is required in environment variables")
    
    @property
    def base_url(self) -> str:
        """Get the base API URL."""
        return f"https://{self.host}/api/fmc_config/v1"
    
    @property
    def platform_url(self) -> str:
        """Get the platform API URL."""
        return f"https://{self.host}/api/fmc_platform/v1"
    
    def get_verify_param(self) -> bool | str:
        """Get SSL verification parameter for requests library."""
        if self.ca_cert:
            return self.ca_cert
        return self.verify_ssl
    
    def __repr__(self):
        """String representation (masks password)."""
        return (f"FMCConfig(host={self.host}, username={self.username}, "
                f"verify_ssl={self.verify_ssl})")
