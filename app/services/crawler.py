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

from bs4 import BeautifulSoup

from app.utils.http_client import HTTPClient

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

        self.http = HTTPClient(timeout=self.timeout)

    def crawl(self):
        """Start BFS crawling from the base URL.

        Returns a dict with discovered pages, forms, and counts.
        """
        logger.info("Starting crawl: %s (depth=%d, max_pages=%d)",
                    self.base_url, self.max_depth, self.max_pages)

        # If we are targeting DVWA, start crawling from index.php after login to ensure we find all links
        start_url = self.base_url
        if "login.php" in self.base_url:
            start_url = self.base_url.replace("login.php", "index.php")
            logger.info("DVWA login page target detected. Re-routing start to: %s", start_url)
        elif self.base_url.endswith('/') or self.base_url.count('/') == 2:
            # It's a root URL like http://dvwa or http://dvwa/
            # For DVWA, we want to jump straight to index.php to avoid redirect issues
            if "dvwa" in self.base_url.lower():
                start_url = self.base_url.rstrip('/') + "/index.php"
                logger.info("DVWA root target detected. Re-routing start to: %s", start_url)

        queue = deque([(start_url, 0)])

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
        resp = self.http.get(url)

        if not resp.get('success'):
            logger.warning("Request failed: %s — %s", url, resp.get('error', 'unknown'))
            return None

        # Only parse HTML responses
        content_type = resp.get('headers', {}).get('Content-Type', '')
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            logger.debug("Skipping non-HTML: %s (%s)", url, content_type)
            return None

        soup = BeautifulSoup(resp['content'], 'html.parser')
        return {
            'soup': soup,
            'status_code': resp.get('status_code', 0),
            'content': resp.get('content', ''),
            'content_length': resp.get('content_length', 0),
        }

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
