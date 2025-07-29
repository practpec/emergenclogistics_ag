import random
from typing import List, Dict, Any
from core.base_service import BaseService
from core.exceptions import GeneticAlgorithmError
from ..core.data_manager import DataManager
from ..models import *
from ..operators.initialization import InitializationOperator
from ..operators.evaluation import EvaluationOperator
from ..operators.crossover import CrossoverOperator
from ..operators.mutation import MutationOperator
from ..operators.selection import SelectionOperator


class LogisticsGeneticAlgorithm(BaseService):
    """Algoritmo genético para optimización logística"""
    
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
            config.elitismo_rate = parametros_ag.get('elitismo_rate', config.elitismo_rate)
        
        self.config = config
        self.evolucion_fitness = []
    
    def _configurar_operadores(self):
        """Configurar operadores del AG"""
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
            
            self.crossover_operator = CrossoverOperator()
            
            self.mutation_operator = MutationOperator(
                self.scenario_data.rutas, 
                self.init_operator.vehiculos_expandidos, 
                self.insumos
            )
            
            self.selection_operator = SelectionOperator()
            
        except Exception as e:
            self.log_error("Error configurando operadores", e)
            raise GeneticAlgorithmError(f"Error en configuración: {e}")
    
    def ejecutar(self) -> Dict[str, Any]:
        """Ejecutar el algoritmo genético"""
        try:
            if not self.scenario_data.rutas:
                raise GeneticAlgorithmError("No hay rutas abiertas")
            
            if not self.scenario_data.vehiculos_disponibles:
                raise GeneticAlgorithmError("No hay vehículos disponibles")
            
            poblacion = self.init_operator.generar_poblacion_inicial(self.config.poblacion_size)
            
            mejor_individuo = None
            mejor_fitness = 0
            
            for generacion in range(self.config.generaciones):
                poblacion_evaluada = self._evaluar_poblacion(poblacion)
                
                fitness_actual = max(fitness for _, fitness in poblacion_evaluada)
                self.evolucion_fitness.append(fitness_actual)
                
                if fitness_actual > mejor_fitness:
                    mejor_fitness = fitness_actual
                    mejor_individuo = max(poblacion_evaluada, key=lambda x: x[1])[0]
                
                tamaño_elite = int(len(poblacion) * self.config.elitismo_rate)
                elite = self.selection_operator.seleccion_elitista(poblacion_evaluada, tamaño_elite)
                
                nueva_poblacion = elite.copy()
                
                while len(nueva_poblacion) < self.config.poblacion_size:
                    padre1 = self.selection_operator.seleccion_torneo(poblacion_evaluada)
                    padre2 = self.selection_operator.seleccion_torneo(poblacion_evaluada)
                    
                    if random.random() < self.config.prob_cruza:
                        hijo1, hijo2 = self.crossover_operator.cruzar_individuos(padre1, padre2)
                    else:
                        hijo1, hijo2 = padre1.copy(), padre2.copy()
                    
                    hijo1 = self.mutation_operator.mutar_individuo(hijo1, self.config.prob_mutacion)
                    hijo2 = self.mutation_operator.mutar_individuo(hijo2, self.config.prob_mutacion)
                    
                    nueva_poblacion.extend([hijo1, hijo2])
                
                poblacion = nueva_poblacion[:self.config.poblacion_size]
            
            poblacion_final = self._evaluar_poblacion(poblacion)
            top_3 = sorted(poblacion_final, key=lambda x: x[1], reverse=True)[:3]
            
            return self._generar_resultados(mejor_individuo, top_3)
            
        except Exception as e:
            self.log_error("Error ejecutando AG", e)
            raise GeneticAlgorithmError(f"Error en ejecución: {e}")
    
    def _evaluar_poblacion(self, poblacion: List[Individual]) -> List[tuple]:
        """Evaluar población"""
        poblacion_evaluada = []
        for individuo in poblacion:
            fitness = self.eval_operator.evaluar_individuo(individuo)
            poblacion_evaluada.append((individuo, fitness))
        return poblacion_evaluada
    
    def _generar_resultados(self, mejor_individuo: Individual, top_3: List[tuple]) -> Dict[str, Any]:
        """Generar resultados finales"""
        
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
                "mejora_total": self.evolucion_fitness[-1] - self.evolucion_fitness[0] if self.evolucion_fitness else 0
            },
            "resumen_escenario": {
                "tipo_desastre": self.scenario_data.tipo_desastre.tipo,
                "total_vehiculos_disponibles": total_vehiculos,
                "total_rutas_abiertas": total_rutas,
                "vehiculos_utilizados": mejor_resultado.vehiculos_utilizados,
                "rutas_cubiertas": mejor_resultado.rutas_utilizadas,
                "eficiencia_vehiculos": mejor_resultado.vehiculos_utilizados / total_vehiculos if total_vehiculos > 0 else 0,
                "cobertura_rutas": mejor_resultado.rutas_utilizadas / total_rutas if total_rutas > 0 else 0
            }
        }
    
    def _procesar_individuo_resultado(self, individuo: Individual, fitness: float) -> ResultadoIndividuo:
        """Procesar individuo para resultado"""
        if not individuo:
            return ResultadoIndividuo(
                asignaciones=[],
                fitness=0,
                rutas_utilizadas=0,
                vehiculos_utilizados=0,
                peso_total_transportado=0,
                combustible_total=0
            )
        
        asignaciones_dict = []
        for asignacion in individuo:
            asignacion_dict = {
                "vehiculo_id": asignacion.vehiculo_id,
                "ruta_id": asignacion.ruta_id,
                "insumos": [{"id": i.id, "nombre": i.nombre, "categoria": i.categoria, "peso_kg": i.peso_kg} for i in asignacion.insumos],
                "peso_total_kg": asignacion.peso_total_kg,
                "distancia_km": asignacion.distancia_km,
                "combustible_usado": asignacion.combustible_usado
            }
            asignaciones_dict.append(asignacion_dict)
        
        return ResultadoIndividuo(
            asignaciones=asignaciones_dict,
            fitness=fitness,
            rutas_utilizadas=len(set(a.ruta_id for a in individuo)),
            vehiculos_utilizados=len(set(a.vehiculo_id for a in individuo)),
            peso_total_transportado=sum(a.peso_total_kg for a in individuo),
            combustible_total=sum(a.combustible_usado for a in individuo)
        )