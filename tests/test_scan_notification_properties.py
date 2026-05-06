"""
Property-based tests for Scan Notification and Previous Scan Progress Panel.
Uses Hypothesis to verify correctness properties defined in the design document.

Properties tested:
  P1 - Toast always has a close button (for any valid flash category/message)
  P2 - Progress Panel shows all 6 required fields for any completed/failed scan
  P3 - Severity badge appears when total_vulnerabilities > 0
  P4 - "View Full Results" link always uses the correct scan ID
  P5 - _get_last_scan() always returns the scan with the most recent completed_at
  P6 - Flash scan_success message always produces a toast showing the vuln count
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

from app import create_app, db
from app.models.scan import Scan
from app.routes.scan import _get_last_scan


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def app():
    """Module-scoped Flask app with in-memory SQLite."""
    test_app = create_app()
    test_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'pbt-secret-key',
    })
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Provide an active app context and clean DB for each test."""
    with app.app_context():
        # Clean all scans before each property test
        db.session.query(Scan).delete()
        db.session.commit()
        yield app
        db.session.query(Scan).delete()
        db.session.commit()


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

safe_text = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), whitelist_characters='.-_/:'),
    min_size=1,
    max_size=80,
)

scan_status = st.sampled_from(['completed', 'failed'])

flash_category = st.sampled_from(['scan_success', 'scan_error'])


def scan_strategy():
    """Strategy that generates Scan-like objects (dicts) for template testing."""
    return st.fixed_dictionaries({
        'id': st.integers(min_value=1, max_value=99999),
        'target_url': st.just('http://example.com'),
        'status': scan_status,
        'total_pages': st.integers(min_value=0, max_value=500),
        'total_forms': st.integers(min_value=0, max_value=200),
        'total_vulnerabilities': st.integers(min_value=0, max_value=100),
        'completed_at': st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 12, 31),
            timezones=st.just(timezone.utc),
        ),
    })


# ---------------------------------------------------------------------------
# P1: Toast always has a close button
# ---------------------------------------------------------------------------

