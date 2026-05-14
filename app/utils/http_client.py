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
        login_url = os.getenv('DVWA_LOGIN_URL', 'http://dvwa/login.php')
        username = os.getenv('DVWA_USER', 'admin')
        password = os.getenv('DVWA_PASS', 'password')
        security_level = os.getenv('DVWA_SECURITY_LEVEL', 'low').lower()

        try:
            # 1. Get the login page to extract CSRF token (user_token)
            logger.info(f"Attempting DVWA auto-login at {login_url} (Security: {security_level})...")
            resp = self.session.get(login_url, timeout=self.timeout)
            
            if resp.status_code != 200:
                logger.warning(f"Could not reach DVWA login page (Status: {resp.status_code})")
                return

            soup = BeautifulSoup(resp.text, 'html.parser')
            user_token = ""
            token_input = soup.find('input', {'name': 'user_token'})
            if token_input:
                user_token = token_input.get('value', '')
            else:
                # Check if we are already logged in
                if 'PHPSESSID' in self.session.cookies:
                    logger.info("Already have a session cookie, skipping login.")
                    return

            # 2. Perform Login POST
            payload = {
                'username': username,
                'password': password,
                'Login': 'Login',
                'user_token': user_token
            }
            
            login_resp = self.session.post(login_url, data=payload, timeout=self.timeout)
            
            # 3. Verify success
            if "login.php" in login_resp.url and "Login failed" in login_resp.text:
                logger.error("DVWA login failed: Invalid credentials or CSRF token.")
                return

            # 4. Set security level
            self.session.cookies.set('security', security_level)
            
            logger.info(f"DVWA login successful (Security Level: {security_level.upper()})")
        except Exception as e:
            logger.warning(f"DVWA auto-login encountered an error: {str(e)}")

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
