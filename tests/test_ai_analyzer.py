"""Tests for AIAnalyzer"""

import pytest
from app.services.ai_analyzer import AIAnalyzer


class TestAIAnalyzer:
    """Test suite for the AI analyzer service."""

    def test_init_default_paths(self):
        """Test initialization uses default model paths."""
        analyzer = AIAnalyzer()
        assert analyzer.model_path == 'ai/models/classifier.pkl'
        assert analyzer.scaler_path == 'ai/models/scaler.pkl'
        assert analyzer.confidence_threshold == 0.7

    def test_init_with_missing_model(self):
        """Test initialization with a non-existent model path."""
        analyzer = AIAnalyzer(model_path='nonexistent/model.pkl')
        assert analyzer.model_loaded is False
        assert analyzer.predictor is None

    def test_init_with_model_path(self):
        """Test initialization with the real model path."""
        analyzer = AIAnalyzer(model_path='ai/models/classifier.pkl')
        assert analyzer.model_path == 'ai/models/classifier.pkl'
        assert analyzer.predictor is not None

    def test_is_available_with_model(self):
        """Test is_available() returns True when model is loaded."""
        analyzer = AIAnalyzer(model_path='ai/models/classifier.pkl')
        assert analyzer.is_available() is True

    def test_is_available_without_model(self):
        """Test is_available() returns False when model is missing."""
        analyzer = AIAnalyzer(model_path='nonexistent/model.pkl')
        assert analyzer.is_available() is False

    def test_classify_response_without_model(self):
        """Test classification returns 'unknown' when no model is loaded."""
        analyzer = AIAnalyzer(model_path='nonexistent/model.pkl')
        response = {
            'content': '<html>Hello</html>',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html'},
        }
        result = analyzer.classify_response(response)
        assert result['classification'] == 'unknown'
        assert result['confidence'] == 0.0
        assert 'features' in result

    def test_classify_response_with_model(self):
        """Test classification works when model is loaded."""
        analyzer = AIAnalyzer(model_path='ai/models/classifier.pkl')
        if not analyzer.is_available():
            pytest.skip("Model not available")

        # Normal response
        response = {
            'content': '<html>Hello</html>',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html'},
        }
        result = analyzer.classify_response(response)
        assert result['classification'] in ('normal', 'suspicious')
        assert 0.0 <= result['confidence'] <= 1.0
        assert 'features' in result

    def test_classify_response_extracts_features(self):
        """Test that features are extracted even without a model."""
        analyzer = AIAnalyzer(model_path='nonexistent/model.pkl')
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

    def test_classify_finding(self):
        """Test classify_finding with response_data attached."""
        analyzer = AIAnalyzer(model_path='ai/models/classifier.pkl')
        if not analyzer.is_available():
            pytest.skip("Model not available")

        finding = {
            'vuln_type': 'sqli',
            'url': 'http://example.com/vuln',
            'payload': "' OR 1=1--",
            'baseline_length': 100,
            'response_data': {
                'status_code': 500,
                'content': 'SQL syntax error near...',
                'headers': {'Content-Type': 'text/html'},
            },
        }
        result = analyzer.classify_finding(finding)
        assert result['classification'] in ('normal', 'suspicious')
        assert 0.0 <= result['confidence'] <= 1.0

    def test_classify_finding_without_response_data(self):
        """Test classify_finding returns 'unknown' when no response_data."""
        analyzer = AIAnalyzer()
        finding = {
            'vuln_type': 'sqli',
            'url': 'http://example.com/vuln',
        }
        result = analyzer.classify_finding(finding)
        assert result['classification'] == 'unknown'
        assert result['confidence'] == 0.0

    def test_classify_batch(self):
        """Test batch classification of multiple responses."""
        analyzer = AIAnalyzer(model_path='nonexistent/model.pkl')
        responses = [
            {'response_data': {'content': 'normal page', 'status_code': 200, 'headers': {}}, 'payload': None},
            {'response_data': {'content': 'sql error here', 'status_code': 500, 'headers': {}}, 'payload': None},
        ]
        results = analyzer.classify_batch(responses)
        assert len(results) == 2
        assert all('classification' in r for r in results)

    def test_classify_findings_batch(self):
        """Test batch classification of findings."""
        analyzer = AIAnalyzer(model_path='ai/models/classifier.pkl')
        if not analyzer.is_available():
            pytest.skip("Model not available")

        findings = [
            {
                'vuln_type': 'sqli',
                'url': 'http://example.com/1',
                'payload': "' OR 1=1--",
                'response_data': {
                    'status_code': 500,
                    'content': 'SQL error',
                    'headers': {},
                },
            },
            {
                'vuln_type': 'xss',
                'url': 'http://example.com/2',
                'payload': '<script>alert(1)</script>',
                'response_data': {
                    'status_code': 200,
                    'content': '<script>alert(1)</script>',
                    'headers': {'Content-Type': 'text/html'},
                },
            },
        ]
        results = analyzer.classify_findings(findings)
        assert len(results) == 2
        assert all('classification' in r for r in results)
        assert all('confidence' in r for r in results)
