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
    from app.routes.tasks import tasks_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(scan_bp, url_prefix='/scan')
    app.register_blueprint(results_bp, url_prefix='/results')
    app.register_blueprint(history_bp, url_prefix='/history')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')

    # Global template context: AI model availability, used by base.html sidebar.
    @app.context_processor
    def inject_globals():
        import os
        model_path = app.config.get('AI_MODEL_PATH', 'ai/models/classifier.pkl')
        return {
            'ai_ready': os.path.isfile(model_path),
        }

    # Create database tables (with auto-recovery on schema mismatch)
    with app.app_context():
        from app import models  # noqa: F401
        from app.models.scan import Scan as _Scan
        try:
            db.create_all()
            # Probe the actual DB columns against the ORM model to detect drift.
            from sqlalchemy import inspect as sa_inspect
            inspector = sa_inspect(db.engine)
            if inspector.has_table('scans'):
                db_cols = {col['name'] for col in inspector.get_columns('scans')}
                model_cols = {c.key for c in _Scan.__table__.columns}
                if db_cols != model_cols:
                    # Schema mismatch — drop all tables and recreate fresh.
                    db.drop_all()
                    db.create_all()
        except Exception:
            db.drop_all()
            db.create_all()

    return app
