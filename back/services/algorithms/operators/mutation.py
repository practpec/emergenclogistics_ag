import random
from typing import List
from ..models import Individual
from ..core.capacity_manager import CapacityManager
from ..core.assignment_validator import AssignmentValidator

class MutationOperator:
    """Operador de mutación refactorizado y simplificado"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.capacity_manager = CapacityManager(data_manager)
        self.validator = AssignmentValidator(data_manager)

    def mutate_population(self, poblacion: List[Individual], prob_mutacion: float) -> List[Individual]:
        """Aplicar mutación a la población con reparación automática"""
        for individuo in poblacion:
            if random.random() < prob_mutacion:
                self._apply_random_mutation(individuo)
            
            # Reparación automática OBLIGATORIA
            self._repair_individual(individuo)
        
        return poblacion

    def _apply_random_mutation(self, individuo: Individual):
        """Aplicar mutación aleatoria según estrategia"""
        tipo_mutacion = random.choice([
            'reassign_duplicates',  # 30%
            'swap_destinations',    # 25%
            'optimize_supplies',    # 25%
            'rebalance_loads'      # 20%
        ])
        
        if tipo_mutacion == 'reassign_duplicates':
            self._mutation_reassign_duplicates(individuo)
        elif tipo_mutacion == 'swap_destinations':
            self._mutation_swap_destinations(individuo)
        elif tipo_mutacion == 'optimize_supplies':
            self._mutation_optimize_supplies(individuo)
        elif tipo_mutacion == 'rebalance_loads':
            self._mutation_rebalance_loads(individuo)

    def _mutation_reassign_duplicates(self, individuo: Individual):
        """Mutación específica para eliminar duplicados"""
        self.validator.reassign_duplicates(individuo)

    def _mutation_swap_destinations(self, individuo: Individual):
        """Intercambiar destinos entre dos vehículos"""
        if len(individuo.vehiculos) < 2:
            return
        
        idx1, idx2 = random.sample(range(len(individuo.vehiculos)), 2)
        
        # Intercambiar destinos
        temp_destino = individuo.vehiculos[idx1].id_destino_ruta
        individuo.vehiculos[idx1].id_destino_ruta = individuo.vehiculos[idx2].id_destino_ruta
        individuo.vehiculos[idx2].id_destino_ruta = temp_destino

    def _mutation_optimize_supplies(self, individuo: Individual):
        """Optimizar carga de un vehículo aleatorio"""
        vehiculo_idx = random.randint(0, len(individuo.vehiculos) - 1)
        asignacion = individuo.vehiculos[vehiculo_idx]
        
        capacidad = self.data_manager.get_capacidad_vehiculo(asignacion.vehiculo_id)
        utilizacion = self.capacity_manager.get_utilization_rate(asignacion)
        
        if utilizacion < 0.6:
            # Incrementar insumos
            self._increment_supplies(asignacion, capacidad)
        elif utilizacion > 0.95:
            # Redistribuir para optimizar
            self._redistribute_supplies(asignacion, capacidad)
        else:
            # Mutación normal
            self._normal_supply_mutation(asignacion)

    def _mutation_rebalance_loads(self, individuo: Individual):
        """Rebalancear cargas entre vehículos"""
        if len(individuo.vehiculos) < 2:
            return
        
        # Calcular utilizaciones
        utilizaciones = []
        for i, asignacion in enumerate(individuo.vehiculos):
            utilizacion = self.capacity_manager.get_utilization_rate(asignacion)
            capacidad = self.data_manager.get_capacidad_vehiculo(asignacion.vehiculo_id)
            utilizaciones.append((i, utilizacion, capacidad))
        
        # Ordenar por utilización
        utilizaciones.sort(key=lambda x: x[1])
        
        # Transferir del más usado al menos usado
        menos_util_idx = utilizaciones[0][0]
        mas_util_idx = utilizaciones[-1][0]
        
        if utilizaciones[-1][1] - utilizaciones[0][1] > 0.3:
            self._transfer_supplies(
                individuo.vehiculos[mas_util_idx],
                individuo.vehiculos[menos_util_idx]
            )

    def _repair_individual(self, individuo: Individual):
        """Reparar individuo completamente"""
        # Reparar capacidades
        for asignacion in individuo.vehiculos:
            self.capacity_manager.repair_capacity_violation(asignacion)
        
        # Reparar duplicados
        self.validator.reassign_duplicates(individuo)

    def _increment_supplies(self, asignacion, capacidad: float):
        """Incrementar insumos respetando capacidad"""
        peso_actual = sum(
            asignacion.insumos[i] * self.data_manager.get_peso_insumo(i)
            for i in range(len(asignacion.insumos))
        )
        peso_disponible = capacidad * 0.9 - peso_actual
        
        if peso_disponible <= 0:
            return
        
        # Encontrar insumos incrementables
        for i, cantidad_actual in enumerate(asignacion.insumos):
            if cantidad_actual > 0:
                peso_unitario = self.data_manager.get_peso_insumo(i)
                if peso_unitario > 0 and peso_disponible >= peso_unitario:
                    incremento = min(3, int(peso_disponible / peso_unitario))
                    if incremento > 0:
                        asignacion.insumos[i] += random.randint(1, incremento)
                        peso_disponible -= incremento * peso_unitario
                        if peso_disponible <= 0:
                            break

    def _redistribute_supplies(self, asignacion, capacidad: float):
        """Redistribuir insumos para peso objetivo"""
        peso_objetivo = capacidad * 0.85
        insumos_originales = asignacion.insumos.copy()
        asignacion.insumos = [0] * len(asignacion.insumos)
        
        peso_restante = peso_objetivo
        total_original = sum(insumos_originales)
        
        if total_original > 0:
            for i, cantidad_original in enumerate(insumos_originales):
                if cantidad_original > 0 and peso_restante > 0:
                    peso_unitario = self.data_manager.get_peso_insumo(i)
                    if peso_unitario > 0:
                        proporcion = cantidad_original / total_original
                        cantidad_objetivo = int((peso_objetivo / peso_unitario) * proporcion)
                        cantidad_real = min(cantidad_objetivo, int(peso_restante / peso_unitario))
                        
                        if cantidad_real > 0:
                            asignacion.insumos[i] = cantidad_real
                            peso_restante -= cantidad_real * peso_unitario

    def _normal_supply_mutation(self, asignacion):
        """Mutación normal de insumos"""
        indices_a_mutar = random.sample(
            range(len(asignacion.insumos)), 
            random.randint(1, min(5, len(asignacion.insumos)))
        )
        
        for idx in indices_a_mutar:
            if random.random() < 0.5:
                asignacion.insumos[idx] += random.randint(1, 3)
            else:
                asignacion.insumos[idx] = max(0, asignacion.insumos[idx] - random.randint(1, 2))

    def _transfer_supplies(self, asignacion_origen, asignacion_destino):
        """Transferir insumos entre vehículos"""
        capacidad_destino = self.data_manager.get_capacidad_vehiculo(asignacion_destino.vehiculo_id)
        peso_actual_destino = sum(
            asignacion_destino.insumos[i] * self.data_manager.get_peso_insumo(i)
            for i in range(len(asignacion_destino.insumos))
        )
        capacidad_disponible = capacidad_destino * 0.9 - peso_actual_destino
        
        if capacidad_disponible <= 0:
            return
        
        # Encontrar insumos transferibles
        for i, cantidad in enumerate(asignacion_origen.insumos):
            if cantidad > 1 and capacidad_disponible > 0:
                peso_unitario = self.data_manager.get_peso_insumo(i)
                if peso_unitario > 0 and capacidad_disponible >= peso_unitario:
                    max_transferible = min(cantidad - 1, int(capacidad_disponible / peso_unitario))
                    if max_transferible > 0:
                        cantidad_transferir = random.randint(1, max_transferible)
                        
                        # Realizar transferencia
                        asignacion_origen.insumos[i] -= cantidad_transferir
                        asignacion_destino.insumos[i] += cantidad_transferir
                        capacidad_disponible -= cantidad_transferir * peso_unitario