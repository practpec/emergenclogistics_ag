from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class EstadoRuta(str, Enum):
    ABIERTA = "abierta"
    CERRADA = "cerrada"


class NivelPrioridad(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


@dataclass
class Localidad:
    clave_localidad: str
    poblacion: int


@dataclass
class Ruta:
    id: int
    distancia_km: float
    localidad: Localidad
    estado: EstadoRuta
    vehiculos_permitidos: List[str]


@dataclass
class VehiculoBase:
    modelo: str
    tipo: str
    consumo_litros_km: float
    maximo_peso_ton: float


@dataclass
class VehiculoDisponible:
    vehiculo: VehiculoBase
    cantidad: int


@dataclass
class Insumo:
    id: int
    nombre: str
    categoria: str
    peso_kg: float


@dataclass
class PrioridadCategoria:
    categoria: str
    nivel: NivelPrioridad


@dataclass
class TipoDesastre:
    tipo: str
    prioridades: List[PrioridadCategoria]


@dataclass
class AsignacionVehiculo:
    vehiculo_id: int
    ruta_id: int
    insumos: List[int]
    peso_total_kg: float
    distancia_km: float
    combustible_usado: float


@dataclass
class ConfiguracionAG:
    poblacion_size: int = 50
    generaciones: int = 100
    prob_cruza: float = 0.8
    prob_mutacion: float = 0.1
    elitismo_rate: float = 0.1


@dataclass
class ScenarioData:
    rutas: List[Ruta]
    vehiculos_disponibles: List[VehiculoDisponible]
    tipo_desastre: TipoDesastre
    configuracion_ag: ConfiguracionAG


@dataclass
class ResultadoIndividuo:
    asignaciones: List[Dict[str, Any]]
    fitness: float
    rutas_utilizadas: int
    vehiculos_utilizados: int
    peso_total_transportado: float
    combustible_total: float


Individual = List[AsignacionVehiculo]
VehicleAssignment = AsignacionVehiculo