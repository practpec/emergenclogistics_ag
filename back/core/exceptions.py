class EmergencLogisticsException(Exception):
    """Excepción base del sistema"""
    pass

class ValidationError(EmergencLogisticsException):
    """Error de validación de datos"""
    pass

class RouteCalculationError(EmergencLogisticsException):
    """Error al calcular rutas"""
    pass

class GeneticAlgorithmError(EmergencLogisticsException):
    """Error en la ejecución del algoritmo genético"""
    pass

class DataLoadError(EmergencLogisticsException):
    """Error al cargar datos"""
    pass