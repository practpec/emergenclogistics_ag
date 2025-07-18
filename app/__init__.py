"""
Factory de aplicación Flask
"""
from flask import Flask
from app.config import Config
from app.routes import register_routes
from utils.logger import get_logger

def create_app():
    """Crear y configurar aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object(Config)
    
    # Registrar rutas
    register_routes(app)
    
    # Logger
    logger = get_logger(__name__)
    logger.info("Aplicación Flask creada exitosamente")
    
    return app