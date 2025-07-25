# Creación de Escenarios de Emergencia

## Flujo de Creación de Escenarios

El sistema de creación de escenarios permite configurar emergencias humanitarias con parámetros específicos adaptados a diferentes tipos de desastres.

### 1. Selección de Tipo de Desastre

El sistema primero carga todos los tipos de desastre disponibles y sus características:

```python
def obtener_tipos_desastre():
    """Carga los tipos de desastre desde entities/data/desastres.json"""
    with open("entities/data/desastres.json", 'r', encoding='utf-8') as f:
        return json.load(f)

# Estructura de datos de desastre
desastre_ejemplo = {
    "tipo": "terremoto",
    "descripcion": "Sismo de gran magnitud con daños estructurales",
    "prioridades_insumos": ["agua", "medicinas", "alimentos", "refugio"],
    "factor_urgencia": 0.9,
    "tiempo_respuesta_critico_horas": 72,
    "restricciones_acceso": ["carreteras_dañadas", "puentes_colapsados"],
    "porcentaje_rutas_afectadas": 0.3
}
```

### 2. Carga de Vehículos Disponibles

El sistema obtiene la flota completa de vehículos disponibles:

```python
def obtener_vehiculos_disponibles():
    """Carga vehículos desde entities/data/vehiculos.json"""
    with open("entities/data/vehiculos.json", 'r', encoding='utf-8') as f:
        vehiculos = json.load(f)
    
    # Agregar disponibilidad por defecto
    for vehiculo in vehiculos:
        vehiculo['disponible'] = True
        vehiculo['cantidad_disponible'] = vehiculo.get('cantidad_disponible', 1)
    
    return vehiculos
```

### 3. Interfaz de Selección de Vehículos

La interfaz permite al usuario:
- Ver todos los vehículos disponibles
- Especificar cantidad de cada modelo
- Agregar vehículos personalizados

```javascript
// Estructura del formulario de vehículos
const FormularioVehiculos = {
  vehiculos_existentes: [
    {
      id_vehiculo: 1,
      cantidad_seleccionada: 2,
      maximo_disponible: 5
    }
  ],
  vehiculo_personalizado: {
    mostrar_formulario: false,
    datos: {
      nombre: "",
      tipo: "camion_mediano",
      capacidad_kg: 5000,
      velocidad_promedio_kmh: 55,
      costo_operacion_por_km: 2.0
    }
  }
}
```

### 4. Validación de Configuración

```python
def validar_configuracion_escenario(config):
    """Valida la configuración del escenario antes de crearlo"""
    errores = []
    
    # Validar punto de partida
    if not config.get('punto_partida'):
        errores.append("Punto de partida es requerido")
    
    # Validar tipo de desastre
    tipos_validos = [d['tipo'] for d in obtener_tipos_desastre()]
    if config.get('tipo_desastre') not in tipos_validos:
        errores.append(f"Tipo de desastre debe ser uno de: {tipos_validos}")
    
    # Validar vehículos seleccionados
    if not config.get('vehiculos_seleccionados'):
        errores.append("Debe seleccionar al menos un vehículo")
    
    for vehiculo_sel in config.get('vehiculos_seleccionados', []):
        if vehiculo_sel.get('cantidad', 0) <= 0:
            errores.append("Cantidad de vehículos debe ser mayor a 0")
    
    # Validar vehículo personalizado si existe
    if config.get('vehiculo_personalizado'):
        errores.extend(validar_vehiculo_personalizado(config['vehiculo_personalizado']))
    
    return errores

def validar_vehiculo_personalizado(vehiculo):
    """Valida los datos de un vehículo personalizado"""
    errores = []
    
    if not vehiculo.get('nombre'):
        errores.append("Nombre del vehículo personalizado es requerido")
    
    if vehiculo.get('capacidad_kg', 0) <= 0:
        errores.append("Capacidad del vehículo debe ser mayor a 0")
    
    if vehiculo.get('velocidad_promedio_kmh', 0) <= 0:
        errores.append("Velocidad del vehículo debe ser mayor a 0")
    
    tipos_validos = ['camion_grande', 'camion_mediano', 'camioneta', 'vehiculo_especial']
    if vehiculo.get('tipo') not in tipos_validos:
        errores.append(f"Tipo de vehículo debe ser uno de: {tipos_validos}")
    
    return errores
```

