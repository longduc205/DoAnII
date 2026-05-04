"""Tests for VulnerabilityDetector — SQL Injection Detection"""

import os
import tempfile

import pytest
from unittest.mock import patch, MagicMock

from app.services.detector import VulnerabilityDetector


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def detector():
    """Create a detector instance with default settings."""
    return VulnerabilityDetector(timeout=5)


@pytest.fixture
def sample_form():
    """A sample form dict as produced by the crawler."""
    return {
        'page_url': 'http://testsite.local/login',
        'action': 'http://testsite.local/login',
        'method': 'POST',
        'inputs': [
            {'name': 'username', 'type': 'text', 'value': ''},
            {'name': 'password', 'type': 'password', 'value': ''},
            {'name': 'submit', 'type': 'submit', 'value': 'Login'},
        ],
    }


def _make_response(status_code=200, content='OK', content_length=None):
    """Helper to build a normalized response dict."""
    return {
        'status_code': status_code,
        'content': content,
        'content_length': content_length if content_length is not None else len(content),
    }


# ---------------------------------------------------------------------------
# Initialization tests
# ---------------------------------------------------------------------------

class TestDetectorInit:
    def test_init_defaults(self):
        detector = VulnerabilityDetector()
        assert detector.timeout == 10
        assert detector.delay == 0.2
        assert len(detector.findings) == 0
        assert len(detector.sqli_payloads) > 0

    def test_init_custom_timeout(self):
        detector = VulnerabilityDetector(timeout=5)
        assert detector.timeout == 5

    def test_sqli_payloads_exist(self):
        assert len(VulnerabilityDetector.SQLI_PAYLOADS) > 0

    def test_xss_payloads_exist(self):
        assert len(VulnerabilityDetector.XSS_PAYLOADS) > 0

    def test_error_patterns_exist(self):
        assert len(VulnerabilityDetector.SQLI_ERROR_PATTERNS) > 0


# ---------------------------------------------------------------------------
# Payload loading tests
# ---------------------------------------------------------------------------

