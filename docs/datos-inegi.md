# Datos del INEGI

## Descripción General

El sistema EmergenLogistics utiliza la base de datos oficial del **Instituto Nacional de Estadística y Geografía (INEGI)** para garantizar precisión geográfica y demográfica en la planificación de rutas de ayuda humanitaria.

## Fuente de Datos

**Catálogo Único de Claves de Áreas Geoestadísticas Estatales, Municipales y Localidades**
- Organismo: INEGI (Instituto Nacional de Estadística y Geografía)
- Actualización: Censos y conteos poblacionales oficiales
- Cobertura: Todo el territorio nacional mexicano
- Total de registros: ~170,000 localidades

## Estructura de la Base de Datos

### Tabla: `localidades`

| Campo       | Tipo    | Descripción                                    | Ejemplo             |
|-------------|---------|------------------------------------------------|---------------------|
| `estado`    | TEXT    | Nombre completo del estado                     | "Chiapas"           |
| `municipio` | TEXT    | Nombre completo del municipio                  | "Tuxtla Gutiérrez"  |
| `localidad` | TEXT    | Nombre de la localidad/comunidad               | "Copoya"            |
| `ambito`    | TEXT    | Clasificación urbana/rural                     | "URBANO" / "RURAL"  |
| `latitud`   | REAL    | Coordenada geográfica (grados decimales)       | 16.7569             |
| `longitud`  | REAL    | Coordenada geográfica (grados decimales)       | -93.0892            |
| `poblacion` | INTEGER | Número total de habitantes                      | 15847               |

## Ventajas de Usar Datos INEGI

### 1. Precisión Geográfica
- Coordenadas oficiales verificadas
- Eliminación de zonas inhabitables (ríos, montañas, reservas)
- Datos actualizados por censos nacionales

### 2. Información Demográfica
- Población real por localidad
- Clasificación urbana/rural para planificación logística
- Datos socioeconómicos implícitos

### 3. Cobertura Nacional Completa
- Desde grandes ciudades hasta pequeñas comunidades rurales
- Representación fidedigna del territorio mexicano
- Ideal para simulaciones de emergencias reales

## Clasificación por Ámbito

### Localidades Urbanas
- Población ≥ 2,500 habitantes
- Mayor densidad poblacional
- Mejor infraestructura de acceso
- Rutas principales pavimentadas

### Localidades Rurales  
- Población < 2,500 habitantes
- Acceso por caminos rurales o terracería
- Mayores desafíos logísticos
- Prioridad en emergencias

## Distribución Poblacional

### Rangos de Población
```
Megalópolis (>1M):      4 localidades
Metrópolis (500K-1M):   8 localidades  
Ciudades (100K-500K):   89 localidades
Medianas (50K-100K):    157 localidades
Pequeñas (10K-50K):     1,387 localidades
Rurales (<10K):         168,000+ localidades
```

### Estados con Mayor Número de Localidades
1. Oaxaca: ~10,500 localidades
2. Chiapas: ~8,900 localidades  
3. Veracruz: ~8,100 localidades
4. Puebla: ~6,800 localidades
5. Guerrero: ~6,200 localidades

## Uso en EmergenLogistics

### Generación de Escenarios
```python
# Selección de localidades por estado
SELECT * FROM localidades 
WHERE estado = 'Chiapas' 
AND poblacion > 1000
ORDER BY poblacion DESC
LIMIT 50
```

### Cálculo de Distancias
```python
# Fórmula de Haversine para distancia entre coordenadas
import math

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la Tierra en km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * 
         math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distancia = R * c
    
    return distancia
```

### Priorización por Población
```python
# Algoritmo de priorización en emergencias
def priorizar_destinos(localidades):
    peso_poblacion = 0.6
    peso_distancia = 0.4
    
    for localidad in localidades:
        score = (localidad['poblacion'] * peso_poblacion - 
                localidad['distancia_km'] * peso_distancia)
        localidad['prioridad'] = score
    
    return sorted(localidades, key=lambda x: x['prioridad'], reverse=True)
```

## Validación de Datos

### Controles de Calidad Implementados
- Verificación de coordenadas dentro del territorio nacional
- Validación de rangos poblacionales coherentes
- Eliminación de duplicados por nombre y coordenadas
- Verificación de existencia de estados y municipios

### Ejemplo de Validación
```python
def validar_coordenadas_mexico(lat, lon):
    """Verificar que las coordenadas estén dentro de México"""
    # Límites aproximados de México
    lat_min, lat_max = 14.5, 32.7
    lon_min, lon_max = -118.4, -86.7
    
    return (lat_min <= lat <= lat_max and 
            lon_min <= lon <= lon_max)
```

## Actualización de Datos

### Frecuencia
- Censos de Población y Vivienda: cada 10 años
- Conteos de Población y Vivienda: cada 5 años
- Actualizaciones menores: según necesidades específicas

### Proceso de Integración
1. Descarga de datos oficiales INEGI
2. Normalización de formatos
3. Validación geográfica y poblacional
4. Integración en base SQLite local
5. Pruebas de integridad

## Limitaciones y Consideraciones

### Limitaciones
- Datos poblacionales pueden estar desactualizados entre censos
- Coordenadas aproximadas para localidades muy pequeñas
- Cambios administrativos no reflejados inmediatamente

### Consideraciones Técnicas
- Base de datos SQLite para portabilidad
- Índices en campos frecuentemente consultados
- Backup automático antes de actualizaciones
- Validación de integridad referencial

## Referencias

- [INEGI - Catálogo Único de Claves](https://www.inegi.org.mx/app/ageeml/)
- [Marco Geoestadístico Nacional](https://www.inegi.org.mx/temas/mg/)
- [Metodología de Censos de Población](https://www.inegi.org.mx/programas/ccpv/2020/)