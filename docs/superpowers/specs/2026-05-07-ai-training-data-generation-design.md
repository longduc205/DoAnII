# AI Training Data Generation - Design Specification

**Date:** 2026-05-07  
**Phase:** Phase 4 - AI Module Integration  
**Tasks:** Days 36-37 - Data Collection & Feature Engineering  
**Author:** AI Web Vulnerability Scanner Project

---

## 1. Overview

### 1.1 Purpose
Generate a comprehensive synthetic training dataset for the AI vulnerability classification model. This dataset will contain labeled HTTP response samples (normal vs suspicious) with extracted features suitable for machine learning model training.

### 1.2 Goals
- Generate 1000 labeled training samples (500 normal + 500 suspicious)
- Create realistic feature distributions that mimic real vulnerability scan responses
- Produce a clean CSV file ready for immediate consumption by the ML trainer
- Establish a reproducible data generation process for academic documentation

### 1.3 Scope
**In Scope:**
- Synthetic data generation using programmatic templates
- Feature extraction from simulated HTTP responses
- CSV file creation with proper schema
- Standalone script for easy execution
- Data validation and quality checks

**Out of Scope:**
- Real scan data collection from DVWA/WebGoat (future enhancement)
- Data augmentation techniques
- Advanced feature engineering beyond existing FeatureExtractor
- Model training (covered in Days 38-39)

---

## 2. System Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Data Generation Pipeline                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  scripts/generate_training_data.py                          │
│  - Parse CLI arguments                                       │
│  - Initialize TrainingDataCollector                          │
│  - Generate synthetic samples                                │
│  - Save to CSV                                               │
│  - Print summary statistics                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ai/data_collector.py (TrainingDataCollector)               │
│  - generate_synthetic(n_normal, n_suspicious, seed)         │
│  - Create normal response templates                          │
│  - Create suspicious response templates                      │
│  - Extract features via FeatureExtractor                     │
│  - Label samples (0=normal, 1=suspicious)                    │
│  - save_to_csv(path)                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ai/feature_extractor.py (FeatureExtractor)                 │
│  - extract(response_data, payload, baseline_length)         │
│  - Returns 10 features as dict                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  data/raw/training_data.csv                                 │
│  - 1000 rows × 11 columns                                    │
│  - Headers: response_length, status_code, ..., label        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

1. **Script Initialization:** User runs `python scripts/generate_training_data.py`
2. **Collector Setup:** Script creates `TrainingDataCollector` instance
3. **Synthetic Generation:** Collector generates 500 normal + 500 suspicious samples
4. **Feature Extraction:** For each sample, `FeatureExtractor.extract()` computes 10 features
5. **Labeling:** Normal samples get label=0, suspicious samples get label=1
6. **CSV Export:** All samples written to `data/raw/training_data.csv`
7. **Summary Output:** Script prints statistics to console

---

## 3. Detailed Design

### 3.1 Script: `scripts/generate_training_data.py`

**Purpose:** Standalone executable script for generating training data.

**Features:**
- Command-line argument parsing (optional custom sample counts)
- Progress indication during generation
- Summary statistics output
- Error handling for file I/O issues

**CLI Interface:**
```bash
# Default: 500 normal + 500 suspicious
python scripts/generate_training_data.py

# Custom counts
python scripts/generate_training_data.py --normal 200 --suspicious 200

# Custom seed for reproducibility
python scripts/generate_training_data.py --seed 123
```

**Output Example:**
```
[DataGenerator] Starting synthetic data generation...
[DataGenerator] Generating 500 normal samples...
[DataGenerator] Generating 500 suspicious samples...
[DataGenerator] Extracting features...
[DataGenerator] Saving to data/raw/training_data.csv...
[DataGenerator] ✓ Success!

Summary:
  Total samples: 1000
  Normal (label=0): 500 (50.0%)
  Suspicious (label=1): 500 (50.0%)
  Output file: data/raw/training_data.csv
  File size: ~85 KB
```

### 3.2 Synthetic Data Generation Strategy

#### 3.2.1 Normal Response Templates

**Characteristics:**
- Status codes: 200 (primary), 301, 302 (occasional redirects)
- Content: Benign HTML pages (welcome pages, forms, tables, lists)
- Length: 50-600 characters (with random padding)
- No SQL error keywords
- No XSS reflection patterns
- Content-Type: `text/html; charset=utf-8`

**Example Templates:**
```html
<html><body><h1>Welcome</h1><p>Home page content.</p></body></html>
<html><body><form><input name="q"><button>Search</button></form></body></html>
<html><body><p>Login successful. Redirecting...</p></body></html>
<html><body><ul><li>Item 1</li><li>Item 2</li></ul></body></html>
<html><body><p>No results found for your query.</p></body></html>
<html><body><p>Your profile has been updated.</p></body></html>
<html><body><table><tr><td>Name</td><td>Email</td></tr></table></body></html>
```

