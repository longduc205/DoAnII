"""
Web Crawler Service

Responsible for:
- Discovering internal pages from a target URL
- Extracting links, forms, and input fields
- Filtering duplicate and out-of-scope URLs
- Respecting crawl depth and page limits
"""

import logging
import time
from urllib.parse import urljoin, urlparse
from collections import deque

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# File extensions to skip during crawling
SKIP_EXTENSIONS = frozenset([
    '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.pdf', '.zip', '.tar', '.gz', '.mp3', '.mp4', '.avi', '.mov',
    '.woff', '.woff2', '.ttf', '.eot', '.map',
])

# URL patterns to skip (logout, static assets, etc.)
SKIP_PATTERNS = frozenset([
    'logout', 'signout', 'sign-out', 'log-out',
    'mailto:', 'tel:', 'javascript:',
])

DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (compatible; AIVulnScanner/1.0; '
        '+https://github.com/educational-scanner)'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


class CrawlerService:
    """Crawls a target website to discover pages and forms."""

    def __init__(self, base_url, max_depth=3, max_pages=50, timeout=10, delay=0.5):
        self.base_url = self._normalize_url(base_url)
        self.base_domain = urlparse(self.base_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.timeout = timeout
        self.delay = delay

        self.visited_urls = set()
        self.discovered_pages = []
        self.discovered_forms = []

        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def crawl(self):
        """Start BFS crawling from the base URL.

        Returns a dict with discovered pages, forms, and counts.
        """
        logger.info("Starting crawl: %s (depth=%d, max_pages=%d)",
                     self.base_url, self.max_depth, self.max_pages)

        queue = deque([(self.base_url, 0)])

        while queue and len(self.visited_urls) < self.max_pages:
            url, depth = queue.popleft()

            if url in self.visited_urls or depth > self.max_depth:
                continue

            page_data = self._fetch_page(url)
            if page_data is None:
                continue

            self.visited_urls.add(url)
            self.discovered_pages.append({
                'url': url,
                'depth': depth,
                'status_code': page_data['status_code'],
            })

            # Extract and process forms
            forms = self._extract_forms(page_data['soup'], url)
            self.discovered_forms.extend(forms)

            page_form_count = len(forms)
            logger.info(
                "[depth=%d] %s — status=%d, forms=%d",
                depth, url, page_data['status_code'], page_form_count,
            )

            # Extract links and add to queue
            if depth < self.max_depth:
                links = self._extract_links(page_data['soup'], url)
                new_links = links - self.visited_urls
                for link in new_links:
                    queue.append((link, depth + 1))
                if new_links:
                    logger.debug("  Found %d new links", len(new_links))

            # Polite delay between requests
            if self.delay > 0:
                time.sleep(self.delay)

        logger.info(
            "Crawl complete: %d pages, %d forms discovered",
            len(self.discovered_pages), len(self.discovered_forms),
        )

        return {
            'pages': self.discovered_pages,
            'forms': self.discovered_forms,
            'total_pages': len(self.discovered_pages),
            'total_forms': len(self.discovered_forms),
        }

    def _fetch_page(self, url):
        """Fetch a page and return parsed content, or None on failure."""
        try:
            response = self.session.get(url, timeout=self.timeout)

            # Only parse HTML responses
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type and 'application/xhtml' not in content_type:
                logger.debug("Skipping non-HTML: %s (%s)", url, content_type)
                return None

            soup = BeautifulSoup(response.text, 'html.parser')
            return {
                'soup': soup,
                'status_code': response.status_code,
                'content': response.text,
                'content_length': len(response.text),
            }

        except requests.ConnectionError:
            logger.warning("Connection error: %s", url)
            return None
        except requests.Timeout:
            logger.warning("Timeout: %s", url)
            return None
        except requests.RequestException as exc:
            logger.warning("Request failed for %s: %s", url, exc)
            return None

    def _extract_links(self, soup, current_url):
        """Extract all internal links from a page."""
        links = set()
        for anchor in soup.find_all('a', href=True):
            href = anchor['href'].strip()

            # Skip empty and fragment-only hrefs
            if not href or href.startswith('#'):
                continue

            full_url = urljoin(current_url, href)

            # Only follow links within the same domain
            if urlparse(full_url).netloc == self.base_domain:
                clean_url = full_url.split('#')[0]  # Remove fragments
                if not self._should_skip(clean_url):
                    links.add(clean_url)

        return links

    def _extract_forms(self, soup, page_url):
        """Extract all forms and their input fields from a page."""
        forms = []
        for form in soup.find_all('form'):
            action = form.get('action', '')
            form_data = {
                'page_url': page_url,
                'action': urljoin(page_url, action) if action else page_url,
                'method': form.get('method', 'GET').upper(),
                'inputs': [],
            }

            for input_tag in form.find_all(['input', 'textarea', 'select']):
                name = input_tag.get('name', '')
                if not name:
                    continue

                input_data = {
                    'name': name,
                    'type': input_tag.get('type', 'text'),
                    'value': input_tag.get('value', ''),
                }
                form_data['inputs'].append(input_data)

            forms.append(form_data)

        return forms

    def _should_skip(self, url):
        """Check if a URL should be skipped during crawling."""
        url_lower = url.lower()

        # Skip known patterns (logout, mailto, etc.)
        if any(pattern in url_lower for pattern in SKIP_PATTERNS):
            return True

        # Skip static file extensions
        parsed_path = urlparse(url_lower).path
        if any(parsed_path.endswith(ext) for ext in SKIP_EXTENSIONS):
            return True

        return False

    @staticmethod
    def _normalize_url(url):
        """Ensure URL has a scheme."""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
