from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Vehicle:
    """Modelo de vehículo"""
    id: int
    modelo: str
    tipo: str
    velocidad_kmh: float
    consumo_litros_km: float
    maximo_peso_ton: float
    
    @property
    def capacidad_kg(self) -> float:
        """Capacidad en kilogramos"""
        return self.maximo_peso_ton * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'vehiculo_id': self.id,
            'modelo': self.modelo,
            'tipo': self.tipo,
            'velocidad_kmh': self.velocidad_kmh,
            'consumo_litros_km': self.consumo_litros_km,
            'maximo_peso_ton': self.maximo_peso_ton,
            'capacidad_kg': self.capacidad_kg
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vehicle':
        """Crear desde diccionario"""
        return cls(
            id=data['id'],
            modelo=data['modelo'],
            tipo=data['tipo'],
            velocidad_kmh=data['velocidad_kmh'],
            consumo_litros_km=data['consumo_litros_km'],
            maximo_peso_ton=data['maximo_peso_ton']
        )
    
    def can_carry_weight(self, weight_kg: float) -> bool:
        """Verificar si puede cargar determinado peso"""
        return weight_kg <= self.capacidad_kg
    
    def calculate_fuel_consumption(self, distance_km: float) -> float:
        """Calcular consumo de combustible para una distancia"""
        return distance_km * self.consumo_litros_km
    
    def calculate_travel_time(self, distance_km: float) -> float:
        """Calcular tiempo de viaje en horas"""
        return distance_km / self.velocidad_kmh