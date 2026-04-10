"""
Data Preprocessor

Transforms raw feature dictionaries into
numpy arrays suitable for ML model input.
"""

import numpy as np


class Preprocessor:
    """Preprocesses feature data for ML model consumption."""

    FEATURE_COLUMNS = [
        'response_length',
        'status_code',
        'has_sql_keywords',
        'sql_keyword_count',
        'has_xss_reflection',
        'xss_keyword_count',
        'content_type_html',
    ]

    def transform(self, features_dict):
        """Transform a single feature dictionary into a numpy array."""
        vector = []
        for col in self.FEATURE_COLUMNS:
            value = features_dict.get(col, 0)
            # Convert booleans to int
            if isinstance(value, bool):
                value = int(value)
            vector.append(value)
        return np.array(vector).reshape(1, -1)

    def transform_batch(self, features_list):
        """Transform a list of feature dictionaries into a 2D numpy array."""
        vectors = []
        for features in features_list:
            vector = []
            for col in self.FEATURE_COLUMNS:
                value = features.get(col, 0)
                if isinstance(value, bool):
                    value = int(value)
                vector.append(value)
            vectors.append(vector)
        return np.array(vectors)
