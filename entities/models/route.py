from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class RoutePoint:
    """Punto de una ruta"""
    lat: float
    lng: float
    
    def to_dict(self) -> Dict[str, float]:
        return {'lat': self.lat, 'lng': self.lng}

@dataclass
class Route:
    """Modelo de ruta"""
    id_destino_ruta: int
    origen: str
    destino: str
    distancia_km: float
    puntos_ruta: List[RoutePoint]
    tipo: str = "Ruta"
    descripcion: str = "Ruta hacia el destino"
    
    @property
    def distancia_metros(self) -> float:
        """Distancia en metros"""
        return self.distancia_km * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id_destino_ruta': self.id_destino_ruta,
            'origen': self.origen,
            'destino': self.destino,
            'distancia_km': self.distancia_km,
            'tipo': self.tipo,
            'descripcion': self.descripcion,
            'puntos_ruta': [punto.to_dict() for punto in self.puntos_ruta],
            'distancia': {
                'text': f"{self.distancia_km:.1f} km",
                'value': self.distancia_metros
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Route':
        """Crear desde diccionario"""
        puntos = []
        if 'puntos_ruta' in data:
            puntos = [RoutePoint(p['lat'], p['lng']) for p in data['puntos_ruta']]
        
        return cls(
            id_destino_ruta=data['id_destino_ruta'],
            origen=data['origen'],
            destino=data['destino'],
            distancia_km=data['distancia_km'],
            puntos_ruta=puntos,
            tipo=data.get('tipo', 'Ruta'),
            descripcion=data.get('descripcion', 'Ruta hacia el destino')
        )

@dataclass
class RouteState:
    """Estado de una ruta en el escenario"""
    id_destino_ruta: int
    estado: str  # abierta, cerrada
    vehiculos_permitidos: List[str]
    razon_bloqueo: Optional[str] = None
    destino: str = ""
    distancia_km: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id_destino_ruta': self.id_destino_ruta,
            'estado': self.estado,
            'vehiculos_permitidos': self.vehiculos_permitidos,
            'razon_bloqueo': self.razon_bloqueo,
            'destino': self.destino,
            'distancia_km': self.distancia_km
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RouteState':
        """Crear desde diccionario"""
        return cls(
            id_destino_ruta=data['id_destino_ruta'],
            estado=data['estado'],
            vehiculos_permitidos=data['vehiculos_permitidos'],
            razon_bloqueo=data.get('razon_bloqueo'),
            destino=data.get('destino', ''),
            distancia_km=data.get('distancia_km', 0.0)
        )
    
    def is_accessible_for_vehicle(self, vehicle_type: str) -> bool:
        """Verificar si la ruta es accesible para un tipo de vehículo"""
        return (self.estado == 'abierta' and 
                vehicle_type in self.vehiculos_permitidos)