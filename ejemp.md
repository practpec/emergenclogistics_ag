Te explico las partes principales del servicio de Algoritmo Genético (AG) para optimización logística de emergencia:

## **Objetivo del Sistema**

El AG busca **optimizar la distribución de ayuda humanitaria** encontrando la mejor asignación de:
- **Vehículos** → **Destinos** → **Insumos**

Maximizando cobertura poblacional y eficiencia, minimizando duplicados y sobrecarga.



## **Estructuras de Datos Principales**

### **1. Individual (Solución)**
```python
@dataclass
class Individual:
    vehiculos: List[VehicleAssignment]  # Lista de asignaciones
    fitness: float = 0.0                # Calidad de la solución
```

### **2. VehicleAssignment (Asignación)**
```python
@dataclass
class VehicleAssignment:
    vehiculo_id: int           # ID del vehículo
    id_destino_ruta: int      # ID de ruta/destino
    insumos: List[int]        # [cantidad_insumo1, cantidad_insumo2, ...]
```


## **Flujo Principal**

1. **Inicialización**: Crea población diversa
2. **Evaluación**:
3. **Evolución**: Cruza, muta y selecciona mejores soluciones
4. **Reparación**: Asegura que todos los vehiculos, esten en cada individuo


## **Problema Core que Resuelve**

- **Entrada**: N vehículos, M destinos, K tipos de insumos
- **Restricciones**: Capacidad vehicular, rutas disponibles, rutas que permiten ciertis tipos de vehiculos, verificar que todas los destinos sean cubiertos(a menos que exisatan mas destioc que ehiuclos porque un vehiculo solo puede ir a un destinos)
