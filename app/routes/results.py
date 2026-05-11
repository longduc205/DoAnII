"""
Results routes - Display scan results with AI remediation
"""

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.models.ai_result import AIResult

results_bp = Blueprint('results', __name__)


@results_bp.route('/<int:scan_id>')
@login_required
def show_results(scan_id):
    """Display results for a specific scan session."""
    scan = Scan.query.get_or_404(scan_id)
    if scan.user_id != current_user.id:
        abort(403)
    vulnerabilities = Vulnerability.query.filter_by(scan_id=scan_id).all()
    ai_results = AIResult.query.filter_by(scan_id=scan_id).all()

    # Build a lookup: vulnerability_id → AIResult for per-finding display
    ai_by_vuln = {}
    for ar in ai_results:
        if ar.vulnerability_id:
            ai_by_vuln[ar.vulnerability_id] = ar

    # AI summary stats
    ai_summary = {
        'total': len(ai_results),
        'has_results': len(ai_results) > 0,
    }

    return render_template(
        'results.html',
        scan=scan,
        vulnerabilities=vulnerabilities,
        ai_summary=ai_summary,
        ai_by_vuln=ai_by_vuln,
    )
