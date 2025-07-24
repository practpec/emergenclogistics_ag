from typing import List, Dict, Set
from ..models import Individual, VehicleAssignment

class AssignmentValidator:
    """Validador optimizado para asignaciones y duplicados"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def find_duplicate_destinations(self, individuo: Individual) -> Dict[str, List[int]]:
        """Encontrar destinos duplicados en un individuo"""
        destinos_asignados = {}
        
        for i, asignacion in enumerate(individuo.vehiculos):
            if asignacion.id_destino_ruta < len(self.data_manager.mapeo_asignaciones):
                mapeo_info = self.data_manager.mapeo_asignaciones[asignacion.id_destino_ruta]
                destino_id = mapeo_info['id_destino_perteneciente']
                
                if destino_id not in destinos_asignados:
                    destinos_asignados[destino_id] = []
                destinos_asignados[destino_id].append(i)
        
        # Retornar solo destinos con duplicados
        return {destino_id: vehiculos_indices 
                for destino_id, vehiculos_indices in destinos_asignados.items()
                if len(vehiculos_indices) > 1}
    
    def mark_invalid_assignments(self, individuo: Individual) -> List[bool]:
        """Marcar asignaciones válidas/inválidas considerando duplicados"""
        asignaciones_validas = [True] * len(individuo.vehiculos)
        duplicados = self.find_duplicate_destinations(individuo)
        
        # Marcar duplicados como inválidos (mantener solo el primero)
        for destino_id, vehiculos_indices in duplicados.items():
            for i, vehiculo_idx in enumerate(vehiculos_indices):
                if i > 0:
                    asignaciones_validas[vehiculo_idx] = False
        
        # Verificar validez técnica de asignaciones restantes
        for i, asignacion in enumerate(individuo.vehiculos):
            if asignaciones_validas[i]:
                if not self._is_technically_valid(asignacion):
                    asignaciones_validas[i] = False
        
        return asignaciones_validas
    
    def _is_technically_valid(self, asignacion: VehicleAssignment) -> bool:
        """Verificar validez técnica de una asignación"""
        return self.data_manager.validate_assignment(
            asignacion.vehiculo_id,
            asignacion.id_destino_ruta,
            asignacion.insumos
        )
    
    def find_free_destination(self, destinos_usados: Set, vehiculo_idx: int) -> Dict:
        """Encontrar destino libre para reasignar vehículo"""
        destinos_compatibles = self.data_manager.get_destinos_disponibles_para_vehiculo(vehiculo_idx)
        
        # Buscar destinos no usados
        for destino_info in destinos_compatibles:
            destino_id = destino_info['id_destino_perteneciente']
            if destino_id not in destinos_usados:
                return destino_info
        
        # Si no hay destinos libres, retornar uno aleatorio compatible
        if destinos_compatibles:
            import random
            return random.choice(destinos_compatibles)
        
        # Último recurso: cualquier asignación válida
        if self.data_manager.mapeo_asignaciones:
            import random
            return random.choice(self.data_manager.mapeo_asignaciones)
        
        return None
    
    def reassign_duplicates(self, individuo: Individual):
        """Reasignar vehículos con destinos duplicados de forma optimizada"""
        duplicados = self.find_duplicate_destinations(individuo)
        
        if not duplicados:
            return
        
        destinos_usados = set()
        
        # Primero, marcar destinos únicos como usados
        for asignacion in individuo.vehiculos:
            if asignacion.id_destino_ruta < len(self.data_manager.mapeo_asignaciones):
                mapeo_info = self.data_manager.mapeo_asignaciones[asignacion.id_destino_ruta]
                destino_id = mapeo_info['id_destino_perteneciente']
                if destino_id not in duplicados:
                    destinos_usados.add(destino_id)
        
        # Reasignar vehículos duplicados
        for destino_id, vehiculos_indices in duplicados.items():
            # Mantener primer vehículo, reasignar resto
            for i, vehiculo_idx in enumerate(vehiculos_indices):
                if i == 0:
                    destinos_usados.add(destino_id)
                    continue
                
                # Encontrar nuevo destino
                nuevo_destino = self.find_free_destination(destinos_usados, vehiculo_idx)
                if nuevo_destino:
                    individuo.vehiculos[vehiculo_idx].id_destino_ruta = nuevo_destino['id_asignacion_unica']
                    nuevo_destino_id = nuevo_destino['id_destino_perteneciente']
                    destinos_usados.add(nuevo_destino_id)
    
    def count_unique_destinations(self, individuo: Individual) -> int:
        """Contar destinos únicos atendidos"""
        destinos_unicos = set()
        for asignacion in individuo.vehiculos:
            if asignacion.id_destino_ruta < len(self.data_manager.mapeo_asignaciones):
                mapeo_info = self.data_manager.mapeo_asignaciones[asignacion.id_destino_ruta]
                destino_id = mapeo_info['id_destino_perteneciente']
                destinos_unicos.add(destino_id)
        return len(destinos_unicos)
    
    def get_destination_coverage_rate(self, individuo: Individual) -> float:
        """Calcular tasa de cobertura de destinos únicos"""
        destinos_atendidos = self.count_unique_destinations(individuo)
        max_destinos_posibles = len(self.data_manager.destinos_unicos)
        return destinos_atendidos / max_destinos_posibles if max_destinos_posibles > 0 else 0
    
    def validate_individual_integrity(self, individuo: Individual) -> Dict[str, any]:
        """Validar integridad completa de un individuo"""
        duplicados = self.find_duplicate_destinations(individuo)
        asignaciones_validas = self.mark_invalid_assignments(individuo)
        
        # Estadísticas de capacidad
        sobrecargas = 0
        utilizacion_total = 0
        
        from .capacity_manager import CapacityManager
        capacity_mgr = CapacityManager(self.data_manager)
        
        for asignacion in individuo.vehiculos:
            if capacity_mgr.is_overloaded(asignacion):
                sobrecargas += 1
            utilizacion_total += capacity_mgr.get_utilization_rate(asignacion)
        
        utilizacion_promedio = utilizacion_total / len(individuo.vehiculos) if individuo.vehiculos else 0
        
        return {
            'destinos_duplicados': len(duplicados),
            'asignaciones_invalidas': sum(1 for v in asignaciones_validas if not v),
            'vehiculos_sobrecargados': sobrecargas,
            'cobertura_destinos': self.get_destination_coverage_rate(individuo),
            'utilizacion_promedio': utilizacion_promedio,
            'es_valido': len(duplicados) == 0 and all(asignaciones_validas) and sobrecargas == 0
        }
    
    def repair_all_violations(self, individuo: Individual):
        """Reparar todas las violaciones de un individuo"""
        from .capacity_manager import CapacityManager
        capacity_mgr = CapacityManager(self.data_manager)
        
        # Reparar capacidades
        for asignacion in individuo.vehiculos:
            capacity_mgr.repair_capacity_violation(asignacion)
        
        # Reparar duplicados
        self.reassign_duplicates(individuo)
    
    def optimize_destination_distribution(self, individuo: Individual):
        """Optimizar distribución de destinos para maximizar cobertura"""
        duplicados = self.find_duplicate_destinations(individuo)
        
        if not duplicados:
            return
        
        # Estrategia: redistribuir para maximizar destinos únicos
        destinos_disponibles = set(self.data_manager.destinos_unicos)
        destinos_asignados = set()
        
        # Marcar destinos ya asignados (sin duplicados)
        for asignacion in individuo.vehiculos:
            if asignacion.id_destino_ruta < len(self.data_manager.mapeo_asignaciones):
                mapeo_info = self.data_manager.mapeo_asignaciones[asignacion.id_destino_ruta]
                destino_id = mapeo_info['id_destino_perteneciente']
                if destino_id not in duplicados:
                    destinos_asignados.add(destino_id)
        
        destinos_libres = destinos_disponibles - destinos_asignados
        
        # Reasignar duplicados a destinos libres
        for destino_id, vehiculos_indices in duplicados.items():
            destinos_asignados.add(destino_id)  # Mantener el primero
            
            for i, vehiculo_idx in enumerate(vehiculos_indices):
                if i == 0:
                    continue
                
                if destinos_libres:
                    nuevo_destino_id = destinos_libres.pop()
                    # Encontrar asignación para este destino
                    asignaciones_destino = self.data_manager.destinos_a_asignaciones.get(nuevo_destino_id, [])
                    if asignaciones_destino:
                        nueva_asignacion = asignaciones_destino[0]
                        individuo.vehiculos[vehiculo_idx].id_destino_ruta = nueva_asignacion['id_asignacion_unica']
                        destinos_asignados.add(nuevo_destino_id)