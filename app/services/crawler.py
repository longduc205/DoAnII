"""
Web Crawler Service

Responsible for:
- Discovering internal pages from a target URL
- Extracting links, forms, and input fields
- Filtering duplicate and out-of-scope URLs
- Respecting crawl depth and page limits
"""

from urllib.parse import urljoin, urlparse
from collections import deque

import requests
from bs4 import BeautifulSoup


class CrawlerService:
    """Crawls a target website to discover pages and forms."""

    def __init__(self, base_url, max_depth=3, max_pages=50, timeout=10):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.timeout = timeout

        self.visited_urls = set()
        self.discovered_pages = []
        self.discovered_forms = []

    def crawl(self):
        """Start crawling from the base URL."""
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
                'status_code': page_data['status_code']
            })

            # Extract and process forms
            forms = self._extract_forms(page_data['soup'], url)
            self.discovered_forms.extend(forms)

            # Extract links and add to queue
            if depth < self.max_depth:
                links = self._extract_links(page_data['soup'], url)
                for link in links:
                    if link not in self.visited_urls:
                        queue.append((link, depth + 1))

        return {
            'pages': self.discovered_pages,
            'forms': self.discovered_forms,
            'total_pages': len(self.discovered_pages),
            'total_forms': len(self.discovered_forms)
        }

    def _fetch_page(self, url):
        """Fetch a page and return parsed content."""
        try:
            response = requests.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'lxml')
            return {
                'soup': soup,
                'status_code': response.status_code,
                'content': response.text
            }
        except requests.RequestException:
            return None

    def _extract_links(self, soup, current_url):
        """Extract all internal links from a page."""
        links = set()
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            full_url = urljoin(current_url, href)

            # Only follow links within the same domain
            if urlparse(full_url).netloc == self.base_domain:
                # Skip logout, external, and fragment-only links
                if not self._should_skip(full_url):
                    links.add(full_url.split('#')[0])  # Remove fragments

        return links

    def _extract_forms(self, soup, page_url):
        """Extract all forms and their input fields from a page."""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'page_url': page_url,
                'action': urljoin(page_url, form.get('action', '')),
                'method': form.get('method', 'GET').upper(),
                'inputs': []
            }

            for input_tag in form.find_all(['input', 'textarea', 'select']):
                input_data = {
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', 'text'),
                    'value': input_tag.get('value', '')
                }
                if input_data['name']:
                    form_data['inputs'].append(input_data)

            forms.append(form_data)

        return forms

    def _should_skip(self, url):
        """Check if a URL should be skipped during crawling."""
        skip_patterns = ['logout', 'signout', 'sign-out', 'log-out']
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in skip_patterns)
