#!/usr/bin/env python3
"""
Punto de entrada principal para EmergenLogistics
Sistema inteligente de distribución de ayuda humanitaria con datos reales de INEGI
"""

import os
import sys
from app import create_app
from app.config import Config

def validate_database():
    """Validar que la base de datos de localidades existe"""
    from utils.config_manager import config_manager
    
    db_path = config_manager.get_database_path()
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Base de datos no encontrada: {db_path}")
        print("Por favor, asegúrate de que el archivo localidades.db esté en la carpeta 'data/'")
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
    directories = [
        'logs',
        'data',
        'static/templates/cache'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[INFO] Directorio creado: {directory}")

def main():
    """Función principal de la aplicación"""
    
    print("=" * 60)
    print("EmergenLogistics - Sistema de Distribución de Ayuda Humanitaria")
    print("Versión 2.0 - Con datos reales de INEGI")
    print("=" * 60)
    
    # Configurar directorios
    setup_directories()
    
    # Validar base de datos antes de iniciar
    if not validate_database():
        print("\n[CRITICAL] No se puede iniciar sin la base de datos de localidades")
        print("Instrucciones:")
        print("1. Descarga la base de datos de localidades mexicanas")
        print("2. Colócala en: data/localidades.db")
        print("3. Asegúrate de que tenga la tabla 'localidades' con las columnas requeridas")
        sys.exit(1)
    
    # Crear aplicación usando factory pattern
    try:
        app = create_app()
    except Exception as e:
        print(f"[ERROR] Error creando aplicación: {e}")
        sys.exit(1)
    
    # Información de inicio
    app.logger.info("=" * 50)
    app.logger.info("EmergenLogistics - Sistema con Datos Reales INEGI")
    app.logger.info("=" * 50)
    app.logger.info(f"Modo DEBUG: {app.config['DEBUG']}")
    app.logger.info(f"Host: {app.config['HOST']}")
    app.logger.info(f"Puerto: {app.config['PORT']}")
    app.logger.info(f"Base de datos: Localidades mexicanas (INEGI)")
    app.logger.info(f"Usando datos reales: SÍ")
    app.logger.info("Sistema iniciado correctamente")
    app.logger.info("=" * 50)
    
    try:
        # Ejecutar aplicación
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        app.logger.info("Aplicación detenida por el usuario")
    except Exception as e:
        app.logger.error(f"Error ejecutando aplicación: {e}")
        raise

if __name__ == "__main__":
    main()