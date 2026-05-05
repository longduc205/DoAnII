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

    # Build AI summary
    # TODO: Populate via AIAnalyzer once model is trained (Phase 4)
    suspicious_count = sum(1 for r in ai_results if r.classification == 'suspicious')
    ai_summary = {
        'model': 'RandomForest',
        'accuracy': '—',
        'suspicious': f'{suspicious_count} / {len(ai_results)} responses',
        'total': len(ai_results),
        'suspicious_count': suspicious_count,
    }

    return render_template(
        'results.html',
        scan=scan,
        vulnerabilities=vulnerabilities,
        ai_summary=ai_summary,
    )
