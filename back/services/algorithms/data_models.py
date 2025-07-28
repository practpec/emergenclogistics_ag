from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class EstadoRuta(str, Enum):
    ABIERTA = "abierta"
    CERRADA = "cerrada"


class NivelPrioridad(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


@dataclass
class CategoriaInsumo:
    id: int
    nombre: str


@dataclass
class Insumo:
    id: int
    nombre: str
    categoria: CategoriaInsumo
    peso_kg: float


@dataclass
class Vehiculo:
    id: int
    modelo: str
    tipo: str
    velocidad_kmh: float
    consumo_litros_km: float
    maximo_peso_ton: float


@dataclass
class CategoriaPrioritaria:
    categoria: CategoriaInsumo
    nivel: NivelPrioridad


@dataclass
class Desastre:
    tipo: str
    prioridades: List[CategoriaPrioritaria]


@dataclass
class Localidad:
    id: int
    poblacion: int


@dataclass
class Ruta:
    id: int
    distancia_km: float
    localidad: Localidad
    estado: EstadoRuta
    vehiculos_permitidos: Optional[List[str]] = None


@dataclass
class VehiculoDisponible:
    modelo: str
    tipo: str
    cantidad: int


@dataclass
class ConfiguracionAG:
    poblacion_size: int
    generaciones: int
    prob_cruza: float
    prob_mutacion: float
    elitismo_rate: float


@dataclass
class ScenarioConfig:
    tipo_desastre: str
    vehiculos_disponibles: List[VehiculoDisponible]
    configuracion: ConfiguracionAG


@dataclass
class DatosRecibidos:
    rutas: List[Ruta]
    scenario_config: ScenarioConfig


@dataclass
class AsignacionVehiculo:
    vehiculo: Vehiculo
    ruta: Ruta
    insumos: List[Insumo]


@dataclass
class IndividuoAG:
    asignaciones: List[AsignacionVehiculo]
    fitness: Optional[float] = None
