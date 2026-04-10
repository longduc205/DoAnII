"""
AI Web Vulnerability Scanner - Flask Application Factory
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='static'
    )

    # Load configuration
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.scan import scan_bp
    from app.routes.results import results_bp
    from app.routes.history import history_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(scan_bp, url_prefix='/scan')
    app.register_blueprint(results_bp, url_prefix='/results')
    app.register_blueprint(history_bp, url_prefix='/history')

    # Create database tables
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app
