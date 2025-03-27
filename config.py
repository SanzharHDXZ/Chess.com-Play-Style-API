import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///chess_api.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis configuration with fallback
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', "100 per day")
    
    # Google API Key
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # Flask environment
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')