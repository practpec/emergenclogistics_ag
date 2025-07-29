from typing import Dict, List, Any, Tuple
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
        """Procesar datos del frontend"""
        try:
            rutas_raw = datos_frontend.get('rutas', [])
            rutas = self._procesar_rutas(rutas_raw)
            
            scenario_config = datos_frontend.get('scenario_config', {})
            vehiculos = self._procesar_vehiculos(scenario_config.get('vehiculos_disponibles', []))
            tipo_desastre_str = scenario_config.get('tipo_desastre', '')
            
            insumos, tipo_desastre = self._obtener_insumos_por_desastre(tipo_desastre_str)
            config_ag = self._procesar_configuracion_ag(scenario_config.get('configuracion', {}))
            
            scenario_data = ScenarioData(
                rutas=rutas,
                vehiculos_disponibles=vehiculos,
                tipo_desastre=tipo_desastre,
                configuracion_ag=config_ag
            )
            
            return scenario_data, insumos
            
        except Exception as e:
            self.log_error("Error procesando datos de entrada", e)
            raise ValidationError(f"Error procesando datos: {e}")
    
    def _procesar_rutas(self, rutas_raw: List[Dict[str, Any]]) -> List[Ruta]:
        """Procesar rutas - solo necesita clave_localidad para obtener población"""
        rutas = []
        
        for ruta_data in rutas_raw:
            try:
                # Solo necesitas la población, nada más
                poblacion = self._obtener_poblacion_localidad(ruta_data)
                estado = EstadoRuta(ruta_data.get('estado', 'cerrada'))
                
                if estado == EstadoRuta.CERRADA:
                    continue
                
                localidad = Localidad(
                    clave_localidad=str(ruta_data.get('clave_localidad', 'unknown')),
                    poblacion=poblacion
                )
                
                ruta = Ruta(
                    id=int(ruta_data['id']),
                    distancia_km=float(ruta_data['distancia_km']),
                    localidad=localidad,
                    estado=estado,
                    vehiculos_permitidos=ruta_data.get('vehiculos_permitidos', [])
                )
                rutas.append(ruta)
                
            except Exception as e:
                self.log_error(f"Error procesando ruta {ruta_data.get('id', 'unknown')}", e)
                continue
        
        return rutas
    
    def _obtener_poblacion_localidad(self, ruta_data: Dict[str, Any]) -> int:
        """Obtener solo la población usando DatabaseService"""
        clave_localidad = ruta_data.get('clave_localidad')
        
        if clave_localidad:
            try:
                localidad_bd = self.db_service.get_localidad_by_clave(str(clave_localidad))
                if localidad_bd:
                    return int(localidad_bd['poblacion'])
            except Exception as e:
                self.log_error(f"Error obteniendo población para {clave_localidad}", e)
        
        # Fallback
        return 1000
    
    def _procesar_vehiculos(self, vehiculos_raw: List[Dict[str, Any]]) -> List[VehiculoDisponible]:
        """Procesar vehículos usando data_loader"""
        vehiculos_disponibles = []
        vehiculos_db = data_loader.get_vehiculos()
        
        for vehiculo_data in vehiculos_raw:
            try:
                modelo = str(vehiculo_data['modelo'])
                tipo = str(vehiculo_data['tipo'])
                cantidad = int(vehiculo_data['cantidad'])
                
                # Buscar en JSON de vehículos
                vehiculo_info = None
                for v in vehiculos_db:
                    if (v['modelo'].lower() in modelo.lower() or 
                        modelo.lower() in v['modelo'].lower() or
                        v['tipo'].lower() == tipo.lower()):
                        vehiculo_info = v
                        break
                
                if not vehiculo_info:
                    vehiculo_info = {
                        'consumo_litros_km': 0.1,
                        'maximo_peso_ton': 1.5
                    }
                
                vehiculo_base = VehiculoBase(
                    modelo=modelo,
                    tipo=tipo,
                    consumo_litros_km=float(vehiculo_info['consumo_litros_km']),
                    maximo_peso_ton=float(vehiculo_info['maximo_peso_ton'])
                )
                
                vehiculos_disponibles.append(VehiculoDisponible(
                    vehiculo=vehiculo_base,
                    cantidad=cantidad
                ))
                
            except Exception as e:
                self.log_error(f"Error procesando vehículo {vehiculo_data}", e)
                continue
        
        return vehiculos_disponibles
    
    def _procesar_configuracion_ag(self, config_raw: Dict[str, Any]) -> ConfiguracionAG:
        """Procesar configuración del AG"""
        return ConfiguracionAG(
            poblacion_size=int(config_raw.get('poblacion_size', 50)),
            generaciones=int(config_raw.get('generaciones', 100)),
            prob_cruza=float(config_raw.get('prob_cruza', 0.8)),
            prob_mutacion=float(config_raw.get('prob_mutacion', 0.1)),
            elitismo_rate=float(config_raw.get('elitismo_rate', 0.1))
        )
    
    def _obtener_insumos_por_desastre(self, tipo_desastre_str: str) -> Tuple[List[Insumo], TipoDesastre]:
        """Obtener insumos usando data_loader"""
        try:
            desastre_data = data_loader.get_desastre_by_tipo(tipo_desastre_str)
            insumos_data = data_loader.get_categorias_insumos()
            
            # Crear prioridades del desastre
            prioridades = []
            for prioridad_data in desastre_data['prioridades']:
                prioridad = PrioridadCategoria(
                    categoria=str(prioridad_data['categoria']),
                    nivel=NivelPrioridad(prioridad_data['nivel'])
                )
                prioridades.append(prioridad)
            
            tipo_desastre = TipoDesastre(
                tipo=str(desastre_data['tipo']),
                prioridades=prioridades
            )
            
            # Crear insumos solo para categorías del desastre
            insumos_prioritarios = []
            categorias_prioritarias = {p.categoria for p in prioridades}
            
            for insumo_data in insumos_data:
                categoria = str(insumo_data['categoria'])
                if categoria in categorias_prioritarias:
                    insumo = Insumo(
                        id=int(insumo_data['id_insumo']),
                        nombre=str(insumo_data['nombre']),
                        categoria=categoria,
                        peso_kg=float(insumo_data['peso_kg'])
                    )
                    insumos_prioritarios.append(insumo)
            
            return insumos_prioritarios, tipo_desastre
            
        except Exception as e:
            self.log_error(f"Error obteniendo insumos para {tipo_desastre_str}", e)
            return [], TipoDesastre(tipo=tipo_desastre_str, prioridades=[])