"""
Scanner Engine (Orchestrator)

Coordinates the scanning workflow:
1. Create scan record in DB
2. Crawl target website
3. Save discovered pages to DB
4. Run vulnerability detection (SQLi, XSS)
5. Save vulnerability findings to DB
6. Run AI remediation advice generation
7. Save AI remediation results to DB
8. Update scan record with final stats
"""

import json
import logging
from datetime import datetime, timezone

from flask import current_app

from app import db
from app.models.scan import Scan
from app.models.page import Page
from app.models.vulnerability import Vulnerability
from app.models.ai_result import AIResult
from app.services.crawler import CrawlerService
from app.services.detector import VulnerabilityDetector
from app.services.ai_advisor import AIAdvisor

logger = logging.getLogger(__name__)


class ScannerEngine:
    """Orchestrates the complete scanning pipeline."""

    def __init__(self, target_url, scan_config=None, user_id=None):
        self.target_url = target_url
        self.config = scan_config or {}
        self.user_id = user_id
        self.scan = None

    def run(self):
        """Execute the complete scanning pipeline.

        Returns the Scan ORM object with all results persisted to DB.
        """
        try:
            self._create_scan_record()
            crawl_results = self._run_crawler()
            self._save_pages(crawl_results)

            # Run vulnerability detection if any test is enabled
            findings = self._run_detection(crawl_results)
            saved_vulns = []
            if findings:
                saved_vulns = self._save_vulnerabilities(findings)

            # Run AI remediation if enabled and findings exist
            if self.config.get('use_ai', True) and saved_vulns:
                self._run_ai_remediation(findings, saved_vulns)

            self._finalize_scan(crawl_results, len(findings))
            return self.scan

        except Exception as exc:
            logger.error("Scan failed for %s: %s", self.target_url, exc)
            self._mark_failed(str(exc))
            raise

    def _create_scan_record(self):
        """Step 0: Create a new scan record in the database."""
        if not self.user_id:
            raise ValueError("user_id is required to create a scan record")

        self.scan = Scan(
            user_id=self.user_id,
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

    def _run_detection(self, crawl_results):
        """Step 3: Run vulnerability detection on discovered forms.

        Tests each form for enabled vulnerability types (SQLi, XSS).
        Returns a flat list of all findings.
        """
        forms = crawl_results.get('forms', [])
        if not forms:
            logger.info("Scan #%d: no forms found — skipping detection",
                        self.scan.id)
            return []

        test_sqli = self.config.get('test_sqli', True)
        test_xss = self.config.get('test_xss', False)

        if not test_sqli and not test_xss:
            logger.info("Scan #%d: no detection types enabled", self.scan.id)
            return []

        detector = VulnerabilityDetector(
            timeout=self.config.get('timeout', 10),
        )

        all_findings = []

        for i, form in enumerate(forms, 1):
            logger.info(
                "Scan #%d: testing form %d/%d — %s (%s)",
                self.scan.id, i, len(forms),
                form.get('action', '?'), form.get('method', '?'),
            )

            if test_sqli:
                sqli_findings = detector.test_sqli(form)
                all_findings.extend(sqli_findings)

            if test_xss:
                xss_findings = detector.test_xss(form) or []
                all_findings.extend(xss_findings)

        logger.info(
            "Scan #%d: detection complete — %d vulnerabilities found",
            self.scan.id, len(all_findings),
        )
        return all_findings

    def _save_vulnerabilities(self, findings):
        """Step 4: Save vulnerability findings to the database.

        Returns:
            list[Vulnerability]: The persisted ORM objects (with IDs set).
        """
        saved = []
        for finding in findings:
            vuln = Vulnerability(
                scan_id=self.scan.id,
                vuln_type=finding.get('vuln_type', 'unknown'),
                severity=finding.get('severity', 'medium'),
                url=finding.get('url', ''),
                parameter=finding.get('parameter', ''),
                payload=finding.get('payload', ''),
                evidence=finding.get('evidence', ''),
            )
            db.session.add(vuln)
            saved.append(vuln)

        db.session.commit()
        logger.info("Scan #%d: saved %d vulnerabilities to DB",
                     self.scan.id, len(findings))
        return saved

    def _run_ai_remediation(self, findings, saved_vulns):
        """Step 5: Generate AI remediation advice for findings.

        Uses Gemini API (or static fallback) to generate remediation
        recommendations for each finding.  Results are saved as
        AIResult records linked to their Vulnerability row.
        """
        api_key = ''
        try:
            api_key = current_app.config.get('GEMINI_API_KEY', '')
        except RuntimeError:
            pass

        advisor = AIAdvisor(api_key=api_key)

        logger.info(
            "Scan #%d: generating AI remediation for %d findings %s",
            self.scan.id, len(findings),
            '(Gemini)' if advisor.is_available() else '(fallback)',
        )

        for finding, vuln_obj in zip(findings, saved_vulns):
            advice = advisor.get_remediation(
                vuln_type=finding.get('vuln_type', 'unknown'),
                severity=finding.get('severity', 'medium'),
                url=finding.get('url', ''),
                parameter=finding.get('parameter', ''),
                payload=finding.get('payload', ''),
                evidence=finding.get('evidence', ''),
            )

            record = AIResult(
                scan_id=self.scan.id,
                vulnerability_id=vuln_obj.id,
                url=finding.get('url', ''),
                explanation=advice.get('explanation', ''),
                impact=advice.get('impact', ''),
                remediation=json.dumps(
                    advice.get('remediation_steps', []),
                    ensure_ascii=False,
                ),
                code_example=advice.get('code_example', ''),
            )
            db.session.add(record)

        db.session.commit()
        logger.info(
            "Scan #%d: AI remediation complete — %d recommendations saved",
            self.scan.id, len(findings),
        )

    def _finalize_scan(self, crawl_results, vuln_count=0):
        """Step final: Update scan record with stats and mark completed."""
        self.scan.status = 'completed'
        self.scan.completed_at = datetime.now(timezone.utc)
        self.scan.total_pages = crawl_results['total_pages']
        self.scan.total_forms = crawl_results['total_forms']
        self.scan.total_vulnerabilities = vuln_count
        db.session.commit()
        logger.info("Scan #%d completed successfully — %d vulns",
                     self.scan.id, vuln_count)

    def _mark_failed(self, error_message):
        """Mark scan as failed if an error occurs."""
        if self.scan and self.scan.id:
            self.scan.status = 'failed'
            self.scan.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            logger.error("Scan #%d marked as failed: %s",
                         self.scan.id, error_message)
