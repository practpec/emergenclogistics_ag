from typing import List, Dict, Set
from ..models import *


class AssignmentValidator:
    """Validador de asignaciones del algoritmo genético"""
    
    def __init__(self, rutas: List[Ruta], vehiculos_expandidos: List[tuple]):
        self.rutas = {r.id: r for r in rutas}
        self.vehiculos_expandidos = {v['id']: v for v in vehiculos_expandidos}
    
    def validar_individuo(self, individuo: Individual) -> Dict[str, any]:
        """Validar un individuo completo"""
        errores = []
        advertencias = []
        
        # Validar asignaciones únicas
        vehiculos_usados = set()
        rutas_usadas = set()
        
        for asignacion in individuo:
            # Verificar vehículos duplicados
            if asignacion.vehiculo_id in vehiculos_usados:
                errores.append(f"Vehículo {asignacion.vehiculo_id} asignado múltiples veces")
            vehiculos_usados.add(asignacion.vehiculo_id)
            
            # Verificar rutas duplicadas
            if asignacion.ruta_id in rutas_usadas:
                errores.append(f"Ruta {asignacion.ruta_id} asignada múltiples veces")
            rutas_usadas.add(asignacion.ruta_id)
            
            # Validar asignación individual
            errores_asig, advert_asig = self._validar_asignacion(asignacion)
            errores.extend(errores_asig)
            advertencias.extend(advert_asig)
        
        return {
            "valido": len(errores) == 0,
            "errores": errores,
            "advertencias": advertencias,
            "estadisticas": self._generar_estadisticas(individuo)
        }
    
    def _validar_asignacion(self, asignacion: AsignacionVehiculo) -> tuple:
        """Validar una asignación individual"""
        errores = []
        advertencias = []
        
        # Verificar existencia de vehículo
        if asignacion.vehiculo_id not in self.vehiculos_expandidos:
            errores.append(f"Vehículo {asignacion.vehiculo_id} no existe")
            return errores, advertencias
        
        # Verificar existencia de ruta
        if asignacion.ruta_id not in self.rutas:
            errores.append(f"Ruta {asignacion.ruta_id} no existe")
            return errores, advertencias
        
        vehiculo = self.vehiculos_expandidos[asignacion.vehiculo_id]
        ruta = self.rutas[asignacion.ruta_id]
        
        # Validar compatibilidad vehículo-ruta
        if not self._es_compatible(vehiculo, ruta):
            errores.append(f"Vehículo {asignacion.vehiculo_id} no compatible con ruta {asignacion.ruta_id}")
        
        # Validar capacidad de peso
        capacidad_kg = vehiculo.maximo_peso_ton * 1000
        if asignacion.peso_total_kg > capacidad_kg:
            errores.append(f"Sobrecarga: {asignacion.peso_total_kg}kg > {capacidad_kg}kg")
        elif asignacion.peso_total_kg < capacidad_kg * 0.5:
            advertencias.append(f"Subutilización: {asignacion.peso_total_kg}kg < 50% capacidad")
        
        # Validar estado de ruta
        if ruta.estado != EstadoRuta.ABIERTA:
            errores.append(f"Ruta {asignacion.ruta_id} no está abierta")
        
        # Validar coherencia de insumos
        peso_calculado = sum(insumo.peso_kg for insumo in asignacion.insumos)
        if abs(peso_calculado - asignacion.peso_total_kg) > 0.1:
            errores.append(f"Peso inconsistente: calculado {peso_calculado}kg, registrado {asignacion.peso_total_kg}kg")
        
        return errores, advertencias
    
    def _es_compatible(self, vehiculo: VehiculoBase, ruta: Ruta) -> bool:
        """Verificar compatibilidad vehículo-ruta"""
        if not ruta.vehiculos_permitidos:
            return True
        
        return any(tipo.lower() in vehiculo.tipo.lower() or 
                  vehiculo.tipo.lower() in tipo.lower() 
                  for tipo in ruta.vehiculos_permitidos)
    
    def _generar_estadisticas(self, individuo: Individual) -> Dict[str, any]:
        """Generar estadísticas del individuo"""
        if not individuo:
            return {
                "total_asignaciones": 0,
                "peso_total": 0,
                "distancia_total": 0,
                "combustible_total": 0,
                "utilizacion_promedio": 0
            }
        
        peso_total = sum(a.peso_total_kg for a in individuo)
        distancia_total = sum(a.distancia_km for a in individuo)
        combustible_total = sum(a.combustible_usado for a in individuo)
        
        # Calcular utilización promedio
        utilizaciones = []
        for asignacion in individuo:
            vehiculo = self.vehiculos_expandidos.get(asignacion.vehiculo_id)
            if vehiculo:
                capacidad = vehiculo.maximo_peso_ton * 1000
                utilizacion = (asignacion.peso_total_kg / capacidad) * 100
                utilizaciones.append(utilizacion)
        
        utilizacion_promedio = sum(utilizaciones) / len(utilizaciones) if utilizaciones else 0
        
        return {
            "total_asignaciones": len(individuo),
            "peso_total": peso_total,
            "distancia_total": distancia_total,
            "combustible_total": combustible_total,
            "utilizacion_promedio": utilizacion_promedio,
            "eficiencia_combustible": peso_total / combustible_total if combustible_total > 0 else 0
        }
    
    def reparar_individuo(self, individuo: Individual) -> Individual:
        """Reparar un individuo eliminando conflictos"""
        if not individuo:
            return individuo
        
        vehiculos_usados = set()
        rutas_usadas = set()
        individuo_reparado = []
        
        for asignacion in individuo:
            # Solo agregar si no hay conflictos
            if (asignacion.vehiculo_id not in vehiculos_usados and 
                asignacion.ruta_id not in rutas_usadas and
                asignacion.vehiculo_id in self.vehiculos_expandidos and
                asignacion.ruta_id in self.rutas):
                
                # Verificar compatibilidad
                vehiculo = self.vehiculos_expandidos[asignacion.vehiculo_id]
                ruta = self.rutas[asignacion.ruta_id]
                
                if self._es_compatible(vehiculo, ruta) and ruta.estado == EstadoRuta.ABIERTA:
                    vehiculos_usados.add(asignacion.vehiculo_id)
                    rutas_usadas.add(asignacion.ruta_id)
                    individuo_reparado.append(asignacion)
        
        return individuo_reparado