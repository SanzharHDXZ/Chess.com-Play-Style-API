from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from config import Config
import os

db = SQLAlchemy()

# Используем Internal Redis URL от Render
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")  # Теперь берёт URL из Render

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://red-cvht2r9c1ekc738fd1sg:6379/0"
)
cache = Cache(config={"CACHE_TYPE": "redis", "CACHE_REDIS_URL": REDIS_URL})  # <-- Кэш теперь тоже использует Redis

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS для локальной разработки и Render
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:4200",
                "https://chess-com-play-style-api.onrender.com"  # <-- Добавлено
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'  # Вместо полного URL
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Chess.com Play Style API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # Регистрация маршрутов
    from app.routes import auth, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)

    return app

app = create_app()