**Feature Distribution (Expected):**
- `response_length`: 50-600
- `status_code`: 200 (75%), 301/302 (25%)
- `has_sql_keywords`: 0
- `sql_keyword_count`: 0
- `has_xss_reflection`: 0
- `xss_keyword_count`: 0
- `content_type_html`: 1
- `error_page_detected`: 0
- `has_redirect`: 0 (75%), 1 (25%)
- `length_delta`: 0-50 (small variations)

#### 3.2.2 Suspicious Response Templates

**Characteristics:**
- Status codes: 500 (primary), 200 (some SQLi/XSS succeed with 200)
- Content: SQL error messages, XSS reflection patterns
- Length: 50-400 characters (with random padding)
- Contains SQL error keywords OR XSS patterns
- Content-Type: `text/html`

**Example Templates:**
```
You have an error in your SQL syntax near '''' at line 1
Warning: mysql_fetch_array() expects parameter 1 to be resource
SQLSTATE[42000]: Syntax error or access violation: 1064
ORA-00933: SQL command not properly ended
Microsoft OLE DB Provider for SQL Server error '80040e14'
<script>alert(1)</script> reflected in response body
"><script>alert(document.cookie)</script>
sqlite3.OperationalError: near "OR": syntax error
PostgreSQL ERROR: unterminated quoted string at or near
Database error: table 'users' doesn't exist
```

**Associated Payloads:**
```
' OR '1'='1
' OR 1=1--
<script>alert(1)</script>
"><script>alert(1)</script>
```

**Feature Distribution (Expected):**
- `response_length`: 50-400
- `status_code`: 500 (75%), 200 (25%)
- `has_sql_keywords`: 1 (80%), 0 (20% for XSS-only)
- `sql_keyword_count`: 1-5
- `has_xss_reflection`: 1 (20%), 0 (80% for SQLi-only)
- `xss_keyword_count`: 0-3
- `content_type_html`: 1
- `error_page_detected`: 1 (75%), 0 (25%)
- `has_redirect`: 0
- `length_delta`: 50-300 (larger anomalies)

### 3.3 Feature Extraction

**Existing FeatureExtractor Usage:**
The `ai/feature_extractor.py` module already implements all required feature extraction logic. The data collector will:

1. Create mock `response_data` dict with keys: `content`, `status_code`, `headers`
2. Call `FeatureExtractor.extract(response_data, payload, baseline_length)`
3. Receive feature dict with 10 keys
4. Add `label` key (0 or 1)
5. Append to samples list

**No modifications needed to FeatureExtractor.**

### 3.4 CSV Schema

**File:** `data/raw/training_data.csv`

**Columns (11 total):**
1. `response_length` (int) - Length of response body in characters
2. `status_code` (int) - HTTP status code (200, 301, 302, 500)
3. `has_sql_keywords` (int) - 1 if SQL error keywords found, else 0
4. `sql_keyword_count` (int) - Number of distinct SQL keywords
5. `has_xss_reflection` (int) - 1 if payload reflected, else 0
6. `xss_keyword_count` (int) - Number of distinct XSS keywords
7. `content_type_html` (int) - 1 if Content-Type is text/html, else 0
8. `error_page_detected` (int) - 1 if status code is 4xx or 5xx, else 0
9. `has_redirect` (int) - 1 if status code is 3xx, else 0
10. `length_delta` (int) - Absolute difference from baseline length
11. `label` (int) - 0 = normal, 1 = suspicious

**Example Rows:**
```csv
response_length,status_code,has_sql_keywords,sql_keyword_count,has_xss_reflection,xss_keyword_count,content_type_html,error_page_detected,has_redirect,length_delta,label
245,200,0,0,0,0,1,0,0,15,0
387,500,1,3,0,0,1,1,0,120,1
156,301,0,0,0,0,1,0,1,8,0
```

---

## 4. Implementation Requirements

### 4.1 File Structure

**New Files:**
- `scripts/generate_training_data.py` - Main executable script

**Modified Files:**
- None (existing `ai/data_collector.py` and `ai/feature_extractor.py` are sufficient)

**Output Files:**
- `data/raw/training_data.csv` - Generated dataset

### 4.2 Dependencies

**Python Standard Library:**
- `argparse` - CLI argument parsing
- `sys` - Exit codes
- `os` - Path operations

**Project Modules:**
- `ai.data_collector.TrainingDataCollector`
- `ai.feature_extractor.FeatureExtractor` (indirect via collector)

**No new external dependencies required.**

### 4.3 Configuration

**Default Parameters:**
- `n_normal`: 500
- `n_suspicious`: 500
- `seed`: 42 (for reproducibility)
- `output_path`: `data/raw/training_data.csv`

