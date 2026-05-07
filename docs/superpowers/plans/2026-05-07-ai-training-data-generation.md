# AI Training Data Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone script that generates 1000 synthetic labeled training samples (500 normal + 500 suspicious) and saves them to CSV format for ML model training.

**Architecture:** Build a CLI script that leverages existing `TrainingDataCollector` and `FeatureExtractor` classes to programmatically generate realistic HTTP response samples with extracted features, then export to CSV.

**Tech Stack:** Python 3, argparse (CLI), existing ai/ modules (data_collector, feature_extractor)

---

## File Structure

**New Files:**
- `scripts/generate_training_data.py` - Main executable script with CLI interface

**Existing Files (No Modifications):**
- `ai/data_collector.py` - Already implements `generate_synthetic()` and `save_to_csv()`
- `ai/feature_extractor.py` - Already implements feature extraction logic

**Output Files:**
- `data/raw/training_data.csv` - Generated dataset (1000 rows × 11 columns)

---

## Task 1: Create Script Directory Structure

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/generate_training_data.py`

- [ ] **Step 1: Create scripts directory if it doesn't exist**

Run: `mkdir -p scripts`

- [ ] **Step 2: Create empty __init__.py**

```bash
touch scripts/__init__.py
```

- [ ] **Step 3: Create script file with shebang and docstring**

```python
#!/usr/bin/env python3
"""
Training Data Generator

Generates synthetic labeled HTTP response samples for ML model training.
Creates realistic normal and suspicious response features without requiring
a live vulnerable target.

Usage:
    python scripts/generate_training_data.py
    python scripts/generate_training_data.py --normal 200 --suspicious 200
    python scripts/generate_training_data.py --seed 123 --output data/custom.csv
"""

import sys


def main():
    """Main entry point."""
    print("[DataGenerator] Starting...")


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: Test script runs**

Run: `python scripts/generate_training_data.py`
Expected: Prints "[DataGenerator] Starting..."

- [ ] **Step 5: Commit**

```bash
git add scripts/__init__.py scripts/generate_training_data.py
git commit -m "feat(ai): add training data generation script skeleton"
```

---

## Task 2: Implement CLI Argument Parsing

**Files:**
- Modify: `scripts/generate_training_data.py`

- [ ] **Step 1: Add argparse imports and argument parser**

```python
#!/usr/bin/env python3
"""
Training Data Generator

Generates synthetic labeled HTTP response samples for ML model training.
Creates realistic normal and suspicious response features without requiring
a live vulnerable target.

Usage:
    python scripts/generate_training_data.py
    python scripts/generate_training_data.py --normal 200 --suspicious 200
    python scripts/generate_training_data.py --seed 123 --output data/custom.csv
"""

import argparse
import sys


def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments with attributes:
            - normal (int): Number of normal samples
            - suspicious (int): Number of suspicious samples
            - seed (int): Random seed for reproducibility
            - output (str): Output CSV file path
    """
    parser = argparse.ArgumentParser(
        description='Generate synthetic training data for vulnerability classification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate default 500+500 samples
  python scripts/generate_training_data.py
  
  # Generate custom sample counts
  python scripts/generate_training_data.py --normal 200 --suspicious 200
  
  # Use custom seed and output path
  python scripts/generate_training_data.py --seed 123 --output data/train.csv
        """
    )
    
    parser.add_argument(
        '--normal',
        type=int,
        default=500,
        help='Number of normal (non-vulnerable) samples to generate (default: 500)'
    )
    
    parser.add_argument(
        '--suspicious',
        type=int,
        default=500,
        help='Number of suspicious (vulnerable) samples to generate (default: 500)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='data/raw/training_data.csv',
        help='Output CSV file path (default: data/raw/training_data.csv)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.normal <= 0:
        parser.error('--normal must be a positive integer')
    if args.suspicious <= 0:
        parser.error('--suspicious must be a positive integer')
    if args.seed < 0:
        parser.error('--seed must be a non-negative integer')
    
    return args


def main():
    """Main entry point."""
    args = parse_arguments()
    
    print(f"[DataGenerator] Configuration:")
    print(f"  Normal samples: {args.normal}")
    print(f"  Suspicious samples: {args.suspicious}")
    print(f"  Random seed: {args.seed}")
    print(f"  Output path: {args.output}")


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Test default arguments**

Run: `python scripts/generate_training_data.py`
Expected: Prints configuration with default values (500, 500, 42, data/raw/training_data.csv)

- [ ] **Step 3: Test custom arguments**

Run: `python scripts/generate_training_data.py --normal 100 --suspicious 100 --seed 999`
Expected: Prints configuration with custom values (100, 100, 999, data/raw/training_data.csv)

- [ ] **Step 4: Test help text**

Run: `python scripts/generate_training_data.py --help`
Expected: Displays usage help with all options and examples

- [ ] **Step 5: Test argument validation**

Run: `python scripts/generate_training_data.py --normal -10`
Expected: Error message "error: --normal must be a positive integer"

- [ ] **Step 6: Commit**

```bash
git add scripts/generate_training_data.py
git commit -m "feat(ai): add CLI argument parsing for data generator"
```

---

## Task 3: Implement Data Generation Logic

**Files:**
- Modify: `scripts/generate_training_data.py`

- [ ] **Step 1: Add imports for data collector**

```python
#!/usr/bin/env python3
"""
Training Data Generator

Generates synthetic labeled HTTP response samples for ML model training.
Creates realistic normal and suspicious response features without requiring
a live vulnerable target.

Usage:
    python scripts/generate_training_data.py
    python scripts/generate_training_data.py --normal 200 --suspicious 200
    python scripts/generate_training_data.py --seed 123 --output data/custom.csv
"""

