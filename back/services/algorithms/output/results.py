from typing import List, Dict, Any
from ..models import Individual

class ResultGenerator:
    """Generador optimizado de resultados del AG"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.vehiculos_disponibles = data_manager.vehiculos_disponibles
        self.mapeo_asignaciones = data_manager.mapeo_asignaciones
        self.insumos_data = data_manager.insumos_data
        self.rutas_estado = data_manager.rutas_estado
        self.num_insumos = data_manager.num_insumos

    def generar_resultado_final(self, mejor_individuo: Individual, historial: List[Dict], 
                               poblacion_final: List[Individual], parametros_ag: Dict) -> Dict[str, Any]:
        """Generar resultado final según formato requerido"""
        # Obtener top 3 individuos
        top_3_individuos = sorted(poblacion_final, key=lambda x: x.fitness, reverse=True)[:3]
        
        # Procesar mejores soluciones
        mejores_soluciones = []
        for i, individuo in enumerate(top_3_individuos):
            solucion_data = self._procesar_individuo_para_resultado(individuo, i + 1)
            mejores_soluciones.append(solucion_data)
        
        # Métricas globales
        metricas_globales = self._calcular_metricas_globales(top_3_individuos)
        
        # Análisis de convergencia
        convergencia_info = self._analizar_convergencia(historial, parametros_ag)
        
        return {
            'mejores_soluciones': mejores_soluciones,
            'metricas_globales': metricas_globales,
            'convergencia': convergencia_info,
            'evolucion_fitness': historial
        }

    def _procesar_individuo_para_resultado(self, individuo: Individual, posicion: int) -> Dict[str, Any]:
        """Procesar individuo según formato del resultado esperado"""
        asignaciones = []
        resumen_totales = {
            'entregas_exitosas': 0,
            'entregas_fallidas': 0,
            'destinos_atendidos': set(),
            'peso_total_entregado': 0.0,
            'combustible_total': 0.0,
            'poblacion_beneficiada': 0,
            'utilizacion_total': 0.0
        }
        
        for asignacion in individuo.vehiculos:
            vehiculo_info = self.vehiculos_disponibles[asignacion.vehiculo_id]
            
            if asignacion.id_destino_ruta < len(self.mapeo_asignaciones):
                mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
                
                # Calcular métricas del vehículo
                peso_vehiculo = self._calcular_peso_insumos(asignacion.insumos)
                combustible = mapeo_info['distancia_km'] * vehiculo_info.get('consumo_litros_km', 0.15)
                tiempo_viaje = mapeo_info['distancia_km'] / vehiculo_info.get('velocidad_kmh', 60)
                
                # Determinar estado de entrega
                estado_entrega = self._determinar_estado_entrega(
                    vehiculo_info, mapeo_info, peso_vehiculo
                )
                
                # Crear asignación para resultado
                asignacion_resultado = {
                    'vehiculo_id': str(asignacion.vehiculo_id + 1),
                    'ruta_id': str(mapeo_info['id_ruta_en_destino'] + 1),
                    'insumos': asignacion.insumos,
                    'peso_total_kg': peso_vehiculo,
                    'combustible_litros': combustible,
                    'tiempo_horas': tiempo_viaje,
                    'estado_entrega': estado_entrega
                }
                
                asignaciones.append(asignacion_resultado)
                
                # Actualizar totales del resumen
                if estado_entrega == 'exitosa':
                    resumen_totales['entregas_exitosas'] += 1
                    resumen_totales['peso_total_entregado'] += peso_vehiculo
                    resumen_totales['poblacion_beneficiada'] += mapeo_info['poblacion']
                    resumen_totales['destinos_atendidos'].add(mapeo_info['id_destino_perteneciente'])
                else:
                    resumen_totales['entregas_fallidas'] += 1
                
                resumen_totales['combustible_total'] += combustible
                utilizacion = peso_vehiculo / vehiculo_info['capacidad_kg']
                resumen_totales['utilizacion_total'] += utilizacion
        
        # Calcular utilización promedio
        utilizacion_promedio = (resumen_totales['utilizacion_total'] / 
                               len(individuo.vehiculos) if individuo.vehiculos else 0)
        
        # Crear resumen final
        resumen = {
            'entregas_exitosas': resumen_totales['entregas_exitosas'],
            'entregas_fallidas': resumen_totales['entregas_fallidas'],
            'destinos_atendidos': len(resumen_totales['destinos_atendidos']),
            'peso_total_entregado': resumen_totales['peso_total_entregado'],
            'combustible_total': resumen_totales['combustible_total'],
            'poblacion_beneficiada': resumen_totales['poblacion_beneficiada'],
            'utilizacion_promedio': utilizacion_promedio
        }
        
        return {
            'posicion': posicion,
            'fitness': individuo.fitness,
            'asignaciones': asignaciones,
            'resumen': resumen
        }

    def _calcular_peso_insumos(self, insumos: List[int]) -> float:
        """Calcular peso total de insumos"""
        return sum(
            insumos[i] * self.data_manager.get_peso_insumo(i)
            for i in range(len(insumos))
        )

    def _determinar_estado_entrega(self, vehiculo_info: Dict, mapeo_info: Dict, peso_vehiculo: float) -> str:
        """Determinar estado de entrega basado en restricciones"""
        # Verificar capacidad
        if peso_vehiculo > vehiculo_info['capacidad_kg']:
            return 'fallida'
        
        # Verificar compatibilidad de ruta
        destino_id = mapeo_info['id_destino_perteneciente']
        ruta_id = f"{destino_id}-ruta-{mapeo_info['id_ruta_en_destino']}"
        
        estado_ruta = self.rutas_estado.get(ruta_id, {
            'estado': 'abierta',
            'vehiculos_permitidos': [vehiculo_info['tipo']]
        })
        
        if (estado_ruta['estado'] == 'abierta' and 
            vehiculo_info['tipo'] in estado_ruta['vehiculos_permitidos']):
            return 'exitosa'
        else:
            return 'fallida'

    def _calcular_metricas_globales(self, top_3_individuos: List[Individual]) -> Dict[str, Any]:
        """Calcular métricas globales de los mejores individuos"""
        mejor_tiempo = float('inf')
        mejor_distancia = float('inf')
        mejor_combustible = float('inf')
        
        for individuo in top_3_individuos:
            tiempo_total = 0
            distancia_total = 0
            combustible_total = 0
            
            for asignacion in individuo.vehiculos:
                if asignacion.id_destino_ruta < len(self.mapeo_asignaciones):
                    vehiculo_info = self.vehiculos_disponibles[asignacion.vehiculo_id]
                    mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
                    
                    tiempo_viaje = mapeo_info['distancia_km'] / vehiculo_info.get('velocidad_kmh', 60)
                    combustible_viaje = mapeo_info['distancia_km'] * vehiculo_info.get('consumo_litros_km', 0.15)
                    
                    tiempo_total += tiempo_viaje
                    distancia_total += mapeo_info['distancia_km']
                    combustible_total += combustible_viaje
            
            mejor_tiempo = min(mejor_tiempo, tiempo_total)
            mejor_distancia = min(mejor_distancia, distancia_total)
            mejor_combustible = min(mejor_combustible, combustible_total)
        
        return {
            'mejor_tiempo': mejor_tiempo if mejor_tiempo != float('inf') else 0,
            'mejor_distancia': mejor_distancia if mejor_distancia != float('inf') else 0,
            'mejor_combustible': mejor_combustible if mejor_combustible != float('inf') else 0
        }

    def _analizar_convergencia(self, historial: List[Dict], parametros_ag: Dict) -> Dict[str, Any]:
        """Analizar convergencia del algoritmo"""
        if not historial:
            return {
                'generaciones_ejecutadas': 0,
                'mejora_porcentual': 0,
                'estado': 'sin_datos'
            }
        
        fitness_inicial = historial[0]['mejor'] if historial else 0
        fitness_final = historial[-1]['mejor'] if historial else 0
        
        mejora_porcentual = 0
        if fitness_inicial > 0:
            mejora_porcentual = ((fitness_final - fitness_inicial) / fitness_inicial) * 100
        
        # Determinar estado de convergencia
        estado_convergencia = 'convergido' if parametros_ag.get('convergencia', False) else 'completado'
        
        return {
            'generaciones_ejecutadas': len(historial),
            'mejora_porcentual': mejora_porcentual,
            'estado': estado_convergencia
        }