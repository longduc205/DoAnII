"""
Scanner Engine (Orchestrator)

Coordinates the scanning workflow:
1. Create scan record in DB
2. Crawl target website
3. Save discovered pages to DB
4. Run vulnerability detection (Phase 3+)
5. Run AI analysis (Phase 3+)
6. Update scan record with final stats
"""

import logging
from datetime import datetime, timezone

from app import db
from app.models.scan import Scan
from app.models.page import Page
from app.services.crawler import CrawlerService

logger = logging.getLogger(__name__)


class ScannerEngine:
    """Orchestrates the complete scanning pipeline."""

    def __init__(self, target_url, scan_config=None):
        self.target_url = target_url
        self.config = scan_config or {}
        self.scan = None

    def run(self):
        """Execute the complete scanning pipeline.

        Returns the Scan ORM object with all results persisted to DB.
        """
        try:
            self._create_scan_record()
            crawl_results = self._run_crawler()
            self._save_pages(crawl_results)
            self._finalize_scan(crawl_results)
            return self.scan

        except Exception as exc:
            logger.error("Scan failed for %s: %s", self.target_url, exc)
            self._mark_failed(str(exc))
            raise

    def _create_scan_record(self):
        """Step 0: Create a new scan record in the database."""
        self.scan = Scan(
            target_url=self.target_url,
            status='running',
            started_at=datetime.now(timezone.utc),
        )
        db.session.add(self.scan)
        db.session.commit()
        logger.info("Scan #%d created for %s", self.scan.id, self.target_url)

    def _run_crawler(self):
        """Step 1: Crawl the target website."""
        crawl_depth = self.config.get('crawl_depth', 2)
        max_pages = self.config.get('max_pages', 50)

        crawler = CrawlerService(
            base_url=self.target_url,
            max_depth=crawl_depth,
            max_pages=max_pages,
        )
        results = crawler.crawl()
        logger.info(
            "Scan #%d crawled %d pages, %d forms",
            self.scan.id, results['total_pages'], results['total_forms'],
        )
        return results

    def _save_pages(self, crawl_results):
        """Step 2: Save discovered pages to the database."""
        for page_data in crawl_results['pages']:
            # Count forms on this page
            forms_on_page = [
                f for f in crawl_results['forms']
                if f['page_url'] == page_data['url']
            ]

            page = Page(
                scan_id=self.scan.id,
                url=page_data['url'],
                status_code=page_data.get('status_code'),
                depth=page_data.get('depth', 0),
                has_forms=len(forms_on_page) > 0,
                form_count=len(forms_on_page),
            )
            db.session.add(page)

        db.session.commit()
        logger.info("Scan #%d: saved %d pages to DB",
                     self.scan.id, len(crawl_results['pages']))

    def _finalize_scan(self, crawl_results):
        """Step final: Update scan record with stats and mark completed."""
        self.scan.status = 'completed'
        self.scan.completed_at = datetime.now(timezone.utc)
        self.scan.total_pages = crawl_results['total_pages']
        self.scan.total_forms = crawl_results['total_forms']
        self.scan.total_vulnerabilities = 0  # Will be updated in detection phase
        db.session.commit()
        logger.info("Scan #%d completed successfully", self.scan.id)

    def _mark_failed(self, error_message):
        """Mark scan as failed if an error occurs."""
        if self.scan and self.scan.id:
            self.scan.status = 'failed'
            self.scan.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            logger.error("Scan #%d marked as failed: %s",
                         self.scan.id, error_message)
