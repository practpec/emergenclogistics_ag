import random
import math
from typing import Dict, List, Tuple
from core.base_service import BaseService
from core.validators import BaseValidator
from services.data.database_service import DatabaseService

class GeoService(BaseService):
    """Servicio geográfico con flujo estado->municipio->localidades del mismo municipio"""
    
    def __init__(self):
        super().__init__()
        self.db_service = DatabaseService()
    
    def get_estados(self) -> List[str]:
        """Obtener lista de estados disponibles (nombres simples para compatibilidad)"""
        try:
            estados_data = self.db_service.get_estados()
            return [estado['nombre'] for estado in estados_data]
        except Exception as e:
            self.log_error("Error obteniendo estados", e)
            raise
    
    def get_estados_completos(self) -> List[Dict[str, str]]:
        """Obtener lista completa de estados con claves"""
        try:
            return self.db_service.get_estados()
        except Exception as e:
            self.log_error("Error obteniendo estados completos", e)
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
            self.log_error(f"Error obteniendo estado por nombre: {nombre_estado}", e)
            raise
    
    def get_municipios_por_estado(self, nombre_estado: str) -> List[Dict[str, str]]:
        """Obtener municipios de un estado"""
        try:
            estado = self.get_estado_by_nombre(nombre_estado)
            municipios = self.db_service.get_municipios_por_estado(estado['clave'])
            
            self.log_info(f"Municipios obtenidos para {nombre_estado}: {len(municipios)}")
            return municipios
            
        except Exception as e:
            self.log_error(f"Error obteniendo municipios para {nombre_estado}", e)
            raise
    
    def get_coordenadas_estado(self, nombre_estado: str) -> Dict[str, any]:
        """Obtener coordenadas principales de un estado (primer municipio disponible)"""
        try:
            estado = self.get_estado_by_nombre(nombre_estado)
            municipios = self.db_service.get_municipios_por_estado(estado['clave'])
            
            if not municipios:
                raise ValueError(f"No se encontraron municipios para el estado: {nombre_estado}")
            
            # Usar el primer municipio para obtener su localidad principal
            primer_municipio = municipios[0]
            nodo_inicial = self.db_service.get_nodo_inicial_municipio(
                estado['clave'], 
                primer_municipio['clave_municipio']
            )
            
            if not nodo_inicial:
                raise ValueError(f"No se encontró localidad principal para {nombre_estado}")
            
            return {
                'lat': nodo_inicial['lat'],
                'lng': nodo_inicial['lng'],
                'nombre': nodo_inicial['nombre'],
                'clave_estado': nodo_inicial['clave_estado'],
                'clave_municipio': nodo_inicial['clave_municipio'],
                'clave_localidad': nodo_inicial['clave_localidad'],
                'poblacion': nodo_inicial['poblacion']
            }
        except Exception as e:
            self.log_error(f"Error obteniendo coordenadas de estado: {nombre_estado}", e)
            raise
    
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
    
    def generar_nodos_secundarios(self, nombre_estado: str, cantidad_nodos: int, 
                                 clave_municipio: str = None) -> Dict[str, any]:
        """Generar nodos secundarios del mismo municipio que el nodo principal"""
        try:
            # Validar parámetros
            BaseValidator.validate_integer_range(cantidad_nodos, 1, 15, "cantidad_nodos")
            
            # Obtener datos del estado
            estado = self.get_estado_by_nombre(nombre_estado)
            
            # Si no se especifica municipio, usar el primer municipio disponible
            if not clave_municipio:
                municipios = self.db_service.get_municipios_por_estado(estado['clave'])
                if not municipios:
                    raise ValueError(f"No se encontraron municipios para {nombre_estado}")
                clave_municipio = municipios[0]['clave_municipio']
            
            # Obtener nodo principal (localidad principal del municipio)
            nodo_principal = self.db_service.get_nodo_inicial_municipio(
                estado['clave'], clave_municipio
            )
            
            if not nodo_principal:
                raise ValueError(f"No se encontró nodo principal para el municipio {clave_municipio}")
            
            # Obtener nodos secundarios del mismo municipio
            localidades_secundarias = self.db_service.get_localidades_municipio(
                estado['clave'],
                clave_municipio,
                nodo_principal['clave_localidad'],
                cantidad_nodos,
                poblacion_minima=20
            )
            
            # Calcular distancias y formatear nodos secundarios
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
                    'ambito': localidad['ambito'],
                    'distancia_directa': round(distancia, 2)
                })
            
            result = {
                "nodo_principal": nodo_principal,
                "nodos_secundarios": nodos_secundarios,
                "municipio_info": {
                    "clave_municipio": clave_municipio,
                    "nombre_municipio": nodo_principal['nombre_municipio'],
                    "total_localidades": len(nodos_secundarios) + 1
                }
            }
            
            self.log_info("Nodos generados del mismo municipio", 
                         estado=nombre_estado,
                         municipio=clave_municipio, 
                         cantidad=len(nodos_secundarios))
            
            return result
            
        except Exception as e:
            self.log_error("Error generando nodos del mismo municipio", e, estado=nombre_estado)
            raise
    
    def buscar_localidades(self, nombre: str, nombre_estado: str = None, limite: int = 10) -> List[Dict]:
        """Buscar localidades por nombre"""
        try:
            clave_estado = None
            if nombre_estado:
                estado = self.get_estado_by_nombre(nombre_estado)
                clave_estado = estado['clave']
            
            localidades = self.db_service.search_localidades(nombre, clave_estado, limite)
            
            # Calcular distancia directa si hay un estado de referencia
            if clave_estado and localidades:
                coord_estado = self.get_coordenadas_estado(nombre_estado)
                for localidad in localidades:
                    distancia = self.calcular_distancia_haversine(
                        coord_estado['lat'], coord_estado['lng'],
                        localidad['lat'], localidad['lng']
                    )
                    localidad['distancia_directa'] = round(distancia, 2)
            
            return localidades
            
        except Exception as e:
            self.log_error(f"Error buscando localidades: {nombre}", e)
            raise
    
    def get_localidad_by_claves(self, clave_estado: str, clave_municipio: str, 
                               clave_localidad: str) -> Dict:
        """Obtener localidad específica por sus claves"""
        try:
            localidad = self.db_service.get_localidad_by_id(
                clave_estado, clave_municipio, clave_localidad
            )
            if not localidad:
                raise ValueError(f"Localidad no encontrada: {clave_estado}-{clave_municipio}-{clave_localidad}")
            return localidad
        except Exception as e:
            self.log_error("Error obteniendo localidad por claves", e)
            raise
    
    def validar_ubicacion_mexico(self, lat: float, lng: float) -> bool:
        """Verificar que la coordenada esté dentro de México"""
        return (14.5 <= lat <= 32.7 and -118.4 <= lng <= -86.7)
    
    def generar_con_municipio_seleccionado(self, nombre_estado: str, clave_municipio: str, 
                                          cantidad_nodos: int) -> Dict[str, any]:
        """Generar nodos cuando el usuario ya seleccionó un municipio específico"""
        return self.generar_nodos_secundarios(nombre_estado, cantidad_nodos, clave_municipio)