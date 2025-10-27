from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: str = "development") -> Flask:
    from config import config_by_name

    # Point Flask to top-level templates/static if they are outside the package
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models for migrations
    from . import models  # noqa: F401

    # Ensure DB is initialized at startup
    try:
        with app.app_context():
            db.create_all()
        app.db_initialized = True
    except Exception:
        app.db_initialized = False

    # Register blueprints
    from .views import bp as main_bp
    app.register_blueprint(main_bp)

    # Start serial reader thread once on first request and ensure DB is initialized
    app.serial_thread_started = False

    @app.before_request
    def _ensure_serial_thread_started():
        # Ensure DB exists before anything else
        if not app.db_initialized:
            try:
                with app.app_context():
                    db.create_all()
                app.db_initialized = True
            except Exception:
                pass

        if not app.serial_thread_started and app.db_initialized:
            try:
                from .serial_reader import SerialReaderThread
                t = SerialReaderThread(app)
                t.start()
                app.serial_thread_started = True
            except Exception:
                # Fail silently; the app can still serve pages and mock may run
                pass

    return app


