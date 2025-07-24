from typing import List, Dict, Any
from core.base_service import BaseService
from core.exceptions import GeneticAlgorithmError

from ..models import Individual, VehicleAssignment
from ..core.data_manager import AlgorithmDataManager
from ..operators.initialization import PopulationInitializer
from ..operators.evaluation import FitnessEvaluator
from ..operators.selection import ParentSelector
from ..operators.crossover import CrossoverOperator
from ..operators.mutation import MutationOperator
from ..operators.replacement import ReplacementOperator
from ..output.results import ResultGenerator

class LogisticsGeneticAlgorithm(BaseService):
    """Algoritmo genético optimizado para logística de emergencia"""
    
    def __init__(self, scenario_data: Dict[str, Any], parametros_ag: Dict[str, Any] = None):
        super().__init__()
        
        self.data_manager = AlgorithmDataManager(scenario_data)
        self._configure_parameters(parametros_ag)
        self._initialize_operators()

    def _configure_parameters(self, parametros_ag: Dict[str, Any] = None):
        """Configurar parámetros del algoritmo genético con validación"""
        defaults = {
            'poblacion_size': 80,
            'generaciones': 500, 
            'prob_cruza': 0.85, 
            'prob_mutacion': 0.20, 
            'elitismo_rate': 0.15  
        }
        
        # El frontend ya valida, solo aplicar
        if parametros_ag:
            for param, value in parametros_ag.items():
                if param in defaults:
                    setattr(self, param, value)
                else:
                    setattr(self, param, defaults[param])
        else:
            for param, value in defaults.items():
                setattr(self, param, value)

    def _initialize_operators(self):
        """Inicializar operadores optimizados"""
        self.initializer = PopulationInitializer(self.data_manager)
        self.evaluator = FitnessEvaluator(self.data_manager)
        self.selector = ParentSelector()
        self.crossover = CrossoverOperator(self.data_manager)
        self.mutation = MutationOperator(self.data_manager)
        self.replacement = ReplacementOperator()
        self.result_generator = ResultGenerator(self.data_manager)

    def ejecutar(self) -> Dict[str, Any]:
        """Ejecutar algoritmo genético optimizado"""
        try:
            # Inicialización inteligente
            poblacion = self._initialize_smart_population()
            
            # Variables de control
            mejor_historico = None
            historial_fitness = []
            generaciones_sin_mejora = 0
            
            # Bucle principal del AG
            for generacion in range(self.generaciones):
                # Evaluación
                for individuo in poblacion:
                    self.evaluator.evaluar_fitness(individuo)
                
                # Tracking del mejor
                mejor_actual = max(poblacion, key=lambda x: x.fitness)
                if mejor_historico is None or mejor_actual.fitness > mejor_historico.fitness:
                    mejor_historico = self._copy_individual(mejor_actual)
                    generaciones_sin_mejora = 0
                else:
                    generaciones_sin_mejora += 1
                
                # Registrar estadísticas
                fitness_values = [ind.fitness for ind in poblacion]
                historial_fitness.append({
                    'generacion': generacion + 1,
                    'mejor': max(fitness_values),
                    'promedio': sum(fitness_values) / len(fitness_values),
                    'peor': min(fitness_values)
                })
                
                # Criterio de convergencia
                if generaciones_sin_mejora > 80:
                    break
                
                # Evolución de la población
                if generacion < self.generaciones - 1:
                    poblacion = self._evolve_population(poblacion, generaciones_sin_mejora)

            # Generar resultado final
            parametros_utilizados = {
                'poblacion_size': self.poblacion_size,
                'generaciones': self.generaciones,
                'prob_cruza': self.prob_cruza,
                'prob_mutacion': self.prob_mutacion,
                'elitismo_rate': self.elitismo_rate,
                'generaciones_ejecutadas': generacion + 1,
                'convergencia': generaciones_sin_mejora > 80
            }
            
            resultado = self.result_generator.generar_resultado_final(
                mejor_historico, historial_fitness, poblacion, parametros_utilizados
            )
            
            return resultado
            
        except Exception as e:
            raise GeneticAlgorithmError(f"Error en ejecución del AG: {e}")

    def _initialize_smart_population(self) -> List[Individual]:
        """Inicializar población con estrategias inteligentes"""
        poblacion = []
        
        # 40% soluciones inteligentes
        num_inteligentes = int(self.poblacion_size * 0.4)
        for _ in range(num_inteligentes):
            poblacion.append(self._generate_intelligent_solution())
        
        # 60% población diversa
        poblacion_diversa = self.initializer.inicializar_poblacion(
            self.poblacion_size - num_inteligentes
        )
        poblacion.extend(poblacion_diversa)
        
        return poblacion

    def _generate_intelligent_solution(self) -> Individual:
        """Generar solución inteligente usando gestores optimizados"""
        from ..core.capacity_manager import CapacityManager
        from ..core.assignment_validator import AssignmentValidator
        
        capacity_mgr = CapacityManager(self.data_manager)
        validator = AssignmentValidator(self.data_manager)
        
        vehiculos_asignados = []
        destinos_asignados = set()
        
        # Ordenar vehículos por capacidad (mayor a menor)
        vehiculos_ordenados = sorted(
            enumerate(self.data_manager.vehiculos_disponibles), 
            key=lambda x: x[1]['capacidad_kg'], 
            reverse=True
        )
        
        # Asignar vehículos evitando duplicados
        for vehiculo_idx, vehiculo_info in vehiculos_ordenados:
            # Buscar destino disponible
            destinos_compatibles = self.data_manager.get_destinos_disponibles_para_vehiculo(vehiculo_idx)
            
            destino_elegido = None
            for destino_info in destinos_compatibles:
                destino_id = destino_info['id_destino_perteneciente']
                if destino_id not in destinos_asignados:
                    destino_elegido = destino_info
                    destinos_asignados.add(destino_id)
                    break
            
            # Fallback si no encuentra destino único
            if destino_elegido is None:
                destino_elegido = validator.find_free_destination(destinos_asignados, vehiculo_idx)
                if destino_elegido:
                    destinos_asignados.add(destino_elegido['id_destino_perteneciente'])
            
            # Generar insumos optimizados
            if destino_elegido:
                poblacion_destino = destino_elegido.get('poblacion', 500)
                insumos = capacity_mgr.adjust_supplies_for_population(
                    vehiculo_info['capacidad_kg'], poblacion_destino
                )
                
                vehiculos_asignados.append(VehicleAssignment(
                    vehiculo_id=vehiculo_idx,
                    id_destino_ruta=destino_elegido['id_asignacion_unica'],
                    insumos=insumos
                ))
        
        return Individual(vehiculos=vehiculos_asignados)

    def _evolve_population(self, poblacion: List[Individual], generaciones_sin_mejora: int) -> List[Individual]:
        """Evolucionar población con operadores optimizados"""
        # Selección de padres
        parejas = self.selector.seleccion_por_orden(poblacion)
        
        # Cruza
        descendencia = self.crossover.crossover_population(parejas, self.prob_cruza)
        
        # Mutación adaptativa
        prob_mutacion_adaptativa = min(
            self.prob_mutacion * (1 + generaciones_sin_mejora * 0.01), 
            0.4
        )
        descendencia = self.mutation.mutate_population(descendencia, prob_mutacion_adaptativa)
        
        # Sustitución con elitismo
        nueva_poblacion = self.replacement.poda_aleatoria_conservando_mejor(
            descendencia, self.poblacion_size, self.elitismo_rate
        )
        
        return nueva_poblacion

    def _copy_individual(self, individuo: Individual) -> Individual:
        """Crear copia profunda de un individuo"""
        vehiculos_copia = []
        for asignacion in individuo.vehiculos:
            vehiculos_copia.append(VehicleAssignment(
                vehiculo_id=asignacion.vehiculo_id,
                id_destino_ruta=asignacion.id_destino_ruta,
                insumos=asignacion.insumos.copy()
            ))
        
        return Individual(vehiculos=vehiculos_copia, fitness=individuo.fitness)