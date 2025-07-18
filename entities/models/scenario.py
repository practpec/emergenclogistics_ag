from dataclasses import dataclass
from typing import List, Dict, Any
from .vehicle import Vehicle
from .disaster import Disaster, SupplyCategory
from .route import RouteState

@dataclass
class ScenarioStatistics:
    """Estadísticas del escenario"""
    total_destinos: int
    total_rutas: int
    rutas_abiertas: int
    rutas_cerradas: int
    total_vehiculos: int
    
    def to_dict(self) -> Dict[str, int]:
        return {
            'total_destinos': self.total_destinos,
            'total_rutas': self.total_rutas,
            'rutas_abiertas': self.rutas_abiertas,
            'rutas_cerradas': self.rutas_cerradas,
            'total_vehiculos': self.total_vehiculos
        }

@dataclass
class Scenario:
    """Modelo completo de escenario"""
    punto_partida: str
    tipo_desastre: str
    desastre_detalles: Disaster
    vehiculos_disponibles: List[Vehicle]
    destinos_rutas: List[List[Dict]]  # Estructura anidada del JSON original
    rutas_estado: List[RouteState]
    categorias_insumos: List[SupplyCategory]
    estadisticas: ScenarioStatistics
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario completo"""
        return {
            'punto_partida': self.punto_partida,
            'tipo_desastre': self.tipo_desastre,
            'desastre_detalles': self.desastre_detalles.to_dict(),
            'vehiculos_disponibles': [v.to_dict() for v in self.vehiculos_disponibles],
            'destinos_rutas': self.destinos_rutas,
            'rutas_estado': [r.to_dict() for r in self.rutas_estado],
            'categorias_insumos': [c.to_dict() for c in self.categorias_insumos],
            'estadisticas': self.estadisticas.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scenario':
        """Crear desde diccionario"""
        desastre = Disaster.from_dict(data['desastre_detalles'])
        vehiculos = [Vehicle.from_dict(v) for v in data['vehiculos_disponibles']]
        rutas_estado = [RouteState.from_dict(r) for r in data['rutas_estado']]
        categorias = [SupplyCategory.from_dict(c) for c in data['categorias_insumos']]
        
        stats_data = data['estadisticas']
        estadisticas = ScenarioStatistics(
            total_destinos=stats_data['total_destinos'],
            total_rutas=stats_data['total_rutas'],
            rutas_abiertas=stats_data['rutas_abiertas'],
            rutas_cerradas=stats_data['rutas_cerradas'],
            total_vehiculos=stats_data['total_vehiculos']
        )
        
        return cls(
            punto_partida=data['punto_partida'],
            tipo_desastre=data['tipo_desastre'],
            desastre_detalles=desastre,
            vehiculos_disponibles=vehiculos,
            destinos_rutas=data['destinos_rutas'],
            rutas_estado=rutas_estado,
            categorias_insumos=categorias,
            estadisticas=estadisticas
        )
    
    def get_available_routes(self) -> List[RouteState]:
        """Obtener rutas disponibles (abiertas)"""
        return [r for r in self.rutas_estado if r.estado == 'abierta']
    
    def get_routes_for_vehicle_type(self, vehicle_type: str) -> List[RouteState]:
        """Obtener rutas disponibles para un tipo de vehículo"""
        return [r for r in self.rutas_estado 
                if r.is_accessible_for_vehicle(vehicle_type)]
    
    def get_supply_category(self, categoria: str) -> SupplyCategory:
        """Obtener categoría de insumo por nombre"""
        for cat in self.categorias_insumos:
            if cat.categoria == categoria:
                return cat
        raise ValueError(f"Categoría no encontrada: {categoria}")