"""
Discovered Page Model
"""

from app import db


class Page(db.Model):
    """Represents a discovered page during crawling."""
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    status_code = db.Column(db.Integer)
    depth = db.Column(db.Integer, default=0)
    has_forms = db.Column(db.Boolean, default=False)
    form_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Page {self.url}>'
