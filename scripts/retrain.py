"""
Regenerate synthetic training data and retrain the model.
Run inside Docker: python3 scripts/retrain.py
"""
import sys
import os
sys.path.insert(0, '/app')

from ai.data_collector import TrainingDataCollector
from ai.preprocessor import Preprocessor

print("=" * 64)
print("  Step 1: Generate improved synthetic training data")
print("=" * 64)

collector = TrainingDataCollector()
collector.generate_synthetic(n_normal=200, n_suspicious=200, seed=42)
n_normal, n_suspicious = collector.get_sample_count()
print(f"  Normal: {n_normal}, Suspicious: {n_suspicious}")
collector.save_to_csv('data/raw/combined_training_data.csv')

print("\n" + "=" * 64)
print("  Step 2: Train model")
print("=" * 64)

# Now run the trainer
from ai.trainer import main as train_main
sys.argv = [
    'trainer',
    '--data', 'data/raw/combined_training_data.csv',
    '--output-model', 'ai/models/classifier.pkl',
    '--output-scaler', 'ai/models/scaler.pkl',
]
train_main()

print("\n" + "=" * 64)
print("  Step 3: Test prediction on blind SQLi case")
print("=" * 64)

from ai.feature_extractor import FeatureExtractor
from ai.predictor import Predictor

extractor = FeatureExtractor()
preprocessor = Preprocessor()

# Simulate the REAL case from the screenshot:
# status_code=200, response_length=4873, baseline=3235, no SQL errors
blind_sqli_response = {
    'content': '<html><body>' + 'x' * 4860 + '</body></html>',
    'status_code': 200,
    'headers': {'Content-Type': 'text/html'},
}
features = extractor.extract(
    blind_sqli_response,
    payload="' OR 1=1--",
    baseline_length=3235,
)
print(f"\n  Test features (blind SQLi case):")
for k, v in features.items():
    print(f"    {k}: {v}")

feature_vector = preprocessor.transform(features)
predictor = Predictor(model_path='ai/models/classifier.pkl')
result = predictor.predict(feature_vector)
print(f"\n  => AI Prediction: {result['classification']} (confidence: {result['confidence']:.2%})")

if result['classification'] == 'suspicious':
    print("  ✅ SUCCESS: AI now correctly identifies blind SQLi as suspicious!")
else:
    print("  ⚠️  AI still classifies as normal — may need more training data or tuning")

# Also test a normal case to make sure we don't have false positives
print("\n  --- Normal case check ---")
normal_response = {
    'content': '<html><body><h1>Welcome</h1><p>Normal page.</p></body></html>',
    'status_code': 200,
    'headers': {'Content-Type': 'text/html'},
}
normal_features = extractor.extract(
    normal_response,
    payload=None,
    baseline_length=65,
)
normal_vector = preprocessor.transform(normal_features)
normal_result = predictor.predict(normal_vector)
print(f"  => AI Prediction: {normal_result['classification']} (confidence: {normal_result['confidence']:.2%})")

if normal_result['classification'] == 'normal':
    print("  ✅ Normal page still correctly classified as normal")
else:
    print("  ⚠️  False positive — normal page classified as suspicious")
