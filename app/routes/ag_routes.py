"""
Rutas para algoritmo genético
"""
from flask import Blueprint, request, jsonify, session
from services.data.scenario_generator import ScenarioGenerator
from services.data.data_loader import DataLoader
from core.validators import ScenarioValidator
from core.exceptions import ValidationError, ScenarioGenerationError
from app.config import Config
from utils.logger import get_logger

ag_bp = Blueprint('ag', __name__)
logger = get_logger(__name__)

# Servicios
data_loader = DataLoader(Config.ENTITIES_PATH)
scenario_generator = ScenarioGenerator(data_loader)

@ag_bp.route('/api/ag/create-scenario', methods=['POST'])
def create_scenario():
    """Crear escenario de emergencia"""
    try:
        data = request.get_json()
        ScenarioValidator.validate_scenario_request(data)
        
        map_data = session.get('mapa_data')
        if not map_data:
            return jsonify({
                'success': False, 
                'error': 'No hay datos de mapa. Genera un mapa primero.'
            }), 400
        
        # Generar escenario
        scenario = scenario_generator.create_scenario(data, map_data)
        
        # Guardar en sesión
        session['escenario_actual'] = scenario
        
        logger.info(f"Escenario creado: {scenario['tipo_desastre']} con {len(scenario['vehiculos_disponibles'])} vehículos")
        
        return jsonify({
            'success': True,
            'escenario': scenario
        })
        
    except ValidationError as e:
        logger.warning(f"Error de validación en escenario: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400
    except ScenarioGenerationError as e:
        logger.error(f"Error generando escenario: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error inesperado en escenario: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@ag_bp.route('/api/ag/execute', methods=['POST'])
def execute_genetic_algorithm():
    """Ejecutar algoritmo genético"""
    try:
        data = request.get_json()
        scenario = data.get('escenario')
        
        if not scenario:
            return jsonify({
                'success': False,
                'error': 'Escenario requerido'
            }), 400
        
        # TODO: Implementar ejecución del algoritmo genético
        # Por ahora, retornar resultado mock
        result = {
            'mejor_solucion': [],
            'fitness': 0.0,
            'generaciones': 0,
            'tiempo_ejecucion': 0.0
        }
        
        logger.info("Algoritmo genético ejecutado (mock)")
        
        return jsonify({
            'success': True,
            'resultado': result
        })
        
    except Exception as e:
        logger.error(f"Error ejecutando AG: {e}")
        return jsonify({'success': False, 'error': 'Error en ejecución'}), 500