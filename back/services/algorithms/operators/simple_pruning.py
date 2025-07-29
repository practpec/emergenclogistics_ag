import random
from typing import List, Tuple
from core.base_service import BaseService
from ..models import Individual

class SimplePruningOperator(BaseService):
    def __init__(self):
        super().__init__()
    
    def poda_aleatoria_conservando_mejor(self, poblacion_evaluada: List[Tuple[Individual, float]], 
                                       poblacion_maxima: int) -> List[Individual]:
        if len(poblacion_evaluada) <= poblacion_maxima:
            return [individuo for individuo, _ in poblacion_evaluada]
        
        if not poblacion_evaluada:
            return []
        
        mejor_individuo = max(poblacion_evaluada, key=lambda x: x[1])[0]
        
        poblacion_temp = []
        for individuo, fitness in poblacion_evaluada:
            if individuo != mejor_individuo:
                poblacion_temp.append(individuo)
        
        individuos_a_conservar = poblacion_maxima - 1
        if individuos_a_conservar < 0:
            individuos_a_conservar = 0
        
        if individuos_a_conservar >= len(poblacion_temp):
            nueva_poblacion = [mejor_individuo] + poblacion_temp
        else:
            indices_seleccionados = random.sample(range(len(poblacion_temp)), individuos_a_conservar)
            nueva_poblacion = [mejor_individuo]
            nueva_poblacion.extend([poblacion_temp[i] for i in indices_seleccionados])
        
        return nueva_poblacion