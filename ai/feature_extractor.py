"""
Feature Extractor

Extracts numerical features from HTTP responses
for use in ML classification.
"""


class FeatureExtractor:
    """Extracts features from HTTP responses for ML input."""

    # SQL-related error keywords
    SQL_KEYWORDS = [
        'sql', 'mysql', 'sqlite', 'postgresql', 'oracle',
        'syntax error', 'query', 'database', 'table',
        'column', 'row', 'select', 'insert', 'update',
    ]

    # XSS-related keywords
    XSS_KEYWORDS = [
        '<script', 'javascript:', 'onerror', 'onload',
        'alert(', 'document.cookie',
    ]

    def extract(self, response_data, payload=None):
        """
        Extract features from a response.

        Returns a dictionary of features:
        - response_length: Length of response body
        - status_code: HTTP status code
        - has_sql_keywords: Whether SQL error keywords are present
        - has_xss_reflection: Whether payload is reflected in response
        - keyword_count: Number of suspicious keywords found
        """
        content = response_data.get('content', '')
        content_lower = content.lower()

        features = {
            'response_length': len(content),
            'status_code': response_data.get('status_code', 0),
            'has_sql_keywords': self._check_keywords(content_lower, self.SQL_KEYWORDS),
            'sql_keyword_count': self._count_keywords(content_lower, self.SQL_KEYWORDS),
            'has_xss_reflection': self._check_reflection(content, payload) if payload else False,
            'xss_keyword_count': self._count_keywords(content_lower, self.XSS_KEYWORDS),
            'content_type_html': 'text/html' in response_data.get('headers', {}).get('Content-Type', ''),
        }

        return features

    def _check_keywords(self, content, keywords):
        """Check if any keywords are present in content."""
        return any(kw in content for kw in keywords)

    def _count_keywords(self, content, keywords):
        """Count how many keywords appear in content."""
        return sum(1 for kw in keywords if kw in content)

    def _check_reflection(self, content, payload):
        """Check if a payload is reflected in the response."""
        if not payload:
            return False
        return payload in content
