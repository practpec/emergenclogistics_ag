import random
from typing import List
from ..models import Individual

class ReplacementOperator:
    """Operador de reemplazo con elitismo"""
    
    def poda_aleatoria_conservando_mejor(self, poblacion: List[Individual], 
                                       poblacion_size: int, elitismo_rate: float) -> List[Individual]:
        """Poda eliminando aleatoriamente pero conservando élite"""
        if len(poblacion) <= poblacion_size:
            return poblacion
        
        # Conservar élite
        poblacion_ordenada = sorted(poblacion, key=lambda x: x.fitness, reverse=True)
        elite_size = int(poblacion_size * elitismo_rate)
        elite = poblacion_ordenada[:elite_size]
        
        # Selección aleatoria del resto
        resto = poblacion_ordenada[elite_size:]
        seleccionados_resto = random.sample(resto, poblacion_size - elite_size)
        
        return elite + seleccionados_resto