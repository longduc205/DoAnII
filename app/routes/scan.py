"""
Scan routes - Scan initiation and management
"""

import logging

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user

from app.models.scan import Scan
from app.services.scanner import ScannerEngine

logger = logging.getLogger(__name__)

scan_bp = Blueprint('scan', __name__)


def _get_last_scan(user_id):
    """Return the user's most recent completed or failed scan, or None on error."""
    try:
        return (
            Scan.query
            .filter(
                Scan.user_id == user_id,
                Scan.status.in_(['completed', 'failed'])
            )
            .order_by(Scan.completed_at.desc())
            .first()
        )
    except Exception as exc:
        logger.error("Failed to fetch last scan: %s", exc)
        return None


@scan_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_scan():
    """Initiate a new vulnerability scan."""
    if request.method == 'POST':
        target_url = request.form.get('target_url', '').strip()
        if not target_url:
            last_scan = _get_last_scan(current_user.id)
            return render_template('scan.html', error='URL is required', last_scan=last_scan)

        scan_config = {
            'crawl_depth': int(request.form.get('crawl_depth', 2)),
            'test_sqli': request.form.get('test_sqli') == 'on',
            'test_xss': request.form.get('test_xss') == 'on',
            'use_ai': request.form.get('use_ai') == 'on',
        }

        try:
            engine = ScannerEngine(target_url, scan_config, user_id=current_user.id)
            scan = engine.run()
            vuln_count = scan.total_vulnerabilities or 0
            vuln_word = 'vulnerability' if vuln_count == 1 else 'vulnerabilities'
            flash(
                f"Scanned {target_url} — {vuln_count} {vuln_word} found.",
                'scan_success'
            )
            return redirect(url_for('results.show_results', scan_id=scan.id))
        except Exception as exc:
            logger.error("Scan failed: %s", exc)
            flash(f"Scan failed for {target_url}: {exc}", 'scan_error')
            last_scan = _get_last_scan(current_user.id)
            return render_template('scan.html', error=f'Scan failed: {exc}', last_scan=last_scan)

    last_scan = _get_last_scan(current_user.id)
    return render_template('scan.html', last_scan=last_scan)


@scan_bp.route('/status/<int:scan_id>')
@login_required
def scan_status(scan_id):
    """Check the status of an ongoing scan."""
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'status': scan.status,
        'scan_id': scan.id,
        'total_pages': scan.total_pages,
        'total_forms': scan.total_forms,
    })
