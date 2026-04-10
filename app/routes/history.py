"""
History routes - Scan history management
"""

from flask import Blueprint, render_template

history_bp = Blueprint('history', __name__)


@history_bp.route('/')
def scan_history():
    """Display all past scan sessions."""
    # TODO: Query database for scan history
    return render_template('history.html')
