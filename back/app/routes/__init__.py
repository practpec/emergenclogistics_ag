from flask import Flask
from .maps_routes import maps_bp
from .scenario_routes import scenario_bp
from .ag_routes import ag_bp

def register_blueprints(app: Flask) -> None:
    """Registrar blueprints de la API"""
    
    app.register_blueprint(maps_bp, url_prefix='/api')
    app.register_blueprint(scenario_bp, url_prefix='/api/scenario')
    app.register_blueprint(ag_bp, url_prefix='/api/ag')
    
    app.logger.info("Blueprints registrados:")
    app.logger.info("- Maps: /api/estados, /api/municipios, /api/maps/*")
    app.logger.info("- Scenario: /api/scenario/*")
    app.logger.info("- Genetic Algorithm: /api/ag/*")