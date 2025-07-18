"""
Sistema de logging centralizado
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger():
    """Configurar logger principal"""
    
    # Crear directorio de logs
    os.makedirs('logs', exist_ok=True)
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Logger raíz
    logger = logging.getLogger('emergenclogistics')
    logger.setLevel(logging.INFO)
    
    # Handler para archivo
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Handler para consola (solo errores críticos)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str):
    """Obtener logger para módulo específico"""
    return logging.getLogger(f'emergenclogistics.{name}')