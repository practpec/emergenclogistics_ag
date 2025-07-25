import os
import logging
from flask import Flask
from .config import Config
from .routes import register_blueprints

def create_app():
    """Factory pattern para crear la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
    )
    
    # Registrar blueprints
    register_blueprints(app)
    
    return app