from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.storage import RedisStorage
from flask_caching import Cache
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS 
from config import Config
import logging
import redis

db = SQLAlchemy()
# Configure Redis storage for rate limiter
redis_client = redis.from_url(Config.CACHE_REDIS_URL)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=Config.CACHE_REDIS_URL,
    storage_func=lambda: RedisStorage(redis_client)
)
cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Logging configuration
    logging.basicConfig(level=logging.INFO)
    
    # Comprehensive error handler
    @app.errorhandler(Exception)
    def handle_error(e):
        app.logger.error(f"Unhandled Exception: {str(e)}")
        return jsonify(error=str(e)), 500

    # CORS configuration with more specific settings
    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}}, supports_credentials=True)

    # Allow OPTIONS method globally
    @app.route('/options', methods=['OPTIONS'])
    def options_handler():
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        return response

    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Chess.com Play Style API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    from app.routes import auth, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)

    return app