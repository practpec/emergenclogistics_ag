import json
import os
from typing import Dict, List, Any
from core.base_service import BaseService
from core.exceptions import DataLoadError
from entities.models.vehicle import Vehicle
from entities.models.disaster import Disaster, SupplyCategory

class DataLoader(BaseService):
    """Servicio para cargar datos desde archivos JSON"""
    
    def __init__(self):
        super().__init__()
        self._cache: Dict[str, Any] = {}
        # Obtener ruta base del proyecto (dos niveles arriba desde services/data/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.dirname(os.path.dirname(current_dir))
    
    def _create_default_files(self):
        """Crear archivos JSON por defecto si no existen"""
        default_data = {
            'vehiculos.json': [
                {
                    "id": 1,
                    "modelo": "Corolla",
                    "tipo": "auto",
                    "velocidad_kmh": 50,
                    "consumo_litros_km": 0.5,
                    "maximo_peso_ton": 1.5
                },
                {
                    "id": 2,
                    "modelo": "Hilux", 
                    "tipo": "camion",
                    "velocidad_kmh": 60,
                    "consumo_litros_km": 0.7,
                    "maximo_peso_ton": 2.5
                },
                {
                    "id": 3,
                    "modelo": "Sprinter",
                    "tipo": "van", 
                    "velocidad_kmh": 55,
                    "consumo_litros_km": 0.6,
                    "maximo_peso_ton": 2.0
                }
            ],
            'desastres.json': [
                {
                    "tipo": "inundacion",
                    "prioridad": [
                        {"categoria": "Alimentación básica", "nivel": "alta"},
                        {"categoria": "Higiene y cuidado personal", "nivel": "alta"},
                        {"categoria": "Medicamentos e insumos médicos", "nivel": "media"},
                        {"categoria": "Artículos para refugio", "nivel": "media"}
                    ]
                },
                {
                    "tipo": "terremoto", 
                    "prioridad": [
                        {"categoria": "Alimentación básica", "nivel": "alta"},
                        {"categoria": "Medicamentos e insumos médicos", "nivel": "alta"},
                        {"categoria": "Equipamiento de emergencia", "nivel": "media"},
                        {"categoria": "Higiene y cuidado personal", "nivel": "media"}
                    ]
                }
            ],
            'categorias_insumos.json': [
                {
                    "categoria": "Alimentación básica",
                    "subcategorias": ["Granos y cereales", "Proteínas enlatadas/secas"],
                    "peso_unitario_kg": 10
                },
                {
                    "categoria": "Higiene y cuidado personal", 
                    "subcategorias": ["Jabones y shampoo", "Salud bucal"],
                    "peso_unitario_kg": 5
                },
                {
                    "categoria": "Medicamentos e insumos médicos",
                    "subcategorias": ["Analgésicos básicos", "Antisépticos"],
                    "peso_unitario_kg": 4
                }
            ]
        }
        
        # Crear directorio entities/data si no existe
        data_dir = os.path.join(self.base_path, 'entities', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Crear archivos faltantes
        for filename, data in default_data.items():
            file_path = os.path.join(data_dir, filename)
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    self.log_info(f"Archivo por defecto creado: {filename}")
                except Exception as e:
                    self.log_error(f"Error creando archivo por defecto {filename}", e)
    
    def _get_file_path(self, filename: str) -> str:
        """Obtener ruta completa del archivo de datos con fallback"""
        # Intentar primero en entities/data/
        data_path = os.path.join(self.base_path, 'entities', 'data', filename)
        if os.path.exists(data_path):
            return data_path
        
        # Fallback a entities/
        entities_path = os.path.join(self.base_path, 'entities', filename)
        if os.path.exists(entities_path):
            return entities_path
        
        # Si no existe, intentar crear archivos por defecto
        self._create_default_files()
        
        # Verificar de nuevo si existe después de crear por defecto
        if os.path.exists(data_path):
            return data_path
            
        # Si aún no existe, retornar la ruta preferida para el error
        return data_path
    
    def load_vehicles(self) -> List[Vehicle]:
        """Cargar lista de vehículos disponibles"""
        if 'vehicles' not in self._cache:
            try:
                file_path = self._get_file_path('vehiculos.json')
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    vehicles = [Vehicle.from_dict(v) for v in data]
                    self._cache['vehicles'] = vehicles
                    self.log_info(f"Cargados {len(vehicles)} vehículos")
            except Exception as e:
                self.log_error("Error cargando vehículos", e)
                raise DataLoadError(f"No se pudieron cargar los vehículos: {e}")
        
        return self._cache['vehicles']
    
    def load_disasters(self) -> List[Disaster]:
        """Cargar tipos de desastres y sus prioridades"""
        if 'disasters' not in self._cache:
            try:
                file_path = self._get_file_path('desastres.json')
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    disasters = [Disaster.from_dict(d) for d in data]
                    self._cache['disasters'] = disasters
                    self.log_info(f"Cargados {len(disasters)} tipos de desastre")
            except Exception as e:
                self.log_error("Error cargando desastres", e)
                raise DataLoadError(f"No se pudieron cargar los desastres: {e}")
        
        return self._cache['disasters']
    
    def load_supply_categories(self) -> List[SupplyCategory]:
        """Cargar categorías de insumos"""
        if 'supply_categories' not in self._cache:
            try:
                file_path = self._get_file_path('categorias_insumos.json')
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    categories = [SupplyCategory.from_dict(c) for c in data]
                    self._cache['supply_categories'] = categories
                    self.log_info(f"Cargadas {len(categories)} categorías de insumos")
            except Exception as e:
                self.log_error("Error cargando categorías de insumos", e)
                raise DataLoadError(f"No se pudieron cargar las categorías: {e}")
        
        return self._cache['supply_categories']
    
    def get_vehicle_by_type(self, vehicle_type: str) -> Vehicle:
        """Obtener vehículo por tipo"""
        vehicles = self.load_vehicles()
        for vehicle in vehicles:
            if vehicle.tipo == vehicle_type:
                return vehicle
        raise DataLoadError(f"Tipo de vehículo no encontrado: {vehicle_type}")
    
    def get_disaster_by_type(self, disaster_type: str) -> Disaster:
        """Obtener desastre por tipo"""
        disasters = self.load_disasters()
        for disaster in disasters:
            if disaster.tipo == disaster_type:
                return disaster
        raise DataLoadError(f"Tipo de desastre no encontrado: {disaster_type}")
    
    def get_all_entities(self) -> Dict[str, List]:
        """Obtener todas las entidades en un diccionario"""
        return {
            'vehiculos': [v.to_dict() for v in self.load_vehicles()],
            'desastres': [d.to_dict() for d in self.load_disasters()],
            'categorias_insumos': [c.to_dict() for c in self.load_supply_categories()]
        }
    
    def clear_cache(self) -> None:
        """Limpiar cache de datos"""
        self._cache.clear()
        self.log_info("Cache de datos limpiado")