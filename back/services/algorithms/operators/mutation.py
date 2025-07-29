import random
import copy
from typing import List
from core.base_service import BaseService
from ..models import Individual, AsignacionVehiculo, Ruta, Insumo

class MutationOperator(BaseService):
    """Operador de mutación para algoritmo genético"""
    
    def __init__(self, rutas: List[Ruta], vehiculos_expandidos: List[dict], insumos: List[Insumo]):
        super().__init__()
        self.rutas = rutas
        self.vehiculos_expandidos = vehiculos_expandidos
        self.insumos = insumos
    
    def mutar_individuo(self, individuo: Individual, probabilidad_mutacion: float) -> Individual:
        """Mutar un individuo según la probabilidad dada"""
        if not individuo or random.random() > probabilidad_mutacion:
            return self._clonar_individuo(individuo)
        
        individuo_mutado = self._clonar_individuo(individuo)
        
        try:
            # Elegir tipo de mutación aleatoriamente
            tipo_mutacion = random.choice([
                'mutar_insumos',
                'intercambiar_vehiculos', 
                'intercambiar_rutas',
                'agregar_asignacion',
                'eliminar_asignacion'
            ])
            
            if tipo_mutacion == 'mutar_insumos':
                self._mutar_insumos(individuo_mutado)
            elif tipo_mutacion == 'intercambiar_vehiculos':
                self._intercambiar_vehiculos(individuo_mutado)
            elif tipo_mutacion == 'intercambiar_rutas':
                self._intercambiar_rutas(individuo_mutado)
            elif tipo_mutacion == 'agregar_asignacion':
                self._agregar_asignacion(individuo_mutado)
            elif tipo_mutacion == 'eliminar_asignacion':
                self._eliminar_asignacion(individuo_mutado)
            
            return individuo_mutado
            
        except Exception as e:
            self.log_error("Error en mutación", e)
            return self._clonar_individuo(individuo)
    
    def _mutar_insumos(self, individuo: Individual):
        """Mutar cantidades de insumos en una asignación aleatoria"""
        if not individuo:
            return
        
        asignacion = random.choice(individuo)
        if not asignacion.insumos:
            return
        
        # Mutar 1-3 insumos aleatorios
        num_mutaciones = random.randint(1, min(3, len(asignacion.insumos)))
        indices_mutar = random.sample(range(len(asignacion.insumos)), num_mutaciones)
        
        for idx in indices_mutar:
            if random.random() < 0.5:
                # Incrementar cantidad
                asignacion.insumos[idx] = min(10, asignacion.insumos[idx] + random.randint(1, 3))
            else:
                # Decrementar cantidad
                asignacion.insumos[idx] = max(0, asignacion.insumos[idx] - random.randint(1, 2))
        
        # Recalcular peso
        asignacion.peso_total_kg = self._calcular_peso_total(asignacion.insumos)
    
    def _intercambiar_vehiculos(self, individuo: Individual):
        """Intercambiar vehículos entre dos asignaciones"""
        if len(individuo) < 2:
            return
        
        asig1, asig2 = random.sample(individuo, 2)
        asig1.vehiculo_id, asig2.vehiculo_id = asig2.vehiculo_id, asig1.vehiculo_id
    
    def _intercambiar_rutas(self, individuo: Individual):
        """Intercambiar rutas entre dos asignaciones"""
        if len(individuo) < 2:
            return
        
        asig1, asig2 = random.sample(individuo, 2)
        asig1.ruta_id, asig2.ruta_id = asig2.ruta_id, asig1.ruta_id
        
        # Actualizar distancias
        ruta1 = next((r for r in self.rutas if r.id == asig1.ruta_id), None)
        ruta2 = next((r for r in self.rutas if r.id == asig2.ruta_id), None)
        
        if ruta1:
            asig1.distancia_km = ruta1.distancia_km
        if ruta2:
            asig2.distancia_km = ruta2.distancia_km
    
    def _agregar_asignacion(self, individuo: Individual):
        """Agregar nueva asignación si es posible"""
        # Encontrar vehículos y rutas no usados
        vehiculos_usados = {asig.vehiculo_id for asig in individuo}
        rutas_usadas = {asig.ruta_id for asig in individuo}
        
        vehiculos_libres = [v for v in self.vehiculos_expandidos if v['id'] not in vehiculos_usados]
        rutas_libres = [r for r in self.rutas if r.id not in rutas_usadas]
        
        if vehiculos_libres and rutas_libres:
            vehiculo = random.choice(vehiculos_libres)
            ruta = random.choice(rutas_libres)
            
            # Generar insumos aleatorios
            cantidades_insumos = self._generar_cantidades_aleatorias()
            peso_total = self._calcular_peso_total(cantidades_insumos)
            combustible = ruta.distancia_km * vehiculo['consumo_litros_km']
            
            nueva_asignacion = AsignacionVehiculo(
                vehiculo_id=vehiculo['id'],
                ruta_id=ruta.id,
                insumos=cantidades_insumos,
                peso_total_kg=peso_total,
                distancia_km=ruta.distancia_km,
                combustible_usado=combustible
            )
            
            individuo.append(nueva_asignacion)
    
    def _eliminar_asignacion(self, individuo: Individual):
        """Eliminar asignación aleatoria (si hay más de una)"""
        if len(individuo) > 1:
            asignacion_eliminar = random.choice(individuo)
            individuo.remove(asignacion_eliminar)
    
    def _generar_cantidades_aleatorias(self) -> List[int]:
        """Generar cantidades aleatorias de insumos"""
        cantidades = []
        for _ in range(len(self.insumos)):
            if random.random() < 0.3:  # 30% probabilidad de incluir cada insumo
                cantidad = random.randint(1, 5)
            else:
                cantidad = 0
            cantidades.append(cantidad)
        return cantidades
    
    def _calcular_peso_total(self, cantidades_insumos: List[int]) -> float:
        """Calcular peso total de insumos"""
        peso_total = 0.0
        for i, cantidad in enumerate(cantidades_insumos):
            if i < len(self.insumos):
                peso_total += cantidad * self.insumos[i].peso_kg
        return peso_total
    
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