class TestP1ToastAlwaysHasCloseButton:
    """
    Feature: scan-notification-and-progress, Property 1
    For any flash message of category scan_success or scan_error,
    the rendered HTML must contain a toast-close button.
    """

    @given(
        category=flash_category,
        message=safe_text,
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_toast_always_has_close_button(self, client, app, category, message):
        with client.session_transaction() as sess:
            sess['_flashes'] = [(category, message)]

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'toast-close' in html, (
            f"Toast close button missing for category={category!r}, message={message!r}"
        )


# ---------------------------------------------------------------------------
# P2: Progress Panel shows all 6 required fields
# ---------------------------------------------------------------------------

class TestP2ProgressPanelShowsAllFields:
    """
    Feature: scan-notification-and-progress, Property 2
    For any Scan object with status completed or failed passed as last_scan,
    the rendered HTML must contain all 6 required fields.
    """

    @given(scan_data=scan_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_progress_panel_shows_all_fields(self, client, app, scan_data):
        # Build a mock Scan object from the strategy data
        mock_scan = _build_mock_scan(scan_data)

        with patch('app.routes.scan._get_last_scan', return_value=mock_scan):
            response = client.get('/scan/new')

        html = response.data.decode()

        # All 6 required fields must appear in the rendered HTML
        assert scan_data['target_url'] in html, "target_url missing from panel"
        assert str(scan_data['total_pages']) in html, "total_pages missing from panel"
        assert str(scan_data['total_forms']) in html, "total_forms missing from panel"
        assert str(scan_data['total_vulnerabilities']) in html, "total_vulnerabilities missing from panel"
        # completed_at date portion
        expected_date = scan_data['completed_at'].strftime('%Y-%m-%d')
        assert expected_date in html, f"completed_at ({expected_date}) missing from panel"
        # status is reflected via badge text
        assert 'panel-badge' in html, "status badge missing from panel"


# ---------------------------------------------------------------------------
# P3: Severity badge appears when total_vulnerabilities > 0
# ---------------------------------------------------------------------------

class TestP3SeverityBadgeWhenVulnsPresent:
    """
    Feature: scan-notification-and-progress, Property 3
    For any completed scan with total_vulnerabilities > 0,
    the panel must contain a danger badge element.
    """

    @given(vuln_count=st.integers(min_value=1, max_value=1000))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_severity_badge_when_vulns_present(self, client, app, vuln_count):
        mock_scan = _build_mock_scan({
            'id': 1,
            'target_url': 'http://example.com',
            'status': 'completed',
            'total_pages': 5,
            'total_forms': 2,
            'total_vulnerabilities': vuln_count,
            'completed_at': datetime(2025, 1, 1, tzinfo=timezone.utc),
        })

        with patch('app.routes.scan._get_last_scan', return_value=mock_scan):
            response = client.get('/scan/new')

        html = response.data.decode()

        assert 'panel-badge--danger' in html, (
            f"Danger badge missing for total_vulnerabilities={vuln_count}"
        )


# ---------------------------------------------------------------------------
# P4: "View Full Results" link always uses the correct scan ID
# ---------------------------------------------------------------------------

class TestP4ViewResultsLinkCorrectId:
    """
    Feature: scan-notification-and-progress, Property 4
    For any Scan with id=N, the panel must contain an <a> href ending in /results/N.
    """

    @given(scan_id=st.integers(min_value=1, max_value=99999))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_view_results_link_uses_correct_id(self, client, app, scan_id):
        mock_scan = _build_mock_scan({
            'id': scan_id,
            'target_url': 'http://example.com',
            'status': 'completed',
            'total_pages': 1,
            'total_forms': 0,
            'total_vulnerabilities': 0,
            'completed_at': datetime(2025, 1, 1, tzinfo=timezone.utc),
        })

        with patch('app.routes.scan._get_last_scan', return_value=mock_scan):
            response = client.get('/scan/new')

        html = response.data.decode()

        assert f'/results/{scan_id}' in html, (
            f"Expected /results/{scan_id} in HTML but not found"
        )


# ---------------------------------------------------------------------------
# P5: _get_last_scan() always returns the scan with the most recent completed_at
# ---------------------------------------------------------------------------

class TestP5QueryReturnsMostRecentScan:
    """
    Feature: scan-notification-and-progress, Property 5
    For any set of Scan records with distinct completed_at values,
    _get_last_scan() must return the one with the largest completed_at
    among those with status in ('completed', 'failed').
    """

    @given(
        offsets=st.lists(
            st.integers(min_value=0, max_value=10000),
            min_size=1,
            max_size=15,
            unique=True,
        )
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_last_scan_query_returns_most_recent(self, app_context, offsets):
        base_time = datetime(2025, 1, 1, tzinfo=timezone.utc)
        statuses = ['completed', 'failed']

        scans = []
        for i, offset in enumerate(offsets):
            scan = Scan(
                target_url=f'http://example{i}.com',
                status=statuses[i % 2],
                total_pages=1,
                total_forms=0,
                total_vulnerabilities=0,
                completed_at=base_time + timedelta(seconds=offset),
            )
            db.session.add(scan)
            scans.append((offset, scan))

        db.session.commit()

        result = _get_last_scan()

        assert result is not None
        max_offset = max(offsets)
        expected_time = base_time + timedelta(seconds=max_offset)
        assert result.completed_at.replace(tzinfo=timezone.utc) == expected_time, (
            f"Expected scan with completed_at={expected_time}, got {result.completed_at}"
        )


# ---------------------------------------------------------------------------
# P6: Flash scan_success always produces a toast showing the vuln count
# ---------------------------------------------------------------------------

class TestP6FlashMessageProducesCorrectToast:
    """
    Feature: scan-notification-and-progress, Property 6
    For any flash message of category scan_success containing an integer N,
    the rendered HTML must contain a toast element displaying N.
    For scan_error, the rendered HTML must contain a toast--error element.
    """

    @given(vuln_count=st.integers(min_value=0, max_value=9999))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_success_flash_shows_vuln_count(self, client, app, vuln_count):
        vuln_word = 'vulnerability' if vuln_count == 1 else 'vulnerabilities'
        message = f"Scanned http://example.com — {vuln_count} {vuln_word} found."

        with client.session_transaction() as sess:
            sess['_flashes'] = [('scan_success', message)]

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'toast--success' in html, "Success toast not rendered"
        assert str(vuln_count) in html, (
            f"Vuln count {vuln_count} not found in toast HTML"
        )

    @given(error_msg=safe_text)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_error_flash_shows_error_toast(self, client, app, error_msg):
        message = f"Scan failed for http://example.com: {error_msg}"

        with client.session_transaction() as sess:
            sess['_flashes'] = [('scan_error', message)]

        response = client.get('/scan/new')
        html = response.data.decode()

        assert 'toast--error' in html, "Error toast not rendered for scan_error flash"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _build_mock_scan(data: dict):
    """Build a simple namespace object that mimics a Scan ORM instance."""
    from types import SimpleNamespace
    return SimpleNamespace(**data)
