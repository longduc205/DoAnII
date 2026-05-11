"""
User model for authentication and ownership.
"""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    """Application user account."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    scans = db.relationship('Scan', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, raw_password):
        """Hash and store user password."""
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Validate raw password against stored hash."""
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f'<User {self.id} - {self.username}>'
