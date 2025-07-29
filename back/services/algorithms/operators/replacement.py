from typing import List, Tuple
from ..models import *


class ReplacementOperator:
    """Operador de reemplazo para el algoritmo genético"""
    
    def reemplazo_generacional(self, poblacion_actual: List[Individual], 
                              nueva_poblacion: List[Individual]) -> List[Individual]:
        """Reemplazo generacional completo"""
        return nueva_poblacion
    
    def reemplazo_elitista(self, poblacion_evaluada: List[Tuple[Individual, float]], 
                          nueva_poblacion_evaluada: List[Tuple[Individual, float]], 
                          porcentaje_elite: float = 0.1) -> List[Individual]:
        """Reemplazo elitista conservando los mejores individuos"""
        
        # Combinar ambas poblaciones
        poblacion_total = poblacion_evaluada + nueva_poblacion_evaluada
        
        # Ordenar por fitness descendente
        poblacion_total.sort(key=lambda x: x[1], reverse=True)
        
        # Tomar los mejores individuos
        tamaño_poblacion = len(poblacion_evaluada)
        mejores = poblacion_total[:tamaño_poblacion]
        
        return [individuo[0] for individuo in mejores]
    
    def reemplazo_por_torneo(self, poblacion_actual: List[Tuple[Individual, float]], 
                            nueva_poblacion: List[Tuple[Individual, float]]) -> List[Individual]:
        """Reemplazo por torneo entre individuos actuales y nuevos"""
        poblacion_resultado = []
        
        for i in range(len(poblacion_actual)):
            individuo_actual = poblacion_actual[i]
            individuo_nuevo = nueva_poblacion[i] if i < len(nueva_poblacion) else poblacion_actual[i]
            
            # El individuo con mayor fitness gana
            if individuo_nuevo[1] > individuo_actual[1]:
                poblacion_resultado.append(individuo_nuevo[0])
            else:
                poblacion_resultado.append(individuo_actual[0])
        
        return poblacion_resultado