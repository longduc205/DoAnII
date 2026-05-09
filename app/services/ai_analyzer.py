"""
AI Analyzer Service

Integrates the AI/ML module into the scanning pipeline.
Classifies HTTP responses as "normal" or "suspicious" using
a trained machine learning model.

This service is the bridge between the scanner engine and the
AI prediction module.
"""

import logging
import os

from ai.predictor import Predictor
from ai.feature_extractor import FeatureExtractor
from ai.preprocessor import Preprocessor

logger = logging.getLogger(__name__)

# Default model artifact paths (relative to project root)
DEFAULT_MODEL_PATH = 'ai/models/classifier.pkl'
DEFAULT_SCALER_PATH = 'ai/models/scaler.pkl'


class AIAnalyzer:
    """AI-based response classification service."""

    def __init__(self, model_path=None, scaler_path=None,
                 confidence_threshold=0.7):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.scaler_path = scaler_path or DEFAULT_SCALER_PATH
        self.confidence_threshold = confidence_threshold
        self.feature_extractor = FeatureExtractor()
        self.preprocessor = Preprocessor()
        self.predictor = None
        self.model_loaded = False

        # Try to load model and scaler
        self._safe_load()

    def _safe_load(self):
        """Attempt to load the model and scaler, logging warnings on failure."""
        if not os.path.isfile(self.model_path):
            logger.warning(
                "AI model not found at %s — AI classification disabled. "
                "Run 'python -m ai.trainer' to train a model.",
                self.model_path,
            )
            return

        try:
            self.predictor = Predictor(
                model_path=self.model_path,
                scaler_path=self.scaler_path,
            )
            self.model_loaded = self.predictor.model is not None
            if self.model_loaded:
                logger.info("AI model loaded successfully from %s", self.model_path)
            else:
                logger.warning("AI model file exists but failed to load")
        except Exception as exc:
            logger.error("Failed to load AI model: %s", exc)
            self.predictor = None
            self.model_loaded = False

    def is_available(self):
        """Check if the AI model is loaded and ready for classification."""
        return self.model_loaded and self.predictor is not None

    def classify_response(self, response_data, payload=None,
                          baseline_length=None):
        """Classify a single response as normal or suspicious.

        Args:
            response_data: dict with keys status_code, content, headers
            payload: optional string - payload used in the test
            baseline_length: optional int - baseline response length

        Returns:
            dict: {
                'classification': 'normal' | 'suspicious' | 'unknown',
                'confidence': float (0.0-1.0),
                'features': dict,
            }
        """
        features = self.feature_extractor.extract(
            response_data, payload, baseline_length
        )

        if not self.is_available():
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

    def classify_finding(self, finding):
        """Classify a vulnerability finding using its attached response_data.

        Args:
            finding (dict): A finding dict from VulnerabilityDetector,
                            expected to contain 'response_data' and 'payload'.

        Returns:
            dict: AI classification result with classification, confidence,
                  and features. Returns 'unknown' if response_data is missing
                  or model is not loaded.
        """
        response_data = finding.get('response_data')
        if not response_data:
            logger.debug("No response_data in finding — skipping AI classification")
            return {
                'classification': 'unknown',
                'confidence': 0.0,
                'features': {},
            }

        payload = finding.get('payload')
        baseline_length = finding.get('baseline_length')

        return self.classify_response(
            response_data, payload, baseline_length
        )

    def classify_findings(self, findings):
        """Classify a batch of vulnerability findings.

        Args:
            findings (list[dict]): List of finding dicts from detector.

        Returns:
            list[dict]: Classification results, one per finding.
        """
        results = []
        for finding in findings:
            result = self.classify_finding(finding)
            results.append(result)
        return results

    def classify_batch(self, responses):
        """Classify a batch of responses (legacy API).

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
