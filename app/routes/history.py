"""
History routes - Scan history management
"""

from flask import Blueprint, render_template

history_bp = Blueprint('history', __name__)


@history_bp.route('/')
def scan_history():
    """Display all past scan sessions."""
    # TODO: Replace mock data with actual database queries in Phase 3
    scans = [
        {
            'id': 8924,
            'target': 'target-website.com',
            'date': 'Oct 24, 2026',
            'critical_vulns': 1,
            'vuln_summary': 'SQLi',
        },
        {
            'id': 8923,
            'target': 'internal-api.local',
            'date': 'Oct 23, 2026',
            'critical_vulns': 0,
            'vuln_summary': '',
        },
    ]

    return render_template('history.html', scans=scans)
