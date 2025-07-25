from typing import List, Dict, Any
from ..models import Individual

class ResultGenerator:
    """Generador optimizado de resultados del AG"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.vehiculos_disponibles = data_manager.vehiculos_disponibles
        self.mapeo_asignaciones = data_manager.mapeo_asignaciones
        self.insumos_data = data_manager.insumos_data
        self.num_insumos = data_manager.num_insumos

    def generar_resultado_final(self, mejor_individuo: Individual, historial: List[Dict], 
                               poblacion_final: List[Individual], parametros_ag: Dict) -> Dict[str, Any]:
        """Generar resultado final según formato requerido"""
        top_3_individuos = sorted(poblacion_final, key=lambda x: x.fitness, reverse=True)[:3]
        
        mejores_soluciones = []
        for i, individuo in enumerate(top_3_individuos):
            solucion_data = self._procesar_individuo_para_resultado(individuo, i + 1)
            mejores_soluciones.append(solucion_data)
        
        metricas_globales = self._calcular_metricas_globales(top_3_individuos)
        convergencia_info = self._analizar_convergencia(historial, parametros_ag)
        
        return {
            'mejores_soluciones': mejores_soluciones,
            'metricas_globales': metricas_globales,
            'convergencia': convergencia_info,
            'evolucion_fitness': historial,
            'parametros_utilizados': parametros_ag
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
        
        for i, asignacion in enumerate(individuo.vehiculos):
            vehiculo_info = self.vehiculos_disponibles[asignacion.vehiculo_id]
            
            if asignacion.id_destino_ruta < len(self.mapeo_asignaciones):
                mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
                
                peso_vehiculo = self._calcular_peso_insumos(asignacion.insumos)
                combustible = mapeo_info['distancia_km'] * vehiculo_info.get('consumo_litros_km', 0.10)
                tiempo_viaje = mapeo_info['distancia_km'] / vehiculo_info.get('velocidad_kmh', 60)
                
                estado_entrega = self._determinar_estado_entrega(
                    vehiculo_info, mapeo_info, peso_vehiculo
                )
                
                asignacion_resultado = {
                    'vehiculo_id': i + 1,
                    'vehiculo_modelo': vehiculo_info.get('modelo', f'Vehículo {i + 1}'),
                    'vehiculo_tipo': vehiculo_info.get('tipo', 'camioneta'),
                    'destino_clave': mapeo_info['id_destino_perteneciente'],
                    'destino_nombre': mapeo_info['destino_nombre'],
                    'ruta_id': mapeo_info['id_ruta_en_destino'],
                    'distancia_km': mapeo_info['distancia_km'],
                    'poblacion_destino': mapeo_info['poblacion'],
                    'insumos_asignados': self._formatear_insumos(asignacion.insumos),
                    'peso_total_kg': round(peso_vehiculo, 2),
                    'combustible_litros': round(combustible, 2),
                    'tiempo_horas': round(tiempo_viaje, 2),
                    'utilizacion_capacidad': round(peso_vehiculo / vehiculo_info['capacidad_kg'] * 100, 1),
                    'estado_entrega': estado_entrega
                }
                
                asignaciones.append(asignacion_resultado)
                
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
        
        utilizacion_promedio = (resumen_totales['utilizacion_total'] / 
                               len(individuo.vehiculos) if individuo.vehiculos else 0)
        
        eficiencia_entrega = (resumen_totales['entregas_exitosas'] / 
                             len(individuo.vehiculos) if individuo.vehiculos else 0)
        
        resumen = {
            'entregas_exitosas': resumen_totales['entregas_exitosas'],
            'entregas_fallidas': resumen_totales['entregas_fallidas'],
            'destinos_atendidos': len(resumen_totales['destinos_atendidos']),
            'peso_total_entregado': round(resumen_totales['peso_total_entregado'], 2),
            'combustible_total': round(resumen_totales['combustible_total'], 2),
            'poblacion_beneficiada': resumen_totales['poblacion_beneficiada'],
            'utilizacion_promedio': round(utilizacion_promedio * 100, 1),
            'eficiencia_entrega': round(eficiencia_entrega * 100, 1)
        }
        
        return {
            'posicion': posicion,
            'fitness': round(individuo.fitness, 2),
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
        if peso_vehiculo > vehiculo_info['capacidad_kg']:
            return 'fallida'
        
        vehiculos_permitidos = mapeo_info.get('vehiculos_permitidos', [])
        estado_ruta = mapeo_info.get('estado', 'abierta')
        
        if (estado_ruta == 'abierta' and 
            vehiculo_info.get('tipo', 'camioneta') in vehiculos_permitidos):
            return 'exitosa'
        else:
            return 'fallida'

    def _formatear_insumos(self, insumos: List[int]) -> List[Dict[str, Any]]:
        """Formatear insumos para resultado"""
        insumos_formateados = []
        for i, cantidad in enumerate(insumos):
            if cantidad > 0 and i < len(self.insumos_data):
                insumo_info = self.insumos_data[i]
                insumos_formateados.append({
                    'id': i,
                    'nombre': insumo_info['nombre'],
                    'categoria': insumo_info['categoria'],
                    'cantidad': cantidad,
                    'peso_unitario': insumo_info['peso_kg'],
                    'peso_total': round(cantidad * insumo_info['peso_kg'], 2)
                })
        return insumos_formateados

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
        
        estado_convergencia = 'convergido' if parametros_ag.get('convergencia', False) else 'completado'
        
        return {
            'generaciones_ejecutadas': len(historial),
            'mejora_porcentual': mejora_porcentual,
            'estado': estado_convergencia
        }