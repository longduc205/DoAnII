"""
Results routes - Display scan results
"""

from flask import Blueprint, render_template

results_bp = Blueprint('results', __name__)


@results_bp.route('/<int:scan_id>')
def show_results(scan_id):
    """Display results for a specific scan session."""
    # TODO: Query database for scan results
    return render_template('results.html', scan_id=scan_id)
