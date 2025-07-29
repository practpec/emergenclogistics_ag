import random
from typing import List
from core.base_service import BaseService
from ..models import Individual, AsignacionVehiculo, Ruta, VehiculoDisponible, Insumo

class InitializationOperator(BaseService): 
    def __init__(self, rutas: List[Ruta], vehiculos_disponibles: List[VehiculoDisponible], insumos: List[Insumo]):
        super().__init__()
        self.rutas = rutas
        self.vehiculos_disponibles = vehiculos_disponibles
        self.insumos = insumos
        self.TOTAL_INSUMOS = 25 

        self.vehiculos_expandidos = []
        vehiculo_id = 0
        for vehiculo_disp in vehiculos_disponibles:
            for i in range(vehiculo_disp.cantidad):
                self.vehiculos_expandidos.append({
                    'id': vehiculo_id,
                    'modelo': f"{vehiculo_disp.vehiculo.modelo} #{i+1}",
                    'tipo': vehiculo_disp.vehiculo.tipo,
                    'consumo_litros_km': vehiculo_disp.vehiculo.consumo_litros_km,
                    'maximo_peso_ton': vehiculo_disp.vehiculo.maximo_peso_ton,
                    'velocidad_kmh': getattr(vehiculo_disp.vehiculo, 'velocidad_kmh', 65)
                })
                vehiculo_id += 1
    
    def generar_poblacion_inicial(self, tamaño_poblacion: int) -> List[Individual]:
        poblacion = []
        
        for _ in range(tamaño_poblacion):
            individuo = self._generar_individuo_aleatorio()
            poblacion.append(individuo)
        
        return poblacion
    
    def _generar_individuo_aleatorio(self) -> Individual:
        asignaciones = []
        rutas_usadas = set()
        
        for vehiculo in self.vehiculos_expandidos:
            ruta_asignada = None
            rutas_disponibles = [r for r in self.rutas if r.id not in rutas_usadas]
            
            for ruta in rutas_disponibles:
                if self._es_compatible_vehiculo_ruta(vehiculo, ruta):
                    ruta_asignada = ruta
                    rutas_usadas.add(ruta.id)
                    break
            
            if ruta_asignada:
                asignacion = self._crear_asignacion_con_ruta(vehiculo, ruta_asignada)
            else:
                asignacion = self._crear_asignacion_standby(vehiculo)
            
            asignaciones.append(asignacion)
        
        return asignaciones
    
    def _crear_asignacion_con_ruta(self, vehiculo: dict, ruta: Ruta) -> AsignacionVehiculo:
        cantidades_insumos = self._generar_cantidades_optimizadas(vehiculo)
        
        peso_total = sum(cantidad * self.insumos[i].peso_kg 
                        for i, cantidad in enumerate(cantidades_insumos) 
                        if i < len(self.insumos))
        
        velocidad = vehiculo.get('velocidad_kmh', 65)
        combustible = ruta.distancia_km * vehiculo['consumo_litros_km']
        
        return AsignacionVehiculo(
            vehiculo_id=vehiculo['id'],
            ruta_id=ruta.id,
            insumos=cantidades_insumos,
            peso_total_kg=peso_total,
            distancia_km=ruta.distancia_km,
            combustible_usado=combustible
        )
    
    def _crear_asignacion_standby(self, vehiculo: dict) -> AsignacionVehiculo:
        cantidades_insumos = [0] * self.TOTAL_INSUMOS
        
        return AsignacionVehiculo(
            vehiculo_id=vehiculo['id'],
            ruta_id=-1,
            insumos=cantidades_insumos,
            peso_total_kg=0,
            distancia_km=0,
            combustible_usado=0
        )
    
    def _generar_cantidades_optimizadas(self, vehiculo: dict) -> List[int]:
        cantidades = [0] * self.TOTAL_INSUMOS
        capacidad_kg = vehiculo['maximo_peso_ton'] * 1000
        peso_actual = 0.0
        
        if capacidad_kg >= 2500:
            objetivo_utilizacion = random.uniform(0.85, 0.95)
        elif capacidad_kg >= 1500:
            objetivo_utilizacion = random.uniform(0.80, 0.92)
        else:
            objetivo_utilizacion = random.uniform(0.75, 0.88)
        
        objetivo_peso = capacidad_kg * objetivo_utilizacion
        
        insumos_ordenados = list(range(min(self.TOTAL_INSUMOS, len(self.insumos))))
        insumos_ordenados.sort(key=lambda i: self.insumos[i].peso_kg if i < len(self.insumos) else 999)
        
        for i in insumos_ordenados:
            if i >= len(self.insumos):
                continue
                
            insumo = self.insumos[i]
            peso_disponible = objetivo_peso - peso_actual
            
            if peso_disponible <= insumo.peso_kg:
                continue
                
            max_cantidad_por_peso = int(peso_disponible // insumo.peso_kg)
            
            if max_cantidad_por_peso > 0:
                probabilidad_inclusion = 0.85 if insumo.peso_kg <= 3.0 else 0.65
                
                if random.random() < probabilidad_inclusion:
                    if capacidad_kg >= 2500:
                        cantidad_max = min(max_cantidad_por_peso, 20)
                    elif capacidad_kg >= 1500:
                        cantidad_max = min(max_cantidad_por_peso, 15)
                    else:
                        cantidad_max = min(max_cantidad_por_peso, 10)
                    
                    cantidad = random.randint(1, max(1, cantidad_max))
                    peso_insumo = cantidad * insumo.peso_kg
                    
                    if peso_actual + peso_insumo <= capacidad_kg:
                        cantidades[i] = cantidad
                        peso_actual += peso_insumo
        
        aprovechamiento_actual = (peso_actual / capacidad_kg) * 100
        
        if aprovechamiento_actual < 70:
            for i in range(len(self.insumos)):
                if cantidades[i] == 0:
                    peso_disponible = objetivo_peso - peso_actual
                    if peso_disponible <= 0:
                        break
                    
                    insumo = self.insumos[i]
                    if peso_disponible >= insumo.peso_kg:
                        cantidad_adicional = min(3, int(peso_disponible // insumo.peso_kg))
                        if cantidad_adicional > 0:
                            cantidades[i] = cantidad_adicional
                            peso_actual += cantidad_adicional * insumo.peso_kg
        
        return cantidades
    
    def _es_compatible_vehiculo_ruta(self, vehiculo: dict, ruta: Ruta) -> bool:
        if not ruta.vehiculos_permitidos:
            return True
        
        tipo_vehiculo = vehiculo['tipo'].lower()
        return any(tipo_permitido.lower() in tipo_vehiculo or 
                  tipo_vehiculo in tipo_permitido.lower() 
                  for tipo_permitido in ruta.vehiculos_permitidos)