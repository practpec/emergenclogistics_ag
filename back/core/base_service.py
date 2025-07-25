import logging
from abc import ABC
from typing import Dict, Any, Optional

class BaseService(ABC):
    """Clase base para servicios del sistema"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Log error crítico únicamente"""
        if exception:
            self.logger.error(f"[ERROR] {message}", exc_info=exception)
        else:
            self.logger.error(f"[ERROR] {message}")

class CacheableService(BaseService):
    """Servicio con cache básico"""
    
    def __init__(self):
        super().__init__()
        self._cache: Dict[str, Any] = {}
        self.max_cache_size = 50
    
    def get_from_cache(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def set_cache(self, key: str, value: Any) -> None:
        if len(self._cache) >= self.max_cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[key] = value