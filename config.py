
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database Configuration - Railway PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # If DATABASE_URL is not set, try to build it from individual components
    if not DATABASE_URL:
        postgres_host = os.environ.get('POSTGRES_HOST', 'postgres.railway.internal')
        postgres_port = os.environ.get('POSTGRES_PORT', '5432')
        postgres_db = os.environ.get('POSTGRES_DB', 'railway')
        postgres_user = os.environ.get('POSTGRES_USER', 'postgres')
        postgres_password = os.environ.get('POSTGRES_PASSWORD', 'OTtJCXtjFmwTdYEBuEwXkMELBxTArGWT')
        postgres_sslmode = os.environ.get('POSTGRES_SSLMODE', 'require')
        
        if all([postgres_host, postgres_db, postgres_user, postgres_password]):
            DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}?sslmode={postgres_sslmode}"
        else:
            # No fallback - PostgreSQL is required
            raise ValueError("PostgreSQL database configuration is required. Please set DATABASE_URL or individual POSTGRES_* environment variables.")
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Enhanced PostgreSQL connection options for Railway
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30')),
        'echo': os.environ.get('DB_ECHO', 'False').lower() in ['true', '1', 'yes'],
    }
    
    # Railway-specific database settings
    RAILWAY_POSTGRES_SSL_MODE = os.environ.get('RAILWAY_POSTGRES_SSL_MODE', 'require')
    RAILWAY_POSTGRES_CONNECTION_TIMEOUT = int(os.environ.get('RAILWAY_POSTGRES_CONNECTION_TIMEOUT', '30'))
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # AI Service Configuration
    AI_SIMILARITY_THRESHOLD = float(os.environ.get('AI_SIMILARITY_THRESHOLD', '0.3'))
    AI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', '500'))
    AI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', '0.7'))
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')  # Default to production for Railway
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # Railway deployment specific settings
    RAILWAY_DEPLOYMENT = os.environ.get('RAILWAY_DEPLOYMENT', 'False').lower() in ['true', '1', 'yes']
    RAILWAY_APP_SERVICE = os.environ.get('RAILWAY_APP_SERVICE', 'False').lower() in ['true', '1', 'yes']