import random
from typing import List, Tuple
from .models import Individual, VehicleAssignment

class CrossoverOperator:
    """Paso 4: Cruza (cruce)"""
    
    def __init__(self, num_vehiculos: int):
        self.num_vehiculos = num_vehiculos

    def cruza_puntos_aleatorios(self, parejas: List[Tuple[Individual, Individual]], 
                               prob_cruza: float) -> List[Individual]:
        """Cruza con cantidad aleatoria de puntos en posiciones aleatorias"""
        descendencia = []
        
        for padre1, padre2 in parejas:
            if random.random() < prob_cruza:
                # Crear hijos copiando padres
                hijo1_vehiculos = []
                hijo2_vehiculos = []
                
                for i in range(self.num_vehiculos):
                    # Cruza para asignación destino-ruta e insumos por separado
                    if random.random() < 0.5:
                        # Destino-ruta del padre1, insumos pueden cruzarse
                        hijo1_vehiculos.append(VehicleAssignment(
                            vehiculo_id=i,
                            id_destino_ruta=padre1.vehiculos[i].id_destino_ruta,
                            insumos=self._cruzar_insumos(padre1.vehiculos[i].insumos, padre2.vehiculos[i].insumos)
                        ))
                        hijo2_vehiculos.append(VehicleAssignment(
                            vehiculo_id=i,
                            id_destino_ruta=padre2.vehiculos[i].id_destino_ruta,
                            insumos=self._cruzar_insumos(padre2.vehiculos[i].insumos, padre1.vehiculos[i].insumos)
                        ))
                    else:
                        # Intercambiar completamente
                        hijo1_vehiculos.append(VehicleAssignment(
                            vehiculo_id=i,
                            id_destino_ruta=padre2.vehiculos[i].id_destino_ruta,
                            insumos=padre2.vehiculos[i].insumos.copy()
                        ))
                        hijo2_vehiculos.append(VehicleAssignment(
                            vehiculo_id=i,
                            id_destino_ruta=padre1.vehiculos[i].id_destino_ruta,
                            insumos=padre1.vehiculos[i].insumos.copy()
                        ))
                
                descendencia.extend([
                    Individual(vehiculos=hijo1_vehiculos),
                    Individual(vehiculos=hijo2_vehiculos)
                ])
            else:
                # Copiar padres sin cruza
                descendencia.extend([
                    Individual(vehiculos=[VehicleAssignment(v.vehiculo_id, v.id_destino_ruta, v.insumos.copy()) for v in padre1.vehiculos]),
                    Individual(vehiculos=[VehicleAssignment(v.vehiculo_id, v.id_destino_ruta, v.insumos.copy()) for v in padre2.vehiculos])
                ])
        
        return descendencia

    def _cruzar_insumos(self, insumos1: List[int], insumos2: List[int]) -> List[int]:
        """Cruza de insumos con puntos aleatorios"""
        if len(insumos1) != len(insumos2):
            return insumos1.copy()
        
        num_puntos = random.randint(1, min(3, len(insumos1) - 1))
        puntos = sorted(random.sample(range(1, len(insumos1)), num_puntos))
        
        resultado = insumos1.copy()
        intercambiar = True
        inicio = 0
        
        for punto in puntos + [len(insumos1)]:
            if intercambiar:
                resultado[inicio:punto] = insumos2[inicio:punto]
            intercambiar = not intercambiar
            inicio = punto
        
        return resultado