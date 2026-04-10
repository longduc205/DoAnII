"""
HTTP Client Wrapper

Provides a consistent interface for making HTTP requests
with timeout, error handling, and response metadata collection.
"""

import requests


class HTTPClient:
    """Wrapper around requests library with scanning-specific features."""

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-VulnScanner/1.0 (Educational Purpose)'
        })

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
