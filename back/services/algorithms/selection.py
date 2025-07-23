from typing import List, Tuple
from .models import Individual

class ParentSelector:
    """Paso 3: Selección de padres"""
    
    def seleccion_por_orden(self, poblacion: List[Individual]) -> List[Tuple[Individual, Individual]]:
        """Selección por ordenamiento - emparejar contiguos"""
        poblacion_ordenada = sorted(poblacion, key=lambda x: x.fitness, reverse=True)
        parejas = []
        
        for i in range(0, len(poblacion_ordenada) - 1, 2):
            if i + 1 < len(poblacion_ordenada):
                parejas.append((poblacion_ordenada[i], poblacion_ordenada[i + 1]))
        
        # Si número impar, emparejar último con el mejor
        if len(poblacion_ordenada) % 2 != 0:
            parejas.append((poblacion_ordenada[-1], poblacion_ordenada[0]))
        
        return parejas