"""
Model Trainer

Trains a classification model to distinguish
normal responses from suspicious ones.
"""

import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble_import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report
)


class ModelTrainer:
    """Trains and evaluates ML models for response classification."""

    MODELS = {
        'logistic_regression': LogisticRegression,
        'random_forest': RandomForestClassifier,
    }

    def __init__(self, model_type='logistic_regression'):
        if model_type not in self.MODELS:
            raise ValueError(f"Unknown model type: {model_type}")
        self.model_type = model_type
        self.model = self.MODELS[model_type]()

    def train(self, X, y, test_size=0.2):
        """Train the model and return evaluation metrics."""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='binary', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='binary', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='binary', zero_division=0),
            'report': classification_report(y_test, y_pred),
        }

        return metrics

    def save_model(self, path):
        """Save the trained model to disk."""
        joblib.dump(self.model, path)

    def load_model(self, path):
        """Load a trained model from disk."""
        self.model = joblib.load(path)
