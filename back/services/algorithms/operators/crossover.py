import random
from typing import List, Tuple
from ..models import Individual, VehicleAssignment

class CrossoverOperator:
    """Operador de cruza optimizado"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager

    def crossover_population(self, parejas: List[Tuple[Individual, Individual]], 
                           prob_cruza: float) -> List[Individual]:
        """Cruza de población con reparación automática"""
        descendencia = []
        
        for padre1, padre2 in parejas:
            if random.random() < prob_cruza:
                hijo1, hijo2 = self._crossover_inteligente(padre1, padre2)
            else:
                hijo1 = self._copy_individual(padre1)
                hijo2 = self._copy_individual(padre2)
            
            # Reparación automática
            self._repair_individual(hijo1)
            self._repair_individual(hijo2)
            
            descendencia.extend([hijo1, hijo2])
        
        return descendencia

    def _crossover_inteligente(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Cruza inteligente preservando destinos únicos"""
        hijo1_vehiculos = []
        hijo2_vehiculos = []
        destinos_usado_hijo1 = set()
        destinos_usado_hijo2 = set()
        
        for i in range(len(padre1.vehiculos)):
            asig1 = padre1.vehiculos[i]
            asig2 = padre2.vehiculos[i]
            
            # Para hijo1: intentar usar padre1, fallback a padre2
            destino1 = self._get_destination_id(asig1.id_destino_ruta)
            if destino1 not in destinos_usado_hijo1:
                insumos1 = self._cross_supplies(asig1.insumos, asig2.insumos)
                hijo1_vehiculos.append(VehicleAssignment(
                    vehiculo_id=i,
                    id_destino_ruta=asig1.id_destino_ruta,
                    insumos=insumos1
                ))
                destinos_usado_hijo1.add(destino1)
            else:
                destino2 = self._get_destination_id(asig2.id_destino_ruta)
                if destino2 not in destinos_usado_hijo1:
                    insumos1 = self._cross_supplies(asig2.insumos, asig1.insumos)
                    hijo1_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig2.id_destino_ruta,
                        insumos=insumos1
                    ))
                    destinos_usado_hijo1.add(destino2)
                else:
                    # Buscar destino libre
                    destino_libre = self._find_free_destination(destinos_usado_hijo1, i)
                    insumos1 = self._mutate_supplies_lightly(asig1.insumos)
                    hijo1_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=destino_libre,
                        insumos=insumos1
                    ))
                    if destino_libre < len(self.data_manager.mapeo_asignaciones):
                        destino_id = self.data_manager.mapeo_asignaciones[destino_libre]['id_destino_perteneciente']
                        destinos_usado_hijo1.add(destino_id)
            
            # Lógica similar para hijo2
            destino2 = self._get_destination_id(asig2.id_destino_ruta)
            if destino2 not in destinos_usado_hijo2:
                insumos2 = self._cross_supplies(asig2.insumos, asig1.insumos)
                hijo2_vehiculos.append(VehicleAssignment(
                    vehiculo_id=i,
                    id_destino_ruta=asig2.id_destino_ruta,
                    insumos=insumos2
                ))
                destinos_usado_hijo2.add(destino2)
            else:
                destino1 = self._get_destination_id(asig1.id_destino_ruta)
                if destino1 not in destinos_usado_hijo2:
                    insumos2 = self._cross_supplies(asig1.insumos, asig2.insumos)
                    hijo2_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig1.id_destino_ruta,
                        insumos=insumos2
                    ))
                    destinos_usado_hijo2.add(destino1)
                else:
                    destino_libre = self._find_free_destination(destinos_usado_hijo2, i)
                    insumos2 = self._mutate_supplies_lightly(asig2.insumos)
                    hijo2_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=destino_libre,
                        insumos=insumos2
                    ))
                    if destino_libre < len(self.data_manager.mapeo_asignaciones):
                        destino_id = self.data_manager.mapeo_asignaciones[destino_libre]['id_destino_perteneciente']
                        destinos_usado_hijo2.add(destino_id)
        
        return Individual(vehiculos=hijo1_vehiculos), Individual(vehiculos=hijo2_vehiculos)

    def _get_destination_id(self, destino_ruta_id: int) -> str:
        """Obtener ID del destino"""
        if destino_ruta_id < len(self.data_manager.mapeo_asignaciones):
            return self.data_manager.mapeo_asignaciones[destino_ruta_id]['id_destino_perteneciente']
        return "default"

    def _find_free_destination(self, destinos_usados: set, vehiculo_idx: int) -> int:
        """Encontrar destino libre"""
        destinos_compatibles = self.data_manager.get_destinos_disponibles_para_vehiculo(vehiculo_idx)
        
        for destino_info in destinos_compatibles:
            destino_id = destino_info['id_destino_perteneciente']
            if destino_id not in destinos_usados:
                return destino_info['id_asignacion_unica']
        
        return random.randint(0, len(self.data_manager.mapeo_asignaciones) - 1)

    def _cross_supplies(self, insumos1: List[int], insumos2: List[int]) -> List[int]:
        """Cruzar insumos inteligentemente"""
        resultado = []
        for i in range(len(insumos1)):
            estrategia = random.choice(['promedio', 'maximo', 'aleatorio'])
            
            if estrategia == 'promedio':
                valor = (insumos1[i] + insumos2[i]) // 2
            elif estrategia == 'maximo':
                valor = max(insumos1[i], insumos2[i])
            else:
                valor = random.choice([insumos1[i], insumos2[i]])
            
            resultado.append(max(0, valor))
        return resultado

    def _mutate_supplies_lightly(self, insumos: List[int]) -> List[int]:
        """Mutación ligera de insumos"""
        resultado = insumos.copy()
        num_mutaciones = random.randint(0, min(3, len(insumos)))
        
        for _ in range(num_mutaciones):
            idx = random.randint(0, len(resultado) - 1)
            cambio = random.randint(-1, 2)
            resultado[idx] = max(0, resultado[idx] + cambio)
        
        return resultado

    def _copy_individual(self, individuo: Individual) -> Individual:
        """Copiar individuo"""
        vehiculos_copia = []
        for asig in individuo.vehiculos:
            vehiculos_copia.append(VehicleAssignment(
                vehiculo_id=asig.vehiculo_id,
                id_destino_ruta=asig.id_destino_ruta,
                insumos=asig.insumos.copy()
            ))
        return Individual(vehiculos=vehiculos_copia)

    def _repair_individual(self, individuo: Individual):
        """Reparar individuo automáticamente"""
        from ..core.capacity_manager import CapacityManager
        from ..core.assignment_validator import AssignmentValidator
        
        capacity_mgr = CapacityManager(self.data_manager)
        validator = AssignmentValidator(self.data_manager)
        
        # Reparar capacidades
        for asignacion in individuo.vehiculos:
            capacity_mgr.repair_capacity_violation(asignacion)
        
        # Reparar duplicados
        validator.reassign_duplicates(individuo)