import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///chess_api.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', "100 per day")
    
    # Redis configuration
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))
    
    # Google API Key
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # Flask environment
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')