import sqlite3
import os
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from core.base_service import BaseService
from core.exceptions import DataLoadError

class DatabaseService(BaseService):
    """Servicio para manejo de base de datos de localidades con flujo estado->municipio->localidades"""
    
    def __init__(self, db_path: str = "data/localidades.db"):
        super().__init__()
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Verificar que la base de datos existe"""
        if not os.path.exists(self.db_path):
            raise DataLoadError(f"Base de datos no encontrada: {self.db_path}")
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='localidades'
                """)
                if not cursor.fetchone():
                    raise DataLoadError("Tabla 'localidades' no encontrada en la base de datos")
        except Exception as e:
            self.log_error("Error verificando base de datos", e)
            raise DataLoadError(f"Error accediendo a la base de datos: {e}")
    
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
                
                estados = []
                for row in cursor.fetchall():
                    estados.append({
                        'clave': row['clave_estado'],
                        'nombre': row['estado']
                    })
                
                self.log_info(f"Estados obtenidos: {len(estados)}")
                return estados
                
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
                
                municipios = []
                for row in cursor.fetchall():
                    municipios.append({
                        'clave_municipio': row['clave_municipio'],
                        'nombre_municipio': row['municipio'],
                        'nombre_estado': row['estado']
                    })
                
                self.log_info(f"Municipios obtenidos para estado {clave_estado}: {len(municipios)}")
                return municipios
                
        except Exception as e:
            self.log_error(f"Error obteniendo municipios para estado {clave_estado}", e)
            raise DataLoadError(f"Error obteniendo municipios: {e}")
    
    def get_nodo_inicial_municipio(self, clave_estado: str, clave_municipio: str) -> Optional[Dict[str, Any]]:
        """Obtener el nodo inicial del municipio (localidad con mayor población)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT clave_estado, estado,
                           clave_municipio, municipio,
                           clave_localidad, localidad,
                           poblacion, latitud, longitud, ambito
                    FROM localidades
                    WHERE clave_estado = ? 
                      AND clave_municipio = ?
                      AND latitud IS NOT NULL 
                      AND longitud IS NOT NULL
                      AND poblacion IS NOT NULL
                    ORDER BY CAST(poblacion AS INTEGER) DESC
                    LIMIT 1
                """, (clave_estado, clave_municipio))
                
                row = cursor.fetchone()
                if row:
                    nodo_inicial = {
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
                    
                    self.log_info(f"Nodo inicial obtenido: {nodo_inicial['nombre']}")
                    return nodo_inicial
                
                return None
                
        except Exception as e:
            self.log_error(f"Error obteniendo nodo inicial para municipio {clave_municipio}", e)
            raise DataLoadError(f"Error obteniendo nodo inicial: {e}")
    
    def get_localidades_municipio(self, clave_estado: str, clave_municipio: str, 
                                 clave_localidad_excluir: str, cantidad: int,
                                 poblacion_minima: int = 20) -> List[Dict[str, Any]]:
        """Obtener localidades del mismo municipio excluyendo el nodo inicial"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT clave_estado, estado,
                           clave_municipio, municipio,
                           clave_localidad, localidad,
                           poblacion, latitud, longitud, ambito
                    FROM localidades
                    WHERE clave_estado = ? 
                      AND clave_municipio = ?
                      AND clave_localidad != ?
                      AND poblacion > ?
                      AND latitud IS NOT NULL 
                      AND longitud IS NOT NULL
                      AND poblacion IS NOT NULL
                    ORDER BY CAST(poblacion AS INTEGER) DESC
                    LIMIT ?
                """, (clave_estado, clave_municipio, clave_localidad_excluir, poblacion_minima, cantidad))
                
                localidades = []
                for row in cursor.fetchall():
                    localidades.append({
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
                    })
                
                self.log_info(f"Localidades secundarias obtenidas para municipio {clave_municipio}: {len(localidades)}")
                return localidades
                
        except Exception as e:
            self.log_error(f"Error obteniendo localidades para municipio {clave_municipio}", e)
            raise DataLoadError(f"Error obteniendo localidades: {e}")
    
    def get_localidad_by_id(self, clave_estado: str, clave_municipio: str, 
                           clave_localidad: str) -> Optional[Dict[str, Any]]:
        """Obtener una localidad específica por sus claves"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT clave_estado, estado,
                           clave_municipio, municipio,
                           clave_localidad, localidad,
                           poblacion, latitud, longitud, ambito
                    FROM localidades
                    WHERE clave_estado = ? AND clave_municipio = ? AND clave_localidad = ?
                """, (clave_estado, clave_municipio, clave_localidad))
                
                row = cursor.fetchone()
                if row and row['latitud'] and row['longitud']:
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
            self.log_error(f"Error obteniendo localidad {clave_localidad}", e)
            raise DataLoadError(f"Error obteniendo localidad: {e}")
    
    def search_localidades(self, nombre: str, clave_estado: str = None, 
                          limite: int = 50) -> List[Dict[str, Any]]:
        """Buscar localidades por nombre"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if clave_estado:
                    cursor.execute("""
                        SELECT clave_estado, estado,
                               clave_municipio, municipio,
                               clave_localidad, localidad,
                               poblacion, latitud, longitud, ambito
                        FROM localidades
                        WHERE clave_estado = ?
                          AND (localidad LIKE ? OR municipio LIKE ?)
                          AND latitud IS NOT NULL 
                          AND longitud IS NOT NULL
                        ORDER BY poblacion DESC
                        LIMIT ?
                    """, (clave_estado, f"%{nombre}%", f"%{nombre}%", limite))
                else:
                    cursor.execute("""
                        SELECT clave_estado, estado,
                               clave_municipio, municipio,
                               clave_localidad, localidad,
                               poblacion, latitud, longitud, ambito
                        FROM localidades
                        WHERE (localidad LIKE ? OR municipio LIKE ?)
                          AND latitud IS NOT NULL 
                          AND longitud IS NOT NULL
                        ORDER BY poblacion DESC
                        LIMIT ?
                    """, (f"%{nombre}%", f"%{nombre}%", limite))
                
                localidades = []
                for row in cursor.fetchall():
                    localidades.append({
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
                    })
                
                return localidades
                
        except Exception as e:
            self.log_error(f"Error buscando localidades con nombre '{nombre}'", e)
            raise DataLoadError(f"Error buscando localidades: {e}")
    
    def get_table_info(self) -> Dict[str, Any]:
        """Obtener información sobre la estructura de la tabla"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener información de columnas
                cursor.execute("PRAGMA table_info(localidades)")
                columns = cursor.fetchall()
                
                # Obtener conteo total
                cursor.execute("SELECT COUNT(*) as total FROM localidades")
                total_rows = cursor.fetchone()['total']
                
                # Obtener conteo por ámbito
                cursor.execute("SELECT ambito, COUNT(*) as count FROM localidades GROUP BY ambito")
                ambito_counts = cursor.fetchall()
                
                # Obtener muestra de datos
                cursor.execute("SELECT * FROM localidades LIMIT 3")
                sample_data = cursor.fetchall()
                
                return {
                    'columns': [dict(col) for col in columns],
                    'total_rows': total_rows,
                    'ambito_counts': [dict(row) for row in ambito_counts],
                    'sample_data': [dict(row) for row in sample_data]
                }
                
        except Exception as e:
            self.log_error("Error obteniendo información de tabla", e)
            raise DataLoadError(f"Error obteniendo información de tabla: {e}")