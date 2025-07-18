"""
Generador de escenarios de emergencia
"""
import random
from typing import Dict, List, Any
from services.data.data_loader import DataLoader
from utils.helpers import calculate_vehicle_capacity_kg
from utils.logger import get_logger
from core.exceptions import ScenarioGenerationError

class ScenarioGenerator:
    """Generador de escenarios para algoritmo genético"""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.logger = get_logger(__name__)
    
    def create_scenario(self, request_data: Dict[str, Any], 
                       map_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear escenario completo"""
        try:
            entities = self.data_loader.load_all_entities()
            
            # Procesar datos básicos
            disaster_type = request_data['tipo_desastre']
            disaster_details = self._find_disaster_details(entities['desastres'], disaster_type)
            
            # Generar componentes del escenario
            destinations_routes = self._generate_destinations_routes(map_data)
            routes_state = self._generate_routes_state(destinations_routes, entities['vehiculos'])
            configured_vehicles = self._configure_vehicles(request_data['vehiculos'], entities['vehiculos'])
            
            # Construir escenario
            scenario = {
                "punto_partida": map_data['punto_inicio'],
                "tipo_desastre": disaster_type,
                "desastre_detalles": disaster_details,
                "vehiculos_disponibles": configured_vehicles,
                "destinos_rutas": [destinations_routes],
                "rutas_estado": routes_state,
                "categorias_insumos": entities['categorias_insumos'],
                "estadisticas": self._calculate_statistics(destinations_routes, routes_state, configured_vehicles)
            }
            
            self.logger.info(f"Escenario generado exitosamente para {disaster_type}")
            return scenario
            
        except Exception as e:
            self.logger.error(f"Error generando escenario: {e}")
            raise ScenarioGenerationError(f"No se pudo generar el escenario: {e}")
    
    def _find_disaster_details(self, disasters: List[Dict[str, Any]], 
                              disaster_type: str) -> Dict[str, Any]:
        """Encontrar detalles del tipo de desastre"""
        for disaster in disasters:
            if disaster['tipo'] == disaster_type:
                return disaster
        
        # Fallback al primer desastre si no se encuentra
        self.logger.warning(f"Tipo de desastre no encontrado: {disaster_type}")
        return disasters[0] if disasters else {}
    
    def _generate_destinations_routes(self, map_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar destinos y rutas desde datos del mapa"""
        destinations_routes = []
        route_id = 1
        
        for i, node in enumerate(map_data['nodos_secundarios']):
            destination_name = f"destino{i+1}"
            distance = node.get('distancia_directa', 25)
            
            # Ruta principal
            destinations_routes.append({
                "id_destino_ruta": route_id,
                "salida": "salida unica",
                "destino": destination_name,
                "distancia_km": distance
            })
            route_id += 1
            
            # Ruta alternativa si existe en rutas_data
            route_destination = next(
                (r for r in map_data['rutas_data'] if r['indice'] == i), None
            )
            
            if route_destination and len(route_destination.get('rutas', [])) > 1:
                alt_distance = route_destination['rutas'][1]['distancia']['value'] / 1000
                destinations_routes.append({
                    "id_destino_ruta": route_id,
                    "salida": "salida unica",
                    "destino": destination_name,
                    "distancia_km": round(alt_distance, 1)
                })
                route_id += 1
        
        return destinations_routes
    
    def _generate_routes_state(self, destinations_routes: List[Dict[str, Any]], 
                              vehicle_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generar estado de rutas con restricciones"""
        routes_state = []
        vehicle_types = [v['tipo'] for v in vehicle_entities]
        block_reasons = [
            "Derrumbe en carretera",
            "Puente dañado",
            "Inundación parcial",
            "Bloqueo por manifestantes",
            "Mantenimiento vial"
        ]
        
        for route in destinations_routes:
            # Vehículos permitidos (1-3 tipos aleatorios)
            num_types = random.randint(1, len(vehicle_types))
            allowed_vehicles = random.sample(vehicle_types, num_types)
            
            # Estado (85% abiertas, 15% cerradas)
            is_open = random.random() > 0.15
            state = "abierta" if is_open else "cerrada"
            
            # Razón de bloqueo si está cerrada
            block_reason = None if is_open else random.choice(block_reasons)
            
            routes_state.append({
                "id_destino_ruta": route["id_destino_ruta"],
                "estado": state,
                "vehiculos_permitidos": allowed_vehicles,
                "razon_bloqueo": block_reason,
                "destino": route["destino"],
                "distancia_km": route["distancia_km"]
            })
        
        return routes_state
    
    def _configure_vehicles(self, requested_vehicles: List[Dict[str, Any]], 
                           vehicle_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Configurar vehículos con detalles completos"""
        configured_vehicles = []
        
        for i, vehicle_config in enumerate(requested_vehicles):
            vehicle_type = vehicle_config.get('tipo')
            
            # Buscar detalles del vehículo
            vehicle_entity = next(
                (v for v in vehicle_entities if v['tipo'] == vehicle_type), None
            )
            
            if vehicle_entity:
                configured_vehicles.append({
                    "vehiculo_id": i + 1,
                    "tipo": vehicle_entity['tipo'],
                    "modelo": vehicle_entity['modelo'],
                    "velocidad_kmh": vehicle_entity['velocidad_kmh'],
                    "consumo_litros_km": vehicle_entity['consumo_litros_km'],
                    "maximo_peso_ton": vehicle_entity['maximo_peso_ton'],
                    "capacidad_kg": calculate_vehicle_capacity_kg(vehicle_entity['maximo_peso_ton'])
                })
        
        return configured_vehicles
    
    def _calculate_statistics(self, destinations_routes: List[Dict[str, Any]], 
                             routes_state: List[Dict[str, Any]], 
                             vehicles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calcular estadísticas del escenario"""
        unique_destinations = set(r['destino'] for r in destinations_routes)
        open_routes = [r for r in routes_state if r['estado'] == 'abierta']
        closed_routes = [r for r in routes_state if r['estado'] == 'cerrada']
        
        return {
            "total_destinos": len(unique_destinations),
            "total_rutas": len(destinations_routes),
            "rutas_abiertas": len(open_routes),
            "rutas_cerradas": len(closed_routes),
            "total_vehiculos": len(vehicles)
        }