import os
from typing import Dict, Any

class ConfigManager:
    """Gestor de configuración centralizado con soporte para base de datos"""
    
    def __init__(self):
        self._config = {}
        self._load_default_config()
    
    def _load_default_config(self):
        """Cargar configuración por defecto con base de datos"""
        self._config = {
            'system': {
                'max_destinations': int(os.getenv('MAX_DESTINATIONS', 15)),
                'max_vehicles': int(os.getenv('MAX_VEHICLES', 10)),
                'request_timeout': int(os.getenv('REQUEST_TIMEOUT', 30)),
                'using_real_data': True
            },
            'database': {
                'path': os.getenv('DATABASE_PATH', 'data/localidades.db'),
                'type': 'sqlite',
                'source': 'inegi_localidades',
                'min_population': int(os.getenv('MIN_POPULATION', 20)),
                'search_min_length': int(os.getenv('SEARCH_MIN_LENGTH', 2))
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
                'max_radius_km': 200,
                'min_radius_km': 10,
                'mexico_bounds': {
                    'lat_min': 14.5,
                    'lat_max': 32.7,
                    'lng_min': -118.4,
                    'lng_max': -86.7
                },
                'coordinate_precision': 4,
                'use_real_coordinates': True
            },
            'api': {
                'max_search_results': int(os.getenv('MAX_SEARCH_RESULTS', 50)),
                'search_timeout': int(os.getenv('SEARCH_TIMEOUT', 5))
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
    
    def get_database_config(self) -> Dict[str, Any]:
        """Obtener configuración específica de base de datos"""
        return self.get('database', default={})
    
    def get_geo_config(self) -> Dict[str, Any]:
        """Obtener configuración geográfica"""
        return self.get('geo', default={})
    
    def get_api_limits(self) -> Dict[str, int]:
        """Obtener límites de API"""
        return {
            'max_destinations': self.get('system', 'max_destinations'),
            'max_vehicles': self.get('system', 'max_vehicles'),
            'max_search_results': self.get('api', 'max_search_results'),
            'min_population': self.get('database', 'min_population')
        }
    
    def validate_config(self) -> bool:
        """Validar configuración actual"""
        try:
            # Validaciones básicas del sistema
            assert self.get('system', 'max_destinations') > 0
            assert self.get('system', 'max_vehicles') > 0
            assert self.get('system', 'request_timeout') > 0
            
            # Validaciones de base de datos
            assert self.get('database', 'path') is not None
            assert self.get('database', 'min_population') >= 0
            assert self.get('database', 'search_min_length') > 0
            
            # Validaciones de OSRM
            assert self.get('osrm', 'base_url') is not None
            assert self.get('osrm', 'timeout') > 0
            
            # Validaciones de cache
            assert self.get('cache', 'max_size') > 0
            
            # Validaciones geográficas
            geo_config = self.get_geo_config()
            assert geo_config['mexico_bounds']['lat_min'] < geo_config['mexico_bounds']['lat_max']
            assert geo_config['mexico_bounds']['lng_min'] < geo_config['mexico_bounds']['lng_max']
            
            return True
        except (AssertionError, TypeError, KeyError):
            return False
    
    def is_using_real_data(self) -> bool:
        """Verificar si se están usando datos reales"""
        return self.get('system', 'using_real_data', True)
    
    def get_database_path(self) -> str:
        """Obtener ruta de la base de datos"""
        return self.get('database', 'path', 'data/localidades.db')

# Instancia global del gestor de configuración
config_manager = ConfigManager()