import random
from typing import List, Dict, Any
from .models import Individual, VehicleAssignment

class PopulationInitializer:
    """Paso 1: Inicialización de población"""
    
    def __init__(self, num_vehiculos: int, mapeo_asignaciones: List[Dict], 
                 vehiculos_disponibles: List[Dict], insumos_data: List[Dict],
                 num_insumos: int, categorias_map: Dict, desastre_info: Any = None):
        self.num_vehiculos = num_vehiculos
        self.mapeo_asignaciones = mapeo_asignaciones
        self.vehiculos_disponibles = vehiculos_disponibles
        self.insumos_data = insumos_data
        self.num_insumos = num_insumos
        self.categorias_map = categorias_map
        self.desastre_info = desastre_info

    def inicializar_poblacion(self, poblacion_size: int) -> List[Individual]:
        """Generar población inicial"""
        poblacion = []
        
        for _ in range(poblacion_size):
            vehiculos_asignados = []
            vehiculos_disponibles_ids = list(range(self.num_vehiculos))
            
            for vehiculo_idx in vehiculos_disponibles_ids:
                # Asignar destino-ruta aleatoriamente
                asignacion = random.choice(self.mapeo_asignaciones)
                id_destino_ruta = asignacion['id_asignacion_unica']
                
                # Generar cantidades de insumos aleatorias
                vehiculo_info = self.vehiculos_disponibles[vehiculo_idx]
                capacidad_kg = vehiculo_info['capacidad_kg']
                insumos = self._generar_insumos_aleatorios(capacidad_kg)
                
                vehiculos_asignados.append(VehicleAssignment(
                    vehiculo_id=vehiculo_idx,
                    id_destino_ruta=id_destino_ruta,
                    insumos=insumos
                ))
            
            individuo = Individual(vehiculos=vehiculos_asignados)
            poblacion.append(individuo)
        
        return poblacion

    def _generar_insumos_aleatorios(self, capacidad_kg: float) -> List[int]:
        """Generar cantidades aleatorias de insumos respetando capacidad"""
        insumos = [0] * self.num_insumos
        peso_restante = capacidad_kg
        
        # Obtener insumos prioritarios por categoría
        insumos_prioritarios = self._get_insumos_prioritarios()
        
        # Distribuir insumos prioritarios primero
        for insumo_id in insumos_prioritarios:
            insumo_info = self.insumos_data[insumo_id]
            peso_unitario = insumo_info['peso_kg']
            
            if peso_unitario > 0 and peso_restante > peso_unitario:
                max_cantidad = min(8, int(peso_restante / peso_unitario))
                if max_cantidad > 0:
                    cantidad = random.randint(0, max_cantidad)
                    insumos[insumo_id] = cantidad
                    peso_restante -= cantidad * peso_unitario
        
        # Completar con otros insumos si queda capacidad
        insumos_restantes = [i for i in range(self.num_insumos) if i not in insumos_prioritarios]
        random.shuffle(insumos_restantes)
        
        for insumo_id in insumos_restantes:
            if peso_restante <= 0:
                break
            
            insumo_info = self.insumos_data[insumo_id]
            peso_unitario = insumo_info['peso_kg']
            
            if peso_unitario > 0 and peso_restante > peso_unitario:
                max_cantidad = min(4, int(peso_restante / peso_unitario))
                if max_cantidad > 0:
                    cantidad = random.randint(0, max_cantidad)
                    insumos[insumo_id] = cantidad
                    peso_restante -= cantidad * peso_unitario
        
        return insumos

    def _get_insumos_prioritarios(self) -> List[int]:
        """Obtener IDs de insumos prioritarios según el desastre"""
        if not self.desastre_info:
            return list(range(min(10, self.num_insumos)))
        
        insumos_prioritarios = []
        for prioridad in self.desastre_info.prioridad:
            if prioridad.nivel in ['alta', 'media']:
                categoria = prioridad.categoria
                if categoria in self.categorias_map:
                    insumos_prioritarios.extend(self.categorias_map[categoria])
        
        return insumos_prioritarios