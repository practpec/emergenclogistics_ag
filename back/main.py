#!/usr/bin/env python3
"""
API backend para EmergenLogistics
Sistema de distribución de ayuda humanitaria - Solo API REST
"""

import os
import sys
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes import register_blueprints
from utils.logger import setup_logger

def validate_database():
    """Validar que la base de datos de localidades existe"""
    from utils.config_manager import config_manager
    
    db_path = config_manager.get_database_path()
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Base de datos no encontrada: {db_path}")
        return False
    
    try:
        from services.data.database_service import DatabaseService
        db_service = DatabaseService(db_path)
        estados = db_service.get_estados()
        
        if len(estados) == 0:
            print("[ERROR] La base de datos no contiene estados")
            return False
            
        print(f"[INFO] Base de datos validada: {len(estados)} estados disponibles")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error validando base de datos: {e}")
        return False

def setup_directories():
    """Crear directorios necesarios si no existen"""
    directories = ['logs', 'data']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[INFO] Directorio creado: {directory}")

def create_app():
    """Factory pattern para crear la aplicación Flask API"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configurar CORS para permitir requests desde React
    CORS(app, origins=Config.CORS_ORIGINS)
    
    # Configurar logging
    setup_logger(app)
    
    # Registrar blueprints de API
    register_blueprints(app)
    
    return app

def main():
    """Función principal de la API"""
    
    print("=" * 60)
    print("EmergenLogistics API - Backend para React Frontend")
    print("Versión 2.0 - API REST con datos reales de INEGI")
    print("=" * 60)
    
    # Configurar directorios
    setup_directories()
    
    # Validar base de datos antes de iniciar
    if not validate_database():
        print("\n[CRITICAL] No se puede iniciar sin la base de datos de localidades")
        sys.exit(1)
    
    # Crear aplicación API
    try:
        app = create_app()
    except Exception as e:
        print(f"[ERROR] Error creando aplicación: {e}")
        sys.exit(1)
    
    # Información de inicio
    app.logger.info("=" * 50)
    app.logger.info("EmergenLogistics API - Sistema con Datos Reales INEGI")
    app.logger.info("=" * 50)
    app.logger.info(f"Modo DEBUG: {app.config['DEBUG']}")
    app.logger.info(f"Host: {app.config['HOST']}")
    app.logger.info(f"Puerto: {app.config['PORT']}")
    app.logger.info(f"CORS habilitado para React frontend")
    app.logger.info("API iniciada correctamente")
    app.logger.info("=" * 50)
    
    try:
        # Ejecutar aplicación
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        app.logger.info("API detenida por el usuario")
    except Exception as e:
        app.logger.error(f"Error ejecutando API: {e}")
        raise

if __name__ == "__main__":
    main()