"""
Cisco FMC REST API Client.
Provides authentication, token management, and base API operations.
"""

import requests
import json
import time
from typing import Dict, Optional, Any, List
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from config.fmc_config import FMCConfig
from lib.utils import setup_logging, rate_limit, format_api_error


class FMCClient:
    """
    Client for interacting with Cisco FMC REST API.
    Handles authentication, token refresh, and API requests.
    """
    
    def __init__(self, config: Optional[FMCConfig] = None):
        """
        Initialize FMC client.
        
        Args:
            config: FMC configuration object. If None, loads from environment.
        """
        self.config = config or FMCConfig()
        self.logger = setup_logging(self.config.log_level)
        
        self.token = None
        self.refresh_token = None
        self.domain_uuid = None
        self.token_expiry = 0
        
        self.session = requests.Session()
        self.session.verify = self.config.get_verify_param()
        
        # Suppress SSL warnings if verification is disabled (lab only)
        if not self.config.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.logger.warning("SSL verification is disabled - use only in lab environments!")
        
        self.logger.info(f"FMC Client initialized for {self.config.host}")
    
    def authenticate(self) -> bool:
        """
        Authenticate with FMC and obtain access token.
        
        Returns:
            True if authentication successful, False otherwise
        """
        url = f"{self.config.platform_url}/auth/generatetoken"
        
        try:
            self.logger.info(f"Authenticating to FMC at {self.config.host}...")
            
            response = self.session.post(
                url,
                auth=(self.config.username, self.config.password),
                headers={'Content-Type': 'application/json'},
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 204:
                self.token = response.headers.get('X-auth-access-token')
                self.refresh_token = response.headers.get('X-auth-refresh-token')
                self.domain_uuid = response.headers.get('DOMAIN_UUID')
                
                # Token expires in 30 minutes
                self.token_expiry = time.time() + (30 * 60)
                
                self.logger.info("Authentication successful")
                self.logger.debug(f"Domain UUID: {self.domain_uuid}")
                return True
            else:
                self.logger.error(f"Authentication failed: {format_api_error(response)}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Connection error during authentication: {e}")
            return False
    
    def refresh_auth_token(self) -> bool:
        """
        Refresh authentication token using refresh token.
        
        Returns:
            True if refresh successful, False otherwise
        """
        url = f"{self.config.platform_url}/auth/refreshtoken"
        
        try:
            self.logger.info("Refreshing authentication token...")
            
            response = self.session.post(
                url,
                headers={
                    'Content-Type': 'application/json',
                    'X-auth-access-token': self.token,
                    'X-auth-refresh-token': self.refresh_token
                },
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 204:
                self.token = response.headers.get('X-auth-access-token')
                self.refresh_token = response.headers.get('X-auth-refresh-token')
                self.token_expiry = time.time() + (30 * 60)
                
                self.logger.info("Token refresh successful")
                return True
            else:
                self.logger.warning("Token refresh failed, re-authenticating...")
                return self.authenticate()
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during token refresh: {e}")
            return self.authenticate()
    
    def _ensure_authenticated(self):
        """Ensure valid authentication token exists."""
        if not self.token:
            self.authenticate()
        elif time.time() >= (self.token_expiry - 60):  # Refresh 1 min before expiry
            self.refresh_auth_token()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for API requests."""
        return {
            'Content-Type': 'application/json',
            'X-auth-access-token': self.token
        }
    
    @rate_limit(max_per_minute=100)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Perform GET request to FMC API.
        
        Args:
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
        
        Returns:
            Response data as dictionary, or None if request fails
        """
        self._ensure_authenticated()
        
        url = f"{self.config.base_url}/domain/{self.domain_uuid}/{endpoint}"
        
        try:
            self.logger.debug(f"GET {url}")
            
            response = self.session.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"GET request failed: {format_api_error(response)}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GET request exception: {e}")
            raise
    
    @rate_limit(max_per_minute=100)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def post(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """
        Perform POST request to FMC API.
        
        Args:
            endpoint: API endpoint
            data: Request body data
        
        Returns:
            Response data as dictionary, or None if request fails
        """
        self._ensure_authenticated()
        
        url = f"{self.config.base_url}/domain/{self.domain_uuid}/{endpoint}"
        
        try:
            self.logger.debug(f"POST {url}")
            
            response = self.session.post(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=self.config.api_timeout
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                self.logger.error(f"POST request failed: {format_api_error(response)}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"POST request exception: {e}")
            raise
    
    @rate_limit(max_per_minute=100)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def put(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """
        Perform PUT request to FMC API.
        
        Args:
            endpoint: API endpoint
            data: Request body data
        
        Returns:
            Response data as dictionary, or None if request fails
        """
        self._ensure_authenticated()
        
        url = f"{self.config.base_url}/domain/{self.domain_uuid}/{endpoint}"
        
        try:
            self.logger.debug(f"PUT {url}")
            
            response = self.session.put(
                url,
                headers=self._get_headers(),
                json=data,
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"PUT request failed: {format_api_error(response)}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"PUT request exception: {e}")
            raise
    
    @rate_limit(max_per_minute=100)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def delete(self, endpoint: str) -> bool:
        """
        Perform DELETE request to FMC API.
        
        Args:
            endpoint: API endpoint
        
        Returns:
            True if deletion successful, False otherwise
        """
        self._ensure_authenticated()
        
        url = f"{self.config.base_url}/domain/{self.domain_uuid}/{endpoint}"
        
        try:
            self.logger.debug(f"DELETE {url}")
            
            response = self.session.delete(
                url,
                headers=self._get_headers(),
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 200:
                return True
            else:
                self.logger.error(f"DELETE request failed: {format_api_error(response)}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"DELETE request exception: {e}")
            raise
    
    def get_all_pages(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Get all pages of paginated results.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
        
        Returns:
            List of all items across all pages
        """
        all_items = []
        offset = 0
        limit = 100  # Max items per page
        
        if params is None:
            params = {}
        
        while True:
            params['offset'] = offset
            params['limit'] = limit
            
            response = self.get(endpoint, params)
            
            if not response or 'items' not in response:
                break
            
            items = response['items']
            all_items.extend(items)
            
            # Check if there are more pages
            paging = response.get('paging', {})
            if offset + limit >= paging.get('count', 0):
                break
            
            offset += limit
            self.logger.debug(f"Fetched {len(all_items)} items so far...")
        
        self.logger.info(f"Retrieved total of {len(all_items)} items")
        return all_items
    
    def logout(self):
        """Revoke authentication token and logout."""
        if not self.token:
            return
        
        url = f"{self.config.platform_url}/auth/revokeaccess"
        
        try:
            self.logger.info("Logging out...")
            
            response = self.session.post(
                url,
                headers=self._get_headers(),
                timeout=self.config.api_timeout
            )
            
            if response.status_code == 204:
                self.logger.info("Logout successful")
            
            self.token = None
            self.refresh_token = None
            self.domain_uuid = None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during logout: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        self.authenticate()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.logout()
