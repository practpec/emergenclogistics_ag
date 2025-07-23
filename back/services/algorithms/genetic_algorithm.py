import json
from typing import List, Dict, Any
from core.base_service import BaseService
from core.exceptions import GeneticAlgorithmError
from services.data.static_data_service import StaticDataService

from .models import Individual, VehicleAssignment
from .initialization import PopulationInitializer
from .evaluation import FitnessEvaluator
from .selection import ParentSelector
from .crossover import CrossoverOperator
from .mutation import MutationOperator
from .replacement import ReplacementOperator
from .results import ResultGenerator

class LogisticsGeneticAlgorithm(BaseService):
    """Algoritmo genético para optimización logística de emergencias"""
    
    def __init__(self, scenario_data: Dict[str, Any], parametros_ag: Dict[str, Any] = None):
        super().__init__()
        self.static_data_service = StaticDataService()
        
        # Extraer datos del escenario
        self.map_data = scenario_data['map_data']
        self.scenario_config = scenario_data['scenario_config']
        
        # Cargar datos estáticos
        self._load_static_data()
        
        # Procesar datos del escenario
        self._process_scenario_data()
        
        # Configurar parámetros del AG
        self._configure_ag_parameters(parametros_ag)
        
        # Inicializar operadores del AG
        self._initialize_operators()

    def _load_static_data(self):
        """Cargar datos estáticos desde JSON"""
        try:
            insumos_path = "entities/data/categorias_insumos.json"
            with open(insumos_path, 'r', encoding='utf-8') as f:
                self.insumos_data = json.load(f)
            
            self.num_insumos = len(self.insumos_data)
            self.tipos_desastre = self.static_data_service.get_all_disasters()
            
            # Crear mapeo de categorías para evaluación
            self.categorias_map = {}
            for insumo in self.insumos_data:
                categoria = insumo['categoria']
                if categoria not in self.categorias_map:
                    self.categorias_map[categoria] = []
                self.categorias_map[categoria].append(insumo['id_insumo'])
            
            self.log_info(f"Datos estáticos cargados: {self.num_insumos} insumos individuales")
        except Exception as e:
            self.log_error("Error cargando datos estáticos", e)
            raise GeneticAlgorithmError(f"Error cargando datos estáticos: {e}")

    def _process_scenario_data(self):
        """Procesar datos del escenario recibido del frontend"""
        self.vehiculos_disponibles = self.scenario_config['vehiculos_disponibles']
        self.num_vehiculos = len(self.vehiculos_disponibles)
        
        self.tipo_desastre = self.scenario_config['tipo_desastre']
        self.desastre_info = next(
            (d for d in self.tipos_desastre if d.tipo == self.tipo_desastre), 
            None
        )
        
        self.mapeo_asignaciones = self._create_route_mapping()
        self.rutas_estado = {r['ruta_id']: r for r in self.scenario_config['rutas_estado']}

    def _configure_ag_parameters(self, parametros_ag: Dict[str, Any] = None):
        """Configurar parámetros del algoritmo genético"""
        defaults = {
            'poblacion_size': 50,
            'generaciones': 100,
            'prob_cruza': 0.8,
            'prob_mutacion': 0.15,
            'elitismo_rate': 0.1
        }
        
        limits = {
            'poblacion_size': {'min': 20, 'max': 100},
            'generaciones': {'min': 50, 'max': 300},
            'prob_cruza': {'min': 0.5, 'max': 1.0},
            'prob_mutacion': {'min': 0.05, 'max': 0.3},
            'elitismo_rate': {'min': 0.05, 'max': 0.2}
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
                        self.log_warning(f"Parámetro {param} fuera de rango ({min_val}-{max_val}), usando default: {defaults[param]}")
                else:
                    self.log_warning(f"Parámetro desconocido ignorado: {param}")
        else:
            for param, value in defaults.items():
                setattr(self, param, value)
        
        self.log_info(f"AG configurado - Población: {self.poblacion_size}, Generaciones: {self.generaciones}")

    def _initialize_operators(self):
        """Inicializar operadores del algoritmo genético"""
        self.initializer = PopulationInitializer(
            self.num_vehiculos, self.mapeo_asignaciones, self.vehiculos_disponibles,
            self.insumos_data, self.num_insumos, self.categorias_map, self.desastre_info
        )
        
        self.evaluator = FitnessEvaluator(
            self.vehiculos_disponibles, self.mapeo_asignaciones, 
            self.insumos_data, self.rutas_estado, self.desastre_info
        )
        
        self.selector = ParentSelector()
        
        self.crossover = CrossoverOperator(self.num_vehiculos)
        
        self.mutation = MutationOperator(
            self.num_vehiculos, self.mapeo_asignaciones, 
            self.vehiculos_disponibles, self.insumos_data
        )
        
        self.replacement = ReplacementOperator()
        
        self.result_generator = ResultGenerator(
            self.vehiculos_disponibles, self.mapeo_asignaciones,
            self.insumos_data, self.rutas_estado
        )

    def _create_route_mapping(self) -> List[Dict[str, Any]]:
        """Crear mapeo de asignaciones destino-ruta basado en los datos del mapa"""
        mapeo = []
        asignacion_id = 0
        
        for destino_data in self.map_data['rutas_data']:
            destino_info = destino_data['destino']
            destino_id = destino_info.get('clave_localidad', destino_data['indice'])
            
            for ruta_idx, ruta in enumerate(destino_data['rutas']):
                mapeo.append({
                    'id_asignacion_unica': asignacion_id,
                    'id_destino_perteneciente': destino_id,
                    'id_ruta_en_destino': ruta_idx,
                    'distancia_km': ruta['distancia']['value'] / 1000,
                    'destino_nombre': destino_info.get('nombre_localidad', f"Destino_{destino_id}"),
                    'poblacion': destino_info.get('poblacion', 100)
                })
                asignacion_id += 1
        
        return mapeo

    def ejecutar(self) -> Dict[str, Any]:
        """Paso 7: Ejecutar el algoritmo genético (bucle principal)"""
        try:
            self.log_info("Iniciando ejecución del algoritmo genético")
            
            # Paso 1: Inicialización
            poblacion = self.initializer.inicializar_poblacion(self.poblacion_size)
            mejor_historico = None
            historial_fitness = []
            
            for generacion in range(self.generaciones):
                # Paso 2: Evaluación
                for individuo in poblacion:
                    self.evaluator.evaluar_fitness(individuo)
                
                # Tracking del mejor
                mejor_actual = max(poblacion, key=lambda x: x.fitness)
                if mejor_historico is None or mejor_actual.fitness > mejor_historico.fitness:
                    mejor_historico = Individual(
                        vehiculos=[VehicleAssignment(v.vehiculo_id, v.id_destino_ruta, v.insumos.copy()) 
                                 for v in mejor_actual.vehiculos],
                        fitness=mejor_actual.fitness
                    )
                
                fitness_promedio = sum(ind.fitness for ind in poblacion) / len(poblacion)
                historial_fitness.append({
                    'generacion': generacion + 1,
                    'mejor': mejor_historico.fitness,
                    'promedio': fitness_promedio,
                    'peor': min(ind.fitness for ind in poblacion)
                })
                
                if generacion < self.generaciones - 1:
                    # Paso 3: Selección
                    parejas = self.selector.seleccion_por_orden(poblacion)
                    
                    # Paso 4: Cruza
                    descendencia = self.crossover.cruza_puntos_aleatorios(parejas, self.prob_cruza)
                    
                    # Paso 5: Mutación
                    descendencia = self.mutation.mutacion_mover_segmento(descendencia, self.prob_mutacion)
                    
                    # Paso 6: Sustitución
                    poblacion = self.replacement.poda_aleatoria_conservando_mejor(
                        descendencia, self.poblacion_size, self.elitismo_rate
                    )
            
            # Generar resultado final
            parametros_utilizados = {
                'poblacion_size': self.poblacion_size,
                'generaciones': self.generaciones,
                'prob_cruza': self.prob_cruza,
                'prob_mutacion': self.prob_mutacion,
                'elitismo_rate': self.elitismo_rate
            }
            
            resultado = self.result_generator.generar_resultado_final(
                mejor_historico, historial_fitness, poblacion, parametros_utilizados
            )
            
            self.log_info(f"AG completado: {self.generaciones} generaciones, mejor fitness: {mejor_historico.fitness:.2f}")
            return resultado
            
        except Exception as e:
            self.log_error("Error ejecutando algoritmo genético", e)
            raise GeneticAlgorithmError(f"Error en ejecución del AG: {e}")