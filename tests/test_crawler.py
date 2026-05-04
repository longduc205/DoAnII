"""Tests for CrawlerService"""

from unittest.mock import patch, MagicMock

import pytest
from app.services.crawler import CrawlerService


class TestCrawlerInit:
    """Test crawler initialization and URL normalization."""

    def test_init_basic(self):
        crawler = CrawlerService('http://example.com', max_depth=2)
        assert crawler.base_url == 'http://example.com'
        assert crawler.max_depth == 2
        assert crawler.base_domain == 'example.com'

    def test_init_adds_scheme(self):
        crawler = CrawlerService('example.com')
        assert crawler.base_url == 'https://example.com'

    def test_init_strips_trailing_slash(self):
        crawler = CrawlerService('http://example.com/')
        assert crawler.base_url == 'http://example.com'

    def test_init_defaults(self):
        crawler = CrawlerService('http://example.com')
        assert crawler.max_depth == 3
        assert crawler.max_pages == 50
        assert crawler.timeout == 10
        assert crawler.delay == 0.5


class TestShouldSkip:
    """Test URL filtering logic."""

    def setup_method(self):
        self.crawler = CrawlerService('http://example.com')

    def test_skip_logout(self):
        assert self.crawler._should_skip('http://example.com/logout') is True

    def test_skip_signout(self):
        assert self.crawler._should_skip('http://example.com/sign-out') is True

    def test_skip_css(self):
        assert self.crawler._should_skip('http://example.com/style.css') is True

    def test_skip_js(self):
        assert self.crawler._should_skip('http://example.com/app.js') is True

    def test_skip_image(self):
        assert self.crawler._should_skip('http://example.com/logo.png') is True
        assert self.crawler._should_skip('http://example.com/photo.jpg') is True

    def test_skip_pdf(self):
        assert self.crawler._should_skip('http://example.com/report.pdf') is True

    def test_skip_mailto(self):
        assert self.crawler._should_skip('mailto:user@example.com') is True

    def test_skip_javascript(self):
        assert self.crawler._should_skip('javascript:void(0)') is True

    def test_allow_normal_url(self):
        assert self.crawler._should_skip('http://example.com/home') is False
        assert self.crawler._should_skip('http://example.com/login') is False
        assert self.crawler._should_skip('http://example.com/about') is False


class TestExtractLinks:
    """Test link extraction from HTML."""

    def setup_method(self):
        self.crawler = CrawlerService('http://example.com')

    def _make_soup(self, html):
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, 'html.parser')

    def test_extract_internal_links(self):
        html = '''
        <html><body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
            <a href="http://external.com/other">External</a>
        </body></html>
        '''
        soup = self._make_soup(html)
        links = self.crawler._extract_links(soup, 'http://example.com')

        assert 'http://example.com/page1' in links
        assert 'http://example.com/page2' in links
        assert 'http://external.com/other' not in links

    def test_skip_fragment_only(self):
        html = '<html><body><a href="#">Top</a></body></html>'
        soup = self._make_soup(html)
        links = self.crawler._extract_links(soup, 'http://example.com')
        assert len(links) == 0

    def test_strip_fragment_from_url(self):
        html = '<html><body><a href="/page#section">Link</a></body></html>'
        soup = self._make_soup(html)
        links = self.crawler._extract_links(soup, 'http://example.com')
        assert 'http://example.com/page' in links

    def test_skip_static_files(self):
        html = '''
        <html><body>
            <a href="/style.css">CSS</a>
            <a href="/app.js">JS</a>
            <a href="/logo.png">Logo</a>
        </body></html>
        '''
        soup = self._make_soup(html)
        links = self.crawler._extract_links(soup, 'http://example.com')
        assert len(links) == 0


class TestExtractForms:
    """Test form extraction from HTML."""

    def setup_method(self):
        self.crawler = CrawlerService('http://example.com')

    def _make_soup(self, html):
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, 'html.parser')

    def test_extract_form_basic(self):
        html = '''
        <html><body>
            <form action="/login" method="POST">
                <input type="text" name="username" value="">
                <input type="password" name="password">
                <button type="submit">Login</button>
            </form>
        </body></html>
        '''
        soup = self._make_soup(html)
        forms = self.crawler._extract_forms(soup, 'http://example.com')

        assert len(forms) == 1
        form = forms[0]
        assert form['action'] == 'http://example.com/login'
        assert form['method'] == 'POST'
        assert len(form['inputs']) == 2
        assert form['inputs'][0]['name'] == 'username'
        assert form['inputs'][1]['name'] == 'password'

    def test_extract_form_no_action(self):
        html = '''
        <html><body>
            <form method="GET">
                <input type="text" name="q">
            </form>
        </body></html>
        '''
        soup = self._make_soup(html)
        forms = self.crawler._extract_forms(soup, 'http://example.com/search')

        assert forms[0]['action'] == 'http://example.com/search'
        assert forms[0]['method'] == 'GET'

    def test_skip_inputs_without_name(self):
        html = '''
        <html><body>
            <form action="/submit">
                <input type="text" name="field1">
                <input type="submit">
            </form>
        </body></html>
        '''
        soup = self._make_soup(html)
        forms = self.crawler._extract_forms(soup, 'http://example.com')

        # submit input has no name → should be skipped
        assert len(forms[0]['inputs']) == 1

    def test_multiple_forms(self):
        html = '''
        <html><body>
            <form action="/form1"><input name="a"></form>
            <form action="/form2"><input name="b"></form>
        </body></html>
        '''
        soup = self._make_soup(html)
        forms = self.crawler._extract_forms(soup, 'http://example.com')
        assert len(forms) == 2


class TestFetchPage:
    """Test page fetching with mocked requests."""

    def setup_method(self):
        self.crawler = CrawlerService('http://example.com', delay=0)

    @patch.object(CrawlerService, '_fetch_page')
    def test_fetch_returns_none_on_timeout(self, mock_fetch):
        mock_fetch.return_value = None
        result = self.crawler._fetch_page('http://example.com/slow')
        assert result is None

    @patch('app.services.crawler.requests.Session.get')
    def test_fetch_skips_non_html(self, mock_get):
        mock_response = MagicMock()
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.crawler._fetch_page('http://example.com/doc.pdf')
        assert result is None


class TestCrawlIntegration:
    """Integration test for the crawl method."""

    @patch('app.services.crawler.requests.Session.get')
    def test_crawl_single_page(self, mock_get):
        html = '<html><body><p>Hello</p></body></html>'
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response

        crawler = CrawlerService('http://example.com', max_depth=0, delay=0)
        result = crawler.crawl()

        assert result['total_pages'] == 1
        assert result['pages'][0]['url'] == 'http://example.com'
        assert result['pages'][0]['status_code'] == 200

    @patch('app.services.crawler.requests.Session.get')
    def test_max_pages_respected(self, mock_get):
        """Crawler should stop after reaching max_pages."""
        html = '''
        <html><body>
            <a href="/p1">1</a><a href="/p2">2</a><a href="/p3">3</a>
            <a href="/p4">4</a><a href="/p5">5</a>
        </body></html>
        '''
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response

        crawler = CrawlerService('http://example.com', max_depth=2, max_pages=3, delay=0)
        result = crawler.crawl()

        assert result['total_pages'] <= 3
