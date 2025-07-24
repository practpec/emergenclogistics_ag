from typing import List, Tuple
from ..models import Individual

class ParentSelector:
    """Operador de selección de padres optimizado"""
    
    def seleccion_por_orden(self, poblacion: List[Individual]) -> List[Tuple[Individual, Individual]]:
        """Selección por ordenamiento - emparejar individuos contiguos"""
        poblacion_ordenada = sorted(poblacion, key=lambda x: x.fitness, reverse=True)
        parejas = []
        
        # Emparejar contiguos
        for i in range(0, len(poblacion_ordenada) - 1, 2):
            if i + 1 < len(poblacion_ordenada):
                parejas.append((poblacion_ordenada[i], poblacion_ordenada[i + 1]))
        
        # Si número impar, emparejar último con el mejor
        if len(poblacion_ordenada) % 2 != 0:
            parejas.append((poblacion_ordenada[-1], poblacion_ordenada[0]))
        
        return parejas