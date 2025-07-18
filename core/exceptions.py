"""
Excepciones personalizadas del sistema
"""

class EmergenLogisticsError(Exception):
    """Excepción base del sistema"""
    pass

class ValidationError(EmergenLogisticsError):
    """Error de validación de datos"""
    pass

class RouteCalculationError(EmergenLogisticsError):
    """Error en cálculo de rutas"""
    pass

class DataLoadError(EmergenLogisticsError):
    """Error al cargar datos"""
    pass

class ScenarioGenerationError(EmergenLogisticsError):
    """Error al generar escenario"""
    pass

class GeneticAlgorithmError(EmergenLogisticsError):
    """Error en algoritmo genético"""
    pass