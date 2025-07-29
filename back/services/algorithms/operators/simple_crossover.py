import random
from typing import List, Tuple
from core.base_service import BaseService
from ..models import Individual, AsignacionVehiculo

class SimpleCrossoverOperator(BaseService):  
    def __init__(self):
        super().__init__()
    
    def cruza_simple(self, parejas: List[Tuple[Individual, Individual]], prob_cruza: float = 0.8) -> List[Individual]:
        descendencia = []
        
        for padre1, padre2 in parejas:
            if random.random() < prob_cruza:
                hijo1, hijo2 = self._cruzar_individuos_simple(padre1, padre2)
                descendencia.extend([hijo1, hijo2])
            else:
                descendencia.extend([self._clonar_individuo(padre1), self._clonar_individuo(padre2)])
        
        return descendencia
    
    def _cruzar_individuos_simple(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        max_size = max(len(padre1), len(padre2))
        
        padre1_ext = self._extender_individuo(padre1, max_size)
        padre2_ext = self._extender_individuo(padre2, max_size)
        
        hijo1 = []
        hijo2 = []
        
        for i in range(max_size):
            asig1 = padre1_ext[i] if i < len(padre1_ext) else None
            asig2 = padre2_ext[i] if i < len(padre2_ext) else None
            
            if asig1 and asig2:
                if random.random() < 0.5:

                    nueva_asig1 = AsignacionVehiculo(
                        vehiculo_id=asig1.vehiculo_id,
                        ruta_id=asig2.ruta_id,
                        insumos=self._mezclar_insumos(asig1.insumos, asig2.insumos),
                        peso_total_kg=0,
                        distancia_km=asig2.distancia_km,
                        combustible_usado=0
                    )
    
                    nueva_asig2 = AsignacionVehiculo(
                        vehiculo_id=asig2.vehiculo_id,
                        ruta_id=asig1.ruta_id,
                        insumos=self._mezclar_insumos(asig2.insumos, asig1.insumos),
                        peso_total_kg=0,
                        distancia_km=asig1.distancia_km,
                        combustible_usado=0
                    )
                else:
                    nueva_asig1 = AsignacionVehiculo(
                        vehiculo_id=asig2.vehiculo_id,
                        ruta_id=asig1.ruta_id,
                        insumos=self._mezclar_insumos(asig2.insumos, asig1.insumos),
                        peso_total_kg=0,
                        distancia_km=asig1.distancia_km,
                        combustible_usado=0
                    )
                    nueva_asig2 = AsignacionVehiculo(
                        vehiculo_id=asig1.vehiculo_id,
                        ruta_id=asig2.ruta_id,
                        insumos=self._mezclar_insumos(asig1.insumos, asig2.insumos),
                        peso_total_kg=0,
                        distancia_km=asig2.distancia_km,
                        combustible_usado=0
                    )
                
                hijo1.append(nueva_asig1)
                hijo2.append(nueva_asig2)
            
            elif asig1:
                hijo1.append(self._clonar_asignacion(asig1))
                hijo2.append(self._clonar_asignacion(asig1))
            elif asig2:
                hijo1.append(self._clonar_asignacion(asig2))
                hijo2.append(self._clonar_asignacion(asig2))
        
        return hijo1, hijo2
    
    def _mezclar_insumos(self, insumos1: List[int], insumos2: List[int]) -> List[int]:
        TOTAL_INSUMOS = 25
        
        insumos1_completo = (insumos1 + [0] * TOTAL_INSUMOS)[:TOTAL_INSUMOS]
        insumos2_completo = (insumos2 + [0] * TOTAL_INSUMOS)[:TOTAL_INSUMOS]
        
        resultado = []
        for i in range(TOTAL_INSUMOS):
            if random.random() < 0.5:
                resultado.append(insumos1_completo[i])
            else:
                resultado.append(insumos2_completo[i])
        
        return resultado
    
    def _extender_individuo(self, individuo: Individual, tamaño_objetivo: int) -> Individual:
        if len(individuo) >= tamaño_objetivo:
            return individuo
        
        individuo_extendido = individuo.copy()
        while len(individuo_extendido) < tamaño_objetivo:
            if individuo:
                asig_copia = self._clonar_asignacion(random.choice(individuo))
                individuo_extendido.append(asig_copia)
            else:
                break
        
        return individuo_extendido
    
    def _clonar_individuo(self, individuo: Individual) -> Individual:
        return [self._clonar_asignacion(asig) for asig in individuo]
    
    def _clonar_asignacion(self, asignacion: AsignacionVehiculo) -> AsignacionVehiculo:
        return AsignacionVehiculo(
            vehiculo_id=asignacion.vehiculo_id,
            ruta_id=asignacion.ruta_id,
            insumos=asignacion.insumos.copy() if asignacion.insumos else [],
            peso_total_kg=asignacion.peso_total_kg,
            distancia_km=asignacion.distancia_km,
            combustible_usado=asignacion.combustible_usado
        )