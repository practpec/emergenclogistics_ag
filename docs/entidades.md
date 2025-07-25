# Estructura de Entidades

## Modelos de Datos Principales

### Vehicle (Vehículo)

Representa los vehículos disponibles para distribución de ayuda humanitaria.

```python
@dataclass
class Vehicle:
    id_vehiculo: int
    nombre: str
    tipo: str
    capacidad_kg: int
    velocidad_promedio_kmh: int
    costo_operacion_por_km: float
    disponible: bool = True
    especificaciones: Dict[str, Any] = field(default_factory=dict)
```

#### Tipos de Vehículos Soportados

| Tipo | Capacidad (kg) | Velocidad (km/h) | Uso Recomendado |
|------|----------------|------------------|-----------------|
| `camion_grande` | 10,000 - 25,000 | 45 | Suministros masivos, rutas principales |
| `camion_mediano` | 5,000 - 10,000 | 55 | Distribución urbana/semiurbana |
| `camioneta` | 1,000 - 3,000 | 65 | Comunidades rurales, acceso difícil |
| `vehiculo_especial` | Variable | 40 | Emergencias, terreno extremo |

#### Especificaciones Adicionales

```python
especificaciones_ejemplo = {
    "combustible": "diesel",
    "traccion": "4x4",
    "refrigeracion": True,
    "equipamiento_especial": ["grua", "equipo_medico"],
    "restricciones_terreno": ["urbano", "rural", "montañoso"]
}
```

### Disaster (Tipo de Desastre)

Define los diferentes tipos de emergencias y sus características específicas.

```python
@dataclass
class Disaster:
    tipo: str
    descripcion: str
    prioridades_insumos: List[str]
    factor_urgencia: float
    restricciones_acceso: List[str]
    tiempo_respuesta_critico_horas: int
```

#### Tipos de Desastres Configurados

```python
desastres_disponibles = {
    "terremoto": {
        "descripcion": "Sismo de gran magnitud con daños estructurales",
        "prioridades_insumos": ["alimentos", "agua", "medicinas", "refugio"],
        "factor_urgencia": 0.9,
        "tiempo_respuesta_critico": 72
    },
    "huracan": {
        "descripcion": "Huracán con vientos y lluvias intensas",
        "prioridades_insumos": ["agua", "alimentos", "energia", "comunicaciones"],
        "factor_urgencia": 0.8,
        "tiempo_respuesta_critico": 48
    },
    "inundacion": {
        "descripcion": "Desbordamiento de ríos o lluvias torrenciales",
        "prioridades_insumos": ["agua_potable", "alimentos", "medicinas", "refugio"],
        "factor_urgencia": 0.7,
        "tiempo_respuesta_critico": 96
    }
}
```

### SupplyCategory (Categoría de Insumos)

Clasifica los diferentes tipos de suministros de ayuda humanitaria.

```python
@dataclass
class SupplyCategory:
    id_categoria: int
    nombre: str
    peso_unitario_kg: float
    volumen_unitario_m3: float
    prioridad_base: int
    perecedero: bool
    requisitos_almacenamiento: List[str]
```

#### Categorías de Insumos Disponibles

| Categoría | Peso Unit. (kg) | Volumen Unit. (m³) | Prioridad | Perecedero |
|-----------|----------------|-------------------|-----------|------------|
| `agua_potable` | 1.0 | 0.001 | 1 | No |
| `alimentos_no_perecederos` | 0.5 | 0.0008 | 2 | No |
| `alimentos_perecederos` | 0.5 | 0.0008 | 2 | Sí |
| `medicinas_basicas` | 0.1 | 0.0002 | 1 | Sí |
| `medicinas_especializadas` | 0.1 | 0.0002 | 1 | Sí |
| `ropa_abrigo` | 0.8 | 0.005 | 3 | No |
| `productos_higiene` | 0.3 | 0.0004 | 3 | No |
| `herramientas_rescate` | 2.0 | 0.002 | 2 | No |
| `material_construccion` | 25.0 | 0.02 | 4 | No |
| `combustible` | 0.8 | 0.001 | 2 | No |

#### Requisitos de Almacenamiento

```python
requisitos_almacenamiento = {
    "medicinas_especializadas": ["refrigeracion", "control_humedad", "proteccion_luz"],
    "alimentos_perecederos": ["refrigeracion", "ventilacion"],
    "combustible": ["contenedor_especial", "ventilacion", "alejado_fuego"],
    "agua_potable": ["contenedor_limpio", "proteccion_contaminacion"]
}
```

### RouteState (Estado de Ruta)

Gestiona el estado y accesibilidad de las rutas hacia destinos específicos.

```python
@dataclass
class RouteState:
    id_ruta: str
    destino_id: str
    estado: str  # 'abierta', 'cerrada', 'restringida'
    vehiculos_permitidos: List[str]
    restricciones_peso: Optional[int]
    tiempo_estimado_horas: float
    observaciones: str = ""
```

#### Estados de Ruta Posibles

```python
estados_ruta = {
    "abierta": {
        "descripcion": "Ruta completamente accesible",
        "restricciones": []
    },
    "cerrada": {
        "descripcion": "Ruta bloqueada o inaccesible",
        "restricciones": ["acceso_bloqueado"]
    },
    "restringida": {
        "descripcion": "Acceso limitado por condiciones específicas",
        "restricciones": ["peso_limitado", "vehiculos_especificos", "horario_limitado"]
    }
}
```

### Scenario (Escenario de Emergencia)

Modelo principal que encapsula toda la información de un escenario de distribución.

