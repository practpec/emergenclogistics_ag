import json
import os
from typing import List, Dict, Any, Optional
from core.base_service import CacheableService
from core.exceptions import DataLoadError
from entities.models.vehicle import Vehicle
from entities.models.disaster import Disaster, DisasterPriority, SupplyCategory

class StaticDataService(CacheableService):
    """Servicio para cargar datos estáticos desde archivos JSON"""
    
    def __init__(self):
        super().__init__()
        self.data_path = "entities/data"
    
    def _load_json_file(self, filename: str) -> List[Dict[str, Any]]:
        """Cargar archivo JSON de forma segura"""
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
            self.log_info(f"Datos cargados desde {filename}")
            return data
            
        except json.JSONDecodeError as e:
            self.log_error(f"Error JSON en {filename}", e)
            raise DataLoadError(f"Error decodificando JSON: {filename}")
        except Exception as e:
            self.log_error(f"Error cargando {filename}", e)
            raise DataLoadError(f"Error cargando archivo: {filename}")
    
    def get_all_vehicles(self) -> List[Vehicle]:
        """Obtener todos los vehículos disponibles"""
        try:
            vehicles_data = self._load_json_file("vehiculos.json")
            vehicles = [Vehicle.from_dict(vehicle_data) for vehicle_data in vehicles_data]
            
            self.log_info(f"Vehículos cargados: {len(vehicles)}")
            return vehicles
            
        except Exception as e:
            self.log_error("Error obteniendo vehículos", e)
            raise
    
    def get_vehicle_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        """Obtener vehículo específico por ID"""
        try:
            vehicles = self.get_all_vehicles()
            for vehicle in vehicles:
                if vehicle.id == vehicle_id:
                    return vehicle
            return None
            
        except Exception as e:
            self.log_error(f"Error obteniendo vehículo {vehicle_id}", e)
            raise
    
    def get_vehicles_by_type(self, vehicle_type: str) -> List[Vehicle]:
        """Obtener vehículos por tipo específico"""
        try:
            vehicles = self.get_all_vehicles()
            filtered_vehicles = [v for v in vehicles if v.tipo.lower() == vehicle_type.lower()]
            
            self.log_info(f"Vehículos tipo '{vehicle_type}': {len(filtered_vehicles)}")
            return filtered_vehicles
            
        except Exception as e:
            self.log_error(f"Error filtrando vehículos por tipo {vehicle_type}", e)
            raise
    
    def get_all_disasters(self) -> List[Disaster]:
        """Obtener todos los tipos de desastre disponibles"""
        try:
            disasters_data = self._load_json_file("desastres.json")
            disasters = []
            
            for disaster_data in disasters_data:
                priorities = [
                    DisasterPriority(
                        categoria=p['categoria'],
                        nivel=p['nivel']
                    ) for p in disaster_data['prioridades']
                ]
                
                disaster = Disaster(
                    tipo=disaster_data['tipo'],
                    prioridad=priorities
                )
                disasters.append(disaster)
            
            self.log_info(f"Tipos de desastre cargados: {len(disasters)}")
            return disasters
            
        except Exception as e:
            self.log_error("Error obteniendo desastres", e)
            raise
    
    def get_disaster_by_type(self, disaster_type: str) -> Optional[Disaster]:
        """Obtener desastre específico por tipo"""
        try:
            disasters = self.get_all_disasters()
            for disaster in disasters:
                if disaster.tipo.lower() == disaster_type.lower():
                    return disaster
            return None
            
        except Exception as e:
            self.log_error(f"Error obteniendo desastre {disaster_type}", e)
            raise
    
    def get_all_supply_categories(self) -> List[SupplyCategory]:
        """Obtener todas las categorías de insumos"""
        try:
            categories_data = self._load_json_file("categorias_insumos.json")
            categories = []
            
            for category_data in categories_data:
                # Calcular peso promedio de subcategorías
                subcategorias = [sub['nombre'] for sub in category_data['subcategorias']]
                peso_promedio = sum(sub['peso_kg'] for sub in category_data['subcategorias']) / len(category_data['subcategorias'])
                
                category = SupplyCategory(
                    categoria=category_data['categoria'],
                    subcategorias=subcategorias,
                    peso_unitario_kg=peso_promedio
                )
                categories.append(category)
            
            self.log_info(f"Categorías de insumos cargadas: {len(categories)}")
            return categories
            
        except Exception as e:
            self.log_error("Error obteniendo categorías de insumos", e)
            raise
    
    def get_supply_category_by_name(self, category_name: str) -> Optional[SupplyCategory]:
        """Obtener categoría específica por nombre"""
        try:
            categories = self.get_all_supply_categories()
            for category in categories:
                if category.categoria.lower() == category_name.lower():
                    return category
            return None
            
        except Exception as e:
            self.log_error(f"Error obteniendo categoría {category_name}", e)
            raise
    
    def get_vehicle_types(self) -> List[str]:
        """Obtener lista de tipos de vehículos únicos"""
        try:
            vehicles = self.get_all_vehicles()
            vehicle_types = list(set(v.tipo for v in vehicles))
            return sorted(vehicle_types)
            
        except Exception as e:
            self.log_error("Error obteniendo tipos de vehículos", e)
            raise
    
    def get_disaster_types(self) -> List[str]:
        """Obtener lista de tipos de desastre únicos"""
        try:
            disasters = self.get_all_disasters()
            disaster_types = [d.tipo for d in disasters]
            return sorted(disaster_types)
            
        except Exception as e:
            self.log_error("Error obteniendo tipos de desastre", e)
            raise
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validar integridad de todos los datos estáticos"""
        try:
            validation_results = {
                'vehicles': {'loaded': False, 'count': 0, 'errors': []},
                'disasters': {'loaded': False, 'count': 0, 'errors': []},
                'supply_categories': {'loaded': False, 'count': 0, 'errors': []}
            }
            
            # Validar vehículos
            try:
                vehicles = self.get_all_vehicles()
                validation_results['vehicles']['loaded'] = True
                validation_results['vehicles']['count'] = len(vehicles)
            except Exception as e:
                validation_results['vehicles']['errors'].append(str(e))
            
            # Validar desastres
            try:
                disasters = self.get_all_disasters()
                validation_results['disasters']['loaded'] = True
                validation_results['disasters']['count'] = len(disasters)
            except Exception as e:
                validation_results['disasters']['errors'].append(str(e))
            
            # Validar categorías
            try:
                categories = self.get_all_supply_categories()
                validation_results['supply_categories']['loaded'] = True
                validation_results['supply_categories']['count'] = len(categories)
            except Exception as e:
                validation_results['supply_categories']['errors'].append(str(e))
            
            validation_results['overall_status'] = all(
                result['loaded'] for result in validation_results.values() 
                if isinstance(result, dict) and 'loaded' in result
            )
            
            return validation_results
            
        except Exception as e:
            self.log_error("Error validando integridad de datos", e)
            raise