import argparse
import os
import sys

# Add project root to path so we can import ai modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.data_collector import TrainingDataCollector


def parse_arguments():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments with attributes:
            - normal (int): Number of normal samples
            - suspicious (int): Number of suspicious samples
            - seed (int): Random seed for reproducibility
            - output (str): Output CSV file path
    """
    parser = argparse.ArgumentParser(
        description='Generate synthetic training data for vulnerability classification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate default 500+500 samples
  python scripts/generate_training_data.py
  
  # Generate custom sample counts
  python scripts/generate_training_data.py --normal 200 --suspicious 200
  
  # Use custom seed and output path
  python scripts/generate_training_data.py --seed 123 --output data/train.csv
        """
    )
    
    parser.add_argument(
        '--normal',
        type=int,
        default=500,
        help='Number of normal (non-vulnerable) samples to generate (default: 500)'
    )
    
    parser.add_argument(
        '--suspicious',
        type=int,
        default=500,
        help='Number of suspicious (vulnerable) samples to generate (default: 500)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='data/raw/training_data.csv',
        help='Output CSV file path (default: data/raw/training_data.csv)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.normal <= 0:
        parser.error('--normal must be a positive integer')
    if args.suspicious <= 0:
        parser.error('--suspicious must be a positive integer')
    if args.seed < 0:
        parser.error('--seed must be a non-negative integer')
    
    return args


def generate_data(n_normal, n_suspicious, seed, output_path):
    """Generate synthetic training data and save to CSV.
    
    Args:
        n_normal (int): Number of normal samples
        n_suspicious (int): Number of suspicious samples
        seed (int): Random seed
        output_path (str): Output CSV file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"[DataGenerator] Starting synthetic data generation...")
        
        # Initialize collector
        collector = TrainingDataCollector()
        
        # Generate samples
        print(f"[DataGenerator] Generating {n_normal} normal samples...")
        print(f"[DataGenerator] Generating {n_suspicious} suspicious samples...")
        collector.generate_synthetic(
            n_normal=n_normal,
            n_suspicious=n_suspicious,
            seed=seed
        )
        
        # Get sample counts for verification
        n_normal_actual, n_suspicious_actual = collector.get_sample_count()
        
        # Save to CSV
        print(f"[DataGenerator] Saving to {output_path}...")
        collector.save_to_csv(output_path)
        
        # Get file size
        file_size_bytes = os.path.getsize(output_path)
        file_size_kb = file_size_bytes / 1024
        
        # Print success summary
        print(f"[DataGenerator] ✓ Success!\n")
        print(f"Summary:")
        print(f"  Total samples: {n_normal_actual + n_suspicious_actual}")
        print(f"  Normal (label=0): {n_normal_actual} ({n_normal_actual/(n_normal_actual+n_suspicious_actual)*100:.1f}%)")
        print(f"  Suspicious (label=1): {n_suspicious_actual} ({n_suspicious_actual/(n_normal_actual+n_suspicious_actual)*100:.1f}%)")
        print(f"  Output file: {output_path}")
        print(f"  File size: ~{file_size_kb:.1f} KB")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Cannot import required modules: {e}", file=sys.stderr)
        print(f"        Make sure you're running this script from the project root directory.", file=sys.stderr)
        return False
        
    except OSError as e:
        print(f"[ERROR] Cannot write to {output_path}", file=sys.stderr)
        print(f"        {e}", file=sys.stderr)
        return False
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Generate data
    success = generate_data(
        n_normal=args.normal,
        n_suspicious=args.suspicious,
        seed=args.seed,
        output_path=args.output
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Test data generation with default parameters**

Run: `python scripts/generate_training_data.py`
Expected: 
- Prints progress messages
- Creates `data/raw/training_data.csv`
- Prints summary with 1000 total samples (500 normal, 500 suspicious)
- File size ~80-90 KB

- [ ] **Step 3: Verify CSV file was created**

Run: `ls -lh data/raw/training_data.csv`
Expected: File exists with size around 85 KB

- [ ] **Step 4: Test with custom parameters**

Run: `python scripts/generate_training_data.py --normal 50 --suspicious 50 --output data/test.csv`
Expected:
- Creates `data/test.csv`
- Summary shows 100 total samples (50 normal, 50 suspicious)

- [ ] **Step 5: Clean up test file**

Run: `rm data/test.csv`

- [ ] **Step 6: Commit**

```bash
git add scripts/generate_training_data.py
git commit -m "feat(ai): implement data generation logic in script"
```

---

## Task 4: Validate CSV Output Quality

**Files:**
- Verify: `data/raw/training_data.csv`

- [ ] **Step 1: Check CSV header**

Run: `head -n 1 data/raw/training_data.csv`
Expected: `response_length,status_code,has_sql_keywords,sql_keyword_count,has_xss_reflection,xss_keyword_count,content_type_html,error_page_detected,has_redirect,length_delta,label`

- [ ] **Step 2: Count total rows (including header)**

Run: `wc -l data/raw/training_data.csv`
Expected: `1001 data/raw/training_data.csv` (1 header + 1000 data rows)

- [ ] **Step 3: Check first 5 data rows**

Run: `head -n 6 data/raw/training_data.csv`
Expected: Header + 5 rows with 11 comma-separated values each

- [ ] **Step 4: Verify label distribution**

Run: `cut -d',' -f11 data/raw/training_data.csv | tail -n +2 | sort | uniq -c`
Expected:
```
    500 0
    500 1
```

- [ ] **Step 5: Spot-check normal samples (label=0)**

Run: `grep ',0$' data/raw/training_data.csv | head -n 3`
Expected: 3 rows ending with `,0` (normal label)
Verify: `has_sql_keywords` (column 3) should be 0, `status_code` (column 2) should be 200/301/302

- [ ] **Step 6: Spot-check suspicious samples (label=1)**

Run: `grep ',1$' data/raw/training_data.csv | head -n 3`
Expected: 3 rows ending with `,1` (suspicious label)
Verify: `has_sql_keywords` (column 3) OR `has_xss_reflection` (column 5) should be 1

- [ ] **Step 7: Verify no missing values**

Run: `grep ',,' data/raw/training_data.csv | wc -l`
Expected: `0` (no consecutive commas = no missing values)

---

## Task 5: Create Validation Script (Optional but Recommended)

**Files:**
- Create: `scripts/validate_training_data.py`

- [ ] **Step 1: Create validation script**

```python
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
```

- [ ] **Step 2: Test validation script**

Run: `python scripts/validate_training_data.py data/raw/training_data.csv`
Expected: All checks pass with ✓ marks

- [ ] **Step 3: Commit**

```bash
git add scripts/validate_training_data.py
git commit -m "feat(ai): add training data validation script"
```

---

## Task 6: Update Documentation

**Files:**
- Modify: `TASKS.md`

- [ ] **Step 1: Mark Day 36-37 tasks as complete in TASKS.md**

Update the Phase 4 section:

```markdown
### Ngày 36-37: Data Collection & Feature Engineering
- [x] **🎯 Học**: Feature engineering for security data
  - Features nào quan trọng để classify response?
  - Cách thu thập training data từ scan sessions
- [x] **📝 Code**: Hoàn thiện `ai/feature_extractor.py`
  - Extract features từ HTTP responses
  - Features: response_length, status_code, keyword presence, reflection
- [x] **📝 Tạo**: Training dataset
  - Tạo synthetic data với 500 normal + 500 suspicious samples
  - Script: `scripts/generate_training_data.py`
  - Lưu vào `data/raw/training_data.csv`
```

- [ ] **Step 2: Add usage instructions to TASKS.md**

Add to the "Useful Commands" section:

```markdown
# Generate training data (default 500+500)
python scripts/generate_training_data.py

# Generate custom sample counts
python scripts/generate_training_data.py --normal 200 --suspicious 200

# Validate training data
python scripts/validate_training_data.py data/raw/training_data.csv
```

- [ ] **Step 3: Commit documentation updates**

```bash
git add TASKS.md
git commit -m "docs: update TASKS.md with completed Day 36-37"
```

---

## Task 7: Final Integration Test

**Files:**
- Test: End-to-end workflow

- [ ] **Step 1: Clean previous output**

Run: `rm -f data/raw/training_data.csv`

- [ ] **Step 2: Generate fresh dataset**

Run: `python scripts/generate_training_data.py`
Expected: Success message with 1000 samples

- [ ] **Step 3: Validate generated data**

Run: `python scripts/validate_training_data.py data/raw/training_data.csv`
Expected: All validation checks pass

- [ ] **Step 4: Verify CSV can be loaded by pandas (for next phase)**

Run:
```bash
python -c "import pandas as pd; df = pd.read_csv('data/raw/training_data.csv'); print(f'Loaded {len(df)} rows, {len(df.columns)} columns'); print(df.head())"
```
Expected: Prints "Loaded 1000 rows, 11 columns" and shows first 5 rows

- [ ] **Step 5: Check file into git**

```bash
git add data/raw/training_data.csv
git commit -m "data: add generated training dataset (1000 samples)"
```

---

## Self-Review Checklist

**Spec Coverage:**
- ✅ Script creation with CLI interface (Task 1-2)
- ✅ Data generation using TrainingDataCollector (Task 3)
- ✅ CSV output validation (Task 4)
- ✅ Optional validation script (Task 5)
- ✅ Documentation updates (Task 6)
- ✅ End-to-end testing (Task 7)

**Placeholder Scan:**
- ✅ No TBD, TODO, or placeholders
- ✅ All code blocks are complete and executable
- ✅ All commands have expected outputs

**Type Consistency:**
- ✅ `TrainingDataCollector` class name consistent throughout
- ✅ Method names match existing implementation (`generate_synthetic`, `save_to_csv`, `get_sample_count`)
- ✅ File paths consistent (`data/raw/training_data.csv`)

---

## Success Criteria

**Functional:**
- ✅ Script runs without errors from project root
- ✅ Generates exactly 1000 samples (500 normal + 500 suspicious)
- ✅ CSV file created at `data/raw/training_data.csv`
- ✅ CSV has 11 columns with correct headers
- ✅ Label distribution is 50/50
- ✅ Normal samples have no SQL/XSS indicators
- ✅ Suspicious samples have SQL or XSS indicators

**Quality:**
- ✅ Feature value ranges are realistic
- ✅ No missing values in CSV
- ✅ Reproducible with same seed
- ✅ CSV is parseable by pandas

**Documentation:**
- ✅ Script includes docstring and help text
- ✅ TASKS.md updated with completion status
- ✅ Usage instructions documented

---

## Estimated Time

- Task 1: 10 minutes (directory setup)
- Task 2: 15 minutes (CLI parsing)
- Task 3: 20 minutes (data generation logic)
- Task 4: 10 minutes (CSV validation)
- Task 5: 20 minutes (validation script)
- Task 6: 10 minutes (documentation)
- Task 7: 15 minutes (integration test)

**Total: ~100 minutes (1.5-2 hours)**

---

## Next Steps (Days 38-39)

After completing this plan, the training data will be ready for model training:

1. Load `data/raw/training_data.csv` with pandas
2. Split features (columns 0-9) and labels (column 10)
3. Train LogisticRegression and RandomForest models
4. Evaluate and save best model to `ai/models/classifier.pkl`

The CSV format is designed to be directly consumable by the trainer with no preprocessing needed.
