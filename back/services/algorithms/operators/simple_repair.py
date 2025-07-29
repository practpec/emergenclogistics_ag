import random
from typing import List, Set
from core.base_service import BaseService
from ..models import Individual, AsignacionVehiculo, EstadoRuta

class SimpleRepairOperator(BaseService):
    def __init__(self, rutas_data: List, vehiculos_expandidos: List[dict]):
        super().__init__()
        self.rutas = {r.id: r for r in rutas_data}
        self.vehiculos = {v['id']: v for v in vehiculos_expandidos}
        self.vehiculos_disponibles = vehiculos_expandidos
    
    def reparar_individuo(self, individuo: Individual) -> Individual:
        if not individuo:
            return self._generar_individuo_basico()
    
        individuo_limpio = self._eliminar_asignaciones_invalidas(individuo)
        individuo_sin_duplicados = self._resolver_duplicados(individuo_limpio)
        individuo_completo = self._asegurar_uso_todos_vehiculos(individuo_sin_duplicados)
        individuo_final = self._recalcular_metricas(individuo_completo)
        
        return individuo_final
    
    def _eliminar_asignaciones_invalidas(self, individuo: Individual) -> Individual:
        asignaciones_validas = []
        
        for asignacion in individuo:
            if asignacion.vehiculo_id not in self.vehiculos:
                continue
            
            if asignacion.ruta_id not in self.rutas:
                continue
            
            ruta = self.rutas[asignacion.ruta_id]
            if ruta.estado != EstadoRuta.ABIERTA:
                continue
            
            vehiculo = self.vehiculos[asignacion.vehiculo_id]
            if not self._es_compatible_vehiculo_ruta(vehiculo, ruta):
                continue
            
            asignaciones_validas.append(asignacion)
        
        return asignaciones_validas
    
    def _resolver_duplicados(self, individuo: Individual) -> Individual:
        vehiculos_usados: Set[int] = set()
        rutas_usadas: Set[int] = set()
        asignaciones_unicas = []
        
        for asignacion in individuo:
            if (asignacion.vehiculo_id not in vehiculos_usados and 
                asignacion.ruta_id not in rutas_usadas):
                
                vehiculos_usados.add(asignacion.vehiculo_id)
                rutas_usadas.add(asignacion.ruta_id)
                asignaciones_unicas.append(asignacion)
        
        return asignaciones_unicas
    
    def _asegurar_uso_todos_vehiculos(self, individuo: Individual) -> Individual:
        vehiculos_usados = {asig.vehiculo_id for asig in individuo}
        rutas_usadas = {asig.ruta_id for asig in individuo}

        vehiculos_sin_usar = [v for v in self.vehiculos_disponibles 
                             if v['id'] not in vehiculos_usados]
        
        rutas_abiertas = [r for r in self.rutas.values() 
                         if r.estado == EstadoRuta.ABIERTA]
        rutas_disponibles = [r for r in rutas_abiertas 
                           if r.id not in rutas_usadas]
        
        individuo_completo = individuo.copy()
        
        for vehiculo in vehiculos_sin_usar:
            ruta_compatible = None
            for ruta in rutas_disponibles:
                if self._es_compatible_vehiculo_ruta(vehiculo, ruta):
                    ruta_compatible = ruta
                    break
            
            if ruta_compatible:
                nueva_asignacion = self._crear_asignacion_basica(vehiculo, ruta_compatible)
                individuo_completo.append(nueva_asignacion)
                rutas_disponibles.remove(ruta_compatible)
            else:
                asignacion_standby = self._crear_asignacion_standby(vehiculo)
                individuo_completo.append(asignacion_standby)
        
        return individuo_completo
    
    def _crear_asignacion_basica(self, vehiculo: dict, ruta) -> AsignacionVehiculo:
        TOTAL_INSUMOS = 25 
        insumos = []
        for i in range(TOTAL_INSUMOS):
            if random.random() < 0.4:
                insumos.append(random.randint(1, 3))
            else:
                insumos.append(0)
        
        return AsignacionVehiculo(
            vehiculo_id=vehiculo['id'],
            ruta_id=ruta.id,
            insumos=insumos,
            peso_total_kg=0,
            distancia_km=ruta.distancia_km,
            combustible_usado=0
        )
    
    def _crear_asignacion_standby(self, vehiculo: dict) -> AsignacionVehiculo:
        TOTAL_INSUMOS = 25
        insumos = [0] * TOTAL_INSUMOS
        
        return AsignacionVehiculo(
            vehiculo_id=vehiculo['id'],
            ruta_id=-1,
            insumos=insumos,
            peso_total_kg=0,
            distancia_km=0,
            combustible_usado=0
        )
    
    def _es_compatible_vehiculo_ruta(self, vehiculo: dict, ruta) -> bool:
        if not ruta.vehiculos_permitidos:
            return True
        
        tipo_vehiculo = vehiculo['tipo'].lower()
        return any(tipo_permitido.lower() in tipo_vehiculo or 
                  tipo_vehiculo in tipo_permitido.lower() 
                  for tipo_permitido in ruta.vehiculos_permitidos)
    
    def _recalcular_metricas(self, individuo: Individual) -> Individual:
        TOTAL_INSUMOS = 25
        peso_promedio_insumo = 5.0
        
        for asignacion in individuo:
            if len(asignacion.insumos) < TOTAL_INSUMOS:
                asignacion.insumos.extend([0] * (TOTAL_INSUMOS - len(asignacion.insumos)))
            elif len(asignacion.insumos) > TOTAL_INSUMOS:
                asignacion.insumos = asignacion.insumos[:TOTAL_INSUMOS]
            
            if asignacion.ruta_id == -1:
                asignacion.insumos = [0] * TOTAL_INSUMOS
                continue
            
            peso_total = sum(asignacion.insumos) * peso_promedio_insumo
            vehiculo = self.vehiculos.get(asignacion.vehiculo_id)
            
            if vehiculo:
                capacidad_kg = vehiculo['maximo_peso_ton'] * 1000
                asignacion.peso_total_kg = min(peso_total, capacidad_kg)
                
                asignacion.combustible_usado = (asignacion.distancia_km * 
                                              vehiculo['consumo_litros_km'])
        
        return individuo
    
    def _generar_individuo_basico(self) -> Individual:
        individuo = []
        rutas_abiertas = [r for r in self.rutas.values() 
                         if r.estado == EstadoRuta.ABIERTA]
        
        for i, vehiculo in enumerate(self.vehiculos_disponibles):
            if i < len(rutas_abiertas):
                ruta = rutas_abiertas[i]
                if self._es_compatible_vehiculo_ruta(vehiculo, ruta):
                    asignacion = self._crear_asignacion_basica(vehiculo, ruta)
                    individuo.append(asignacion)
                else:
                    asignacion = self._crear_asignacion_standby(vehiculo)
                    individuo.append(asignacion)
            else:
                asignacion = self._crear_asignacion_standby(vehiculo)
                individuo.append(asignacion)
        
        return self._recalcular_metricas(individuo)