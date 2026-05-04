"""
Scan routes - Scan initiation and management
"""

import logging

from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from app.models.scan import Scan
from app.services.scanner import ScannerEngine

logger = logging.getLogger(__name__)

scan_bp = Blueprint('scan', __name__)


@scan_bp.route('/new', methods=['GET', 'POST'])
def new_scan():
    """Initiate a new vulnerability scan."""
    if request.method == 'POST':
        target_url = request.form.get('target_url', '').strip()
        if not target_url:
            return render_template('scan.html', error='URL is required')

        scan_config = {
            'crawl_depth': int(request.form.get('crawl_depth', 2)),
            'test_sqli': request.form.get('test_sqli') == 'on',
            'test_xss': request.form.get('test_xss') == 'on',
            'use_ai': request.form.get('use_ai') == 'on',
        }

        try:
            engine = ScannerEngine(target_url, scan_config)
            scan = engine.run()
            return redirect(url_for('results.show_results', scan_id=scan.id))
        except Exception as exc:
            logger.error("Scan failed: %s", exc)
            return render_template('scan.html', error=f'Scan failed: {exc}')

    return render_template('scan.html')


@scan_bp.route('/status/<int:scan_id>')
def scan_status(scan_id):
    """Check the status of an ongoing scan."""
    scan = Scan.query.get_or_404(scan_id)
    return jsonify({
        'status': scan.status,
        'scan_id': scan.id,
        'total_pages': scan.total_pages,
        'total_forms': scan.total_forms,
    })
