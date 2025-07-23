from flask import Flask
from .api_routes import api_bp
from .maps_routes import maps_bp
from .ag_routes import ag_bp

def register_blueprints(app: Flask) -> None:
    """Registrar todos los blueprints de la API"""
    
    # API general routes
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Maps/Geo routes
    app.register_blueprint(maps_bp, url_prefix='/api/maps')
    
    # Genetic Algorithm routes
    app.register_blueprint(ag_bp, url_prefix='/api/ag')
    
    app.logger.info("API Blueprints registrados correctamente")