"""
AI Web Vulnerability Scanner - Flask Application Factory
"""

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


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
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.scan import scan_bp
    from app.routes.results import results_bp
    from app.routes.history import history_bp
    from app.routes.tasks import tasks_bp
    from app.routes.auth import auth_bp
    from app.routes.ai_chat import ai_chat_bp
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(scan_bp, url_prefix='/scan')
    app.register_blueprint(results_bp, url_prefix='/results')
    app.register_blueprint(history_bp, url_prefix='/history')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(ai_chat_bp, url_prefix='/ai')

    # Global template context: AI status, used by sidebar.
    @app.context_processor
    def inject_globals():
        api_key = app.config.get('BLACKBOX_API_KEY')
        # We consider AI ready if we have a key (or if it starts with 'sk-')
        is_ready = bool(api_key and len(api_key) > 10)
        return {
            'ai_ready': is_ready,
            'ai_model_name': 'Blackbox (DeepSeek-V3)' if is_ready else 'No AI Key'
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
