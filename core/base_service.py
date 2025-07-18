import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseService(ABC):
    """Clase base para todos los servicios del sistema"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs) -> None:
        """Log información"""
        if kwargs:
            message = f"{message} - {kwargs}"
        self.logger.info(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None, **kwargs) -> None:
        """Log error"""
        if kwargs:
            message = f"{message} - {kwargs}"
        if exception:
            self.logger.error(message, exc_info=exception)
        else:
            self.logger.error(message)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning"""
        if kwargs:
            message = f"{message} - {kwargs}"
        self.logger.warning(message)

class CacheableService(BaseService):
    """Servicio con capacidades de cache"""
    
    def __init__(self):
        super().__init__()
        self._cache: Dict[str, Any] = {}
        self._cache_size = 0
        self.max_cache_size = 100
    
    def get_from_cache(self, key: str) -> Optional[Any]:
        """Obtener elemento del cache"""
        return self._cache.get(key)
    
    def set_cache(self, key: str, value: Any) -> None:
        """Guardar elemento en cache"""
        if self._cache_size >= self.max_cache_size:
            # Remover el primer elemento (FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._cache_size -= 1
        
        self._cache[key] = value
        self._cache_size += 1
    
    def clear_cache(self) -> None:
        """Limpiar cache"""
        self._cache.clear()
        self._cache_size = 0