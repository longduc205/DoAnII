"""
Vulnerability Detection Module

Performs rule-based testing for:
- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)

Detection strategies for SQLi:
1. Error-based: SQL error keywords in response body
2. Content length anomaly: significant difference from baseline
3. Status code change: different status code from baseline

Detection strategies for XSS:
1. Reflected payload: payload appears unencoded in response body
2. Event handler detection: dangerous JS event handlers in response
3. Dangerous tag detection: script/iframe/svg tags near injection point
"""

import logging
import os
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

# Threshold for content length anomaly (30% difference from baseline)
LENGTH_ANOMALY_THRESHOLD = 0.3

# Minimum number of indicators to flag as "high" severity
HIGH_CONFIDENCE_INDICATORS = 2


class VulnerabilityDetector:
    """Detects vulnerabilities using payload injection and response analysis."""

    # Default SQL Injection test payloads (fallback when file not found)
    SQLI_PAYLOADS = [
        "' OR '1'='1",
        "' OR 1=1--",
        "'; DROP TABLE users--",
        "' UNION SELECT NULL--",
        "1' AND '1'='1",
    ]

    # SQL error indicators in responses
    SQLI_ERROR_PATTERNS = [
        'sql syntax', 'mysql', 'sqlite', 'postgresql',
        'syntax error', 'unclosed quotation', 'unterminated',
        'odbc', 'oracle', 'microsoft sql', 'mysql_fetch',
        'pg_query', 'sql error', 'database error',
        'warning: mysql', 'warning: pg_', 'warning: sqlite',
    ]

    # XSS test payloads
    XSS_PAYLOADS = [
        '<script>alert(1)</script>',
        '"><script>alert(1)</script>',
        "'><script>alert(1)</script>",
        '<img src=x onerror=alert(1)>',
        '<svg/onload=alert(1)>',
    ]

    # Dangerous JS event handler patterns
    XSS_EVENT_HANDLERS = [
        'onerror=', 'onload=', 'onfocus=', 'onclick=',
        'onmouseover=', 'onsubmit=', 'onchange=',
    ]

    # Dangerous HTML tags that can execute scripts
    XSS_DANGEROUS_TAGS = [
        '<script', '<iframe', '<object', '<embed',
        '<svg', '<img src=x', '<body',
    ]

    # HTML-encoded equivalents that indicate proper sanitization
    XSS_ENCODED_PATTERNS = [
        '&lt;script', '&lt;img', '&lt;svg', '&lt;iframe',
        '&amp;lt;', '&#60;', '&#x3c;',
    ]

    # Input types to skip when injecting payloads
    SKIP_INPUT_TYPES = frozenset([
        'submit', 'button', 'image', 'reset', 'file',
    ])

    def __init__(self, timeout=10, sqli_payload_file=None,
                 xss_payload_file=None, delay=0.2):
        self.timeout = timeout
        self.delay = delay
        self.findings = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (compatible; AIVulnScanner/1.0; '
                '+https://github.com/educational-scanner)'
            ),
        })
        
        # Attempt auto-login if scanning DVWA
        self._login_dvwa()

        # Load SQLi payloads from file or use defaults
        self.sqli_payloads = self._load_payloads(
            sqli_payload_file or 'data/payloads/sqli_payloads.txt',
            fallback=self.SQLI_PAYLOADS,
        )
        logger.info("Loaded %d SQLi payloads", len(self.sqli_payloads))

        # Load XSS payloads from file or use defaults
        self.xss_payloads = self._load_payloads(
            xss_payload_file or 'data/payloads/xss_payloads.txt',
            fallback=self.XSS_PAYLOADS,
        )
        logger.info("Loaded %d XSS payloads", len(self.xss_payloads))

    def _login_dvwa(self):
        """Simple DVWA auto-login for the detector's internal session."""
        import os
        import re
        login_url = os.getenv('DVWA_LOGIN_URL', 'http://localhost:8080/login.php')
        user = os.getenv('DVWA_USER', 'admin')
        password = os.getenv('DVWA_PASS', 'password')
        
        try:
            # 1. Get token
            r = self.session.get(login_url, timeout=5)
            token = re.search(r"user_token' value='(.*?)'", r.text)
            user_token = token.group(1) if token else ""
            
            # 2. Login
            self.session.post(login_url, data={
                'username': user, 'password': password, 
                'Login': 'Login', 'user_token': user_token
            }, timeout=5)
            
            # 3. Security Level
            self.session.cookies.set('security', 'low')
        except:
            pass


    # ------------------------------------------------------------------
    # Payload loading
    # ------------------------------------------------------------------

    @staticmethod
    def _load_payloads(filepath, fallback=None):
        """Load payloads from a text file (one per line).

        Lines starting with '#' and empty lines are ignored.
        Falls back to the provided default list if the file is missing.
        """
        path = Path(filepath)
        if not path.is_file():
            logger.warning(
                "Payload file not found: %s — using %d built-in payloads",
                filepath, len(fallback or []),
            )
            return list(fallback or [])

        payloads = []
        with open(path, 'r', encoding='utf-8') as fh:
            for line in fh:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    payloads.append(stripped)

        if not payloads:
            logger.warning("Payload file empty: %s — using fallback", filepath)
            return list(fallback or [])

        return payloads

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _send_request(self, url, method, params):
        """Send an HTTP request and return a normalized response dict.

        Returns:
            dict with keys: status_code, content, content_length
            None on failure (timeout, connection error, etc.)
        """
        try:
            if method.upper() == 'POST':
                resp = self.session.post(url, data=params, timeout=self.timeout)
            else:
                resp = self.session.get(url, params=params, timeout=self.timeout)

            return {
                'status_code': resp.status_code,
                'content': resp.text,
                'content_length': len(resp.text),
            }
        except requests.Timeout:
            logger.warning("Request timeout: %s %s", method, url)
            return None
        except requests.ConnectionError:
            logger.warning("Connection error: %s %s", method, url)
            return None
        except requests.RequestException as exc:
            logger.warning("Request failed: %s %s — %s", method, url, exc)
            return None

    def _get_baseline_response(self, url, method, params):
        """Get a normal (baseline) response for comparison.

        Sends a request with benign default values so we can later
        compare injected-payload responses against this baseline.
        """
        baseline_params = {}
        for key, value in params.items():
            # Use existing default value or a harmless placeholder
            baseline_params[key] = value if value else 'test'

        response = self._send_request(url, method, baseline_params)
        if response is None:
            logger.warning("Could not obtain baseline for %s", url)
        return response

    # ------------------------------------------------------------------
    # Response comparison / analysis
    # ------------------------------------------------------------------

    def _compare_responses(self, baseline, test_response):
        """Compare a test response against the baseline to detect anomalies.

        Returns:
            dict: {
                'is_suspicious': bool,
                'reasons': list[str],
                'score': float (0.0 – 1.0),
            }
        """
        reasons = []
        score = 0.0

        if baseline is None or test_response is None:
            return {'is_suspicious': False, 'reasons': [], 'score': 0.0}

        # --- Strategy 1: SQL error keyword presence ---
        body_lower = test_response['content'].lower()
        matched_keywords = [
            kw for kw in self.SQLI_ERROR_PATTERNS if kw in body_lower
        ]
        if matched_keywords:
            reasons.append(
                f"SQL error keyword(s) found: {', '.join(matched_keywords[:3])}"
            )
            score += 0.5

        # --- Strategy 2: Status code change ---
        if baseline['status_code'] != test_response['status_code']:
            reasons.append(
                f"Status code changed: {baseline['status_code']} → "
                f"{test_response['status_code']}"
            )
            # 500-level errors are more suspicious
            if test_response['status_code'] >= 500:
                score += 0.3
            else:
                score += 0.15

        # --- Strategy 3: Content length anomaly ---
        if baseline['content_length'] > 0:
            length_diff = abs(
                test_response['content_length'] - baseline['content_length']
            )
            ratio = length_diff / baseline['content_length']
            if ratio > LENGTH_ANOMALY_THRESHOLD:
                reasons.append(
                    f"Content length anomaly: {baseline['content_length']} → "
                    f"{test_response['content_length']} "
                    f"(Δ {ratio:.0%})"
                )
                score += 0.3

        # Clamp score to [0, 1]
        score = min(score, 1.0)

        is_suspicious = len(reasons) > 0 and score >= 0.3
        return {
            'is_suspicious': is_suspicious,
            'reasons': reasons,
            'score': score,
        }

    # ------------------------------------------------------------------
    # SQL Injection detection
    # ------------------------------------------------------------------

    def test_sqli(self, form_data):
        """Test a form for SQL Injection vulnerabilities.

        Args:
            form_data: dict from crawler with keys:
                - action (str): form action URL
                - method (str): GET or POST
                - inputs (list[dict]): each with 'name', 'type', 'value'
                - page_url (str): page where the form was found

        Returns:
            list[dict]: findings for this form
        """
        form_findings = []
        action_url = form_data.get('action', '')
        method = form_data.get('method', 'GET').upper()
        inputs = form_data.get('inputs', [])

        if not action_url or not inputs:
            return form_findings

        # Build default params dict from form inputs
        default_params = {}
        testable_fields = []
        for inp in inputs:
            name = inp.get('name', '')
            if not name:
                continue
            input_type = inp.get('type', 'text').lower()
            default_params[name] = inp.get('value', '') or 'test'
            if input_type not in self.SKIP_INPUT_TYPES:
                testable_fields.append(name)

        if not testable_fields:
            logger.debug("No testable fields in form: %s", action_url)
            return form_findings

        # Get baseline response
        baseline = self._get_baseline_response(action_url, method, default_params)
        if baseline is None:
            logger.warning(
                "Skipping SQLi test for %s — no baseline", action_url
            )
            return form_findings

        logger.info(
            "Testing SQLi on %s (%s) — %d fields × %d payloads",
            action_url, method, len(testable_fields), len(self.sqli_payloads),
        )

        # Test each field with each payload
        for field_name in testable_fields:
            for payload in self.sqli_payloads:
                # Clone params and inject payload
                test_params = dict(default_params)
                test_params[field_name] = payload

                test_response = self._send_request(
                    action_url, method, test_params
                )
                if test_response is None:
                    continue

                comparison = self._compare_responses(baseline, test_response)

                if comparison['is_suspicious']:
                    # Determine severity based on confidence score
                    if len(comparison['reasons']) >= HIGH_CONFIDENCE_INDICATORS:
                        severity = 'high'
                    elif comparison['score'] >= 0.5:
                        severity = 'high'
                    else:
                        severity = 'medium'

                    finding = {
                        'vuln_type': 'sqli',
                        'severity': severity,
                        'url': action_url,
                        'page_url': form_data.get('page_url', action_url),
                        'parameter': field_name,
                        'payload': payload,
                        'evidence': '; '.join(comparison['reasons']),
                        'method': method,
                        'score': comparison['score'],
                        'baseline_length': baseline['content_length'],
                        'test_length': test_response['content_length'],
                        'baseline_status': baseline['status_code'],
                        'test_status': test_response['status_code'],
                        # Response data for AI classification
                        'response_data': {
                            'status_code': test_response['status_code'],
                            'content': test_response['content'],
                            'headers': {'Content-Type': 'text/html'},
                        },
                    }
                    form_findings.append(finding)
                    self.findings.append(finding)

                    logger.info(
                        "  [SQLi FOUND] %s — param=%s, payload=%s, "
                        "severity=%s, evidence=%s",
                        action_url, field_name, payload[:30],
                        severity, comparison['reasons'][0],
                    )

                    # Once we find one payload that works for this field,
                    # skip remaining payloads for this field to save time
                    break

        return form_findings

    # ------------------------------------------------------------------
    # XSS detection
    # ------------------------------------------------------------------

    def _check_xss_reflection(self, payload, response_content):
        """Check if an XSS payload is reflected (unencoded) in the response.

        Returns:
            dict: {
                'is_reflected': bool,
                'reasons': list[str],
                'score': float (0.0 – 1.0),
            }
        """
        reasons = []
        score = 0.0
        content_lower = response_content.lower()
        payload_lower = payload.lower()

        # --- Strategy 1: Exact payload reflection ---
        if payload_lower in content_lower:
            # Verify it's NOT the HTML-encoded version
            is_encoded = any(
                enc in content_lower
                for enc in self.XSS_ENCODED_PATTERNS
            )
            if not is_encoded:
                reasons.append(
                    f"Reflected payload found in response: {payload[:40]}"
                )
                score += 0.6

        # --- Strategy 2: Event handler detection ---
        matched_handlers = [
            handler for handler in self.XSS_EVENT_HANDLERS
            if handler in content_lower
        ]
        # Only flag if these handlers weren't already in a clean context
        # (i.e., they likely came from our injection)
        if matched_handlers and score > 0:
            reasons.append(
                f"Event handler(s) detected: {', '.join(matched_handlers[:3])}"
            )
            score += 0.2

        # --- Strategy 3: Dangerous tag detection ---
        matched_tags = [
            tag for tag in self.XSS_DANGEROUS_TAGS
            if tag in content_lower
        ]
        if matched_tags and score > 0:
            reasons.append(
                f"Dangerous tag(s) in response: {', '.join(matched_tags[:3])}"
            )
            score += 0.2

        score = min(score, 1.0)
        is_reflected = score >= 0.5

        return {
            'is_reflected': is_reflected,
            'reasons': reasons,
            'score': score,
        }

    def test_xss(self, form_data):
        """Test a form for Cross-Site Scripting (Reflected XSS) vulnerabilities.

        Args:
            form_data: dict from crawler with keys:
                - action (str): form action URL
                - method (str): GET or POST
                - inputs (list[dict]): each with 'name', 'type', 'value'
                - page_url (str): page where the form was found

        Returns:
            list[dict]: findings for this form
        """
        form_findings = []
        action_url = form_data.get('action', '')
        method = form_data.get('method', 'GET').upper()
        inputs = form_data.get('inputs', [])

        if not action_url or not inputs:
            return form_findings

        # Build default params and identify testable fields
        default_params = {}
        testable_fields = []
        for inp in inputs:
            name = inp.get('name', '')
            if not name:
                continue
            input_type = inp.get('type', 'text').lower()
            default_params[name] = inp.get('value', '') or 'test'
            if input_type not in self.SKIP_INPUT_TYPES:
                testable_fields.append(name)

        if not testable_fields:
            logger.debug("No testable fields in form: %s", action_url)
            return form_findings

        logger.info(
            "Testing XSS on %s (%s) — %d fields × %d payloads",
            action_url, method, len(testable_fields), len(self.xss_payloads),
        )

        # Test each field with each payload
        for field_name in testable_fields:
            for payload in self.xss_payloads:
                # Clone params and inject payload
                test_params = dict(default_params)
                test_params[field_name] = payload

                test_response = self._send_request(
                    action_url, method, test_params
                )
                if test_response is None:
                    continue

                reflection = self._check_xss_reflection(
                    payload, test_response['content']
                )

                if reflection['is_reflected']:
                    # Determine severity
                    if reflection['score'] >= 0.8:
                        severity = 'high'
                    elif reflection['score'] >= 0.5:
                        severity = 'medium'
                    else:
                        severity = 'low'

                    finding = {
                        'vuln_type': 'xss',
                        'severity': severity,
                        'url': action_url,
                        'page_url': form_data.get('page_url', action_url),
                        'parameter': field_name,
                        'payload': payload,
                        'evidence': '; '.join(reflection['reasons']),
                        'method': method,
                        'score': reflection['score'],
                        # Response data for AI classification
                        'response_data': {
                            'status_code': test_response['status_code'],
                            'content': test_response['content'],
                            'headers': {'Content-Type': 'text/html'},
                        },
                    }
                    form_findings.append(finding)
                    self.findings.append(finding)

                    logger.info(
                        "  [XSS FOUND] %s — param=%s, payload=%s, "
                        "severity=%s, evidence=%s",
                        action_url, field_name, payload[:30],
                        severity, reflection['reasons'][0],
                    )

                    # One payload per field is enough
                    break

        return form_findings

    def get_all_findings(self):
        """Return all findings collected across all tested forms."""
        return list(self.findings)

    def clear_findings(self):
        """Reset findings list."""
        self.findings = []
