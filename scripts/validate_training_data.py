#!/usr/bin/env python3
"""
Training Data Validator

Validates the quality and correctness of generated training data.
Checks label distribution, feature ranges, and data integrity.

Usage:
    python scripts/validate_training_data.py data/raw/training_data.csv
"""

import argparse
import sys

try:
    import pandas as pd
except ImportError:
    print("[ERROR] pandas is required for validation. Install with: pip install pandas")
    sys.exit(1)


def validate_data(csv_path):
    """Validate training data CSV file.
    
    Args:
        csv_path (str): Path to CSV file
        
    Returns:
        bool: True if all checks pass, False otherwise
    """
    print(f"[Validator] Loading {csv_path}...")
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {csv_path}")
        return False
    except Exception as e:
        print(f"[ERROR] Cannot read CSV: {e}")
        return False
    
    print(f"[Validator] Running validation checks...\n")
    
    all_passed = True
    
    # Check 1: Row count
    print(f"✓ Total rows: {len(df)}")
    
    # Check 2: Column count
    expected_columns = [
        'response_length', 'status_code', 'has_sql_keywords', 'sql_keyword_count',
        'has_xss_reflection', 'xss_keyword_count', 'content_type_html',
        'error_page_detected', 'has_redirect', 'length_delta', 'label'
    ]
    if list(df.columns) == expected_columns:
        print(f"✓ Columns: {len(df.columns)} (correct)")
    else:
        print(f"✗ Columns mismatch!")
        print(f"  Expected: {expected_columns}")
        print(f"  Got: {list(df.columns)}")
        all_passed = False
    
    # Check 3: Label distribution
    label_counts = df['label'].value_counts().sort_index()
    print(f"✓ Label distribution:")
    for label, count in label_counts.items():
        pct = count / len(df) * 100
        print(f"    label={label}: {count} ({pct:.1f}%)")
    
    # Check 4: No missing values
    missing = df.isnull().sum().sum()
    if missing == 0:
        print(f"✓ Missing values: 0")
    else:
        print(f"✗ Missing values: {missing}")
        all_passed = False
    
    # Check 5: Normal samples should have no SQL/XSS indicators
    normal_df = df[df['label'] == 0]
    normal_with_sql = normal_df[normal_df['has_sql_keywords'] == 1]
    normal_with_xss = normal_df[normal_df['has_xss_reflection'] == 1]
    
    if len(normal_with_sql) == 0 and len(normal_with_xss) == 0:
        print(f"✓ Normal samples: clean (no SQL/XSS indicators)")
    else:
        print(f"✗ Normal samples have indicators:")
        print(f"    With SQL keywords: {len(normal_with_sql)}")
        print(f"    With XSS reflection: {len(normal_with_xss)}")
        all_passed = False
    
    # Check 6: Suspicious samples should have SQL or XSS indicators
    suspicious_df = df[df['label'] == 1]
    suspicious_with_indicators = suspicious_df[
        (suspicious_df['has_sql_keywords'] == 1) | 
        (suspicious_df['has_xss_reflection'] == 1)
    ]
    
    if len(suspicious_with_indicators) == len(suspicious_df):
        print(f"✓ Suspicious samples: all have indicators")
    else:
        missing_indicators = len(suspicious_df) - len(suspicious_with_indicators)
        print(f"✗ Suspicious samples missing indicators: {missing_indicators}")
        all_passed = False
    
    # Check 7: Feature value ranges
    print(f"✓ Feature ranges:")
    print(f"    response_length: {df['response_length'].min()}-{df['response_length'].max()}")
    print(f"    status_code: {df['status_code'].unique()}")
    print(f"    sql_keyword_count: {df['sql_keyword_count'].min()}-{df['sql_keyword_count'].max()}")
    print(f"    xss_keyword_count: {df['xss_keyword_count'].min()}-{df['xss_keyword_count'].max()}")
    
    # Check 8: Status code distribution
    print(f"✓ Status code distribution:")
    status_counts = df['status_code'].value_counts().sort_index()
    for status, count in status_counts.items():
        pct = count / len(df) * 100
        print(f"    {status}: {count} ({pct:.1f}%)")
    
    print()
    if all_passed:
        print("[Validator] ✓ All checks passed!")
        return True
    else:
        print("[Validator] ✗ Some checks failed")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Validate training data CSV')
    parser.add_argument('csv_path', help='Path to training data CSV file')
    args = parser.parse_args()
    
    success = validate_data(args.csv_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
