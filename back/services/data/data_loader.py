import json
import os
from typing import List, Dict, Any
from core.base_service import CacheableService
from core.exceptions import DataLoadError

class DataLoader(CacheableService):
    """Servicio para cargar datos estáticos desde archivos JSON"""
    
    def __init__(self):
        super().__init__()
        self.data_path = "entities/data"
    
    def _load_json_file(self, filename: str) -> List[Dict[str, Any]]:
        """Cargar archivo JSON de forma segura con cache"""
        cache_key = f"json_{filename}"
        cached_data = self.get_from_cache(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        try:
            file_path = os.path.join(self.data_path, filename)
            
            if not os.path.exists(file_path):
                raise DataLoadError(f"Archivo no encontrado: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            self.set_cache(cache_key, data)
            return data
            
        except json.JSONDecodeError as e:
            self.log_error(f"Error JSON en {filename}", e)
            raise DataLoadError(f"Error decodificando JSON: {filename}")
        except Exception as e:
            self.log_error(f"Error cargando {filename}", e)
            raise DataLoadError(f"Error cargando archivo: {filename}")
    
    def get_vehiculos(self) -> List[Dict[str, Any]]:
        """Obtener todos los vehículos"""
        try:
            return self._load_json_file("vehiculos.json")
        except Exception as e:
            self.log_error("Error obteniendo vehículos", e)
            raise
    
    def get_desastres(self) -> List[Dict[str, Any]]:
        """Obtener todos los tipos de desastre"""
        try:
            return self._load_json_file("desastres.json")
        except Exception as e:
            self.log_error("Error obteniendo desastres", e)
            raise
    
    def get_categorias_insumos(self) -> List[Dict[str, Any]]:
        """Obtener todas las categorías de insumos"""
        try:
            return self._load_json_file("categorias_insumos.json")
        except Exception as e:
            self.log_error("Error obteniendo categorías de insumos", e)
            raise
    
    def get_desastre_by_tipo(self, tipo_desastre: str) -> Dict[str, Any]:
        """Obtener desastre específico por tipo"""
        try:
            desastres = self.get_desastres()
            for desastre in desastres:
                if desastre['tipo'].lower() == tipo_desastre.lower():
                    return desastre
            raise ValueError(f"Tipo de desastre no encontrado: {tipo_desastre}")
        except Exception as e:
            self.log_error(f"Error obteniendo desastre {tipo_desastre}", e)
            raise

# Instancia global para reutilización
data_loader = DataLoader()