import random
import copy
from typing import List, Tuple
from core.base_service import BaseService
from ..models import Individual, AsignacionVehiculo

class CrossoverOperator(BaseService):
    """Operador de cruza para algoritmo genético"""
    
    def __init__(self):
        super().__init__()
    
    def cruzar_individuos(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Cruza dos individuos para generar descendencia"""
        try:
            if not padre1 or not padre2:
                return self._clonar_individuo(padre1), self._clonar_individuo(padre2)
            
            # Cruza de asignaciones vehículo-ruta
            hijo1_asignaciones = []
            hijo2_asignaciones = []
            
            # Obtener todas las rutas y vehículos de ambos padres
            rutas_padre1 = {asig.ruta_id: asig for asig in padre1}
            rutas_padre2 = {asig.ruta_id: asig for asig in padre2}
            vehiculos_padre1 = {asig.vehiculo_id: asig for asig in padre1}
            vehiculos_padre2 = {asig.vehiculo_id: asig for asig in padre2}
            
            todas_rutas = set(rutas_padre1.keys()) | set(rutas_padre2.keys())
            
            vehiculos_usados_h1 = set()
            vehiculos_usados_h2 = set()
            rutas_asignadas_h1 = set()
            rutas_asignadas_h2 = set()
            
            # Cruza por rutas
            for ruta_id in todas_rutas:
                asig1 = rutas_padre1.get(ruta_id)
                asig2 = rutas_padre2.get(ruta_id)
                
                # Hijo 1: intentar tomar del padre1, si no del padre2
                if asig1 and asig1.vehiculo_id not in vehiculos_usados_h1 and ruta_id not in rutas_asignadas_h1:
                    hijo1_asignaciones.append(self._clonar_asignacion(asig1))
                    vehiculos_usados_h1.add(asig1.vehiculo_id)
                    rutas_asignadas_h1.add(ruta_id)
                elif asig2 and asig2.vehiculo_id not in vehiculos_usados_h1 and ruta_id not in rutas_asignadas_h1:
                    hijo1_asignaciones.append(self._clonar_asignacion(asig2))
                    vehiculos_usados_h1.add(asig2.vehiculo_id)
                    rutas_asignadas_h1.add(ruta_id)
                
                # Hijo 2: intentar tomar del padre2, si no del padre1
                if asig2 and asig2.vehiculo_id not in vehiculos_usados_h2 and ruta_id not in rutas_asignadas_h2:
                    hijo2_asignaciones.append(self._clonar_asignacion(asig2))
                    vehiculos_usados_h2.add(asig2.vehiculo_id)
                    rutas_asignadas_h2.add(ruta_id)
                elif asig1 and asig1.vehiculo_id not in vehiculos_usados_h2 and ruta_id not in rutas_asignadas_h2:
                    hijo2_asignaciones.append(self._clonar_asignacion(asig1))
                    vehiculos_usados_h2.add(asig1.vehiculo_id)
                    rutas_asignadas_h2.add(ruta_id)
            
            # Cruza de insumos para asignaciones válidas
            for asig_h1 in hijo1_asignaciones:
                asig_padre1 = rutas_padre1.get(asig_h1.ruta_id)
                asig_padre2 = rutas_padre2.get(asig_h1.ruta_id)
                
                if asig_padre1 and asig_padre2:
                    asig_h1.insumos = self._cruzar_insumos(asig_padre1.insumos, asig_padre2.insumos)
                    asig_h1.peso_total_kg = self._calcular_peso_total(asig_h1.insumos)
            
            for asig_h2 in hijo2_asignaciones:
                asig_padre1 = rutas_padre1.get(asig_h2.ruta_id)
                asig_padre2 = rutas_padre2.get(asig_h2.ruta_id)
                
                if asig_padre1 and asig_padre2:
                    asig_h2.insumos = self._cruzar_insumos(asig_padre2.insumos, asig_padre1.insumos)
                    asig_h2.peso_total_kg = self._calcular_peso_total(asig_h2.insumos)
            
            return hijo1_asignaciones, hijo2_asignaciones
            
        except Exception as e:
            self.log_error("Error en cruza", e)
            return self._clonar_individuo(padre1), self._clonar_individuo(padre2)
    
    def _cruzar_insumos(self, insumos1: List[int], insumos2: List[int]) -> List[int]:
        """Cruza las cantidades de insumos"""
        if not insumos1 or not insumos2:
            return insumos1 or insumos2 or []
        
        # Asegurar mismo tamaño
        tamaño = max(len(insumos1), len(insumos2))
        insumos1_ext = insumos1 + [0] * (tamaño - len(insumos1))
        insumos2_ext = insumos2 + [0] * (tamaño - len(insumos2))
        
        # Cruza uniforme
        resultado = []
        for i in range(tamaño):
            if random.random() < 0.5:
                resultado.append(insumos1_ext[i])
            else:
                resultado.append(insumos2_ext[i])
        
        return resultado
    
    def _calcular_peso_total(self, cantidades_insumos: List[int]) -> float:
        """Calcular peso total aproximado (necesitaría acceso a lista de insumos)"""
        # Peso promedio estimado por insumo: 5kg
        return sum(cantidades_insumos) * 5.0
    
    def _clonar_individuo(self, individuo: Individual) -> Individual:
        """Clonar un individuo completo"""
        if not individuo:
            return []
        
        return [self._clonar_asignacion(asig) for asig in individuo]
    
    def _clonar_asignacion(self, asignacion: AsignacionVehiculo) -> AsignacionVehiculo:
        """Clonar una asignación"""
        return AsignacionVehiculo(
            vehiculo_id=asignacion.vehiculo_id,
            ruta_id=asignacion.ruta_id,
            insumos=asignacion.insumos.copy() if asignacion.insumos else [],
            peso_total_kg=asignacion.peso_total_kg,
            distancia_km=asignacion.distancia_km,
            combustible_usado=asignacion.combustible_usado
        )