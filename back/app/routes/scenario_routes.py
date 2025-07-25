from flask import Blueprint, jsonify, current_app
from core.exceptions import DataLoadError
from core.helpers import ResponseFormatter
from services.data.data_loader import data_loader

scenario_bp = Blueprint('scenario', __name__)

@scenario_bp.route('/vehicles')
def get_vehicles():
    """Obtener todos los vehículos disponibles"""
    try:
        vehicles = data_loader.get_vehiculos()
        return jsonify(ResponseFormatter.success(
            data=vehicles,
            message=f"Vehículos obtenidos: {len(vehicles)}"
        ))
        
    except DataLoadError as e:
        current_app.logger.error(f"Error cargando vehículos: {e}")
        return jsonify(ResponseFormatter.error(
            "Error cargando vehículos", "VEHICLES_LOAD_ERROR"
        )), 500
    except Exception as e:
        current_app.logger.error(f"Error obteniendo vehículos: {e}")
        return jsonify(ResponseFormatter.error(
            "Error obteniendo vehículos", "VEHICLES_ERROR"
        )), 500

@scenario_bp.route('/disasters')
def get_disasters():
    """Obtener todos los tipos de desastre disponibles"""
    try:
        disasters = data_loader.get_desastres()
        return jsonify(ResponseFormatter.success(
            data=disasters,
            message=f"Desastres obtenidos: {len(disasters)}"
        ))
        
    except DataLoadError as e:
        current_app.logger.error(f"Error cargando desastres: {e}")
        return jsonify(ResponseFormatter.error(
            "Error cargando desastres", "DISASTERS_LOAD_ERROR"
        )), 500
    except Exception as e:
        current_app.logger.error(f"Error obteniendo desastres: {e}")
        return jsonify(ResponseFormatter.error(
            "Error obteniendo desastres", "DISASTERS_ERROR"
        )), 500

@scenario_bp.route('/supplies')
def get_supplies():
    """Obtener todas las categorías de insumos"""
    try:
        supplies = data_loader.get_categorias_insumos()
        return jsonify(ResponseFormatter.success(
            data=supplies,
            message=f"Insumos obtenidos: {len(supplies)}"
        ))
        
    except DataLoadError as e:
        current_app.logger.error(f"Error cargando insumos: {e}")
        return jsonify(ResponseFormatter.error(
            "Error cargando insumos", "SUPPLIES_LOAD_ERROR"
        )), 500
    except Exception as e:
        current_app.logger.error(f"Error obteniendo insumos: {e}")
        return jsonify(ResponseFormatter.error(
            "Error obteniendo insumos", "SUPPLIES_ERROR"
        )), 500