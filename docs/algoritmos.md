# Algoritmos y Fórmulas

## Generación de Rutas

### Algoritmo de Selección de Destinos

El sistema utiliza un algoritmo híbrido que combina factores geográficos y demográficos para seleccionar destinos óptimos:

```python
def seleccionar_destinos(estado, n_destinos, municipio=None):
    """
    Selecciona destinos basándose en:
    - Distribución geográfica equilibrada
    - Priorización por población
    - Evitar agrupaciones excesivas
    """
    
    # Consulta base de localidades INEGI
    localidades = obtener_localidades(estado, municipio)
    
    # Aplicar filtros de población mínima
    localidades_filtradas = filtrar_por_poblacion(localidades, min_poblacion=500)
    
    # Algoritmo de selección distribuida
    destinos_seleccionados = []
    
    while len(destinos_seleccionados) < n_destinos:
        candidato = seleccionar_candidato_optimo(
            localidades_filtradas, 
            destinos_seleccionados
        )
        destinos_seleccionados.append(candidato)
        
    return destinos_seleccionados
```

### Función de Scoring para Candidatos

```python
def calcular_score_candidato(candidato, destinos_existentes):
    """
    Score = w1*población + w2*distancia_minima + w3*distribucion
    """
    
    # Componente poblacional (normalizado)
    score_poblacion = math.log(candidato['poblacion'] + 1) / 10
    
    # Componente de distancia mínima a destinos existentes
    if destinos_existentes:
        distancias = [
            calcular_distancia_haversine(candidato, destino) 
            for destino in destinos_existentes
        ]
        distancia_minima = min(distancias)
        score_distancia = min(distancia_minima / 50, 5)  # Cap a 5
    else:
        score_distancia = 5
    
    # Componente de distribución geográfica
    score_distribucion = evaluar_distribucion_geografica(candidato, destinos_existentes)
    
    # Pesos configurables
    w1, w2, w3 = 0.4, 0.4, 0.2
    
    return w1 * score_poblacion + w2 * score_distancia + w3 * score_distribucion
```

## Cálculo de Distancias

### Fórmula de Haversine

Para calcular distancias entre coordenadas geográficas:

```python
import math

def calcular_distancia_haversine(punto1, punto2):
    """
    Calcula la distancia ortodrómica entre dos puntos en la superficie terrestre
    
    Fórmula de Haversine:
    a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
    c = 2 ⋅ atan2(√a, √(1−a))
    d = R ⋅ c
    
    donde:
    φ = latitud, λ = longitud, R = radio terrestre
    """
    
    R = 6371.0  # Radio de la Tierra en kilómetros
    
    # Convertir coordenadas a radianes
    lat1_rad = math.radians(punto1['latitud'])
    lon1_rad = math.radians(punto1['longitud'])
    lat2_rad = math.radians(punto2['latitud'])
    lon2_rad = math.radians(punto2['longitud'])
    
    # Diferencias
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Aplicar fórmula de Haversine
    a = (math.sin(dlat / 2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(dlon / 2)**2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distancia_km = R * c
    
    return distancia_km
```

### Estimación de Tiempo de Viaje

```python
def estimar_tiempo_viaje(distancia_km, tipo_vehiculo, tipo_terreno="mixto"):
    """
    Estima tiempo de viaje considerando:
    - Tipo de vehículo
    - Condiciones del terreno
    - Factores de tráfico y logística
    """
    
    # Velocidades promedio por tipo de vehículo (km/h)
    velocidades_base = {
        'camion_grande': 45,
        'camion_mediano': 55,
        'camioneta': 65,
        'vehiculo_especial': 40
    }
    
    # Factores de terreno
    factores_terreno = {
        'urbano': 0.7,      # Tráfico denso
        'carretera': 1.0,   # Condiciones normales
        'rural': 0.8,       # Caminos secundarios
        'mixto': 0.85       # Combinación típica
    }
    
    velocidad_efectiva = (velocidades_base[tipo_vehiculo] * 
                         factores_terreno[tipo_terreno])
    
    tiempo_horas = distancia_km / velocidad_efectiva
    
    # Agregar tiempo de carga/descarga (30 min por parada)
    tiempo_logistico = 0.5
    
    return tiempo_horas + tiempo_logistico
```

## Algoritmo de Distribución Geográfica

### K-means Adaptado para Distribución Equilibrada

```python
def distribuir_geograficamente(localidades, n_clusters):
    """
    Adapta K-means para asegurar distribución geográfica equilibrada
    considerando población como peso
    """
    
    # Preparar datos ponderados por población
    puntos_ponderados = []
    for loc in localidades:
        peso = math.log(loc['poblacion'] + 1)  # Suavizar extremos
        for _ in range(int(peso)):
            puntos_ponderados.append([loc['latitud'], loc['longitud']])
    
    # Aplicar K-means con inicialización inteligente
    from sklearn.cluster import KMeans
    
    kmeans = KMeans(
        n_clusters=n_clusters,
        init='k-means++',
        n_init=10,
        random_state=42
    )
    
    clusters = kmeans.fit(puntos_ponderados)
    
    # Seleccionar representante más poblado de cada cluster
    destinos_finales = []
    for i in range(n_clusters):
        localidades_cluster = [
            loc for j, loc in enumerate(localidades)
            if asignar_a_cluster(loc, clusters.cluster_centers_) == i
        ]
        
        if localidades_cluster:
            mejor_representante = max(
                localidades_cluster, 
                key=lambda x: x['poblacion']
            )
            destinos_finales.append(mejor_representante)
    
    return destinos_finales
```

