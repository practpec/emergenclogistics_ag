from flask import Blueprint, request, jsonify, current_app
from core.exceptions import EmergencLogisticsException, ValidationError, GeneticAlgorithmError
from core.validators import BaseValidator
from services.algorithms.main.genetic_algorithm import LogisticsGeneticAlgorithm
from utils.helpers import ResponseFormatter

ag_bp = Blueprint('ag', __name__)

@ag_bp.route('/run-scenario', methods=['POST'])
def run_genetic_algorithm():
    """Ejecutar algoritmo genético para optimización logística"""
    try:
        data = request.get_json()
        
        # Validar estructura de datos requerida
        if not data:
            raise ValidationError("No se recibieron datos")
        
        required_keys = ['map_data', 'scenario_config']
        if not all(key in data for key in required_keys):
            raise ValidationError(f"Faltan campos requeridos: {required_keys}")
        
        # Validar map_data
        map_data = data['map_data']
        map_required = ['nodo_principal', 'nodos_secundarios', 'rutas_data']
        if not all(key in map_data for key in map_required):
            raise ValidationError(f"map_data incompleto, requiere: {map_required}")
        
        # Validar scenario_config
        scenario_config = data['scenario_config']
        scenario_required = ['tipo_desastre', 'vehiculos_disponibles', 'rutas_estado']
        if not all(key in scenario_config for key in scenario_required):
            raise ValidationError(f"scenario_config incompleto, requiere: {scenario_required}")
        
        # Validar vehículos
        vehiculos = scenario_config['vehiculos_disponibles']
        if not isinstance(vehiculos, list) or len(vehiculos) == 0:
            raise ValidationError("Se requiere al menos un vehículo disponible")
        
        for i, vehiculo in enumerate(vehiculos):
            vehiculo_required = ['modelo', 'tipo', 'velocidad_kmh', 'consumo_litros_km', 'maximo_peso_ton', 'capacidad_kg', 'matricula']
            if not all(key in vehiculo for key in vehiculo_required):
                raise ValidationError(f"Vehículo {i+1} incompleto, requiere: {vehiculo_required}")
            
            # Validar valores numéricos
            BaseValidator.validate_positive_number(vehiculo['velocidad_kmh'], f"velocidad_kmh vehículo {i+1}")
            BaseValidator.validate_positive_number(vehiculo['consumo_litros_km'], f"consumo_litros_km vehículo {i+1}")
            BaseValidator.validate_positive_number(vehiculo['maximo_peso_ton'], f"maximo_peso_ton vehículo {i+1}")
            BaseValidator.validate_positive_number(vehiculo['capacidad_kg'], f"capacidad_kg vehículo {i+1}")
        
        # Validar rutas_estado
        rutas_estado = scenario_config['rutas_estado']
        if not isinstance(rutas_estado, list):
            raise ValidationError("rutas_estado debe ser una lista")
        
        for i, ruta in enumerate(rutas_estado):
            ruta_required = ['ruta_id', 'estado', 'vehiculos_permitidos']
            if not all(key in ruta for key in ruta_required):
                raise ValidationError(f"Ruta {i+1} incompleta, requiere: {ruta_required}")
            
            if ruta['estado'] not in ['abierta', 'cerrada']:
                raise ValidationError(f"Estado de ruta {i+1} debe ser 'abierta' o 'cerrada'")
        
        # Validar datos de rutas
        rutas_data = map_data['rutas_data']
        if not isinstance(rutas_data, list) or len(rutas_data) == 0:
            raise ValidationError("Se requieren datos de rutas")
        
        for i, destino_data in enumerate(rutas_data):
            if 'destino' not in destino_data or 'rutas' not in destino_data:
                raise ValidationError(f"Destino {i+1} requiere campos 'destino' y 'rutas'")
            
            if not isinstance(destino_data['rutas'], list) or len(destino_data['rutas']) == 0:
                raise ValidationError(f"Destino {i+1} debe tener al menos una ruta")
        
        # Extraer parámetros del AG si se proporcionan
        parametros_ag = data.get('parametros_ag', {})
        
        current_app.logger.info(f"Iniciando AG con {len(vehiculos)} vehículos, {len(rutas_data)} destinos y parámetros: {parametros_ag}")
        
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
        
    except EmergencLogisticsException as e:
        current_app.logger.error(f"Error del sistema: {e}")
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="SYSTEM_ERROR"
        )), 500
        
    except Exception as e:
        current_app.logger.error(f"Error inesperado en AG: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error interno del servidor",
            error_code="INTERNAL_ERROR"
        )), 500

@ag_bp.route('/parametros', methods=['GET'])
def get_ag_parameters():
    """Obtener parámetros configurables del algoritmo genético"""
    try:
        parametros = {
            'poblacion_size': {'min': 20, 'max': 100, 'default': 50, 'descripcion': 'Tamaño de la población'},
            'generaciones': {'min': 50, 'max': 300, 'default': 100, 'descripcion': 'Número de generaciones'},
            'prob_cruza': {'min': 0.5, 'max': 1.0, 'default': 0.8, 'descripcion': 'Probabilidad de cruza'},
            'prob_mutacion': {'min': 0.05, 'max': 0.3, 'default': 0.15, 'descripcion': 'Probabilidad de mutación'},
            'elitismo_rate': {'min': 0.05, 'max': 0.2, 'default': 0.1, 'descripcion': 'Porcentaje de élite'}
        }
        
        return jsonify(ResponseFormatter.success(
            data=parametros,
            message="Parámetros del AG obtenidos"
        ))
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo parámetros AG: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo parámetros",
            error_code="PARAMETERS_ERROR"
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