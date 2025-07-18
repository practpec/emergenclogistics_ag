"""
Factory de aplicación Flask
"""
import os
from flask import Flask
from app.config import Config
from app.routes import register_routes
from utils.logger import get_logger

def create_app():
    """Crear y configurar aplicación Flask"""
    
    # Determinar la ruta base del proyecto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    
    # Verificar que los directorios existan
    if not os.path.exists(template_dir):
        print(f"ADVERTENCIA: Directorio de templates no existe: {template_dir}")
        os.makedirs(template_dir, exist_ok=True)
    
    if not os.path.exists(static_dir):
        print(f"ADVERTENCIA: Directorio de static no existe: {static_dir}")
        os.makedirs(static_dir, exist_ok=True)
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configuración
    app.config.from_object(Config)
    
    # Registrar rutas
    register_routes(app)
    
    # Logger
    logger = get_logger(__name__)
    logger.info("Aplicación Flask creada exitosamente")
    logger.info(f"Template folder: {app.template_folder}")
    logger.info(f"Static folder: {app.static_folder}")
    logger.info(f"Template dir exists: {os.path.exists(template_dir)}")
    logger.info(f"Static dir exists: {os.path.exists(static_dir)}")
    
    return app