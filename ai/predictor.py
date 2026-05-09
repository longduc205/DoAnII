"""
Predictor

Uses a trained model to classify new HTTP responses.
Optionally applies a fitted StandardScaler before prediction
(required for Logistic Regression, optional for Random Forest).
"""

import logging
import os

import joblib
import numpy as np

logger = logging.getLogger(__name__)


class Predictor:
    """Loads a trained model and makes predictions."""

    def __init__(self, model_path=None, scaler_path=None):
        self.model = None
        self.scaler = None
        if model_path:
            self.load(model_path)
        if scaler_path:
            self.load_scaler(scaler_path)

    def load(self, model_path):
        """Load a trained model from disk."""
        if not os.path.isfile(model_path):
            logger.warning("Model file not found: %s", model_path)
            return
        self.model = joblib.load(model_path)
        logger.info("Model loaded from %s", model_path)

    def load_scaler(self, scaler_path):
        """Load a fitted scaler from disk."""
        if not os.path.isfile(scaler_path):
            logger.warning("Scaler file not found: %s — predictions will use raw features", scaler_path)
            return
        self.scaler = joblib.load(scaler_path)
        logger.info("Scaler loaded from %s", scaler_path)

    def _maybe_scale(self, features_array):
        """Apply scaler if one is loaded, otherwise return as-is."""
        if self.scaler is not None:
            return self.scaler.transform(features_array)
        return features_array

    def predict(self, features_array):
        """
        Predict classification for feature array.

        Returns:
            dict with 'label' (0=normal, 1=suspicious), 'classification',
            and 'confidence'
        """
        if self.model is None:
            raise RuntimeError("No model loaded. Call load() first.")

        scaled = self._maybe_scale(features_array)
        prediction = self.model.predict(scaled)
        probabilities = self.model.predict_proba(scaled)

        return {
            'label': int(prediction[0]),
            'classification': 'suspicious' if prediction[0] == 1 else 'normal',
            'confidence': float(np.max(probabilities[0])),
        }

    def predict_batch(self, features_array):
        """Predict classifications for a batch of features."""
        if self.model is None:
            raise RuntimeError("No model loaded. Call load() first.")

        scaled = self._maybe_scale(features_array)
        predictions = self.model.predict(scaled)
        probabilities = self.model.predict_proba(scaled)

        results = []
        for i, pred in enumerate(predictions):
            results.append({
                'label': int(pred),
                'classification': 'suspicious' if pred == 1 else 'normal',
                'confidence': float(np.max(probabilities[i])),
            })
        return results
