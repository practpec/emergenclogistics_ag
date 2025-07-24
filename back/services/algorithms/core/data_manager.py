from typing import List, Dict, Any, Set
import json

class AlgorithmDataManager:
    """Gestor centralizado de datos para el algoritmo genético"""
    
    def __init__(self, scenario_data: Dict[str, Any]):
        self.scenario_data = scenario_data
        
        # Datos procesados
        self.vehiculos_disponibles = []
        self.insumos_data = []
        self.mapeo_asignaciones = []
        self.rutas_estado = {}
        self.tipo_desastre = ""
        self.desastre_info = None
        
        # Datos optimizados
        self.num_vehiculos = 0
        self.num_insumos = 0
        self.destinos_unicos = []
        self.destinos_a_asignaciones = {}
        self.categorias_map = {}
        
        self._process_scenario_data()
        self._load_static_data()
        self._build_optimization_maps()
    
    def _process_scenario_data(self):
        """Procesar datos del escenario de entrada"""
        self.vehiculos_disponibles = self.scenario_data['scenario_config']['vehiculos_disponibles']
        self.num_vehiculos = len(self.vehiculos_disponibles)
        
        self.tipo_desastre = self.scenario_data['scenario_config']['tipo_desastre']
        
        # Procesar mapeo de rutas desde map_data
        self.mapeo_asignaciones = self._create_route_mapping()
        
        # Procesar estado de rutas
        rutas_estado_list = self.scenario_data['scenario_config'].get('rutas_estado', [])
        self.rutas_estado = {f"ruta-{i}": r for i, r in enumerate(rutas_estado_list)}
    
    def _load_static_data(self):
        """Cargar datos estáticos desde archivos JSON"""
        try:
            # Cargar insumos
            with open("entities/data/categorias_insumos.json", 'r', encoding='utf-8') as f:
                self.insumos_data = json.load(f)
            self.num_insumos = len(self.insumos_data)
            
            # Cargar información de desastres
            with open("entities/data/desastres.json", 'r', encoding='utf-8') as f:
                tipos_desastre = json.load(f)
                self.desastre_info = next(
                    (d for d in tipos_desastre if d['tipo'] == self.tipo_desastre), 
                    None
                )
            
            # Crear mapa de categorías
            for insumo in self.insumos_data:
                categoria = insumo['categoria']
                if categoria not in self.categorias_map:
                    self.categorias_map[categoria] = []
                self.categorias_map[categoria].append(insumo['id_insumo'])
                
        except FileNotFoundError as e:
            raise Exception(f"Archivo de datos estáticos no encontrado: {e}")
    
    def _create_route_mapping(self) -> List[Dict[str, Any]]:
        """Crear mapeo optimizado de asignaciones destino-ruta"""
        mapeo = []
        asignacion_id = 0
        
        # Obtener datos desde map_data
        map_data = self.scenario_data['map_data']
        rutas_data = map_data['rutas_data']
        
        # Crear lista de destinos desde map_data
        destinos = []
        for destino_data in self.scenario_data['map_data']['rutas_data']:
            destino_clave = destino_data['destino']['clave_localidad']
            destinos.append(destino_clave)
        for destino_data in rutas_data:
            destino_info = destino_data['destino']
            destino_clave = destino_info['clave_localidad']
            
            for ruta_idx, ruta in enumerate(destino_data['rutas']):
                mapeo.append({
                    'id_asignacion_unica': asignacion_id,
                    'id_destino_perteneciente': destino_clave,
                    'id_ruta_en_destino': ruta_idx,
                    'distancia_km': ruta['distancia']['value'] / 1000,  # Convertir metros a km
                    'destino_nombre': destino_info['nombre'],
                    'poblacion': int(destino_info['poblacion'])
                })
                asignacion_id += 1
        
        return mapeo
    
    def _get_poblacion_destino(self, destino_clave: str) -> int:
        """Obtener población estimada para un destino"""
        poblaciones_base = {
            'clave_localidad1': 1200,
            'clave_localidad2': 800,
            'clave_localidad3': 1500,
            'clave_localidad4': 600
        }
        return poblaciones_base.get(destino_clave, 500)
    
    def _build_optimization_maps(self):
        """Construir mapas de optimización para consultas rápidas"""
        # Destinos únicos
        self.destinos_unicos = list(set(
            m['id_destino_perteneciente'] for m in self.mapeo_asignaciones
        ))
        
        # Mapeo destinos a asignaciones
        for mapeo in self.mapeo_asignaciones:
            destino_id = mapeo['id_destino_perteneciente']
            if destino_id not in self.destinos_a_asignaciones:
                self.destinos_a_asignaciones[destino_id] = []
            self.destinos_a_asignaciones[destino_id].append(mapeo)
    
    def get_insumos_prioritarios(self) -> List[int]:
        """Obtener IDs de insumos prioritarios según el desastre"""
        if not self.desastre_info or 'prioridades' not in self.desastre_info:
            return list(range(min(8, self.num_insumos)))
        
        insumos_prioritarios = []
        for prioridad in self.desastre_info['prioridades']:
            if prioridad['nivel'] in ['alta', 'media']:
                categoria = prioridad['categoria']
                if categoria in self.categorias_map:
                    insumos_prioritarios.extend(self.categorias_map[categoria])
        
        return insumos_prioritarios[:15]
    
    def get_peso_insumo(self, insumo_id: int) -> float:
        """Obtener peso de un insumo específico"""
        if 0 <= insumo_id < len(self.insumos_data):
            return self.insumos_data[insumo_id]['peso_kg']
        return 0.0
    
    def get_capacidad_vehiculo(self, vehiculo_id: int) -> float:
        """Obtener capacidad de un vehículo específico"""
        if 0 <= vehiculo_id < len(self.vehiculos_disponibles):
            return self.vehiculos_disponibles[vehiculo_id]['capacidad_kg']
        return 1000.0
    
    def get_destinos_disponibles_para_vehiculo(self, vehiculo_id: int) -> List[Dict]:
        """Obtener destinos disponibles para un vehículo específico"""
        if vehiculo_id >= len(self.vehiculos_disponibles):
            return []
        
        vehiculo_info = self.vehiculos_disponibles[vehiculo_id]
        destinos_compatibles = []
        
        for destino_id in self.destinos_unicos:
            asignaciones_destino = self.destinos_a_asignaciones[destino_id]
            
            for asignacion in asignaciones_destino:
                ruta_id = f"{destino_id}-ruta-{asignacion['id_ruta_en_destino']}"
                estado_ruta = self.rutas_estado.get(ruta_id, {
                    'estado': 'abierta',
                    'vehiculos_permitidos': [vehiculo_info['tipo']]
                })
                
                if (estado_ruta['estado'] == 'abierta' and 
                    vehiculo_info['tipo'] in estado_ruta['vehiculos_permitidos']):
                    destinos_compatibles.append(asignacion)
                    break
        
        return destinos_compatibles
    
    def validate_assignment(self, vehiculo_id: int, destino_ruta_id: int, insumos: List[int]) -> bool:
        """Validar si una asignación es técnicamente válida"""
        if vehiculo_id >= len(self.vehiculos_disponibles) or destino_ruta_id >= len(self.mapeo_asignaciones):
            return False
        
        vehiculo = self.vehiculos_disponibles[vehiculo_id]
        mapeo_info = self.mapeo_asignaciones[destino_ruta_id]
        
        # Verificar peso
        peso_total = sum(insumos[i] * self.get_peso_insumo(i) for i in range(len(insumos)))
        if peso_total > vehiculo['capacidad_kg'] * 1.05:
            return False
        
        # Verificar compatibilidad de ruta
        destino_id = mapeo_info['id_destino_perteneciente']
        ruta_id = f"{destino_id}-ruta-{mapeo_info['id_ruta_en_destino']}"
        estado_ruta = self.rutas_estado.get(ruta_id, {
            'estado': 'abierta',
            'vehiculos_permitidos': [vehiculo['tipo']]
        })
        
        return (estado_ruta['estado'] == 'abierta' and 
                vehiculo['tipo'] in estado_ruta['vehiculos_permitidos'])
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas resumidas de los datos"""
        return {
            'num_vehiculos': self.num_vehiculos,
            'num_insumos': self.num_insumos,
            'num_destinos_unicos': len(self.destinos_unicos),
            'num_asignaciones_posibles': len(self.mapeo_asignaciones),
            'tipo_desastre': self.tipo_desastre,
            'categorias_insumos': list(self.categorias_map.keys())
        }