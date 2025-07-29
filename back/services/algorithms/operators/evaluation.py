from typing import List, Dict
from ..models import *


class EvaluationOperator:
    """Operador de evaluación con cantidades de insumos"""
    
    def __init__(self, rutas: List[Ruta], tipo_desastre: TipoDesastre, insumos: List[Insumo]):
        self.rutas = {r.id: r for r in rutas}
        self.tipo_desastre = tipo_desastre
        self.insumos = insumos
        self.prioridades_insumos = self._calcular_prioridades_insumos()
        self.total_rutas = len(self.rutas)
        self.total_poblacion = sum(r.localidad.poblacion for r in self.rutas.values())
    
    def evaluar_individuo(self, asignaciones: Individual) -> float:
        """Evaluar la aptitud de un individuo"""
        if not asignaciones:
            return 0.0
        
        cobertura_rutas = self._evaluar_cobertura_rutas(asignaciones)
        cobertura_poblacion = self._evaluar_cobertura_poblacion(asignaciones)
        eficiencia_carga = self._evaluar_eficiencia_carga(asignaciones)
        diversidad_insumos = self._evaluar_diversidad_insumos(asignaciones)
        
        fitness = (
            cobertura_rutas * 0.40 +
            cobertura_poblacion * 0.30 +
            eficiencia_carga * 0.20 +
            diversidad_insumos * 0.10
        )
        
        return fitness
    
    def _evaluar_cobertura_rutas(self, asignaciones: Individual) -> float:
        """Evaluar qué porcentaje de rutas están cubiertas"""
        if not asignaciones:
            return 0.0
        
        rutas_cubiertas = len(set(a.ruta_id for a in asignaciones))
        return rutas_cubiertas / self.total_rutas
    
    def _evaluar_cobertura_poblacion(self, asignaciones: Individual) -> float:
        """Evaluar cobertura de población"""
        if not asignaciones:
            return 0.0
        
        poblacion_cubierta = 0
        peso_total_enviado = 0
        
        for asignacion in asignaciones:
            ruta = self.rutas.get(asignacion.ruta_id)
            if ruta:
                poblacion_cubierta += ruta.localidad.poblacion
                peso_total_enviado += asignacion.peso_total_kg
        
        cobertura_poblacional = poblacion_cubierta / self.total_poblacion
        
        if poblacion_cubierta > 0:
            eficiencia_distribucion = peso_total_enviado / poblacion_cubierta * 1000
            eficiencia_distribucion = min(eficiencia_distribucion / 50, 1.0)
        else:
            eficiencia_distribucion = 0
        
        return (cobertura_poblacional * 0.7) + (eficiencia_distribucion * 0.3)
    
    def _evaluar_eficiencia_carga(self, asignaciones: Individual) -> float:
        """Evaluar eficiencia de carga"""
        if not asignaciones:
            return 0.0
        
        eficiencias = []
        penalizacion_subutilizacion = 0
        
        for asignacion in asignaciones:
            capacidad_estimada = 2000.0
            utilizacion = asignacion.peso_total_kg / capacidad_estimada
            
            if utilizacion < 0.3:
                penalizacion_subutilizacion += 0.2
                eficiencia = utilizacion * 0.5
            elif utilizacion < 0.6:
                penalizacion_subutilizacion += 0.1
                eficiencia = utilizacion * 0.8
            elif utilizacion <= 1.0:
                eficiencia = utilizacion
            else:
                eficiencia = 2.0 - utilizacion
            
            eficiencias.append(eficiencia)
        
        eficiencia_promedio = sum(eficiencias) / len(eficiencias)
        penalizacion = min(penalizacion_subutilizacion, 0.5)
        
        return max(0, eficiencia_promedio - penalizacion)
    
    def _evaluar_diversidad_insumos(self, asignaciones: Individual) -> float:
        """Evaluar diversidad de insumos usando cantidades"""
        if not asignaciones:
            return 0.0
        
        # Sumar cantidades por categoría
        cantidades_por_categoria = {}
        peso_por_categoria = {}
        
        for asignacion in asignaciones:
            for i, cantidad in enumerate(asignacion.insumos):
                if cantidad > 0:
                    insumo = self.insumos[i]
                    categoria = insumo.categoria
                    
                    if categoria not in cantidades_por_categoria:
                        cantidades_por_categoria[categoria] = 0
                        peso_por_categoria[categoria] = 0
                    
                    cantidades_por_categoria[categoria] += cantidad
                    peso_por_categoria[categoria] += cantidad * insumo.peso_kg
        
        if not cantidades_por_categoria:
            return 0.0
        
        # Diversidad: cuántas categorías diferentes tienen insumos
        diversidad = len(cantidades_por_categoria) / len(self.prioridades_insumos)
        
        # Prioridad ponderada por peso
        puntuacion_prioridad = 0
        peso_total = 0
        
        for categoria, peso in peso_por_categoria.items():
            prioridad = self.prioridades_insumos.get(categoria, 0.3)
            puntuacion_prioridad += peso * prioridad
            peso_total += peso
        
        if peso_total > 0:
            prioridad_ponderada = puntuacion_prioridad / peso_total
        else:
            prioridad_ponderada = 0
        
        return (diversidad * 0.4) + (prioridad_ponderada * 0.6)
    
    def _calcular_prioridades_insumos(self) -> Dict[str, float]:
        """Calcular prioridades usando valores del JSON del desastre"""
        prioridades = {}
        
        valores_prioridad = {
            NivelPrioridad.ALTA: 1.0,
            NivelPrioridad.MEDIA: 0.6,
            NivelPrioridad.BAJA: 0.3
        }
        
        for prioridad_categoria in self.tipo_desastre.prioridades:
            categoria_nombre = prioridad_categoria.categoria
            nivel = prioridad_categoria.nivel
            prioridades[categoria_nombre] = valores_prioridad.get(nivel, 0.5)
        
        return prioridades