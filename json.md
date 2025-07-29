Estructura General del JSON
El JSON está organizado en cinco objetos principales en el nivel raíz:

vehiculos

insumos

configuracion_escenario

desastre_seleccionado

estados_rutas

A continuación, se detalla la estructura de cada uno de estos objetos.

1. vehiculos
Este objeto es una lista (array) de vehículos. Cada elemento de la lista es un objeto que representa un vehículo y contiene las siguientes claves:

consumo_litros_km (Número): Eficiencia de combustible del vehículo en litros por kilómetro.

id (Número): Identificador único para el tipo de vehículo.

maximo_peso_ton (Número): Capacidad máxima de carga en toneladas.

modelo (Cadena de texto): Nombre del modelo del vehículo.

tipo (Cadena de texto): Categoría del vehículo (ej. "camioneta pickup", "camión ligero").

velocidad_kmh (Número): Velocidad promedio del vehículo en kilómetros por hora.

2. insumos
Este objeto es una lista (array) de suministros o insumos. Cada elemento de la lista es un objeto que representa un tipo de insumo y contiene las siguientes claves:

categoria (Cadena de texto): Grupo al que pertenece el insumo (ej. "Alimentación básica", "Higiene y cuidado personal").

id_insumo (Número): Identificador único para el insumo.

nombre (Cadena de texto): Nombre descriptivo del insumo.

peso_kg (Número): Peso del insumo en kilogramos.

3. configuracion_escenario
Este objeto define los parámetros para un escenario de desastre específico. Contiene:

tipo_desastre (Cadena de texto): El tipo de desastre simulado (ej. "inundación").

vehiculos_disponibles (Lista): Una lista de los vehículos específicos disponibles para este escenario, cada uno con:

modelo (Cadena de texto)

tipo (Cadena de texto)

cantidad (Número)

configuracion (Objeto): Parámetros para un algoritmo, posiblemente genético, para optimizar la distribución.

poblacion_size (Número): Tamaño de la población para el algoritmo.

generaciones (Número): Número de generaciones o iteraciones.

prob_cruza (Número): Probabilidad de cruce.

prob_mutacion (Número): Probabilidad de mutación.

elitismo_rate (Número): Tasa de elitismo.

4. desastre_seleccionado
Este objeto describe las características y prioridades del desastre actual. Contiene:

prioridades (Lista): Una lista que define la importancia de cada categoría de insumo para este desastre. Cada elemento tiene:

categoria (Cadena de texto)

nivel (Cadena de texto): Nivel de prioridad (ej. "alta", "media", "baja").

tipo (Cadena de texto): Repite el tipo de desastre.

5. estados_rutas
Este objeto contiene información sobre el estado de las diferentes rutas de acceso. Es un objeto donde cada clave es un número (como "0", "1", etc.) que probablemente representa un origen o un segmento de ruta. El valor asociado a cada clave es una lista de destinos posibles desde ese origen. Cada destino es un objeto con la siguiente estructura:

id (Número): Identificador único de la ruta.

distancia_km (Número): La distancia de la ruta en kilómetros.

clave_localidad (Número): Un identificador para la localidad de destino.

estado (Cadena de texto): Condición de la ruta (ej. "abierta").

vehiculos_permitidos (Lista): Una lista de los tipos de vehículos que pueden transitar por esa ruta.



Claro, aquí tienes la explicación de la estructura de este JSON, que está diseñado para describir rutas geográficas desde un punto de origen a varios destinos.

Estructura General del JSON
Este JSON se organiza en cinco objetos principales que describen un conjunto de rutas desde una localidad de origen hacia varias localidades de destino.

metadata

municipio_info

nodo_principal

nodos_secundarios

rutas_data

A continuación, se detalla la estructura de cada sección.

1. metadata
Este objeto contiene datos generales que resumen el contenido del archivo. Es una vista rápida de la información.

estado_origen (Cadena de texto): El nombre del estado donde se origina la ruta.

mismo_municipio (Booleano): Indica si el origen y los destinos están en el mismo municipio.

municipio_origen (Cadena de texto): La clave oficial del municipio de origen.

total_destinos (Número): El número total de localidades de destino.

total_rutas (Número): El número total de rutas calculadas.

usando_datos_reales (Booleano): Indica si la información se basa en datos reales.

2. municipio_info
Proporciona información específica del municipio de origen.

clave_municipio (Cadena de texto): La clave oficial del municipio.

nombre_municipio (Cadena de texto): El nombre completo del municipio.

total_localidades (Número): El número total de localidades que existen dentro de ese municipio.

3. nodo_principal
Este objeto representa el punto de partida o el origen de todas las rutas. 📍

ambito (Cadena de texto): Indica si la localidad es Urbana ('U') o Rural ('R').

clave_estado, clave_localidad, clave_municipio (Número): Claves geográficas oficiales para identificar la ubicación.

