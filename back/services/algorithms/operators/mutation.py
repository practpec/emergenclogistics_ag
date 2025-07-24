import random
from typing import List
from ..models import Individual

class MutationOperator:
    """Operador de mutación optimizado"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def mutate_population(self, poblacion: List[Individual], prob_mutacion: float) -> List[Individual]:
        """Aplicar mutación a la población con reparación automática"""
        for individuo in poblacion:
            if random.random() < prob_mutacion:
                self._apply_mutation_strategy(individuo)
            
            # Reparación automática obligatoria
            self._repair_individual(individuo)
        
        return poblacion

    def _apply_mutation_strategy(self, individuo: Individual):
        """Aplicar estrategia de mutación aleatoria"""
        estrategias = [
            'reassign_duplicates',
            'swap_destinations', 
            'optimize_supplies',
            'rebalance_loads'
        ]
        
        estrategia = random.choice(estrategias)
        
        if estrategia == 'reassign_duplicates':
            self._mutation_reassign_duplicates(individuo)
        elif estrategia == 'swap_destinations':
            self._mutation_swap_destinations(individuo)
        elif estrategia == 'optimize_supplies':
            self._mutation_optimize_supplies(individuo)
        elif estrategia == 'rebalance_loads':
            self._mutation_rebalance_loads(individuo)

    def _mutation_reassign_duplicates(self, individuo: Individual):
        """Mutación específica para eliminar duplicados"""
        from ..core.assignment_validator import AssignmentValidator
        validator = AssignmentValidator(self.data_manager)
        validator.reassign_duplicates(individuo)

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
        if not individuo.vehiculos:
            return
            
        vehiculo_idx = random.randint(0, len(individuo.vehiculos) - 1)
        asignacion = individuo.vehiculos[vehiculo_idx]
        
        from ..core.capacity_manager import CapacityManager
        capacity_mgr = CapacityManager(self.data_manager)
        
        utilizacion = capacity_mgr.get_utilization_rate(asignacion)
        capacidad = self.data_manager.get_capacidad_vehiculo(asignacion.vehiculo_id)
        
        if utilizacion < 0.5:
            # Incrementar insumos si hay capacidad
            self._increment_supplies(asignacion, capacidad)
        elif utilizacion > 0.95:
            # Redistribuir para optimizar
            self._redistribute_supplies(asignacion, capacidad)
        else:
            # Mutación normal de insumos
            self._normal_supply_mutation(asignacion)

    def _mutation_rebalance_loads(self, individuo: Individual):
        """Rebalancear cargas entre vehículos"""
        if len(individuo.vehiculos) < 2:
            return
        
        from ..core.capacity_manager import CapacityManager
        capacity_mgr = CapacityManager(self.data_manager)
        
        # Calcular utilizaciones
        utilizaciones = []
        for i, asignacion in enumerate(individuo.vehiculos):
            utilizacion = capacity_mgr.get_utilization_rate(asignacion)
            utilizaciones.append((i, utilizacion))
        
        # Ordenar por utilización
        utilizaciones.sort(key=lambda x: x[1])
        
        # Transferir del más usado al menos usado
        if len(utilizaciones) >= 2:
            menos_util_idx = utilizaciones[0][0]
            mas_util_idx = utilizaciones[-1][0]
            
            if utilizaciones[-1][1] - utilizaciones[0][1] > 0.3:
                self._transfer_supplies(
                    individuo.vehiculos[mas_util_idx],
                    individuo.vehiculos[menos_util_idx]
                )

    def _increment_supplies(self, asignacion, capacidad: float):
        """Incrementar insumos respetando capacidad"""
        peso_actual = sum(
            asignacion.insumos[i] * self.data_manager.get_peso_insumo(i)
            for i in range(len(asignacion.insumos))
        )
        peso_disponible = capacidad * 0.85 - peso_actual
        
        if peso_disponible <= 0:
            return
        
        # Incrementar insumos prioritarios
        insumos_prioritarios = self.data_manager.get_insumos_prioritarios()
        
        for insumo_id in random.sample(insumos_prioritarios, min(len(insumos_prioritarios), 3)):
            if peso_disponible <= 0:
                break
                
            peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
            if peso_unitario > 0 and peso_disponible >= peso_unitario:
                incremento_max = int(peso_disponible / peso_unitario)
                incremento = min(incremento_max, 3)
                
                if incremento > 0:
                    asignacion.insumos[insumo_id] += incremento
                    peso_disponible -= incremento * peso_unitario

    def _redistribute_supplies(self, asignacion, capacidad: float):
        """Redistribuir insumos para peso objetivo"""
        peso_objetivo = capacidad * 0.80
        
        # Calcular total actual
        total_actual = sum(asignacion.insumos)
        if total_actual == 0:
            return
        
        # Redistribuir proporcionalmente
        factor_reduccion = 0.85
        for i in range(len(asignacion.insumos)):
            if asignacion.insumos[i] > 0:
                nueva_cantidad = int(asignacion.insumos[i] * factor_reduccion)
                asignacion.insumos[i] = max(1, nueva_cantidad)

    def _normal_supply_mutation(self, asignacion):
        """Mutación normal de insumos"""
        num_mutaciones = random.randint(1, min(4, len(asignacion.insumos)))
        indices_mutar = random.sample(range(len(asignacion.insumos)), num_mutaciones)
        
        for idx in indices_mutar:
            if random.random() < 0.6:
                # Incrementar
                incremento = random.randint(1, 2)
                asignacion.insumos[idx] += incremento
            else:
                # Decrementar
                decremento = random.randint(1, 2)
                asignacion.insumos[idx] = max(0, asignacion.insumos[idx] - decremento)

    def _transfer_supplies(self, asignacion_origen, asignacion_destino):
        """Transferir insumos entre vehículos"""
        capacidad_destino = self.data_manager.get_capacidad_vehiculo(asignacion_destino.vehiculo_id)
        peso_actual_destino = sum(
            asignacion_destino.insumos[i] * self.data_manager.get_peso_insumo(i)
            for i in range(len(asignacion_destino.insumos))
        )
        capacidad_disponible = capacidad_destino * 0.85 - peso_actual_destino
        
        if capacidad_disponible <= 0:
            return
        
        # Transferir algunos insumos
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
                        
                        break

    def _repair_individual(self, individuo: Individual):
        """Reparar individuo después de mutación"""
        from ..core.capacity_manager import CapacityManager
        from ..core.assignment_validator import AssignmentValidator
        
        capacity_mgr = CapacityManager(self.data_manager)
        validator = AssignmentValidator(self.data_manager)
        
        # Reparar capacidades
        for asignacion in individuo.vehiculos:
            capacity_mgr.repair_capacity_violation(asignacion)
        
        # Reparar duplicados
        validator.reassign_duplicates(individuo)