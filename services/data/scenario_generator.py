import random
from typing import Dict, List, Any
from core.base_service import BaseService
from core.exceptions import ValidationError
from entities.models.scenario import Scenario, ScenarioStatistics
from entities.models.vehicle import Vehicle
from entities.models.route import RouteState
from .data_loader import DataLoader

class ScenarioGenerator(BaseService):
    """Generador de escenarios de emergencia"""
    
    def __init__(self):
        super().__init__()
        self.data_loader = DataLoader()
        self.bloqueo_reasons = [
            "Derrumbe en carretera",
            "Puente dañado", 
            "Inundación parcial",
            "Bloqueo por manifestantes",
            "Mantenimiento vial"
        ]
    
    def generate_scenario(self, config: Dict[str, Any], map_data: Dict[str, Any]) -> Scenario:
        """Generar escenario completo basado en configuración y datos del mapa"""
        try:
            # Validar datos de entrada
            self._validate_config(config)
            self._validate_map_data(map_data)
            
            # Obtener datos base
            disaster = self.data_loader.get_disaster_by_type(config['tipo_desastre'])
            supply_categories = self.data_loader.load_supply_categories()
            
            # Procesar vehículos
            vehicles = self._process_vehicles(config['vehiculos'])
            
            # Generar rutas y estados
            destinos_rutas, rutas_estado = self._generate_routes_data(map_data)
            
            # Calcular estadísticas
            stats = self._calculate_statistics(destinos_rutas, rutas_estado, vehicles)
            
            scenario = Scenario(
                punto_partida=map_data['punto_inicio'],
                tipo_desastre=config['tipo_desastre'],
                desastre_detalles=disaster,
                vehiculos_disponibles=vehicles,
                destinos_rutas=[destinos_rutas],
                rutas_estado=rutas_estado,
                categorias_insumos=supply_categories,
                estadisticas=stats
            )
            
            self.log_info("Escenario generado exitosamente", 
                         tipo_desastre=config['tipo_desastre'],
                         num_vehiculos=len(vehicles),
                         num_rutas=len(rutas_estado))
            
            return scenario
            
        except Exception as e:
            self.log_error("Error generando escenario", e)
            raise
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validar configuración del escenario"""
        if not config.get('tipo_desastre'):
            raise ValidationError("Tipo de desastre es requerido")
        
        if not config.get('vehiculos'):
            raise ValidationError("Lista de vehículos es requerida")
        
        if len(config['vehiculos']) == 0:
            raise ValidationError("Debe haber al menos un vehículo")
    
    def _validate_map_data(self, map_data: Dict[str, Any]) -> None:
        """Validar datos del mapa"""
        if not map_data.get('punto_inicio'):
            raise ValidationError("Punto de inicio es requerido")
        
        if not map_data.get('nodos_secundarios'):
            raise ValidationError("Nodos secundarios son requeridos")
        
        if not map_data.get('rutas_data'):
            raise ValidationError("Datos de rutas son requeridos")
    
    def _process_vehicles(self, vehicle_configs: List[Dict]) -> List[Vehicle]:
        """Procesar configuración de vehículos"""
        vehicles = []
        
        for i, config in enumerate(vehicle_configs):
            vehicle_template = self.data_loader.get_vehicle_by_type(config['tipo'])
            
            # Crear copia con ID único
            vehicle = Vehicle(
                id=i + 1,
                modelo=vehicle_template.modelo,
                tipo=vehicle_template.tipo,
                velocidad_kmh=vehicle_template.velocidad_kmh,
                consumo_litros_km=vehicle_template.consumo_litros_km,
                maximo_peso_ton=vehicle_template.maximo_peso_ton
            )
            vehicles.append(vehicle)
        
        return vehicles
    
    def _generate_routes_data(self, map_data: Dict[str, Any]) -> tuple[List[Dict], List[RouteState]]:
        """Generar datos de rutas y estados"""
        destinos_rutas = []
        rutas_estado = []
        ruta_id = 1
        
        vehicle_types = [v.tipo for v in self.data_loader.load_vehicles()]
        
        # Procesar cada nodo secundario
        for i, nodo in enumerate(map_data['nodos_secundarios']):
            destino_name = f"destino{i+1}"
            distancia = nodo.get('distancia_directa', 25)
            
            # Ruta principal
            destinos_rutas.append({
                "id_destino_ruta": ruta_id,
                "salida": "salida unica",
                "destino": destino_name,
                "distancia_km": distancia
            })
            
            # Estado de la ruta principal
            rutas_estado.append(self._generate_route_state(
                ruta_id, destino_name, distancia, vehicle_types
            ))
            ruta_id += 1
            
            # Ruta alternativa si hay múltiples rutas disponibles
            ruta_destino = next((r for r in map_data['rutas_data'] if r['indice'] == i), None)
            if ruta_destino and len(ruta_destino.get('rutas', [])) > 1:
                distancia_alt = ruta_destino['rutas'][1]['distancia']['value'] / 1000
                
                destinos_rutas.append({
                    "id_destino_ruta": ruta_id,
                    "salida": "salida unica", 
                    "destino": destino_name,
                    "distancia_km": round(distancia_alt, 1)
                })
                
                rutas_estado.append(self._generate_route_state(
                    ruta_id, destino_name, round(distancia_alt, 1), vehicle_types
                ))
                ruta_id += 1
        
        return destinos_rutas, rutas_estado
    
    def _generate_route_state(self, ruta_id: int, destino: str, distancia: float, 
                            vehicle_types: List[str]) -> RouteState:
        """Generar estado aleatorio para una ruta"""
        # 85% probabilidad de estar abierta
        estado = "abierta" if random.random() > 0.15 else "cerrada"
        
        # Vehículos permitidos (1-3 tipos aleatorios)
        num_tipos = random.randint(1, len(vehicle_types))
        vehiculos_permitidos = random.sample(vehicle_types, num_tipos)
        
        # Razón del bloqueo si está cerrada
        razon_bloqueo = None
        if estado == "cerrada":
            razon_bloqueo = random.choice(self.bloqueo_reasons)
        
        return RouteState(
            id_destino_ruta=ruta_id,
            estado=estado,
            vehiculos_permitidos=vehiculos_permitidos,
            razon_bloqueo=razon_bloqueo,
            destino=destino,
            distancia_km=distancia
        )
    
    def _calculate_statistics(self, destinos_rutas: List[Dict], 
                            rutas_estado: List[RouteState], 
                            vehicles: List[Vehicle]) -> ScenarioStatistics:
        """Calcular estadísticas del escenario"""
        unique_destinos = set(r['destino'] for r in destinos_rutas)
        rutas_abiertas = sum(1 for r in rutas_estado if r.estado == 'abierta')
        rutas_cerradas = sum(1 for r in rutas_estado if r.estado == 'cerrada')
        
        return ScenarioStatistics(
            total_destinos=len(unique_destinos),
            total_rutas=len(destinos_rutas),
            rutas_abiertas=rutas_abiertas,
            rutas_cerradas=rutas_cerradas,
            total_vehiculos=len(vehicles)
        )