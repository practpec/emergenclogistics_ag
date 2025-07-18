"""
Registro centralizado de rutas
"""
from flask import Flask
from .maps_routes import maps_bp
from .ag_routes import ag_bp
from .api_routes import api_bp

def register_routes(app: Flask):
    """Registrar todos los blueprints"""
    
    # Rutas principales
    app.register_blueprint(maps_bp)
    app.register_blueprint(ag_bp)
    
    # API
    app.register_blueprint(api_bp, url_prefix='/api')