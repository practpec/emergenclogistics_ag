#!/usr/bin/env python3
"""
API backend para EmergenLogistics
Sistema de distribución de ayuda humanitaria
"""

import os
import sys
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes import register_blueprints

def validate_database():
    """Validar que la base de datos existe"""
    db_path = Config.DATABASE_PATH
    
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

def create_app():
    """Factory pattern para crear la aplicación Flask API"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, origins=Config.CORS_ORIGINS)
    
    register_blueprints(app)
    
    return app

def main():
    """Función principal de la API"""
    
    print("=" * 50)
    print("EmergenLogistics API - Backend")
    print("=" * 50)
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    if not validate_database():
        print("\n[CRITICAL] No se puede iniciar sin la base de datos")
        sys.exit(1)
    
    try:
        app = create_app()
    except Exception as e:
        print(f"[ERROR] Error creando aplicación: {e}")
        sys.exit(1)
    
    app.logger.info("API iniciada correctamente")
    
    try:
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