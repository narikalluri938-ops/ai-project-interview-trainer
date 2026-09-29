import os
import logging
from flask import Flask, render_template
from .config import config_by_name
from .models import db
from .routes import main_bp, projects_bp, interview_bp, api_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def create_app(config_name: str = "default") -> Flask:
    """Application factory for AI Project Interview Trainer."""
    app = Flask(__name__)
    
    # Load configuration
    config_obj = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_obj)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(api_bp)

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # Create tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables initialized successfully.")

    return app
