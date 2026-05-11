"""
AI Remediation Result Model

Stores AI-generated remediation advice for each vulnerability finding.
Replaces the old classification-based model (normal/suspicious).
"""

from datetime import datetime, timezone
from app import db


class AIResult(db.Model):
    """Represents an AI-generated remediation for a vulnerability."""
    __tablename__ = 'ai_results'

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    vulnerability_id = db.Column(
        db.Integer, db.ForeignKey('vulnerabilities.id'), nullable=True
    )
    url = db.Column(db.String(500), nullable=False)

    # AI-generated remediation content
    explanation = db.Column(db.Text)       # What this vulnerability is
    impact = db.Column(db.Text)            # What damage it can cause
    remediation = db.Column(db.Text)       # JSON array of fix steps
    code_example = db.Column(db.Text)      # Example fix code snippet

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationship
    vulnerability = db.relationship(
        'Vulnerability', backref=db.backref('ai_remediation', uselist=False)
    )

    def get_remediation_steps(self):
        """Parse remediation JSON into a Python list."""
        import json
        if not self.remediation:
            return []
        try:
            return json.loads(self.remediation)
        except (json.JSONDecodeError, TypeError):
            return [self.remediation]

    def __repr__(self):
        return f'<AIResult remediation for vuln #{self.vulnerability_id}>'