```python
@dataclass
class Scenario:
    punto_partida: str
    tipo_desastre: str
    desastre_detalles: Disaster
    vehiculos_disponibles: List[Vehicle]
    destinos_rutas: List[List[Dict]]
    rutas_estado: List[RouteState]
    categorias_insumos: List[SupplyCategory]
    estadisticas: ScenarioStatistics
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### ScenarioStatistics (Estadísticas del Escenario)

Proporciona métricas y estadísticas calculadas del escenario.

```python
@dataclass
class ScenarioStatistics:
    total_destinos: int
    total_rutas: int
    rutas_abiertas: int
    rutas_cerradas: int
    total_vehiculos: int
    poblacion_total_destinos: int = 0
    usando_datos_reales: bool = True
```

#### Métricas Calculadas

```python
def calcular_metricas_adicionales(estadisticas):
    return {
        'porcentaje_rutas_abiertas': round(
            (estadisticas.rutas_abiertas / estadisticas.total_rutas * 100) 
            if estadisticas.total_rutas > 0 else 0, 1
        ),
        'poblacion_promedio_destino': round(
            estadisticas.poblacion_total_destinos / estadisticas.total_destinos
        ) if estadisticas.total_destinos > 0 else 0,
        'densidad_vehicular': round(
            estadisticas.total_vehiculos / estadisticas.total_destinos, 2
        ) if estadisticas.total_destinos > 0 else 0
    }
```

## Validaciones de Entidades

### Validación de Vehículos

```python
def validar_vehiculo(vehiculo: Vehicle) -> List[str]:
    errores = []
    
    if vehiculo.capacidad_kg <= 0:
        errores.append("Capacidad debe ser mayor a 0")
    
    if vehiculo.velocidad_promedio_kmh <= 0:
        errores.append("Velocidad debe ser mayor a 0")
    
    if vehiculo.costo_operacion_por_km < 0:
        errores.append("Costo de operación no puede ser negativo")
    
    tipos_validos = ['camion_grande', 'camion_mediano', 'camioneta', 'vehiculo_especial']
    if vehiculo.tipo not in tipos_validos:
        errores.append(f"Tipo de vehículo debe ser uno de: {tipos_validos}")
    
    return errores
```

### Validación de Compatibilidad

```python
def validar_compatibilidad_insumo_vehiculo(insumo: SupplyCategory, 
                                         vehiculo: Vehicle, 
                                         cantidad: int) -> bool:
    # Validar peso total
    peso_total = insumo.peso_unitario_kg * cantidad
    if peso_total > vehiculo.capacidad_kg:
        return False
    
    # Validar requisitos especiales
    if insumo.requisitos_almacenamiento:
        for requisito in insumo.requisitos_almacenamiento:
            if requisito == "refrigeracion":
                if not vehiculo.especificaciones.get("refrigeracion", False):
                    return False
    
    return True
```

## Relaciones Entre Entidades

### Diagrama de Relaciones

```
Scenario
├── Disaster (1:1)
├── Vehicle (1:N)
├── SupplyCategory (1:N)
├── RouteState (1:N)
└── ScenarioStatistics (1:1)

RouteState
├── Destino (1:1)
└── Vehicle (N:M) [a través de vehiculos_permitidos]

Vehicle
├── SupplyCategory (N:M) [a través de asignaciones]
└── RouteState (N:M) [a través de restricciones]
```

### Consultas Comunes

```python
# Obtener vehículos compatibles con una ruta específica
def obtener_vehiculos_compatibles(ruta: RouteState, 
                                vehiculos: List[Vehicle]) -> List[Vehicle]:
    return [
        v for v in vehiculos 
        if v.tipo in ruta.vehiculos_permitidos 
        and v.disponible
        and (not ruta.restricciones_peso or 
             v.capacidad_kg <= ruta.restricciones_peso)
    ]

# Calcular capacidad total disponible para un tipo de insumo
def calcular_capacidad_total(vehiculos: List[Vehicle], 
                           insumo: SupplyCategory) -> float:
    capacidad_total = 0
    for vehiculo in vehiculos:
        if vehiculo.disponible:
            unidades_maximas = vehiculo.capacidad_kg / insumo.peso_unitario_kg
            capacidad_total += unidades_maximas
    return capacidad_total
```

## Serialización y Persistencia

### Conversión a JSON

```python
def scenario_to_json(scenario: Scenario) -> str:
    scenario_dict = {
        'punto_partida': scenario.punto_partida,
        'tipo_desastre': scenario.tipo_desastre,
        'desastre_detalles': asdict(scenario.desastre_detalles),
        'vehiculos_disponibles': [asdict(v) for v in scenario.vehiculos_disponibles],
        'destinos_rutas': scenario.destinos_rutas,
        'rutas_estado': [asdict(r) for r in scenario.rutas_estado],
        'categorias_insumos': [asdict(c) for c in scenario.categorias_insumos],
        'estadisticas': asdict(scenario.estadisticas),
        'metadata': scenario.metadata
    }
    return json.dumps(scenario_dict, indent=2, ensure_ascii=False)
```

### Carga desde JSON

```python
def scenario_from_json(json_str: str) -> Scenario:
    data = json.loads(json_str)
    
    return Scenario(
        punto_partida=data['punto_partida'],
        tipo_desastre=data['tipo_desastre'],
        desastre_detalles=Disaster(**data['desastre_detalles']),
        vehiculos_disponibles=[Vehicle(**v) for v in data['vehiculos_disponibles']],
        destinos_rutas=data['destinos_rutas'],
        rutas_estado=[RouteState(**r) for r in data['rutas_estado']],
        categorias_insumos=[SupplyCategory(**c) for c in data['categorias_insumos']],
        estadisticas=ScenarioStatistics(**data['estadisticas']),
        metadata=data.get('metadata', {})
    )
```