### 5. Procesamiento de Datos de Destinos

```python
def procesar_destinos_rutas(destinos_rutas_json, tipo_desastre):
    """Procesa los datos del mapa generado y aplica efectos del desastre"""
    
    # Obtener información del tipo de desastre
    desastre_info = next(
        (d for d in obtener_tipos_desastre() if d['tipo'] == tipo_desastre), 
        None
    )
    
    if not desastre_info:
        raise ValueError(f"Tipo de desastre '{tipo_desastre}' no encontrado")
    
    # Procesar destinos
    destinos_procesados = []
    rutas_estado = []
    
    for destino in destinos_rutas_json.get('destinos', []):
        # Calcular demanda basada en población y tipo de desastre
        demanda_base = calcular_demanda_por_poblacion(
            destino['poblacion'], 
            desastre_info['factor_urgencia']
        )
        
        destino_procesado = {
            **destino,
            'demanda_calculada': demanda_base,
            'prioridad': calcular_prioridad_destino(destino, desastre_info)
        }
        destinos_procesados.append(destino_procesado)
        
        # Generar estados de rutas para cada destino
        rutas_destino = generar_rutas_para_destino(
            destino, 
            desastre_info['porcentaje_rutas_afectadas']
        )
        rutas_estado.extend(rutas_destino)
    
    return destinos_procesados, rutas_estado

def calcular_demanda_por_poblacion(poblacion, factor_urgencia):
    """Calcula la demanda de insumos basada en población y urgencia"""
    
    # Fórmulas base por categoría de insumo
    formulas_demanda = {
        'agua_potable': lambda p: p * 3.0,  # 3L por persona por día
        'alimentos': lambda p: p * 0.5,     # 0.5kg por persona por día
        'medicinas': lambda p: p * 0.1,     # 0.1kg por persona
        'refugio': lambda p: p * 0.2,       # Material para 20% de población
        'higiene': lambda p: p * 0.05       # 0.05kg por persona
    }
    
    demanda = {}
    for categoria, formula in formulas_demanda.items():
        demanda[categoria] = formula(poblacion) * factor_urgencia
    
    return demanda

def calcular_prioridad_destino(destino, desastre_info):
    """Calcula la prioridad del destino basada en múltiples factores"""
    
    # Factores de priorización
    factor_poblacion = min(math.log(destino['poblacion'] + 1) / 10, 1.0)
    factor_distancia = max(0, 1 - (destino['distancia_desde_origen_km'] / 200))
    factor_urgencia = desastre_info['factor_urgencia']
    
    # Prioridad compuesta
    prioridad = (
        0.4 * factor_poblacion +
        0.3 * factor_distancia +
        0.3 * factor_urgencia
    )
    
    return round(prioridad, 3)

def generar_rutas_para_destino(destino, porcentaje_afectadas):
    """Genera múltiples rutas alternativas para un destino"""
    
    rutas = []
    num_rutas = 3  # Número estándar de rutas alternativas
    
    for i in range(num_rutas):
        # Determinar si la ruta está afectada por el desastre
        esta_afectada = random.random() < porcentaje_afectadas
        
        ruta = {
            'id_ruta': f"{destino['id']}-ruta-{i+1}",
            'destino_id': destino['id'],
            'estado': 'cerrada' if esta_afectada else 'abierta',
            'vehiculos_permitidos': determinar_vehiculos_permitidos(i, esta_afectada),
            'restricciones_peso': determinar_restricciones_peso(i, esta_afectada),
            'tiempo_estimado_horas': calcular_tiempo_estimado_ruta(destino, i, esta_afectada),
            'observaciones': generar_observaciones_ruta(i, esta_afectada)
        }
        
        rutas.append(ruta)
    
    return rutas

def determinar_vehiculos_permitidos(indice_ruta, esta_afectada):
    """Determina qué tipos de vehículos pueden usar cada ruta"""
    
    # Ruta principal (índice 0) - más restrictiva si está afectada
    if indice_ruta == 0:
        if esta_afectada:
            return ['vehiculo_especial']  # Solo vehículos especializados
        else:
            return ['camion_grande', 'camion_mediano', 'camioneta', 'vehiculo_especial']
    
    # Ruta secundaria (índice 1) - medianamente restrictiva
    elif indice_ruta == 1:
        if esta_afectada:
            return ['camioneta', 'vehiculo_especial']
        else:
            return ['camion_mediano', 'camioneta', 'vehiculo_especial']
    
    # Ruta terciaria (índice 2) - más restrictiva por defecto
    else:
        if esta_afectada:
            return []  # Ruta completamente bloqueada
        else:
            return ['camioneta', 'vehiculo_especial']

def determinar_restricciones_peso(indice_ruta, esta_afectada):
    """Determina restricciones de peso para cada ruta"""
    
    if esta_afectada:
        # Rutas afectadas tienen restricciones de peso más severas
        restricciones = [5000, 3000, 1000]  # kg
        return restricciones[min(indice_ruta, len(restricciones) - 1)]
    else:
        # Rutas normales sin restricciones especiales
        return None
```

