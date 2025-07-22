from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .vehicle import Vehicle
from .disaster import Disaster, SupplyCategory
from .route import RouteState

@dataclass
class ScenarioStatistics:
    """Estadísticas del escenario con soporte para datos reales"""
    total_destinos: int
    total_rutas: int
    rutas_abiertas: int
    rutas_cerradas: int
    total_vehiculos: int
    poblacion_total_destinos: int = 0
    usando_datos_reales: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_destinos': self.total_destinos,
            'total_rutas': self.total_rutas,
            'rutas_abiertas': self.rutas_abiertas,
            'rutas_cerradas': self.rutas_cerradas,
            'total_vehiculos': self.total_vehiculos,
            'poblacion_total_destinos': self.poblacion_total_destinos,
            'usando_datos_reales': self.usando_datos_reales,
            'porcentaje_rutas_abiertas': round((self.rutas_abiertas / self.total_rutas * 100) if self.total_rutas > 0 else 0, 1),
            'poblacion_promedio_destino': round(self.poblacion_total_destinos / self.total_destinos) if self.total_destinos > 0 else 0
        }

@dataclass
class Scenario:
    """Modelo completo de escenario con soporte para datos reales de localidades"""
    punto_partida: str
    tipo_desastre: str
    desastre_detalles: Disaster
    vehiculos_disponibles: List[Vehicle]
    destinos_rutas: List[List[Dict]]  # Estructura anidada del JSON original
    rutas_estado: List[RouteState]
    categorias_insumos: List[SupplyCategory]
    estadisticas: ScenarioStatistics
    metadata: Dict[str, Any] = field(default_factory=dict)
    
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
            'estadisticas': self.estadisticas.to_dict(),
            'metadata': {
                **self.metadata,
                'usando_datos_reales': True,
                'version_esquema': '2.0',
                'fuente_datos': 'INEGI_localidades'
            }
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
            total_vehiculos=stats_data['total_vehiculos'],
            poblacion_total_destinos=stats_data.get('poblacion_total_destinos', 0),
            usando_datos_reales=stats_data.get('usando_datos_reales', True)
        )
        
        return cls(
            punto_partida=data['punto_partida'],
            tipo_desastre=data['tipo_desastre'],
            desastre_detalles=desastre,
            vehiculos_disponibles=vehiculos,
            destinos_rutas=data['destinos_rutas'],
            rutas_estado=rutas_estado,
            categorias_insumos=categorias,
            estadisticas=estadisticas,
            metadata=data.get('metadata', {})
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
    
    def get_destinos_by_population(self, min_population: int = 0) -> List[Dict]:
        """Obtener destinos filtrados por población mínima"""
        destinos_filtrados = []
        
        for destino_lista in self.destinos_rutas:
            for destino in destino_lista:
                poblacion = destino.get('poblacion_destino', 0)
                if poblacion >= min_population:
                    destinos_filtrados.append(destino)
        
        # Ordenar por población descendente
        return sorted(destinos_filtrados, key=lambda x: x.get('poblacion_destino', 0), reverse=True)
    
    def get_localidades_info(self) -> List[Dict[str, Any]]:
        """Obtener información detallada de todas las localidades del escenario"""
        localidades = []
        
        for destino_lista in self.destinos_rutas:
            for destino in destino_lista:
                if 'localidad_info' in destino:
                    localidades.append({
                        'nombre': destino['localidad_info']['nombre_completo'],
                        'clave_estado': destino['localidad_info']['clave_estado'],
                        'clave_municipio': destino['localidad_info']['clave_municipio'],
                        'clave_localidad': destino['localidad_info']['clave_localidad'],
                        'poblacion': destino.get('poblacion_destino', 0),
                        'distancia_km': destino.get('distancia_km', 0),
                        'coordenadas': destino.get('coordenadas', {}),
                        'rutas_disponibles': len([r for r in self.rutas_estado 
                                                if destino['destino'] in r.destino and r.estado == 'abierta'])
                    })
        
        return localidades
    
    def get_coverage_analysis(self) -> Dict[str, Any]:
        """Análisis de cobertura del escenario"""
        localidades = self.get_localidades_info()
        total_poblacion = sum(loc['poblacion'] for loc in localidades)
        
        rutas_disponibles = len(self.get_available_routes())
        cobertura_poblacional = total_poblacion / len(localidades) if localidades else 0
        
        return {
            'total_localidades': len(localidades),
            'poblacion_total': total_poblacion,
            'poblacion_promedio': round(cobertura_poblacional),
            'rutas_operativas': rutas_disponibles,
            'porcentaje_conectividad': round((rutas_disponibles / self.estadisticas.total_rutas * 100) if self.estadisticas.total_rutas > 0 else 0, 1),
            'localidad_mayor_poblacion': max(localidades, key=lambda x: x['poblacion'])['nombre'] if localidades else None,
            'localidad_mas_lejana': max(localidades, key=lambda x: x['distancia_km'])['nombre'] if localidades else None,
            'distancia_maxima': max(localidades, key=lambda x: x['distancia_km'])['distancia_km'] if localidades else 0
        }
    
    def validate_scenario_integrity(self) -> Dict[str, Any]:
        """Validar integridad del escenario con datos reales"""
        issues = []
        warnings = []
        
        # Validar que hay localidades reales
        localidades = self.get_localidades_info()
        if not localidades:
            issues.append("No hay localidades con información real")
        
        # Validar coordenadas
        for loc in localidades:
            coords = loc.get('coordenadas', {})
            if not coords.get('lat') or not coords.get('lng'):
                issues.append(f"Localidad {loc['nombre']} sin coordenadas válidas")
        
        # Validar rutas disponibles
        rutas_abiertas = len(self.get_available_routes())
        if rutas_abiertas == 0:
            issues.append("No hay rutas disponibles para distribución")
        elif rutas_abiertas < len(localidades) * 0.5:
            warnings.append("Menos del 50% de las rutas están disponibles")
        
        # Validar vehículos vs rutas
        tipos_vehiculos = set(v.tipo for v in self.vehiculos_disponibles)
        rutas_sin_vehiculos = []
        
        for ruta in self.rutas_estado:
            if ruta.estado == 'abierta':
                vehiculos_compatibles = set(ruta.vehiculos_permitidos).intersection(tipos_vehiculos)
                if not vehiculos_compatibles:
                    rutas_sin_vehiculos.append(ruta.destino)
        
        if rutas_sin_vehiculos:
            warnings.append(f"Rutas sin vehículos compatibles: {len(rutas_sin_vehiculos)}")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_checks': len(localidades) + len(self.rutas_estado) + len(self.vehiculos_disponibles),
            'usando_datos_reales': self.estadisticas.usando_datos_reales
        }