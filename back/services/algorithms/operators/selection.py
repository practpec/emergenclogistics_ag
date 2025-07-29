import random
from typing import List, Tuple
from ..models import *


class SelectionOperator:
    """Operador de selección para el algoritmo genético"""
    
    def seleccion_torneo(self, poblacion: List[Tuple[Individual, float]], 
                        tamaño_torneo: int = 3) -> Individual:
        """Selección por torneo"""
        if not poblacion:
            return []
        
        participantes = random.sample(poblacion, min(tamaño_torneo, len(poblacion)))
        mejor = max(participantes, key=lambda x: x[1])
        return mejor[0]
    
    def seleccion_elitista(self, poblacion: List[Tuple[Individual, float]], 
                          tamaño_elite: int) -> List[Individual]:
        """Selección elitista - retorna los mejores individuos"""
        if not poblacion:
            return []
        
        poblacion_ordenada = sorted(poblacion, key=lambda x: x[1], reverse=True)
        return [individuo[0] for individuo in poblacion_ordenada[:tamaño_elite]]