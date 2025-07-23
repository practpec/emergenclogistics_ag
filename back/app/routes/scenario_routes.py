from flask import Blueprint, jsonify, current_app
from core.exceptions import DataLoadError
from utils.helpers import ResponseFormatter

scenario_bp = Blueprint('scenario', __name__)

@scenario_bp.route('/vehicles')
def get_vehicles():
    """Obtener todos los vehículos disponibles"""
    try:
        from services.data.static_data_service import StaticDataService
        static_data_service = StaticDataService()
        
        vehicles = static_data_service.get_all_vehicles()
        vehicles_data = [vehicle.to_dict() for vehicle in vehicles]
        
        return jsonify(ResponseFormatter.success(
            data=vehicles_data,
            message=f"Vehículos obtenidos: {len(vehicles_data)}"
        ))
        
    except DataLoadError as e:
        current_app.logger.error(f"Error cargando vehículos: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error cargando vehículos",
            error_code="VEHICLES_LOAD_ERROR"
        )), 500
    except Exception as e:
        current_app.logger.error(f"Error obteniendo vehículos: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo vehículos",
            error_code="VEHICLES_ERROR"
        )), 500

@scenario_bp.route('/disasters')
def get_disasters():
    """Obtener todos los tipos de desastre disponibles"""
    try:
        from services.data.static_data_service import StaticDataService
        static_data_service = StaticDataService()
        
        disasters = static_data_service.get_all_disasters()
        disasters_data = [disaster.to_dict() for disaster in disasters]
        
        return jsonify(ResponseFormatter.success(
            data=disasters_data,
            message=f"Desastres obtenidos: {len(disasters_data)}"
        ))
        
    except DataLoadError as e:
        current_app.logger.error(f"Error cargando desastres: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error cargando desastres",
            error_code="DISASTERS_LOAD_ERROR"
        )), 500
    except Exception as e:
        current_app.logger.error(f"Error obteniendo desastres: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo desastres",
            error_code="DISASTERS_ERROR"
        )), 500