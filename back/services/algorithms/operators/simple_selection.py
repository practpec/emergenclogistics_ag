import random
from typing import List, Tuple
from core.base_service import BaseService
from ..models import Individual

class SimpleSelectionOperator(BaseService):
    
    def __init__(self):
        super().__init__()
    
    def seleccion_por_orden(self, poblacion_evaluada: List[Tuple[Individual, float]]) -> List[Tuple[Individual, Individual]]:
        poblacion_ordenada = sorted(poblacion_evaluada, key=lambda x: x[1], reverse=True)
        
        parejas = []
        for i in range(0, len(poblacion_ordenada) - 1, 2):
            if i + 1 < len(poblacion_ordenada):
                padre1 = poblacion_ordenada[i][0]
                padre2 = poblacion_ordenada[i + 1][0]
                parejas.append((padre1, padre2))
        
        if len(poblacion_ordenada) % 2 != 0 and len(poblacion_ordenada) > 0:
            ultimo = poblacion_ordenada[-1][0]
            mejor = poblacion_ordenada[0][0]
            parejas.append((ultimo, mejor))
        
        return parejas