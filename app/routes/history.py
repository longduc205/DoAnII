"""
History routes - Scan history management
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user

from app import db
from app.models.scan import Scan

history_bp = Blueprint('history', __name__)


@history_bp.route('/')
@login_required
def scan_history():
    """Display past scan sessions with pagination and filtering."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    status = request.args.get('status', 'all')
    per_page = 10

    query = Scan.query.filter(Scan.user_id == current_user.id)

    if status != 'all':
        query = query.filter(Scan.status == status)
    
    if q:
        # Search by ID or URL
        if q.isdigit():
            query = query.filter((Scan.id == int(q)) | (Scan.target_url.contains(q)))
        else:
            query = query.filter(Scan.target_url.contains(q))

    pagination = query.order_by(Scan.started_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Global stats for the header
    total_findings = (
        db.session.query(db.func.sum(Scan.total_vulnerabilities))
        .filter(Scan.user_id == current_user.id)
        .scalar()
        or 0
    )
    total_completed = Scan.query.filter(
        Scan.user_id == current_user.id,
        Scan.status == 'completed'
    ).count()
    
    return render_template('history.html', 
                           pagination=pagination, 
                           q=q, 
                           status=status,
                           total_findings=total_findings,
                           total_completed=total_completed)


@history_bp.route('/<int:scan_id>', methods=['DELETE'])
@login_required
def delete_scan(scan_id):
    """Delete a scan and all its related data (cascade)."""
    scan = Scan.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    db.session.delete(scan)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Scan #{scan_id} deleted'})
