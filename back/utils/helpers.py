import json
from typing import Any, Dict, List
from datetime import datetime

def format_distance(distance_meters: float) -> str:
    """Formatear distancia en metros a texto legible"""
    if distance_meters < 1000:
        return f"{distance_meters:.0f} m"
    else:
        return f"{distance_meters/1000:.1f} km"

def format_weight(weight_kg: float) -> str:
    """Formatear peso en kilogramos"""
    if weight_kg < 1000:
        return f"{weight_kg:.1f} kg"
    else:
        return f"{weight_kg/1000:.1f} t"

def format_time(time_hours: float) -> str:
    """Formatear tiempo en horas a texto legible"""
    if time_hours < 1:
        minutes = int(time_hours * 60)
        return f"{minutes} min"
    else:
        hours = int(time_hours)
        minutes = int((time_hours - hours) * 60)
        if minutes > 0:
            return f"{hours}h {minutes}min"
        else:
            return f"{hours}h"

def calculate_percentage(part: float, total: float) -> float:
    """Calcular porcentaje con manejo de división por cero"""
    if total == 0:
        return 0.0
    return (part / total) * 100

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """División segura con valor por defecto"""
    if denominator == 0:
        return default
    return numerator / denominator

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncar texto a longitud máxima"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def validate_json_structure(data: Dict, required_keys: List[str]) -> bool:
    """Validar que un diccionario tenga las claves requeridas"""
    return all(key in data for key in required_keys)

def merge_dicts(*dicts: Dict) -> Dict:
    """Combinar múltiples diccionarios"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

def generate_unique_id(prefix: str = "") -> str:
    """Generar ID único basado en timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return f"{prefix}{timestamp}" if prefix else timestamp

def round_coordinates(lat: float, lng: float, precision: int = 4) -> tuple:
    """Redondear coordenadas a precisión específica"""
    return round(lat, precision), round(lng, precision)

def normalize_string(text: str) -> str:
    """Normalizar string (lowercase, sin espacios extra)"""
    return text.lower().strip()

def is_valid_coordinate(lat: float, lng: float) -> bool:
    """Validar que las coordenadas estén en rangos válidos"""
    return -90 <= lat <= 90 and -180 <= lng <= 180

def group_by_key(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """Agrupar lista de diccionarios por una clave específica"""
    groups = {}
    for item in items:
        group_key = item.get(key)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    return groups

def filter_dict_keys(data: Dict, allowed_keys: List[str]) -> Dict:
    """Filtrar diccionario manteniendo solo claves permitidas"""
    return {k: v for k, v in data.items() if k in allowed_keys}

def deep_get(dictionary: Dict, keys: str, default=None) -> Any:
    """Obtener valor anidado usando notación de punto"""
    keys_list = keys.split('.')
    value = dictionary
    
    try:
        for key in keys_list:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

class ResponseFormatter:
    """Clase helper para formatear respuestas de API"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Operación exitosa") -> Dict:
        """Formatear respuesta exitosa"""
        response = {"success": True, "message": message}
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def error(message: str, error_code: str = None, details: Dict = None) -> Dict:
        """Formatear respuesta de error"""
        response = {"success": False, "message": message}
        if error_code:
            response["error_code"] = error_code
        if details:
            response["details"] = details
        return response