import random
from typing import List, Tuple
from core.base_service import BaseService
from ..models import Individual

class SelectionOperator(BaseService):    
    def __init__(self):
        super().__init__()
        self.tamaño_torneo = 3
    
    def seleccion_elitista(self, poblacion_evaluada: List[Tuple[Individual, float]], tamaño_elite: int) -> List[Individual]:
        if not poblacion_evaluada:
            return []
        poblacion_ordenada = sorted(poblacion_evaluada, key=lambda x: x[1], reverse=True)
        
        elite = [individuo for individuo, _ in poblacion_ordenada[:tamaño_elite]]
        
        return elite
    
    def seleccion_torneo(self, poblacion_evaluada: List[Tuple[Individual, float]]) -> Individual:
        if not poblacion_evaluada:
            return []
        
        tamaño_torneo = min(self.tamaño_torneo, len(poblacion_evaluada))
        candidatos = random.sample(poblacion_evaluada, tamaño_torneo)
        
        mejor_candidato = max(candidatos, key=lambda x: x[1])
        return mejor_candidato[0]
    
    def seleccion_ruleta(self, poblacion_evaluada: List[Tuple[Individual, float]]) -> Individual:
        if not poblacion_evaluada:
            return []
        
        fitness_total = sum(fitness for _, fitness in poblacion_evaluada)
        
        if fitness_total <= 0:
            return random.choice(poblacion_evaluada)[0]
        
        punto_seleccion = random.uniform(0, fitness_total)
        
        acumulado = 0
        for individuo, fitness in poblacion_evaluada:
            acumulado += fitness
            if acumulado >= punto_seleccion:
                return individuo
        
        return poblacion_evaluada[-1][0]