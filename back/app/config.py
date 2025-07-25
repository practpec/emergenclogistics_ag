import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'emergencia_logistics_2025_api')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Base de datos
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/localidades.db')
    
    # OSRM
    OSRM_BASE_URL = os.getenv('OSRM_BASE_URL', 'http://router.project-osrm.org')
    
    # CORS para desarrollo React
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173"
    ]