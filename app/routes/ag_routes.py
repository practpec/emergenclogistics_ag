from flask import Blueprint, request, jsonify, session, current_app
from core.exceptions import EmergencLogisticsException, ValidationError
from core.validators import ScenarioValidator
from services.data.scenario_generator import ScenarioGenerator
from services.genetic_algorithm.ag_service import AGService
from utils.helpers import ResponseFormatter

ag_bp = Blueprint('ag', __name__)

# Servicios
scenario_generator = ScenarioGenerator()
ag_service = AGService()

@ag_bp.route('/create-scenario', methods=['POST'])
def create_scenario():
    """Crear escenario de emergencia basado en datos del mapa"""
    try:
        data = request.get_json()
        
        # Validar datos de entrada
        ScenarioValidator.validate_scenario_data(data)
        
        # Obtener datos del mapa desde la sesión
        mapa_data = session.get('mapa_data')
        if not mapa_data:
            raise ValidationError("No hay datos de mapa disponibles. Genera un mapa primero.")
        
        # Generar escenario completo
        escenario = scenario_generator.generate_scenario(data, mapa_data)
        
        # Guardar escenario en sesión
        session['escenario_actual'] = escenario.to_dict()
        
        return jsonify(ResponseFormatter.success(
            data={'escenario': escenario.to_dict()},
            message="Escenario generado exitosamente"
        ))
        
    except ValidationError as e:
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="VALIDATION_ERROR"
        )), 400
        
    except EmergencLogisticsException as e:
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="SCENARIO_GENERATION_ERROR"
        )), 500
        
    except Exception as e:
        ag_bp.logger.error(f"Error creando escenario: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error interno creando escenario",
            error_code="INTERNAL_ERROR"
        )), 500

@ag_bp.route('/execute', methods=['POST'])
def execute_algorithm():
    """Ejecutar algoritmo genético"""
    try:
        data = request.get_json()
        
        # Obtener escenario desde sesión o datos enviados
        escenario_data = data.get('escenario') or session.get('escenario_actual')
        
        if not escenario_data:
            raise ValidationError("No hay escenario disponible. Crea un escenario primero.")
        
        # Recrear objeto Scenario desde diccionario
        from entities.models.scenario import Scenario
        escenario = Scenario.from_dict(escenario_data)
        
        # Ejecutar algoritmo genético
        resultado = ag_service.execute_genetic_algorithm(escenario)
        
        return jsonify(ResponseFormatter.success(
            data={'resultado': resultado},
            message="Algoritmo genético ejecutado"
        ))
        
    except ValidationError as e:
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="VALIDATION_ERROR"
        )), 400
        
    except EmergencLogisticsException as e:
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="AG_EXECUTION_ERROR"
        )), 500
        
    except Exception as e:
        ag_bp.logger.error(f"Error ejecutando AG: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error interno ejecutando algoritmo",
            error_code="INTERNAL_ERROR"
        )), 500

@ag_bp.route('/info')
def get_algorithm_info():
    """Obtener información sobre el algoritmo genético"""
    try:
        info = ag_service.get_algorithm_info()
        
        return jsonify(ResponseFormatter.success(
            data=info,
            message="Información del algoritmo obtenida"
        ))
        
    except Exception as e:
        ag_bp.logger.error(f"Error obteniendo info del AG: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo información",
            error_code="INTERNAL_ERROR"
        )), 500

@ag_bp.route('/validate-scenario', methods=['POST'])
def validate_scenario():
    """Validar un escenario sin ejecutar el algoritmo"""
    try:
        data = request.get_json()
        
        # Validar estructura básica
        ScenarioValidator.validate_scenario_data(data)
        
        return jsonify(ResponseFormatter.success(
            message="Escenario válido"
        ))
        
    except ValidationError as e:
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="VALIDATION_ERROR"
        )), 400
        
    except Exception as e:
        ag_bp.logger.error(f"Error validando escenario: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error interno validando escenario",
            error_code="INTERNAL_ERROR"
        )), 500

@ag_bp.errorhandler(404)
def not_found(error):
    """Manejar errores 404 en rutas AG"""
    return jsonify(ResponseFormatter.error(
        message="Endpoint de algoritmo genético no encontrado",
        error_code="AG_NOT_FOUND"
    )), 404

@ag_bp.errorhandler(405)
def method_not_allowed(error):
    """Manejar errores 405 en rutas AG"""
    return jsonify(ResponseFormatter.error(
        message="Método no permitido para algoritmo genético",
        error_code="AG_METHOD_NOT_ALLOWED"
    )), 405