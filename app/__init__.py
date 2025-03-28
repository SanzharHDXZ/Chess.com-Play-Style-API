from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS 
from flask_migrate import Migrate
from config import Config
import logging
import redis
import os

db = SQLAlchemy()
migrate = Migrate()

# Create Redis client
redis_client = redis.from_url(Config.CACHE_REDIS_URL) if Config.CACHE_REDIS_URL else None

# Configure limiter with fallback to in-memory storage
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=Config.CACHE_REDIS_URL if redis_client else None,
    default_limits=["200 per day"]
)

cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Logging configuration
    logging.basicConfig(level=logging.INFO)
    
    # Comprehensive CORS configuration
    CORS(app, 
         resources={r"/*": {
             "origins": ["https://chess-com-play-style-api.onrender.com", "http://localhost:5000", "*"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": [
                 "Content-Type", 
                 "Authorization", 
                 "Access-Control-Allow-Credentials", 
                 "X-API-Key"
             ]
         }},
         supports_credentials=True
    )

    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; img-src 'self' data:"
        return response

    # Global OPTIONS handler
    @app.route('/options', methods=['OPTIONS'])
    def options_handler():
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-API-Key, Authorization')
        return response

    # Error handler
    @app.errorhandler(Exception)
    def handle_error(e):
        app.logger.error(f"Unhandled Exception: {str(e)}")
        return jsonify(error=str(e)), 500

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    cache.init_app(app)

    # Create tables (optional, but can be useful)
    with app.app_context():
        db.create_all()
        migrate.init_app(app, db)

    # Swagger UI configuration
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Chess.com Play Style API",
            'validatorUrl': None  # Disable validator
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    from app.routes import auth, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)

    return app