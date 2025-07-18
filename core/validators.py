"""
Validadores centralizados
"""
from typing import Dict, List, Any
from core.exceptions import ValidationError

class BaseValidator:
    """Validador base"""
    
    @staticmethod
    def validate_required(data: Dict[str, Any], required_fields: List[str]):
        """Validar campos requeridos"""
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValidationError(f"Campos requeridos faltantes: {missing}")
    
    @staticmethod
    def validate_range(value: int, min_val: int, max_val: int, field_name: str):
        """Validar rango numérico"""
        if not min_val <= value <= max_val:
            raise ValidationError(f"{field_name} debe estar entre {min_val} y {max_val}")

class MapValidator(BaseValidator):
    """Validador para datos de mapas"""
    
    @classmethod
    def validate_map_request(cls, data: Dict[str, Any]):
        """Validar solicitud de mapa"""
        cls.validate_required(data, ['estado', 'n_nodos'])
        cls.validate_range(data['n_nodos'], 1, 15, 'n_nodos')

class ScenarioValidator(BaseValidator):
    """Validador para escenarios"""
    
    @classmethod
    def validate_scenario_request(cls, data: Dict[str, Any]):
        """Validar solicitud de escenario"""
        cls.validate_required(data, ['tipo_desastre', 'vehiculos'])
        
        if not data['vehiculos']:
            raise ValidationError("Se requiere al menos un vehículo")
        
        if len(data['vehiculos']) > 10:
            raise ValidationError("Máximo 10 vehículos permitidos")