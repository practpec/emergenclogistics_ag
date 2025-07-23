import random
from typing import List, Dict
from .models import Individual

class MutationOperator:
    """Paso 5: Mutación"""
    
    def __init__(self, num_vehiculos: int, mapeo_asignaciones: List[Dict],
                 vehiculos_disponibles: List[Dict], insumos_data: List[Dict]):
        self.num_vehiculos = num_vehiculos
        self.mapeo_asignaciones = mapeo_asignaciones
        self.vehiculos_disponibles = vehiculos_disponibles
        self.insumos_data = insumos_data

    def mutacion_mover_segmento(self, poblacion: List[Individual], prob_mutacion: float) -> List[Individual]:
        """Mutación moviendo segmentos de insumos y cambiando asignaciones"""
        for individuo in poblacion:
            if random.random() < prob_mutacion:
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

    def _reparar_capacidad(self, asignacion):
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