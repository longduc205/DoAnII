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
    'content_length_ratio',
    'length_anomaly_flag',
    'payload_length',
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

    def generate_synthetic(self, n_normal=200, n_suspicious=200, seed=42):
        """Generate synthetic training samples without a live target.

        Produces realistic-looking feature vectors by simulating:
        - Normal responses: HTML pages, status 200/301/302, no error keywords
        - Suspicious responses split into 3 categories:
          a) Error-based SQLi: SQL error keywords, status 500
          b) Blind SQLi: status 200 BUT large content length anomaly
          c) XSS: reflected payload in response body

        The blind SQLi category is crucial: many real-world SQLi findings
        have status_code=200 with no SQL error keywords — only a content
        length change gives them away.

        Args:
            n_normal (int): Number of normal samples to generate.
            n_suspicious (int): Number of suspicious samples to generate.
            seed (int): Random seed for reproducibility.
        """
        random.seed(seed)

        # --- Normal response templates (various realistic pages) ---
        normal_contents = [
            '<html><body><h1>Welcome</h1><p>Home page content.</p></body></html>',
            '<html><body><form><input name="q"><button>Search</button></form></body></html>',
            '<html><body><p>Login successful. Redirecting...</p></body></html>',
            '<html><body><ul><li>Item 1</li><li>Item 2</li></ul></body></html>',
            '<html><body><p>No results found for your query.</p></body></html>',
            '<html><body><p>Your profile has been updated.</p></body></html>',
            '<html><body><table><tr><td>Name</td><td>Email</td></tr></table></body></html>',
            '<html><head><title>Dashboard</title></head><body><div class="container"><h1>Dashboard</h1><p>Welcome back, user.</p><div class="stats"><span>Posts: 12</span><span>Comments: 34</span></div></div></body></html>',
            '<html><body><div class="login-form"><h2>Sign In</h2><form method="POST"><input type="text" name="username"><input type="password" name="password"><button type="submit">Login</button></form></div></body></html>',
        ]

        # --- Error-based SQLi templates (classic SQL errors) ---
        sqli_error_contents = [
            "You have an error in your SQL syntax near '''' at line 1",
            "Warning: mysql_fetch_array() expects parameter 1 to be resource",
            "SQLSTATE[42000]: Syntax error or access violation: 1064",
            "ORA-00933: SQL command not properly ended",
            "Microsoft OLE DB Provider for SQL Server error '80040e14'",
            "sqlite3.OperationalError: near \"OR\": syntax error",
            "PostgreSQL ERROR: unterminated quoted string at or near",
            "Database error: table 'users' doesn't exist",
        ]

        # --- Blind SQLi templates (NO SQL errors, normal-looking pages
        #     but with DIFFERENT content than baseline) ---
        blind_sqli_contents = [
            '<html><body><h1>Search Results</h1><table><tr><td>admin</td><td>admin@test.com</td></tr><tr><td>user1</td><td>user1@test.com</td></tr><tr><td>user2</td><td>user2@test.com</td></tr></table></body></html>',
            '<html><body><div class="results"><h2>Users</h2><ul><li>Administrator - admin@company.com</li><li>John Doe - john@company.com</li><li>Jane Smith - jane@company.com</li></ul></div></body></html>',
            '<html><body><h1>Products</h1><div class="product"><h3>Product A</h3><p>Price: $10</p></div><div class="product"><h3>Product B</h3><p>Price: $20</p></div><div class="product"><h3>Product C</h3><p>Price: $30</p></div><div class="product"><h3>Secret Product</h3><p>Internal Only</p></div></body></html>',
            '<html><body><p>Welcome admin</p><p>You are logged in as administrator.</p><div class="admin-panel"><a href="/users">Manage Users</a><a href="/settings">Settings</a></div></body></html>',
            '<html><body><table border="1"><tr><th>ID</th><th>Username</th><th>Password Hash</th></tr><tr><td>1</td><td>admin</td><td>5f4dcc3b5aa765d61d8327deb882cf99</td></tr></table></body></html>',
        ]

        # --- XSS templates (reflected payloads) ---
        xss_contents = [
            '<html><body><p>Search results for: <script>alert(1)</script></p></body></html>',
            '<html><body><input value=""><script>alert(document.cookie)</script>"></body></html>',
            '<html><body><div>Hello <img src=x onerror=alert(1)></div></body></html>',
            '<html><body><p>Welcome <svg/onload=alert(1)></p></body></html>',
        ]

        sqli_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE users--",
            "' UNION SELECT NULL--",
            "1' AND '1'='1",
            "' UNION SELECT username,password FROM users--",
        ]
        xss_payloads = [
            '<script>alert(1)</script>',
            '"><script>alert(document.cookie)</script>',
            '<img src=x onerror=alert(1)>',
            '<svg/onload=alert(1)>',
        ]

        # ===================== NORMAL SAMPLES =====================
        for _ in range(n_normal):
            content = random.choice(normal_contents)
            # Vary length: pad with spaces (100-5000 range to match real pages)
            content += ' ' * random.randint(0, 4000)
            # Baseline is close to the response (small delta = normal)
            baseline = len(content) + random.randint(-50, 50)
            response_data = {
                'content': content,
                'status_code': random.choice([200, 200, 200, 200, 301, 302]),
                'headers': {'Content-Type': 'text/html; charset=utf-8'},
            }
            features = self.extractor.extract(
                response_data,
                payload=None,
                baseline_length=max(1, baseline),
            )
            features['label'] = 0
            self.samples.append(features)

        # ===================== SUSPICIOUS SAMPLES =====================
        # Split: ~40% error-based SQLi, ~35% blind SQLi, ~25% XSS
        n_error_sqli = int(n_suspicious * 0.40)
        n_blind_sqli = int(n_suspicious * 0.35)
        n_xss = n_suspicious - n_error_sqli - n_blind_sqli

        # --- (a) Error-based SQLi: SQL error keywords + status 500 ---
        for _ in range(n_error_sqli):
            content = random.choice(sqli_error_contents)
            content += ' ' * random.randint(0, 200)
            baseline = random.randint(500, 3000)  # baseline is a normal page
            payload = random.choice(sqli_payloads)
            response_data = {
                'content': content,
                'status_code': random.choice([500, 500, 500, 200]),
                'headers': {'Content-Type': 'text/html'},
            }
            features = self.extractor.extract(
                response_data,
                payload=payload,
                baseline_length=max(1, baseline),
            )
            features['label'] = 1
            self.samples.append(features)

        # --- (b) Blind SQLi: status 200, NO SQL errors, but
        #     content length differs significantly from baseline ---
        for _ in range(n_blind_sqli):
            content = random.choice(blind_sqli_contents)
            content += ' ' * random.randint(0, 3000)
            response_len = len(content)
            # Baseline is MUCH smaller or larger (30-80% difference)
            delta_pct = random.uniform(0.3, 0.8)
            if random.random() < 0.7:
                # Response is LARGER than baseline (data leaked)
                baseline = int(response_len / (1 + delta_pct))
            else:
                # Response is SMALLER than baseline (content hidden)
                baseline = int(response_len * (1 + delta_pct))
            payload = random.choice(sqli_payloads)
            response_data = {
                'content': content,
                'status_code': 200,  # Always 200 for blind SQLi
                'headers': {'Content-Type': 'text/html'},
            }
            features = self.extractor.extract(
                response_data,
                payload=payload,
                baseline_length=max(1, baseline),
            )
            features['label'] = 1
            self.samples.append(features)

        # --- (c) XSS: reflected payload in response ---
        for _ in range(n_xss):
            content = random.choice(xss_contents)
            content += ' ' * random.randint(0, 2000)
            baseline = len(content) + random.randint(-100, 200)
            payload = random.choice(xss_payloads)
            response_data = {
                'content': content,
                'status_code': 200,
                'headers': {'Content-Type': 'text/html'},
            }
            features = self.extractor.extract(
                response_data,
                payload=payload,
                baseline_length=max(1, baseline),
            )
            features['label'] = 1
            self.samples.append(features)

        logger.info(
            "Generated %d synthetic samples (%d normal, %d suspicious "
            "[%d error-sqli, %d blind-sqli, %d xss])",
            len(self.samples), n_normal, n_suspicious,
            n_error_sqli, n_blind_sqli, n_xss,
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
