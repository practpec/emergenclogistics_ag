import json
import random
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
    """Algoritmo genético mejorado para optimización logística de emergencias"""
    
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
        
        # MEJORA: Validar que hay suficientes destinos únicos
        destinos_unicos = len(set(m['id_destino_perteneciente'] for m in self.mapeo_asignaciones))
        self.log_info(f"Destinos únicos disponibles: {destinos_unicos}, Vehículos: {self.num_vehiculos}")

    def _configure_ag_parameters(self, parametros_ag: Dict[str, Any] = None):
        """Configurar parámetros del algoritmo genético mejorado"""
        defaults = {
            'poblacion_size': 80,  # Reducido para mejor convergencia
            'generaciones': 500,   # Reducido para enfoque en calidad
            'prob_cruza': 0.85,    # Aumentado para mejor exploración
            'prob_mutacion': 0.20, # Aumentado para mejor diversidad
            'elitismo_rate': 0.15  # Aumentado para conservar mejores soluciones
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
                        self.log_warning(f"Parámetro {param} fuera de rango ({min_val}-{max_val}), usando default: {defaults[param]}")
                else:
                    self.log_warning(f"Parámetro desconocido ignorado: {param}")
        else:
            for param, value in defaults.items():
                setattr(self, param, value)
        
        self.log_info(f"AG configurado - Población: {self.poblacion_size}, Generaciones: {self.generaciones}")

    def _initialize_operators(self):
        """Inicializar operadores del algoritmo genético mejorado"""
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

    def _generar_solucion_inteligente(self) -> Individual:
        """Generar una solución inicial más inteligente"""
        vehiculos_asignados = []
        destinos_asignados = set()
        
        # Ordenar vehículos por capacidad (mayor a menor)
        vehiculos_ordenados = sorted(
            enumerate(self.vehiculos_disponibles), 
            key=lambda x: x[1]['capacidad_kg'], 
            reverse=True
        )
        
        # Ordenar destinos por población (mayor a menor)
        destinos_ordenados = sorted(
            self.mapeo_asignaciones, 
            key=lambda x: x['poblacion'], 
            reverse=True
        )
        
        # Asignar vehículos a destinos únicos
        for vehiculo_idx, vehiculo_info in vehiculos_ordenados:
            # Buscar destino no asignado
            asignacion_elegida = None
            for mapeo_info in destinos_ordenados:
                destino_id = mapeo_info['id_destino_perteneciente']
                
                if destino_id not in destinos_asignados:
                    # Verificar compatibilidad de ruta
                    ruta_id = f"Destino{destino_id}-Ruta{mapeo_info['id_ruta_en_destino'] + 1}"
                    estado_ruta = self.rutas_estado.get(ruta_id, {
                        'estado': 'abierta', 
                        'vehiculos_permitidos': [vehiculo_info['tipo']]
                    })
                    
                    if (estado_ruta['estado'] == 'abierta' and 
                        vehiculo_info['tipo'] in estado_ruta['vehiculos_permitidos']):
                        asignacion_elegida = mapeo_info
                        destinos_asignados.add(destino_id)
                        break
            
            # Si no encuentra destino compatible, asignar uno aleatorio disponible
            if asignacion_elegida is None:
                destinos_disponibles = [
                    m for m in self.mapeo_asignaciones 
                    if m['id_destino_perteneciente'] not in destinos_asignados
                ]
                if destinos_disponibles:
                    asignacion_elegida = random.choice(destinos_disponibles)
                    destinos_asignados.add(asignacion_elegida['id_destino_perteneciente'])
                else:
                    # Último recurso: asignar cualquier destino
                    asignacion_elegida = random.choice(self.mapeo_asignaciones)
            
            # Generar insumos optimizados para este vehículo
            insumos = self._generar_insumos_optimizados(vehiculo_info['capacidad_kg'])
            
            vehiculos_asignados.append(VehicleAssignment(
                vehiculo_id=vehiculo_idx,
                id_destino_ruta=asignacion_elegida['id_asignacion_unica'],
                insumos=insumos
            ))
        
        return Individual(vehiculos=vehiculos_asignados)

    def _generar_insumos_optimizados(self, capacidad_kg: float) -> List[int]:
        """Generar insumos optimizados RESPETANDO ESTRICTAMENTE la capacidad"""
        insumos = [0] * self.num_insumos
        peso_maximo = capacidad_kg * 0.90  # NUNCA usar más del 90%
        peso_restante = peso_maximo
        
        # Obtener insumos prioritarios
        insumos_prioritarios = self._get_insumos_prioritarios()
        
        # Ordenar insumos por prioridad y peso (más ligeros primero para optimizar)
        insumos_ordenados = []
        for insumo_id in insumos_prioritarios:
            peso_unitario = self.insumos_data[insumo_id]['peso_kg']
            insumos_ordenados.append((insumo_id, peso_unitario, True))  # True = prioritario
        
        # Añadir insumos no prioritarios
        for i in range(self.num_insumos):
            if i not in insumos_prioritarios:
                peso_unitario = self.insumos_data[i]['peso_kg']
                insumos_ordenados.append((i, peso_unitario, False))  # False = no prioritario
        
        # Ordenar: prioritarios primero, luego por peso ascendente
        insumos_ordenados.sort(key=lambda x: (not x[2], x[1]))
        
        # Asignar cantidades usando estrategia greedy ESTRICTA
        for insumo_id, peso_unitario, es_prioritario in insumos_ordenados:
            if peso_unitario <= 0 or peso_restante < peso_unitario:
                continue
            
            # Calcular cantidad máxima SEGURA
            max_cantidad_teorica = int(peso_restante / peso_unitario)
            if max_cantidad_teorica <= 0:
                continue
            
            # Limitar cantidades para evitar concentración excesiva
            max_cantidad_practica = min(max_cantidad_teorica, 12 if es_prioritario else 6)
            
            if max_cantidad_practica > 0:
                cantidad = random.randint(1, max_cantidad_practica)
                peso_asignado = cantidad * peso_unitario
                
                # VERIFICACIÓN DOBLE de capacidad
                if peso_asignado <= peso_restante:
                    insumos[insumo_id] = cantidad
                    peso_restante -= peso_asignado
        
        # VERIFICACIÓN FINAL OBLIGATORIA
        peso_total = sum(insumos[i] * self.insumos_data[i]['peso_kg'] for i in range(self.num_insumos))
        
        # Si por alguna razón excede, corregir inmediatamente
        while peso_total > capacidad_kg and sum(insumos) > 0:
            # Encontrar insumo con mayor peso total y reducirlo
            pesos_por_insumo = []
            for i in range(self.num_insumos):
                if insumos[i] > 0:
                    peso_total_insumo = insumos[i] * self.insumos_data[i]['peso_kg']
                    pesos_por_insumo.append((i, peso_total_insumo))
            
            if pesos_por_insumo:
                # Reducir el insumo con mayor peso total
                pesos_por_insumo.sort(key=lambda x: x[1], reverse=True)
                insumo_a_reducir = pesos_por_insumo[0][0]
                insumos[insumo_a_reducir] = max(0, insumos[insumo_a_reducir] - 1)
                peso_total = sum(insumos[i] * self.insumos_data[i]['peso_kg'] for i in range(self.num_insumos))
            else:
                break  # No hay más insumos que reducir
        
        return insumos

    def _get_insumos_prioritarios(self) -> List[int]:
        """Obtener IDs de insumos prioritarios según el desastre"""
        if not self.desastre_info:
            return list(range(min(10, self.num_insumos)))
        
        insumos_prioritarios = []
        for prioridad in self.desastre_info.prioridad:
            if prioridad.nivel in ['alta', 'media']:
                categoria = prioridad.categoria
                if categoria in self.categorias_map:
                    insumos_prioritarios.extend(self.categorias_map[categoria])
        
        return insumos_prioritarios

    def ejecutar(self) -> Dict[str, Any]:
        """Ejecutar el algoritmo genético mejorado"""
        try:
            self.log_info("Iniciando ejecución del algoritmo genético mejorado")
            
            # Paso 1: Inicialización con soluciones más inteligentes
            poblacion = []
            
            # 30% de la población con soluciones inteligentes
            num_inteligentes = int(self.poblacion_size * 0.3)
            for _ in range(num_inteligentes):
                poblacion.append(self._generar_solucion_inteligente())
            
            # 70% de la población aleatoria
            poblacion_aleatoria = self.initializer.inicializar_poblacion(
                self.poblacion_size - num_inteligentes
            )
            poblacion.extend(poblacion_aleatoria)
            
            mejor_historico = None
            historial_fitness = []
            generaciones_sin_mejora = 0
            mejor_fitness_previo = 0
            
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
                    generaciones_sin_mejora = 0
                else:
                    generaciones_sin_mejora += 1
                
                fitness_promedio = sum(ind.fitness for ind in poblacion) / len(poblacion)
                fitness_mejor = mejor_historico.fitness
                fitness_peor = min(ind.fitness for ind in poblacion)
                
                historial_fitness.append({
                    'generacion': generacion + 1,
                    'mejor': fitness_mejor,
                    'promedio': fitness_promedio,
                    'peor': fitness_peor
                })
                
                # Log de progreso cada 50 generaciones
                if generacion % 50 == 0:
                    self.log_info(f"Generación {generacion}: Mejor={fitness_mejor:.2f}, Promedio={fitness_promedio:.2f}")
                
                # Criterio de parada temprana
                if generaciones_sin_mejora > 100:
                    self.log_info(f"Convergencia alcanzada en generación {generacion}")
                    break
                
                if generacion < self.generaciones - 1:
                    # Paso 3: Selección con presión adaptativa
                    presion_seleccion = min(1.5 + (generacion / self.generaciones), 2.5)
                    parejas = self.selector.seleccion_por_orden(poblacion)
                    
                    # Paso 4: Cruza mejorada
                    descendencia = self.crossover.cruza_puntos_aleatorios(parejas, self.prob_cruza)
                    
                    # Paso 5: Mutación adaptativa
                    prob_mutacion_adaptativa = self.prob_mutacion * (1 + generaciones_sin_mejora * 0.01)
                    descendencia = self.mutation.mutacion_mover_segmento(
                        descendencia, 
                        min(prob_mutacion_adaptativa, 0.4)
                    )
                    
                    # Paso 6: Sustitución con elitismo mejorado
                    elite_size = max(int(self.poblacion_size * self.elitismo_rate), 1)
                    poblacion = self.replacement.poda_aleatoria_conservando_mejor(
                        descendencia, self.poblacion_size, self.elitismo_rate
                    )
                
                mejor_fitness_previo = fitness_mejor
            
            # Generar resultado final
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
            
            self.log_info(f"AG completado: {generacion + 1} generaciones, mejor fitness: {mejor_historico.fitness:.2f}")
            return resultado
            
        except Exception as e:
            self.log_error("Error ejecutando algoritmo genético", e)
            raise GeneticAlgorithmError(f"Error en ejecución del AG: {e}")