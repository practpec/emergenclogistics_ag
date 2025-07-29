from typing import List, Dict, Any
from core.base_service import BaseService
from ..models import Individual, AsignacionVehiculo, Insumo, TipoDesastre

class EvaluationOperator(BaseService):    
    def __init__(self, rutas: List, tipo_desastre: TipoDesastre, insumos: List[Insumo]):
        super().__init__()
        self.rutas = rutas
        self.tipo_desastre = tipo_desastre
        self.insumos = insumos
        
        self.prioridades_categoria = {}
        for prioridad in tipo_desastre.prioridades:
            self.prioridades_categoria[prioridad.categoria] = prioridad.nivel.value
    
    def evaluar_individuo(self, individuo: Individual) -> float:
        if not individuo:
            return 0.0
        
        try:
            asignaciones = individuo
    
            cobertura_rutas = self._evaluar_cobertura_rutas(asignaciones)
            eficiencia_vehiculos = self._evaluar_eficiencia_vehiculos(asignaciones)
            diversidad_insumos = self._evaluar_diversidad_insumos(asignaciones)
            prioridad_insumos = self._evaluar_prioridad_insumos(asignaciones)
            
            peso_cobertura = 0.3
            peso_eficiencia = 0.25
            peso_diversidad = 0.2
            peso_prioridad = 0.25
            
            fitness = (
                cobertura_rutas * peso_cobertura +
                eficiencia_vehiculos * peso_eficiencia +
                diversidad_insumos * peso_diversidad +
                prioridad_insumos * peso_prioridad
            )
            
            return max(0.0, min(1.0, fitness))
            
        except Exception as e:
            self.log_error(f"Error evaluando individuo", e)
            return 0.0
    
    def _evaluar_cobertura_rutas(self, asignaciones: List[AsignacionVehiculo]) -> float:
        if not asignaciones:
            return 0.0
        
        rutas_cubiertas = set(asig.ruta_id for asig in asignaciones)
        total_rutas = len(self.rutas)
        
        return len(rutas_cubiertas) / max(1, total_rutas)
    
    def _evaluar_eficiencia_vehiculos(self, asignaciones: List[AsignacionVehiculo]) -> float:
        if not asignaciones:
            return 0.0
        
        eficiencia_total = 0.0
        
        for asignacion in asignaciones:
            peso_total = asignacion.peso_total_kg
            capacidad_maxima = 1000.0
            
            if peso_total > capacidad_maxima:
                eficiencia = 0.1
            else:
                eficiencia = min(1.0, peso_total / capacidad_maxima)
            
            eficiencia_total += eficiencia
        
        return eficiencia_total / len(asignaciones)
    
    def _evaluar_diversidad_insumos(self, asignaciones: List[AsignacionVehiculo]) -> float:
        if not asignaciones:
            return 0.0
        
        insumos_distribuidos = set()
        
        for asignacion in asignaciones:
            cantidades_o_insumos = asignacion.insumos
            
            if not cantidades_o_insumos:
                continue
                
            primer_elemento = cantidades_o_insumos[0]
            
            if isinstance(primer_elemento, int):
                for i, cantidad in enumerate(cantidades_o_insumos):
                    if cantidad > 0 and i < len(self.insumos):
                        insumos_distribuidos.add(self.insumos[i].id)
                        
            elif hasattr(primer_elemento, 'id'):
                for insumo in cantidades_o_insumos:
                    if hasattr(insumo, 'id'):
                        insumos_distribuidos.add(insumo.id)
            else:
                try:
                    for item in cantidades_o_insumos:
                        if isinstance(item, (int, float)) and item > 0:
                            continue
                        elif hasattr(item, 'id'):
                            insumos_distribuidos.add(item.id)
                except:
                    continue
        
        total_insumos = len(self.insumos)
        return len(insumos_distribuidos) / max(1, total_insumos)
    
    def _evaluar_prioridad_insumos(self, asignaciones: List[AsignacionVehiculo]) -> float:
        if not asignaciones:
            return 0.0
        
        puntuacion_total = 0.0
        total_items = 0
        
        for asignacion in asignaciones:
            cantidades_o_insumos = asignacion.insumos
            
            if not cantidades_o_insumos:
                continue
            
            primer_elemento = cantidades_o_insumos[0]
            
            if isinstance(primer_elemento, int):
                for i, cantidad in enumerate(cantidades_o_insumos):
                    if cantidad > 0 and i < len(self.insumos):
                        insumo = self.insumos[i]
                        prioridad = self.prioridades_categoria.get(insumo.categoria, 'baja')
                        peso = self._calcular_peso_prioridad(prioridad)
                        puntuacion_total += cantidad * peso
                        total_items += cantidad
                        
            elif hasattr(primer_elemento, 'categoria'):
                for insumo in cantidades_o_insumos:
                    if hasattr(insumo, 'categoria'):
                        prioridad = self.prioridades_categoria.get(insumo.categoria, 'baja')
                        peso = self._calcular_peso_prioridad(prioridad)
                        puntuacion_total += peso
                        total_items += 1
        
        if total_items == 0:
            return 0.0

        return (puntuacion_total / total_items) / 3.0
    
    def _calcular_peso_prioridad(self, nivel: str) -> float:
        pesos = {'alta': 3.0, 'media': 2.0, 'baja': 1.0}
        return pesos.get(nivel, 1.0)