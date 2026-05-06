"""
AI Analyzer Service

Integrates the AI/ML module into the scanning pipeline.
Classifies HTTP responses as "normal" or "suspicious" using
a trained machine learning model.
"""

import logging

from ai.predictor import Predictor
from ai.feature_extractor import FeatureExtractor
from ai.preprocessor import Preprocessor

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-based response classification service."""

    def __init__(self, model_path=None, confidence_threshold=0.7):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.predictor = Predictor(model_path) if model_path else None
        self.feature_extractor = FeatureExtractor()
        self.preprocessor = Preprocessor()

    def load_model(self):
        """Load the trained ML model from disk."""
        if self.model_path:
            self.predictor = Predictor(self.model_path)
            self.predictor.load(self.model_path)
            logger.info("AI model loaded from %s", self.model_path)

    def classify_response(self, response_data, payload=None):
        """Classify a single response as normal or suspicious.

        Args:
            response_data: dict with keys status_code, content, headers
            payload: optional string - payload used in the test

        Returns:
            dict: {
                'classification': 'normal' | 'suspicious' | 'unknown',
                'confidence': float (0.0-1.0),
                'features': dict,
            }
        """
        features = self.feature_extractor.extract(response_data, payload)

        if self.predictor is None or self.predictor.model is None:
            logger.warning("No model loaded - returning default classification")
            return {
                'classification': 'unknown',
                'confidence': 0.0,
                'features': features,
            }

        feature_vector = self.preprocessor.transform(features)
        result = self.predictor.predict(feature_vector)

        return {
            'classification': result['classification'],
            'confidence': result['confidence'],
            'features': features,
        }

    def classify_batch(self, responses):
        """Classify a batch of responses.

        Args:
            responses: list of dicts with response_data and optional payload

        Returns:
            list of classification dicts
        """
        results = []
        for resp in responses:
            result = self.classify_response(
                resp.get('response_data', {}),
                resp.get('payload'),
            )
            results.append(result)
        return results
