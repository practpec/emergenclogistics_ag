import random
from typing import List
from ..models import *


class InitializationOperator:
    """Operador de inicialización con cantidades de insumos"""
    
    def __init__(self, rutas: List[Ruta], vehiculos: List[VehiculoDisponible], 
                 insumos: List[Insumo]):
        self.rutas_abiertas = [r for r in rutas if r.estado == EstadoRuta.ABIERTA]
        self.vehiculos = vehiculos
        self.insumos = insumos
        self.vehiculos_expandidos = self._expandir_vehiculos()
        self.num_insumos = len(insumos)
    
    def _expandir_vehiculos(self) -> List[tuple]:
        """Expandir vehículos según su cantidad"""
        vehiculos_expandidos = []
        vehiculo_id = 0
        
        for vehiculo_disponible in self.vehiculos:
            for _ in range(vehiculo_disponible.cantidad):
                vehiculos_expandidos.append((vehiculo_id, vehiculo_disponible.vehiculo))
                vehiculo_id += 1
        
        return vehiculos_expandidos
    
    def generar_poblacion_inicial(self, tamaño_poblacion: int) -> List[Individual]:
        """Generar población inicial con diferentes estrategias"""
        poblacion = []
        
        for i in range(tamaño_poblacion):
            if i < tamaño_poblacion // 3:
                individuo = self._generar_individuo_greedy()
            elif i < 2 * tamaño_poblacion // 3:
                individuo = self._generar_individuo_balanceado()
            else:
                individuo = self._generar_individuo_aleatorio()
            
            poblacion.append(individuo)
        
        return poblacion
    
    def _generar_individuo_greedy(self) -> Individual:
        """Generar individuo greedy - asignar todos los vehículos optimamente"""
        asignaciones = []
        rutas_disponibles = self.rutas_abiertas.copy()
        vehiculos_disponibles = self.vehiculos_expandidos.copy()
        
        # Ordenar rutas por población (mayor primero)
        rutas_disponibles.sort(key=lambda r: r.localidad.poblacion, reverse=True)
        # Ordenar vehículos por capacidad (mayor primero)
        vehiculos_disponibles.sort(key=lambda v: v[1].maximo_peso_ton, reverse=True)
        
        for i, (vehiculo_id, vehiculo) in enumerate(vehiculos_disponibles):
            if i < len(rutas_disponibles):
                ruta = rutas_disponibles[i]
                
                if self._es_vehiculo_compatible(vehiculo, ruta):
                    cantidades_insumos = self._generar_cantidades_optimas(vehiculo)
                    peso_total = self._calcular_peso_total(cantidades_insumos)
                    combustible = vehiculo.consumo_litros_km * ruta.distancia_km
                    
                    asignacion = AsignacionVehiculo(
                        vehiculo_id=vehiculo_id,
                        ruta_id=ruta.id,
                        insumos=cantidades_insumos,
                        peso_total_kg=peso_total,
                        distancia_km=ruta.distancia_km,
                        combustible_usado=combustible
                    )
                    asignaciones.append(asignacion)
        
        return asignaciones
    
    def _generar_individuo_balanceado(self) -> Individual:
        """Generar individuo balanceado"""
        asignaciones = []
        rutas_disponibles = self.rutas_abiertas.copy()
        vehiculos_disponibles = self.vehiculos_expandidos.copy()
        
        random.shuffle(rutas_disponibles)
        random.shuffle(vehiculos_disponibles)
        
        for i in range(min(len(rutas_disponibles), len(vehiculos_disponibles))):
            if random.random() < 0.8:
                vehiculo_id, vehiculo = vehiculos_disponibles[i]
                ruta = rutas_disponibles[i]
                
                if self._es_vehiculo_compatible(vehiculo, ruta):
                    cantidades_insumos = self._generar_cantidades_balanceadas(vehiculo)
                    peso_total = self._calcular_peso_total(cantidades_insumos)
                    combustible = vehiculo.consumo_litros_km * ruta.distancia_km
                    
                    asignacion = AsignacionVehiculo(
                        vehiculo_id=vehiculo_id,
                        ruta_id=ruta.id,
                        insumos=cantidades_insumos,
                        peso_total_kg=peso_total,
                        distancia_km=ruta.distancia_km,
                        combustible_usado=combustible
                    )
                    asignaciones.append(asignacion)
        
        return asignaciones
    
    def _generar_individuo_aleatorio(self) -> Individual:
        """Generar individuo aleatorio"""
        asignaciones = []
        rutas_disponibles = self.rutas_abiertas.copy()
        vehiculos_disponibles = self.vehiculos_expandidos.copy()
        
        random.shuffle(rutas_disponibles)
        random.shuffle(vehiculos_disponibles)
        
        for i in range(min(len(rutas_disponibles), len(vehiculos_disponibles))):
            if random.random() < 0.6:
                vehiculo_id, vehiculo = vehiculos_disponibles[i]
                ruta = rutas_disponibles[i]
                
                if self._es_vehiculo_compatible(vehiculo, ruta):
                    cantidades_insumos = self._generar_cantidades_aleatorias(vehiculo)
                    peso_total = self._calcular_peso_total(cantidades_insumos)
                    combustible = vehiculo.consumo_litros_km * ruta.distancia_km
                    
                    asignacion = AsignacionVehiculo(
                        vehiculo_id=vehiculo_id,
                        ruta_id=ruta.id,
                        insumos=cantidades_insumos,
                        peso_total_kg=peso_total,
                        distancia_km=ruta.distancia_km,
                        combustible_usado=combustible
                    )
                    asignaciones.append(asignacion)
        
        return asignaciones
    
    def _generar_cantidades_optimas(self, vehiculo: VehiculoBase) -> List[int]:
        """Generar cantidades óptimas de insumos para llenar 85% de capacidad"""
        capacidad_kg = vehiculo.maximo_peso_ton * 1000
        target_peso = capacidad_kg * 0.85
        
        cantidades = [0] * self.num_insumos
        peso_actual = 0
        
        # Estrategia greedy: llenar con insumos más ligeros primero
        insumos_ordenados = sorted(enumerate(self.insumos), key=lambda x: x[1].peso_kg)
        
        for idx, insumo in insumos_ordenados:
            if peso_actual >= target_peso:
                break
                
            # Calcular cuántas unidades podemos agregar de este insumo
            peso_disponible = target_peso - peso_actual
            max_unidades = int(peso_disponible / insumo.peso_kg)
            
            if max_unidades > 0:
                # Agregar entre 1 y max_unidades
                unidades = random.randint(1, min(max_unidades, 10))  # Máximo 10 unidades por insumo
                cantidades[idx] = unidades
                peso_actual += unidades * insumo.peso_kg
        
        return cantidades
    
    def _generar_cantidades_balanceadas(self, vehiculo: VehiculoBase) -> List[int]:
        """Generar cantidades balanceadas entre diversidad y capacidad"""
        capacidad_kg = vehiculo.maximo_peso_ton * 1000
        target_peso = capacidad_kg * random.uniform(0.6, 0.9)
        
        cantidades = [0] * self.num_insumos
        peso_actual = 0
        
        # Primero asegurar diversidad - al menos 1 de cada categoría importante
        categorias_importantes = set()
        for i, insumo in enumerate(self.insumos):
            if peso_actual < target_peso * 0.5:  # Solo usar la mitad del peso para diversidad
                if insumo.categoria not in categorias_importantes:
                    cantidades[i] = 1
                    peso_actual += insumo.peso_kg
                    categorias_importantes.add(insumo.categoria)
        
        # Luego llenar con insumos aleatorios
        indices_disponibles = list(range(self.num_insumos))
        random.shuffle(indices_disponibles)
        
        for idx in indices_disponibles:
            if peso_actual >= target_peso:
                break
                
            insumo = self.insumos[idx]
            peso_disponible = target_peso - peso_actual
            max_unidades = int(peso_disponible / insumo.peso_kg)
            
            if max_unidades > 0:
                unidades_adicionales = random.randint(0, min(max_unidades, 5))
                cantidades[idx] += unidades_adicionales
                peso_actual += unidades_adicionales * insumo.peso_kg
        
        return cantidades
    
    def _generar_cantidades_aleatorias(self, vehiculo: VehiculoBase) -> List[int]:
        """Generar cantidades completamente aleatorias"""
        capacidad_kg = vehiculo.maximo_peso_ton * 1000
        target_peso = capacidad_kg * random.uniform(0.4, 0.8)
        
        cantidades = [0] * self.num_insumos
        peso_actual = 0
        
        indices = list(range(self.num_insumos))
        random.shuffle(indices)
        
        for idx in indices:
            if peso_actual >= target_peso:
                break
                
            if random.random() < 0.3:  # 30% probabilidad de incluir cada insumo
                insumo = self.insumos[idx]
                peso_disponible = target_peso - peso_actual
                max_unidades = int(peso_disponible / insumo.peso_kg)
                
                if max_unidades > 0:
                    unidades = random.randint(1, min(max_unidades, 8))
                    cantidades[idx] = unidades
                    peso_actual += unidades * insumo.peso_kg
        
        return cantidades
    
    def _calcular_peso_total(self, cantidades: List[int]) -> float:
        """Calcular peso total basado en cantidades"""
        peso_total = 0.0
        for i, cantidad in enumerate(cantidades):
            if cantidad > 0:
                peso_total += cantidad * self.insumos[i].peso_kg
        return peso_total
    
    def _es_vehiculo_compatible(self, vehiculo: VehiculoBase, ruta: Ruta) -> bool:
        """Verificar compatibilidad vehículo-ruta"""
        if not ruta.vehiculos_permitidos:
            return True
        
        return any(tipo.lower() in vehiculo.tipo.lower() or 
                  vehiculo.tipo.lower() in tipo.lower() 
                  for tipo in ruta.vehiculos_permitidos)