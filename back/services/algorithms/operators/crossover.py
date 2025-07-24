import random
from typing import List, Tuple
from ..models import Individual, VehicleAssignment
from ..core.capacity_manager import CapacityManager
from ..core.assignment_validator import AssignmentValidator

class CrossoverOperator:
    """Operador de cruza refactorizado y simplificado"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.capacity_manager = CapacityManager(data_manager)
        self.validator = AssignmentValidator(data_manager)

    def crossover_population(self, parejas: List[Tuple[Individual, Individual]], 
                           prob_cruza: float) -> List[Individual]:
        """Método principal de cruza con reparación automática"""
        descendencia = []
        
        for padre1, padre2 in parejas:
            if random.random() < prob_cruza:
                hijo1, hijo2 = self._execute_intelligent_crossover(padre1, padre2)
            else:
                hijo1 = self._copy_and_improve(padre1)
                hijo2 = self._copy_and_improve(padre2)
            
            # Reparación automática OBLIGATORIA
            self._repair_offspring(hijo1)
            self._repair_offspring(hijo2)
            
            descendencia.extend([hijo1, hijo2])
        
        return descendencia

    def _execute_intelligent_crossover(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Ejecutar cruza inteligente con estrategia aleatoria"""
        estrategia = random.choice([
            'preserve_destinations',  # 40%
            'uniform_enhanced',       # 35%
            'vehicle_blocks'         # 25%
        ])
        
        if estrategia == 'preserve_destinations':
            return self._preserve_destinations_crossover(padre1, padre2)
        elif estrategia == 'uniform_enhanced':
            return self._uniform_enhanced_crossover(padre1, padre2)
        else:
            return self._vehicle_blocks_crossover(padre1, padre2)

    def _preserve_destinations_crossover(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Cruza preservando diversidad de destinos"""
        hijo1_vehiculos = []
        hijo2_vehiculos = []
        destinos_usado_hijo1 = set()
        destinos_usado_hijo2 = set()
        
        for i in range(self.data_manager.num_vehiculos):
            asig_padre1 = padre1.vehiculos[i]
            asig_padre2 = padre2.vehiculos[i]
            
            # Para hijo1: intentar usar asignación de padre1 si destino no repetido
            destino1 = self._get_destination_id(asig_padre1.id_destino_ruta)
            if destino1 not in destinos_usado_hijo1:
                insumos_hijo1 = self._cross_supplies(asig_padre1.insumos, asig_padre2.insumos)
                hijo1_vehiculos.append(VehicleAssignment(
                    vehiculo_id=i,
                    id_destino_ruta=asig_padre1.id_destino_ruta,
                    insumos=insumos_hijo1
                ))
                destinos_usado_hijo1.add(destino1)
            else:
                # Usar padre2 o buscar alternativa
                destino2 = self._get_destination_id(asig_padre2.id_destino_ruta)
                if destino2 not in destinos_usado_hijo1:
                    insumos_hijo1 = self._cross_supplies(asig_padre2.insumos, asig_padre1.insumos)
                    hijo1_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig_padre2.id_destino_ruta,
                        insumos=insumos_hijo1
                    ))
                    destinos_usado_hijo1.add(destino2)
                else:
                    # Buscar destino libre
                    destino_libre = self.validator.find_free_destination(destinos_usado_hijo1, i)
                    insumos_hijo1 = self._mutate_supplies_lightly(asig_padre1.insumos)
                    hijo1_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=destino_libre['id_asignacion_unica'],
                        insumos=insumos_hijo1
                    ))
                    destinos_usado_hijo1.add(destino_libre['id_destino_perteneciente'])
            
            # Para hijo2: lógica similar priorizando padre2
            destino2 = self._get_destination_id(asig_padre2.id_destino_ruta)
            if destino2 not in destinos_usado_hijo2:
                insumos_hijo2 = self._cross_supplies(asig_padre2.insumos, asig_padre1.insumos)
                hijo2_vehiculos.append(VehicleAssignment(
                    vehiculo_id=i,
                    id_destino_ruta=asig_padre2.id_destino_ruta,
                    insumos=insumos_hijo2
                ))
                destinos_usado_hijo2.add(destino2)
            else:
                destino1 = self._get_destination_id(asig_padre1.id_destino_ruta)
                if destino1 not in destinos_usado_hijo2:
                    insumos_hijo2 = self._cross_supplies(asig_padre1.insumos, asig_padre2.insumos)
                    hijo2_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig_padre1.id_destino_ruta,
                        insumos=insumos_hijo2
                    ))
                    destinos_usado_hijo2.add(destino1)
                else:
                    destino_libre = self.validator.find_free_destination(destinos_usado_hijo2, i)
                    insumos_hijo2 = self._mutate_supplies_lightly(asig_padre2.insumos)
                    hijo2_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=destino_libre['id_asignacion_unica'],
                        insumos=insumos_hijo2
                    ))
                    destinos_usado_hijo2.add(destino_libre['id_destino_perteneciente'])
        
        return Individual(vehiculos=hijo1_vehiculos), Individual(vehiculos=hijo2_vehiculos)

    def _uniform_enhanced_crossover(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Cruza uniforme mejorada"""
        hijo1_vehiculos = []
        hijo2_vehiculos = []
        
        for i in range(self.data_manager.num_vehiculos):
            asig_padre1 = padre1.vehiculos[i]
            asig_padre2 = padre2.vehiculos[i]
            
            # Decidir intercambio de destinos
            if random.random() < 0.5:
                destino_hijo1 = asig_padre1.id_destino_ruta
                destino_hijo2 = asig_padre2.id_destino_ruta
                base_insumos1 = asig_padre1.insumos
                base_insumos2 = asig_padre2.insumos
            else:
                destino_hijo1 = asig_padre2.id_destino_ruta
                destino_hijo2 = asig_padre1.id_destino_ruta
                base_insumos1 = asig_padre2.insumos
                base_insumos2 = asig_padre1.insumos
            
            # Cruzar insumos
            insumos_hijo1 = self._cross_supplies(base_insumos1, asig_padre2.insumos)
            insumos_hijo2 = self._cross_supplies(base_insumos2, asig_padre1.insumos)
            
            hijo1_vehiculos.append(VehicleAssignment(
                vehiculo_id=i,
                id_destino_ruta=destino_hijo1,
                insumos=insumos_hijo1
            ))
            
            hijo2_vehiculos.append(VehicleAssignment(
                vehiculo_id=i,
                id_destino_ruta=destino_hijo2,
                insumos=insumos_hijo2
            ))
        
        return Individual(vehiculos=hijo1_vehiculos), Individual(vehiculos=hijo2_vehiculos)

    def _vehicle_blocks_crossover(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Cruza por bloques de vehículos"""
        num_puntos = random.randint(1, min(3, self.data_manager.num_vehiculos - 1))
        puntos_corte = sorted(random.sample(range(1, self.data_manager.num_vehiculos), num_puntos))
        
        hijo1_vehiculos = []
        hijo2_vehiculos = []
        
        usar_padre1 = True
        inicio = 0
        
        for punto in puntos_corte + [self.data_manager.num_vehiculos]:
            for i in range(inicio, punto):
                if usar_padre1:
                    asig1 = padre1.vehiculos[i]
                    asig2 = padre2.vehiculos[i]
                else:
                    asig1 = padre2.vehiculos[i]
                    asig2 = padre1.vehiculos[i]
                
                hijo1_vehiculos.append(VehicleAssignment(
                    vehiculo_id=i,
                    id_destino_ruta=asig1.id_destino_ruta,
                    insumos=self._mutate_supplies_lightly(asig1.insumos)
                ))
                
                hijo2_vehiculos.append(VehicleAssignment(
                    vehiculo_id=i,
                    id_destino_ruta=asig2.id_destino_ruta,
                    insumos=self._mutate_supplies_lightly(asig2.insumos)
                ))
            
            usar_padre1 = not usar_padre1
            inicio = punto
        
        return Individual(vehiculos=hijo1_vehiculos), Individual(vehiculos=hijo2_vehiculos)

    def _copy_and_improve(self, padre: Individual) -> Individual:
        """Copiar individuo con pequeñas mejoras"""
        vehiculos_mejorados = []
        
        for asignacion in padre.vehiculos:
            insumos_mejorados = self._mutate_supplies_lightly(asignacion.insumos)
            vehiculos_mejorados.append(VehicleAssignment(
                vehiculo_id=asignacion.vehiculo_id,
                id_destino_ruta=asignacion.id_destino_ruta,
                insumos=insumos_mejorados
            ))
        
        return Individual(vehiculos=vehiculos_mejorados)

    def _repair_offspring(self, individuo: Individual):
        """Reparar descendencia automáticamente"""
        # Reparar capacidades
        for asignacion in individuo.vehiculos:
            self.capacity_manager.repair_capacity_violation(asignacion)
        
        # Reparar duplicados
        self.validator.reassign_duplicates(individuo)

    def _get_destination_id(self, destino_ruta_id: int) -> int:
        """Obtener ID del destino para una asignación"""
        mapeo = self.data_manager.mapeo_asignaciones[destino_ruta_id]
        return mapeo['id_destino_perteneciente']

    def _cross_supplies(self, insumos1: List[int], insumos2: List[int]) -> List[int]:
        """Cruzar insumos inteligentemente"""
        if len(insumos1) != len(insumos2):
            return insumos1.copy()
        
        resultado = []
        for i in range(len(insumos1)):
            estrategia = random.choice(['promedio', 'maximo', 'aleatorio', 'ponderado'])
            
            if estrategia == 'promedio':
                valor = (insumos1[i] + insumos2[i]) // 2
            elif estrategia == 'maximo':
                valor = max(insumos1[i], insumos2[i])
            elif estrategia == 'aleatorio':
                valor = random.choice([insumos1[i], insumos2[i]])
            else:  # ponderado
                peso = random.random()
                valor = int(insumos1[i] * peso + insumos2[i] * (1 - peso))
            
            resultado.append(max(0, valor))
        
        return resultado

    def _mutate_supplies_lightly(self, insumos: List[int]) -> List[int]:
        """Mutación ligera de insumos"""
        resultado = insumos.copy()
        num_mutaciones = random.randint(0, min(3, len(insumos)))
        indices_mutar = random.sample(range(len(insumos)), num_mutaciones)
        
        for idx in indices_mutar:
            cambio = random.randint(-2, 3)
            resultado[idx] = max(0, resultado[idx] + cambio)
        
        return resultado