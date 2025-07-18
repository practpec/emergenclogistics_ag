#!/usr/bin/env python3
"""
Punto de entrada principal para EmergenLogistics
Sistema inteligente de distribución de ayuda humanitaria
"""

from app import create_app
from app.config import Config

def main():
    """Función principal de la aplicación"""
    
    # Crear aplicación usando factory pattern
    app = create_app()
    
    # Información de inicio
    app.logger.info("=" * 50)
    app.logger.info("EmergenLogistics - Sistema de Distribución de Ayuda Humanitaria")
    app.logger.info("=" * 50)
    app.logger.info(f"Modo DEBUG: {app.config['DEBUG']}")
    app.logger.info(f"Host: {app.config['HOST']}")
    app.logger.info(f"Puerto: {app.config['PORT']}")
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