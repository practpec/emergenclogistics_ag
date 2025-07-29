import random
from typing import List
from core.base_service import BaseService
from ..models import Individual, AsignacionVehiculo

class SimpleMutationOperator(BaseService):
    def __init__(self):
        super().__init__()
    
    def mutacion_segmento_aleatorio(self, poblacion: List[Individual], prob_mutacion_ind: float = 0.15) -> List[Individual]:
        for i in range(len(poblacion)):
            if random.random() < prob_mutacion_ind:
                individuo = poblacion[i]
                if len(individuo) <= 1:
                    continue
                
                poblacion[i] = self._mutar_segmento_asignaciones(individuo)
                
                poblacion[i] = self._mutar_insumos_aleatorios(poblacion[i])
        
        return poblacion
    
    def _mutar_segmento_asignaciones(self, individuo: Individual) -> Individual:
        if len(individuo) <= 1:
            return individuo
        
        max_longitud = min(3, len(individuo))
        longitud_segmento = random.randint(2, max_longitud)
        
        if len(individuo) - longitud_segmento < 0:
            return individuo
        
        pos_inicial = random.randint(0, len(individuo) - longitud_segmento)
        
        segmento = individuo[pos_inicial:pos_inicial + longitud_segmento]
        
        segmento_reordenado = segmento.copy()
        random.shuffle(segmento_reordenado)
        
        individuo_mutado = individuo.copy()
        for j in range(longitud_segmento):
            individuo_mutado[pos_inicial + j] = segmento_reordenado[j]
        
        return individuo_mutado
    
    def _mutar_insumos_aleatorios(self, individuo: Individual) -> Individual:
        if not individuo:
            return individuo
        
        TOTAL_INSUMOS = 25
        num_asignaciones_mutar = random.randint(1, min(3, len(individuo)))
        asignaciones_a_mutar = random.sample(range(len(individuo)), num_asignaciones_mutar)
        
        for idx in asignaciones_a_mutar:
            asignacion = individuo[idx]
            
            if len(asignacion.insumos) < TOTAL_INSUMOS:
                asignacion.insumos.extend([0] * (TOTAL_INSUMOS - len(asignacion.insumos)))
            elif len(asignacion.insumos) > TOTAL_INSUMOS:
                asignacion.insumos = asignacion.insumos[:TOTAL_INSUMOS]
            
            vehiculo_id = asignacion.vehiculo_id
            capacidad_kg = 1000 

            peso_actual = sum(asignacion.insumos) * 5.0
            utilizacion_actual = (peso_actual / capacidad_kg) * 100
            
            if utilizacion_actual < 50:
                num_insumos_mutar = random.randint(3, 6)
                indices_insumos = random.sample(range(TOTAL_INSUMOS), num_insumos_mutar)
                
                for insumo_idx in indices_insumos:
                    if random.random() < 0.8:
                        asignacion.insumos[insumo_idx] = min(12, asignacion.insumos[insumo_idx] + random.randint(2, 4))
                    else:
                        asignacion.insumos[insumo_idx] = max(0, asignacion.insumos[insumo_idx] - 1)
            
            elif utilizacion_actual < 70: 
                num_insumos_mutar = random.randint(2, 4)
                indices_insumos = random.sample(range(TOTAL_INSUMOS), num_insumos_mutar)
                
                for insumo_idx in indices_insumos:
                    if random.random() < 0.7:
                        asignacion.insumos[insumo_idx] = min(10, asignacion.insumos[insumo_idx] + random.randint(1, 3))
                    else:
                        asignacion.insumos[insumo_idx] = max(0, asignacion.insumos[insumo_idx] - 1)
            
            elif utilizacion_actual > 95: 
                num_insumos_mutar = random.randint(2, 4)
                indices_insumos = random.sample(range(TOTAL_INSUMOS), num_insumos_mutar)
                
                for insumo_idx in indices_insumos:
                    if asignacion.insumos[insumo_idx] > 0:
                        asignacion.insumos[insumo_idx] = max(0, asignacion.insumos[insumo_idx] - random.randint(1, 3))
            
            else: 
                num_insumos_mutar = random.randint(1, 2)
                indices_insumos = random.sample(range(TOTAL_INSUMOS), num_insumos_mutar)
                
                for insumo_idx in indices_insumos:
                    if random.random() < 0.5:
                        asignacion.insumos[insumo_idx] = min(8, asignacion.insumos[insumo_idx] + 1)
                    else:
                        asignacion.insumos[insumo_idx] = max(0, asignacion.insumos[insumo_idx] - 1)
        
        return individuo
