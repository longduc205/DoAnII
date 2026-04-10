"""
Predictor

Uses a trained model to classify new responses.
"""

import joblib
import numpy as np


class Predictor:
    """Loads a trained model and makes predictions."""

    def __init__(self, model_path=None):
        self.model = None
        if model_path:
            self.load(model_path)

    def load(self, model_path):
        """Load a trained model from disk."""
        self.model = joblib.load(model_path)

    def predict(self, features_array):
        """
        Predict classification for feature array.

        Returns:
            dict with 'label' (0=normal, 1=suspicious) and 'confidence'
        """
        if self.model is None:
            raise RuntimeError("No model loaded. Call load() first.")

        prediction = self.model.predict(features_array)
        probabilities = self.model.predict_proba(features_array)

        return {
            'label': int(prediction[0]),
            'classification': 'suspicious' if prediction[0] == 1 else 'normal',
            'confidence': float(np.max(probabilities[0])),
        }

    def predict_batch(self, features_array):
        """Predict classifications for a batch of features."""
        if self.model is None:
            raise RuntimeError("No model loaded. Call load() first.")

        predictions = self.model.predict(features_array)
        probabilities = self.model.predict_proba(features_array)

        results = []
        for i, pred in enumerate(predictions):
            results.append({
                'label': int(pred),
                'classification': 'suspicious' if pred == 1 else 'normal',
                'confidence': float(np.max(probabilities[i])),
            })
        return results
