"""
Scan Session Model
"""

from datetime import datetime, timezone
from app import db


class Scan(db.Model):
    """Represents a vulnerability scan session."""
    __tablename__ = 'scans'

    id = db.Column(db.Integer, primary_key=True)
    target_url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    total_pages = db.Column(db.Integer, default=0)
    total_forms = db.Column(db.Integer, default=0)
    total_vulnerabilities = db.Column(db.Integer, default=0)

    # Relationships
    pages = db.relationship('Page', backref='scan', lazy=True, cascade='all, delete-orphan')
    vulnerabilities = db.relationship('Vulnerability', backref='scan', lazy=True, cascade='all, delete-orphan')
    ai_results = db.relationship('AIResult', backref='scan', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Scan {self.id} - {self.target_url}>'
