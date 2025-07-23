# algorithms/evaluation.py
from typing import List, Dict, Any
from .models import Individual

class FitnessEvaluator:
    """Paso 2: Evaluación de fitness"""
    
    def __init__(self, vehiculos_disponibles: List[Dict], mapeo_asignaciones: List[Dict],
                 insumos_data: List[Dict], rutas_estado: Dict, desastre_info: Any = None):
        self.vehiculos_disponibles = vehiculos_disponibles
        self.mapeo_asignaciones = mapeo_asignaciones
        self.insumos_data = insumos_data
        self.rutas_estado = rutas_estado
        self.desastre_info = desastre_info
        self.num_insumos = len(insumos_data)

    def evaluar_fitness(self, individuo: Individual) -> float:
        """Evaluar fitness de un individuo"""
        fitness_total = 0.0
        peso_total_utilizado = 0.0
        combustible_total = 0.0
        localidades_atendidas = set()
        penalizaciones = 0.0
        
        # Para penalizar destinos repetidos por diferentes vehículos
        destinos_asignados_en_individuo = set() #

        for asignacion in individuo.vehiculos:
            vehiculo = self.vehiculos_disponibles[asignacion.vehiculo_id]
            mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
            
            # Penalización por destino repetido por otro vehículo en el mismo individuo
            id_destino_actual = mapeo_info['id_destino_perteneciente'] #
            if id_destino_actual in destinos_asignados_en_individuo: #
                penalizaciones += 500  # Penalización fuerte por redundancia de destino
            destinos_asignados_en_individuo.add(id_destino_actual) #

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
            fitness_total += eficiencia_poblacional * 10 # Aumentado el peso para esta bonificación
            fitness_total += peso_insumos * 0.5  # Incentivar más el uso de capacidad
            
            peso_total_utilizado += peso_insumos
            localidades_atendidas.add(mapeo_info['id_destino_perteneciente'])
        
        # Bonificaciones
        cobertura_localidades = len(localidades_atendidas) / len(set(m['id_destino_perteneciente'] for m in self.mapeo_asignaciones))
        fitness_total += cobertura_localidades * 100
        
        # Penalizaciones
        fitness_total -= combustible_total * 0.5  # Penalizar consumo de combustible
        fitness_total -= penalizaciones
        
        # Penalizar subutilización grave (ajustado el umbral y penalización)
        utilizacion_promedio = peso_total_utilizado / sum(v['capacidad_kg'] for v in self.vehiculos_disponibles)
        if utilizacion_promedio < 0.5: # Umbral más alto para penalizar subutilización
            fitness_total -= 300 # Penalización aumentada
        
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
        """Evaluar eficiencia según población del destino y capacidad del vehículo"""
        eficiencia_score = peso_insumos / 100 # Valor base proporcional al peso

        # Bonificar/penalizar por la relación capacidad-población
        capacidad_vehiculo = vehiculo['capacidad_kg'] #

        if poblacion < 50: # Población pequeña
            if capacidad_vehiculo < 1000: # Vehículo de baja capacidad
                eficiencia_score += 50 # Bonificación por buena coincidencia
            else: # Vehículo de alta capacidad para población pequeña
                eficiencia_score -= 80 # Penalización

        elif poblacion > 500: # Población grande
            if capacidad_vehiculo > 1500: # Vehículo de alta capacidad
                eficiencia_score += 70 # Bonificación por buena coincidencia
            else: # Vehículo de baja capacidad para población grande
                eficiencia_score -= 100 # Penalización fuerte
        
        return eficiencia_score