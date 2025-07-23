# algorithms/initialization.py
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
        
        # Ordenar vehículos por capacidad (de menor a mayor)
        vehiculos_ordenados = sorted(self.vehiculos_disponibles, key=lambda v: v['capacidad_kg']) #
        # Ordenar asignaciones de destino por población (de menor a mayor)
        mapeo_asignaciones_ordenado = sorted(self.mapeo_asignaciones, key=lambda m: m['poblacion']) #

        for _ in range(poblacion_size):
            vehiculos_asignados = []
            vehiculos_disponibles_ids = list(range(self.num_vehiculos))
            random.shuffle(vehiculos_disponibles_ids) # Mezclar para variar las asignaciones
            
            destinos_ya_asignados = set() # Para evitar destinos repetidos en la inicialización
            rutas_disponibles_indices = list(range(len(mapeo_asignaciones_ordenado))) #
            random.shuffle(rutas_disponibles_indices) # Mezclar para la selección
            
            for i, vehiculo_idx in enumerate(vehiculos_disponibles_ids):
                vehiculo_info = vehiculos_ordenados[vehiculo_idx] # Usar vehículo ordenado
                
                # Intentar asignar destino basado en capacidad y población, evitando repeticiones
                asignacion_elegida = None
                for idx_mapeo in rutas_disponibles_indices: # Iterar sobre destinos mezclados
                    mapeo_info = mapeo_asignaciones_ordenado[idx_mapeo]
                    id_destino_actual = mapeo_info['id_destino_perteneciente'] #

                    if id_destino_actual not in destinos_ya_asignados: # Asegurarse que el destino no se repita
                        # Estrategia de asignación: Emparejar capacidad con población
                        # Si es un vehículo de baja capacidad y población baja, o alta capacidad y población alta
                        if (vehiculo_info['capacidad_kg'] < 1000 and mapeo_info['poblacion'] < 50) or \
                           (vehiculo_info['capacidad_kg'] > 1500 and mapeo_info['poblacion'] > 500) or \
                           (1000 <= vehiculo_info['capacidad_kg'] <= 1500 and 50 <= mapeo_info['poblacion'] <= 500): # Rango medio
                            asignacion_elegida = mapeo_info
                            break # Encontró una buena coincidencia y no repetida
                
                if asignacion_elegida is None: # Si no se encontró una coincidencia "inteligente" no repetida
                    # Fallback: Elegir cualquier destino no repetido restante
                    for idx_mapeo in rutas_disponibles_indices:
                        mapeo_info = mapeo_asignaciones_ordenado[idx_mapeo]
                        id_destino_actual = mapeo_info['id_destino_perteneciente']
                        if id_destino_actual not in destinos_ya_asignados:
                            asignacion_elegida = mapeo_info
                            break
                    if asignacion_elegida is None: # Si todos los destinos están asignados, puede repetir
                        asignacion_elegida = random.choice(self.mapeo_asignaciones) # Último recurso: aleatorio, puede repetir

                id_destino_ruta = asignacion_elegida['id_asignacion_unica'] #
                destinos_ya_asignados.add(asignacion_elegida['id_destino_perteneciente']) # Registrar el destino asignado

                # Generar cantidades de insumos aleatorias (con la modificación del 90%)
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
                    # Modificación para al menos 9/10 de capacidad
                    cantidad = random.randint(int(max_cantidad * 0.9), max_cantidad) if max_cantidad > 0 else 0
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
                    # Modificación para al menos 9/10 de capacidad
                    cantidad = random.randint(int(max_cantidad * 0.9), max_cantidad) if max_cantidad > 0 else 0
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