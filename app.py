"""
Flask Application Entrypoint for AI Resume Analyzer.
Initializes the application using the factory pattern, registers blueprints,
configures CORS, and establishes global error handlers.
"""
import sys
import os

# Ensure backend root directory is in sys.path
_CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

import logging
from flask import Flask, jsonify
from flask_cors import CORS

try:
    from config import Config
    from database import init_db
    from routes import register_routes
except ImportError:
    from backend.config import Config
    from backend.database import init_db
    from backend.routes import register_routes

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ResumeAnalyzerApp")

def create_app(config_class=Config) -> Flask:
    """Application factory for Flask backend."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure max content length for uploads (5MB)
    app.config["MAX_CONTENT_LENGTH"] = config_class.MAX_FILE_SIZE_BYTES

    # Enable CORS for frontend clients
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize SQLite database schema
    init_db()

    # Register modular blueprints
    register_routes(app)

    # Register centralized error handlers
    register_error_handlers(app)

    return app

def register_error_handlers(app: Flask):
    """Centralized JSON error handling."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": getattr(error, 'description', str(error))
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": getattr(error, 'description', "The requested endpoint does not exist.")
        }), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        max_mb = round(Config.MAX_FILE_SIZE_BYTES / (1024 * 1024), 1)
        return jsonify({
            "error": "File Too Large",
            "message": f"Uploaded file exceeds maximum allowed limit of {max_mb}MB."
        }), 413

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "error": "Unprocessable Entity",
            "message": getattr(error, 'description', str(error))
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.exception("Internal server error caught:")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request."
        }), 500

# Create WSGI application instance
app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting AI Resume Analyzer backend on port {Config.PORT}...")
    logger.info(f"AI Engine Status: {'Google Gemini Live' if Config.is_ai_configured() else 'Transparent Rule Engine (Demo Active)'}")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
