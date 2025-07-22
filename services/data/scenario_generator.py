import random
from typing import Dict, List, Any
from core.base_service import BaseService
from core.exceptions import ValidationError
from entities.models.scenario import Scenario, ScenarioStatistics
from entities.models.vehicle import Vehicle
from entities.models.route import RouteState
from .data_loader import DataLoader

class ScenarioGenerator(BaseService):
    """Generador de escenarios de emergencia con datos reales de localidades"""
    
    def __init__(self):
        super().__init__()
        self.data_loader = DataLoader()
        self.bloqueo_reasons = [
            "Derrumbe en carretera principal",
            "Puente dañado por lluvias", 
            "Inundación en zona urbana",
            "Bloqueo por manifestantes",
            "Mantenimiento vial programado",
            "Deslizamiento de tierra",
            "Carretera en mal estado",
            "Restricción por contingencia"
        ]
    
    def generate_scenario(self, config: Dict[str, Any], map_data: Dict[str, Any]) -> Scenario:
        """Generar escenario completo basado en configuración y datos reales del mapa"""
        try:
            # Validar datos de entrada
            self._validate_config(config)
            self._validate_map_data(map_data)
            
            # Obtener datos base
            disaster = self.data_loader.get_disaster_by_type(config['tipo_desastre'])
            supply_categories = self.data_loader.load_supply_categories()
            
            # Procesar vehículos
            vehicles = self._process_vehicles(config['vehiculos'])
            
            # Generar rutas y estados con datos reales
            destinos_rutas, rutas_estado = self._generate_routes_data_real(map_data)
            
            # Calcular estadísticas
            stats = self._calculate_statistics(destinos_rutas, rutas_estado, vehicles)
            
            # Crear punto de partida desde datos reales
            punto_partida = self._format_punto_partida(map_data)
            
            scenario = Scenario(
                punto_partida=punto_partida,
                tipo_desastre=config['tipo_desastre'],
                desastre_detalles=disaster,
                vehiculos_disponibles=vehicles,
                destinos_rutas=[destinos_rutas],
                rutas_estado=rutas_estado,
                categorias_insumos=supply_categories,
                estadisticas=stats
            )
            
            self.log_info("Escenario generado con datos reales", 
                         tipo_desastre=config['tipo_desastre'],
                         num_vehiculos=len(vehicles),
                         num_rutas=len(rutas_estado),
                         localidades_reales=len(map_data.get('nodos_secundarios', [])))
            
            return scenario
            
        except Exception as e:
            self.log_error("Error generando escenario con datos reales", e)
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
        """Validar datos del mapa con información real"""
        if not map_data.get('punto_inicio'):
            raise ValidationError("Punto de inicio es requerido")
        
        if not map_data.get('nodo_principal'):
            raise ValidationError("Nodo principal con datos reales es requerido")
        
        if not map_data.get('nodos_secundarios'):
            raise ValidationError("Nodos secundarios con localidades reales son requeridos")
        
        if not map_data.get('rutas_data'):
            raise ValidationError("Datos de rutas calculadas son requeridos")
        
        # Validar que los nodos tengan información de localidades reales
        nodo_principal = map_data['nodo_principal']
        if not all(key in nodo_principal for key in ['clave_estado', 'clave_municipio', 'clave_localidad']):
            raise ValidationError("Nodo principal debe tener claves de localidad real")
        
        for nodo in map_data['nodos_secundarios']:
            if not all(key in nodo for key in ['clave_estado', 'clave_municipio', 'clave_localidad']):
                raise ValidationError("Todos los nodos secundarios deben tener claves de localidades reales")
    
    def _format_punto_partida(self, map_data: Dict[str, Any]) -> str:
        """Formatear punto de partida con información detallada"""
        nodo_principal = map_data['nodo_principal']
        return f"{nodo_principal['nombre']} (Clave: {nodo_principal['clave_estado']}-{nodo_principal['clave_municipio']}-{nodo_principal['clave_localidad']})"
    
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
    
    def _generate_routes_data_real(self, map_data: Dict[str, Any]) -> tuple[List[Dict], List[RouteState]]:
        """Generar datos de rutas y estados con información real de localidades"""
        destinos_rutas = []
        rutas_estado = []
        ruta_id = 1
        
        vehicle_types = [v.tipo for v in self.data_loader.load_vehicles()]
        nodo_principal = map_data['nodo_principal']
        
        # Procesar cada nodo secundario con información real
        for i, nodo in enumerate(map_data['nodos_secundarios']):
            destino_name = f"{nodo['nombre']} (Clave: {nodo['clave_estado']}-{nodo['clave_municipio']}-{nodo['clave_localidad']})"
            distancia = nodo.get('distancia_directa', 25)
            
            # Información adicional del destino real
            destino_info = {
                "id_destino_ruta": ruta_id,
                "salida": f"{nodo_principal['nombre']}",
                "destino": destino_name,
                "distancia_km": distancia,
                "poblacion_destino": nodo.get('poblacion', 0),
                "coordenadas": {
                    "lat": nodo['lat'],
                    "lng": nodo['lng']
                },
                "localidad_info": {
                    "clave_estado": nodo['clave_estado'],
                    "clave_municipio": nodo['clave_municipio'],
                    "clave_localidad": nodo['clave_localidad'],
                    "nombre_completo": nodo['nombre']
                }
            }
            
            destinos_rutas.append(destino_info)
            
            # Estado de la ruta principal
            rutas_estado.append(self._generate_route_state_real(
                ruta_id, destino_name, distancia, vehicle_types, nodo
            ))
            ruta_id += 1
            
            # Ruta alternativa si hay múltiples rutas disponibles
            ruta_destino = next((r for r in map_data['rutas_data'] if r['indice'] == i), None)
            if ruta_destino and len(ruta_destino.get('rutas', [])) > 1:
                distancia_alt = ruta_destino['rutas'][1]['distancia']['value'] / 1000
                
                destino_alt_info = destino_info.copy()
                destino_alt_info.update({
                    "id_destino_ruta": ruta_id,
                    "distancia_km": round(distancia_alt, 1),
                    "tipo_ruta": "alternativa"
                })
                
                destinos_rutas.append(destino_alt_info)
                
                rutas_estado.append(self._generate_route_state_real(
                    ruta_id, destino_name, round(distancia_alt, 1), vehicle_types, nodo, es_alternativa=True
                ))
                ruta_id += 1
        
        return destinos_rutas, rutas_estado
    
    def _generate_route_state_real(self, ruta_id: int, destino: str, distancia: float, 
                                  vehicle_types: List[str], nodo_info: Dict, es_alternativa: bool = False) -> RouteState:
        """Generar estado de ruta considerando características reales de la localidad"""
        
        # Probabilidad de bloqueo basada en características reales
        probabilidad_bloqueo = 0.15  # Base 15%
        
        # Ajustar probabilidad según población (localidades pequeñas más propensas a bloqueos)
        poblacion = nodo_info.get('poblacion', 0)
        if poblacion < 1000:
            probabilidad_bloqueo += 0.10  # +10% para localidades muy pequeñas
        elif poblacion < 5000:
            probabilidad_bloqueo += 0.05  # +5% para localidades pequeñas
        
        # Ajustar probabilidad según distancia (rutas más largas más propensas a problemas)
        if distancia > 100:
            probabilidad_bloqueo += 0.10
        elif distancia > 50:
            probabilidad_bloqueo += 0.05
        
        # Rutas alternativas tienen mayor probabilidad de bloqueo
        if es_alternativa:
            probabilidad_bloqueo += 0.10
        
        # Determinar estado
        estado = "abierta" if random.random() > probabilidad_bloqueo else "cerrada"
        
        # Vehículos permitidos (considerar accesibilidad según tipo de localidad)
        if poblacion < 500:
            # Localidades muy pequeñas: solo vehículos menores
            vehiculos_permitidos = [t for t in vehicle_types if t in ['auto', 'van']]
            if not vehiculos_permitidos:
                vehiculos_permitidos = vehicle_types[:2]  # Al menos 2 tipos
        elif poblacion < 2000:
            # Localidades pequeñas: la mayoría de vehículos
            num_tipos = random.randint(2, len(vehicle_types))
            vehiculos_permitidos = random.sample(vehicle_types, num_tipos)
        else:
            # Localidades grandes: todos los vehículos
            vehiculos_permitidos = vehicle_types.copy()
        
        # Razón del bloqueo si está cerrada
        razon_bloqueo = None
        if estado == "cerrada":
            if poblacion < 1000:
                razones_locales = [
                    "Camino rural en mal estado",
                    "Puente local dañado",
                    "Acceso restringido por lluvias"
                ]
                razon_bloqueo = random.choice(razones_locales + self.bloqueo_reasons)
            else:
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
        """Calcular estadísticas del escenario con datos reales"""
        unique_destinos = set()
        total_poblacion = 0
        
        for ruta in destinos_rutas:
            if 'localidad_info' in ruta:
                clave_localidad = f"{ruta['localidad_info']['clave_estado']}-{ruta['localidad_info']['clave_municipio']}-{ruta['localidad_info']['clave_localidad']}"
                unique_destinos.add(clave_localidad)
                total_poblacion += ruta.get('poblacion_destino', 0)
        
        rutas_abiertas = sum(1 for r in rutas_estado if r.estado == 'abierta')
        rutas_cerradas = sum(1 for r in rutas_estado if r.estado == 'cerrada')
        
        # Crear estadísticas básicas
        stats = ScenarioStatistics(
            total_destinos=len(unique_destinos),
            total_rutas=len(destinos_rutas),
            rutas_abiertas=rutas_abiertas,
            rutas_cerradas=rutas_cerradas,
            total_vehiculos=len(vehicles),
            poblacion_total_destinos=total_poblacion,
            usando_datos_reales=True
        )
        
        return stats