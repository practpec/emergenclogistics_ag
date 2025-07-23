import random
from typing import List, Tuple, Set
from .models import Individual, VehicleAssignment

class CrossoverOperator:
    """Operador de cruza mejorado que preserva diversidad de destinos"""
    
    def __init__(self, num_vehiculos: int):
        self.num_vehiculos = num_vehiculos

    def cruza_puntos_aleatorios(self, parejas: List[Tuple[Individual, Individual]], 
                               prob_cruza: float) -> List[Individual]:
        """Cruza mejorada con reparación OBLIGATORIA de capacidad"""
        descendencia = []
        
        for padre1, padre2 in parejas:
            if random.random() < prob_cruza:
                # Aplicar cruza inteligente
                hijo1, hijo2 = self._cruza_inteligente(padre1, padre2)
                
                # REPARACIÓN OBLIGATORIA de capacidad después de cruza
                for asignacion in hijo1.vehiculos:
                    self._reparar_capacidad_cruza(asignacion)
                for asignacion in hijo2.vehiculos:
                    self._reparar_capacidad_cruza(asignacion)
                
                descendencia.extend([hijo1, hijo2])
            else:
                # Copiar padres sin cruza pero con pequeñas mejoras
                hijo1 = self._copiar_y_mejorar(padre1)
                hijo2 = self._copiar_y_mejorar(padre2)
                
                # REPARACIÓN OBLIGATORIA
                for asignacion in hijo1.vehiculos:
                    self._reparar_capacidad_cruza(asignacion)
                for asignacion in hijo2.vehiculos:
                    self._reparar_capacidad_cruza(asignacion)
                
                descendencia.extend([hijo1, hijo2])
        
        return descendencia

    def _reparar_capacidad_cruza(self, asignacion):
        """Reparar capacidad específicamente después de cruza"""
        # Esta función debe ser importada desde mutation o redefinida aquí
        # Por simplicidad, implementación básica:
        vehiculo_idx = asignacion.vehiculo_id
        # Necesitaríamos acceso a vehiculos_disponibles e insumos_data
        # Por ahora, implementación simplificada que reduce proporcionalmente
        
        # Implementación simplificada - en producción debería usar los datos reales
        peso_total = sum(asignacion.insumos)  # Simplificación
        capacidad_estimada = 1000  # Capacidad promedio estimada
        
        if peso_total > capacidad_estimada:
            factor = capacidad_estimada * 0.9 / peso_total
            for i in range(len(asignacion.insumos)):
                asignacion.insumos[i] = max(0, int(asignacion.insumos[i] * factor))

    def _cruza_inteligente(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Cruza que intenta preservar las mejores características de cada padre"""
        
        # Estrategia de cruza aleatoria
        estrategia = random.choice([
            'destinos_preservados',  # 40% - Preservar destinos únicos
            'uniforme_mejorado',     # 35% - Cruza uniforme con validación
            'bloques_vehiculos'      # 25% - Cruza por bloques de vehículos
        ])
        
        if estrategia == 'destinos_preservados':
            return self._cruza_preservando_destinos(padre1, padre2)
        elif estrategia == 'uniforme_mejorado':
            return self._cruza_uniforme_mejorado(padre1, padre2)
        else:
            return self._cruza_por_bloques(padre1, padre2)

    def _cruza_preservando_destinos(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Cruza que intenta preservar diversidad de destinos"""
        
        # Analizar destinos de cada padre
        destinos_padre1 = self._extraer_destinos_unicos(padre1)
        destinos_padre2 = self._extraer_destinos_unicos(padre2)
        
        # Crear hijos preservando lo mejor de cada padre
        hijo1_vehiculos = []
        hijo2_vehiculos = []
        
        destinos_usado_hijo1 = set()
        destinos_usado_hijo2 = set()
        
        for i in range(self.num_vehiculos):
            asig_padre1 = padre1.vehiculos[i]
            asig_padre2 = padre2.vehiculos[i]
            
            # Para hijo1: intentar usar asignación de padre1, si no está repetida
            destino1 = self._get_destino_from_asignacion(padre1, i)
            if destino1 not in destinos_usado_hijo1:
                # Usar asignación de padre1 con posible cruza de insumos
                insumos_hijo1 = self._cruzar_insumos(asig_padre1.insumos, asig_padre2.insumos)
                hijo1_vehiculos.append(VehicleAssignment(
                    vehiculo_id=i,
                    id_destino_ruta=asig_padre1.id_destino_ruta,
                    insumos=insumos_hijo1
                ))
                destinos_usado_hijo1.add(destino1)
            else:
                # Usar asignación de padre2 o buscar alternativa
                destino2 = self._get_destino_from_asignacion(padre2, i)
                if destino2 not in destinos_usado_hijo1:
                    insumos_hijo1 = self._cruzar_insumos(asig_padre2.insumos, asig_padre1.insumos)
                    hijo1_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig_padre2.id_destino_ruta,
                        insumos=insumos_hijo1
                    ))
                    destinos_usado_hijo1.add(destino2)
                else:
                    # Usar padre1 con insumos modificados (permitir duplicado ocasional)
                    insumos_hijo1 = self._mutar_insumos_ligeramente(asig_padre1.insumos)
                    hijo1_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig_padre1.id_destino_ruta,
                        insumos=insumos_hijo1
                    ))
            
            # Para hijo2: lógica similar pero priorizando padre2
            destino2 = self._get_destino_from_asignacion(padre2, i)
            if destino2 not in destinos_usado_hijo2:
                insumos_hijo2 = self._cruzar_insumos(asig_padre2.insumos, asig_padre1.insumos)
                hijo2_vehiculos.append(VehicleAssignment(
                    vehiculo_id=i,
                    id_destino_ruta=asig_padre2.id_destino_ruta,
                    insumos=insumos_hijo2
                ))
                destinos_usado_hijo2.add(destino2)
            else:
                destino1 = self._get_destino_from_asignacion(padre1, i)
                if destino1 not in destinos_usado_hijo2:
                    insumos_hijo2 = self._cruzar_insumos(asig_padre1.insumos, asig_padre2.insumos)
                    hijo2_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig_padre1.id_destino_ruta,
                        insumos=insumos_hijo2
                    ))
                    destinos_usado_hijo2.add(destino1)
                else:
                    insumos_hijo2 = self._mutar_insumos_ligeramente(asig_padre2.insumos)
                    hijo2_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig_padre2.id_destino_ruta,
                        insumos=insumos_hijo2
                    ))
        
        return Individual(vehiculos=hijo1_vehiculos), Individual(vehiculos=hijo2_vehiculos)

    def _cruza_uniforme_mejorado(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Cruza uniforme con validación de destinos"""
        hijo1_vehiculos = []
        hijo2_vehiculos = []
        
        for i in range(self.num_vehiculos):
            asig_padre1 = padre1.vehiculos[i]
            asig_padre2 = padre2.vehiculos[i]
            
            # Decidir qué padre aporta el destino para cada hijo
            if random.random() < 0.5:
                # Hijo1 toma destino de padre1, hijo2 de padre2
                destino_hijo1 = asig_padre1.id_destino_ruta
                destino_hijo2 = asig_padre2.id_destino_ruta
                insumos_base1 = asig_padre1.insumos
                insumos_base2 = asig_padre2.insumos
            else:
                # Hijo1 toma destino de padre2, hijo2 de padre1
                destino_hijo1 = asig_padre2.id_destino_ruta
                destino_hijo2 = asig_padre1.id_destino_ruta
                insumos_base1 = asig_padre2.insumos
                insumos_base2 = asig_padre1.insumos
            
            # Cruzar insumos
            insumos_hijo1 = self._cruzar_insumos(insumos_base1, asig_padre2.insumos if destino_hijo1 == asig_padre1.id_destino_ruta else asig_padre1.insumos)
            insumos_hijo2 = self._cruzar_insumos(insumos_base2, asig_padre1.insumos if destino_hijo2 == asig_padre2.id_destino_ruta else asig_padre2.insumos)
            
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

    def _cruza_por_bloques(self, padre1: Individual, padre2: Individual) -> Tuple[Individual, Individual]:
        """Cruza intercambiando bloques de vehículos"""
        # Determinar puntos de corte
        num_puntos = random.randint(1, min(3, self.num_vehiculos - 1))
        puntos_corte = sorted(random.sample(range(1, self.num_vehiculos), num_puntos))
        
        hijo1_vehiculos = []
        hijo2_vehiculos = []
        
        # Alternar entre padres según los puntos de corte
        usar_padre1 = True
        inicio = 0
        
        for punto in puntos_corte + [self.num_vehiculos]:
            for i in range(inicio, punto):
                if usar_padre1:
                    # Copiar de padre1 a hijo1, padre2 a hijo2
                    asig1 = padre1.vehiculos[i]
                    asig2 = padre2.vehiculos[i]
                    
                    hijo1_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig1.id_destino_ruta,
                        insumos=self._mutar_insumos_ligeramente(asig1.insumos)
                    ))
                    
                    hijo2_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig2.id_destino_ruta,
                        insumos=self._mutar_insumos_ligeramente(asig2.insumos)
                    ))
                else:
                    # Copiar de padre2 a hijo1, padre1 a hijo2
                    asig1 = padre2.vehiculos[i]
                    asig2 = padre1.vehiculos[i]
                    
                    hijo1_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig1.id_destino_ruta,
                        insumos=self._mutar_insumos_ligeramente(asig1.insumos)
                    ))
                    
                    hijo2_vehiculos.append(VehicleAssignment(
                        vehiculo_id=i,
                        id_destino_ruta=asig2.id_destino_ruta,
                        insumos=self._mutar_insumos_ligeramente(asig2.insumos)
                    ))
            
            usar_padre1 = not usar_padre1
            inicio = punto
        
        return Individual(vehiculos=hijo1_vehiculos), Individual(vehiculos=hijo2_vehiculos)

    def _copiar_y_mejorar(self, padre: Individual) -> Individual:
        """Copiar individuo con pequeñas mejoras aleatorias"""
        vehiculos_mejorados = []
        
        for asignacion in padre.vehiculos:
            # Copiar con pequeña mutación en insumos
            insumos_mejorados = self._mutar_insumos_ligeramente(asignacion.insumos)
            
            vehiculos_mejorados.append(VehicleAssignment(
                vehiculo_id=asignacion.vehiculo_id,
                id_destino_ruta=asignacion.id_destino_ruta,
                insumos=insumos_mejorados
            ))
        
        return Individual(vehiculos=vehiculos_mejorados)

    def _extraer_destinos_unicos(self, individuo: Individual) -> Set[int]:
        """Extraer conjunto de destinos únicos de un individuo"""
        # Nota: Necesitaríamos acceso a mapeo_asignaciones para esto
        # Por simplicidad, usamos id_destino_ruta como proxy
        return set(asig.id_destino_ruta for asig in individuo.vehiculos)

    def _get_destino_from_asignacion(self, individuo: Individual, vehiculo_idx: int) -> int:
        """Obtener ID del destino para una asignación específica"""
        # Simplificación: usar id_destino_ruta como identificador de destino
        return individuo.vehiculos[vehiculo_idx].id_destino_ruta

    def _cruzar_insumos(self, insumos1: List[int], insumos2: List[int]) -> List[int]:
        """Cruzar insumos de manera inteligente"""
        if len(insumos1) != len(insumos2):
            return insumos1.copy()
        
        resultado = []
        
        for i in range(len(insumos1)):
            # Diferentes estrategias de cruza para insumos
            estrategia = random.choice(['promedio', 'maximo', 'aleatorio', 'ponderado'])
            
            if estrategia == 'promedio':
                # Promedio de ambos padres
                valor = (insumos1[i] + insumos2[i]) // 2
            elif estrategia == 'maximo':
                # Tomar el máximo de ambos
                valor = max(insumos1[i], insumos2[i])
            elif estrategia == 'aleatorio':
                # Seleccionar aleatoriamente de uno de los padres
                valor = random.choice([insumos1[i], insumos2[i]])
            else:  # ponderado
                # Ponderación aleatoria
                peso = random.random()
                valor = int(insumos1[i] * peso + insumos2[i] * (1 - peso))
            
            resultado.append(max(0, valor))  # Asegurar no negativos
        
        return resultado

    def _mutar_insumos_ligeramente(self, insumos: List[int]) -> List[int]:
        """Aplicar mutación ligera a los insumos"""
        resultado = insumos.copy()
        
        # Mutar algunos insumos aleatoriamente
        num_mutaciones = random.randint(0, min(3, len(insumos)))
        indices_mutar = random.sample(range(len(insumos)), num_mutaciones)
        
        for idx in indices_mutar:
            cambio = random.randint(-2, 3)  # Cambio pequeño
            resultado[idx] = max(0, resultado[idx] + cambio)
        
        return resultado