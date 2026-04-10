"""
Main routes - Home page
"""

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render the home page with URL input form."""
    return render_template('index.html')
