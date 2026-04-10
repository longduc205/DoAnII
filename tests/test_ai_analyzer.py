"""Tests for AI Analyzer"""

import pytest
from ai.feature_extractor import FeatureExtractor


class TestFeatureExtractor:
    """Test suite for the feature extractor."""

    def test_extract_basic(self):
        """Test basic feature extraction."""
        extractor = FeatureExtractor()
        response = {
            'content': '<html><body>Hello World</body></html>',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html'},
        }
        features = extractor.extract(response)
        assert features['status_code'] == 200
        assert features['response_length'] > 0
        assert features['content_type_html'] is True

    def test_sql_keyword_detection(self):
        """Test SQL keyword detection in response."""
        extractor = FeatureExtractor()
        response = {
            'content': 'You have an error in your SQL syntax near...',
            'status_code': 500,
            'headers': {},
        }
        features = extractor.extract(response)
        assert features['has_sql_keywords'] is True

    def test_xss_reflection_detection(self):
        """Test XSS payload reflection detection."""
        extractor = FeatureExtractor()
        payload = '<script>alert(1)</script>'
        response = {
            'content': f'<html><body>{payload}</body></html>',
            'status_code': 200,
            'headers': {},
        }
        features = extractor.extract(response, payload=payload)
        assert features['has_xss_reflection'] is True
