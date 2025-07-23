import random
from typing import List, Dict, Set
from .models import Individual

class MutationOperator:
    """Operador de mutación mejorado con estrategias anti-duplicación"""
    
    def __init__(self, num_vehiculos: int, mapeo_asignaciones: List[Dict],
                 vehiculos_disponibles: List[Dict], insumos_data: List[Dict]):
        self.num_vehiculos = num_vehiculos
        self.mapeo_asignaciones = mapeo_asignaciones
        self.vehiculos_disponibles = vehiculos_disponibles
        self.insumos_data = insumos_data
        
        # Crear mapas de destinos únicos
        self.destinos_unicos = list(set(
            m['id_destino_perteneciente'] for m in self.mapeo_asignaciones
        ))
        
        self.destinos_a_asignaciones = {}
        for mapeo in self.mapeo_asignaciones:
            destino_id = mapeo['id_destino_perteneciente']
            if destino_id not in self.destinos_a_asignaciones:
                self.destinos_a_asignaciones[destino_id] = []
            self.destinos_a_asignaciones[destino_id].append(mapeo)

    def mutacion_mover_segmento(self, poblacion: List[Individual], prob_mutacion: float) -> List[Individual]:
        """Mutación mejorada con reparación OBLIGATORIA de capacidad"""
        for individuo in poblacion:
            if random.random() < prob_mutacion:
                # Elegir tipo de mutación aleatoriamente
                tipo_mutacion = random.choice([
                    'reassign_duplicates',  # 30% - Reasignar duplicados
                    'swap_destinations',    # 25% - Intercambiar destinos
                    'optimize_supplies',    # 25% - Optimizar insumos
                    'rebalance_loads'      # 20% - Rebalancear cargas
                ])
                
                if tipo_mutacion == 'reassign_duplicates':
                    self._mutacion_reasignar_duplicados(individuo)
                elif tipo_mutacion == 'swap_destinations':
                    self._mutacion_intercambiar_destinos(individuo)
                elif tipo_mutacion == 'optimize_supplies':
                    self._mutacion_optimizar_insumos(individuo)
                elif tipo_mutacion == 'rebalance_loads':
                    self._mutacion_rebalancear_cargas(individuo)
            
            # REPARACIÓN OBLIGATORIA después de cada mutación
            for asignacion in individuo.vehiculos:
                self._reparar_capacidad(asignacion)
        
        return poblacion

    def _mutacion_reasignar_duplicados(self, individuo: Individual):
        """Mutación específica para eliminar destinos duplicados"""
        # Encontrar destinos duplicados
        destinos_asignados = {}
        for i, asignacion in enumerate(individuo.vehiculos):
            mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
            destino_id = mapeo_info['id_destino_perteneciente']
            
            if destino_id not in destinos_asignados:
                destinos_asignados[destino_id] = []
            destinos_asignados[destino_id].append(i)
        
        # Reasignar vehículos duplicados
        destinos_usados = set()
        for destino_id, vehiculos_indices in destinos_asignados.items():
            if len(vehiculos_indices) > 1:
                # Mantener el primer vehículo, reasignar los demás
                for i, vehiculo_idx in enumerate(vehiculos_indices):
                    if i == 0:
                        destinos_usados.add(destino_id)
                        continue
                    
                    # Reasignar este vehículo a un destino libre
                    nuevo_destino = self._encontrar_destino_libre(destinos_usados, vehiculo_idx)
                    if nuevo_destino:
                        individuo.vehiculos[vehiculo_idx].id_destino_ruta = nuevo_destino['id_asignacion_unica']
                        destinos_usados.add(nuevo_destino['id_destino_perteneciente'])
            else:
                destinos_usados.add(destino_id)

    def _mutacion_intercambiar_destinos(self, individuo: Individual):
        """Intercambiar destinos entre dos vehículos aleatoriamente"""
        if len(individuo.vehiculos) < 2:
            return
        
        # Seleccionar dos vehículos aleatoriamente
        idx1, idx2 = random.sample(range(len(individuo.vehiculos)), 2)
        
        # Intercambiar sus destinos
        temp_destino = individuo.vehiculos[idx1].id_destino_ruta
        individuo.vehiculos[idx1].id_destino_ruta = individuo.vehiculos[idx2].id_destino_ruta
        individuo.vehiculos[idx2].id_destino_ruta = temp_destino

    def _mutacion_optimizar_insumos(self, individuo: Individual):
        """Optimizar la carga de insumos de un vehículo aleatorio"""
        vehiculo_idx = random.randint(0, len(individuo.vehiculos) - 1)
        asignacion = individuo.vehiculos[vehiculo_idx]
        vehiculo_info = self.vehiculos_disponibles[asignacion.vehiculo_id]
        
        # Calcular peso actual
        peso_actual = sum(
            asignacion.insumos[i] * self.insumos_data[i]['peso_kg']
            for i in range(len(asignacion.insumos))
        )
        
        capacidad = vehiculo_info['capacidad_kg']
        utilizacion_actual = peso_actual / capacidad
        
        # Si la utilización es muy baja, incrementar insumos
        if utilizacion_actual < 0.6:
            self._incrementar_insumos(asignacion, capacidad * 0.9 - peso_actual)
        
        # Si la utilización es muy alta, redistribuir para optimizar
        elif utilizacion_actual > 0.95:
            self._redistribuir_insumos(asignacion, capacidad * 0.9)
        
        # Mutación normal de insumos
        else:
            self._mutar_insumos_normalmente(asignacion)

    def _mutacion_rebalancear_cargas(self, individuo: Individual):
        """Rebalancear cargas entre vehículos para mejor eficiencia"""
        if len(individuo.vehiculos) < 2:
            return
        
        # Encontrar vehículo subutilizado y vehículo sobreutilizado
        utilizaciones = []
        for i, asignacion in enumerate(individuo.vehiculos):
            vehiculo_info = self.vehiculos_disponibles[asignacion.vehiculo_id]
            peso_actual = sum(
                asignacion.insumos[j] * self.insumos_data[j]['peso_kg']
                for j in range(len(asignacion.insumos))
            )
            utilizacion = peso_actual / vehiculo_info['capacidad_kg']
            utilizaciones.append((i, utilizacion, peso_actual, vehiculo_info['capacidad_kg']))
        
        # Ordenar por utilización
        utilizaciones.sort(key=lambda x: x[1])
        
        # Tomar el menos utilizado y el más utilizado
        menos_util_idx, menos_util_ratio, peso_menor, cap_menor = utilizaciones[0]
        mas_util_idx, mas_util_ratio, peso_mayor, cap_mayor = utilizaciones[-1]
        
        # Solo rebalancear si hay una diferencia significativa
        if mas_util_ratio - menos_util_ratio > 0.3:
            self._transferir_insumos(
                individuo.vehiculos[mas_util_idx],
                individuo.vehiculos[menos_util_idx],
                cap_menor - peso_menor
            )

    def _encontrar_destino_libre(self, destinos_usados: Set[int], vehiculo_idx: int) -> Dict:
        """Encontrar un destino libre para reasignar un vehículo"""
        vehiculo_info = self.vehiculos_disponibles[vehiculo_idx]
        
        # Buscar destinos no usados
        destinos_libres = [d for d in self.destinos_unicos if d not in destinos_usados]
        
        if not destinos_libres:
            # Si no hay destinos libres, usar cualquiera
            return random.choice(self.mapeo_asignaciones)
        
        # Intentar encontrar destino compatible
        for destino_id in destinos_libres:
            asignaciones_destino = self.destinos_a_asignaciones[destino_id]
            
            # Buscar asignación compatible con el tipo de vehículo
            for asignacion in asignaciones_destino:
                # Aquí podrías agregar verificación de rutas_estado si está disponible
                # Por simplicidad, retornar la primera disponible
                return asignacion
        
        # Fallback: retornar cualquier asignación del primer destino libre
        destino_libre = destinos_libres[0]
        return self.destinos_a_asignaciones[destino_libre][0]

    def _incrementar_insumos(self, asignacion, peso_disponible: float):
        """Incrementar la cantidad de insumos respetando el peso disponible"""
        if peso_disponible <= 0:
            return
        
        # Encontrar insumos que se pueden incrementar
        insumos_incrementables = []
        for i, cantidad_actual in enumerate(asignacion.insumos):
            if cantidad_actual > 0:  # Solo incrementar insumos ya presentes
                peso_unitario = self.insumos_data[i]['peso_kg']
                if peso_unitario > 0 and peso_disponible >= peso_unitario:
                    max_incremento = int(peso_disponible / peso_unitario)
                    insumos_incrementables.append((i, max_incremento, peso_unitario))
        
        # Incrementar insumos aleatoriamente
        if insumos_incrementables:
            num_incrementos = random.randint(1, min(3, len(insumos_incrementables)))
            insumos_seleccionados = random.sample(insumos_incrementables, num_incrementos)
            
            peso_restante = peso_disponible
            for insumo_idx, max_incremento, peso_unitario in insumos_seleccionados:
                if peso_restante <= 0:
                    break
                
                incremento_posible = min(max_incremento, int(peso_restante / peso_unitario))
                if incremento_posible > 0:
                    incremento = random.randint(1, incremento_posible)
                    asignacion.insumos[insumo_idx] += incremento
                    peso_restante -= incremento * peso_unitario

    def _redistribuir_insumos(self, asignacion, peso_objetivo: float):
        """Redistribuir insumos para alcanzar un peso objetivo"""
        # Resetear todos los insumos y redistribuir
        insumos_originales = asignacion.insumos.copy()
        asignacion.insumos = [0] * len(asignacion.insumos)
        
        peso_restante = peso_objetivo
        
        # Redistribuir manteniendo proporciones similares
        total_original = sum(insumos_originales)
        if total_original > 0:
            for i, cantidad_original in enumerate(insumos_originales):
                if cantidad_original > 0 and peso_restante > 0:
                    peso_unitario = self.insumos_data[i]['peso_kg']
                    if peso_unitario > 0:
                        proporcion = cantidad_original / total_original
                        cantidad_objetivo = int((peso_objetivo / peso_unitario) * proporcion)
                        cantidad_real = min(cantidad_objetivo, int(peso_restante / peso_unitario))
                        
                        if cantidad_real > 0:
                            asignacion.insumos[i] = cantidad_real
                            peso_restante -= cantidad_real * peso_unitario

    def _mutar_insumos_normalmente(self, asignacion):
        """Aplicar mutación normal a los insumos"""
        # Seleccionar algunos insumos para mutar
        indices_a_mutar = random.sample(
            range(len(asignacion.insumos)), 
            random.randint(1, min(5, len(asignacion.insumos)))
        )
        
        for idx in indices_a_mutar:
            if random.random() < 0.5:
                # Incrementar
                asignacion.insumos[idx] += random.randint(1, 3)
            else:
                # Decrementar
                asignacion.insumos[idx] = max(0, asignacion.insumos[idx] - random.randint(1, 2))

    def _transferir_insumos(self, asignacion_origen, asignacion_destino, capacidad_disponible: float):
        """Transferir algunos insumos de un vehículo a otro"""
        if capacidad_disponible <= 0:
            return
        
        # Encontrar insumos que se pueden transferir
        transferibles = []
        for i, cantidad in enumerate(asignacion_origen.insumos):
            if cantidad > 1:  # Solo transferir si tiene más de 1
                peso_unitario = self.insumos_data[i]['peso_kg']
                if peso_unitario > 0 and capacidad_disponible >= peso_unitario:
                    max_transferible = min(cantidad - 1, int(capacidad_disponible / peso_unitario))
                    if max_transferible > 0:
                        transferibles.append((i, max_transferible, peso_unitario))
        
        # Realizar transferencias
        if transferibles:
            num_transferencias = random.randint(1, min(3, len(transferibles)))
            insumos_a_transferir = random.sample(transferibles, num_transferencias)
            
            capacidad_restante = capacidad_disponible
            for insumo_idx, max_cantidad, peso_unitario in insumos_a_transferir:
                if capacidad_restante <= 0:
                    break
                
                cantidad_maxima = min(max_cantidad, int(capacidad_restante / peso_unitario))
                if cantidad_maxima > 0:
                    cantidad_transferir = random.randint(1, cantidad_maxima)
                    
                    # Realizar transferencia
                    asignacion_origen.insumos[insumo_idx] -= cantidad_transferir
                    asignacion_destino.insumos[insumo_idx] += cantidad_transferir
                    capacidad_restante -= cantidad_transferir * peso_unitario

    def _reparar_capacidad(self, asignacion):
        """Reparar asignación que excede capacidad del vehículo - OBLIGATORIO"""
        vehiculo = self.vehiculos_disponibles[asignacion.vehiculo_id]
        capacidad_kg = vehiculo['capacidad_kg']
        
        peso_actual = sum(
            asignacion.insumos[i] * self.insumos_data[i]['peso_kg']
            for i in range(len(asignacion.insumos))
        )
        
        # Si excede capacidad, reducir AGRESIVAMENTE
        if peso_actual > capacidad_kg:
            peso_objetivo = capacidad_kg * 0.85  # Objetivo: 85% de capacidad
            
            # Método 1: Reducción proporcional
            if peso_actual > 0:
                factor_reduccion = peso_objetivo / peso_actual
                for i in range(len(asignacion.insumos)):
                    if asignacion.insumos[i] > 0:
                        nueva_cantidad = int(asignacion.insumos[i] * factor_reduccion)
                        asignacion.insumos[i] = max(0, nueva_cantidad)
            
            # Método 2: Verificación y ajuste fino
            peso_ajustado = sum(
                asignacion.insumos[i] * self.insumos_data[i]['peso_kg']
                for i in range(len(asignacion.insumos))
            )
            
            # Si aún excede, reducir elemento por elemento
            intentos = 0
            while peso_ajustado > capacidad_kg and intentos < 50:
                indices_con_insumos = [i for i, cant in enumerate(asignacion.insumos) if cant > 0]
                if not indices_con_insumos:
                    break
                
                # Priorizar reducir insumos con mayor peso total
                pesos_insumos = []
                for idx in indices_con_insumos:
                    peso_total = asignacion.insumos[idx] * self.insumos_data[idx]['peso_kg']
                    pesos_insumos.append((idx, peso_total))
                
                pesos_insumos.sort(key=lambda x: x[1], reverse=True)
                idx_reducir = pesos_insumos[0][0]
                
                peso_unitario = self.insumos_data[idx_reducir]['peso_kg']
                asignacion.insumos[idx_reducir] -= 1
                peso_ajustado -= peso_unitario
                intentos += 1
            
            # Método 3: Si aún excede, resetear completamente
            if peso_ajustado > capacidad_kg:
                asignacion.insumos = [0] * len(asignacion.insumos)