class TestPayloadLoading:
    def test_load_from_file(self):
        """Load payloads from a text file successfully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("payload_one\n")
            f.write("payload_two\n")
            f.write("# comment line\n")
            f.write("\n")  # empty line
            f.write("payload_three\n")
            tmp_path = f.name

        try:
            payloads = VulnerabilityDetector._load_payloads(tmp_path)
            assert payloads == ['payload_one', 'payload_two', 'payload_three']
        finally:
            os.unlink(tmp_path)

    def test_load_fallback_when_file_missing(self):
        """Fall back to defaults when file doesn't exist."""
        fallback = ["fb1", "fb2"]
        payloads = VulnerabilityDetector._load_payloads(
            '/nonexistent/path.txt', fallback=fallback
        )
        assert payloads == fallback

    def test_load_fallback_when_file_empty(self):
        """Fall back to defaults when file is empty."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# only comments\n\n")
            tmp_path = f.name

        try:
            fallback = ["fb1"]
            payloads = VulnerabilityDetector._load_payloads(
                tmp_path, fallback=fallback
            )
            assert payloads == fallback
        finally:
            os.unlink(tmp_path)

    def test_load_no_fallback_no_file(self):
        """Return empty list when no file and no fallback."""
        payloads = VulnerabilityDetector._load_payloads('/nonexistent/path.txt')
        assert payloads == []


# ---------------------------------------------------------------------------
# HTTP helper tests
# ---------------------------------------------------------------------------

class TestSendRequest:
    @patch.object(VulnerabilityDetector, '__init__', lambda self, **kw: None)
    def _make_detector(self):
        d = VulnerabilityDetector.__new__(VulnerabilityDetector)
        d.timeout = 5
        d.session = MagicMock()
        return d

    def test_send_get_request(self):
        detector = self._make_detector()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = 'Hello World'
        detector.session.get.return_value = mock_resp

        result = detector._send_request('http://test.local', 'GET', {'q': '1'})
        assert result is not None
        assert result['status_code'] == 200
        assert result['content'] == 'Hello World'
        assert result['content_length'] == 11

    def test_send_post_request(self):
        detector = self._make_detector()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = 'OK'
        detector.session.post.return_value = mock_resp

        result = detector._send_request('http://test.local', 'POST', {'a': 'b'})
        assert result is not None
        detector.session.post.assert_called_once()

    def test_send_request_timeout(self):
        """Graceful handling of timeouts — returns None."""
        detector = self._make_detector()
        import requests as req
        detector.session.get.side_effect = req.Timeout("timed out")

        result = detector._send_request('http://test.local', 'GET', {})
        assert result is None

    def test_send_request_connection_error(self):
        detector = self._make_detector()
        import requests as req
        detector.session.get.side_effect = req.ConnectionError("refused")

        result = detector._send_request('http://test.local', 'GET', {})
        assert result is None


# ---------------------------------------------------------------------------
# Baseline response tests
# ---------------------------------------------------------------------------

class TestGetBaseline:
    def test_baseline_uses_default_values(self, detector):
        """Baseline request uses existing values or 'test' placeholder."""
        with patch.object(detector, '_send_request') as mock_send:
            mock_send.return_value = _make_response()
            detector._get_baseline_response(
                'http://test.local', 'GET',
                {'username': '', 'password': 'preset'},
            )
            called_params = mock_send.call_args[0][2]
            assert called_params['username'] == 'test'
            assert called_params['password'] == 'preset'

    def test_baseline_returns_none_on_failure(self, detector):
        with patch.object(detector, '_send_request', return_value=None):
            result = detector._get_baseline_response(
                'http://test.local', 'GET', {'q': 'x'}
            )
            assert result is None


# ---------------------------------------------------------------------------
# Response comparison tests
# ---------------------------------------------------------------------------

class TestCompareResponses:
    def test_normal_responses_not_suspicious(self, detector):
        """Two identical responses should not be flagged."""
        baseline = _make_response(200, 'Normal page content')
        test_resp = _make_response(200, 'Normal page content')
        result = detector._compare_responses(baseline, test_resp)
        assert result['is_suspicious'] is False
        assert result['score'] == 0.0
        assert result['reasons'] == []

    def test_sql_error_keyword_detected(self, detector):
        """Response containing SQL error keywords should be flagged."""
        baseline = _make_response(200, 'Normal page')
        test_resp = _make_response(
            200,
            'You have an error in your SQL syntax near mysql_fetch_array',
        )
        result = detector._compare_responses(baseline, test_resp)
        assert result['is_suspicious'] is True
        assert any('SQL error keyword' in r for r in result['reasons'])
        assert result['score'] >= 0.5

    def test_status_code_change_500(self, detector):
        """Status code changing to 500 should be flagged."""
        baseline = _make_response(200, 'OK')
        test_resp = _make_response(500, 'Internal Server Error')
        result = detector._compare_responses(baseline, test_resp)
        assert result['is_suspicious'] is True
        assert any('Status code' in r for r in result['reasons'])

    def test_status_code_change_302(self, detector):
        """Status code changing to 302 — flagged but lower score."""
        baseline = _make_response(200, 'OK' * 100)
        test_resp = _make_response(302, 'Redirecting...')
        result = detector._compare_responses(baseline, test_resp)
        assert any('Status code' in r for r in result['reasons'])

    def test_content_length_anomaly(self, detector):
        """Significant content length difference should be flagged."""
        baseline = _make_response(200, 'A' * 1000)
        test_resp = _make_response(200, 'A' * 2000)  # 100% difference
        result = detector._compare_responses(baseline, test_resp)
        assert any('Content length' in r for r in result['reasons'])

    def test_no_anomaly_within_threshold(self, detector):
        """Small content length difference should NOT be flagged."""
        baseline = _make_response(200, 'A' * 1000)
        test_resp = _make_response(200, 'A' * 1100)  # 10% — under 30%
        result = detector._compare_responses(baseline, test_resp)
        assert not any('Content length' in r for r in result['reasons'])

    def test_none_baseline_returns_safe(self, detector):
        """None baseline should return not suspicious."""
        result = detector._compare_responses(None, _make_response())
        assert result['is_suspicious'] is False

    def test_none_test_response_returns_safe(self, detector):
        result = detector._compare_responses(_make_response(), None)
        assert result['is_suspicious'] is False


# ---------------------------------------------------------------------------
# SQLi detection integration tests (mocked HTTP)
# ---------------------------------------------------------------------------

class TestSQLiDetection:
    def test_sqli_detection_on_vulnerable_form(self, detector, sample_form):
        """Detector should find SQLi when error keywords appear."""
        baseline = _make_response(200, 'Normal login page')
        vuln_resp = _make_response(
            200,
            'Error: You have an error in your SQL syntax near mysql',
        )

        call_count = [0]
        def fake_send(url, method, params):
            call_count[0] += 1
            # First two calls = baselines, subsequent = payload tests
            for val in params.values():
                if "'" in val or '--' in val:
                    return vuln_resp
            return baseline

        with patch.object(detector, '_send_request', side_effect=fake_send):
            findings = detector.test_sqli(sample_form)

        assert len(findings) > 0
        assert findings[0]['vuln_type'] == 'sqli'
        assert findings[0]['parameter'] in ('username', 'password')
        assert findings[0]['severity'] in ('high', 'medium')
        assert 'sql' in findings[0]['evidence'].lower()

    def test_sqli_detection_on_safe_form(self, detector, sample_form):
        """No findings should be produced for a safe form."""
        normal = _make_response(200, 'Normal login page — no errors here')

        with patch.object(detector, '_send_request', return_value=normal):
            findings = detector.test_sqli(sample_form)

        assert len(findings) == 0

    def test_sqli_skips_submit_fields(self, detector):
        """Submit/button fields should not be tested."""
        form = {
            'page_url': 'http://test.local/form',
            'action': 'http://test.local/form',
            'method': 'POST',
            'inputs': [
                {'name': 'submit', 'type': 'submit', 'value': 'Go'},
            ],
        }
        with patch.object(detector, '_send_request') as mock_send:
            mock_send.return_value = _make_response()
            findings = detector.test_sqli(form)

        assert len(findings) == 0

    def test_sqli_empty_form_returns_empty(self, detector):
        """Form with no inputs should return no findings."""
        form = {
            'page_url': 'http://test.local',
            'action': 'http://test.local',
            'method': 'GET',
            'inputs': [],
        }
        findings = detector.test_sqli(form)
        assert findings == []

    def test_sqli_no_action_url(self, detector):
        """Form with no action URL should be skipped."""
        form = {
            'page_url': 'http://test.local',
            'action': '',
            'method': 'GET',
            'inputs': [{'name': 'q', 'type': 'text', 'value': ''}],
        }
        findings = detector.test_sqli(form)
        assert findings == []

    def test_findings_accumulated(self, detector, sample_form):
        """Findings from test_sqli should also be in get_all_findings()."""
        vuln_resp = _make_response(
            200,
            'sql syntax error in mysql database query',
        )

        def fake_send(url, method, params):
            for val in params.values():
                if "'" in val:
                    return vuln_resp
            return _make_response(200, 'Normal page')

        with patch.object(detector, '_send_request', side_effect=fake_send):
            detector.test_sqli(sample_form)

        all_findings = detector.get_all_findings()
        assert len(all_findings) > 0
        assert all_findings[0]['vuln_type'] == 'sqli'

    def test_clear_findings(self, detector):
        """clear_findings() should reset the list."""
        detector.findings = [{'vuln_type': 'sqli'}]
        detector.clear_findings()
        assert detector.findings == []

    def test_baseline_failure_skips_form(self, detector, sample_form):
        """When baseline cannot be obtained, form should be skipped."""
        with patch.object(detector, '_send_request', return_value=None):
            findings = detector.test_sqli(sample_form)
        assert findings == []


# ---------------------------------------------------------------------------
# XSS Reflection tests
# ---------------------------------------------------------------------------

class TestXSSReflection:
    def test_payload_reflected_unencoded(self, detector):
        """Payload appears raw in response → reflected XSS."""
        payload = '<script>alert(1)</script>'
        content = f'<html><body>Search results for: {payload}</body></html>'
        result = detector._check_xss_reflection(payload, content)
        assert result['is_reflected'] is True
        assert any('Reflected payload' in r for r in result['reasons'])
        assert result['score'] >= 0.6

    def test_payload_html_encoded_is_safe(self, detector):
        """HTML-encoded payload → NOT reflected (properly sanitized)."""
        payload = '<script>alert(1)</script>'
        content = '<html><body>Search: &lt;script&gt;alert(1)&lt;/script&gt;</body></html>'
        result = detector._check_xss_reflection(payload, content)
        assert result['is_reflected'] is False

    def test_payload_not_in_response(self, detector):
        """Payload completely absent from response → safe."""
        payload = '<script>alert(1)</script>'
        content = '<html><body>Welcome to our site</body></html>'
        result = detector._check_xss_reflection(payload, content)
        assert result['is_reflected'] is False
        assert result['reasons'] == []
        assert result['score'] == 0.0

    def test_event_handler_adds_score(self, detector):
        """Event handler detected alongside reflected payload → higher score."""
        payload = '<img src=x onerror=alert(1)>'
        content = f'<html><body>{payload}</body></html>'
        result = detector._check_xss_reflection(payload, content)
        assert result['is_reflected'] is True
        assert any('Event handler' in r for r in result['reasons'])
        assert result['score'] > 0.6  # reflection + event handler

    def test_dangerous_tag_adds_score(self, detector):
        """Dangerous tag detected alongside reflected payload → higher score."""
        payload = '<script>alert(1)</script>'
        content = f'<html><body>Result: {payload}</body></html>'
        result = detector._check_xss_reflection(payload, content)
        assert result['is_reflected'] is True
        assert any('Dangerous tag' in r for r in result['reasons'])

    def test_event_handler_alone_not_flagged(self, detector):
        """Event handler present but payload NOT reflected → not flagged.

        This prevents false positives on pages that legitimately use
        event handlers (e.g., onclick on buttons).
        """
        payload = '<script>alert(1)</script>'
        # Page has onclick but payload is NOT reflected
        content = '<html><body><button onclick="save()">Save</button></body></html>'
        result = detector._check_xss_reflection(payload, content)
        assert result['is_reflected'] is False


# ---------------------------------------------------------------------------
# XSS detection integration tests (mocked HTTP)
# ---------------------------------------------------------------------------

class TestXSSDetection:
    @pytest.fixture
    def xss_form(self):
        """A sample search form for XSS testing."""
        return {
            'page_url': 'http://testsite.local/search',
            'action': 'http://testsite.local/search',
            'method': 'GET',
            'inputs': [
                {'name': 'q', 'type': 'text', 'value': ''},
                {'name': 'submit', 'type': 'submit', 'value': 'Search'},
            ],
        }

    def test_xss_detection_vulnerable_form(self, detector, xss_form):
        """Detector finds XSS when payload is reflected in response."""
        def fake_send(url, method, params):
            q_val = params.get('q', '')
            # Vulnerable server reflects input without encoding
            return _make_response(
                200,
                f'<html><body>Results for: {q_val}</body></html>',
            )

        with patch.object(detector, '_send_request', side_effect=fake_send):
            findings = detector.test_xss(xss_form)

        assert len(findings) > 0
        assert findings[0]['vuln_type'] == 'xss'
        assert findings[0]['parameter'] == 'q'
        assert findings[0]['severity'] in ('high', 'medium')
        assert 'Reflected payload' in findings[0]['evidence']

    def test_xss_detection_safe_form(self, detector, xss_form):
        """No findings when server HTML-encodes the input."""
        def fake_send(url, method, params):
            # Safe server: encodes special chars
            return _make_response(
                200,
                '<html><body>Results for: &lt;script&gt;alert(1)&lt;/script&gt;</body></html>',
            )

        with patch.object(detector, '_send_request', side_effect=fake_send):
            findings = detector.test_xss(xss_form)

        assert len(findings) == 0

    def test_xss_skips_submit_fields(self, detector):
        """Submit/button fields should not be tested."""
        form = {
            'page_url': 'http://test.local/form',
            'action': 'http://test.local/form',
            'method': 'GET',
            'inputs': [
                {'name': 'go', 'type': 'submit', 'value': 'Go'},
            ],
        }
        with patch.object(detector, '_send_request') as mock_send:
            mock_send.return_value = _make_response()
            findings = detector.test_xss(form)
        assert len(findings) == 0

    def test_xss_empty_form(self, detector):
        """Form with no inputs returns no findings."""
        form = {
            'page_url': 'http://test.local',
            'action': 'http://test.local',
            'method': 'GET',
            'inputs': [],
        }
        findings = detector.test_xss(form)
        assert findings == []

    def test_xss_no_action_url(self, detector):
        """Form with no action URL should be skipped."""
        form = {
            'page_url': 'http://test.local',
            'action': '',
            'method': 'GET',
            'inputs': [{'name': 'q', 'type': 'text', 'value': ''}],
        }
        findings = detector.test_xss(form)
        assert findings == []

    def test_xss_finding_format(self, detector, xss_form):
        """Verify the finding dict has the correct keys."""
        def fake_send(url, method, params):
            q_val = params.get('q', '')
            return _make_response(200, f'<html>{q_val}</html>')

        with patch.object(detector, '_send_request', side_effect=fake_send):
            findings = detector.test_xss(xss_form)

        assert len(findings) > 0
        f = findings[0]
        assert f['vuln_type'] == 'xss'
        assert 'severity' in f
        assert 'url' in f
        assert 'parameter' in f
        assert 'payload' in f
        assert 'evidence' in f
        assert 'method' in f
        assert 'score' in f

    def test_xss_findings_in_global_list(self, detector, xss_form):
        """XSS findings also appear in get_all_findings()."""
        def fake_send(url, method, params):
            q_val = params.get('q', '')
            return _make_response(200, f'<html>{q_val}</html>')

        with patch.object(detector, '_send_request', side_effect=fake_send):
            detector.test_xss(xss_form)

        all_findings = detector.get_all_findings()
        xss_findings = [f for f in all_findings if f['vuln_type'] == 'xss']
        assert len(xss_findings) > 0
