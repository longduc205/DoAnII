"""
History routes - Scan history management
"""

from flask import Blueprint, render_template, jsonify

from app import db
from app.models.scan import Scan

history_bp = Blueprint('history', __name__)


@history_bp.route('/')
def scan_history():
    """Display all past scan sessions."""
    scans = Scan.query.order_by(Scan.started_at.desc()).all()
    return render_template('history.html', scans=scans)


@history_bp.route('/<int:scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    """Delete a scan and all its related data (cascade)."""
    scan = Scan.query.get_or_404(scan_id)
    db.session.delete(scan)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Scan #{scan_id} deleted'})
