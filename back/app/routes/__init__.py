from flask import Flask
from .api_routes import api_bp
from .maps_routes import maps_bp
from .scenario_routes import scenario_bp

def register_blueprints(app: Flask) -> None:
    """Registrar todos los blueprints de la API"""
    
    # API general routes
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Maps/Geo routes - CORREGIDO: usar /api/maps en lugar de /api/maps
    app.register_blueprint(maps_bp, url_prefix='/api')

    # Scenario data routes
    app.register_blueprint(scenario_bp, url_prefix='/api/scenario')
    
    
    # Log de rutas registradas
    app.logger.info("Blueprints registrados:")
    app.logger.info("- API general: /api/*")
    app.logger.info("- Maps: /api/estados, /api/municipios, /api/maps/*")
    app.logger.info("- Scenario: /api/scenario/*")
  