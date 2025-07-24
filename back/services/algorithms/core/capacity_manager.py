import random
from typing import List, Dict
from ..models import VehicleAssignment

class CapacityManager:
    """Gestor especializado para operaciones de capacidad y reparación de peso"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def repair_capacity_violation(self, asignacion: VehicleAssignment):
        """Reparar violación de capacidad - MÉTODO PRINCIPAL"""
        vehiculo_id = asignacion.vehiculo_id
        capacidad_kg = self.data_manager.get_capacidad_vehiculo(vehiculo_id)
        
        peso_actual = self._calculate_weight(asignacion.insumos)
        
        if peso_actual > capacidad_kg:
            self._aggressive_weight_reduction(asignacion, capacidad_kg * 0.85)
    
    def _calculate_weight(self, insumos: List[int]) -> float:
        """Calcular peso total de insumos"""
        return sum(
            insumos[i] * self.data_manager.get_peso_insumo(i)
            for i in range(len(insumos))
        )
    
    def _aggressive_weight_reduction(self, asignacion: VehicleAssignment, peso_objetivo: float):
        """Reducción agresiva de peso hasta alcanzar objetivo"""
        peso_actual = self._calculate_weight(asignacion.insumos)
        
        if peso_actual <= peso_objetivo:
            return
        
        # Método 1: Reducción proporcional
        if peso_actual > 0:
            factor_reduccion = peso_objetivo / peso_actual
            for i in range(len(asignacion.insumos)):
                if asignacion.insumos[i] > 0:
                    nueva_cantidad = int(asignacion.insumos[i] * factor_reduccion)
                    asignacion.insumos[i] = max(0, nueva_cantidad)
        
        # Método 2: Verificación y ajuste fino
        peso_ajustado = self._calculate_weight(asignacion.insumos)
        intentos = 0
        
        while peso_ajustado > peso_objetivo and intentos < 50:
            indices_con_insumos = [i for i, cant in enumerate(asignacion.insumos) if cant > 0]
            if not indices_con_insumos:
                break
            
            # Priorizar reducir insumos con mayor peso total
            pesos_insumos = []
            for idx in indices_con_insumos:
                peso_total = asignacion.insumos[idx] * self.data_manager.get_peso_insumo(idx)
                pesos_insumos.append((idx, peso_total))
            
            pesos_insumos.sort(key=lambda x: x[1], reverse=True)
            idx_reducir = pesos_insumos[0][0]
            
            peso_unitario = self.data_manager.get_peso_insumo(idx_reducir)
            asignacion.insumos[idx_reducir] -= 1
            peso_ajustado -= peso_unitario
            intentos += 1
        
        # Método 3: Si aún excede, resetear completamente
        if peso_ajustado > peso_objetivo:
            asignacion.insumos = [0] * len(asignacion.insumos)
    
    def generate_optimized_supplies(self, capacidad_kg: float) -> List[int]:
        """Generar insumos optimizados respetando capacidad"""
        insumos = [0] * self.data_manager.num_insumos
        peso_maximo = capacidad_kg * 0.90
        peso_restante = peso_maximo
        
        insumos_prioritarios = self.data_manager.get_insumos_prioritarios()
        
        # Ordenar insumos por prioridad y peso
        insumos_ordenados = []
        for insumo_id in insumos_prioritarios:
            peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
            insumos_ordenados.append((insumo_id, peso_unitario, True))
        
        # Añadir insumos no prioritarios
        for i in range(self.data_manager.num_insumos):
            if i not in insumos_prioritarios:
                peso_unitario = self.data_manager.get_peso_insumo(i)
                insumos_ordenados.append((i, peso_unitario, False))
        
        # Ordenar: prioritarios primero, luego por peso ascendente
        insumos_ordenados.sort(key=lambda x: (not x[2], x[1]))
        
        # Asignar cantidades usando estrategia greedy
        for insumo_id, peso_unitario, es_prioritario in insumos_ordenados:
            if peso_unitario <= 0 or peso_restante < peso_unitario:
                continue
            
            max_cantidad_teorica = int(peso_restante / peso_unitario)
            if max_cantidad_teorica <= 0:
                continue
            
            max_cantidad_practica = min(max_cantidad_teorica, 12 if es_prioritario else 6)
            
            if max_cantidad_practica > 0:
                cantidad = random.randint(1, max_cantidad_practica)
                peso_asignado = cantidad * peso_unitario
                
                if peso_asignado <= peso_restante:
                    insumos[insumo_id] = cantidad
                    peso_restante -= peso_asignado
        
        # Verificación final
        self._ensure_capacity_compliance(insumos, capacidad_kg)
        return insumos
    
    def _ensure_capacity_compliance(self, insumos: List[int], capacidad_kg: float):
        """Asegurar que los insumos no excedan la capacidad"""
        peso_total = sum(insumos[i] * self.data_manager.get_peso_insumo(i) 
                        for i in range(len(insumos)))
        
        while peso_total > capacidad_kg and sum(insumos) > 0:
            pesos_por_insumo = []
            for i in range(len(insumos)):
                if insumos[i] > 0:
                    peso_total_insumo = insumos[i] * self.data_manager.get_peso_insumo(i)
                    pesos_por_insumo.append((i, peso_total_insumo))
            
            if pesos_por_insumo:
                pesos_por_insumo.sort(key=lambda x: x[1], reverse=True)
                insumo_a_reducir = pesos_por_insumo[0][0]
                insumos[insumo_a_reducir] = max(0, insumos[insumo_a_reducir] - 1)
                peso_total = sum(insumos[i] * self.data_manager.get_peso_insumo(i) 
                               for i in range(len(insumos)))
            else:
                break
    
    def adjust_supplies_for_population(self, capacidad_kg: float, poblacion: int) -> List[int]:
        """Generar insumos apropiados para el tamaño de población"""
        insumos = [0] * self.data_manager.num_insumos
        
        factor_poblacion = min(poblacion / 500, 2.0)
        peso_objetivo = capacidad_kg * random.uniform(0.8, 0.95) * factor_poblacion
        peso_objetivo = min(peso_objetivo, capacidad_kg * 0.98)
        
        peso_restante = peso_objetivo
        insumos_prioritarios = self.data_manager.get_insumos_prioritarios()
        
        for insumo_id in insumos_prioritarios:
            if peso_restante <= 0:
                break
                
            peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
            if peso_unitario > 0 and peso_restante > peso_unitario:
                base_cantidad = max(1, int(poblacion / 100))
                max_cantidad = min(int(peso_restante / peso_unitario), base_cantidad * 2)
                
                if max_cantidad > 0:
                    cantidad = random.randint(1, max_cantidad)
                    insumos[insumo_id] = cantidad
                    peso_restante -= cantidad * peso_unitario
        
        return insumos
    
    def get_utilization_rate(self, asignacion: VehicleAssignment) -> float:
        """Calcular tasa de utilización de capacidad"""
        peso_actual = self._calculate_weight(asignacion.insumos)
        capacidad = self.data_manager.get_capacidad_vehiculo(asignacion.vehiculo_id)
        return peso_actual / capacidad if capacidad > 0 else 0
    
    def is_overloaded(self, asignacion: VehicleAssignment, tolerance: float = 0.05) -> bool:
        """Verificar si un vehículo está sobrecargado"""
        utilization = self.get_utilization_rate(asignacion)
        return utilization > (1.0 + tolerance)