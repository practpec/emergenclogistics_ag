from typing import Dict, List, Any
from .exceptions import ValidationError

class BaseValidator:
    """Validador base para datos del sistema"""
    
    @staticmethod
    def validate_coordinates(lat: Any, lng: Any) -> bool:
        """Validar coordenadas geográficas"""
        # Verificar que no sean None
        if lat is None or lng is None:
            raise ValidationError("Las coordenadas no pueden ser nulas")
        
        # Convertir a float
        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            raise ValidationError(f"Coordenadas inválidas: lat={lat}, lng={lng}")
        
        if not (-90 <= lat <= 90):
            raise ValidationError(f"Latitud inválida: {lat}")
        if not (-180 <= lng <= 180):
            raise ValidationError(f"Longitud inválida: {lng}")
        return True
    
    @staticmethod
    def validate_positive_number(value: Any, field_name: str) -> float:
        """Validar que un valor sea un número positivo"""
        try:
            num = float(value)
            if num <= 0:
                raise ValidationError(f"{field_name} debe ser positivo: {value}")
            return num
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} debe ser un número válido: {value}")
    
    @staticmethod
    def validate_integer_range(value: Any, min_val: int, max_val: int, field_name: str) -> int:
        """Validar que un entero esté en un rango específico"""
        try:
            num = int(value)
            if not (min_val <= num <= max_val):
                raise ValidationError(f"{field_name} debe estar entre {min_val} y {max_val}: {value}")
            return num
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} debe ser un entero válido: {value}")

class ScenarioValidator(BaseValidator):
    """Validador específico para escenarios"""
    
    @classmethod
    def validate_scenario_data(cls, data: Dict[str, Any]) -> None:
        """Validar datos de escenario completo"""
        if not data.get('tipo_desastre'):
            raise ValidationError("Tipo de desastre es requerido")
        
        if not data.get('vehiculos'):
            raise ValidationError("Lista de vehículos es requerida")
        
        cls.validate_vehicles_list(data['vehiculos'])
    
    @classmethod
    def validate_vehicles_list(cls, vehicles: List[Dict]) -> None:
        """Validar lista de vehículos"""
        if not isinstance(vehicles, list):
            raise ValidationError("Vehículos debe ser una lista")
        
        if len(vehicles) == 0:
            raise ValidationError("Debe haber al menos un vehículo")
        
        for i, vehicle in enumerate(vehicles):
            if not vehicle.get('tipo'):
                raise ValidationError(f"Vehículo {i+1} requiere tipo")

class RouteValidator(BaseValidator):
    """Validador específico para rutas"""
    
    @classmethod
    def validate_route_data(cls, data: Dict[str, Any]) -> None:
        """Validar datos de ruta"""
        # Esta validación se usa para datos de entrada del frontend
        # que tiene una estructura diferente
        pass
    
    @classmethod
    def validate_route_request(cls, estado: str, n_nodos: int) -> None:
        """Validar petición de generación de rutas"""
        if not estado:
            raise ValidationError("Estado es requerido")
        
        if not isinstance(n_nodos, int) or n_nodos < 1 or n_nodos > 15:
            raise ValidationError("Número de nodos debe estar entre 1 y 15")