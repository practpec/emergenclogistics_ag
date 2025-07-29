from flask import Blueprint, request, jsonify, current_app
from core.exceptions import ValidationError, GeneticAlgorithmError
from core.helpers import ResponseFormatter
from services.algorithms.main.genetic_algorithm import LogisticsGeneticAlgorithm

ag_bp = Blueprint('ag', __name__)

@ag_bp.route('/run-scenario', methods=['POST'])
def run_genetic_algorithm():
    """Ejecutar algoritmo genético para optimización logística"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("No se recibieron datos")
        
        if 'datos_actuales_frontend_a_backend' not in data:
            raise ValidationError("Estructura de datos incorrecta")
        
        frontend_data = data['datos_actuales_frontend_a_backend']
        
        required_keys = ['map_data', 'scenario_config']
        missing_keys = [key for key in required_keys if key not in frontend_data]
        if missing_keys:
            raise ValidationError(f"Faltan campos requeridos: {missing_keys}")
        
        map_data = frontend_data['map_data']
        if not map_data.get('rutas_data'):
            raise ValidationError("map_data requiere rutas_data")
        
        scenario_config = frontend_data['scenario_config']
        if not scenario_config.get('vehiculos_disponibles') or not scenario_config.get('tipo_desastre'):
            raise ValidationError("scenario_config requiere vehiculos_disponibles y tipo_desastre")
        
        parametros_ag = scenario_config.get('configuracion', {})
        
        current_app.logger.info(f"Ejecutando AG con {len(scenario_config['vehiculos_disponibles'])} vehículos y {len(map_data['rutas_data'])} rutas")
        
        ag = LogisticsGeneticAlgorithm(frontend_data, parametros_ag)
        resultado = ag.ejecutar()
        
        return jsonify(ResponseFormatter.success(
            data=resultado,
            message="Algoritmo genético ejecutado exitosamente"
        ))
        
    except ValidationError as e:
        current_app.logger.error(f"Error de validación AG: {e}")
        return jsonify(ResponseFormatter.error(str(e), "VALIDATION_ERROR")), 400
        
    except GeneticAlgorithmError as e:
        current_app.logger.error(f"Error AG: {e}")
        return jsonify(ResponseFormatter.error(str(e), "GENETIC_ALGORITHM_ERROR")), 500
        
    except Exception as e:
        current_app.logger.error(f"Error AG inesperado: {e}")
        return jsonify(ResponseFormatter.error("Error interno del servidor", "INTERNAL_ERROR")), 500