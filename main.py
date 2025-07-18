#!/usr/bin/env python3
"""
Punto de entrada principal de EmergenLogistics
Sistema de distribución de ayuda humanitaria
"""
import os
from app import create_app
from utils.logger import setup_logger

def main():
    # Configurar logging
    logger = setup_logger()
    logger.info("Iniciando EmergenLogistics")
    
    # Crear aplicación
    app = create_app()
    
    # Configuración del servidor
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    try:
        logger.info(f"Servidor iniciado en http://{host}:{port}")
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Aplicación detenida por el usuario")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()