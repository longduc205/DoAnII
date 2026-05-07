"""
Data Preprocessor

Transforms raw feature dictionaries into numpy arrays suitable for ML
model input, and optionally normalises numeric columns with a
StandardScaler so that large-range features (e.g. response_length)
don't dominate the model.

Usage (training time):
    preprocessor = Preprocessor()
    X = preprocessor.transform_batch(features_list)   # raw array
    X_scaled = preprocessor.fit_transform(X)           # fit + scale
    preprocessor.save_scaler('ai/models/scaler.pkl')

Usage (inference time):
    preprocessor = Preprocessor()
    preprocessor.load_scaler('ai/models/scaler.pkl')
    x = preprocessor.transform(features_dict)          # single sample
    x_scaled = preprocessor.scale(x)
"""

import joblib
import numpy as np


class Preprocessor:
    """Preprocesses feature data for ML model consumption."""

    # Must stay in sync with FeatureExtractor.extract() output keys.
    FEATURE_COLUMNS = [
        'response_length',
        'status_code',
        'has_sql_keywords',
        'sql_keyword_count',
        'has_xss_reflection',
        'xss_keyword_count',
        'content_type_html',
        'error_page_detected',
        'has_redirect',
        'length_delta',
    ]

    def __init__(self):
        self.scaler = None  # set after fit_transform() or load_scaler()

    # ------------------------------------------------------------------
    # Core transform helpers
    # ------------------------------------------------------------------

    def _dict_to_vector(self, features_dict):
        """Convert a feature dict to a plain Python list (in column order)."""
        vector = []
        for col in self.FEATURE_COLUMNS:
            value = features_dict.get(col, 0)
            if isinstance(value, bool):
                value = int(value)
            vector.append(value)
        return vector

    def transform(self, features_dict):
        """Transform a single feature dict into a (1, n_features) numpy array."""
        return np.array(self._dict_to_vector(features_dict)).reshape(1, -1)

    def transform_batch(self, features_list):
        """Transform a list of feature dicts into a (n_samples, n_features) array."""
        return np.array([self._dict_to_vector(f) for f in features_list])

    # ------------------------------------------------------------------
    # Scaling (optional but recommended for Logistic Regression)
    # ------------------------------------------------------------------

    def fit_transform(self, X):
        """Fit a StandardScaler on X and return the scaled array.

        Args:
            X (np.ndarray): Shape (n_samples, n_features).

        Returns:
            np.ndarray: Scaled array with same shape.
        """
        from sklearn.preprocessing import StandardScaler
        self.scaler = StandardScaler()
        return self.scaler.fit_transform(X)

    def scale(self, X):
        """Apply the already-fitted scaler to X.

        Args:
            X (np.ndarray): Shape (1, n_features) or (n_samples, n_features).

        Returns:
            np.ndarray: Scaled array.
        """
        if self.scaler is None:
            # No scaler fitted — return as-is (e.g. RandomForest doesn't need it)
            return X
        return self.scaler.transform(X)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_scaler(self, path):
        """Persist the fitted scaler to disk."""
        if self.scaler is None:
            raise RuntimeError("No scaler fitted yet. Call fit_transform() first.")
        joblib.dump(self.scaler, path)

    def load_scaler(self, path):
        """Load a previously saved scaler from disk."""
        self.scaler = joblib.load(path)
