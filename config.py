import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///chess_api.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATELIMIT_DEFAULT = "100 per day"
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
