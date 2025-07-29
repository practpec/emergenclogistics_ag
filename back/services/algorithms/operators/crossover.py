import random
from typing import List, Tuple
from ..models import *


class CrossoverOperator:
    """Operador de cruzamiento para el algoritmo genético"""
    
    def cruzar_individuos(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Cruzamiento de dos individuos usando punto de corte"""
        if not padre1 or not padre2:
            return padre1.copy(), padre2.copy()
        
        # Verificar que ambos padres tengan al menos 2 elementos para cruzar
        min_len = min(len(padre1), len(padre2))
        if min_len < 2:
            # Si son muy pequeños, simplemente intercambiar
            return padre2.copy(), padre1.copy()
        
        # Punto de corte aleatorio - asegurar que esté en rango válido
        punto_corte = random.randint(1, min_len - 1)
        
        # Crear hijos intercambiando segmentos
        hijo1 = padre1[:punto_corte] + padre2[punto_corte:]
        hijo2 = padre2[:punto_corte] + padre1[punto_corte:]
        
        # Reparar conflictos (vehículos o rutas duplicadas)
        hijo1 = self._reparar_individuo(hijo1)
        hijo2 = self._reparar_individuo(hijo2)
        
        return hijo1, hijo2
    
    def _reparar_individuo(self, individuo: Individual) -> Individual:
        """Reparar individuo eliminando conflictos"""
        if not individuo:
            return individuo
        
        vehiculos_usados = set()
        rutas_usadas = set()
        individuo_reparado = []
        
        for asignacion in individuo:
            if (asignacion.vehiculo_id not in vehiculos_usados and 
                asignacion.ruta_id not in rutas_usadas):
                vehiculos_usados.add(asignacion.vehiculo_id)
                rutas_usadas.add(asignacion.ruta_id)
                individuo_reparado.append(asignacion)
        
        return individuo_reparado