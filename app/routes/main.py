"""
Main routes - Dashboard (Home page)
"""

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render the dashboard with overview stats and recent activity."""
    # TODO: Replace mock data with actual database queries in Phase 3
    stats = {
        'total_scans': 142,
        'critical_vulns': 12,
        'ai_detections': 48,
        'active_scans': 1,
        'risk_sqli': 40,
        'risk_xss': 35,
        'risk_other': 25,
    }

    recent_activity = [
        {
            'target': 'target-website.com',
            'status': 'Completed',
            'status_class': 'completed',
            'vulns': '1 Critical',
            'time': '2 mins ago',
        },
        {
            'target': 'example-shop.com',
            'status': 'Running (48%)',
            'status_class': 'running',
            'vulns': '0',
            'time': 'Just now',
        },
        {
            'target': 'api.service.io',
            'status': 'Completed',
            'status_class': 'completed',
            'vulns': '0',
            'time': '1 hour ago',
        },
    ]

    return render_template(
        'index.html',
        stats=stats,
        recent_activity=recent_activity,
    )
