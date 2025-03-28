import os
from urllib.parse import urlparse, quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Original database URL
    DATABASE_URL = 'postgresql://chessnotessss_user:6uLDqOzeWg6E72GIfiSPu4K34E8BCF9P@dpg-cvhscbtrie7s73ea5pjg-a.oregon-postgres.render.com/chessnotessss'
    
    # Parse the database URL with SSL parameters for Render
    SQLALCHEMY_DATABASE_URI = f"{DATABASE_URL}?sslmode=require"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'connect_args': {
            'sslmode': 'require'
        }
    }
    
    # Redis configuration with fallback
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', "200 per day")
    
    # Google API Key
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # Flask environment
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')