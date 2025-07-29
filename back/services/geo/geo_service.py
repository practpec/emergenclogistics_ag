import math
from typing import Dict, List
from core.base_service import BaseService
from core.helpers import validate_coordinates
from services.data.database_service import DatabaseService

class GeoService(BaseService):
    """Servicio geográfico optimizado"""
    
    def __init__(self):
        super().__init__()
        self.db_service = DatabaseService()
    
    def get_estados_completos(self) -> List[Dict[str, str]]:
        """Obtener lista completa de estados"""
        try:
            return self.db_service.get_estados()
        except Exception as e:
            self.log_error("Error obteniendo estados", e)
            raise
    
    def get_estado_by_nombre(self, nombre_estado: str) -> Dict[str, str]:
        """Obtener datos de estado por nombre"""
        try:
            estados = self.db_service.get_estados()
            for estado in estados:
                if estado['nombre'].lower() == nombre_estado.lower():
                    return estado
            raise ValueError(f"Estado no encontrado: {nombre_estado}")
        except Exception as e:
            self.log_error(f"Error obteniendo estado: {nombre_estado}", e)
            raise
    
    def get_municipios_por_estado(self, nombre_estado: str) -> List[Dict[str, str]]:
        """Obtener municipios de un estado"""
        try:
            estado = self.get_estado_by_nombre(nombre_estado)
            return self.db_service.get_municipios_por_estado(estado['clave'])
        except Exception as e:
            self.log_error(f"Error obteniendo municipios para {nombre_estado}", e)
            raise
    
    def calcular_distancia_haversine(self, lat1: float, lon1: float, 
                                   lat2: float, lon2: float) -> float:
        """Calcular distancia entre dos puntos usando Haversine"""
        if not all(validate_coordinates(lat, lng) for lat, lng in [(lat1, lon1), (lat2, lon2)]):
            raise ValueError("Coordenadas inválidas")
        
        R = 6371
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def generar_nodos_secundarios(self, nombre_estado: str, cantidad_nodos: int, 
                                 clave_municipio: str = None) -> Dict:
        """Generar nodos secundarios del mismo municipio"""
        try:
            if not (5 <= cantidad_nodos <= 20):
                raise ValueError("Cantidad de nodos debe estar entre 5 y 20")
            
            estado = self.get_estado_by_nombre(nombre_estado)
            
            if not clave_municipio:
                municipios = self.db_service.get_municipios_por_estado(estado['clave'])
                if not municipios:
                    raise ValueError(f"No hay municipios para {nombre_estado}")
                clave_municipio = municipios[0]['clave_municipio']
            
            nodo_principal = self.db_service.get_nodo_inicial_municipio(
                estado['clave'], clave_municipio
            )
            
            if not nodo_principal:
                raise ValueError(f"No se encontró nodo principal para {clave_municipio}")
            
            localidades_secundarias = self.db_service.get_localidades_municipio(
                estado['clave'], clave_municipio, 
                nodo_principal['clave_localidad'], cantidad_nodos, 20
            )
            
            nodos_secundarios = []
            for localidad in localidades_secundarias:
                distancia = self.calcular_distancia_haversine(
                    nodo_principal['lat'], nodo_principal['lng'],
                    localidad['lat'], localidad['lng']
                )
                
                nodos_secundarios.append({
                    'lat': localidad['lat'],
                    'lng': localidad['lng'],
                    'nombre': localidad['nombre'],
                    'clave_estado': localidad['clave_estado'],
                    'clave_municipio': localidad['clave_municipio'],
                    'clave_localidad': localidad['clave_localidad'],
                    'poblacion': localidad['poblacion'],
                    'distancia_directa': round(distancia, 2)
                })
            
            return {
                "nodo_principal": nodo_principal,
                "nodos_secundarios": nodos_secundarios,
                "municipio_info": {
                    "clave_municipio": clave_municipio,
                    "nombre_municipio": nodo_principal['nombre_municipio'],
                    "total_localidades": len(nodos_secundarios) + 1
                }
            }
            
        except Exception as e:
            self.log_error("Error generando nodos", e)
            raise