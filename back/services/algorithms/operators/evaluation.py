# algorithms/evaluation.py
from typing import List, Dict, Any
from ..models import Individual

class FitnessEvaluator:
    """Evaluador de fitness mejorado con penalizaciones más estrictas"""
    
    def __init__(self, vehiculos_disponibles: List[Dict], mapeo_asignaciones: List[Dict],
                 insumos_data: List[Dict], rutas_estado: Dict, desastre_info: Any = None):
        self.vehiculos_disponibles = vehiculos_disponibles
        self.mapeo_asignaciones = mapeo_asignaciones
        self.insumos_data = insumos_data
        self.rutas_estado = rutas_estado
        self.desastre_info = desastre_info
        self.num_insumos = len(insumos_data)

    def evaluar_fitness(self, individuo: Individual) -> float:
        """Evaluar fitness con penalizaciones mejoradas para evitar duplicados"""
        fitness_total = 0.0
        peso_total_utilizado = 0.0
        combustible_total = 0.0
        localidades_atendidas = set()
        penalizaciones = 0.0
        
        # Análisis de destinos asignados
        destinos_asignados = {}  # {destino_id: [vehiculo_indices]}
        asignaciones_validas = []
        
        # Primera pasada: analizar asignaciones y detectar duplicados
        for i, asignacion in enumerate(individuo.vehiculos):
            vehiculo = self.vehiculos_disponibles[asignacion.vehiculo_id]
            mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
            destino_id = mapeo_info['id_destino_perteneciente']
            
            # Registrar destino asignado
            if destino_id not in destinos_asignados:
                destinos_asignados[destino_id] = []
            destinos_asignados[destino_id].append(i)
            
            # Verificar validez de la asignación
            es_valida = self._validar_asignacion(vehiculo, mapeo_info, asignacion.insumos)
            asignaciones_validas.append(es_valida)
        
        # Penalizar destinos duplicados FUERTEMENTE
        for destino_id, vehiculos_indices in destinos_asignados.items():
            if len(vehiculos_indices) > 1:
                # Penalización masiva por duplicación
                penalizaciones += len(vehiculos_indices) * 2000
                
                # Solo el primer vehículo asignado al destino es válido
                for i, vehiculo_idx in enumerate(vehiculos_indices):
                    if i > 0:  # Todos excepto el primero son inválidos
                        asignaciones_validas[vehiculo_idx] = False
        
        # Segunda pasada: calcular fitness solo para asignaciones válidas
        for i, asignacion in enumerate(individuo.vehiculos):
            if not asignaciones_validas[i]:
                continue  # Saltar asignaciones inválidas
                
            vehiculo = self.vehiculos_disponibles[asignacion.vehiculo_id]
            mapeo_info = self.mapeo_asignaciones[asignacion.id_destino_ruta]
            
            # Calcular peso de insumos
            peso_insumos = sum(
                asignacion.insumos[j] * self.insumos_data[j]['peso_kg']
                for j in range(self.num_insumos)
            )
            
            # Penalización MASIVA por sobrecarga - esto NO debe pasar
            if peso_insumos > vehiculo['capacidad_kg']:
                exceso = peso_insumos - vehiculo['capacidad_kg']
                penalizaciones += exceso * 1000  # Penalización masiva
                penalizaciones += 5000  # Penalización adicional por violar restricción
                # NO limitar el peso aquí - debe ser penalizado fuertemente
                continue  # Saltar esta asignación completamente
            
            # Verificar compatibilidad de ruta
            destino_id = mapeo_info['id_destino_perteneciente']
            ruta_id = f"Destino{destino_id}-Ruta{mapeo_info['id_ruta_en_destino'] + 1}"
            estado_ruta = self.rutas_estado.get(ruta_id, {
                'estado': 'abierta', 
                'vehiculos_permitidos': [vehiculo['tipo']]
            })
            
            if estado_ruta['estado'] == 'cerrada' or vehiculo['tipo'] not in estado_ruta['vehiculos_permitidos']:
                penalizaciones += 1500  # Penalización por ruta inválida
                continue
            
            # Calcular combustible
            distancia_km = mapeo_info['distancia_km']
            combustible = distancia_km * vehiculo['consumo_litros_km']
            combustible_total += combustible
            
            # Evaluar relevancia de insumos (MEJORADO)
            relevancia_insumos = self._evaluar_relevancia_insumos_mejorada(asignacion.insumos)
            
            # Evaluar eficiencia poblacional (MEJORADO)
            poblacion_destino = mapeo_info['poblacion']
            eficiencia_poblacional = self._evaluar_eficiencia_poblacional_mejorada(
                peso_insumos, poblacion_destino, vehiculo
            )
            
            # Bonificar utilización alta de capacidad
            utilizacion_capacidad = peso_insumos / vehiculo['capacidad_kg']
            bonificacion_capacidad = 0
            if utilizacion_capacidad >= 0.9:
                bonificacion_capacidad = 200  # Bonificación por uso > 90%
            elif utilizacion_capacidad >= 0.7:
                bonificacion_capacidad = 100  # Bonificación por uso > 70%
            elif utilizacion_capacidad >= 0.5:
                bonificacion_capacidad = 50   # Bonificación por uso > 50%
            
            # Contribución positiva al fitness
            fitness_total += relevancia_insumos * 15      # Aumentado
            fitness_total += eficiencia_poblacional * 12  # Aumentado
            fitness_total += bonificacion_capacidad       # Nuevo
            fitness_total += peso_insumos * 0.8           # Aumentado
            
            peso_total_utilizado += peso_insumos
            localidades_atendidas.add(destino_id)
        
        # Bonificaciones globales mejoradas
        num_destinos_unicos = len(set(
            self.mapeo_asignaciones[asig.id_destino_ruta]['id_destino_perteneciente']
            for asig in individuo.vehiculos
        ))
        max_destinos_posibles = len(set(
            m['id_destino_perteneciente'] for m in self.mapeo_asignaciones
        ))
        
        # Bonificación por cobertura de destinos únicos
        cobertura_destinos = len(localidades_atendidas) / max_destinos_posibles
        fitness_total += cobertura_destinos * 300  # Aumentado significativamente
        
        # Bonificación extra por cobertura completa
        if len(localidades_atendidas) == max_destinos_posibles:
            fitness_total += 500  # Bonificación por cobertura total
        
        # Penalizaciones de eficiencia
        fitness_total -= combustible_total * 0.3  # Reducido para no penalizar tanto
        
        # Penalizar subutilización grave
        if peso_total_utilizado > 0:
            utilizacion_promedio = peso_total_utilizado / sum(v['capacidad_kg'] for v in self.vehiculos_disponibles)
            if utilizacion_promedio < 0.3:
                penalizaciones += 400  # Penalización por muy baja utilización
            elif utilizacion_promedio < 0.5:
                penalizaciones += 200  # Penalización moderada
        
        # Penalizar vehículos sin carga
        vehiculos_sin_carga = sum(1 for asig in individuo.vehiculos 
                                if sum(asig.insumos) == 0)
        penalizaciones += vehiculos_sin_carga * 300
        
        # Aplicar penalizaciones
        fitness_total -= penalizaciones
        
        # Asegurar fitness no negativo
        individuo.fitness = max(0, fitness_total)
        return individuo.fitness

    def _validar_asignacion(self, vehiculo: Dict, mapeo_info: Dict, insumos: List[int]) -> bool:
        """Validar si una asignación es técnicamente válida"""
        # Verificar peso
        peso_total = sum(insumos[i] * self.insumos_data[i]['peso_kg'] 
                        for i in range(len(insumos)))
        if peso_total > vehiculo['capacidad_kg'] * 1.1:  # Permitir 10% de tolerancia
            return False
        
        # Verificar ruta
        destino_id = mapeo_info['id_destino_perteneciente']
        ruta_id = f"Destino{destino_id}-Ruta{mapeo_info['id_ruta_en_destino'] + 1}"
        estado_ruta = self.rutas_estado.get(ruta_id, {
            'estado': 'abierta', 
            'vehiculos_permitidos': [vehiculo['tipo']]
        })
        
        if estado_ruta['estado'] == 'cerrada':
            return False
        if vehiculo['tipo'] not in estado_ruta['vehiculos_permitidos']:
            return False
        
        return True

    def _evaluar_relevancia_insumos_mejorada(self, insumos: List[int]) -> float:
        """Evaluar relevancia de insumos con mejor distribución"""
        if not self.desastre_info:
            return sum(insumos) * 1.0
        
        relevancia_total = 0.0
        peso_total_insumos = 0.0
        
        for i, cantidad in enumerate(insumos):
            if cantidad > 0:
                insumo_info = self.insumos_data[i]
                categoria = insumo_info['categoria']
                prioridad = self.desastre_info.get_priority_weight(categoria)
                peso_insumo = cantidad * insumo_info['peso_kg']
                
                # Calcular relevancia ponderada
                relevancia_item = cantidad * prioridad * 2.0  # Factor aumentado
                relevancia_total += relevancia_item
                peso_total_insumos += peso_insumo
        
        # Bonificar diversidad de categorías
        categorias_presentes = set()
        for i, cantidad in enumerate(insumos):
            if cantidad > 0:
                categoria = self.insumos_data[i]['categoria']
                categorias_presentes.add(categoria)
        
        bonificacion_diversidad = len(categorias_presentes) * 20
        
        return relevancia_total + bonificacion_diversidad

    def _evaluar_eficiencia_poblacional_mejorada(self, peso_insumos: float, poblacion: int, vehiculo: Dict) -> float:
        """Evaluar eficiencia con criterios mejorados"""
        if peso_insumos == 0:
            return -100  # Penalizar vehículos vacíos
        
        capacidad_vehiculo = vehiculo['capacidad_kg']
        utilizacion = peso_insumos / capacidad_vehiculo
        
        # Score base proporcional al peso y población
        eficiencia_score = (peso_insumos / 100) * (poblacion / 1000)
        
        # Bonificaciones por buena utilización
        if utilizacion >= 0.9:
            eficiencia_score += 150  # Excelente utilización
        elif utilizacion >= 0.7:
            eficiencia_score += 100  # Buena utilización
        elif utilizacion >= 0.5:
            eficiencia_score += 50   # Utilización aceptable
        else:
            eficiencia_score -= 50   # Penalizar baja utilización
        
        # Ajustar por tamaño de población vs capacidad del vehículo
        ratio_poblacion_capacidad = poblacion / capacidad_vehiculo
        
        if poblacion < 100:  # Población muy pequeña
            if capacidad_vehiculo < 1500:  # Vehículo pequeño
                eficiencia_score += 80  # Buena coincidencia
            else:  # Vehículo grande para población pequeña
                eficiencia_score -= 60  # Ineficiente
                
        elif poblacion > 1000:  # Población grande
            if capacidad_vehiculo > 2000:  # Vehículo grande
                eficiencia_score += 100  # Excelente coincidencia
            elif capacidad_vehiculo < 1500:  # Vehículo pequeño para población grande
                eficiencia_score -= 80  # Muy ineficiente
        
        # Bonificar ratio óptimo de kg por persona
        kg_per_persona = peso_insumos / max(poblacion, 1)
        if 0.5 <= kg_per_persona <= 2.0:  # Rango óptimo
            eficiencia_score += 50
        elif kg_per_persona < 0.2:  # Muy poco por persona
            eficiencia_score -= 30
        elif kg_per_persona > 5.0:  # Demasiado por persona
            eficiencia_score -= 20
        
        return eficiencia_score