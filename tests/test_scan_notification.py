"""
Unit tests (example-based) for Scan Notification and Previous Scan Progress Panel.

Tests cover:
- Toast rendering from flash messages (scan_success / scan_error)
- Progress Panel rendering with last_scan data
- Empty state when no scan exists
- Failed scan state
- Clean scan state (no vulnerabilities)
- DB error fallback (_get_last_scan returns None)
- Flash message categories
- Navigation links
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from app import create_app, db
from app.models.scan import Scan


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Create a Flask test application with an in-memory SQLite database."""
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
    })
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


def _make_scan(
    target_url='http://example.com',
    status='completed',
    total_pages=5,
    total_forms=3,
    total_vulnerabilities=2,
    completed_at=None,
):
    """Helper to create and persist a Scan record."""
    scan = Scan(
        target_url=target_url,
        status=status,
        total_pages=total_pages,
        total_forms=total_forms,
        total_vulnerabilities=total_vulnerabilities,
        completed_at=completed_at or datetime.now(timezone.utc),
    )
    db.session.add(scan)
    db.session.commit()
    return scan


# ---------------------------------------------------------------------------
# Toast Notification Tests
# ---------------------------------------------------------------------------

class TestToastNotification:
    """Tests for flash-message-driven toast rendering in base.html."""

    def test_toast_renders_on_scan_success_flash(self, client, app):
        """Flash scan_success → toast with success class appears in HTML."""
        with client.session_transaction() as sess:
            # Manually inject a flash message into the session
            sess['_flashes'] = [('scan_success', 'Scanned http://example.com — 2 vulnerabilities found.')]

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'toast--success' in html
        assert 'Scan Complete' in html
        assert 'Scanned http://example.com' in html

    def test_toast_renders_on_scan_error_flash(self, client, app):
        """Flash scan_error → toast with error class appears in HTML."""
        with client.session_transaction() as sess:
            sess['_flashes'] = [('scan_error', 'Scan failed for http://example.com: timeout')]

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'toast--error' in html
        assert 'Scan Failed' in html
        assert 'Scan failed for http://example.com' in html

    def test_no_toast_without_flash(self, client, app):
        """No flash message → no toast rendered."""
        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'toast--success' not in html
        assert 'toast--error' not in html

    def test_toast_has_close_button(self, client, app):
        """Every rendered toast must contain a close button."""
        with client.session_transaction() as sess:
            sess['_flashes'] = [('scan_success', 'Scanned http://example.com — 0 vulnerabilities found.')]

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'toast-close' in html

    def test_unknown_flash_category_not_rendered(self, client, app):
        """Flash messages with unsupported categories are silently ignored."""
        with client.session_transaction() as sess:
            sess['_flashes'] = [('info', 'Some info message')]

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'toast--success' not in html
        assert 'toast--error' not in html
        assert 'Some info message' not in html


# ---------------------------------------------------------------------------
# Progress Panel Tests
# ---------------------------------------------------------------------------

