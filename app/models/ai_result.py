"""
AI Classification Result Model
"""

from datetime import datetime, timezone
from app import db


class AIResult(db.Model):
    """Represents an AI classification result for a response."""
    __tablename__ = 'ai_results'

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    classification = db.Column(db.String(20))  # normal, suspicious
    confidence = db.Column(db.Float)
    response_length = db.Column(db.Integer)
    status_code = db.Column(db.Integer)
    has_reflection = db.Column(db.Boolean, default=False)
    has_error_keywords = db.Column(db.Boolean, default=False)
    classified_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<AIResult {self.classification} ({self.confidence:.2f}) for {self.url}>'
