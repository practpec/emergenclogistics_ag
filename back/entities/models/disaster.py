from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class DisasterPriority:
    """Prioridad de insumo para un desastre"""
    categoria: str
    nivel: str  # alta, media, baja
    
    @property
    def priority_weight(self) -> float:
        """Peso numérico de la prioridad"""
        weights = {'alta': 3.0, 'media': 2.0, 'baja': 1.0}
        return weights.get(self.nivel, 1.0)

@dataclass
class Disaster:
    """Modelo de desastre"""
    tipo: str
    prioridad: List[DisasterPriority]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'tipo': self.tipo,
            'prioridad': [
                {'categoria': p.categoria, 'nivel': p.nivel}
                for p in self.prioridad
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Disaster':
        """Crear desde diccionario"""
        priorities = [
            DisasterPriority(categoria=p['categoria'], nivel=p['nivel'])
            for p in data['prioridad']
        ]
        return cls(tipo=data['tipo'], prioridad=priorities)
    
    def get_priority_for_category(self, categoria: str) -> DisasterPriority:
        """Obtener prioridad para una categoría específica"""
        for priority in self.prioridad:
            if priority.categoria == categoria:
                return priority
        return DisasterPriority(categoria=categoria, nivel='baja')
    
    def get_priority_weight(self, categoria: str) -> float:
        """Obtener peso de prioridad para una categoría"""
        priority = self.get_priority_for_category(categoria)
        return priority.priority_weight

@dataclass
class SupplyCategory:
    """Categoría de insumos"""
    categoria: str
    subcategorias: List[str]
    peso_unitario_kg: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'categoria': self.categoria,
            'subcategorias': self.subcategorias,
            'peso_unitario_kg': self.peso_unitario_kg
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupplyCategory':
        """Crear desde diccionario"""
        return cls(
            categoria=data['categoria'],
            subcategorias=data.get('subcategorias', []),
            peso_unitario_kg=data['peso_unitario_kg']
        )
    
    def calculate_weight(self, quantity: int) -> float:
        """Calcular peso total para una cantidad"""
        return quantity * self.peso_unitario_kg