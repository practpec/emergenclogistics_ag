import os
from flask import Flask
from .config import Config
from .routes import register_blueprints
from utils.logger import setup_logger

def create_app():
    """Factory pattern para crear la aplicación Flask"""
    # Obtener la ruta absoluta del directorio raíz del proyecto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Configurar rutas de templates y static
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    # Crear la aplicación con las rutas correctas
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    app.config.from_object(Config)
    
    # Verificar que las carpetas existan
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
        app.logger.warning(f"Carpeta de templates creada: {template_dir}")
    
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        app.logger.warning(f"Carpeta static creada: {static_dir}")
    
    # Configurar logging
    setup_logger(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Log de depuración
    app.logger.info(f"Template folder: {app.template_folder}")
    app.logger.info(f"Static folder: {app.static_folder}")
    
    return app