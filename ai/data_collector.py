"""
Training Data Collector

Collects labelled HTTP response samples and saves them as a CSV file
that the ModelTrainer can consume directly.

Two collection strategies are supported:

1. **From the database** (real scan data):
   - Reads vulnerability records (label = 1 / "suspicious")
   - Reads page records with no vulnerabilities (label = 0 / "normal")

2. **Synthetic generation** (when no live target is available):
   - Programmatically constructs realistic normal and suspicious
     response samples so the pipeline can be tested end-to-end
     without requiring DVWA or another vulnerable app.

CSV schema (one row per response):
    response_length, status_code, has_sql_keywords, sql_keyword_count,
    has_xss_reflection, xss_keyword_count, content_type_html,
    error_page_detected, has_redirect, length_delta, label
"""

import csv
import logging
import os
import random

from ai.feature_extractor import FeatureExtractor

logger = logging.getLogger(__name__)

# Column order must match Preprocessor.FEATURE_COLUMNS + 'label'
CSV_COLUMNS = [
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
    'label',
]


class TrainingDataCollector:
    """Collects and labels HTTP response samples for model training."""

    def __init__(self):
        self.extractor = FeatureExtractor()
        self.samples = []  # list of feature dicts with 'label' key

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def collect_from_db(self, app):
        """Collect labelled samples from an existing Flask app's database.

        Reads the `vulnerabilities` and `pages` tables to build a
        labelled dataset from real scan history.

        Args:
            app: Flask application instance (needed for app context).
        """
        with app.app_context():
            from app.models.vulnerability import Vulnerability
            from app.models.page import Page

            # Suspicious samples — pages that had vulnerabilities detected
            vulns = Vulnerability.query.all()
            for v in vulns:
                response_data = {
                    'content': v.evidence or '',
                    'status_code': 500,
                    'headers': {'Content-Type': 'text/html'},
                }
                features = self.extractor.extract(response_data, payload=v.payload)
                features['label'] = 1
                self.samples.append(features)
                logger.debug("Added suspicious sample from vuln #%d", v.id)

            # Normal samples — pages with no associated vulnerabilities
            vuln_urls = {v.url for v in vulns}
            pages = Page.query.all()
            for page in pages:
                if page.url not in vuln_urls:
                    response_data = {
                        'content': '',
                        'status_code': page.status_code or 200,
                        'headers': {'Content-Type': 'text/html'},
                    }
                    features = self.extractor.extract(response_data)
                    features['label'] = 0
                    self.samples.append(features)
                    logger.debug("Added normal sample from page #%d", page.id)

        logger.info("Collected %d samples from database", len(self.samples))

    def generate_synthetic(self, n_normal=100, n_suspicious=100, seed=42):
        """Generate synthetic training samples without a live target.

        Produces realistic-looking feature vectors by simulating:
        - Normal responses: short HTML pages, status 200, no error keywords
        - Suspicious responses: SQL error messages, XSS reflections, 500 errors

        Args:
            n_normal (int): Number of normal samples to generate.
            n_suspicious (int): Number of suspicious samples to generate.
            seed (int): Random seed for reproducibility.
        """
        random.seed(seed)

        # --- Normal response templates ---
        normal_contents = [
            '<html><body><h1>Welcome</h1><p>Home page content.</p></body></html>',
            '<html><body><form><input name="q"><button>Search</button></form></body></html>',
            '<html><body><p>Login successful. Redirecting...</p></body></html>',
            '<html><body><ul><li>Item 1</li><li>Item 2</li></ul></body></html>',
            '<html><body><p>No results found for your query.</p></body></html>',
            '<html><body><p>Your profile has been updated.</p></body></html>',
            '<html><body><table><tr><td>Name</td><td>Email</td></tr></table></body></html>',
        ]

        # --- Suspicious response templates ---
        suspicious_contents = [
            "You have an error in your SQL syntax near '''' at line 1",
            "Warning: mysql_fetch_array() expects parameter 1 to be resource",
            "SQLSTATE[42000]: Syntax error or access violation: 1064",
            "ORA-00933: SQL command not properly ended",
            "Microsoft OLE DB Provider for SQL Server error '80040e14'",
            "<script>alert(1)</script> reflected in response body",
            "\"><script>alert(document.cookie)</script>",
            "sqlite3.OperationalError: near \"OR\": syntax error",
            "PostgreSQL ERROR: unterminated quoted string at or near",
            "Database error: table 'users' doesn't exist",
        ]

        for _ in range(n_normal):
            content = random.choice(normal_contents)
            # Add some length variation
            content += ' ' * random.randint(0, 500)
            baseline = len(content) + random.randint(-20, 20)
            response_data = {
                'content': content,
                'status_code': random.choice([200, 200, 200, 301, 302]),
                'headers': {'Content-Type': 'text/html; charset=utf-8'},
            }
            features = self.extractor.extract(
                response_data,
                payload=None,
                baseline_length=max(0, baseline),
            )
            features['label'] = 0
            self.samples.append(features)

        for _ in range(n_suspicious):
            content = random.choice(suspicious_contents)
            content += ' ' * random.randint(0, 200)
            baseline = len(content) + random.randint(50, 300)
            # Pick a representative payload
            payload = random.choice([
                "' OR '1'='1",
                "' OR 1=1--",
                "<script>alert(1)</script>",
                "\"><script>alert(1)</script>",
            ])
            response_data = {
                'content': content,
                'status_code': random.choice([200, 500, 500, 500]),
                'headers': {'Content-Type': 'text/html'},
            }
            features = self.extractor.extract(
                response_data,
                payload=payload,
                baseline_length=max(0, baseline),
            )
            features['label'] = 1
            self.samples.append(features)

        logger.info(
            "Generated %d synthetic samples (%d normal, %d suspicious)",
            len(self.samples), n_normal, n_suspicious,
        )

    def save_to_csv(self, path):
        """Write collected samples to a CSV file.

        Args:
            path (str): Destination file path, e.g. 'data/raw/training_data.csv'.
        """
        if not self.samples:
            raise ValueError("No samples collected. Call generate_synthetic() or collect_from_db() first.")

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction='ignore')
            writer.writeheader()
            for sample in self.samples:
                # Convert booleans to int for CSV readability
                row = {
                    col: int(sample[col]) if isinstance(sample[col], bool) else sample[col]
                    for col in CSV_COLUMNS
                }
                writer.writerow(row)

        logger.info("Saved %d samples to %s", len(self.samples), path)
        print(f"[DataCollector] Saved {len(self.samples)} samples → {path}")

    def get_sample_count(self):
        """Return (n_normal, n_suspicious) counts."""
        n_suspicious = sum(1 for s in self.samples if s.get('label') == 1)
        n_normal = len(self.samples) - n_suspicious
        return n_normal, n_suspicious
