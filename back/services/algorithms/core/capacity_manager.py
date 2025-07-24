import random
from typing import List, Dict
from ..models import VehicleAssignment

class CapacityManager:
    """Gestor optimizado para operaciones de capacidad y reparación de peso"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def repair_capacity_violation(self, asignacion: VehicleAssignment):
        """Reparar violación de capacidad con estrategia agresiva"""
        vehiculo_id = asignacion.vehiculo_id
        capacidad_kg = self.data_manager.get_capacidad_vehiculo(vehiculo_id)
        
        peso_actual = self._calculate_weight(asignacion.insumos)
        
        if peso_actual > capacidad_kg:
            peso_objetivo = capacidad_kg * 0.90
            self._reduce_weight_to_target(asignacion, peso_objetivo)
    
    def _calculate_weight(self, insumos: List[int]) -> float:
        """Calcular peso total de insumos"""
        return sum(
            insumos[i] * self.data_manager.get_peso_insumo(i)
            for i in range(len(insumos))
        )
    
    def _reduce_weight_to_target(self, asignacion: VehicleAssignment, peso_objetivo: float):
        """Reducir peso hasta alcanzar objetivo específico"""
        peso_actual = self._calculate_weight(asignacion.insumos)
        
        if peso_actual <= peso_objetivo:
            return
        
        # Reducción proporcional inicial
        if peso_actual > 0:
            factor_reduccion = peso_objetivo / peso_actual
            for i in range(len(asignacion.insumos)):
                if asignacion.insumos[i] > 0:
                    nueva_cantidad = int(asignacion.insumos[i] * factor_reduccion)
                    asignacion.insumos[i] = max(0, nueva_cantidad)
        
        # Ajuste fino por eliminación selectiva
        peso_ajustado = self._calculate_weight(asignacion.insumos)
        intentos = 0
        
        while peso_ajustado > peso_objetivo and intentos < 50:
            indices_con_insumos = [i for i, cant in enumerate(asignacion.insumos) if cant > 0]
            if not indices_con_insumos:
                break
            
            # Priorizar eliminación de insumos pesados
            pesos_totales = []
            for idx in indices_con_insumos:
                peso_total_insumo = asignacion.insumos[idx] * self.data_manager.get_peso_insumo(idx)
                pesos_totales.append((idx, peso_total_insumo))
            
            pesos_totales.sort(key=lambda x: x[1], reverse=True)
            idx_reducir = pesos_totales[0][0]
            
            peso_unitario = self.data_manager.get_peso_insumo(idx_reducir)
            asignacion.insumos[idx_reducir] -= 1
            peso_ajustado -= peso_unitario
            intentos += 1
        
        # Limpieza final si aún excede
        if peso_ajustado > peso_objetivo:
            asignacion.insumos = [0] * len(asignacion.insumos)
    
    def generate_optimized_supplies(self, capacidad_kg: float) -> List[int]:
        """Generar insumos optimizados respetando capacidad estrictamente"""
        insumos = [0] * self.data_manager.num_insumos
        peso_maximo = capacidad_kg * 0.92
        peso_restante = peso_maximo
        
        insumos_prioritarios = self.data_manager.get_insumos_prioritarios()
        
        # Fase 1: Insumos prioritarios
        insumos_prioritarios_mezclados = insumos_prioritarios.copy()
        random.shuffle(insumos_prioritarios_mezclados)
        
        for insumo_id in insumos_prioritarios_mezclados:
            if peso_restante <= 0:
                break
                
            peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
            if peso_unitario > 0 and peso_restante >= peso_unitario:
                max_cantidad_teorica = int(peso_restante / peso_unitario)
                max_cantidad_practica = min(max_cantidad_teorica, 12)
                
                if max_cantidad_practica > 0:
                    cantidad = random.randint(1, max_cantidad_practica)
                    peso_asignado = cantidad * peso_unitario
                    
                    if peso_asignado <= peso_restante:
                        insumos[insumo_id] = cantidad
                        peso_restante -= peso_asignado
        
        # Fase 2: Completar con otros insumos
        otros_insumos = [i for i in range(self.data_manager.num_insumos) 
                        if i not in insumos_prioritarios]
        random.shuffle(otros_insumos)
        
        for insumo_id in otros_insumos:
            if peso_restante <= 0:
                break
                
            peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
            if peso_unitario > 0 and peso_restante >= peso_unitario:
                max_cantidad = min(int(peso_restante / peso_unitario), 6)
                
                if max_cantidad > 0:
                    cantidad = random.randint(1, max_cantidad)
                    peso_asignado = cantidad * peso_unitario
                    
                    if peso_asignado <= peso_restante:
                        insumos[insumo_id] = cantidad
                        peso_restante -= peso_asignado
        
        # Verificación final de capacidad
        self._ensure_capacity_compliance(insumos, capacidad_kg)
        return insumos
    
    def _ensure_capacity_compliance(self, insumos: List[int], capacidad_kg: float):
        """Asegurar cumplimiento estricto de capacidad"""
        peso_total = self._calculate_weight_from_list(insumos)
        
        while peso_total > capacidad_kg and sum(insumos) > 0:
            # Encontrar insumo con mayor peso total
            pesos_por_insumo = []
            for i in range(len(insumos)):
                if insumos[i] > 0:
                    peso_total_insumo = insumos[i] * self.data_manager.get_peso_insumo(i)
                    pesos_por_insumo.append((i, peso_total_insumo))
            
            if pesos_por_insumo:
                pesos_por_insumo.sort(key=lambda x: x[1], reverse=True)
                insumo_a_reducir = pesos_por_insumo[0][0]
                insumos[insumo_a_reducir] = max(0, insumos[insumo_a_reducir] - 1)
                peso_total = self._calculate_weight_from_list(insumos)
            else:
                break
    
    def _calculate_weight_from_list(self, insumos: List[int]) -> float:
        """Calcular peso desde lista de insumos"""
        return sum(insumos[i] * self.data_manager.get_peso_insumo(i) 
                  for i in range(len(insumos)))
    
    def adjust_supplies_for_population(self, capacidad_kg: float, poblacion: int) -> List[int]:
        """Generar insumos apropiados para tamaño de población"""
        insumos = [0] * self.data_manager.num_insumos
        
        # Factor de escala basado en población
        factor_poblacion = min(poblacion / 400, 2.5)
        peso_objetivo = capacidad_kg * random.uniform(0.75, 0.95) * factor_poblacion
        peso_objetivo = min(peso_objetivo, capacidad_kg * 0.95)
        
        peso_restante = peso_objetivo
        insumos_prioritarios = self.data_manager.get_insumos_prioritarios()
        
        for insumo_id in insumos_prioritarios:
            if peso_restante <= 0:
                break
                
            peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
            if peso_unitario > 0 and peso_restante > peso_unitario:
                base_cantidad = max(1, int(poblacion / 80))
                max_cantidad = min(int(peso_restante / peso_unitario), base_cantidad * 3)
                
                if max_cantidad > 0:
                    cantidad = random.randint(1, max_cantidad)
                    insumos[insumo_id] = cantidad
                    peso_restante -= cantidad * peso_unitario
        
        self._ensure_capacity_compliance(insumos, capacidad_kg)
        return insumos
    
    def get_utilization_rate(self, asignacion: VehicleAssignment) -> float:
        """Calcular tasa de utilización de capacidad"""
        peso_actual = self._calculate_weight(asignacion.insumos)
        capacidad = self.data_manager.get_capacidad_vehiculo(asignacion.vehiculo_id)
        return peso_actual / capacidad if capacidad > 0 else 0
    
    def is_overloaded(self, asignacion: VehicleAssignment, tolerance: float = 0.02) -> bool:
        """Verificar si un vehículo está sobrecargado"""
        utilization = self.get_utilization_rate(asignacion)
        return utilization > (1.0 + tolerance)
    
    def optimize_load_distribution(self, asignacion: VehicleAssignment):
        """Optimizar distribución de carga en un vehículo"""
        capacidad = self.data_manager.get_capacidad_vehiculo(asignacion.vehiculo_id)
        utilizacion_actual = self.get_utilization_rate(asignacion)
        
        if utilizacion_actual < 0.6:
            # Incrementar carga eficientemente
            self._increase_load_efficiently(asignacion, capacidad)
        elif utilizacion_actual > 0.95:
            # Optimizar sin exceder capacidad
            self._optimize_without_exceeding(asignacion, capacidad)
    
    def _increase_load_efficiently(self, asignacion: VehicleAssignment, capacidad: float):
        """Incrementar carga de manera eficiente"""
        peso_actual = self._calculate_weight(asignacion.insumos)
        peso_disponible = capacidad * 0.90 - peso_actual
        
        if peso_disponible <= 0:
            return
        
        insumos_prioritarios = self.data_manager.get_insumos_prioritarios()
        
        for insumo_id in insumos_prioritarios:
            if peso_disponible <= 0:
                break
                
            peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
            if peso_unitario > 0 and peso_disponible >= peso_unitario:
                incremento_max = int(peso_disponible / peso_unitario)
                incremento = min(incremento_max, 5)
                
                if incremento > 0:
                    asignacion.insumos[insumo_id] += incremento
                    peso_disponible -= incremento * peso_unitario
    
    def _optimize_without_exceeding(self, asignacion: VehicleAssignment, capacidad: float):
        """Optimizar sin exceder capacidad"""
        peso_objetivo = capacidad * 0.88
        self._reduce_weight_to_target(asignacion, peso_objetivo)