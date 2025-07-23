from typing import List, Dict, Any
from .models import Individual

class ResultGenerator:
    """Generador de resultados y análisis del AG"""
    
    def __init__(self, vehiculos_disponibles: List[Dict], mapeo_asignaciones: List[Dict],
                 insumos_data: List[Dict], rutas_estado: Dict):
        self.vehiculos_disponibles = vehiculos_disponibles
        self.mapeo_asignaciones = mapeo_asignaciones
        self.insumos_data = insumos_data
        self.rutas_estado = rutas_estado
        self.num_insumos = len(insumos_data)

    def generar_resultado_final(self, mejor_individuo: Individual, historial: List[Dict], 
                               poblacion_final: List[Individual], parametros_ag: Dict) -> Dict[str, Any]:
        """Generar resultado final completo del algoritmo"""
        # Obtener los 3 mejores individuos
        top_3_individuos = sorted(poblacion_final, key=lambda x: x.fitness, reverse=True)[:3]
        
        # Procesar cada uno de los 3 mejores
        mejores_soluciones = []
        for i, individuo in enumerate(top_3_individuos):
            solucion_data = self._procesar_individuo(individuo, i + 1)
            mejores_soluciones.append(solucion_data)
        
        # Análisis comparativo de rendimiento
        analisis_rendimiento = self._generar_analisis_rendimiento(top_3_individuos)
        
        # Distribución de carga por vehículo
        distribucion_carga = self._generar_distribucion_carga(mejor_individuo)
        
        # Panel de control de simulación
        panel_control = self._generar_panel_control(mejor_individuo)
        
        # Análisis de rutas optimizadas
        rutas_optimizadas = self._generar_analisis_rutas(mejor_individuo)
        
        # Reportes de optimización
        reportes_optimizacion = self._generar_reportes_optimizacion(top_3_individuos, historial)
        
        return {
            'mejores_soluciones': mejores_soluciones,
            'analisis_rendimiento': analisis_rendimiento,
            'distribucion_carga': distribucion_carga,
            'panel_control': panel_control,
            'rutas_optimizadas': rutas_optimizadas,
            'reportes_optimizacion': reportes_optimizacion,
            'parametros_ag': parametros_ag,
            'evolucion_fitness': historial,
            'mapeo_asignaciones': self.mapeo_asignaciones,
            'configuracion_insumos': [
                {
                    'id_insumo': insumo['id_insumo'],
                    'nombre': insumo['nombre'],
                    'categoria': insumo['categoria'],
                    'peso_kg': insumo['peso_kg']
                } for insumo in self.insumos_data
            ]
        }

    def _procesar_individuo(self, individuo: Individual, posicion: int) -> Dict[str, Any]:
        """Procesar un individuo para generar datos completos"""
        vehiculos_procesados = []
        resumen_individuo = {
            'peso_total': 0.0,
            'combustible_total': 0.0,
            'localidades_atendidas': set(),
            'insumos_totales': [0] * self.num_insumos,
            'distancia_total': 0.0
        }
        
        for asignacion in individuo.vehiculos:
            vehiculo_info = self.vehiculos_disponibles[asignacion.vehiculo_id]
            mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
            
            peso_vehiculo = sum(
                asignacion.insumos[i] * self.insumos_data[i]['peso_kg']
                for i in range(self.num_insumos)
            )
            
            combustible_vehiculo = mapeo_info['distancia_km'] * vehiculo_info['consumo_litros_km']
            tiempo_viaje = mapeo_info['distancia_km'] / vehiculo_info['velocidad_kmh']
            
            # Detalles de insumos transportados
            insumos_detalle = []
            for i, cantidad in enumerate(asignacion.insumos):
                if cantidad > 0:
                    insumo_info = self.insumos_data[i]
                    peso_insumo = cantidad * insumo_info['peso_kg']
                    insumos_detalle.append({
                        'id_insumo': i,
                        'nombre': insumo_info['nombre'],
                        'categoria': insumo_info['categoria'],
                        'cantidad': cantidad,
                        'peso_total_kg': peso_insumo,
                        'peso_unitario': insumo_info['peso_kg']
                    })
            
            vehiculo_data = {
                'vehiculo_id': asignacion.vehiculo_id,
                'modelo': vehiculo_info['modelo'],
                'tipo': vehiculo_info['tipo'],
                'matricula': vehiculo_info['matricula'],
                'id_destino_ruta': asignacion.id_destino_ruta,
                'destino_nombre': mapeo_info['destino_nombre'],
                'destino_poblacion': mapeo_info['poblacion'],
                'distancia_km': mapeo_info['distancia_km'],
                'tiempo_viaje_horas': tiempo_viaje,
                'insumos_array': asignacion.insumos,
                'insumos_detalle': insumos_detalle,
                'peso_total_kg': peso_vehiculo,
                'combustible_litros': combustible_vehiculo,
                'capacidad_kg': vehiculo_info['capacidad_kg'],
                'utilizacion_capacidad': peso_vehiculo / vehiculo_info['capacidad_kg'],
                'eficiencia_kg_por_litro': peso_vehiculo / max(1, combustible_vehiculo)
            }
            
            vehiculos_procesados.append(vehiculo_data)
            
            # Actualizar resumen
            resumen_individuo['peso_total'] += peso_vehiculo
            resumen_individuo['combustible_total'] += combustible_vehiculo
            resumen_individuo['distancia_total'] += mapeo_info['distancia_km']
            resumen_individuo['localidades_atendidas'].add(mapeo_info['id_destino_perteneciente'])
            
            for i, cantidad in enumerate(asignacion.insumos):
                resumen_individuo['insumos_totales'][i] += cantidad
        
        return {
            'posicion': posicion,
            'fitness': individuo.fitness,
            'vehiculos': vehiculos_procesados,
            'resumen': {
                **resumen_individuo,
                'localidades_atendidas': len(resumen_individuo['localidades_atendidas']),
                'eficiencia_global': resumen_individuo['peso_total'] / max(1, resumen_individuo['combustible_total']),
                'utilizacion_promedio': resumen_individuo['peso_total'] / sum(v['capacidad_kg'] for v in self.vehiculos_disponibles)
            }
        }

    def _generar_analisis_rendimiento(self, top_3: List[Individual]) -> Dict[str, Any]:
        """Generar análisis comparativo de rendimiento"""
        comparacion = []
        
        for i, individuo in enumerate(top_3):
            tiempo_total = 0
            distancia_total = 0
            nodos_visitados = set()
            combustible_total = 0
            
            for asignacion in individuo.vehiculos:
                vehiculo_info = self.vehiculos_disponibles[asignacion.vehiculo_id]
                mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
                
                tiempo_total += mapeo_info['distancia_km'] / vehiculo_info['velocidad_kmh']
                distancia_total += mapeo_info['distancia_km']
                combustible_total += mapeo_info['distancia_km'] * vehiculo_info['consumo_litros_km']
                nodos_visitados.add(mapeo_info['id_destino_perteneciente'])
            
            comparacion.append({
                'individuo': i + 1,
                'fitness': individuo.fitness,
                'tiempo_total_horas': tiempo_total,
                'distancia_total_km': distancia_total,
                'nodos_visitados': len(nodos_visitados),
                'combustible_total_litros': combustible_total,
                'eficiencia_tiempo': individuo.fitness / max(1, tiempo_total),
                'eficiencia_distancia': individuo.fitness / max(1, distancia_total)
            })
        
        return {
            'comparacion_top_3': comparacion,
            'mejor_tiempo': min(comparacion, key=lambda x: x['tiempo_total_horas']),
            'mejor_distancia': min(comparacion, key=lambda x: x['distancia_total_km']),
            'mejor_combustible': min(comparacion, key=lambda x: x['combustible_total_litros'])
        }

    def _generar_distribucion_carga(self, individuo: Individual) -> Dict[str, Any]:
        """Generar análisis de distribución de carga por vehículo"""
        distribucion_vehiculos = []
        total_capacidad = 0
        total_utilizado = 0
        
        for asignacion in individuo.vehiculos:
            vehiculo_info = self.vehiculos_disponibles[asignacion.vehiculo_id]
            peso_vehiculo = sum(
                asignacion.insumos[i] * self.insumos_data[i]['peso_kg']
                for i in range(self.num_insumos)
            )
            
            capacidad = vehiculo_info['capacidad_kg']
            utilizacion = peso_vehiculo / capacidad
            
            # Distribución por categorías
            carga_por_categoria = {}
            for i, cantidad in enumerate(asignacion.insumos):
                if cantidad > 0:
                    categoria = self.insumos_data[i]['categoria']
                    peso_categoria = cantidad * self.insumos_data[i]['peso_kg']
                    
                    if categoria not in carga_por_categoria:
                        carga_por_categoria[categoria] = {'peso_kg': 0, 'items': 0}
                    
                    carga_por_categoria[categoria]['peso_kg'] += peso_categoria
                    carga_por_categoria[categoria]['items'] += cantidad
            
            distribucion_vehiculos.append({
                'vehiculo_id': asignacion.vehiculo_id,
                'modelo': vehiculo_info['modelo'],
                'tipo': vehiculo_info['tipo'],
                'capacidad_kg': capacidad,
                'peso_utilizado_kg': peso_vehiculo,
                'utilizacion_porcentual': utilizacion * 100,
                'espacio_libre_kg': capacidad - peso_vehiculo,
                'carga_por_categoria': carga_por_categoria,
                'eficiencia_carga': 'OPTIMA' if utilizacion > 0.7 else 'BUENA' if utilizacion > 0.5 else 'BAJA'
            })
            
            total_capacidad += capacidad
            total_utilizado += peso_vehiculo
        
        return {
            'vehiculos': distribucion_vehiculos,
            'resumen_global': {
                'capacidad_total_kg': total_capacidad,
                'peso_total_utilizado_kg': total_utilizado,
                'utilizacion_global_porcentual': (total_utilizado / total_capacidad) * 100,
                'espacio_desperdiciado_kg': total_capacidad - total_utilizado
            }
        }

    def _generar_panel_control(self, individuo: Individual) -> Dict[str, Any]:
        """Generar panel de control de simulación"""
        entregas = []
        estados_destinos = {}
        
        # Procesar cada entrega
        for asignacion in individuo.vehiculos:
            vehiculo_info = self.vehiculos_disponibles[asignacion.vehiculo_id]
            mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
            
            peso_vehiculo = sum(
                asignacion.insumos[i] * self.insumos_data[i]['peso_kg']
                for i in range(self.num_insumos)
            )
            
            # Determinar estado de entrega
            ruta_id = f"Destino{mapeo_info['id_destino_perteneciente']}-Ruta{mapeo_info['id_ruta_en_destino'] + 1}"
            estado_ruta = self.rutas_estado.get(ruta_id, {'estado': 'abierta', 'vehiculos_permitidos': [vehiculo_info['tipo']]})
            
            exitosa = (estado_ruta['estado'] == 'abierta' and 
                      vehiculo_info['tipo'] in estado_ruta['vehiculos_permitidos'] and
                      peso_vehiculo <= vehiculo_info['capacidad_kg'])
            
            tiempo_entrega = mapeo_info['distancia_km'] / vehiculo_info['velocidad_kmh']
            
            entrega = {
                'vehiculo_id': asignacion.vehiculo_id,
                'destino': mapeo_info['destino_nombre'],
                'tiempo_estimado_horas': tiempo_entrega,
                'peso_entregado_kg': peso_vehiculo if exitosa else 0,
                'estado': 'COMPLETADA' if exitosa else 'FALLIDA',
                'razon_falla': estado_ruta.get('razon_bloqueo', 'Ruta cerrada') if not exitosa else None,
                'poblacion_beneficiada': mapeo_info['poblacion'] if exitosa else 0
            }
            
            entregas.append(entrega)
            
            # Actualizar estados de destinos
            destino_id = mapeo_info['id_destino_perteneciente']
            if destino_id not in estados_destinos:
                estados_destinos[destino_id] = {
                    'nombre': mapeo_info['destino_nombre'],
                    'poblacion': mapeo_info['poblacion'],
                    'vehiculos_asignados': 0,
                    'peso_total_kg': 0,
                    'entregas_exitosas': 0,
                    'entregas_fallidas': 0
                }
            
            estados_destinos[destino_id]['vehiculos_asignados'] += 1
            if exitosa:
                estados_destinos[destino_id]['peso_total_kg'] += peso_vehiculo
                estados_destinos[destino_id]['entregas_exitosas'] += 1
            else:
                estados_destinos[destino_id]['entregas_fallidas'] += 1
        
        # Calcular métricas de eficiencia
        entregas_exitosas = sum(1 for e in entregas if e['estado'] == 'COMPLETADA')
        total_entregas = len(entregas)
        peso_total_entregado = sum(e['peso_entregado_kg'] for e in entregas)
        poblacion_total_beneficiada = sum(e['poblacion_beneficiada'] for e in entregas)
        
        metricas_eficiencia = {
            'tasa_exito_porcentual': (entregas_exitosas / total_entregas) * 100 if total_entregas > 0 else 0,
            'peso_total_entregado_kg': peso_total_entregado,
            'poblacion_total_beneficiada': poblacion_total_beneficiada,
            'promedio_kg_por_persona': peso_total_entregado / max(1, poblacion_total_beneficiada),
            'entregas_completadas': entregas_exitosas,
            'entregas_fallidas': total_entregas - entregas_exitosas
        }
        
        return {
            'cronologia_entregas': sorted(entregas, key=lambda x: x['tiempo_estimado_horas']),
            'metricas_eficiencia': metricas_eficiencia,
            'estados_destinos': list(estados_destinos.values())
        }

    def _generar_analisis_rutas(self, individuo: Individual) -> Dict[str, Any]:
        """Generar análisis de rutas optimizadas"""
        rutas_utilizadas = {}
        
        for asignacion in individuo.vehiculos:
            mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
            destino_id = mapeo_info['id_destino_perteneciente']
            ruta_seleccionada = mapeo_info['id_ruta_en_destino']
            
            # Encontrar todas las rutas disponibles para este destino
            rutas_destino = [m for m in self.mapeo_asignaciones 
                           if m['id_destino_perteneciente'] == destino_id]
            
            if destino_id not in rutas_utilizadas:
                rutas_utilizadas[destino_id] = {
                    'destino_nombre': mapeo_info['destino_nombre'],
                    'ruta_seleccionada': ruta_seleccionada,
                    'distancia_seleccionada': mapeo_info['distancia_km'],
                    'rutas_disponibles': len(rutas_destino),
                    'alternativas': []
                }
                
                # Agregar información de rutas alternativas
                for ruta_alt in rutas_destino:
                    if ruta_alt['id_ruta_en_destino'] != ruta_seleccionada:
                        rutas_utilizadas[destino_id]['alternativas'].append({
                            'ruta_id': ruta_alt['id_ruta_en_destino'],
                            'distancia_km': ruta_alt['distancia_km'],
                            'diferencia_km': ruta_alt['distancia_km'] - mapeo_info['distancia_km']
                        })
        
        return {
            'rutas_por_destino': rutas_utilizadas,
            'optimizacion_global': {
                'destinos_con_multiples_rutas': sum(1 for r in rutas_utilizadas.values() if len(r['alternativas']) > 0),
                'ahorro_distancia_total': sum(
                    min([alt['diferencia_km'] for alt in r['alternativas']] + [0])
                    for r in rutas_utilizadas.values() if r['alternativas']
                )
            }
        }

    def _generar_reportes_optimizacion(self, top_3: List[Individual], historial: List[Dict]) -> Dict[str, Any]:
        """Generar reportes completos de optimización"""
        # Tabla de los 3 mejores individuos
        tabla_mejores = []
        for i, individuo in enumerate(top_3):
            peso_total = sum(
                sum(asig.insumos[j] * self.insumos_data[j]['peso_kg'] for j in range(self.num_insumos))
                for asig in individuo.vehiculos
            )
            
            combustible_total = sum(
                self.mapeo_asignaciones[asig.id_destino_ruta]['distancia_km'] * 
                self.vehiculos_disponibles[asig.vehiculo_id]['consumo_litros_km']
                for asig in individuo.vehiculos
            )
            
            localidades = len(set(
                self.mapeo_asignaciones[asig.id_destino_ruta]['id_destino_perteneciente']
                for asig in individuo.vehiculos
            ))
            
            tabla_mejores.append({
                'posicion': i + 1,
                'fitness': individuo.fitness,
                'peso_total_kg': peso_total,
                'combustible_total_litros': combustible_total,
                'localidades_atendidas': localidades,
                'eficiencia_peso_combustible': peso_total / max(1, combustible_total),
                'vehiculos_utilizados': len(individuo.vehiculos)
            })
        
        # Análisis de evolución
        evolucion_analisis = {
            'generaciones_totales': len(historial),
            'fitness_inicial': historial[0]['mejor'] if historial else 0,
            'fitness_final': historial[-1]['mejor'] if historial else 0,
            'mejora_absoluta': (historial[-1]['mejor'] - historial[0]['mejor']) if len(historial) > 1 else 0,
            'mejora_porcentual': ((historial[-1]['mejor'] - historial[0]['mejor']) / max(1, historial[0]['mejor'])) * 100 if len(historial) > 1 else 0,
            'convergencia': self._analizar_convergencia(historial)
        }
        
        return {
            'tabla_top_3': tabla_mejores,
            'evolucion_fitness': historial,
            'analisis_evolucion': evolucion_analisis,
            'configuraciones_comparadas': self._generar_comparacion_configuraciones(top_3)
        }

    def _analizar_convergencia(self, historial: List[Dict]) -> Dict[str, Any]:
        """Analizar convergencia del algoritmo"""
        if len(historial) < 10:
            return {'convergencia': 'INSUFICIENTES_DATOS'}
        
        ultimas_10 = historial[-10:]
        fitness_ultimas = [g['mejor'] for g in ultimas_10]
        
        variacion = max(fitness_ultimas) - min(fitness_ultimas)
        promedio_final = sum(fitness_ultimas) / len(fitness_ultimas)
        
        if variacion < promedio_final * 0.01:
            estado = 'CONVERGIDO'
        elif variacion < promedio_final * 0.05:
            estado = 'SEMI_CONVERGIDO'
        else:
            estado = 'EN_EVOLUCION'
        
        return {
            'estado': estado,
            'variacion_ultimas_10': variacion,
            'estabilidad_porcentual': (1 - variacion / max(1, promedio_final)) * 100
        }

    def _generar_comparacion_configuraciones(self, top_3: List[Individual]) -> List[Dict[str, Any]]:
        """Generar comparación entre diferentes configuraciones"""
        configuraciones = []
        
        for i, individuo in enumerate(top_3):
            # Analizar patrones de asignación
            tipos_vehiculos_usados = set()
            destinos_priorizados = {}
            
            for asignacion in individuo.vehiculos:
                vehiculo_tipo = self.vehiculos_disponibles[asignacion.vehiculo_id]['tipo']
                tipos_vehiculos_usados.add(vehiculo_tipo)
                
                destino_id = self.mapeo_asignaciones[asignacion.id_destino_ruta]['id_destino_perteneciente']
                poblacion = self.mapeo_asignaciones[asignacion.id_destino_ruta]['poblacion']
                
                if destino_id not in destinos_priorizados:
                    destinos_priorizados[destino_id] = {'poblacion': poblacion, 'vehiculos': 0}
                destinos_priorizados[destino_id]['vehiculos'] += 1
            
            configuraciones.append({
                'configuracion_id': i + 1,
                'fitness': individuo.fitness,
                'tipos_vehiculos_usados': list(tipos_vehiculos_usados),
                'diversidad_vehiculos': len(tipos_vehiculos_usados),
                'estrategia_poblacional': 'ALTA_POBLACION' if any(d['poblacion'] > 400 for d in destinos_priorizados.values()) else 'DISTRIBUIDA'
            })
        
        return configuraciones