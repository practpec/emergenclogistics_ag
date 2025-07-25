from typing import Any, Dict

class ResponseFormatter:
    """Formatear respuestas de API"""
    
    @staticmethod
    def success(data: Any = None, message: str = "Operación exitosa") -> Dict:
        response = {"success": True, "message": message}
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def error(message: str, error_code: str = None) -> Dict:
        response = {"success": False, "message": message}
        if error_code:
            response["error_code"] = error_code
        return response

def validate_coordinates(lat: Any, lng: Any) -> bool:
    """Validar coordenadas geográficas"""
    try:
        lat_f = float(lat)
        lng_f = float(lng)
        return -90 <= lat_f <= 90 and -180 <= lng_f <= 180
    except (ValueError, TypeError):
        return False