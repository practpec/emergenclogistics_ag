from dataclasses import dataclass
from typing import List

@dataclass
class VehicleAssignment:
    """Asignación individual de vehículo"""
    vehiculo_id: int
    id_destino_ruta: int
    insumos: List[int]  # Cantidades de cada tipo de insumo

@dataclass
class Individual:
    """Individuo del algoritmo genético"""
    vehiculos: List[VehicleAssignment]
    fitness: float = 0.0