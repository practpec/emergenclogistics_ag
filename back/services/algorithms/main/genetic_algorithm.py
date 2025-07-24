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
    """Algoritmo genético refactorizado para optimización logística"""
    
    def __init__(self, scenario_data: Dict[str, Any], parametros_ag: Dict[str, Any] = None):
        super().__init__()
        
        self.data_manager = AlgorithmDataManager(scenario_data)
        self._configure_parameters(parametros_ag)
        self._initialize_operators()

    def _configure_parameters(self, parametros_ag: Dict[str, Any] = None):
        """Configurar parámetros del algoritmo genético"""
        defaults = {
            'poblacion_size': 80,
            'generaciones': 500, 
            'prob_cruza': 0.85, 
            'prob_mutacion': 0.20, 
            'elitismo_rate': 0.15  
        }
        
        limits = {
            'poblacion_size': {'min': 20, 'max': 100},
            'generaciones': {'min': 50, 'max': 1000},
            'prob_cruza': {'min': 0.5, 'max': 1.0},
            'prob_mutacion': {'min': 0.05, 'max': 0.4},
            'elitismo_rate': {'min': 0.05, 'max': 0.3}
        }
        
        if parametros_ag:
            for param, value in parametros_ag.items():
                if param in defaults:
                    min_val = limits[param]['min']
                    max_val = limits[param]['max']
                    
                    if min_val <= value <= max_val:
                        setattr(self, param, value)
                    else:
                        setattr(self, param, defaults[param])
                        self.log_warning(f"Parámetro {param} fuera de rango, usando default: {defaults[param]}")
                else:
                    self.log_warning(f"Parámetro desconocido: {param}")
        else:
            for param, value in defaults.items():
                setattr(self, param, value)
        
        # Log de configuración
        stats = self.data_manager.get_summary_stats()
        self.log_info(f"AG configurado - Población: {self.poblacion_size}, Generaciones: {self.generaciones}")
        self.log_info(f"Datos: {stats['num_vehiculos']} vehículos, {stats['num_destinos_unicos']} destinos únicos")

    def _initialize_operators(self):
        """Inicializar operadores simplificados con data_manager"""
        self.initializer = PopulationInitializer(
            self.data_manager.num_vehiculos, 
            self.data_manager.mapeo_asignaciones, 
            self.data_manager.vehiculos_disponibles,
            self.data_manager.insumos_data, 
            self.data_manager.num_insumos, 
            self.data_manager.categorias_map, 
            self.data_manager.desastre_info
        )
        
        self.evaluator = FitnessEvaluator(
            self.data_manager.vehiculos_disponibles, 
            self.data_manager.mapeo_asignaciones, 
            self.data_manager.insumos_data, 
            self.data_manager.rutas_estado, 
            self.data_manager.desastre_info
        )
        
        self.selector = ParentSelector()
        self.crossover = CrossoverOperator(self.data_manager)
        self.mutation = MutationOperator(self.data_manager)
        self.replacement = ReplacementOperator()
        
        self.result_generator = ResultGenerator(
            self.data_manager.vehiculos_disponibles, 
            self.data_manager.mapeo_asignaciones,
            self.data_manager.insumos_data, 
            self.data_manager.rutas_estado
        )

    def ejecutar(self) -> Dict[str, Any]:
        """Ejecutar algoritmo genético con operadores simplificados"""
        try:
            self.log_info("Iniciando ejecución del algoritmo genético")
            
            # Inicialización mejorada
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
                fitness_promedio = sum(ind.fitness for ind in poblacion) / len(poblacion)
                fitness_mejor = mejor_historico.fitness
                fitness_peor = min(ind.fitness for ind in poblacion)
                
                historial_fitness.append({
                    'generacion': generacion + 1,
                    'mejor': fitness_mejor,
                    'promedio': fitness_promedio,
                    'peor': fitness_peor
                })
                
                if generacion % 50 == 0:
                    self.log_info(f"Generación {generacion}: Mejor={fitness_mejor:.2f}, Promedio={fitness_promedio:.2f}")
                
                if generaciones_sin_mejora > 100:
                    self.log_info(f"Convergencia en generación {generacion}")
                    break
                
                if generacion < self.generaciones - 1:
                    poblacion = self._evolve_population(poblacion, generaciones_sin_mejora)

            parametros_utilizados = {
                'poblacion_size': self.poblacion_size,
                'generaciones': self.generaciones,
                'prob_cruza': self.prob_cruza,
                'prob_mutacion': self.prob_mutacion,
                'elitismo_rate': self.elitismo_rate,
                'generaciones_ejecutadas': generacion + 1,
                'convergencia': generaciones_sin_mejora > 100
            }
            
            resultado = self.result_generator.generar_resultado_final(
                mejor_historico, historial_fitness, poblacion, parametros_utilizados
            )
            
            self.log_info(f"AG completado: {generacion + 1} generaciones, fitness: {mejor_historico.fitness:.2f}")
            return resultado
            
        except Exception as e:
            self.log_error("Error ejecutando algoritmo genético", e)
            raise GeneticAlgorithmError(f"Error en ejecución del AG: {e}")

    def _initialize_smart_population(self) -> List[Individual]:
        """Inicializar población con estrategias inteligentes"""
        poblacion = []
        
        # 30% soluciones inteligentes usando data_manager
        num_inteligentes = int(self.poblacion_size * 0.3)
        for _ in range(num_inteligentes):
            poblacion.append(self._generate_intelligent_solution())
        
        # 70% población aleatoria
        poblacion_aleatoria = self.initializer.inicializar_poblacion(
            self.poblacion_size - num_inteligentes
        )
        poblacion.extend(poblacion_aleatoria)
        
        return poblacion

    def _generate_intelligent_solution(self) -> Individual:
        """Generar solución inteligente usando data_manager"""
        from ..core.capacity_manager import CapacityManager
        from ..core.assignment_validator import AssignmentValidator
        
        capacity_mgr = CapacityManager(self.data_manager)
        validator = AssignmentValidator(self.data_manager)
        
        vehiculos_asignados = []
        destinos_asignados = set()
        
        # Ordenar vehículos por capacidad
        vehiculos_ordenados = sorted(
            enumerate(self.data_manager.vehiculos_disponibles), 
            key=lambda x: x[1]['capacidad_kg'], 
            reverse=True
        )
        
        # Asignar vehículos a destinos únicos
        for vehiculo_idx, vehiculo_info in vehiculos_ordenados:
            # Buscar destino disponible
            destinos_compatibles = self.data_manager.get_destinos_disponibles_para_vehiculo(vehiculo_idx)
            
            # Encontrar destino no usado
            destino_elegido = None
            for destino_info in destinos_compatibles:
                destino_id = destino_info['id_destino_perteneciente']
                if destino_id not in destinos_asignados:
                    destino_elegido = destino_info
                    destinos_asignados.add(destino_id)
                    break
            
            # Si no encuentra, usar destino libre
            if destino_elegido is None:
                destino_elegido = validator.find_free_destination(destinos_asignados, vehiculo_idx)
                if destino_elegido:
                    destinos_asignados.add(destino_elegido['id_destino_perteneciente'])
            
            # Generar insumos optimizados
            insumos = capacity_mgr.generate_optimized_supplies(vehiculo_info['capacidad_kg'])
            
            vehiculos_asignados.append(VehicleAssignment(
                vehiculo_id=vehiculo_idx,
                id_destino_ruta=destino_elegido['id_asignacion_unica'] if destino_elegido else 0,
                insumos=insumos
            ))
        
        return Individual(vehiculos=vehiculos_asignados)

    def _evolve_population(self, poblacion: List[Individual], generaciones_sin_mejora: int) -> List[Individual]:
        """Evolucionar población usando operadores simplificados"""
        # Selección
        parejas = self.selector.seleccion_por_orden(poblacion)
        
        # Cruza con operadores refactorizados
        descendencia = self.crossover.crossover_population(parejas, self.prob_cruza)
        
        # Mutación adaptativa con operadores refactorizados
        prob_mutacion_adaptativa = self.prob_mutacion * (1 + generaciones_sin_mejora * 0.01)
        descendencia = self.mutation.mutate_population(
            descendencia, 
            min(prob_mutacion_adaptativa, 0.4)
        )
        
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