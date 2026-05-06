"""Tests for AIAnalyzer"""

import pytest
from app.services.ai_analyzer import AIAnalyzer


class TestAIAnalyzer:
    """Test suite for the AI analyzer service."""

    def test_init_without_model(self):
        """Test initialization without a Model path."""
        analyzer = AIAnalyzer()
        assert analyzer.model_path is None
        assert analyzer.predictor is None
        assert analyzer.confidence_threshold == 0.7

    def test_init_with_model_path(self):
        """Test initialization with a Model path (model not loaded yet)."""
        analyzer = AIAnalyzer(model_path='ai/models/classifier.pkl')
        assert analyzer.model_path == 'ai/models/classifier.pkl'
        assert analyzer.predictor is not None

    def test_classify_response_without_model(self):
        """Test classification returns 'unknown' when no model is loaded."""
        analyzer = AIAnalyzer()
        response = {
            'content': '<html>Hello</html>',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html'},
        }
        result = analyzer.classify_response(response)
        assert result['classification'] == 'unknown'
        assert result['confidence'] == 0.0
        assert 'features' in result

    def test_classify_response_extracts_features(self):
        """Test that features are extracted even without a model."""
        analyzer = AIAnalyzer()
        response = {
            'content': 'You have an error in your SQL syntax near...',
            'status_code': 500,
            'headers': {},
        }
        result = analyzer.classify_response(response)
        features = result['features']
        assert features['status_code'] == 500
        assert features['has_sql_keywords'] is True
        assert features['sql_keyword_count'] > 0

    def test_classify_batch(self):
        """Test batch classification of multiple responses."""
        analyzer = AIAnalyzer()
        responses = [
            {'response_data': {'content': 'normal page', 'status_code': 200, 'headers': {}}, 'payload': None},
            {'response_data': {'content': 'sql error here', 'status_code': 500, 'headers': {}}, 'payload': None},
        ]
        results = analyzer.classify_batch(responses)
        assert len(results) == 2
        assert all('classification' in r for r in results)
