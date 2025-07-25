from typing import List, Dict, Any, Set
from services.data.data_loader import data_loader
from services.data.database_service import DatabaseService

class AlgorithmDataManager:
    """Gestor centralizado de datos para el algoritmo genético"""
    
    def __init__(self, scenario_data: Dict[str, Any]):
        self.scenario_data = scenario_data
        self.db_service = DatabaseService()
        
        self.vehiculos_disponibles = []
        self.mapeo_asignaciones = []
        self.tipo_desastre = ""
        self.desastre_info = None
        
        self.num_vehiculos = 0
        self.num_insumos = 0
        self.destinos_unicos = []
        self.destinos_a_asignaciones = {}
        self.categorias_map = {}
        self.insumos_data = []
        
        self._process_scenario_data()
        self._load_static_data()
        self._build_optimization_maps()
    
    def _process_scenario_data(self):
        """Procesar datos del escenario según nueva estructura"""
        vehiculos_raw = self.scenario_data['scenario_config']['vehiculos_disponibles']
        
        self.vehiculos_disponibles = []
        for vehiculo in vehiculos_raw:
            vehiculo_procesado = vehiculo.copy()
            
            if 'capacidad_kg' not in vehiculo_procesado:
                if 'maximo_peso_ton' in vehiculo_procesado:
                    vehiculo_procesado['capacidad_kg'] = vehiculo_procesado['maximo_peso_ton'] * 1000
                else:
                    vehiculo_procesado['capacidad_kg'] = 1000.0
            
            self.vehiculos_disponibles.append(vehiculo_procesado)
        
        self.num_vehiculos = len(self.vehiculos_disponibles)
        self.tipo_desastre = self.scenario_data['scenario_config']['tipo_desastre']
        
        self.mapeo_asignaciones = self._create_route_mapping()
    
    def _create_route_mapping(self) -> List[Dict[str, Any]]:
        """Crear mapeo de asignaciones según nueva estructura del JSON"""
        mapeo = []
        asignacion_id = 0
        
        map_data = self.scenario_data['map_data']
        
        # Verificar si hay datos reales de localidades
        if 'nodos_secundarios' in map_data and map_data.get('nodos_secundarios'):
            # Usar datos reales de la BD
            mapeo = self._create_mapping_from_real_data(map_data)
        else:
            # Usar estructura simplificada del JSON
            rutas_data = map_data.get('rutas_data', [])
            for ruta_info in rutas_data:
                destino_clave = ruta_info.get('claves_localiada_destinos', f'LOC{asignacion_id:03d}')
                
                mapeo.append({
                    'id_asignacion_unica': asignacion_id,
                    'id_destino_perteneciente': destino_clave,
                    'id_ruta_en_destino': ruta_info.get('id_ruta', asignacion_id),
                    'distancia_km': ruta_info.get('distancia_km', 10),
                    'destino_nombre': f'Destino {destino_clave}',
                    'poblacion': self._estimate_population_from_distance(ruta_info.get('distancia_km', 10)),
                    'estado': ruta_info.get('estado', 'abierta'),
                    'vehiculos_permitidos': ruta_info.get('vehiculos_permitidos', ['camioneta', 'van'])
                })
                asignacion_id += 1
        
        return mapeo
    
    def _create_mapping_from_real_data(self, map_data: Dict) -> List[Dict[str, Any]]:
        """Crear mapeo usando datos reales de localidades de la BD"""
        mapeo = []
        asignacion_id = 0
        
        nodos_secundarios = map_data['nodos_secundarios']
        rutas_data = map_data.get('rutas_data', [])
        
        for i, nodo in enumerate(nodos_secundarios):
            ruta_info = {}
            if i < len(rutas_data):
                ruta_info = rutas_data[i]
            
            mapeo.append({
                'id_asignacion_unica': asignacion_id,
                'id_destino_perteneciente': nodo['clave_localidad'],
                'id_ruta_en_destino': i,
                'distancia_km': nodo.get('distancia_directa', ruta_info.get('distancia_km', 10)),
                'destino_nombre': nodo['nombre'],
                'poblacion': int(nodo.get('poblacion', 500)),
                'estado': ruta_info.get('estado', 'abierta'),
                'vehiculos_permitidos': ruta_info.get('vehiculos_permitidos', ['camioneta', 'van']),
                'coordenadas': {
                    'lat': nodo.get('lat'),
                    'lng': nodo.get('lng')
                },
                'clave_estado': nodo.get('clave_estado'),
                'clave_municipio': nodo.get('clave_municipio')
            })
            asignacion_id += 1
        
        return mapeo
    
    def _estimate_population_from_distance(self, distancia_km: float) -> int:
        """Estimar población basada en distancia"""
        if distancia_km <= 10:
            return 800
        elif distancia_km <= 15:
            return 600
        elif distancia_km <= 20:
            return 400
        else:
            return 200
    
    def _load_static_data(self):
        """Cargar datos estáticos usando servicios especializados"""
        try:
            self.insumos_data = data_loader.get_categorias_insumos()
            self.num_insumos = len(self.insumos_data)
            
            self.desastre_info = data_loader.get_desastre_by_tipo(self.tipo_desastre)
            
            for insumo in self.insumos_data:
                categoria = insumo['categoria']
                if categoria not in self.categorias_map:
                    self.categorias_map[categoria] = []
                self.categorias_map[categoria].append(insumo['id_insumo'])
                
        except Exception as e:
            raise Exception(f"Error cargando datos estáticos: {e}")
    
    def _build_optimization_maps(self):
        """Construir mapas de optimización para consultas rápidas"""
        self.destinos_unicos = list(set(
            m['id_destino_perteneciente'] for m in self.mapeo_asignaciones
        ))
        
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
        
        for asignacion in self.mapeo_asignaciones:
            vehiculos_permitidos = asignacion.get('vehiculos_permitidos', [])
            estado_ruta = asignacion.get('estado', 'abierta')
            
            if (estado_ruta == 'abierta' and 
                vehiculo_info.get('tipo', 'camioneta') in vehiculos_permitidos):
                destinos_compatibles.append(asignacion)
        
        return destinos_compatibles
    
    def validate_assignment(self, vehiculo_id: int, destino_ruta_id: int, insumos: List[int]) -> bool:
        """Validar si una asignación es técnicamente válida"""
        if vehiculo_id >= len(self.vehiculos_disponibles) or destino_ruta_id >= len(self.mapeo_asignaciones):
            return False
        
        vehiculo = self.vehiculos_disponibles[vehiculo_id]
        mapeo_info = self.mapeo_asignaciones[destino_ruta_id]
        
        peso_total = sum(insumos[i] * self.get_peso_insumo(i) for i in range(len(insumos)))
        if peso_total > vehiculo['capacidad_kg'] * 1.05:
            return False
        
        vehiculos_permitidos = mapeo_info.get('vehiculos_permitidos', [])
        estado_ruta = mapeo_info.get('estado', 'abierta')
        
    def get_localidad_info_by_clave(self, clave_localidad: str, clave_estado: str = None, clave_municipio: str = None) -> Dict:
        """Obtener información completa de localidad usando DatabaseService"""
        try:
            if clave_estado and clave_municipio:
                # Usar DatabaseService para obtener datos completos
                nodo = self.db_service.get_nodo_inicial_municipio(clave_estado, clave_municipio)
                if nodo and nodo['clave_localidad'] == clave_localidad:
                    return nodo
            
            # Fallback: buscar en mapeo existente
            for mapeo in self.mapeo_asignaciones:
                if mapeo['id_destino_perteneciente'] == clave_localidad:
                    return {
                        'clave_localidad': clave_localidad,
                        'nombre': mapeo['destino_nombre'],
                        'poblacion': mapeo['poblacion'],
                        'coordenadas': mapeo.get('coordenadas', {})
                    }
            
            return {}
        except Exception:
            return {}
    
    def get_localidades_by_municipio(self, clave_estado: str, clave_municipio: str, cantidad: int = 5) -> List[Dict]:
        """Obtener localidades de un municipio usando DatabaseService"""
        try:
            # Obtener nodo principal
            nodo_principal = self.db_service.get_nodo_inicial_municipio(clave_estado, clave_municipio)
            if not nodo_principal:
                return []
            
            # Obtener localidades secundarias
            localidades = self.db_service.get_localidades_municipio(
                clave_estado, clave_municipio, 
                nodo_principal['clave_localidad'], cantidad
            )
            
            return localidades
        except Exception:
            return []