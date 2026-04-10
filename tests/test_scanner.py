"""Tests for ScannerEngine"""

import pytest
from app.services.scanner import ScannerEngine


class TestScannerEngine:
    """Test suite for the scanner engine orchestrator."""

    def test_init(self):
        """Test scanner engine initialization."""
        engine = ScannerEngine('http://example.com')
        assert engine.target_url == 'http://example.com'
        assert engine.results['status'] == 'pending'
