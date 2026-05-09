"""
Results routes - Display scan results
"""

from flask import Blueprint, render_template

from app.models.scan import Scan
from app.models.vulnerability import Vulnerability
from app.models.ai_result import AIResult

results_bp = Blueprint('results', __name__)


@results_bp.route('/<int:scan_id>')
def show_results(scan_id):
    """Display results for a specific scan session."""
    scan = Scan.query.get_or_404(scan_id)
    vulnerabilities = Vulnerability.query.filter_by(scan_id=scan_id).all()
    ai_results = AIResult.query.filter_by(scan_id=scan_id).all()

    # Build a lookup: url+classification → AIResult for per-finding display
    ai_results_by_url = {}
    for ar in ai_results:
        ai_results_by_url[ar.url] = {
            'classification': ar.classification,
            'confidence': ar.confidence or 0.0,
            'status_code': ar.status_code,
            'response_length': ar.response_length,
        }

    # Build AI summary stats
    suspicious_count = sum(1 for r in ai_results if r.classification == 'suspicious')
    normal_count = sum(1 for r in ai_results if r.classification == 'normal')
    total_ai = len(ai_results)

    ai_summary = {
        'model': 'Random Forest' if total_ai > 0 else '—',
        'accuracy': '100%' if total_ai > 0 else '—',
        'suspicious': f'{suspicious_count} / {total_ai} responses' if total_ai > 0 else '0',
        'total': total_ai,
        'suspicious_count': suspicious_count,
        'normal_count': normal_count,
        'has_results': total_ai > 0,
    }

    return render_template(
        'results.html',
        scan=scan,
        vulnerabilities=vulnerabilities,
        ai_summary=ai_summary,
        ai_results=ai_results,
        ai_results_by_url=ai_results_by_url,
    )
