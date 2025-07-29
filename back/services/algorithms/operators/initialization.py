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
        
        self.vehiculos_expandidos = []
        vehiculo_id = 0
        for vehiculo_disp in vehiculos_disponibles:
            for i in range(vehiculo_disp.cantidad):
                self.vehiculos_expandidos.append({
                    'id': vehiculo_id,
                    'modelo': f"{vehiculo_disp.vehiculo.modelo} #{i+1}",
                    'tipo': vehiculo_disp.vehiculo.tipo,
                    'consumo_litros_km': vehiculo_disp.vehiculo.consumo_litros_km,
                    'maximo_peso_ton': vehiculo_disp.vehiculo.maximo_peso_ton
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
        vehiculos_usados = set()
        rutas_asignadas = set()
        
        max_asignaciones = min(len(self.vehiculos_expandidos), len(self.rutas))
        num_asignaciones = random.randint(1, max_asignaciones)
        
        for _ in range(num_asignaciones):
            vehiculos_disponibles = [v for v in self.vehiculos_expandidos if v['id'] not in vehiculos_usados]
            if not vehiculos_disponibles:
                break
            
            vehiculo = random.choice(vehiculos_disponibles)
            
            rutas_disponibles = [r for r in self.rutas if r.id not in rutas_asignadas]
            if not rutas_disponibles:
                break
            
            ruta = random.choice(rutas_disponibles)
            
            cantidades_insumos = self._generar_cantidades_insumos(vehiculo)

            peso_total = sum(cantidad * self.insumos[i].peso_kg 
                           for i, cantidad in enumerate(cantidades_insumos) 
                           if i < len(self.insumos))
            
            combustible = ruta.distancia_km * vehiculo['consumo_litros_km']
            
            asignacion = AsignacionVehiculo(
                vehiculo_id=vehiculo['id'],
                ruta_id=ruta.id,
                insumos=cantidades_insumos,
                peso_total_kg=peso_total,
                distancia_km=ruta.distancia_km,
                combustible_usado=combustible
            )
            
            asignaciones.append(asignacion)
            vehiculos_usados.add(vehiculo['id'])
            rutas_asignadas.add(ruta.id)
        
        return asignaciones
    def _generar_cantidades_insumos(self, vehiculo: dict) -> List[int]:
        num_insumos = len(self.insumos)
        cantidades = [0] * num_insumos
        capacidad_kg = vehiculo['maximo_peso_ton'] * 1000
        peso_actual = 0.0
        
        indices_insumos = list(range(num_insumos))
        random.shuffle(indices_insumos)
        
        for i in indices_insumos:
            insumo = self.insumos[i]
            
            peso_disponible = capacidad_kg - peso_actual
            max_cantidad_por_peso = int(peso_disponible // insumo.peso_kg)
            
            if max_cantidad_por_peso > 0:
                if random.random() < 0.5:
                    cantidad_max = min(max_cantidad_por_peso, 10) 
                    cantidad = random.randint(1, max(1, cantidad_max))
                    peso_insumo = cantidad * insumo.peso_kg
                    
                    if peso_actual + peso_insumo <= capacidad_kg:
                        cantidades[i] = cantidad
                        peso_actual += peso_insumo
        
        return cantidades