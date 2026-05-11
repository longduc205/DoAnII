"""
Model Trainer

Trains classification models (Logistic Regression and Random Forest)
to distinguish normal HTTP responses from suspicious ones.

Supports training, evaluation, model comparison, and persistence.

Usage:
    python -m ai.trainer
    python -m ai.trainer --data data/raw/combined_training_data.csv
"""

import argparse
import os
import sys

import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)


class ModelTrainer:
    """Trains and evaluates ML models for response classification."""

    MODELS = {
        'logistic_regression': lambda: LogisticRegression(max_iter=1000, random_state=42),
        'random_forest': lambda: RandomForestClassifier(
            n_estimators=100, random_state=42
        ),
    }

    def __init__(self, model_type='logistic_regression'):
        if model_type not in self.MODELS:
            raise ValueError(f"Unknown model type: {model_type}")
        self.model_type = model_type
        self.model = self.MODELS[model_type]()

    def train(self, X, y, test_size=0.2):
        """Train the model and return evaluation metrics.

        Args:
            X (np.ndarray): Feature matrix (n_samples, n_features).
            y (np.ndarray): Label array (n_samples,).
            test_size (float): Fraction of data held out for testing.

        Returns:
            dict: Evaluation metrics including accuracy, precision,
                  recall, f1_score, confusion_matrix, and a text report.
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='binary', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='binary', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='binary', zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'report': classification_report(y_test, y_pred),
        }

        return metrics

    def save_model(self, path):
        """Save the trained model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)

    def load_model(self, path):
        """Load a trained model from disk."""
        self.model = joblib.load(path)


# ======================================================================
# Comparison & runner helpers
# ======================================================================

def train_and_compare(X_raw, y, test_size=0.2):
    """Train both Logistic Regression and Random Forest, compare metrics.

    Logistic Regression receives *scaled* features (StandardScaler).
    Random Forest receives *raw* features (tree models don't need scaling).

    Args:
        X_raw (np.ndarray): Un-scaled feature matrix.
        y (np.ndarray): Labels.
        test_size (float): Test split ratio.

    Returns:
        tuple: (best_model_name, best_trainer, best_metrics, scaler, all_results)
    """
    from ai.preprocessor import Preprocessor

    preprocessor = Preprocessor()

    # --- Prepare scaled copy for LogisticRegression ---
    X_scaled = preprocessor.fit_transform(X_raw.copy())

    results = {}

    # 1) Logistic Regression (scaled data)
    print("\n[1/2] Training Logistic Regression ...")
    lr_trainer = ModelTrainer('logistic_regression')
    lr_metrics = lr_trainer.train(X_scaled, y, test_size)
    results['logistic_regression'] = {
        'trainer': lr_trainer,
        'metrics': lr_metrics,
    }

    # 2) Random Forest (raw data)
    print("[2/2] Training Random Forest ...")
    rf_trainer = ModelTrainer('random_forest')
    rf_metrics = rf_trainer.train(X_raw, y, test_size)
    results['random_forest'] = {
        'trainer': rf_trainer,
        'metrics': rf_metrics,
    }

    # --- Print comparison table ---
    _print_comparison(results)

    # --- Pick best by F1-Score ---
    best_name = max(results, key=lambda k: results[k]['metrics']['f1_score'])
    best = results[best_name]

    return best_name, best['trainer'], best['metrics'], preprocessor, results


def _print_comparison(results):
    """Pretty-print a comparison table of all trained models."""
    print("\n" + "=" * 64)
    print("            MODEL COMPARISON RESULTS")
    print("=" * 64)

    header = f"{'Metric':<20}"
    for name in results:
        header += f"  {name:<20}"
    print(header)
    print("-" * 64)

    for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
        row = f"{metric:<20}"
        for name in results:
            val = results[name]['metrics'][metric]
            row += f"  {val:<20.4f}"
        print(row)

    print("-" * 64)

    best_name = max(results, key=lambda k: results[k]['metrics']['f1_score'])
    best_f1 = results[best_name]['metrics']['f1_score']
    print(f"  ★ Winner: {best_name} (F1-Score: {best_f1:.4f})")
    print("=" * 64)

    # Print the detailed classification report for the best model
    print(f"\n--- Classification Report ({best_name}) ---")
    print(results[best_name]['metrics']['report'])

    # Print confusion matrix
    cm = results[best_name]['metrics']['confusion_matrix']
    print(f"--- Confusion Matrix ({best_name}) ---")
    print(f"  TN={cm[0][0]}  FP={cm[0][1]}")
    print(f"  FN={cm[1][0]}  TP={cm[1][1]}")
    print()


# ======================================================================
# __main__  — runnable via  `python -m ai.trainer`
# ======================================================================

def _parse_args():
    parser = argparse.ArgumentParser(
        description='Train AI classification model for vulnerability detection'
    )
    parser.add_argument(
        '--data',
        type=str,
        default='data/raw/combined_training_data.csv',
        help='Path to training CSV (default: data/raw/combined_training_data.csv)',
    )
    parser.add_argument(
        '--output-model',
        type=str,
        default='ai/models/classifier.pkl',
        help='Output path for the best model (default: ai/models/classifier.pkl)',
    )
    parser.add_argument(
        '--output-scaler',
        type=str,
        default='ai/models/scaler.pkl',
        help='Output path for the fitted scaler (default: ai/models/scaler.pkl)',
    )
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Fraction of data for testing (default: 0.2)',
    )
    return parser.parse_args()


def main():
    args = _parse_args()

    print("=" * 64)
    print("  AI Web Vulnerability Scanner — Model Training")
    print("=" * 64)

    # 1. Load data
    from ai.preprocessor import Preprocessor
    preprocessor = Preprocessor()

    print(f"\n[*] Loading data from: {args.data}")
    X_raw, y = preprocessor.load_csv(args.data)
    X_raw = preprocessor.handle_missing(X_raw)

    n_normal = int(np.sum(y == 0))
    n_suspicious = int(np.sum(y == 1))
    print(f"    Total samples : {len(y)}")
    print(f"    Normal  (0)   : {n_normal}")
    print(f"    Suspicious (1): {n_suspicious}")

    # 2. Train & compare
    best_name, best_trainer, best_metrics, prep, all_results = train_and_compare(
        X_raw, y, test_size=args.test_size
    )

    # 3. Save best model
    print(f"[*] Saving best model ({best_name}) → {args.output_model}")
    best_trainer.save_model(args.output_model)

    # 4. Save scaler
    print(f"[*] Saving scaler → {args.output_scaler}")
    prep.save_scaler(args.output_scaler)

    print("\n✅ Training complete!")
    print(f"   Model : {args.output_model}")
    print(f"   Scaler: {args.output_scaler}")

    # 5. Quick sanity check — load model back and predict one sample
    print("\n[*] Sanity check: loading model back and predicting first sample ...")
    from ai.predictor import Predictor
    pred = Predictor(model_path=args.output_model)

    sample = X_raw[:1]
    if best_name == 'logistic_regression':
        sample = prep.scale(sample)
    result = pred.predict(sample)
    print(f"    Prediction: {result['classification']} (confidence: {result['confidence']:.4f})")
    print("\nDone. ✓")


if __name__ == '__main__':
    main()
