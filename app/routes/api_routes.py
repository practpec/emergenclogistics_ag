from flask import Blueprint, jsonify, request
from core.exceptions import EmergencLogisticsException
from services.data.data_loader import DataLoader
from utils.helpers import ResponseFormatter

api_bp = Blueprint('api', __name__)
data_loader = DataLoader()

@api_bp.route('/status')
def get_status():
    """Verificar estado del servidor"""
    return jsonify(ResponseFormatter.success({
        'status': 'online',
        'message': 'Servidor funcionando correctamente'
    }))

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
                'max_vehicles': config_manager.get('system', 'max_vehicles')
            },
            'geo': config_manager.get('geo')
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