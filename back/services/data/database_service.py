import sqlite3
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from core.base_service import BaseService
from core.exceptions import DataLoadError

class DatabaseService(BaseService):
    """Servicio para manejo de base de datos de localidades - FILTRADO POR POBLACIÓN"""
    
    def __init__(self, db_path: str = "data/localidades.db"):
        super().__init__()
        self.db_path = db_path
        self.MIN_POBLACION = 1000
            
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.log_error("Error en conexión a base de datos", e)
            raise
        finally:
            if conn:
                conn.close()
    
    def get_estados(self) -> List[Dict[str, Any]]:
        """Obtener lista de estados disponibles"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT clave_estado, estado
                    FROM localidades
                    ORDER BY estado
                """)
                
                return [{'clave': row['clave_estado'], 'nombre': row['estado']} 
                       for row in cursor.fetchall()]
                
        except Exception as e:
            self.log_error("Error obteniendo estados", e)
            raise DataLoadError(f"Error obteniendo estados: {e}")
    
    def get_municipios_por_estado(self, clave_estado: str) -> List[Dict[str, Any]]:
        """Obtener municipios de un estado"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT l.clave_municipio, l.municipio, l.estado
                    FROM localidades l
                    WHERE l.clave_estado = ?
                    ORDER BY l.municipio
                """, (clave_estado,))
                
                return [{
                    'clave_municipio': row['clave_municipio'],
                    'nombre_municipio': row['municipio'],
                    'nombre_estado': row['estado']
                } for row in cursor.fetchall()]
                
        except Exception as e:
            self.log_error(f"Error obteniendo municipios para estado {clave_estado}", e)
            raise DataLoadError(f"Error obteniendo municipios: {e}")
    
    def get_nodo_inicial_municipio(self, clave_estado: str, clave_municipio: str) -> Optional[Dict[str, Any]]:
        """Obtener el nodo inicial del municipio (localidad con mayor población >= 1000)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT clave_estado, estado,
                           clave_municipio, municipio,
                           clave_localidad, localidad,
                           poblacion, latitud, longitud, ambito
                    FROM localidades
                    WHERE clave_estado = ? AND clave_municipio = ?
                      AND latitud IS NOT NULL AND longitud IS NOT NULL
                      AND poblacion IS NOT NULL
                      AND CAST(poblacion AS INTEGER) >= ?
                    ORDER BY CAST(poblacion AS INTEGER) DESC
                    LIMIT 1
                """, (clave_estado, clave_municipio, self.MIN_POBLACION))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'clave_estado': row['clave_estado'],
                        'nombre_estado': row['estado'],
                        'clave_municipio': row['clave_municipio'],
                        'nombre_municipio': row['municipio'],
                        'clave_localidad': row['clave_localidad'],
                        'nombre_localidad': row['localidad'],
                        'poblacion': row['poblacion'],
                        'lat': float(row['latitud']),
                        'lng': float(row['longitud']),
                        'ambito': row['ambito'],
                        'nombre': f"{row['localidad']}, {row['municipio']}, {row['estado']}"
                    }
                
                return None
                
        except Exception as e:
            self.log_error(f"Error obteniendo nodo inicial para municipio {clave_municipio}", e)
            raise DataLoadError(f"Error obteniendo nodo inicial: {e}")
    
    def get_localidad_by_clave(self, clave_localidad: str) -> Optional[Dict[str, Any]]:
        """Consultar localidad específica por clave_localidad (población >= 1000)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT clave_estado, estado,
                           clave_municipio, municipio,
                           clave_localidad, localidad,
                           poblacion, latitud, longitud, ambito
                    FROM localidades
                    WHERE clave_localidad = ?
                      AND latitud IS NOT NULL AND longitud IS NOT NULL
                      AND poblacion IS NOT NULL
                      AND CAST(poblacion AS INTEGER) >= ?
                    LIMIT 1
                """, (clave_localidad, self.MIN_POBLACION))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'clave_estado': row['clave_estado'],
                        'nombre_estado': row['estado'],
                        'clave_municipio': row['clave_municipio'],
                        'nombre_municipio': row['municipio'],
                        'clave_localidad': row['clave_localidad'],
                        'nombre_localidad': row['localidad'],
                        'poblacion': int(row['poblacion']) if row['poblacion'] else 0,
                        'lat': float(row['latitud']) if row['latitud'] else None,
                        'lng': float(row['longitud']) if row['longitud'] else None,
                        'ambito': row['ambito'],
                        'nombre': f"{row['localidad']}, {row['municipio']}, {row['estado']}"
                    }
                
                return None
                
        except Exception as e:
            self.log_error(f"Error obteniendo localidad {clave_localidad}", e)
            raise DataLoadError(f"Error obteniendo localidad: {e}")
    
    def get_localidades_by_claves(self, claves_localidades: List[str]) -> List[Dict[str, Any]]:
        """Consultar múltiples localidades por sus claves (población >= 1000)"""
        try:
            if not claves_localidades:
                return []
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' * len(claves_localidades))
                cursor.execute(f"""
                    SELECT clave_estado, estado,
                           clave_municipio, municipio,
                           clave_localidad, localidad,
                           poblacion, latitud, longitud, ambito
                    FROM localidades
                    WHERE clave_localidad IN ({placeholders})
                      AND latitud IS NOT NULL AND longitud IS NOT NULL
                      AND poblacion IS NOT NULL
                      AND CAST(poblacion AS INTEGER) >= ?
                    ORDER BY CAST(poblacion AS INTEGER) DESC
                """, claves_localidades + [self.MIN_POBLACION])
                
                return [{
                    'clave_estado': row['clave_estado'],
                    'nombre_estado': row['estado'],
                    'clave_municipio': row['clave_municipio'],
                    'nombre_municipio': row['municipio'],
                    'clave_localidad': row['clave_localidad'],
                    'nombre_localidad': row['localidad'],
                    'poblacion': int(row['poblacion']) if row['poblacion'] else 0,
                    'lat': float(row['latitud']) if row['latitud'] else None,
                    'lng': float(row['longitud']) if row['longitud'] else None,
                    'ambito': row['ambito'],
                    'nombre': f"{row['localidad']}, {row['municipio']}, {row['estado']}"
                } for row in cursor.fetchall()]
                
        except Exception as e:
            self.log_error(f"Error obteniendo localidades por claves", e)
            raise DataLoadError(f"Error obteniendo localidades: {e}")
    
    def count_localidades_municipio(self, clave_estado: str, clave_municipio: str) -> int:
        """Contar total de localidades en un municipio (población >= 1000)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM localidades
                    WHERE clave_estado = ? AND clave_municipio = ?
                      AND latitud IS NOT NULL AND longitud IS NOT NULL
                      AND poblacion IS NOT NULL
                      AND CAST(poblacion AS INTEGER) >= ?
                """, (clave_estado, clave_municipio, self.MIN_POBLACION))
                
                row = cursor.fetchone()
                return row['total'] if row else 0
                
        except Exception as e:
            self.log_error(f"Error contando localidades para municipio {clave_municipio}", e)
            raise DataLoadError(f"Error contando localidades: {e}")
    
    def get_localidades_municipio(self, clave_estado: str, clave_municipio: str, 
                                 clave_localidad_excluir: str, cantidad: int,
                                 poblacion_minima: int = None) -> List[Dict[str, Any]]:
        """Obtener localidades del mismo municipio excluyendo el nodo inicial (población >= 1000)"""
        if poblacion_minima is None:
            poblacion_minima = self.MIN_POBLACION
        else:
            poblacion_minima = max(poblacion_minima, self.MIN_POBLACION)
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT clave_estado, estado,
                           clave_municipio, municipio,
                           clave_localidad, localidad,
                           poblacion, latitud, longitud, ambito
                    FROM localidades
                    WHERE clave_estado = ? AND clave_municipio = ?
                      AND clave_localidad != ?
                      AND CAST(poblacion AS INTEGER) >= ?
                      AND latitud IS NOT NULL AND longitud IS NOT NULL
                      AND poblacion IS NOT NULL
                    ORDER BY CAST(poblacion AS INTEGER) DESC
                    LIMIT ?
                """, (clave_estado, clave_municipio, clave_localidad_excluir, poblacion_minima, cantidad))
                
                return [{
                    'clave_estado': row['clave_estado'],
                    'nombre_estado': row['estado'],
                    'clave_municipio': row['clave_municipio'],
                    'nombre_municipio': row['municipio'],
                    'clave_localidad': row['clave_localidad'],
                    'nombre_localidad': row['localidad'],
                    'poblacion': row['poblacion'],
                    'lat': float(row['latitud']),
                    'lng': float(row['longitud']),
                    'ambito': row['ambito'],
                    'nombre': f"{row['localidad']}, {row['municipio']}, {row['estado']}"
                } for row in cursor.fetchall()]
                
        except Exception as e:
            self.log_error(f"Error obteniendo localidades para municipio {clave_municipio}", e)
            raise DataLoadError(f"Error obteniendo localidades: {e}")
    
    def validate_localidades_existen(self, claves_localidades: List[str]) -> Dict[str, bool]:
        """Validar que las claves de localidades existen en BD (población >= 1000)"""
        try:
            if not claves_localidades:
                return {}
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                placeholders = ','.join('?' * len(claves_localidades))
                cursor.execute(f"""
                    SELECT clave_localidad
                    FROM localidades
                    WHERE clave_localidad IN ({placeholders})
                      AND CAST(poblacion AS INTEGER) >= ?
                """, claves_localidades + [self.MIN_POBLACION])
                
                claves_existentes = set(row['clave_localidad'] for row in cursor.fetchall())
                
                return {clave: clave in claves_existentes for clave in claves_localidades}
                
        except Exception as e:
            self.log_error(f"Error validando existencia de localidades", e)
            return {clave: False for clave in claves_localidades}