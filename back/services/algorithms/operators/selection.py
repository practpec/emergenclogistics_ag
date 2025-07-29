import random
from typing import List, Tuple
from core.base_service import BaseService
from ..models import Individual

class SelectionOperator(BaseService):
    """Operador de selección para algoritmo genético"""
    
    def __init__(self):
        super().__init__()
        self.tamaño_torneo = 3
    
    def seleccion_elitista(self, poblacion_evaluada: List[Tuple[Individual, float]], tamaño_elite: int) -> List[Individual]:
        """Selección elitista - mantener los mejores individuos"""
        if not poblacion_evaluada:
            return []
        
        # Ordenar por fitness descendente
        poblacion_ordenada = sorted(poblacion_evaluada, key=lambda x: x[1], reverse=True)
        
        # Tomar los mejores
        elite = [individuo for individuo, _ in poblacion_ordenada[:tamaño_elite]]
        
        return elite
    
    def seleccion_torneo(self, poblacion_evaluada: List[Tuple[Individual, float]]) -> Individual:
        """Selección por torneo"""
        if not poblacion_evaluada:
            return []
        
        # Seleccionar candidatos aleatorios para el torneo
        tamaño_torneo = min(self.tamaño_torneo, len(poblacion_evaluada))
        candidatos = random.sample(poblacion_evaluada, tamaño_torneo)
        
        # Retornar el mejor candidato
        mejor_candidato = max(candidatos, key=lambda x: x[1])
        return mejor_candidato[0]  # Retornar solo el individuo, no la tupla
    
    def seleccion_ruleta(self, poblacion_evaluada: List[Tuple[Individual, float]]) -> Individual:
        """Selección por ruleta (proporcional al fitness)"""
        if not poblacion_evaluada:
            return []
        
        # Calcular fitness total
        fitness_total = sum(fitness for _, fitness in poblacion_evaluada)
        
        if fitness_total <= 0:
            # Si no hay fitness positivo, selección aleatoria
            return random.choice(poblacion_evaluada)[0]
        
        # Generar número aleatorio
        punto_seleccion = random.uniform(0, fitness_total)
        
        # Encontrar individuo correspondiente
        acumulado = 0
        for individuo, fitness in poblacion_evaluada:
            acumulado += fitness
            if acumulado >= punto_seleccion:
                return individuo
        
        # Fallback
        return poblacion_evaluada[-1][0]