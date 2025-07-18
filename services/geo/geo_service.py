import random
import math
from typing import Dict, List, Tuple
from core.base_service import BaseService
from core.validators import BaseValidator

class GeoService(BaseService):
    """Servicio para manejo de datos geográficos"""
    
    def __init__(self):
        super().__init__()
        self.estados_coords = {
            "Chiapas": {"lat": 16.75, "lng": -93.1167, "nombre": "Chiapas"},
            "CDMX": {"lat": 19.4326, "lng": -99.1332, "nombre": "Ciudad de México"},
            "Jalisco": {"lat": 20.6597, "lng": -103.3496, "nombre": "Jalisco"},
            "Nuevo León": {"lat": 25.6866, "lng": -100.3161, "nombre": "Nuevo León"},
            "Yucatán": {"lat": 20.7099, "lng": -89.0943, "nombre": "Yucatán"},
            "Oaxaca": {"lat": 17.0732, "lng": -96.7266, "nombre": "Oaxaca"},
            "Puebla": {"lat": 19.0414, "lng": -98.2063, "nombre": "Puebla"},
            "Veracruz": {"lat": 19.1738, "lng": -96.1342, "nombre": "Veracruz"},
            "Guanajuato": {"lat": 21.0190, "lng": -101.2574, "nombre": "Guanajuato"},
            "Michoacán": {"lat": 19.5665, "lng": -101.7068, "nombre": "Michoacán"},
            "Guerrero": {"lat": 17.4392, "lng": -99.5451, "nombre": "Guerrero"},
            "Sonora": {"lat": 29.2972, "lng": -110.3309, "nombre": "Sonora"},
            "Tamaulipas": {"lat": 24.2669, "lng": -98.8363, "nombre": "Tamaulipas"},
            "Sinaloa": {"lat": 25.1721, "lng": -107.4795, "nombre": "Sinaloa"},
            "Coahuila": {"lat": 27.0587, "lng": -101.7068, "nombre": "Coahuila"},
            "Quintana Roo": {"lat": 19.1817, "lng": -88.4791, "nombre": "Quintana Roo"},
            "Baja California": {"lat": 30.8406, "lng": -115.2838, "nombre": "Baja California"},
            "San Luis Potosí": {"lat": 22.1565, "lng": -100.9855, "nombre": "San Luis Potosí"}
        }
        
        # Ciudades principales por estado para generación inteligente
        self.ciudades_mexico = {
            "Chiapas": [
                (16.7569, -93.1292),  # Tuxtla Gutiérrez
                (16.7409, -92.6375),  # San Cristóbal
                (17.5569, -93.4016),  # Palenque
                (16.2418, -93.7636),  # Tapachula
            ],
            "CDMX": [
                (19.4326, -99.1332),  # Centro
                (19.3629, -99.2837),  # Santa Fe
                (19.5047, -99.1181),  # Satélite
                (19.2911, -99.0940),  # Coyoacán
            ],
            "Jalisco": [
                (20.6597, -103.3496), # Guadalajara
                (20.5888, -103.4224), # Zapopan
                (20.6668, -105.2064), # Puerto Vallarta
                (20.5230, -103.4068), # Tlaquepaque
            ]
        }
    
    def get_estados(self) -> List[str]:
        """Obtener lista de estados disponibles"""
        return list(self.estados_coords.keys())
    
    def get_coordenadas_estado(self, estado: str) -> Dict[str, any]:
        """Obtener coordenadas de un estado específico"""
        coords = self.estados_coords.get(estado)
        if not coords:
            raise ValueError(f"Estado no encontrado: {estado}")
        return coords
    
    def calcular_distancia_haversine(self, lat1: float, lon1: float, 
                                   lat2: float, lon2: float) -> float:
        """Calcular distancia entre dos puntos usando la fórmula de Haversine"""
        R = 6371  # Radio de la Tierra en kilómetros
        
        # Validar coordenadas
        BaseValidator.validate_coordinates(lat1, lon1)
        BaseValidator.validate_coordinates(lat2, lon2)
        
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def generar_nodos_secundarios(self, estado: str, cantidad_nodos: int) -> Dict[str, any]:
        """Generar nodos secundarios para un estado específico"""
        try:
            # Validar parámetros
            BaseValidator.validate_integer_range(cantidad_nodos, 1, 15, "cantidad_nodos")
            
            nodo_principal = self.get_coordenadas_estado(estado)
            
            # Generar coordenadas inteligentes
            coordenadas_candidatas = self._generar_coordenadas_inteligentes(
                estado, cantidad_nodos * 5
            )
            
            # Filtrar por distancia
            nodos_filtrados = self._filtrar_por_distancia(
                nodo_principal, coordenadas_candidatas, 100
            )
            
            # Completar con nodos aleatorios si es necesario
            if len(nodos_filtrados) < cantidad_nodos:
                nodos_extra = self._generar_nodos_aleatorios_cerca(
                    nodo_principal, cantidad_nodos - len(nodos_filtrados)
                )
                nodos_filtrados.extend(nodos_extra)
            
            # Seleccionar cantidad solicitada
            nodos_secundarios = random.sample(
                nodos_filtrados, 
                min(cantidad_nodos, len(nodos_filtrados))
            )
            
            result = {
                "nodo_principal": nodo_principal,
                "nodos_secundarios": nodos_secundarios
            }
            
            self.log_info("Nodos generados exitosamente", 
                         estado=estado, 
                         cantidad=len(nodos_secundarios))
            
            return result
            
        except Exception as e:
            self.log_error("Error generando nodos", e, estado=estado)
            raise
    
    def _generar_coordenadas_inteligentes(self, estado_base: str, cantidad: int) -> List[Dict]:
        """Generar coordenadas cerca de ciudades conocidas"""
        coordenadas = []
        base_coords = self.get_coordenadas_estado(estado_base)
        ciudades_estado = self.ciudades_mexico.get(estado_base, [])
        
        # Si no hay ciudades definidas, usar el centro del estado
        if not ciudades_estado:
            ciudades_estado = [(base_coords['lat'], base_coords['lng'])]
        
        # Generar puntos alrededor de las ciudades
        for ciudad_lat, ciudad_lng in ciudades_estado:
            puntos_por_ciudad = cantidad // len(ciudades_estado)
            
            for _ in range(puntos_por_ciudad):
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(5, 50)  # Entre 5 y 50 km
                
                # Convertir a grados
                lat_offset = (radius / 111.32) * math.cos(angle)
                lng_offset = (radius / (111.32 * math.cos(math.radians(ciudad_lat)))) * math.sin(angle)
                
                nueva_lat = ciudad_lat + lat_offset
                nueva_lng = ciudad_lng + lng_offset
                
                # Verificar que esté dentro de México
                if self._es_coordenada_valida_mexico(nueva_lat, nueva_lng):
                    coordenadas.append({"lat": nueva_lat, "lng": nueva_lng})
        
        # Completar con puntos aleatorios si es necesario
        while len(coordenadas) < cantidad:
            lat = random.uniform(
                max(14.5, base_coords['lat'] - 2),
                min(32.7, base_coords['lat'] + 2)
            )
            lng = random.uniform(
                max(-118.4, base_coords['lng'] - 2),
                min(-86.7, base_coords['lng'] + 2)
            )
            
            if self._es_coordenada_valida_mexico(lat, lng):
                coordenadas.append({"lat": lat, "lng": lng})
        
        return coordenadas[:cantidad]
    
    def _filtrar_por_distancia(self, nodo_principal: Dict, candidatos: List[Dict], 
                              radio_km: float) -> List[Dict]:
        """Filtrar nodos dentro del radio especificado"""
        nodos_filtrados = []
        
        for nodo in candidatos:
            distancia = self.calcular_distancia_haversine(
                nodo_principal["lat"], nodo_principal["lng"],
                nodo["lat"], nodo["lng"]
            )
            
            if distancia <= radio_km:
                nodos_filtrados.append({
                    "lat": nodo["lat"],
                    "lng": nodo["lng"],
                    "distancia_directa": round(distancia, 2)
                })
        
        return nodos_filtrados
    
    def _generar_nodos_aleatorios_cerca(self, nodo_central: Dict, cantidad: int) -> List[Dict]:
        """Generar nodos aleatorios cerca de un punto central"""
        nodos = []
        
        for _ in range(cantidad * 3):  # Generar extra para filtrar
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(10, 100)  # Entre 10 y 100 km
            
            lat_offset = (radius / 111.32) * math.cos(angle)
            lng_offset = (radius / (111.32 * math.cos(math.radians(nodo_central['lat'])))) * math.sin(angle)
            
            nueva_lat = nodo_central['lat'] + lat_offset
            nueva_lng = nodo_central['lng'] + lng_offset
            
            if self._es_coordenada_valida_mexico(nueva_lat, nueva_lng):
                distancia = self.calcular_distancia_haversine(
                    nodo_central['lat'], nodo_central['lng'],
                    nueva_lat, nueva_lng
                )
                
                if distancia <= 100:
                    nodos.append({
                        "lat": nueva_lat,
                        "lng": nueva_lng,
                        "distancia_directa": round(distancia, 2)
                    })
                    
                    if len(nodos) >= cantidad:
                        break
        
        return nodos[:cantidad]
    
    def _es_coordenada_valida_mexico(self, lat: float, lng: float) -> bool:
        """Verificar que la coordenada esté dentro de México"""
        return (14.5 <= lat <= 32.7 and -118.4 <= lng <= -86.7)