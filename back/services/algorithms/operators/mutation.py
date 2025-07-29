import random
from typing import List, Tuple
from ..models import *


class MutationOperator:
    """Operador de mutación para el algoritmo genético"""
    
    def __init__(self, rutas: List[Ruta], vehiculos_expandidos: List[Tuple[int, VehiculoBase]], 
                 insumos: List[Insumo]):
        self.rutas_abiertas = [r for r in rutas if r.estado == EstadoRuta.ABIERTA]
        self.vehiculos_expandidos = vehiculos_expandidos
        self.insumos = insumos
    
    def mutar_individuo(self, individuo: Individual, probabilidad_mutacion: float) -> Individual:
        """Aplicar mutación a un individuo"""
        if not individuo or random.random() > probabilidad_mutacion:
            return individuo
        
        individuo_mutado = individuo.copy()
        tipo_mutacion = random.choice(['cambiar_ruta', 'cambiar_insumos', 'eliminar_asignacion'])
        
        if tipo_mutacion == 'cambiar_ruta':
            individuo_mutado = self._mutar_cambiar_ruta(individuo_mutado)
        elif tipo_mutacion == 'cambiar_insumos':
            individuo_mutado = self._mutar_cambiar_insumos(individuo_mutado)
        elif tipo_mutacion == 'eliminar_asignacion':
            individuo_mutado = self._mutar_eliminar_asignacion(individuo_mutado)
        
        return individuo_mutado
    
    def _mutar_cambiar_ruta(self, individuo: Individual) -> Individual:
        """Cambiar la ruta de una asignación aleatoria"""
        if not individuo:
            return individuo
        
        indice = random.randint(0, len(individuo) - 1)
        asignacion = individuo[indice]
        
        rutas_asignadas = {a.ruta_id for a in individuo}
        rutas_disponibles = [r for r in self.rutas_abiertas if r.id not in rutas_asignadas]
        
        if rutas_disponibles:
            nueva_ruta = random.choice(rutas_disponibles)
            
            individuo[indice] = AsignacionVehiculo(
                vehiculo_id=asignacion.vehiculo_id,
                ruta_id=nueva_ruta.id,
                insumos=asignacion.insumos,
                peso_total_kg=asignacion.peso_total_kg,
                distancia_km=nueva_ruta.distancia_km,
                combustible_usado=self._calcular_combustible(asignacion.vehiculo_id, nueva_ruta.distancia_km)
            )
        
        return individuo
    
    def _mutar_cambiar_insumos(self, individuo: Individual) -> Individual:
        """Cambiar los insumos de una asignación"""
        if not individuo:
            return individuo
        
        indice = random.randint(0, len(individuo) - 1)
        asignacion = individuo[indice]
        
        vehiculo = self._obtener_vehiculo_por_id(asignacion.vehiculo_id)
        if vehiculo:
            nuevos_insumos = self._asignar_insumos_aleatorios(vehiculo)
            if nuevos_insumos is not None:  # Verificar que no sea None
                nuevo_peso = sum(insumo.peso_kg for insumo in nuevos_insumos)
                
                individuo[indice] = AsignacionVehiculo(
                    vehiculo_id=asignacion.vehiculo_id,
                    ruta_id=asignacion.ruta_id,
                    insumos=nuevos_insumos,
                    peso_total_kg=nuevo_peso,
                    distancia_km=asignacion.distancia_km,
                    combustible_usado=asignacion.combustible_usado
                )
        
        return individuo
    
    def _mutar_eliminar_asignacion(self, individuo: Individual) -> Individual:
        """Eliminar una asignación aleatoria"""
        if len(individuo) <= 1:
            return individuo
        
        indice = random.randint(0, len(individuo) - 1)
        return individuo[:indice] + individuo[indice + 1:]
    
    def _calcular_combustible(self, vehiculo_id: int, distancia_km: float) -> float:
        """Calcular combustible para un vehículo y distancia"""
        vehiculo = self._obtener_vehiculo_por_id(vehiculo_id)
        if vehiculo:
            return vehiculo.consumo_litros_km * distancia_km
        return 0.1 * distancia_km
    
    def _obtener_vehiculo_por_id(self, vehiculo_id: int) -> VehiculoBase:
        """Obtener vehículo por ID"""
        for v_id, vehiculo in self.vehiculos_expandidos:
            if v_id == vehiculo_id:
                return vehiculo
        return None
    
    def _asignar_insumos_aleatorios(self, vehiculo: VehiculoBase) -> List[Insumo]:
        """Asignar insumos aleatorios respetando capacidad"""
        if not vehiculo or not self.insumos:
            return []
        
        capacidad_kg = vehiculo.maximo_peso_ton * 1000
        insumos_asignados = []
        peso_actual = 0
        
        insumos_disponibles = self.insumos.copy()
        random.shuffle(insumos_disponibles)
        
        for insumo in insumos_disponibles:
            if peso_actual + insumo.peso_kg <= capacidad_kg:
                insumos_asignados.append(insumo)
                peso_actual += insumo.peso_kg
            
            if peso_actual >= capacidad_kg * 0.7:
                break
        
        return insumos_asignados