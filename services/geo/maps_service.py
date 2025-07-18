import requests
import time
from typing import Dict, List, Any, Optional
from geopy.distance import geodesic
from core.base_service import CacheableService
from core.exceptions import ExternalAPIError, RouteCalculationError

class OSRMService(CacheableService):
    """Servicio para obtener rutas usando OSRM"""
    
    def __init__(self, base_url: str = "http://router.project-osrm.org"):
        super().__init__()
        self.base_url = base_url
        self.timeout = 8
        self.delay_between_requests = 0.3
    
    def obtener_rutas_completas(self, origen: Dict, destinos: List[Dict]) -> List[Dict]:
        """Obtener rutas completas para todos los destinos"""
        rutas_data = []
        
        for i, destino in enumerate(destinos):
            try:
                rutas_destino = self._obtener_rutas_multiples_destino(origen, destino, i)
                
                rutas_data.append({
                    'indice': i,
                    'destino': destino,
                    'rutas': rutas_destino
                })
                
                # Delay para evitar sobrecarga de la API
                time.sleep(self.delay_between_requests)
                
            except Exception as e:
                self.log_warning(f"Error obteniendo rutas para destino {i+1}", error=str(e))
                # Agregar ruta directa como fallback
                rutas_data.append({
                    'indice': i,
                    'destino': destino,
                    'rutas': [self._calcular_ruta_directa(origen, destino)]
                })
        
        self.log_info(f"Rutas obtenidas para {len(destinos)} destinos")
        return rutas_data
    
    def _obtener_rutas_multiples_destino(self, origen: Dict, destino: Dict, index: int) -> List[Dict]:
        """Obtener múltiples rutas para un destino específico"""
        rutas = []
        
        try:
            # Ruta principal
            ruta_principal = self._obtener_ruta_simple(origen, destino)
            if ruta_principal:
                ruta_principal['tipo'] = 'Ruta 1'
                ruta_principal['descripcion'] = 'Ruta hacia el destino'
                rutas.append(ruta_principal)
            
            distancia_km = self._calcular_distancia_directa(origen, destino)
            
            # Rutas alternativas solo para distancias mayores
            if distancia_km > 10:
                ruta_norte = self._obtener_ruta_variante(origen, destino, 'norte')
                if ruta_norte and not self._son_rutas_similares(ruta_principal, ruta_norte):
                    ruta_norte['tipo'] = 'Ruta 2'
                    ruta_norte['descripcion'] = 'Ruta alternativa'
                    rutas.append(ruta_norte)
                
                if distancia_km > 30:
                    ruta_sur = self._obtener_ruta_variante(origen, destino, 'sur')
                    if ruta_sur and not self._es_ruta_similar_a_lista(ruta_sur, rutas):
                        ruta_sur['tipo'] = 'Ruta 3'
                        ruta_sur['descripcion'] = 'Ruta alternativa'
                        rutas.append(ruta_sur)
            
            # Si no hay rutas, usar ruta directa
            if not rutas:
                rutas.append(self._calcular_ruta_directa(origen, destino))
                
        except Exception as e:
            self.log_error(f"Error obteniendo rutas para destino {index + 1}", e)
            rutas = [self._calcular_ruta_directa(origen, destino)]
        
        return rutas
    
    def _obtener_ruta_simple(self, origen: Dict, destino: Dict) -> Optional[Dict]:
        """Obtener ruta simple entre dos puntos"""
        cache_key = f"route_{origen['lat']},{origen['lng']}_{destino['lat']},{destino['lng']}"
        
        # Verificar cache
        cached_route = self.get_from_cache(cache_key)
        if cached_route:
            return cached_route
        
        try:
            origen_str = f"{origen['lng']},{origen['lat']}"
            destino_str = f"{destino['lng']},{destino['lat']}"
            
            url = f"{self.base_url}/route/v1/driving/{origen_str};{destino_str}"
            params = {
                'overview': 'simplified',
                'geometries': 'geojson'
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code != 200:
                return self._calcular_ruta_directa(origen, destino)
            
            data = response.json()
            
            if 'routes' not in data or len(data['routes']) == 0:
                return self._calcular_ruta_directa(origen, destino)
            
            route = data['routes'][0]
            
            result = {
                'distancia': {
                    'text': f"{route['distance']/1000:.1f} km",
                    'value': route['distance']
                },
                'puntos_ruta': self._extraer_puntos_geojson(route['geometry'])
            }
            
            # Guardar en cache
            self.set_cache(cache_key, result)
            
            return result
            
        except requests.RequestException as e:
            self.log_warning("Error en solicitud OSRM", error=str(e))
            return self._calcular_ruta_directa(origen, destino)
        except Exception as e:
            self.log_error("Error procesando respuesta OSRM", e)
            return self._calcular_ruta_directa(origen, destino)
    
    def _obtener_ruta_variante(self, origen: Dict, destino: Dict, direccion: str) -> Optional[Dict]:
        """Obtener ruta alternativa usando waypoint"""
        try:
            mid_lat = (origen['lat'] + destino['lat']) / 2
            mid_lng = (origen['lng'] + destino['lng']) / 2
            
            offset = 0.01 if direccion == 'norte' else -0.01
            waypoint = {
                'lat': mid_lat + offset,
                'lng': mid_lng
            }
            
            ruta1 = self._obtener_ruta_simple(origen, waypoint)
            ruta2 = self._obtener_ruta_simple(waypoint, destino)
            
            if ruta1 and ruta2:
                return self._combinar_rutas(ruta1, ruta2)
                
        except Exception as e:
            self.log_warning("Error obteniendo ruta variante", error=str(e))
        
        return None
    
    def _combinar_rutas(self, ruta1: Dict, ruta2: Dict) -> Dict:
        """Combinar dos rutas en una sola"""
        return {
            'distancia': {
                'text': f"{(ruta1['distancia']['value'] + ruta2['distancia']['value'])/1000:.1f} km",
                'value': ruta1['distancia']['value'] + ruta2['distancia']['value']
            },
            'puntos_ruta': ruta1['puntos_ruta'] + ruta2['puntos_ruta']
        }
    
    def _calcular_ruta_directa(self, origen: Dict, destino: Dict) -> Dict:
        """Calcular ruta directa entre dos puntos"""
        distancia_km = geodesic(
            (origen['lat'], origen['lng']),
            (destino['lat'], destino['lng'])
        ).kilometers
        
        return {
            'distancia': {
                'text': f"{distancia_km:.1f} km",
                'value': distancia_km * 1000
            },
            'puntos_ruta': [
                {'lat': origen['lat'], 'lng': origen['lng']},
                {'lat': destino['lat'], 'lng': destino['lng']}
            ],
            'tipo': 'Ruta Directa',
            'descripcion': 'Línea directa al destino'
        }
    
    def _extraer_puntos_geojson(self, geometry: Dict) -> List[Dict]:
        """Extraer puntos de geometría GeoJSON"""
        if geometry['type'] == 'LineString':
            puntos = []
            coords = geometry['coordinates']
            
            # Simplificar la ruta tomando cada N puntos
            step = max(1, len(coords) // 20)
            
            for i in range(0, len(coords), step):
                coord = coords[i]
                puntos.append({
                    'lat': coord[1],
                    'lng': coord[0]
                })
            
            # Asegurar que incluimos el último punto
            if len(coords) > 0 and coords[-1] != coords[step * (len(coords) // step - 1)]:
                coord = coords[-1]
                puntos.append({
                    'lat': coord[1],
                    'lng': coord[0]
                })
            
            return puntos
        return []
    
    def _calcular_distancia_directa(self, origen: Dict, destino: Dict) -> float:
        """Calcular distancia directa entre dos puntos"""
        return geodesic(
            (origen['lat'], origen['lng']),
            (destino['lat'], destino['lng'])
        ).kilometers
    
    def _son_rutas_similares(self, ruta1: Dict, ruta2: Dict, threshold: float = 0.15) -> bool:
        """Verificar si dos rutas son similares"""
        if not ruta1 or not ruta2:
            return False
        
        diff = abs(ruta1['distancia']['value'] - ruta2['distancia']['value']) / ruta1['distancia']['value']
        return diff < threshold
    
    def _es_ruta_similar_a_lista(self, nueva_ruta: Dict, rutas_existentes: List[Dict], 
                                threshold: float = 0.15) -> bool:
        """Verificar si una ruta es similar a alguna de una lista"""
        return any(self._son_rutas_similares(nueva_ruta, ruta, threshold) 
                  for ruta in rutas_existentes)