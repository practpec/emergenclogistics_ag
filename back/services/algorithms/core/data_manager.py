from typing import Dict, Any, List, Tuple
from core.base_service import BaseService
from core.exceptions import ValidationError
from services.data.data_loader import data_loader
from services.data.database_service import DatabaseService
from ..models import *

class DataManager(BaseService):
    """Gestor de datos para el algoritmo genético"""
    
    def __init__(self):
        super().__init__()
        self.db_service = DatabaseService()
    
    def procesar_datos_entrada(self, datos_frontend: Dict[str, Any]) -> Tuple[ScenarioData, List[Insumo]]:
        try:
            map_data = datos_frontend.get('map_data', {})
            scenario_config = datos_frontend.get('scenario_config', {})
            
            rutas = self._procesar_rutas(map_data.get('rutas_data', []))
            
            vehiculos_disponibles = self._procesar_vehiculos_disponibles(
                scenario_config.get('vehiculos_disponibles', [])
            )
            
            tipo_desastre_str = scenario_config.get('tipo_desastre', 'terremoto')
            tipo_desastre = self._procesar_tipo_desastre(tipo_desastre_str)
            
            config_ag = self._procesar_configuracion_ag(
                scenario_config.get('configuracion', {})
            )
            
            scenario_data = ScenarioData(
                rutas=rutas,
                vehiculos_disponibles=vehiculos_disponibles,
                tipo_desastre=tipo_desastre,
                configuracion_ag=config_ag
            )
            
            insumos = self._cargar_insumos()
            
            return scenario_data, insumos
            
        except Exception as e:
            self.log_error("Error procesando datos de entrada", e)
            raise ValidationError(f"Error procesando datos: {e}")
    
    def _procesar_rutas(self, rutas_data: List[Dict[str, Any]]) -> List[Ruta]:
        """Procesar rutas del frontend"""
        rutas = []
        
        for ruta_data in rutas_data:
            try:
                clave_localidad = str(ruta_data.get('clave_localidad', ''))
                localidad_info = self.db_service.get_localidad_by_clave(clave_localidad)
                
                if localidad_info:
                    poblacion = localidad_info.get('poblacion', 1000)
                else:
                    poblacion = 1000
                
                localidad = Localidad(
                    clave_localidad=clave_localidad,
                    poblacion=poblacion
                )
                
                estado_str = ruta_data.get('estado', 'abierta').lower()
                estado = EstadoRuta.ABIERTA if estado_str == 'abierta' else EstadoRuta.CERRADA
                
                ruta = Ruta(
                    id=ruta_data.get('id', len(rutas) + 1),
                    distancia_km=float(ruta_data.get('distancia_km', 10.0)),
                    localidad=localidad,
                    estado=estado,
                    vehiculos_permitidos=ruta_data.get('vehiculos_permitidos', [])
                )
                
                rutas.append(ruta)
                
            except Exception as e:
                self.log_error(f"Error procesando ruta: {ruta_data}", e)
                continue
        
        return rutas
    
    def _procesar_vehiculos_disponibles(self, vehiculos_data: List[Dict[str, Any]]) -> List[VehiculoDisponible]:
        vehiculos_disponibles = []
        vehiculos_db = data_loader.get_vehiculos()
        
        for vehiculo_data in vehiculos_data:
            try:
                modelo = vehiculo_data.get('modelo', '')
                cantidad = vehiculo_data.get('cantidad', 1)
                
                vehiculo_info = None
                for v in vehiculos_db:
                    if modelo in v['modelo'] or v['modelo'] in modelo:
                        vehiculo_info = v
                        break
                
                if not vehiculo_info:
                    self.log_error(f"Vehículo no encontrado: {modelo}", None)
                    continue
                
                vehiculo_base = VehiculoBase(
                    modelo=vehiculo_info['modelo'],
                    tipo=vehiculo_info['tipo'],
                    consumo_litros_km=vehiculo_info['consumo_litros_km'],
                    maximo_peso_ton=vehiculo_info['maximo_peso_ton']
                )
                
                vehiculo_disponible = VehiculoDisponible(
                    vehiculo=vehiculo_base,
                    cantidad=cantidad
                )
                
                vehiculos_disponibles.append(vehiculo_disponible)
                
            except Exception as e:
                self.log_error(f"Error procesando vehículo: {vehiculo_data}", e)
                continue
        
        return vehiculos_disponibles
    
    def _procesar_tipo_desastre(self, tipo_desastre_str: str) -> TipoDesastre:
        try:
            desastre_info = data_loader.get_desastre_by_tipo(tipo_desastre_str)
            
            prioridades = []
            for prioridad_data in desastre_info.get('prioridades', []):
                categoria = prioridad_data.get('categoria', '')
                nivel_str = prioridad_data.get('nivel', 'baja').lower()
                
                if nivel_str == 'alta':
                    nivel = NivelPrioridad.ALTA
                elif nivel_str == 'media':
                    nivel = NivelPrioridad.MEDIA
                else:
                    nivel = NivelPrioridad.BAJA
                
                prioridad = PrioridadCategoria(
                    categoria=categoria,
                    nivel=nivel
                )
                prioridades.append(prioridad)
            
            return TipoDesastre(
                tipo=tipo_desastre_str,
                prioridades=prioridades
            )
            
        except Exception as e:
            self.log_error(f"Error procesando tipo de desastre: {tipo_desastre_str}", e)
            return TipoDesastre(
                tipo=tipo_desastre_str,
                prioridades=[
                    PrioridadCategoria(categoria="Alimentación básica", nivel=NivelPrioridad.ALTA),
                    PrioridadCategoria(categoria="Agua", nivel=NivelPrioridad.ALTA)
                ]
            )
    
    def _procesar_configuracion_ag(self, config_data: Dict[str, Any]) -> ConfiguracionAG:
        return ConfiguracionAG(
            poblacion_size=config_data.get('poblacion_size', 50),
            generaciones=config_data.get('generaciones', 100),
            prob_cruza=config_data.get('prob_cruza', 0.8),
            prob_mutacion=config_data.get('prob_mutacion', 0.15),
            elitismo_rate=config_data.get('elitismo_rate', 0.1)
        )
    
    def _cargar_insumos(self) -> List[Insumo]:
        try:
            insumos_data = data_loader.get_categorias_insumos()
            insumos = []
            
            for insumo_data in insumos_data:
                insumo = Insumo(
                    id=insumo_data['id_insumo'],
                    nombre=insumo_data['nombre'],
                    categoria=insumo_data['categoria'],
                    peso_kg=insumo_data['peso_kg']
                )
                insumos.append(insumo)
            
            return insumos
            
        except Exception as e:
            self.log_error("Error cargando insumos", e)
            return []