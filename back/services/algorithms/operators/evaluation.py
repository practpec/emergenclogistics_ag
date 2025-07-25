from typing import List, Dict, Any, Set
from ..models import Individual

class FitnessEvaluator:
    """Evaluador de fitness optimizado con penalizaciones estrictas"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.vehiculos_disponibles = data_manager.vehiculos_disponibles
        self.mapeo_asignaciones = data_manager.mapeo_asignaciones
        self.insumos_data = data_manager.insumos_data
        self.num_insumos = data_manager.num_insumos

    def evaluar_fitness(self, individuo: Individual) -> float:
        """Evaluar fitness con análisis optimizado de duplicados"""
        fitness_total = 0.0
        peso_total_utilizado = 0.0
        combustible_total = 0.0
        localidades_atendidas = set()
        penalizaciones = 0.0
        
        destinos_asignados = self._analizar_destinos_asignados(individuo)
        duplicados = {dest_id: vehiculos for dest_id, vehiculos in destinos_asignados.items() 
                     if len(vehiculos) > 1}
        
        for destino_id, vehiculos_indices in duplicados.items():
            penalizaciones += len(vehiculos_indices) * 1500
        
        asignaciones_validas = self._marcar_asignaciones_validas(individuo, duplicados)
        
        for i, asignacion in enumerate(individuo.vehiculos):
            if not asignaciones_validas[i]:
                continue
            
            vehiculo = self.vehiculos_disponibles[asignacion.vehiculo_id]
            
            if asignacion.id_destino_ruta >= len(self.mapeo_asignaciones):
                penalizaciones += 2000
                continue
                
            mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
            
            peso_vehiculo = self._calcular_peso_insumos(asignacion.insumos)
            
            if peso_vehiculo > vehiculo['capacidad_kg']:
                exceso = peso_vehiculo - vehiculo['capacidad_kg']
                penalizaciones += exceso * 800 + 3000
                continue
            
            if not self._verificar_compatibilidad_ruta(vehiculo, mapeo_info):
                penalizaciones += 1200
                continue
            
            combustible_vehiculo = self._calcular_combustible(mapeo_info, vehiculo)
            relevancia_insumos = self._evaluar_relevancia_insumos(asignacion.insumos)
            eficiencia_poblacional = self._evaluar_eficiencia_poblacional(
                peso_vehiculo, mapeo_info['poblacion'], vehiculo
            )
            
            utilizacion = peso_vehiculo / vehiculo['capacidad_kg']
            bonificacion_utilizacion = self._calcular_bonificacion_utilizacion(utilizacion)
            
            fitness_total += relevancia_insumos * 18
            fitness_total += eficiencia_poblacional * 15
            fitness_total += bonificacion_utilizacion
            fitness_total += peso_vehiculo * 0.9
            
            peso_total_utilizado += peso_vehiculo
            combustible_total += combustible_vehiculo
            localidades_atendidas.add(mapeo_info['id_destino_perteneciente'])
        
        fitness_total += self._calcular_bonificaciones_globales(localidades_atendidas)
        
        fitness_total -= combustible_total * 0.25
        fitness_total -= self._penalizar_subutilizacion(peso_total_utilizado)
        fitness_total -= self._penalizar_vehiculos_vacios(individuo)
        
        fitness_total -= penalizaciones
        
        individuo.fitness = max(0, fitness_total)
        return individuo.fitness

    def _analizar_destinos_asignados(self, individuo: Individual) -> Dict[str, List[int]]:
        """Analizar destinos asignados y detectar duplicados"""
        destinos_asignados = {}
        
        for i, asignacion in enumerate(individuo.vehiculos):
            if asignacion.id_destino_ruta < len(self.mapeo_asignaciones):
                mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
                destino_id = mapeo_info['id_destino_perteneciente']
                
                if destino_id not in destinos_asignados:
                    destinos_asignados[destino_id] = []
                destinos_asignados[destino_id].append(i)
        
        return destinos_asignados

    def _marcar_asignaciones_validas(self, individuo: Individual, duplicados: Dict) -> List[bool]:
        """Marcar qué asignaciones son válidas (sin duplicados)"""
        asignaciones_validas = [True] * len(individuo.vehiculos)
        
        for destino_id, vehiculos_indices in duplicados.items():
            for i, vehiculo_idx in enumerate(vehiculos_indices):
                if i > 0:
                    asignaciones_validas[vehiculo_idx] = False
        
        return asignaciones_validas

    def _calcular_peso_insumos(self, insumos: List[int]) -> float:
        """Calcular peso total de insumos"""
        return sum(
            insumos[i] * self.data_manager.get_peso_insumo(i)
            for i in range(len(insumos))
        )

    def _verificar_compatibilidad_ruta(self, vehiculo: Dict, mapeo_info: Dict) -> bool:
        """Verificar si vehículo es compatible con la ruta"""
        vehiculos_permitidos = mapeo_info.get('vehiculos_permitidos', [])
        estado_ruta = mapeo_info.get('estado', 'abierta')
        
        return (estado_ruta == 'abierta' and 
                vehiculo.get('tipo', 'camioneta') in vehiculos_permitidos)

    def _calcular_combustible(self, mapeo_info: Dict, vehiculo: Dict) -> float:
        """Calcular combustible necesario"""
        return mapeo_info['distancia_km'] * vehiculo.get('consumo_litros_km', 0.15)

    def _evaluar_relevancia_insumos(self, insumos: List[int]) -> float:
        """Evaluar relevancia de insumos según prioridades del desastre"""
        relevancia_total = 0.0
        insumos_prioritarios = self.data_manager.get_insumos_prioritarios()
        
        for i, cantidad in enumerate(insumos):
            if cantidad > 0:
                peso_base = cantidad * 1.0
                
                if i in insumos_prioritarios:
                    peso_base *= 2.5
                
                relevancia_total += peso_base
        
        categorias_presentes = set()
        for i, cantidad in enumerate(insumos):
            if cantidad > 0 and i < len(self.insumos_data):
                categoria = self.insumos_data[i]['categoria']
                categorias_presentes.add(categoria)
        
        bonificacion_diversidad = len(categorias_presentes) * 25
        
        return relevancia_total + bonificacion_diversidad

    def _evaluar_eficiencia_poblacional(self, peso_insumos: float, poblacion: int, vehiculo: Dict) -> float:
        """Evaluar eficiencia poblacional mejorada"""
        if peso_insumos == 0:
            return -80
        
        capacidad_vehiculo = vehiculo['capacidad_kg']
        utilizacion = peso_insumos / capacidad_vehiculo
        
        eficiencia_score = (peso_insumos / 50) * (poblacion / 500)
        
        if utilizacion >= 0.85:
            eficiencia_score += 120
        elif utilizacion >= 0.65:
            eficiencia_score += 80
        elif utilizacion >= 0.45:
            eficiencia_score += 40
        else:
            eficiencia_score -= 40
        
        if poblacion < 200 and capacidad_vehiculo < 1500:
            eficiencia_score += 60
        elif poblacion > 800 and capacidad_vehiculo > 2000:
            eficiencia_score += 80
        elif poblacion > 800 and capacidad_vehiculo < 1500:
            eficiencia_score -= 60
        
        kg_per_persona = peso_insumos / max(poblacion, 1)
        if 0.4 <= kg_per_persona <= 1.8:
            eficiencia_score += 40
        elif kg_per_persona < 0.15:
            eficiencia_score -= 25
        
        return eficiencia_score

    def _calcular_bonificacion_utilizacion(self, utilizacion: float) -> float:
        """Calcular bonificación por utilización de capacidad"""
        if utilizacion >= 0.9:
            return 180
        elif utilizacion >= 0.75:
            return 120
        elif utilizacion >= 0.6:
            return 80
        elif utilizacion >= 0.4:
            return 40
        else:
            return 0

    def _calcular_bonificaciones_globales(self, localidades_atendidas: Set) -> float:
        """Calcular bonificaciones globales por cobertura"""
        max_destinos_posibles = len(self.data_manager.destinos_unicos)
        cobertura_destinos = len(localidades_atendidas) / max_destinos_posibles
        
        bonificacion_cobertura = cobertura_destinos * 400
        
        if len(localidades_atendidas) == max_destinos_posibles:
            bonificacion_cobertura += 300
        
        return bonificacion_cobertura

    def _penalizar_subutilizacion(self, peso_total_utilizado: float) -> float:
        """Penalizar subutilización grave"""
        capacidad_total = sum(v['capacidad_kg'] for v in self.vehiculos_disponibles)
        utilizacion_promedio = peso_total_utilizado / capacidad_total
        
        if utilizacion_promedio < 0.25:
            return 350
        elif utilizacion_promedio < 0.4:
            return 180
        else:
            return 0

    def _penalizar_vehiculos_vacios(self, individuo: Individual) -> float:
        """Penalizar vehículos sin carga"""
        vehiculos_sin_carga = sum(1 for asig in individuo.vehiculos 
                                if sum(asig.insumos) == 0)
        return vehiculos_sin_carga * 250