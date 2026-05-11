"""
HTTP Client Wrapper

Provides a consistent interface for making HTTP requests
with timeout, error handling, and session management (including DVWA auto-login).
"""

import requests
import logging
import os
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class HTTPClient:
    """Wrapper around requests library with scanning-specific features."""

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-VulnScanner/1.0 (Educational Purpose)'
        })
        
        # Try to auto-login if target is DVWA
        self._check_and_login_dvwa()

    def _check_and_login_dvwa(self):
        """Attempts to login to DVWA automatically if credentials are provided."""
        login_url = os.getenv('DVWA_LOGIN_URL', 'http://localhost:8080/login.php')
        username = os.getenv('DVWA_USER', 'admin')
        password = os.getenv('DVWA_PASS', 'password')

        try:
            # 1. Get the login page to extract CSRF token (user_token)
            logger.info(f"Attempting DVWA auto-login at {login_url}...")
            resp = self.session.get(login_url, timeout=self.timeout)
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            user_token = ""
            token_input = soup.find('input', {'name': 'user_token'})
            if token_input:
                user_token = token_input.get('value', '')

            # 2. Perform Login POST
            payload = {
                'username': username,
                'password': password,
                'Login': 'Login',
                'user_token': user_token
            }
            
            self.session.post(login_url, data=payload, timeout=self.timeout)
            
            # 3. Set security level to low for testing
            # DVWA uses a 'security' cookie
            self.session.cookies.set('security', 'low')
            
            logger.info("DVWA login successful (Security Level: LOW)")
        except Exception as e:
            logger.warning(f"DVWA auto-login failed: {str(e)}. Using guest/manual session.")

    def get(self, url, params=None):
        """Send a GET request."""
        try:
            response = self.session.get(
                url, params=params, timeout=self.timeout
            )
            return self._build_response_data(response)
        except requests.RequestException as e:
            return {'error': str(e), 'success': False}

    def post(self, url, data=None):
        """Send a POST request."""
        try:
            response = self.session.post(
                url, data=data, timeout=self.timeout
            )
            return self._build_response_data(response)
        except requests.RequestException as e:
            return {'error': str(e), 'success': False}

    def _build_response_data(self, response):
        """Build a standardized response dictionary."""
        return {
            'success': True,
            'status_code': response.status_code,
            'content': response.text,
            'content_length': len(response.text),
            'headers': dict(response.headers),
            'url': response.url,
            'elapsed_ms': response.elapsed.total_seconds() * 1000
        }