class TestProgressPanel:
    """Tests for the Previous Scan Progress Panel in scan.html."""

    def test_progress_panel_empty_state(self, client, app):
        """No scans in DB → placeholder message shown."""
        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'No previous scans available' in html

    def test_progress_panel_shows_completed_scan(self, client, app):
        """Completed scan in DB → panel renders all 6 fields."""
        with app.app_context():
            scan = _make_scan(
                target_url='http://test.com',
                status='completed',
                total_pages=10,
                total_forms=4,
                total_vulnerabilities=3,
                completed_at=datetime(2025, 1, 15, 12, 30, 0, tzinfo=timezone.utc),
            )
            scan_id = scan.id

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'http://test.com' in html
        assert 'completed' in html.lower() or 'Completed' in html
        assert '10' in html   # total_pages
        assert '4' in html    # total_forms
        assert '3' in html    # total_vulnerabilities
        assert '2025-01-15' in html  # completed_at date

    def test_progress_panel_clean_scan(self, client, app):
        """Completed scan with 0 vulnerabilities → green success badge."""
        with app.app_context():
            _make_scan(total_vulnerabilities=0, status='completed')

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'panel-badge--success' in html
        assert 'panel-badge--danger' not in html

    def test_progress_panel_failed_scan(self, client, app):
        """Failed scan → error badge with 'Scan Failed' text."""
        with app.app_context():
            _make_scan(status='failed', total_vulnerabilities=0)

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'panel-badge--error' in html
        assert 'Scan Failed' in html

    def test_progress_panel_vuln_scan_shows_danger_badge(self, client, app):
        """Completed scan with vulnerabilities → danger badge."""
        with app.app_context():
            _make_scan(status='completed', total_vulnerabilities=5)

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'panel-badge--danger' in html

    def test_history_link_present(self, client, app):
        """Progress panel always includes a link to scan history."""
        with app.app_context():
            _make_scan()

        response = client.get('/scan/new')
        html = response.data.decode()

        assert '/history' in html
        assert 'View All History' in html

    def test_view_full_results_link(self, client, app):
        """Progress panel includes a 'View Full Results' link with correct scan ID."""
        with app.app_context():
            scan = _make_scan()
            scan_id = scan.id

        response = client.get('/scan/new')
        html = response.data.decode()

        assert f'/results/{scan_id}' in html
        assert 'View Full Results' in html


# ---------------------------------------------------------------------------
# Route / DB Integration Tests
# ---------------------------------------------------------------------------

class TestScanRouteIntegration:
    """Tests for scan route behavior with last_scan and flash messages."""

    def test_scan_route_get_passes_last_scan(self, client, app):
        """GET /scan/new passes last_scan to template when scan exists."""
        with app.app_context():
            _make_scan(target_url='http://route-test.com')

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'http://route-test.com' in html

    def test_scan_route_get_passes_none_when_no_scan(self, client, app):
        """GET /scan/new renders empty state when no scans exist."""
        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'No previous scans available' in html

    def test_scan_route_post_sets_flash_success(self, client, app):
        """POST scan success → flash scan_success is set and redirect occurs."""
        mock_scan = MagicMock()
        mock_scan.id = 42
        mock_scan.total_vulnerabilities = 1

        with patch('app.routes.scan.ScannerEngine') as MockEngine:
            MockEngine.return_value.run.return_value = mock_scan
            response = client.post('/scan/new', data={
                'target_url': 'http://example.com',
                'crawl_depth': '2',
                'test_sqli': 'on',
                'test_xss': 'on',
            })

        # Should redirect to results page
        assert response.status_code == 302
        assert '/results/42' in response.headers.get('Location', '')

    def test_scan_route_post_sets_flash_error(self, client, app):
        """POST scan failure → flash scan_error is set and error page renders."""
        with patch('app.routes.scan.ScannerEngine') as MockEngine:
            MockEngine.return_value.run.side_effect = Exception('Connection refused')
            response = client.post('/scan/new', data={
                'target_url': 'http://example.com',
                'crawl_depth': '2',
            })

        html = response.data.decode()
        assert response.status_code == 200
        assert 'Scan failed' in html or 'Connection refused' in html

    def test_db_error_returns_none_last_scan(self, app):
        """DB exception in _get_last_scan → returns None, page still renders."""
        from app.routes.scan import _get_last_scan

        with app.app_context():
            with patch('app.routes.scan.Scan') as MockScan:
                MockScan.query.filter.side_effect = Exception('DB connection lost')
                result = _get_last_scan()

        assert result is None

    def test_scan_route_get_renders_without_crash_on_db_error(self, client, app):
        """GET /scan/new renders successfully even when DB query fails."""
        with patch('app.routes.scan._get_last_scan', return_value=None):
            response = client.get('/scan/new')

        assert response.status_code == 200
        assert 'No previous scans available' in response.data.decode()
