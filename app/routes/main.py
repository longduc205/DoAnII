"""
Main routes - Dashboard (Home page)
"""

from flask import Blueprint, render_template

from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.models.ai_result import AIResult

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render the dashboard with overview stats and recent activity."""
    total_scans = Scan.query.count()
    critical_vulns = Vulnerability.query.filter(
        Vulnerability.severity.in_(['high', 'critical'])
    ).count()
    ai_detections = AIResult.query.filter_by(classification='suspicious').count()

    # Count active (running) scans
    active_scans = Scan.query.filter_by(status='running').count()

    # Risk distribution — count by vuln type
    total_vulns = Vulnerability.query.count()
    if total_vulns > 0:
        sqli_count = Vulnerability.query.filter_by(vuln_type='sqli').count()
        xss_count = Vulnerability.query.filter_by(vuln_type='xss').count()
        other_count = total_vulns - sqli_count - xss_count
        risk_sqli = round(sqli_count / total_vulns * 100)
        risk_xss = round(xss_count / total_vulns * 100)
        risk_other = 100 - risk_sqli - risk_xss
    else:
        risk_sqli = risk_xss = risk_other = 0

    stats = {
        'total_scans': total_scans,
        'critical_vulns': critical_vulns,
        'ai_detections': ai_detections,
        'active_scans': active_scans,
        'risk_sqli': risk_sqli,
        'risk_xss': risk_xss,
        'risk_other': risk_other,
    }

    # Recent activity, last 8 scans for the dashboard list.
    recent_scans = Scan.query.order_by(Scan.started_at.desc()).limit(8).all()

    return render_template(
        'index.html',
        stats=stats,
        recent_scans=recent_scans,
    )
