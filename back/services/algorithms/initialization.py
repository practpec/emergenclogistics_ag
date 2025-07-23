# algorithms/initialization.py
import random
from typing import List, Dict, Any
from .models import Individual, VehicleAssignment

class PopulationInitializer:
    """Inicializador de población mejorado con estrategias inteligentes"""
    
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
        
        # Crear lista de destinos únicos disponibles
        self.destinos_unicos = list(set(
            m['id_destino_perteneciente'] for m in self.mapeo_asignaciones
        ))
        
        # Crear mapeo de destinos a asignaciones disponibles
        self.destinos_a_asignaciones = {}
        for mapeo in self.mapeo_asignaciones:
            destino_id = mapeo['id_destino_perteneciente']
            if destino_id not in self.destinos_a_asignaciones:
                self.destinos_a_asignaciones[destino_id] = []
            self.destinos_a_asignaciones[destino_id].append(mapeo)

    def inicializar_poblacion(self, poblacion_size: int) -> List[Individual]:
        """Generar población inicial con estrategias mejoradas"""
        poblacion = []
        
        # Estrategia 1: 40% - Asignación por capacidad (sin duplicados)
        num_capacidad = int(poblacion_size * 0.4)
        for _ in range(num_capacidad):
            individuo = self._generar_por_capacidad()
            poblacion.append(individuo)
        
        # Estrategia 2: 30% - Asignación por población de destinos
        num_poblacion = int(poblacion_size * 0.3)
        for _ in range(num_poblacion):
            individuo = self._generar_por_poblacion()
            poblacion.append(individuo)
        
        # Estrategia 3: 20% - Asignación balanceada
        num_balanceada = int(poblacion_size * 0.2)
        for _ in range(num_balanceada):
            individuo = self._generar_balanceada()
            poblacion.append(individuo)
        
        # Estrategia 4: 10% - Completamente aleatoria
        num_restante = poblacion_size - len(poblacion)
        for _ in range(num_restante):
            individuo = self._generar_aleatoria()
            poblacion.append(individuo)
        
        return poblacion

    def _generar_por_capacidad(self) -> Individual:
        """Generar individuo asignando vehículos por capacidad sin duplicar destinos"""
        vehiculos_asignados = []
        destinos_usados = set()
        
        # Ordenar vehículos por capacidad (mayor a menor)
        vehiculos_ordenados = sorted(
            enumerate(self.vehiculos_disponibles), 
            key=lambda x: x[1]['capacidad_kg'], 
            reverse=True
        )
        
        # Ordenar destinos por población (mayor a menor)
        destinos_ordenados = sorted(
            self.destinos_unicos, 
            key=lambda dest_id: max(
                m['poblacion'] for m in self.destinos_a_asignaciones[dest_id]
            ), 
            reverse=True
        )
        
        for vehiculo_idx, vehiculo_info in vehiculos_ordenados:
            # Buscar primer destino disponible no usado
            destino_asignado = None
            asignacion_elegida = None
            
            for destino_id in destinos_ordenados:
                if destino_id not in destinos_usados:
                    # Encontrar mejor asignación para este destino
                    asignaciones_destino = self.destinos_a_asignaciones[destino_id]
                    asignacion_valida = self._encontrar_asignacion_valida(
                        vehiculo_info, asignaciones_destino
                    )
                    
                    if asignacion_valida:
                        destino_asignado = destino_id
                        asignacion_elegida = asignacion_valida
                        destinos_usados.add(destino_id)
                        break
            
            # Si no encontró destino válido, usar uno aleatorio disponible
            if asignacion_elegida is None:
                destinos_disponibles = [d for d in self.destinos_unicos if d not in destinos_usados]
                if destinos_disponibles:
                    destino_id = random.choice(destinos_disponibles)
                    asignaciones_destino = self.destinos_a_asignaciones[destino_id]
                    asignacion_elegida = random.choice(asignaciones_destino)
                    destinos_usados.add(destino_id)
                else:
                    # Último recurso: cualquier asignación
                    asignacion_elegida = random.choice(self.mapeo_asignaciones)
            
            # Generar insumos optimizados
            insumos = self._generar_insumos_por_capacidad(vehiculo_info['capacidad_kg'])
            
            vehiculos_asignados.append(VehicleAssignment(
                vehiculo_id=vehiculo_idx,
                id_destino_ruta=asignacion_elegida['id_asignacion_unica'],
                insumos=insumos
            ))
        
        return Individual(vehiculos=vehiculos_asignados)

    def _generar_por_poblacion(self) -> Individual:
        """Generar individuo priorizando destinos por población"""
        vehiculos_asignados = []
        destinos_usados = set()
        
        # Mezclar vehículos para variabilidad
        vehiculos_mezclados = list(enumerate(self.vehiculos_disponibles))
        random.shuffle(vehiculos_mezclados)
        
        # Ordenar destinos por población
        destinos_por_poblacion = sorted(
            self.destinos_unicos,
            key=lambda dest_id: max(
                m['poblacion'] for m in self.destinos_a_asignaciones[dest_id]
            ),
            reverse=True
        )
        
        for vehiculo_idx, vehiculo_info in vehiculos_mezclados:
            # Asignar a destino de alta población si está disponible
            destino_asignado = None
            asignacion_elegida = None
            
            # Priorizar destinos de alta población
            for destino_id in destinos_por_poblacion:
                if destino_id not in destinos_usados:
                    asignaciones_destino = self.destinos_a_asignaciones[destino_id]
                    asignacion_valida = self._encontrar_asignacion_valida(
                        vehiculo_info, asignaciones_destino
                    )
                    
                    if asignacion_valida:
                        asignacion_elegida = asignacion_valida
                        destinos_usados.add(destino_id)
                        break
            
            # Fallback a asignación aleatoria si es necesario
            if asignacion_elegida is None:
                asignacion_elegida = self._asignar_destino_fallback(destinos_usados, vehiculo_info)
                if asignacion_elegida:
                    destino_id = self.mapeo_asignaciones[
                        asignacion_elegida['id_asignacion_unica']
                    ]['id_destino_perteneciente']
                    destinos_usados.add(destino_id)
            
            # Generar insumos apropiados para la población del destino
            poblacion_destino = asignacion_elegida['poblacion'] if asignacion_elegida else 100
            insumos = self._generar_insumos_por_poblacion(
                vehiculo_info['capacidad_kg'], poblacion_destino
            )
            
            vehiculos_asignados.append(VehicleAssignment(
                vehiculo_id=vehiculo_idx,
                id_destino_ruta=asignacion_elegida['id_asignacion_unica'] if asignacion_elegida else 0,
                insumos=insumos
            ))
        
        return Individual(vehiculos=vehiculos_asignados)

    def _generar_balanceada(self) -> Individual:
        """Generar individuo con estrategia balanceada"""
        vehiculos_asignados = []
        destinos_usados = set()
        
        # Mezclar tanto vehículos como destinos
        vehiculos_mezclados = list(enumerate(self.vehiculos_disponibles))
        random.shuffle(vehiculos_mezclados)
        
        destinos_mezclados = self.destinos_unicos.copy()
        random.shuffle(destinos_mezclados)
        
        for i, (vehiculo_idx, vehiculo_info) in enumerate(vehiculos_mezclados):
            asignacion_elegida = None
            
            # Intentar asignar a destino no usado
            for destino_id in destinos_mezclados:
                if destino_id not in destinos_usados:
                    asignaciones_destino = self.destinos_a_asignaciones[destino_id]
                    asignacion_valida = self._encontrar_asignacion_valida(
                        vehiculo_info, asignaciones_destino
                    )
                    
                    if asignacion_valida:
                        asignacion_elegida = asignacion_valida
                        destinos_usados.add(destino_id)
                        break
            
            # Fallback
            if asignacion_elegida is None:
                asignacion_elegida = self._asignar_destino_fallback(destinos_usados, vehiculo_info)
            
            # Generar insumos balanceados
            insumos = self._generar_insumos_balanceados(vehiculo_info['capacidad_kg'])
            
            vehiculos_asignados.append(VehicleAssignment(
                vehiculo_id=vehiculo_idx,
                id_destino_ruta=asignacion_elegida['id_asignacion_unica'] if asignacion_elegida else 0,
                insumos=insumos
            ))
        
        return Individual(vehiculos=vehiculos_asignados)

    def _generar_aleatoria(self) -> Individual:
        """Generar individuo completamente aleatorio pero sin duplicar destinos"""
        vehiculos_asignados = []
        destinos_usados = set()
        
        vehiculos_indices = list(range(self.num_vehiculos))
        random.shuffle(vehiculos_indices)
        
        for vehiculo_idx in vehiculos_indices:
            vehiculo_info = self.vehiculos_disponibles[vehiculo_idx]
            
            # Intentar asignar destino único
            intentos = 0
            asignacion_elegida = None
            
            while intentos < 10 and asignacion_elegida is None:
                candidato = random.choice(self.mapeo_asignaciones)
                destino_id = candidato['id_destino_perteneciente']
                
                if destino_id not in destinos_usados:
                    asignacion_elegida = candidato
                    destinos_usados.add(destino_id)
                    break
                
                intentos += 1
            
            # Si no pudo encontrar destino único, usar cualquiera
            if asignacion_elegida is None:
                asignacion_elegida = random.choice(self.mapeo_asignaciones)
            
            # Generar insumos aleatorios
            insumos = self._generar_insumos_aleatorios(vehiculo_info['capacidad_kg'])
            
            vehiculos_asignados.append(VehicleAssignment(
                vehiculo_id=vehiculo_idx,
                id_destino_ruta=asignacion_elegida['id_asignacion_unica'],
                insumos=insumos
            ))
        
        return Individual(vehiculos=vehiculos_asignados)

    def _encontrar_asignacion_valida(self, vehiculo_info: Dict, asignaciones_destino: List[Dict]) -> Dict:
        """Encontrar una asignación válida para el vehículo en el destino"""
        # Filtrar asignaciones compatibles con el tipo de vehículo
        asignaciones_compatibles = []
        
        for asignacion in asignaciones_destino:
            # Construir ID de ruta para verificar estado
            destino_id = asignacion['id_destino_perteneciente']
            ruta_id = f"Destino{destino_id}-Ruta{asignacion['id_ruta_en_destino'] + 1}"
            
            # Verificar en rutas_estado si existe, sino asumir abierta
            from core.base_service import BaseService
            estado_ruta = getattr(self, 'rutas_estado', {}).get(ruta_id, {
                'estado': 'abierta',
                'vehiculos_permitidos': [vehiculo_info['tipo']]
            })
            
            if (estado_ruta['estado'] == 'abierta' and 
                vehiculo_info['tipo'] in estado_ruta['vehiculos_permitidos']):
                asignaciones_compatibles.append(asignacion)
        
        # Retornar una asignación compatible aleatoria
        return random.choice(asignaciones_compatibles) if asignaciones_compatibles else None

    def _asignar_destino_fallback(self, destinos_usados: set, vehiculo_info: Dict) -> Dict:
        """Asignar destino como último recurso"""
        destinos_disponibles = [d for d in self.destinos_unicos if d not in destinos_usados]
        
        if destinos_disponibles:
            destino_id = random.choice(destinos_disponibles)
            asignaciones_destino = self.destinos_a_asignaciones[destino_id]
            return random.choice(asignaciones_destino)
        else:
            # Último recurso: cualquier asignación
            return random.choice(self.mapeo_asignaciones)

    def _generar_insumos_por_capacidad(self, capacidad_kg: float) -> List[int]:
        """Generar insumos NUNCA excediendo la capacidad máxima"""
        insumos = [0] * self.num_insumos
        peso_maximo = capacidad_kg * 0.95  # NUNCA exceder 95% de capacidad
        peso_restante = peso_maximo
        
        # Obtener insumos prioritarios
        insumos_prioritarios = self._get_insumos_prioritarios()
        
        # Llenar primero con insumos prioritarios
        insumos_mezclados = insumos_prioritarios.copy()
        random.shuffle(insumos_mezclados)
        
        for insumo_id in insumos_mezclados:
            if peso_restante <= 0:
                break
                
            peso_unitario = self.insumos_data[insumo_id]['peso_kg']
            if peso_unitario > 0 and peso_restante >= peso_unitario:
                max_cantidad = max(1, int(peso_restante / peso_unitario))
                cantidad = random.randint(1, min(max_cantidad, 10))
                
                # VERIFICAR que no exceda capacidad
                peso_total_nuevo = cantidad * peso_unitario
                if peso_total_nuevo <= peso_restante:
                    insumos[insumo_id] = cantidad
                    peso_restante -= peso_total_nuevo
        
        # Completar con otros insumos si queda espacio
        otros_insumos = [i for i in range(self.num_insumos) if i not in insumos_prioritarios]
        random.shuffle(otros_insumos)
        
        for insumo_id in otros_insumos:
            if peso_restante <= 0:
                break
                
            peso_unitario = self.insumos_data[insumo_id]['peso_kg']
            if peso_unitario > 0 and peso_restante >= peso_unitario:
                max_cantidad = max(1, int(peso_restante / peso_unitario))
                cantidad = random.randint(1, min(max_cantidad, 5))
                
                # VERIFICAR que no exceda capacidad
                peso_total_nuevo = cantidad * peso_unitario
                if peso_total_nuevo <= peso_restante:
                    insumos[insumo_id] = cantidad
                    peso_restante -= peso_total_nuevo
        
        # VERIFICACIÓN FINAL - asegurar que nunca exceda
        peso_final = sum(insumos[i] * self.insumos_data[i]['peso_kg'] for i in range(self.num_insumos))
        if peso_final > capacidad_kg:
            # Reducir proporcionalmente
            factor = (capacidad_kg * 0.9) / peso_final
            for i in range(self.num_insumos):
                if insumos[i] > 0:
                    insumos[i] = max(1, int(insumos[i] * factor))
        
        return insumos

    def _generar_insumos_por_poblacion(self, capacidad_kg: float, poblacion: int) -> List[int]:
        """Generar insumos apropiados para el tamaño de población"""
        insumos = [0] * self.num_insumos
        
        # Calcular factor de población (más población = más insumos)
        factor_poblacion = min(poblacion / 500, 2.0)  # Máximo 2x
        peso_objetivo = capacidad_kg * random.uniform(0.8, 0.95) * factor_poblacion
        peso_objetivo = min(peso_objetivo, capacidad_kg * 0.98)  # No exceder capacidad
        
        peso_restante = peso_objetivo
        insumos_prioritarios = self._get_insumos_prioritarios()
        
        # Distribuir insumos según población
        for insumo_id in insumos_prioritarios:
            if peso_restante <= 0:
                break
                
            peso_unitario = self.insumos_data[insumo_id]['peso_kg']
            if peso_unitario > 0 and peso_restante > peso_unitario:
                # Más cantidad para poblaciones grandes
                base_cantidad = max(1, int(poblacion / 100))
                max_cantidad = min(int(peso_restante / peso_unitario), base_cantidad * 2)
                
                if max_cantidad > 0:
                    cantidad = random.randint(1, max_cantidad)
                    insumos[insumo_id] = cantidad
                    peso_restante -= cantidad * peso_unitario
        
        return insumos

    def _generar_insumos_balanceados(self, capacidad_kg: float) -> List[int]:
        """Generar insumos con distribución balanceada"""
        insumos = [0] * self.num_insumos
        peso_objetivo = capacidad_kg * random.uniform(0.75, 0.9)
        peso_restante = peso_objetivo
        
        # Intentar incluir insumos de todas las categorías disponibles
        categorias_disponibles = list(self.categorias_map.keys())
        random.shuffle(categorias_disponibles)
        
        for categoria in categorias_disponibles:
            if peso_restante <= 0:
                break
                
            insumos_categoria = self.categorias_map[categoria]
            insumo_id = random.choice(insumos_categoria)
            
            peso_unitario = self.insumos_data[insumo_id]['peso_kg']
            if peso_unitario > 0 and peso_restante > peso_unitario:
                max_cantidad = int(peso_restante / peso_unitario)
                cantidad = random.randint(1, min(max_cantidad, 8))
                insumos[insumo_id] = cantidad
                peso_restante -= cantidad * peso_unitario
        
        return insumos

    def _generar_insumos_aleatorios(self, capacidad_kg: float) -> List[int]:
        """Generar cantidades aleatorias respetando capacidad"""
        insumos = [0] * self.num_insumos
        peso_restante = capacidad_kg * random.uniform(0.6, 0.9)
        
        # Seleccionar insumos aleatoriamente
        insumos_indices = list(range(self.num_insumos))
        random.shuffle(insumos_indices)
        
        for insumo_id in insumos_indices:
            if peso_restante <= 0:
                break
                
            if random.random() < 0.4:  # 40% probabilidad de incluir cada insumo
                peso_unitario = self.insumos_data[insumo_id]['peso_kg']
                if peso_unitario > 0 and peso_restante > peso_unitario:
                    max_cantidad = int(peso_restante / peso_unitario)
                    cantidad = random.randint(1, min(max_cantidad, 10))
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