"""Quick analysis of the training data."""
import pandas as pd

df = pd.read_csv('data/raw/combined_training_data.csv')
print("Shape:", df.shape)
print("\nLabel distribution:")
print(df['label'].value_counts())
print("\nFeature stats:")
print(df.describe().to_string())
print("\n--- Suspicious samples (label=1) ---")
sus = df[df['label'] == 1]
print(f"status_code distribution: {sus['status_code'].value_counts().to_dict()}")
print(f"has_sql_keywords: {sus['has_sql_keywords'].value_counts().to_dict()}")
print(f"length_delta mean: {sus['length_delta'].mean():.1f}, max: {sus['length_delta'].max()}")
print(f"response_length mean: {sus['response_length'].mean():.1f}")

print("\n--- Normal samples (label=0) ---")
norm = df[df['label'] == 0]
print(f"status_code distribution: {norm['status_code'].value_counts().to_dict()}")
print(f"response_length mean: {norm['response_length'].mean():.1f}")
print(f"length_delta mean: {norm['length_delta'].mean():.1f}")