lat, lng (Número): Las coordenadas geográficas (latitud y longitud) del punto de origen.

nombre (Cadena de texto): Nombre completo y formal de la localidad de origen (Localidad, Municipio, Estado).

nombre_estado, nombre_localidad, nombre_municipio (Cadena de texto): Nombres desglosados de la ubicación.

poblacion (Cadena de texto): El número de habitantes en la localidad de origen.

4. nodos_secundarios
Es una lista (array) de objetos, donde cada objeto es un posible destino.

Contiene las mismas claves que el nodo_principal (clave_estado, lat, lng, nombre, poblacion, etc.).

distancia_directa (Número): La distancia en línea recta (aérea) desde el nodo_principal hasta este destino, generalmente en kilómetros.

5. rutas_data
Esta es la sección más detallada. Es una lista (array) donde cada elemento corresponde a un destino y contiene la información de la ruta terrestre para llegar a él. 🗺️

destino (Objeto): Contiene una copia completa de la información del nodo_secundario al que se dirige esta ruta.

indice (Número): Un identificador para la ruta.

rutas (Lista): Una lista que contiene los detalles de la ruta calculada.

descripcion (Cadena de texto): Breve descripción de la ruta.

distancia (Objeto): La distancia real por carretera.

text (Cadena de texto): La distancia en formato legible (ej. "8.0 km").

value (Número): La distancia en metros.

puntos_ruta (Lista): Una lista muy larga de coordenadas (lat, lng) que trazan el camino exacto de la ruta, punto por punto. Sirve para dibujar la ruta en un mapa.

tipo (Cadena de texto): Un identificador para el tipo de ruta (ej. "Ruta 1").




Este JSON es el resultado de un proceso de optimización logística, probablemente de un algoritmo genético. Muestra la solución óptima, alternativas y reportes de rendimiento para un plan de distribución de ayuda.

Estructura General del JSON
El archivo está organizado en cuatro secciones principales que presentan los resultados desde diferentes perspectivas:

alternativas

solucion_optima

reportes

visualizaciones

1. alternativas
Esta sección es una lista (array) que contiene varias de las mejores soluciones (o "individuos") encontradas por el algoritmo. Cada elemento de la lista es una alternativa de plan completo y tiene la siguiente estructura:

fitness (Número): Una puntuación que califica qué tan buena es la solución. Un valor más alto generalmente significa una mejor solución.

posicion (Número): El ranking de esta alternativa (1, 2, 3, etc.).

resumen (Objeto): Un resumen simple de la alternativa con el peso total movido y el número de rutas y vehículos usados.

asignaciones (Lista): Esta es la parte central de cada alternativa. Es una lista de viajes individuales o misiones, donde cada viaje es un objeto con:

vehiculo_id y ruta_id (Número): Identificadores que conectan con los datos de vehículos y rutas.

peso_total_kg, distancia_km, combustible_usado (Número): Métricas clave para ese viaje específico.

insumos_cantidades (Lista): Un desglose detallado de cada tipo de insumo (id_insumo) y la cantidad que se transporta en ese viaje.

2. solucion_optima
Este objeto representa la mejor solución encontrada por el algoritmo 🏆. Es el plan recomendado. Su estructura es casi idéntica a una de las alternativas, pero se presenta por separado para un acceso fácil.

fitness (Número): La puntuación más alta alcanzada.

asignaciones (Lista): La lista de viajes que componen el mejor plan logístico.

metricas (Objeto): Un resumen final de los totales para la solución óptima, como el combustible_total y peso_total.

3. reportes
Este objeto agrupa varias estadísticas y métricas de rendimiento que resumen todo el proceso. Se divide en tres sub-reportes:

eficiencia (Objeto): Contiene promedios de la operación, como el combustible, la distancia y el peso promedio por viaje.

escenario (Objeto): Mide el éxito del plan en el contexto del problema, indicando la cobertura de rutas, cuántos vehículos se usaron del total disponible, etc.

optimizacion (Objeto): Proporciona datos sobre el rendimiento del propio algoritmo, como el número de generaciones que se ejecutaron, el fitness final y la mejora total desde el inicio.

4. visualizaciones
Esta sección contiene datos pre-procesados y listos para generar gráficos y mapas. 📊

distribucion_carga (Objeto): Datos para analizar la eficiencia del uso de la capacidad de carga de los vehículos. Indica el peso transportado vs. la capacidad disponible y si hubo vehículos subutilizados o sobrecargados.

evolucion_fitness (Objeto): Contiene una lista (datos) con el mejor valor de fitness de cada generación del algoritmo. Es ideal para crear un gráfico de líneas que muestre cómo el algoritmo "aprendió" y mejoró la solución con el tiempo.

mapa_entregas (Objeto): Datos sencillos para visualizar en un mapa cuántas entregas fueron exitosas y cuántas fallaron.