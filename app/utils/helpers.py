"""
General Helper Functions
"""

from urllib.parse import urlparse


def is_valid_url(url):
    """Validate if a string is a proper URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url):
    """Normalize a URL by removing fragments and trailing slashes."""
    parsed = urlparse(url)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    return normalized.rstrip('/')
