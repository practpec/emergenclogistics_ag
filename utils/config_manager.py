import os
from typing import Dict, Any

class ConfigManager:
    """Gestor de configuración centralizado"""
    
    def __init__(self):
        self._config = {}
        self._load_default_config()
    
    def _load_default_config(self):
        """Cargar configuración por defecto"""
        self._config = {
            'system': {
                'max_destinations': int(os.getenv('MAX_DESTINATIONS', 15)),
                'max_vehicles': int(os.getenv('MAX_VEHICLES', 10)),
                'request_timeout': int(os.getenv('REQUEST_TIMEOUT', 30))
            },
            'osrm': {
                'base_url': os.getenv('OSRM_BASE_URL', 'http://router.project-osrm.org'),
                'timeout': 8,
                'delay_between_requests': 0.3
            },
            'cache': {
                'max_age': int(os.getenv('CACHE_MAX_AGE', 300)),
                'max_size': int(os.getenv('CACHE_MAX_SIZE', 100))
            },
            'geo': {
                'max_radius_km': 100,
                'min_radius_km': 10,
                'mexico_bounds': {
                    'lat_min': 14.5,
                    'lat_max': 32.7,
                    'lng_min': -118.4,
                    'lng_max': -86.7
                }
            }
        }
    
    def get(self, section: str, key: str = None, default=None) -> Any:
        """Obtener valor de configuración"""
        if key is None:
            return self._config.get(section, default)
        
        section_config = self._config.get(section, {})
        return section_config.get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Establecer valor de configuración"""
        if section not in self._config:
            self._config[section] = {}
        
        self._config[section][key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Obtener toda la configuración"""
        return self._config.copy()
    
    def validate_config(self) -> bool:
        """Validar configuración actual"""
        try:
            # Validaciones básicas
            assert self.get('system', 'max_destinations') > 0
            assert self.get('system', 'max_vehicles') > 0
            assert self.get('system', 'request_timeout') > 0
            assert self.get('osrm', 'base_url') is not None
            assert self.get('cache', 'max_size') > 0
            
            return True
        except (AssertionError, TypeError):
            return False

# Instancia global del gestor de configuración
config_manager = ConfigManager()