from typing import List, Dict, Tuple
from ..models import *


class CapacityManager:
    """Gestor de capacidades para optimización de carga"""
    
    def __init__(self, vehiculos_expandidos: List[dict],
                 insumos: List[Insumo], tipo_desastre: TipoDesastre):
        self.vehiculos_expandidos = vehiculos_expandidos
        self.insumos = insumos
        self.tipo_desastre = tipo_desastre
        self.vehiculos_dict = {v['id']: v for v in vehiculos_expandidos}
        self.prioridades_categorias = self._obtener_prioridades_del_desastre()
    
    def _obtener_prioridades_del_desastre(self) -> Dict[str, float]:
        """Obtener prioridades desde el JSON del desastre"""
        prioridades = {}
        
        # Mapear niveles a valores numéricos
        valores_nivel = {
            NivelPrioridad.ALTA: 1.0,
            NivelPrioridad.MEDIA: 0.6,
            NivelPrioridad.BAJA: 0.3
        }
        
        # Usar las prioridades exactas del JSON del desastre
        for prioridad_categoria in self.tipo_desastre.prioridades:
            categoria_nombre = prioridad_categoria.categoria
            nivel = prioridad_categoria.nivel
            prioridades[categoria_nombre] = valores_nivel.get(nivel, 0.5)
        
        return prioridades
    
    def optimizar_carga_vehiculo(self, vehiculo_id: int, insumos_disponibles: List[Insumo] = None) -> List[Insumo]:
        """Optimizar la carga de un vehículo específico"""
        if vehiculo_id not in self.vehiculos_dict:
            return []
        
        vehiculo = self.vehiculos_dict[vehiculo_id]
        capacidad_kg = vehiculo.maximo_peso_ton * 1000
        
        if insumos_disponibles is None:
            insumos_disponibles = self.insumos
        
        # Ordenar insumos por prioridad del desastre específico
        insumos_ordenados = self._ordenar_insumos_por_prioridad(insumos_disponibles)
        
        carga_optima = []
        peso_actual = 0
        
        for insumo in insumos_ordenados:
            if peso_actual + insumo.peso_kg <= capacidad_kg:
                carga_optima.append(insumo)
                peso_actual += insumo.peso_kg
            
            # Objetivo: usar entre 70-95% de la capacidad
            if peso_actual >= capacidad_kg * 0.7:
                break
        
        return carga_optima
    
    def _ordenar_insumos_por_prioridad(self, insumos: List[Insumo]) -> List[Insumo]:
        """Ordenar insumos por prioridad usando los valores del JSON del desastre"""
        
        def calcular_prioridad(insumo: Insumo) -> float:
            categoria_nombre = insumo.categoria.nombre
            prioridad_categoria = self.prioridades_categorias.get(categoria_nombre, 0.1)
            # Ratio prioridad/peso para optimizar distribución
            return prioridad_categoria / max(insumo.peso_kg, 0.1)
        
        return sorted(insumos, key=calcular_prioridad, reverse=True)
    
    def calcular_utilizacion_vehiculo(self, asignacion: AsignacionVehiculo) -> Dict[str, float]:
        """Calcular métricas de utilización de un vehículo"""
        if asignacion.vehiculo_id not in self.vehiculos_dict:
            return {"utilizacion_peso": 0, "eficiencia": 0}
        
        vehiculo = self.vehiculos_dict[asignacion.vehiculo_id]
        capacidad_kg = vehiculo['maximo_peso_ton'] * 1000
        
        utilizacion_peso = (asignacion.peso_total_kg / capacidad_kg) * 100
        
        # Eficiencia: peso transportado por litro de combustible
        eficiencia = asignacion.peso_total_kg / asignacion.combustible_usado if asignacion.combustible_usado > 0 else 0
        
        return {
            "utilizacion_peso": utilizacion_peso,
            "eficiencia_combustible": eficiencia,
            "capacidad_maxima": capacidad_kg,
            "peso_utilizado": asignacion.peso_total_kg,
            "peso_disponible": capacidad_kg - asignacion.peso_total_kg,
            "estado": self._determinar_estado_carga(utilizacion_peso)
        }
    
    def _determinar_estado_carga(self, utilizacion_porcentual: float) -> str:
        """Determinar estado de carga del vehículo"""
        if utilizacion_porcentual > 95:
            return "Sobrecarga"
        elif utilizacion_porcentual >= 70:
            return "Óptima"
        elif utilizacion_porcentual >= 50:
            return "Aceptable"
        else:
            return "Subutilizada"
    
    def sugerir_redistribucion(self, individuo: Individual) -> List[Dict[str, any]]:
        """Sugerir redistribución de carga entre vehículos"""
        sugerencias = []
        
        # Identificar vehículos subutilizados y sobrecargados
        vehiculos_subutilizados = []
        vehiculos_sobrecargados = []
        
        for asignacion in individuo:
            utilizacion = self.calcular_utilizacion_vehiculo(asignacion)
            
            if utilizacion["estado"] == "Subutilizada":
                vehiculos_subutilizados.append((asignacion, utilizacion))
            elif utilizacion["estado"] == "Sobrecarga":
                vehiculos_sobrecargados.append((asignacion, utilizacion))
        
        # Generar sugerencias de redistribución
        for asig_sobre, util_sobre in vehiculos_sobrecargados:
            for asig_sub, util_sub in vehiculos_subutilizados:
                exceso = asig_sobre.peso_total_kg - (util_sobre["capacidad_maxima"] * 0.9)
                disponible = util_sub["peso_disponible"]
                
                if exceso > 0 and disponible > exceso:
                    sugerencias.append({
                        "tipo": "redistribuir",
                        "vehiculo_origen": asig_sobre,
                        "vehiculo_destino": asig_sub.vehiculo_id,
                        "peso_mover": exceso,
                        "razon": f"Reducir sobrecarga de {exceso:.1f}kg"
                    })
        
        return sugerencias
    
    def validar_capacidades_individuo(self, individuo: Individual) -> Dict[str, any]:
        """Validar todas las capacidades de un individuo"""
        resultados = {
            "total_vehiculos": len(individuo),
            "vehiculos_optimos": 0,
            "vehiculos_subutilizados": 0,
            "vehiculos_sobrecargados": 0,
            "utilizacion_promedio": 0,
            "peso_total_transportado": 0,
            "capacidad_total_disponible": 0
        }
        
        utilizaciones = []
        
        for asignacion in individuo:
            utilizacion = self.calcular_utilizacion_vehiculo(asignacion)
            utilizaciones.append(utilizacion["utilizacion_peso"])
            
            resultados["peso_total_transportado"] += asignacion.peso_total_kg
            resultados["capacidad_total_disponible"] += utilizacion["capacidad_maxima"]
            
            if utilizacion["estado"] == "Óptima":
                resultados["vehiculos_optimos"] += 1
            elif utilizacion["estado"] in ["Subutilizada", "Aceptable"]:
                resultados["vehiculos_subutilizados"] += 1
            elif utilizacion["estado"] == "Sobrecarga":
                resultados["vehiculos_sobrecargados"] += 1
        
        if utilizaciones:
            resultados["utilizacion_promedio"] = sum(utilizaciones) / len(utilizaciones)
        
        resultados["utilizacion_total"] = (resultados["peso_total_transportado"] / 
                                         resultados["capacidad_total_disponible"] * 100) if resultados["capacidad_total_disponible"] > 0 else 0
        
        return resultados