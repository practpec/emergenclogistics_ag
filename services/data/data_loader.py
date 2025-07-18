"""
Servicio para cargar datos de entidades
"""
import os
from typing import Dict, List, Any
from utils.helpers import load_json_file
from utils.logger import get_logger
from core.exceptions import DataLoadError

class DataLoader:
    """Cargador centralizado de datos"""
    
    def __init__(self, entities_path: str):
        self.entities_path = entities_path
        self.logger = get_logger(__name__)
        self._cache = {}
    
    def load_all_entities(self) -> Dict[str, List[Any]]:
        """Cargar todas las entidades"""
        if 'all' in self._cache:
            return self._cache['all']
        
        entities = {
            'desastres': self.load_disasters(),
            'vehiculos': self.load_vehicles(),
            'categorias_insumos': self.load_supply_categories()
        }
        
        self._cache['all'] = entities
        self.logger.info("Entidades cargadas exitosamente")
        return entities
    
    def load_disasters(self) -> List[Dict[str, Any]]:
        """Cargar tipos de desastres"""
        return self._load_entity_file('desastres.json')
    
    def load_vehicles(self) -> List[Dict[str, Any]]:
        """Cargar tipos de vehículos"""
        return self._load_entity_file('vehiculos.json')
    
    def load_supply_categories(self) -> List[Dict[str, Any]]:
        """Cargar categorías de insumos"""
        return self._load_entity_file('categorias_insumos.json')
    
    def _load_entity_file(self, filename: str) -> List[Dict[str, Any]]:
        """Cargar archivo de entidad específico"""
        if filename in self._cache:
            return self._cache[filename]
        
        file_path = os.path.join(self.entities_path, filename)
        try:
            data = load_json_file(file_path)
            self._cache[filename] = data
            return data
        except Exception as e:
            self.logger.error(f"Error cargando {filename}: {e}")
            raise DataLoadError(f"No se pudo cargar {filename}")
    
    def clear_cache(self):
        """Limpiar cache de datos"""
        self._cache.clear()
        self.logger.info("Cache de datos limpiado")