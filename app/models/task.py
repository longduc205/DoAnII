"""
Task Model
"""

from datetime import datetime, timezone
from app import db


class Task(db.Model):
    """Represents a task from TASKS.md."""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    phase = db.Column(db.String(100), nullable=False)
    day = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, done
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Task {self.id} - {self.title[:30]}>'

    def to_dict(self):
        return {
            'id': self.id,
            'phase': self.phase,
            'day': self.day,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