### 6. Creación del Escenario Completo

```python
def crear_escenario_completo(configuracion):
    """Función principal que crea un escenario completo"""
    
    # Validar configuración
    errores = validar_configuracion_escenario(configuracion)
    if errores:
        raise ValueError(f"Configuración inválida: {'; '.join(errores)}")
    
    # Procesar vehículos
    vehiculos_finales = procesar_vehiculos_escenario(configuracion)
    
    # Procesar destinos y rutas
    destinos_procesados, rutas_estado = procesar_destinos_rutas(
        configuracion['destinos_rutas_json'],
        configuracion['tipo_desastre']
    )
    
    # Obtener información del desastre
    desastre_info = next(
        d for d in obtener_tipos_desastre() 
        if d['tipo'] == configuracion['tipo_desastre']
    )
    
    # Calcular estadísticas
    estadisticas = calcular_estadisticas_escenario(
        destinos_procesados, 
        rutas_estado, 
        vehiculos_finales
    )
    
    # Crear objeto escenario
    escenario = {
        'id_escenario': generar_id_escenario(),
        'punto_partida': configuracion['punto_partida'],
        'tipo_desastre': configuracion['tipo_desastre'],
        'desastre_detalles': desastre_info,
        'vehiculos_disponibles': vehiculos_finales,
        'destinos_rutas': convertir_a_estructura_anidada(destinos_procesados, rutas_estado),
        'rutas_estado': rutas_estado,
        'categorias_insumos': obtener_categorias_insumos(),
        'estadisticas': estadisticas,
        'metadata': {
            'fecha_creacion': datetime.now().isoformat(),
            'version_sistema': '1.0.0',
            'datos_inegi': True
        }
    }
    
    return escenario

def procesar_vehiculos_escenario(configuracion):
    """Procesa y valida los vehículos seleccionados para el escenario"""
    
    vehiculos_disponibles = obtener_vehiculos_disponibles()
    vehiculos_finales = []
    
    # Procesar vehículos existentes seleccionados
    for vehiculo_sel in configuracion.get('vehiculos_seleccionados', []):
        vehiculo_base = next(
            (v for v in vehiculos_disponibles if v['id_vehiculo'] == vehiculo_sel['id_vehiculo']),
            None
        )
        
        if not vehiculo_base:
            continue
        
        # Crear instancias múltiples según cantidad seleccionada
        for i in range(vehiculo_sel['cantidad']):
            vehiculo_instancia = {
                **vehiculo_base,
                'id_instancia': f"{vehiculo_base['id_vehiculo']}-{i+1}",
                'disponible': True
            }
            vehiculos_finales.append(vehiculo_instancia)
    
    # Agregar vehículo personalizado si existe
    if configuracion.get('vehiculo_personalizado'):
        vehiculo_personalizado = {
            **configuracion['vehiculo_personalizado'],
            'id_vehiculo': len(vehiculos_disponibles) + 1,
            'id_instancia': 'personalizado-1',
            'disponible': True,
            'personalizado': True
        }
        vehiculos_finales.append(vehiculo_personalizado)
    
    return vehiculos_finales

def convertir_a_estructura_anidada(destinos, rutas_estado):
    """Convierte destinos y rutas a la estructura anidada requerida"""
    
    estructura_anidada = []
    
    for destino in destinos:
        # Obtener rutas para este destino
        rutas_destino = [
            ruta for ruta in rutas_estado 
            if ruta['destino_id'] == destino['id']
        ]
        
        # Crear estructura anidada
        destino_con_rutas = {
            'destino': destino,
            'rutas': rutas_destino
        }
        
        estructura_anidada.append(destino_con_rutas)
    
    return estructura_anidada

def calcular_estadisticas_escenario(destinos, rutas_estado, vehiculos):
    """Calcula estadísticas del escenario creado"""
    
    rutas_abiertas = len([r for r in rutas_estado if r['estado'] == 'abierta'])
    rutas_cerradas = len([r for r in rutas_estado if r['estado'] == 'cerrada'])
    poblacion_total = sum(d['poblacion'] for d in destinos)
    
    return {
        'total_destinos': len(destinos),
        'total_rutas': len(rutas_estado),
        'rutas_abiertas': rutas_abiertas,
        'rutas_cerradas': rutas_cerradas,
        'total_vehiculos': len(vehiculos),
        'poblacion_total_destinos': poblacion_total,
        'usando_datos_reales': True,
        'porcentaje_rutas_abiertas': round(
            (rutas_abiertas / len(rutas_estado) * 100) if rutas_estado else 0, 1
        ),
        'poblacion_promedio_destino': round(
            poblacion_total / len(destinos)
        ) if destinos else 0
    }

def generar_id_escenario():
    """Genera un ID único para el escenario"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"escenario_{timestamp}"
```

