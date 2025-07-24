import random
from typing import List, Dict
from ..models import Individual, VehicleAssignment

class PopulationInitializer:
    """Inicializador optimizado de población"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        
    def inicializar_poblacion(self, poblacion_size: int) -> List[Individual]:
        """Generar población inicial con estrategias diversificadas"""
        poblacion = []
        
        # 50% - Asignación por capacidad (sin duplicados)
        num_capacidad = int(poblacion_size * 0.5)
        for _ in range(num_capacidad):
            individuo = self._generar_por_capacidad()
            poblacion.append(individuo)
        
        # 30% - Asignación por población de destinos
        num_poblacion = int(poblacion_size * 0.3)
        for _ in range(num_poblacion):
            individuo = self._generar_por_poblacion()
            poblacion.append(individuo)
        
        # 20% - Completamente aleatoria pero válida
        num_restante = poblacion_size - len(poblacion)
        for _ in range(num_restante):
            individuo = self._generar_aleatoria_valida()
            poblacion.append(individuo)
        
        return poblacion

    def _generar_por_capacidad(self) -> Individual:
        """Generar individuo asignando por capacidad sin duplicar destinos"""
        vehiculos_asignados = []
        destinos_usados = set()
        
        # Ordenar vehículos por capacidad
        vehiculos_ordenados = sorted(
            enumerate(self.data_manager.vehiculos_disponibles), 
            key=lambda x: x[1]['capacidad_kg'], 
            reverse=True
        )
        
        for vehiculo_idx, vehiculo_info in vehiculos_ordenados:
            # Buscar destino disponible
            destinos_compatibles = self.data_manager.get_destinos_disponibles_para_vehiculo(vehiculo_idx)
            
            destino_elegido = None
            for destino_info in destinos_compatibles:
                destino_id = destino_info['id_destino_perteneciente']
                if destino_id not in destinos_usados:
                    destino_elegido = destino_info
                    destinos_usados.add(destino_id)
                    break
            
            # Fallback si no encuentra destino único
            if destino_elegido is None and destinos_compatibles:
                destino_elegido = random.choice(destinos_compatibles)
            
            # Generar insumos respetando capacidad
            if destino_elegido:
                insumos = self._generar_insumos_por_capacidad(vehiculo_info['capacidad_kg'])
                
                vehiculos_asignados.append(VehicleAssignment(
                    vehiculo_id=vehiculo_idx,
                    id_destino_ruta=destino_elegido['id_asignacion_unica'],
                    insumos=insumos
                ))
        
        return Individual(vehiculos=vehiculos_asignados)

    def _generar_por_poblacion(self) -> Individual:
        """Generar individuo priorizando destinos por población"""
        vehiculos_asignados = []
        destinos_usados = set()
        
        # Ordenar destinos por población
        destinos_por_poblacion = sorted(
            self.data_manager.destinos_unicos,
            key=lambda dest_id: self._get_poblacion_maxima_destino(dest_id),
            reverse=True
        )
        
        vehiculos_mezclados = list(enumerate(self.data_manager.vehiculos_disponibles))
        random.shuffle(vehiculos_mezclados)
        
        for vehiculo_idx, vehiculo_info in vehiculos_mezclados:
            destino_elegido = None
            
            # Priorizar destinos de alta población
            for destino_id in destinos_por_poblacion:
                if destino_id not in destinos_usados:
                    asignaciones_destino = self.data_manager.destinos_a_asignaciones[destino_id]
                    asignacion_valida = self._encontrar_asignacion_valida(vehiculo_info, asignaciones_destino)
                    
                    if asignacion_valida:
                        destino_elegido = asignacion_valida
                        destinos_usados.add(destino_id)
                        break
            
            # Fallback
            if destino_elegido is None:
                destinos_compatibles = self.data_manager.get_destinos_disponibles_para_vehiculo(vehiculo_idx)
                if destinos_compatibles:
                    destino_elegido = random.choice(destinos_compatibles)
            
            # Generar insumos apropiados
            if destino_elegido:
                poblacion_destino = destino_elegido.get('poblacion', 500)
                insumos = self._generar_insumos_por_poblacion(
                    vehiculo_info['capacidad_kg'], poblacion_destino
                )
                
                vehiculos_asignados.append(VehicleAssignment(
                    vehiculo_id=vehiculo_idx,
                    id_destino_ruta=destino_elegido['id_asignacion_unica'],
                    insumos=insumos
                ))
        
        return Individual(vehiculos=vehiculos_asignados)

    def _generar_aleatoria_valida(self) -> Individual:
        """Generar individuo aleatorio pero válido"""
        vehiculos_asignados = []
        destinos_usados = set()
        
        vehiculos_indices = list(range(self.data_manager.num_vehiculos))
        random.shuffle(vehiculos_indices)
        
        for vehiculo_idx in vehiculos_indices:
            vehiculo_info = self.data_manager.vehiculos_disponibles[vehiculo_idx]
            
            # Intentar asignar destino único
            destino_elegido = None
            intentos = 0
            
            while intentos < 8 and destino_elegido is None:
                candidato = random.choice(self.data_manager.mapeo_asignaciones)
                destino_id = candidato['id_destino_perteneciente']
                
                if destino_id not in destinos_usados:
                    destino_elegido = candidato
                    destinos_usados.add(destino_id)
                    break
                
                intentos += 1
            
            # Si no encuentra destino único, usar cualquiera
            if destino_elegido is None:
                destino_elegido = random.choice(self.data_manager.mapeo_asignaciones)
            
            # Generar insumos aleatorios válidos
            insumos = self._generar_insumos_aleatorios(vehiculo_info['capacidad_kg'])
            
            vehiculos_asignados.append(VehicleAssignment(
                vehiculo_id=vehiculo_idx,
                id_destino_ruta=destino_elegido['id_asignacion_unica'],
                insumos=insumos
            ))
        
        return Individual(vehiculos=vehiculos_asignados)

    def _get_poblacion_maxima_destino(self, destino_id: str) -> int:
        """Obtener población máxima de un destino"""
        asignaciones_destino = self.data_manager.destinos_a_asignaciones.get(destino_id, [])
        if asignaciones_destino:
            return max(a['poblacion'] for a in asignaciones_destino)
        return 0

    def _encontrar_asignacion_valida(self, vehiculo_info: Dict, asignaciones_destino: List[Dict]) -> Dict:
        """Encontrar asignación válida para el vehículo"""
        asignaciones_compatibles = []
        
        for asignacion in asignaciones_destino:
            destino_id = asignacion['id_destino_perteneciente']
            ruta_id = f"{destino_id}-ruta-{asignacion['id_ruta_en_destino']}"
            
            estado_ruta = self.data_manager.rutas_estado.get(ruta_id, {
                'estado': 'abierta',
                'vehiculos_permitidos': [vehiculo_info['tipo']]
            })
            
            if (estado_ruta['estado'] == 'abierta' and 
                vehiculo_info['tipo'] in estado_ruta['vehiculos_permitidos']):
                asignaciones_compatibles.append(asignacion)
        
        return random.choice(asignaciones_compatibles) if asignaciones_compatibles else None

    def _generar_insumos_por_capacidad(self, capacidad_kg: float) -> List[int]:
        """Generar insumos respetando capacidad estrictamente"""
        insumos = [0] * self.data_manager.num_insumos
        peso_maximo = capacidad_kg * 0.90
        peso_restante = peso_maximo
        
        insumos_prioritarios = self.data_manager.get_insumos_prioritarios()
        
        # Llenar con insumos prioritarios
        for insumo_id in random.sample(insumos_prioritarios, min(len(insumos_prioritarios), 8)):
            if peso_restante <= 0:
                break
                
            peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
            if peso_unitario > 0 and peso_restante >= peso_unitario:
                max_cantidad = int(peso_restante / peso_unitario)
                cantidad = random.randint(1, min(max_cantidad, 10))
                
                peso_asignado = cantidad * peso_unitario
                if peso_asignado <= peso_restante:
                    insumos[insumo_id] = cantidad
                    peso_restante -= peso_asignado
        
        # Completar con otros insumos
        otros_insumos = [i for i in range(self.data_manager.num_insumos) 
                        if i not in insumos_prioritarios]
        
        for insumo_id in random.sample(otros_insumos, min(len(otros_insumos), 5)):
            if peso_restante <= 0:
                break
                
            peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
            if peso_unitario > 0 and peso_restante >= peso_unitario:
                max_cantidad = int(peso_restante / peso_unitario)
                cantidad = random.randint(1, min(max_cantidad, 5))
                
                peso_asignado = cantidad * peso_unitario
                if peso_asignado <= peso_restante:
                    insumos[insumo_id] = cantidad
                    peso_restante -= peso_asignado
        
        return insumos

    def _generar_insumos_por_poblacion(self, capacidad_kg: float, poblacion: int) -> List[int]:
        """Generar insumos apropiados para población"""
        insumos = [0] * self.data_manager.num_insumos
        
        factor_poblacion = min(poblacion / 400, 2.0)
        peso_objetivo = capacidad_kg * random.uniform(0.75, 0.92) * factor_poblacion
        peso_objetivo = min(peso_objetivo, capacidad_kg * 0.95)
        
        peso_restante = peso_objetivo
        insumos_prioritarios = self.data_manager.get_insumos_prioritarios()
        
        for insumo_id in insumos_prioritarios:
            if peso_restante <= 0:
                break
                
            peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
            if peso_unitario > 0 and peso_restante > peso_unitario:
                base_cantidad = max(1, int(poblacion / 120))
                max_cantidad = min(int(peso_restante / peso_unitario), base_cantidad * 2)
                
                if max_cantidad > 0:
                    cantidad = random.randint(1, max_cantidad)
                    insumos[insumo_id] = cantidad
                    peso_restante -= cantidad * peso_unitario
        
        return insumos

    def _generar_insumos_aleatorios(self, capacidad_kg: float) -> List[int]:
        """Generar insumos aleatorios respetando capacidad"""
        insumos = [0] * self.data_manager.num_insumos
        peso_restante = capacidad_kg * random.uniform(0.6, 0.85)
        
        insumos_indices = list(range(self.data_manager.num_insumos))
        random.shuffle(insumos_indices)
        
        for insumo_id in insumos_indices:
            if peso_restante <= 0:
                break
                
            if random.random() < 0.4:
                peso_unitario = self.data_manager.get_peso_insumo(insumo_id)
                if peso_unitario > 0 and peso_restante > peso_unitario:
                    max_cantidad = int(peso_restante / peso_unitario)
                    cantidad = random.randint(1, min(max_cantidad, 8))
                    insumos[insumo_id] = cantidad
                    peso_restante -= cantidad * peso_unitario
        
        return insumos