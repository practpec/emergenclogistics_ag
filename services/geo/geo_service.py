"""
Servicio geográfico optimizado
"""
import random
import math
from typing import Dict, List, Tuple
from utils.logger import get_logger

class GeoService:
    """Servicio para operaciones geográficas"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.estados_coords = self._load_states_data()
    
    def _load_states_data(self) -> Dict[str, Dict[str, float]]:
        """Cargar coordenadas de estados"""
        return {
            "Chiapas": {"lat": 16.75, "lng": -93.1167},
            "CDMX": {"lat": 19.4326, "lng": -99.1332},
            "Jalisco": {"lat": 20.6597, "lng": -103.3496},
            "Nuevo León": {"lat": 25.6866, "lng": -100.3161},
            "Yucatán": {"lat": 20.7099, "lng": -89.0943},
            "Oaxaca": {"lat": 17.0732, "lng": -96.7266},
            "Puebla": {"lat": 19.0414, "lng": -98.2063},
            "Veracruz": {"lat": 19.1738, "lng": -96.1342},
            "Guanajuato": {"lat": 21.0190, "lng": -101.2574},
            "Michoacán": {"lat": 19.5665, "lng": -101.7068},
            "Guerrero": {"lat": 17.4392, "lng": -99.5451},
            "Sonora": {"lat": 29.2972, "lng": -110.3309},
            "Tamaulipas": {"lat": 24.2669, "lng": -98.8363},
            "Sinaloa": {"lat": 25.1721, "lng": -107.4795},
            "Coahuila": {"lat": 27.0587, "lng": -101.7068},
            "Quintana Roo": {"lat": 19.1817, "lng": -88.4791},
            "Baja California": {"lat": 30.8406, "lng": -115.2838},
            "San Luis Potosí": {"lat": 22.1565, "lng": -100.9855}
        }
    
    def get_states(self) -> List[str]:
        """Obtener lista de estados"""
        return list(self.estados_coords.keys())
    
    def get_state_coords(self, state: str) -> Dict[str, float]:
        """Obtener coordenadas de estado"""
        coords = self.estados_coords.get(state)
        if not coords:
            self.logger.warning(f"Estado no encontrado: {state}")
            return self.estados_coords["Chiapas"]  # Fallback
        return coords
    
    def calculate_distance_haversine(self, lat1: float, lon1: float, 
                                   lat2: float, lon2: float) -> float:
        """Calcular distancia usando fórmula de Haversine"""
        R = 6371  # Radio terrestre en km
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def generate_secondary_nodes(self, state: str, count: int) -> Dict[str, any]:
        """Generar nodos secundarios para un estado"""
        base_coords = self.get_state_coords(state)
        
        nodes = []
        for _ in range(count):
            # Generar punto aleatorio en radio de 100km
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(10, 100)
            
            # Convertir a coordenadas
            lat_offset = (radius / 111.32) * math.cos(angle)
            lng_offset = (radius / (111.32 * math.cos(math.radians(base_coords['lat'])))) * math.sin(angle)
            
            new_lat = base_coords['lat'] + lat_offset
            new_lng = base_coords['lng'] + lng_offset
            
            # Validar límites de México
            if 14.5 <= new_lat <= 32.7 and -118.4 <= new_lng <= -86.7:
                distance = self.calculate_distance_haversine(
                    base_coords['lat'], base_coords['lng'], new_lat, new_lng
                )
                
                nodes.append({
                    "lat": new_lat,
                    "lng": new_lng,
                    "distancia_directa": round(distance, 2)
                })
        
        # Asegurar que tengamos suficientes nodos
        while len(nodes) < count:
            nodes.append(self._generate_fallback_node(base_coords))
        
        result = {
            "nodo_principal": {**base_coords, "nombre": state},
            "nodos_secundarios": nodes[:count]
        }
        
        self.logger.info(f"Generados {len(result['nodos_secundarios'])} nodos para {state}")
        return result
    
    def _generate_fallback_node(self, base_coords: Dict[str, float]) -> Dict[str, float]:
        """Generar nodo de respaldo cerca del centro"""
        lat_offset = random.uniform(-0.5, 0.5)
        lng_offset = random.uniform(-0.5, 0.5)
        
        new_lat = base_coords['lat'] + lat_offset
        new_lng = base_coords['lng'] + lng_offset
        
        distance = self.calculate_distance_haversine(
            base_coords['lat'], base_coords['lng'], new_lat, new_lng
        )
        
        return {
            "lat": new_lat,
            "lng": new_lng,
            "distancia_directa": round(distance, 2)
        }