**Configurable via CLI:**
- `--normal N` - Number of normal samples
- `--suspicious N` - Number of suspicious samples
- `--seed N` - Random seed
- `--output PATH` - Custom output path

---

## 5. Testing & Validation

### 5.1 Automated Validation

**Script Self-Checks:**
1. Verify `data/raw/` directory exists (create if missing)
2. Verify CSV file is created successfully
3. Verify row count matches expected (n_normal + n_suspicious + 1 header)
4. Verify column count is exactly 11
5. Verify label distribution (count label=0 vs label=1)

**Exit Codes:**
- `0` - Success
- `1` - File I/O error
- `2` - Invalid arguments

### 5.2 Manual Validation

**Quality Checks:**
1. Open CSV in text editor or Excel
2. Spot-check 10 random normal samples:
   - Verify `label=0`
   - Verify `has_sql_keywords=0` and `sql_keyword_count=0`
   - Verify `status_code` is 200/301/302
3. Spot-check 10 random suspicious samples:
   - Verify `label=1`
   - Verify `has_sql_keywords=1` OR `has_xss_reflection=1`
   - Verify `status_code` is often 500
4. Verify no missing values (all cells populated)
5. Verify feature value ranges are realistic

### 5.3 Statistical Validation

**Expected Distributions:**
- Label balance: 50% normal, 50% suspicious (±0%)
- Normal samples: `has_sql_keywords=0` in 100% of cases
- Suspicious samples: `has_sql_keywords=1` OR `has_xss_reflection=1` in 100% of cases
- Status code distribution: 200 (50%), 500 (37.5%), 301/302 (12.5%)

**Validation Script (Optional):**
```python
import pandas as pd

df = pd.read_csv('data/raw/training_data.csv')
print(f"Total rows: {len(df)}")
print(f"Label distribution:\n{df['label'].value_counts()}")
print(f"Status code distribution:\n{df['status_code'].value_counts()}")
print(f"Normal samples with SQL keywords: {df[(df['label']==0) & (df['has_sql_keywords']==1)].shape[0]}")
print(f"Suspicious samples with indicators: {df[(df['label']==1) & ((df['has_sql_keywords']==1) | (df['has_xss_reflection']==1))].shape[0]}")
```

---

## 6. Error Handling

### 6.1 File I/O Errors

**Scenario:** Cannot create `data/raw/` directory or write CSV file

**Handling:**
- Catch `OSError` / `PermissionError`
- Print clear error message with path
- Exit with code 1

**Example:**
```
[ERROR] Cannot write to data/raw/training_data.csv
        Permission denied. Check directory permissions.
```

### 6.2 Invalid Arguments

**Scenario:** User provides negative sample counts or invalid seed

**Handling:**
- Validate arguments in script
- Print usage help
- Exit with code 2

**Example:**
```
[ERROR] Invalid argument: --normal must be a positive integer
Usage: python scripts/generate_training_data.py [--normal N] [--suspicious N] [--seed N]
```

### 6.3 Import Errors

**Scenario:** Cannot import `ai.data_collector` (e.g., running from wrong directory)

**Handling:**
- Catch `ImportError` / `ModuleNotFoundError`
- Print helpful message about running from project root
- Exit with code 1

**Example:**
```
[ERROR] Cannot import ai.data_collector
        Make sure you're running this script from the project root directory.
```

---

## 7. Usage Examples

### 7.1 Basic Usage (Default Parameters)

```bash
# Generate 500 normal + 500 suspicious samples
python scripts/generate_training_data.py
```

**Expected Output:**
```
[DataGenerator] Starting synthetic data generation...
[DataGenerator] Generating 500 normal samples...
[DataGenerator] Generating 500 suspicious samples...
[DataGenerator] Extracting features...
[DataGenerator] Saving to data/raw/training_data.csv...
[DataGenerator] ✓ Success!

Summary:
  Total samples: 1000
  Normal (label=0): 500 (50.0%)
  Suspicious (label=1): 500 (50.0%)
  Output file: data/raw/training_data.csv
  File size: ~85 KB
```

### 7.2 Custom Sample Counts

```bash
# Generate 200 normal + 200 suspicious samples (smaller dataset for testing)
python scripts/generate_training_data.py --normal 200 --suspicious 200
```

### 7.3 Custom Seed

```bash
# Use different random seed for variation
python scripts/generate_training_data.py --seed 123
```

### 7.4 Custom Output Path

```bash
# Save to different location
python scripts/generate_training_data.py --output data/processed/train.csv
```

---

## 8. Integration with Training Pipeline

### 8.1 Next Steps (Days 38-39)

After generating `training_data.csv`, the model training script will:

1. Load CSV using `pandas.read_csv()`
2. Split features (columns 0-9) and labels (column 10)
3. Split into train/test sets (80/20)
4. Train LogisticRegression and RandomForest models
5. Evaluate on test set
6. Save best model to `ai/models/classifier.pkl`

