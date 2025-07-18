"""
Configuración de la aplicación
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'emergencia_logistics_2025')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Paths
    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'
    
    # Entities
    ENTITIES_PATH = os.path.join(os.path.dirname(__file__), '..', 'entities', 'data')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # External APIs
    OSRM_BASE_URL = "http://router.project-osrm.org"
    
    # Limits
    MAX_DESTINATIONS = 15
    MAX_VEHICLES = 10
    REQUEST_TIMEOUT = 30