## Optimización de Recursos

### Función de Aptitud para Asignación de Vehículos

```python
def calcular_aptitud_asignacion(asignacion, datos_escenario):
    """
    Función de aptitud que evalúa la calidad de una asignación de recursos:
    
    F(x) = w1*cobertura + w2*eficiencia - w3*penalizaciones
    
    donde:
    - cobertura: porcentaje de demanda satisfecha
    - eficiencia: utilización óptima de capacidad vehicular
    - penalizaciones: violaciones de restricciones
    """
    
    cobertura = calcular_cobertura_demanda(asignacion, datos_escenario)
    eficiencia = calcular_eficiencia_vehicular(asignacion)
    penalizaciones = calcular_penalizaciones(asignacion, datos_escenario)
    
    # Pesos ajustables según prioridades del escenario
    w1, w2, w3 = 0.5, 0.3, 0.2
    
    aptitud = w1 * cobertura + w2 * eficiencia - w3 * penalizaciones
    
    return max(0, aptitud)  # Asegurar que la aptitud no sea negativa
```

### Cálculo de Cobertura de Demanda

```python
def calcular_cobertura_demanda(asignacion, datos_escenario):
    """
    Calcula qué porcentaje de la demanda total es satisfecha
    """
    
    demanda_total = sum(
        destino['demanda_total'] 
        for destino in datos_escenario['destinos']
    )
    
    suministro_total = 0
    
    for vehiculo_id, rutas in asignacion.items():
        vehiculo = datos_escenario['vehiculos'][vehiculo_id]
        
        for ruta in rutas:
            carga_util = min(
                sum(ruta['insumos']),
                vehiculo['capacidad_kg']
            )
            suministro_total += carga_util
    
    cobertura = min(suministro_total / demanda_total, 1.0)
    
    return cobertura
```

### Cálculo de Eficiencia Vehicular

```python
def calcular_eficiencia_vehicular(asignacion):
    """
    Mide qué tan bien se utiliza la capacidad de los vehículos
    """
    
    eficiencias = []
    
    for vehiculo_id, rutas in asignacion.items():
        vehiculo = obtener_vehiculo(vehiculo_id)
        capacidad_total = vehiculo['capacidad_kg']
        
        for ruta in rutas:
            peso_carga = sum(ruta['insumos'])
            eficiencia_ruta = peso_carga / capacidad_total
            eficiencias.append(min(eficiencia_ruta, 1.0))
    
    return sum(eficiencias) / len(eficiencias) if eficiencias else 0
```

## Validación de Restricciones

### Restricciones de Capacidad

```python
def validar_restriccion_capacidad(vehiculo, carga_asignada):
    """
    Valida que la carga no exceda la capacidad del vehículo
    
    Margen de tolerancia: 5% para considerar variaciones reales
    """
    
    peso_total = sum(
        cantidad * obtener_peso_insumo(tipo_insumo)
        for tipo_insumo, cantidad in carga_asignada.items()
    )
    
    capacidad_maxima = vehiculo['capacidad_kg'] * 1.05  # Tolerancia 5%
    
    return peso_total <= capacidad_maxima
```

### Restricciones de Compatibilidad de Rutas

```python
def validar_compatibilidad_ruta(vehiculo, ruta, estado_rutas):
    """
    Valida que el vehículo pueda acceder a la ruta específica
    """
    
    ruta_info = estado_rutas.get(ruta['id'])
    
    if not ruta_info:
        return False
    
    # Verificar si la ruta está abierta
    if ruta_info['estado'] != 'abierta':
        return False
    
    # Verificar compatibilidad del tipo de vehículo
    if vehiculo['tipo'] not in ruta_info['vehiculos_permitidos']:
        return False
    
    return True
```

## Métricas de Rendimiento

### Tiempo de Convergencia

```python
def medir_convergencia(historial_aptitud, ventana=10, umbral=0.01):
    """
    Determina si el algoritmo ha convergido basándose en:
    - Estabilidad de la función de aptitud
    - Ventana deslizante de observación
    """
    
    if len(historial_aptitud) < ventana * 2:
        return False
    
    valores_recientes = historial_aptitud[-ventana:]
    valores_anteriores = historial_aptitud[-ventana*2:-ventana]
    
    mejora_promedio = (
        sum(valores_recientes) / len(valores_recientes) -
        sum(valores_anteriores) / len(valores_anteriores)
    )
    
    return abs(mejora_promedio) < umbral
```

### Diversidad de Población

```python
def calcular_diversidad_poblacion(poblacion):
    """
    Mide la diversidad genética de la población para evitar convergencia prematura
    """
    
    distancias = []
    n = len(poblacion)
    
    for i in range(n):
        for j in range(i + 1, n):
            distancia = calcular_distancia_hamming(poblacion[i], poblacion[j])
            distancias.append(distancia)
    
    diversidad = sum(distancias) / len(distancias) if distancias else 0
    
    return diversidad / max(len(poblacion[0]), 1)  # Normalizar
```