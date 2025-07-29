# back/services/algorithms/main/genetic_algorithm.py - ACTUALIZADO

import random
from typing import List, Dict, Any
from core.base_service import BaseService
from core.exceptions import GeneticAlgorithmError
from ..core.data_manager import DataManager
from ..models import (
    Individual, ResultadoIndividuo, EstadoRuta
)
from ..operators.initialization import InitializationOperator
from ..operators.evaluation import EvaluationOperator
from ..operators.simple_selection import SimpleSelectionOperator
from ..operators.simple_crossover import SimpleCrossoverOperator
from ..operators.simple_mutation import SimpleMutationOperator
from ..operators.simple_pruning import SimplePruningOperator
from ..operators.simple_repair import SimpleRepairOperator
from ..output.result_formatter import ResultFormatter

class LogisticsGeneticAlgorithm(BaseService):
    def __init__(self, datos_frontend: Dict[str, Any], parametros_ag: Dict[str, Any] = None):
        super().__init__()
        self.data_manager = DataManager()
        self.scenario_data, self.insumos = self.data_manager.procesar_datos_entrada(datos_frontend)
        
        self._configurar_operadores()
        
        config = self.scenario_data.configuracion_ag
        if parametros_ag:
            config.poblacion_size = parametros_ag.get('poblacion_size', config.poblacion_size)
            config.generaciones = parametros_ag.get('generaciones', config.generaciones)
            config.prob_cruza = parametros_ag.get('prob_cruza', config.prob_cruza)
            config.prob_mutacion = parametros_ag.get('prob_mutacion', config.prob_mutacion)
        
        self.config = config
        self.evolucion_fitness = []
    
    def _configurar_operadores(self):
        try:
            self.init_operator = InitializationOperator(
                self.scenario_data.rutas, 
                self.scenario_data.vehiculos_disponibles, 
                self.insumos
            )
            
            self.eval_operator = EvaluationOperator(
                self.scenario_data.rutas, 
                self.scenario_data.tipo_desastre, 
                self.insumos
            )
            
            self.selection_operator = SimpleSelectionOperator()
            self.crossover_operator = SimpleCrossoverOperator()
            self.mutation_operator = SimpleMutationOperator()
            self.pruning_operator = SimplePruningOperator()
            self.repair_operator = SimpleRepairOperator(
                self.scenario_data.rutas,
                self.init_operator.vehiculos_expandidos
            )
            
        except Exception as e:
            self.log_error("Error configurando operadores", e)
            raise GeneticAlgorithmError(f"Error en configuración: {e}")
    
    def ejecutar(self) -> Dict[str, Any]:
        try:
            rutas_abiertas = [r for r in self.scenario_data.rutas if r.estado == EstadoRuta.ABIERTA]
            
            if not rutas_abiertas:
                raise GeneticAlgorithmError("No hay rutas abiertas")
            
            if not self.scenario_data.vehiculos_disponibles:
                raise GeneticAlgorithmError("No hay vehículos disponibles")
            
            # PASO 0: Generar población inicial
            poblacion = self.init_operator.generar_poblacion_inicial(self.config.poblacion_size)
            
            mejor_individuo = None
            mejor_fitness = 0
            
            for generacion in range(self.config.generaciones):
                # PASO 1: EVALUACIÓN
                poblacion_evaluada = self._evaluar_poblacion(poblacion)
                
                fitness_actual = max(fitness for _, fitness in poblacion_evaluada)
                self.evolucion_fitness.append(fitness_actual)
                
                if fitness_actual > mejor_fitness:
                    mejor_fitness = fitness_actual
                    mejor_individuo = max(poblacion_evaluada, key=lambda x: x[1])[0]
                
                # PASO 2: SELECCIÓN POR ORDEN (mejor con segundo, tercero con cuarto)
                parejas = self.selection_operator.seleccion_por_orden(poblacion_evaluada)
                
                # PASO 3: CRUZA SIMPLE (vehículo con vehículo, ruta con ruta, insumos aleatorios)
                descendencia = self.crossover_operator.cruza_simple(parejas, self.config.prob_cruza)
                
                # PASO 4: MUTACIÓN POR SEGMENTOS
                descendencia_mutada = self.mutation_operator.mutacion_segmento_aleatorio(
                    descendencia, self.config.prob_mutacion
                )
                
                # PASO 5: REPARACIÓN (asegurar uso de todos los vehículos)
                descendencia_reparada = []
                for individuo in descendencia_mutada:
                    individuo_reparado = self.repair_operator.reparar_individuo(individuo)
                    descendencia_reparada.append(individuo_reparado)
                
                # PASO 6: EVALUACIÓN DE DESCENDENCIA
                descendencia_evaluada = self._evaluar_poblacion(descendencia_reparada)
                
                # PASO 7: COMBINAR POBLACIONES
                poblacion_total = poblacion_evaluada + descendencia_evaluada
                
                # PASO 8: PODA ALEATORIA CONSERVANDO MEJOR
                poblacion = self.pruning_operator.poda_aleatoria_conservando_mejor(
                    poblacion_total, self.config.poblacion_size
                )
            
            poblacion_final = self._evaluar_poblacion(poblacion)
            top_3 = sorted(poblacion_final, key=lambda x: x[1], reverse=True)[:3]
            
            resultado_ag = self._generar_resultados(mejor_individuo, top_3)
            
            return ResultFormatter.formatear_para_frontend(resultado_ag)
            
        except Exception as e:
            self.log_error("Error ejecutando AG", e)
            raise GeneticAlgorithmError(f"Error en ejecución: {e}")
    
    def _evaluar_poblacion(self, poblacion: List[Individual]) -> List[tuple]:
        poblacion_evaluada = []
        for individuo in poblacion:
            try:
                fitness = self.eval_operator.evaluar_individuo(individuo)
                poblacion_evaluada.append((individuo, fitness))
            except Exception as e:
                self.log_error(f"Error evaluando individuo: {e}", e)
                poblacion_evaluada.append((individuo, 0.0))
        return poblacion_evaluada
    
    def _generar_resultados(self, mejor_individuo: Individual, top_3: List[tuple]) -> Dict[str, Any]:
        mejor_resultado = self._procesar_individuo_resultado(mejor_individuo, top_3[0][1])
        
        top_3_resultados = []
        for individuo, fitness in top_3:
            resultado = self._procesar_individuo_resultado(individuo, fitness)
            top_3_resultados.append(resultado)
        
        total_vehiculos = sum(v.cantidad for v in self.scenario_data.vehiculos_disponibles)
        total_rutas = len([r for r in self.scenario_data.rutas if r.estado == EstadoRuta.ABIERTA])
        
        return {
            "mejor_solucion": mejor_resultado.__dict__,
            "top_3_soluciones": [r.__dict__ for r in top_3_resultados],
            "evolucion_fitness": self.evolucion_fitness,
            "metricas_optimizacion": {
                "generaciones_ejecutadas": self.config.generaciones,
                "poblacion_size": self.config.poblacion_size,
                "fitness_final": mejor_resultado.fitness,
                "mejora_total": (self.evolucion_fitness[-1] - self.evolucion_fitness[0] 
                               if len(self.evolucion_fitness) > 1 else 0)
            },
            "resumen_escenario": {
                "tipo_desastre": self.scenario_data.tipo_desastre.tipo,
                "total_vehiculos_disponibles": total_vehiculos,
                "total_rutas_abiertas": total_rutas,
                "vehiculos_utilizados": mejor_resultado.vehiculos_utilizados,
                "rutas_cubiertas": mejor_resultado.rutas_utilizadas,
                "eficiencia_vehiculos": mejor_resultado.vehiculos_utilizados / total_vehiculos if total_vehiculos > 0 else 0,
                "cobertura_rutas": mejor_resultado.rutas_utilizadas / total_rutas if total_rutas > 0 else 0
            },
            "distribucion_carga": self._calcular_distribucion_simple(mejor_individuo),
            "cronologia_entregas": self._calcular_entregas_simple(mejor_individuo),
            "analisis_eficiencia": self._calcular_eficiencia_simple(mejor_individuo)
        }
    
    def _procesar_individuo_resultado(self, individuo: Individual, fitness: float) -> ResultadoIndividuo:
        if not individuo:
            return ResultadoIndividuo(
                asignaciones=[], fitness=0, rutas_utilizadas=0,
                vehiculos_utilizados=0, peso_total_transportado=0, combustible_total=0
            )
        
        asignaciones_dict = []
        for asignacion in individuo:
            if asignacion.ruta_id == -1:
                continue
            
            insumos_transportados = []
            for i, cantidad in enumerate(asignacion.insumos):
                if cantidad > 0 and i < len(self.insumos):
                    insumos_transportados.append({
                        "id_insumo": self.insumos[i].id,
                        "cantidad": cantidad
                    })
            
            asignacion_dict = {
                "vehiculo_id": asignacion.vehiculo_id,
                "ruta_id": asignacion.ruta_id,
                "insumos_cantidades": insumos_transportados,
                "peso_total_kg": asignacion.peso_total_kg,
                "distancia_km": asignacion.distancia_km,
                "combustible_usado": asignacion.combustible_usado
            }
            asignaciones_dict.append(asignacion_dict)
        
        return ResultadoIndividuo(
            asignaciones=asignaciones_dict,
            fitness=fitness,
            rutas_utilizadas=len(set(asig["ruta_id"] for asig in asignaciones_dict)),
            vehiculos_utilizados=len(set(asig["vehiculo_id"] for asig in asignaciones_dict)),
            peso_total_transportado=sum(asig["peso_total_kg"] for asig in asignaciones_dict),
            combustible_total=sum(asig["combustible_usado"] for asig in asignaciones_dict)
        )
    
    def _calcular_distribucion_simple(self, individuo: Individual) -> Dict[str, Any]:
        vehiculos_activos = [a for a in individuo if a.ruta_id != -1]
        total_peso = sum(a.peso_total_kg for a in vehiculos_activos)
        total_capacidad = len(self.init_operator.vehiculos_expandidos) * 1000
        
        return {
            "utilizacion_promedio": (total_peso / total_capacidad * 100) if total_capacidad > 0 else 0,
            "vehiculos_optimos": len([a for a in vehiculos_activos if 700 <= a.peso_total_kg <= 950]),
            "vehiculos_subutilizados": len([a for a in vehiculos_activos if a.peso_total_kg < 700]),
            "peso_total_transportado": total_peso,
            "capacidad_total_disponible": total_capacidad,
            "utilizacion_total": (total_peso / total_capacidad * 100) if total_capacidad > 0 else 0
        }
    
    def _calcular_entregas_simple(self, individuo: Individual) -> Dict[str, Any]:
        """Cronología simplificada"""
        entregas_exitosas = len([a for a in individuo if a.ruta_id != -1])
        entregas_fallidas = len([a for a in individuo if a.ruta_id == -1])
        
        return {
            "entregas_exitosas": entregas_exitosas,
            "entregas_fallidas": entregas_fallidas,
            "tasa_exito": (entregas_exitosas / len(individuo) * 100) if individuo else 0,
            "poblacion_cubierta": entregas_exitosas * 5000,
            "poblacion_no_cubierta": entregas_fallidas * 5000
        }
    
    def _calcular_eficiencia_simple(self, individuo: Individual) -> Dict[str, Any]:
        """Eficiencia simplificada"""
        vehiculos_activos = [a for a in individuo if a.ruta_id != -1]
        if not vehiculos_activos:
            return {"combustible_promedio": 0, "peso_promedio": 0, "distancia_promedio": 0}
        
        return {
            "combustible_promedio": sum(a.combustible_usado for a in vehiculos_activos) / len(vehiculos_activos),
            "peso_promedio": sum(a.peso_total_kg for a in vehiculos_activos) / len(vehiculos_activos),
            "distancia_promedio": sum(a.distancia_km for a in vehiculos_activos) / len(vehiculos_activos)
        }