"""
Servicio de mapas y rutas optimizado
"""
import requests
import time
from typing import Dict, List, Any, Optional
from geopy.distance import geodesic
from utils.logger import get_logger
from core.exceptions import RouteCalculationError

class MapsService:
    """Servicio para cálculo de rutas"""
    
    def __init__(self, osrm_base_url: str):
        self.osrm_base_url = osrm_base_url
        self.logger = get_logger(__name__)
        self.request_delay = 0.3  # Delay entre requests
    
    def calculate_complete_routes(self, origin: Dict[str, float], 
                                destinations: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Calcular rutas completas para múltiples destinos"""
        routes_data = []
        
        for i, destination in enumerate(destinations):
            try:
                routes = self._calculate_multiple_routes(origin, destination, i)
                routes_data.append({
                    'indice': i,
                    'destino': destination,
                    'rutas': routes
                })
                
                # Delay para evitar rate limiting
                time.sleep(self.request_delay)
                
            except Exception as e:
                self.logger.error(f"Error calculando rutas para destino {i}: {e}")
                # Agregar ruta directa como fallback
                routes_data.append({
                    'indice': i,
                    'destino': destination,
                    'rutas': [self._calculate_direct_route(origin, destination)]
                })
        
        self.logger.info(f"Calculadas rutas para {len(routes_data)} destinos")
        return routes_data
    
    def _calculate_multiple_routes(self, origin: Dict[str, float], 
                                 destination: Dict[str, float], index: int) -> List[Dict[str, Any]]:
        """Calcular múltiples rutas para un destino"""
        routes = []
        
        # Ruta principal
        main_route = self._calculate_single_route(origin, destination)
        if main_route:
            main_route['tipo'] = 'Ruta Principal'
            main_route['descripcion'] = 'Camino más directo'
            routes.append(main_route)
        
        # Rutas alternativas solo para distancias > 10km
        distance_km = self._calculate_direct_distance(origin, destination)
        if distance_km > 10:
            alt_route = self._calculate_alternative_route(origin, destination)
            if alt_route and not self._are_routes_similar(main_route, alt_route):
                alt_route['tipo'] = 'Ruta Alternativa'
                alt_route['descripcion'] = 'Camino alternativo'
                routes.append(alt_route)
        
        # Si no hay rutas, usar directa
        if not routes:
            routes.append(self._calculate_direct_route(origin, destination))
        
        return routes
    
    def _calculate_single_route(self, origin: Dict[str, float], 
                              destination: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Calcular ruta individual usando OSRM"""
        try:
            origin_str = f"{origin['lng']},{origin['lat']}"
            dest_str = f"{destination['lng']},{destination['lat']}"
            
            url = f"{self.osrm_base_url}/route/v1/driving/{origin_str};{dest_str}"
            params = {
                'overview': 'simplified',
                'geometries': 'geojson'
            }
            
            response = requests.get(url, params=params, timeout=8)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            if 'routes' not in data or not data['routes']:
                return None
            
            route = data['routes'][0]
            return {
                'distancia': {
                    'text': f"{route['distance']/1000:.1f} km",
                    'value': route['distance']
                },
                'puntos_ruta': self._extract_route_points(route['geometry'])
            }
            
        except Exception as e:
            self.logger.warning(f"Error en OSRM: {e}")
            return None
    
    def _calculate_alternative_route(self, origin: Dict[str, float], 
                                   destination: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Calcular ruta alternativa con waypoint"""
        try:
            # Punto intermedio con offset
            mid_lat = (origin['lat'] + destination['lat']) / 2
            mid_lng = (origin['lng'] + destination['lng']) / 2
            
            waypoint = {
                'lat': mid_lat + 0.01,  # Offset de ~1km
                'lng': mid_lng
            }
            
            # Calcular ruta con waypoint
            route1 = self._calculate_single_route(origin, waypoint)
            route2 = self._calculate_single_route(waypoint, destination)
            
            if route1 and route2:
                return self._combine_routes(route1, route2)
                
        except Exception as e:
            self.logger.warning(f"Error calculando ruta alternativa: {e}")
        
        return None
    
    def _calculate_direct_route(self, origin: Dict[str, float], 
                              destination: Dict[str, float]) -> Dict[str, Any]:
        """Calcular ruta directa (línea recta)"""
        distance_km = self._calculate_direct_distance(origin, destination)
        
        return {
            'distancia': {
                'text': f"{distance_km:.1f} km",
                'value': distance_km * 1000
            },
            'puntos_ruta': [
                {'lat': origin['lat'], 'lng': origin['lng']},
                {'lat': destination['lat'], 'lng': destination['lng']}
            ],
            'tipo': 'Ruta Directa',
            'descripcion': 'Línea recta (estimación)'
        }
    
    def _calculate_direct_distance(self, origin: Dict[str, float], 
                                 destination: Dict[str, float]) -> float:
        """Calcular distancia directa"""
        return geodesic(
            (origin['lat'], origin['lng']),
            (destination['lat'], destination['lng'])
        ).kilometers
    
    def _extract_route_points(self, geometry: Dict[str, Any]) -> List[Dict[str, float]]:
        """Extraer puntos de geometría GeoJSON"""
        if geometry['type'] != 'LineString':
            return []
        
        coords = geometry['coordinates']
        points = []
        
        # Simplificar ruta (máximo 20 puntos)
        step = max(1, len(coords) // 20)
        
        for i in range(0, len(coords), step):
            coord = coords[i]
            points.append({
                'lat': coord[1],
                'lng': coord[0]
            })
        
        # Asegurar punto final
        if coords and coords[-1] != coords[len(coords) - step]:
            final_coord = coords[-1]
            points.append({
                'lat': final_coord[1],
                'lng': final_coord[0]
            })
        
        return points
    
    def _combine_routes(self, route1: Dict[str, Any], 
                       route2: Dict[str, Any]) -> Dict[str, Any]:
        """Combinar dos rutas"""
        return {
            'distancia': {
                'text': f"{(route1['distancia']['value'] + route2['distancia']['value'])/1000:.1f} km",
                'value': route1['distancia']['value'] + route2['distancia']['value']
            },
            'puntos_ruta': route1['puntos_ruta'] + route2['puntos_ruta']
        }
    
    def _are_routes_similar(self, route1: Optional[Dict[str, Any]], 
                           route2: Optional[Dict[str, Any]], threshold: float = 0.15) -> bool:
        """Verificar si dos rutas son similares"""
        if not route1 or not route2:
            return False
        
        diff = abs(route1['distancia']['value'] - route2['distancia']['value'])
        relative_diff = diff / route1['distancia']['value']
        
        return relative_diff < threshold