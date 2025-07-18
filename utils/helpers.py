"""
Funciones auxiliares generales
"""
import json
import os
from typing import Dict, Any
from core.exceptions import DataLoadError

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Cargar archivo JSON con manejo de errores"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise DataLoadError(f"Archivo no encontrado: {file_path}")
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Error al parsear JSON {file_path}: {e}")

def save_json_file(data: Dict[str, Any], file_path: str):
    """Guardar datos en archivo JSON"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise DataLoadError(f"Error al guardar archivo {file_path}: {e}")

def format_distance(distance_m: float) -> str:
    """Formatear distancia en metros a texto legible"""
    if distance_m < 1000:
        return f"{distance_m:.0f} m"
    else:
        return f"{distance_m/1000:.1f} km"

def calculate_vehicle_capacity_kg(capacity_ton: float) -> int:
    """Convertir capacidad de toneladas a kilogramos"""
    return int(capacity_ton * 1000)