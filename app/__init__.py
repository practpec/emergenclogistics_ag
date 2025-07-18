from flask import Flask
from .config import Config
from .routes import register_blueprints
from utils.logger import setup_logger

def create_app():
    """Factory pattern para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configurar logging
    setup_logger(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    return app