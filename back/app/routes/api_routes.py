from flask import Blueprint, jsonify, request
from core.exceptions import EmergencLogisticsException
from services.data.data_loader import DataLoader
from services.geo.geo_service import GeoService
from utils.helpers import ResponseFormatter

api_bp = Blueprint('api', __name__)
data_loader = DataLoader()
geo_service = GeoService()

@api_bp.route('/status')
def get_status():
    """Verificar estado del servidor y base de datos"""
    try:
        # Verificar acceso a base de datos
        estados = geo_service.get_estados()
        
        return jsonify(ResponseFormatter.success({
            'status': 'online',
            'database': 'connected',
            'estados_disponibles': len(estados),
            'message': 'Servidor y base de datos funcionando correctamente'
        }))
    except Exception as e:
        return jsonify(ResponseFormatter.error(
            message=f"Error en servidor o base de datos: {str(e)}",
            error_code="SERVER_ERROR"
        )), 500

@api_bp.route('/entities/<entity_type>')
def get_entity_data(entity_type):
    """Obtener datos específicos de una entidad"""
    try:
        entities = data_loader.get_all_entities()
        
        if entity_type in entities:
            return jsonify(ResponseFormatter.success(
                data=entities[entity_type],
                message=f"Datos de {entity_type} obtenidos correctamente"
            ))
        else:
            return jsonify(ResponseFormatter.error(
                message=f"Entidad no encontrada: {entity_type}",
                error_code="ENTITY_NOT_FOUND"
            )), 404
            
    except EmergencLogisticsException as e:
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="DATA_LOAD_ERROR"
        )), 500
    except Exception as e:
        return jsonify(ResponseFormatter.error(
            message="Error interno del servidor",
            error_code="INTERNAL_ERROR",
            details={"error": str(e)}
        )), 500

@api_bp.route('/config')
def get_config():
    """Obtener configuración del sistema"""
    try:
        from utils.config_manager import config_manager
        
        # Solo retornar configuración no sensible
        public_config = {
            'system': {
                'max_destinations': config_manager.get('system', 'max_destinations'),
                'max_vehicles': config_manager.get('system', 'max_vehicles'),
                'using_real_data': True
            },
            'geo': config_manager.get('geo'),
            'database': {
                'type': 'sqlite',
                'source': 'localidades_mexico'
            }
        }
        
        return jsonify(ResponseFormatter.success(
            data=public_config,
            message="Configuración obtenida correctamente"
        ))
        
    except Exception as e:
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo configuración",
            error_code="CONFIG_ERROR"
        )), 500

@api_bp.route('/geo/estados')
def get_geo_estados():
    """Obtener estados con información geográfica"""
    try:
        estados = geo_service.get_estados_completos()
        return jsonify(ResponseFormatter.success(
            data=estados,
            message=f"Estados con datos geográficos: {len(estados)}"
        ))
    except Exception as e:
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo datos geográficos",
            error_code="GEO_ERROR"
        )), 500

@api_bp.route('/geo/coordenadas/<estado>')
def get_coordenadas_estado(estado):
    """Obtener coordenadas principales de un estado"""
    try:
        coordenadas = geo_service.get_coordenadas_estado(estado)
        return jsonify(ResponseFormatter.success(
            data=coordenadas,
            message=f"Coordenadas obtenidas para {estado}"
        ))
    except ValueError as e:
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="ESTADO_NOT_FOUND"
        )), 404
    except Exception as e:
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo coordenadas",
            error_code="GEO_ERROR"
        )), 500

@api_bp.route('/database/info')
def get_database_info():
    """Obtener información sobre la base de datos"""
    try:
        from services.data.database_service import DatabaseService
        db_service = DatabaseService()
        
        # Obtener estadísticas básicas
        estados = db_service.get_estados()
        
        info = {
            'total_estados': len(estados),
            'database_path': db_service.db_path,
            'status': 'connected',
            'sample_estados': estados[:5] if len(estados) > 5 else estados
        }
        
        return jsonify(ResponseFormatter.success(
            data=info,
            message="Información de base de datos obtenida"
        ))
        
    except Exception as e:
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo información de base de datos",
            error_code="DATABASE_ERROR"
        )), 500

@api_bp.errorhandler(404)
def not_found(error):
    """Manejar errores 404 en API"""
    return jsonify(ResponseFormatter.error(
        message="Endpoint no encontrado",
        error_code="NOT_FOUND"
    )), 404

@api_bp.errorhandler(405)
def method_not_allowed(error):
    """Manejar errores 405 en API"""
    return jsonify(ResponseFormatter.error(
        message="Método no permitido",
        error_code="METHOD_NOT_ALLOWED"
    )), 405

@api_bp.errorhandler(500)
def internal_error(error):
    """Manejar errores 500 en API"""
    return jsonify(ResponseFormatter.error(
        message="Error interno del servidor",
        error_code="INTERNAL_ERROR"
    )), 500