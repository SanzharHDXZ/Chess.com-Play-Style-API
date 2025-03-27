from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS 
from config import Config
from flask import request, make_response

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()

def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,X-API-Key")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    return response

def create_app():
    app = Flask(__name__)
    
    # Apply CORS middleware
    app.after_request(add_cors_headers)

    # Enable CORS for all routes and allow all origins
    CORS(app, 
     resources={r"/*": {"origins": "*"}}, 
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=[
                      "Content-Type", 
             "Authorization", 
             "Access-Control-Allow-Credentials",
             "X-API-Key"
     ]
)

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