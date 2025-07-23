import random
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from core.base_service import BaseService
from core.exceptions import GeneticAlgorithmError
from services.data.static_data_service import StaticDataService

@dataclass
class VehicleAssignment:
    """Asignación individual de vehículo"""
    vehiculo_id: int
    id_destino_ruta: int
    insumos: List[int]  # Cantidades de cada tipo de insumo

@dataclass
class Individual:
    """Individuo del algoritmo genético"""
    vehiculos: List[VehicleAssignment]
    fitness: float = 0.0

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
        
        # Configurar parámetros del AG (usar custom o default)
        self._configure_ag_parameters(parametros_ag)

    def _load_static_data(self):
        """Cargar datos estáticos desde JSON"""
        try:
            # Cargar insumos individuales desde el JSON existente
            import json
            import os
            
            insumos_path = "entities/data/categorias_insumos.json"
            with open(insumos_path, 'r', encoding='utf-8') as f:
                self.insumos_data = json.load(f)
            
            self.num_insumos = len(self.insumos_data)  # 25 insumos individuales
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
        # Vehículos disponibles
        self.vehiculos_disponibles = self.scenario_config['vehiculos_disponibles']
        self.num_vehiculos = len(self.vehiculos_disponibles)
        
        # Tipo de desastre y prioridades
        self.tipo_desastre = self.scenario_config['tipo_desastre']
        self.desastre_info = next(
            (d for d in self.tipos_desastre if d.tipo == self.tipo_desastre), 
            None
        )
        
        # Mapeo de asignaciones destino-ruta
        self.mapeo_asignaciones = self._create_route_mapping()
        
        # Estados de rutas
        self.rutas_estado = {r['ruta_id']: r for r in self.scenario_config['rutas_estado']}
        
    def _configure_ag_parameters(self, parametros_ag: Dict[str, Any] = None):
        """Configurar parámetros del algoritmo genético"""
        # Parámetros por defecto
        defaults = {
            'poblacion_size': 50,
            'generaciones': 100,
            'prob_cruza': 0.8,
            'prob_mutacion': 0.15,
            'elitismo_rate': 0.1
        }
        
        # Límites de validación
        limits = {
            'poblacion_size': {'min': 20, 'max': 100},
            'generaciones': {'min': 50, 'max': 300},
            'prob_cruza': {'min': 0.5, 'max': 1.0},
            'prob_mutacion': {'min': 0.05, 'max': 0.3},
            'elitismo_rate': {'min': 0.05, 'max': 0.2}
        }
        
        # Usar parámetros custom si se proporcionan, sino usar defaults
        if parametros_ag:
            for param, value in parametros_ag.items():
                if param in defaults:
                    # Validar límites
                    min_val = limits[param]['min']
                    max_val = limits[param]['max']
                    
                    if min_val <= value <= max_val:
                        setattr(self, param, value)
                        self.log_info(f"Parámetro {param} configurado: {value}")
                    else:
                        setattr(self, param, defaults[param])
                        self.log_warning(f"Parámetro {param} fuera de rango ({min_val}-{max_val}), usando default: {defaults[param]}")
                else:
                    self.log_warning(f"Parámetro desconocido ignorado: {param}")
        else:
            # Usar todos los defaults
            for param, value in defaults.items():
                setattr(self, param, value)
        
        self.log_info(f"AG configurado - Población: {self.poblacion_size}, Generaciones: {self.generaciones}, "
                     f"Cruza: {self.prob_cruza}, Mutación: {self.prob_mutacion}, Elitismo: {self.elitismo_rate}")

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

    def inicializar_poblacion(self) -> List[Individual]:
        """Generar población inicial"""
        poblacion = []
        
        for _ in range(self.poblacion_size):
            vehiculos_asignados = []
            vehiculos_disponibles_ids = list(range(self.num_vehiculos))
            
            for vehiculo_idx in vehiculos_disponibles_ids:
                # Asignar destino-ruta aleatoriamente
                asignacion = random.choice(self.mapeo_asignaciones)
                id_destino_ruta = asignacion['id_asignacion_unica']
                
                # Generar cantidades de insumos aleatorias
                vehiculo_info = self.vehiculos_disponibles[vehiculo_idx]
                capacidad_kg = vehiculo_info['capacidad_kg']
                insumos = self._generar_insumos_aleatorios(capacidad_kg)
                
                vehiculos_asignados.append(VehicleAssignment(
                    vehiculo_id=vehiculo_idx,
                    id_destino_ruta=id_destino_ruta,
                    insumos=insumos
                ))
            
            individuo = Individual(vehiculos=vehiculos_asignados)
            poblacion.append(individuo)
        
        return poblacion

    def _generar_insumos_aleatorios(self, capacidad_kg: float) -> List[int]:
        """Generar cantidades aleatorias de insumos respetando capacidad"""
        insumos = [0] * self.num_insumos
        peso_restante = capacidad_kg
        
        # Obtener insumos prioritarios por categoría
        insumos_prioritarios = self._get_insumos_prioritarios()
        
        # Distribuir insumos prioritarios primero
        for insumo_id in insumos_prioritarios:
            insumo_info = self.insumos_data[insumo_id]
            peso_unitario = insumo_info['peso_kg']
            
            if peso_unitario > 0 and peso_restante > peso_unitario:
                max_cantidad = min(8, int(peso_restante / peso_unitario))
                if max_cantidad > 0:
                    cantidad = random.randint(0, max_cantidad)
                    insumos[insumo_id] = cantidad
                    peso_restante -= cantidad * peso_unitario
        
        # Completar con otros insumos si queda capacidad
        insumos_restantes = [i for i in range(self.num_insumos) if i not in insumos_prioritarios]
        random.shuffle(insumos_restantes)
        
        for insumo_id in insumos_restantes:
            if peso_restante <= 0:
                break
            
            insumo_info = self.insumos_data[insumo_id]
            peso_unitario = insumo_info['peso_kg']
            
            if peso_unitario > 0 and peso_restante > peso_unitario:
                max_cantidad = min(4, int(peso_restante / peso_unitario))
                if max_cantidad > 0:
                    cantidad = random.randint(0, max_cantidad)
                    insumos[insumo_id] = cantidad
                    peso_restante -= cantidad * peso_unitario
        
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

    def evaluar_fitness(self, individuo: Individual) -> float:
        """Evaluar fitness de un individuo"""
        fitness_total = 0.0
        peso_total_utilizado = 0.0
        combustible_total = 0.0
        localidades_atendidas = set()
        penalizaciones = 0.0
        
        for asignacion in individuo.vehiculos:
            vehiculo = self.vehiculos_disponibles[asignacion.vehiculo_id]
            mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
            
            # Calcular peso de insumos usando datos reales
            peso_insumos = sum(
                asignacion.insumos[i] * self.insumos_data[i]['peso_kg']
                for i in range(self.num_insumos)
            )
            
            # Penalización por sobrecarga
            if peso_insumos > vehiculo['capacidad_kg']:
                penalizaciones += (peso_insumos - vehiculo['capacidad_kg']) * 100
                peso_insumos = vehiculo['capacidad_kg']  # Límite máximo
            
            # Verificar compatibilidad de ruta
            ruta_id = f"Destino{mapeo_info['id_destino_perteneciente']}-Ruta{mapeo_info['id_ruta_en_destino'] + 1}"
            estado_ruta = self.rutas_estado.get(ruta_id, {'estado': 'abierta', 'vehiculos_permitidos': [vehiculo['tipo']]})
            
            if estado_ruta['estado'] == 'cerrada' or vehiculo['tipo'] not in estado_ruta['vehiculos_permitidos']:
                penalizaciones += 1000  # Penalización fuerte por ruta inválida
                continue
            
            # Calcular combustible
            distancia_km = mapeo_info['distancia_km']
            combustible = distancia_km * vehiculo['consumo_litros_km']
            combustible_total += combustible
            
            # Evaluar relevancia de insumos
            relevancia_insumos = self._evaluar_relevancia_insumos(asignacion.insumos)
            
            # Evaluar eficiencia poblacional
            poblacion_destino = mapeo_info['poblacion']
            eficiencia_poblacional = self._evaluar_eficiencia_poblacional(peso_insumos, poblacion_destino, vehiculo)
            
            # Contribución positiva al fitness
            fitness_total += relevancia_insumos * 10
            fitness_total += eficiencia_poblacional * 5
            fitness_total += peso_insumos * 0.1  # Incentivar uso de capacidad
            
            peso_total_utilizado += peso_insumos
            localidades_atendidas.add(mapeo_info['id_destino_perteneciente'])
        
        # Bonificaciones
        cobertura_localidades = len(localidades_atendidas) / len(set(m['id_destino_perteneciente'] for m in self.mapeo_asignaciones))
        fitness_total += cobertura_localidades * 100
        
        # Penalizaciones
        fitness_total -= combustible_total * 0.5  # Penalizar consumo de combustible
        fitness_total -= penalizaciones
        
        # Penalizar subutilización grave
        utilizacion_promedio = peso_total_utilizado / sum(v['capacidad_kg'] for v in self.vehiculos_disponibles)
        if utilizacion_promedio < 0.3:
            fitness_total -= 200
        
        individuo.fitness = max(0, fitness_total)
        return individuo.fitness

    def _evaluar_relevancia_insumos(self, insumos: List[int]) -> float:
        """Evaluar relevancia de insumos según el tipo de desastre"""
        if not self.desastre_info:
            return sum(insumos) * 0.5
        
        relevancia_total = 0.0
        for i, cantidad in enumerate(insumos):
            if cantidad > 0:
                insumo_info = self.insumos_data[i]
                categoria = insumo_info['categoria']
                prioridad = self.desastre_info.get_priority_weight(categoria)
                relevancia_total += cantidad * prioridad
        
        return relevancia_total

    def _evaluar_eficiencia_poblacional(self, peso_insumos: float, poblacion: int, vehiculo: Dict) -> float:
        """Evaluar eficiencia según población del destino"""
        if poblacion < 20:
            # Localidades pequeñas: penalizar vehículos grandes
            if vehiculo['tipo'] == 'camión ligero' and peso_insumos > vehiculo['capacidad_kg'] * 0.3:
                return -50  # Penalización por uso ineficiente
            elif vehiculo['tipo'] == 'camioneta pickup':
                return 20  # Bonificación por uso apropiado
        
        elif poblacion > 500:
            # Localidades grandes: bonificar vehículos grandes con buena carga
            if vehiculo['tipo'] == 'camión ligero' and peso_insumos > vehiculo['capacidad_kg'] * 0.7:
                return 30
        
        return peso_insumos / 100  # Valor base proporcional al peso

    def seleccion_por_orden(self, poblacion: List[Individual]) -> List[Tuple[Individual, Individual]]:
        """Selección por ordenamiento - emparejar contiguos"""
        poblacion_ordenada = sorted(poblacion, key=lambda x: x.fitness, reverse=True)
        parejas = []
        
        for i in range(0, len(poblacion_ordenada) - 1, 2):
            if i + 1 < len(poblacion_ordenada):
                parejas.append((poblacion_ordenada[i], poblacion_ordenada[i + 1]))
        
        # Si número impar, emparejar último con el mejor
        if len(poblacion_ordenada) % 2 != 0:
            parejas.append((poblacion_ordenada[-1], poblacion_ordenada[0]))
        
        return parejas

    def cruza_puntos_aleatorios(self, parejas: List[Tuple[Individual, Individual]]) -> List[Individual]:
        """Cruza con cantidad aleatoria de puntos en posiciones aleatorias"""
        descendencia = []
        
        for padre1, padre2 in parejas:
            if random.random() < self.prob_cruza:
                # Crear hijos copiando padres
                hijo1_vehiculos = []
                hijo2_vehiculos = []
                
                for i in range(self.num_vehiculos):
                    # Cruza para asignación destino-ruta y insumos por separado
                    if random.random() < 0.5:
                        # Destino-ruta del padre1, insumos pueden cruzarse
                        hijo1_vehiculos.append(VehicleAssignment(
                            vehiculo_id=i,
                            id_destino_ruta=padre1.vehiculos[i].id_destino_ruta,
                            insumos=self._cruzar_insumos(padre1.vehiculos[i].insumos, padre2.vehiculos[i].insumos)
                        ))
                        hijo2_vehiculos.append(VehicleAssignment(
                            vehiculo_id=i,
                            id_destino_ruta=padre2.vehiculos[i].id_destino_ruta,
                            insumos=self._cruzar_insumos(padre2.vehiculos[i].insumos, padre1.vehiculos[i].insumos)
                        ))
                    else:
                        # Intercambiar completamente
                        hijo1_vehiculos.append(VehicleAssignment(
                            vehiculo_id=i,
                            id_destino_ruta=padre2.vehiculos[i].id_destino_ruta,
                            insumos=padre2.vehiculos[i].insumos.copy()
                        ))
                        hijo2_vehiculos.append(VehicleAssignment(
                            vehiculo_id=i,
                            id_destino_ruta=padre1.vehiculos[i].id_destino_ruta,
                            insumos=padre1.vehiculos[i].insumos.copy()
                        ))
                
                descendencia.extend([
                    Individual(vehiculos=hijo1_vehiculos),
                    Individual(vehiculos=hijo2_vehiculos)
                ])
            else:
                # Copiar padres sin cruza
                descendencia.extend([
                    Individual(vehiculos=[VehicleAssignment(v.vehiculo_id, v.id_destino_ruta, v.insumos.copy()) for v in padre1.vehiculos]),
                    Individual(vehiculos=[VehicleAssignment(v.vehiculo_id, v.id_destino_ruta, v.insumos.copy()) for v in padre2.vehiculos])
                ])
        
        return descendencia

    def _cruzar_insumos(self, insumos1: List[int], insumos2: List[int]) -> List[int]:
        """Cruza de insumos con puntos aleatorios"""
        if len(insumos1) != len(insumos2):
            return insumos1.copy()
        
        num_puntos = random.randint(1, min(3, len(insumos1) - 1))
        puntos = sorted(random.sample(range(1, len(insumos1)), num_puntos))
        
        resultado = insumos1.copy()
        intercambiar = True
        inicio = 0
        
        for punto in puntos + [len(insumos1)]:
            if intercambiar:
                resultado[inicio:punto] = insumos2[inicio:punto]
            intercambiar = not intercambiar
            inicio = punto
        
        return resultado

    def mutacion_mover_segmento(self, poblacion: List[Individual]) -> List[Individual]:
        """Mutación moviendo segmentos de insumos y cambiando asignaciones"""
        for individuo in poblacion:
            if random.random() < self.prob_mutacion:
                vehiculo_idx = random.randint(0, self.num_vehiculos - 1)
                
                # Mutar asignación destino-ruta
                if random.random() < 0.3:
                    nueva_asignacion = random.choice(self.mapeo_asignaciones)
                    individuo.vehiculos[vehiculo_idx].id_destino_ruta = nueva_asignacion['id_asignacion_unica']
                
                # Mutar insumos
                insumos = individuo.vehiculos[vehiculo_idx].insumos
                if len(insumos) > 2:
                    # Mover segmento
                    longitud_segmento = random.randint(1, min(3, len(insumos) // 2))
                    pos_inicial = random.randint(0, len(insumos) - longitud_segmento)
                    segmento = insumos[pos_inicial:pos_inicial + longitud_segmento]
                    
                    # Remover segmento
                    nuevo_insumos = insumos[:pos_inicial] + insumos[pos_inicial + longitud_segmento:]
                    
                    # Insertar en nueva posición
                    nueva_pos = random.randint(0, len(nuevo_insumos))
                    resultado = nuevo_insumos[:nueva_pos] + segmento + nuevo_insumos[nueva_pos:]
                    
                    individuo.vehiculos[vehiculo_idx].insumos = resultado
                
                # Reparar capacidad si es necesario
                self._reparar_capacidad(individuo.vehiculos[vehiculo_idx])
        
        return poblacion

    def _reparar_capacidad(self, asignacion: VehicleAssignment):
        """Reparar asignación que excede capacidad del vehículo"""
        vehiculo = self.vehiculos_disponibles[asignacion.vehiculo_id]
        capacidad_kg = vehiculo['capacidad_kg']
        
        peso_actual = sum(
            asignacion.insumos[i] * self.insumos_data[i]['peso_kg']
            for i in range(len(asignacion.insumos))
        )
        
        if peso_actual > capacidad_kg:
            # Reducir cantidades proporcionalmente
            factor_reduccion = capacidad_kg / peso_actual
            for i in range(len(asignacion.insumos)):
                asignacion.insumos[i] = int(asignacion.insumos[i] * factor_reduccion)

    def poda_aleatoria_conservando_mejor(self, poblacion: List[Individual]) -> List[Individual]:
        """Poda eliminando aleatoriamente pero conservando al mejor"""
        if len(poblacion) <= self.poblacion_size:
            return poblacion
        
        # Conservar élite
        poblacion_ordenada = sorted(poblacion, key=lambda x: x.fitness, reverse=True)
        elite_size = int(self.poblacion_size * self.elitismo_rate)
        elite = poblacion_ordenada[:elite_size]
        
        # Selección aleatoria del resto
        resto = poblacion_ordenada[elite_size:]
        seleccionados_resto = random.sample(resto, self.poblacion_size - elite_size)
        
        return elite + seleccionados_resto

    def ejecutar(self) -> Dict[str, Any]:
        """Ejecutar el algoritmo genético"""
        try:
            self.log_info("Iniciando ejecución del algoritmo genético")
            
            # Inicialización
            poblacion = self.inicializar_poblacion()
            mejor_historico = None
            historial_fitness = []
            
            for generacion in range(self.generaciones):
                # Evaluación
                for individuo in poblacion:
                    self.evaluar_fitness(individuo)
                
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
                
                if generacion < self.generaciones - 1:  # No procesar en última generación
                    # Selección
                    parejas = self.seleccion_por_orden(poblacion)
                    
                    # Cruza
                    descendencia = self.cruza_puntos_aleatorios(parejas)
                    
                    # Mutación
                    descendencia = self.mutacion_mover_segmento(descendencia)
                    
                    # Poda/Sustitución
                    poblacion = self.poda_aleatoria_conservando_mejor(descendencia)
            
            # Generar resultado final con población completa
            resultado = self._generar_resultado_final(mejor_historico, historial_fitness, poblacion)
            
            self.log_info(f"AG completado: {self.generaciones} generaciones, mejor fitness: {mejor_historico.fitness:.2f}")
            return resultado
            
        except Exception as e:
            self.log_error("Error ejecutando algoritmo genético", e)
            raise GeneticAlgorithmError(f"Error en ejecución del AG: {e}")

    def _generar_resultado_final(self, mejor_individuo: Individual, historial: List[Dict], poblacion_final: List[Individual]) -> Dict[str, Any]:
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
            'parametros_ag': {
                'poblacion_size': self.poblacion_size,
                'generaciones': self.generaciones,
                'prob_cruza': self.prob_cruza,
                'prob_mutacion': self.prob_mutacion,
                'elitismo_rate': self.elitismo_rate
            },
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
        metricas_eficiencia = {}
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
        comparacion_rutas = []
        
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
        
        if variacion < promedio_final * 0.01:  # Variación menor al 1%
            estado = 'CONVERGIDO'
        elif variacion < promedio_final * 0.05:  # Variación menor al 5%
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