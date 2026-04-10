"""Tests for VulnerabilityDetector"""

import pytest
from app.services.detector import VulnerabilityDetector


class TestVulnerabilityDetector:
    """Test suite for the vulnerability detector."""

    def test_init(self):
        """Test detector initialization."""
        detector = VulnerabilityDetector(timeout=5)
        assert detector.timeout == 5
        assert len(detector.findings) == 0

    def test_sqli_payloads_exist(self):
        """Test that SQLi payloads are defined."""
        assert len(VulnerabilityDetector.SQLI_PAYLOADS) > 0

    def test_xss_payloads_exist(self):
        """Test that XSS payloads are defined."""
        assert len(VulnerabilityDetector.XSS_PAYLOADS) > 0
