"""
Feature Extractor

Extracts numerical features from HTTP responses
for use in ML classification.

Features extracted:
  - response_length      : Length of response body (chars)
  - status_code          : HTTP status code
  - has_sql_keywords     : 1 if SQL error keywords found, else 0
  - sql_keyword_count    : Number of distinct SQL keywords found
  - has_xss_reflection   : 1 if payload is reflected in response, else 0
  - xss_keyword_count    : Number of distinct XSS keywords found
  - content_type_html    : 1 if Content-Type is text/html, else 0
  - error_page_detected  : 1 if status code is 4xx or 5xx, else 0
  - has_redirect         : 1 if status code is 3xx, else 0
  - length_delta         : Difference in length vs baseline response (0 if no baseline)
"""


class FeatureExtractor:
    """Extracts features from HTTP responses for ML input."""

    # SQL-related error keywords that appear in database error messages
    SQL_KEYWORDS = [
        'sql', 'mysql', 'sqlite', 'postgresql', 'oracle',
        'syntax error', 'query', 'database', 'table',
        'column', 'row', 'select', 'insert', 'update',
    ]

    # XSS-related keywords / patterns
    XSS_KEYWORDS = [
        '<script', 'javascript:', 'onerror', 'onload',
        'alert(', 'document.cookie',
    ]

    def extract(self, response_data, payload=None, baseline_length=None):
        """Extract features from a single HTTP response.

        Args:
            response_data (dict): Keys: status_code (int), content (str), headers (dict)
            payload (str | None): The payload injected in this request, used to
                                  detect reflection.
            baseline_length (int | None): Length of the baseline (no-payload) response.
                                          Used to compute length_delta.

        Returns:
            dict: Feature name → value (int / bool / float).
        """
        content = response_data.get('content', '')
        content_lower = content.lower()
        status_code = response_data.get('status_code', 0)

        features = {
            'response_length': len(content),
            'status_code': status_code,
            'has_sql_keywords': self._check_keywords(content_lower, self.SQL_KEYWORDS),
            'sql_keyword_count': self._count_keywords(content_lower, self.SQL_KEYWORDS),
            'has_xss_reflection': self._check_reflection(content, payload) if payload else False,
            'xss_keyword_count': self._count_keywords(content_lower, self.XSS_KEYWORDS),
            'content_type_html': 'text/html' in response_data.get('headers', {}).get('Content-Type', ''),
            'error_page_detected': 400 <= status_code < 600,
            'has_redirect': 300 <= status_code < 400,
            'length_delta': abs(len(content) - baseline_length) if baseline_length is not None else 0,
        }

        return features

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _check_keywords(self, content, keywords):
        """Return True if any keyword appears in content."""
        return any(kw in content for kw in keywords)

    def _count_keywords(self, content, keywords):
        """Return the number of distinct keywords that appear in content."""
        return sum(1 for kw in keywords if kw in content)

    def _check_reflection(self, content, payload):
        """Return True if the payload string is reflected verbatim in content."""
        if not payload:
            return False
        return payload in content
