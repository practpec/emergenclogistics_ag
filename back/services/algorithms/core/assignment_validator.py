from typing import List, Dict, Set
from ..models import Individual, VehicleAssignment

class AssignmentValidator:
    """Validador especializado para asignaciones y duplicados"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def find_duplicate_destinations(self, individuo: Individual) -> Dict[int, List[int]]:
        """Encontrar destinos duplicados en un individuo"""
        destinos_asignados = {}
        
        for i, asignacion in enumerate(individuo.vehiculos):
            mapeo_info = self.data_manager.mapeo_asignaciones[asignacion.id_destino_ruta]
            destino_id = mapeo_info['id_destino_perteneciente']
            
            if destino_id not in destinos_asignados:
                destinos_asignados[destino_id] = []
            destinos_asignados[destino_id].append(i)
        
        # Retornar solo los que tienen duplicados
        return {destino_id: vehiculos_indices 
                for destino_id, vehiculos_indices in destinos_asignados.items()
                if len(vehiculos_indices) > 1}
    
    def mark_invalid_assignments(self, individuo: Individual) -> List[bool]:
        """Marcar asignaciones válidas/inválidas considerando duplicados"""
        asignaciones_validas = [True] * len(individuo.vehiculos)
        duplicados = self.find_duplicate_destinations(individuo)
        
        # Marcar duplicados como inválidos (excepto el primero)
        for destino_id, vehiculos_indices in duplicados.items():
            for i, vehiculo_idx in enumerate(vehiculos_indices):
                if i > 0:  # Todos excepto el primero son inválidos
                    asignaciones_validas[vehiculo_idx] = False
        
        # Verificar validez técnica de las asignaciones restantes
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
    
    def find_free_destination(self, destinos_usados: Set[int], vehiculo_idx: int) -> Dict:
        """Encontrar un destino libre para reasignar un vehículo"""
        destinos_compatibles = self.data_manager.get_destinos_disponibles_para_vehiculo(vehiculo_idx)
        
        # Buscar destinos no usados
        for destino_info in destinos_compatibles:
            destino_id = destino_info['id_destino_perteneciente']
            if destino_id not in destinos_usados:
                return destino_info
        
        # Si no hay destinos libres, retornar uno aleatorio
        if destinos_compatibles:
            import random
            return random.choice(destinos_compatibles)
        
        # Último recurso: cualquier asignación
        import random
        return random.choice(self.data_manager.mapeo_asignaciones)
    
    def reassign_duplicates(self, individuo: Individual):
        """Reasignar vehículos con destinos duplicados"""
        duplicados = self.find_duplicate_destinations(individuo)
        destinos_usados = set()
        
        # Primero, marcar destinos únicos como usados
        for destino_id, vehiculos_indices in duplicados.items():
            if vehiculos_indices:
                destinos_usados.add(destino_id)
        
        # Agregar destinos no duplicados también
        for asignacion in individuo.vehiculos:
            mapeo_info = self.data_manager.mapeo_asignaciones[asignacion.id_destino_ruta]
            destino_id = mapeo_info['id_destino_perteneciente']
            if destino_id not in duplicados:
                destinos_usados.add(destino_id)
        
        # Reasignar vehículos duplicados
        for destino_id, vehiculos_indices in duplicados.items():
            # Mantener el primer vehículo, reasignar los demás
            for i, vehiculo_idx in enumerate(vehiculos_indices):
                if i == 0:
                    continue  # Mantener el primero
                
                # Encontrar nuevo destino para este vehículo
                nuevo_destino = self.find_free_destination(destinos_usados, vehiculo_idx)
                if nuevo_destino:
                    individuo.vehiculos[vehiculo_idx].id_destino_ruta = nuevo_destino['id_asignacion_unica']
                    nuevo_destino_id = nuevo_destino['id_destino_perteneciente']
                    destinos_usados.add(nuevo_destino_id)
    
    def count_unique_destinations(self, individuo: Individual) -> int:
        """Contar destinos únicos atendidos por un individuo"""
        destinos_unicos = set()
        for asignacion in individuo.vehiculos:
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
        for asignacion in individuo.vehiculos:
            from .capacity_manager import CapacityManager
            capacity_mgr = CapacityManager(self.data_manager)
            
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