**No manual intervention needed** - the CSV format is designed to be directly consumable by the trainer.

### 8.2 Reproducibility

**For Academic Report:**
- Document the exact command used: `python scripts/generate_training_data.py`
- Document the seed value: `42`
- Document the sample counts: `500 normal + 500 suspicious`
- Include sample statistics in report (mean, std, min, max for each feature)

**Regeneration:**
Running the script with the same seed will produce identical data, ensuring reproducibility for academic evaluation.

---

## 9. Future Enhancements (Out of Scope)

### 9.1 Real Scan Data Collection

**Approach:**
- Run scanner on DVWA/WebGoat
- Collect actual HTTP responses
- Label based on vulnerability findings
- Merge with synthetic data

**Benefits:**
- More realistic feature distributions
- Better model generalization
- Captures real-world edge cases

### 9.2 Data Augmentation

**Techniques:**
- Add noise to numeric features
- Synonym replacement in text content
- SMOTE for class balancing

### 9.3 Advanced Feature Engineering

**Additional Features:**
- Response time (latency)
- Number of redirects followed
- Presence of specific HTML tags
- Entropy of response content

---

## 10. Acceptance Criteria

### 10.1 Functional Requirements

- ✅ Script runs without errors from project root
- ✅ Generates exactly 1000 samples (500 normal + 500 suspicious)
- ✅ CSV file created at `data/raw/training_data.csv`
- ✅ CSV has 11 columns with correct headers
- ✅ All normal samples have `label=0`
- ✅ All suspicious samples have `label=1`
- ✅ Normal samples have no SQL/XSS indicators
- ✅ Suspicious samples have SQL or XSS indicators
- ✅ Script prints summary statistics

### 10.2 Quality Requirements

- ✅ Feature value ranges are realistic (no negative lengths, valid status codes)
- ✅ No missing values in CSV
- ✅ Label distribution is exactly 50/50
- ✅ Reproducible with same seed
- ✅ CSV is valid and parseable by pandas

### 10.3 Documentation Requirements

- ✅ Script includes docstring explaining usage
- ✅ CLI help text available (`--help`)
- ✅ Design spec documents data generation strategy
- ✅ README or TASKS.md updated with usage instructions

---

## 11. Timeline

**Day 36 (4 hours):**
- Hour 1: Create `scripts/generate_training_data.py` skeleton
- Hour 2: Implement CLI argument parsing and main logic
- Hour 3: Test script execution and CSV generation
- Hour 4: Validate output quality and fix issues

**Day 37 (2 hours):**
- Hour 1: Write validation script and perform statistical checks
- Hour 2: Document usage in TASKS.md, take screenshots for report

**Total Effort:** 6 hours

---

## 12. Success Metrics

**Quantitative:**
- 1000 samples generated
- 0 errors during generation
- 100% label accuracy (no mislabeled samples)
- File size ~80-90 KB

**Qualitative:**
- CSV is human-readable and well-formatted
- Feature distributions look realistic when plotted
- Data is ready for immediate use in model training
- Process is documented and reproducible

---

## Appendix A: Feature Descriptions

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `response_length` | int | 50-600 | Length of HTTP response body in characters |
| `status_code` | int | 200, 301, 302, 500 | HTTP status code |
| `has_sql_keywords` | int | 0, 1 | Binary flag: 1 if SQL error keywords found |
| `sql_keyword_count` | int | 0-10 | Count of distinct SQL error keywords |
| `has_xss_reflection` | int | 0, 1 | Binary flag: 1 if payload reflected in response |
| `xss_keyword_count` | int | 0-5 | Count of distinct XSS-related keywords |
| `content_type_html` | int | 0, 1 | Binary flag: 1 if Content-Type is text/html |
| `error_page_detected` | int | 0, 1 | Binary flag: 1 if status code is 4xx or 5xx |
| `has_redirect` | int | 0, 1 | Binary flag: 1 if status code is 3xx |
| `length_delta` | int | 0-300 | Absolute difference from baseline response length |
| `label` | int | 0, 1 | Target variable: 0=normal, 1=suspicious |

---

## Appendix B: Sample Data Preview

**Normal Sample:**
```csv
245,200,0,0,0,0,1,0,0,15,0
```
- Response length: 245 chars
- Status: 200 OK
- No SQL keywords
- No XSS reflection
- HTML content
- Not an error page
- Not a redirect
- Small length delta
- Label: normal

**Suspicious Sample:**
```csv
387,500,1,3,0,0,1,1,0,120,1
```
- Response length: 387 chars
- Status: 500 Internal Server Error
- Has SQL keywords (3 distinct)
- No XSS reflection
- HTML content
- Is an error page
- Not a redirect
- Large length delta
- Label: suspicious

---

**End of Design Specification**
