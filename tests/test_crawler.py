"""Tests for CrawlerService"""

import pytest
from app.services.crawler import CrawlerService


class TestCrawlerService:
    """Test suite for the web crawler."""

    def test_init(self):
        """Test crawler initialization."""
        crawler = CrawlerService('http://example.com', max_depth=2)
        assert crawler.base_url == 'http://example.com'
        assert crawler.max_depth == 2
        assert crawler.base_domain == 'example.com'

    def test_should_skip_logout(self):
        """Test URL skip logic for logout links."""
        crawler = CrawlerService('http://example.com')
        assert crawler._should_skip('http://example.com/logout') is True
        assert crawler._should_skip('http://example.com/home') is False
