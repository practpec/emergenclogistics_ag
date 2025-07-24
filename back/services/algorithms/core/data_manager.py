from typing import List, Dict, Any, Set
from services.data.static_data_service import StaticDataService

class AlgorithmDataManager:
    """Gestor centralizado de datos para el algoritmo genético"""
    
    def __init__(self, scenario_data: Dict[str, Any]):
        self.static_data_service = StaticDataService()
        
        # Datos del escenario
        self.map_data = scenario_data['map_data']
        self.scenario_config = scenario_data['scenario_config']
        
        # Datos estáticos
        self.vehiculos_disponibles = None
        self.insumos_data = None
        self.tipos_desastre = None
        self.mapeo_asignaciones = None
        self.rutas_estado = None
        self.desastre_info = None
        
        # Datos procesados
        self.num_vehiculos = 0
        self.num_insumos = 0
        self.categorias_map = {}
        self.destinos_unicos = []
        self.destinos_a_asignaciones = {}
        
        self._load_all_data()
        
    def _load_all_data(self):
        """Cargar todos los datos necesarios"""
        self._load_static_data()
        self._process_scenario_data()
        self._build_lookup_maps()
    
    def _load_static_data(self):
        """Cargar datos estáticos desde archivos JSON"""
        import json
        
        # Cargar insumos
        with open("entities/data/categorias_insumos.json", 'r', encoding='utf-8') as f:
            self.insumos_data = json.load(f)
        
        self.num_insumos = len(self.insumos_data)
        self.tipos_desastre = self.static_data_service.get_all_disasters()
        
        # Crear mapa de categorías
        for insumo in self.insumos_data:
            categoria = insumo['categoria']
            if categoria not in self.categorias_map:
                self.categorias_map[categoria] = []
            self.categorias_map[categoria].append(insumo['id_insumo'])
    
    def _process_scenario_data(self):
        """Procesar datos del escenario"""
        self.vehiculos_disponibles = self.scenario_config['vehiculos_disponibles']
        self.num_vehiculos = len(self.vehiculos_disponibles)
        
        self.tipo_desastre = self.scenario_config['tipo_desastre']
        self.desastre_info = next(
            (d for d in self.tipos_desastre if d.tipo == self.tipo_desastre), 
            None
        )
        
        self.mapeo_asignaciones = self._create_route_mapping()
        self.rutas_estado = {r['ruta_id']: r for r in self.scenario_config['rutas_estado']}
    
    def _build_lookup_maps(self):
        """Construir mapas de búsqueda para optimizar consultas"""
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
    
    def _create_route_mapping(self) -> List[Dict[str, Any]]:
        """Crear mapeo de asignaciones destino-ruta"""
        mapeo = []
        asignacion_id = 0
        
        for destino_data in self.map_data['rutas_data']:
            destino_info = destino_data['destino']
            destino_id = destino_info.get('clave_localidad', destino_data['indice'])
            
            for ruta_idx, ruta in enumerate(destino_data['rutas']):
                mapeo.append({
                    'id_asignacion_unica': asignacion_id,
                    'id_destino_perteneciente': destino_id,
                    'id_ruta_en_destino': ruta_idx,
                    'distancia_km': ruta['distancia']['value'] / 1000,
                    'destino_nombre': destino_info.get('nombre_localidad', f"Destino_{destino_id}"),
                    'poblacion': destino_info.get('poblacion', 100)
                })
                asignacion_id += 1
        
        return mapeo
    
    def get_insumos_prioritarios(self) -> List[int]:
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
    
    def get_peso_insumo(self, insumo_id: int) -> float:
        """Obtener peso de un insumo específico"""
        return self.insumos_data[insumo_id]['peso_kg']
    
    def get_capacidad_vehiculo(self, vehiculo_id: int) -> float:
        """Obtener capacidad de un vehículo específico"""
        return self.vehiculos_disponibles[vehiculo_id]['capacidad_kg']
    
    def get_destinos_disponibles_para_vehiculo(self, vehiculo_id: int) -> List[Dict]:
        """Obtener destinos disponibles para un vehículo específico"""
        vehiculo_info = self.vehiculos_disponibles[vehiculo_id]
        destinos_compatibles = []
        
        for destino_id in self.destinos_unicos:
            asignaciones_destino = self.destinos_a_asignaciones[destino_id]
            
            for asignacion in asignaciones_destino:
                ruta_id = f"Destino{destino_id}-Ruta{asignacion['id_ruta_en_destino'] + 1}"
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
        vehiculo = self.vehiculos_disponibles[vehiculo_id]
        mapeo_info = self.mapeo_asignaciones[destino_ruta_id]
        
        # Verificar peso
        peso_total = sum(insumos[i] * self.insumos_data[i]['peso_kg'] 
                        for i in range(len(insumos)))
        if peso_total > vehiculo['capacidad_kg'] * 1.1:
            return False
        
        # Verificar ruta
        destino_id = mapeo_info['id_destino_perteneciente']
        ruta_id = f"Destino{destino_id}-Ruta{mapeo_info['id_ruta_en_destino'] + 1}"
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