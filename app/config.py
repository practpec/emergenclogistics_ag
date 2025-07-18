import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'emergencia_logistics_2025_dev')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # APIs externas
    OSRM_BASE_URL = os.getenv('OSRM_BASE_URL', 'http://router.project-osrm.org')
    
    # Límites del sistema
    MAX_DESTINATIONS = int(os.getenv('MAX_DESTINATIONS', 15))
    MAX_VEHICLES = int(os.getenv('MAX_VEHICLES', 10))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
    
    # Cache
    CACHE_MAX_AGE = int(os.getenv('CACHE_MAX_AGE', 300))
    CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 100))