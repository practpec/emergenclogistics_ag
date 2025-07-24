from flask import Blueprint, request, jsonify, current_app
from core.exceptions import ValidationError, GeneticAlgorithmError
from services.algorithms.main.genetic_algorithm import LogisticsGeneticAlgorithm
from utils.helpers import ResponseFormatter

ag_bp = Blueprint('ag', __name__)

@ag_bp.route('/run-scenario', methods=['POST'])
def run_genetic_algorithm():
    """Ejecutar algoritmo genético para optimización logística"""
    try:
        data = request.get_json()
        
        # Debug: Mostrar qué se está recibiendo
        current_app.logger.info("=== DATOS RECIBIDOS EN AG ===")
        current_app.logger.info(f"Tipo de datos: {type(data)}")
        current_app.logger.info(f"Es None: {data is None}")
        
        if data:
            current_app.logger.info(f"Claves recibidas: {list(data.keys())}")
            current_app.logger.info(f"Contenido completo: {data}")
        else:
            current_app.logger.info("No se recibieron datos JSON")
        current_app.logger.info("=========================")
        
        if not data:
            raise ValidationError("No se recibieron datos")
        
        # Validación según estructura real recibida
        required_keys = ['map_data', 'scenario_config']
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValidationError(f"Faltan campos requeridos: {missing_keys}")
        
        # Validar map_data
        map_data = data['map_data']
        if not map_data.get('rutas_data') or not map_data.get('nodos_secundarios'):
            raise ValidationError("map_data requiere rutas_data y nodos_secundarios")
        
        # Validar scenario_config
        scenario_config = data['scenario_config']
        if not scenario_config.get('vehiculos_disponibles') or not scenario_config.get('tipo_desastre'):
            raise ValidationError("scenario_config requiere vehiculos_disponibles y tipo_desastre")
        
        # Extraer parámetros del AG desde scenario_config
        parametros_ag = scenario_config.get('ag_params')
        
        current_app.logger.info(f"Ejecutando AG con {len(scenario_config['vehiculos_disponibles'])} vehículos y {len(map_data['rutas_data'])} destinos")
        
        # Crear y ejecutar algoritmo genético
        ag = LogisticsGeneticAlgorithm(data, parametros_ag)
        resultado = ag.ejecutar()
        
        return jsonify(ResponseFormatter.success(
            data=resultado,
            message="Algoritmo genético ejecutado exitosamente"
        ))
        
    except ValidationError as e:
        current_app.logger.error(f"Error de validación en AG: {e}")
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="VALIDATION_ERROR"
        )), 400
        
    except GeneticAlgorithmError as e:
        current_app.logger.error(f"Error en algoritmo genético: {e}")
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="GENETIC_ALGORITHM_ERROR"
        )), 500
        
    except Exception as e:
        current_app.logger.error(f"Error inesperado en AG: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error interno del servidor",
            error_code="INTERNAL_ERROR"
        )), 500

@ag_bp.errorhandler(404)
def not_found(error):
    """Manejar errores 404 en rutas AG"""
    return jsonify(ResponseFormatter.error(
        message="Endpoint del algoritmo genético no encontrado",
        error_code="AG_NOT_FOUND"
    )), 404

@ag_bp.errorhandler(500)
def internal_error(error):
    """Manejar errores 500 en rutas AG"""
    return jsonify(ResponseFormatter.error(
        message="Error interno del algoritmo genético",
        error_code="AG_INTERNAL_ERROR"
    )), 500