"""
Chat Message Model

Stores interactive conversation between the user and AI for a specific vulnerability.
"""

from datetime import datetime, timezone
from app import db


class ChatMessage(db.Model):
    """Represents a single message in an AI Q&A session."""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    vulnerability_id = db.Column(
        db.Integer, db.ForeignKey('vulnerabilities.id'), nullable=False
    )
    role = db.Column(db.String(20), nullable=False) # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Relationship
    vulnerability = db.relationship(
        'Vulnerability', backref=db.backref('chat_history', lazy=True, order_by='ChatMessage.created_at')
    )

    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<ChatMessage {self.role} for vuln #{self.vulnerability_id}>'