### 7. Endpoint de Creación

```python
@bp_ag.route('/create-scenario', methods=['POST'])
def create_scenario():
    """Endpoint para crear un nuevo escenario de emergencia"""
    
    try:
        # Obtener datos de la solicitud
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos JSON requeridos'
            }), 400
        
        # Crear escenario
        escenario = crear_escenario_completo(data)
        
        # Guardar escenario (opcional - en memoria o base de datos)
        # guardar_escenario(escenario)
        
        return jsonify({
            'success': True,
            'data': escenario,
            'message': 'Escenario creado exitosamente'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'details': str(e)
        }), 500
```

### 8. Interfaz Frontend (Estructura)

```javascript
// Componente principal de creación de escenarios
const CrearEscenario = {
  state: {
    paso_actual: 1,  // 1: Desastre, 2: Vehículos, 3: Confirmación
    tipo_desastre_seleccionado: null,
    vehiculos_disponibles: [],
    vehiculos_seleccionados: [],
    vehiculo_personalizado: null,
    mapa_datos: null,
    escenario_creado: null
  },
  
  methods: {
    async cargarTiposDesastre() {
      const response = await fetch('/api/entities/disasters');
      return await response.json();
    },
    
    async cargarVehiculos() {
      const response = await fetch('/api/entities/vehicles');
      return await response.json();
    },
    
    async crearEscenario() {
      const configuracion = {
        punto_partida: this.state.mapa_datos.info_generacion.punto_partida.nombre,
        tipo_desastre: this.state.tipo_desastre_seleccionado,
        vehiculos_seleccionados: this.state.vehiculos_seleccionados,
        vehiculo_personalizado: this.state.vehiculo_personalizado,
        destinos_rutas_json: this.state.mapa_datos
      };
      
      const response = await fetch('/api/ag/create-scenario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configuracion)
      });
      
      return await response.json();
    }
  }
};
```

## Estado del Desarrollo

### Completado
- Carga de tipos de desastre desde JSON
- Carga de vehículos disponibles
- Validación de configuración de escenarios
- Procesamiento de destinos con datos INEGI
- Generación de rutas alternativas
- Cálculo de estadísticas de escenario
- Endpoint REST de creación

### Pendiente
- Algoritmo genético de optimización
- Interfaz frontend completa para creación
- Sistema de persistencia de escenarios
- Visualización de resultados
- Exportación de reportes

### Diferencias con Algoritmo Genético

El sistema de **creación de escenarios** es independiente del **algoritmo genético**:

- **Creación de escenarios**: Configura el problema (vehículos, destinos, restricciones)
- **Algoritmo genético**: Resuelve el problema de optimización de distribución

La separación permite:
1. Reutilizar escenarios para diferentes estrategias de optimización
2. Desarrollar cada módulo independientemente
3. Facilitar testing y validación por separado