"""
Rutas API para servicios backend
"""
from flask import Blueprint, request, jsonify, session
from services.geo.geo_service import GeoService
from services.geo.maps_service import MapsService
from services.data.scenario_generator import ScenarioGenerator
from services.data.data_loader import DataLoader
from core.validators import MapValidator, ScenarioValidator
from core.exceptions import ValidationError, RouteCalculationError
from app.config import Config
from utils.logger import get_logger

api_bp = Blueprint('api', __name__)
logger = get_logger(__name__)

# Servicios
geo_service = GeoService()
maps_service = MapsService(Config.OSRM_BASE_URL)
data_loader = DataLoader(Config.ENTITIES_PATH)
scenario_generator = ScenarioGenerator(data_loader)

@api_bp.route('/status')
def get_status():
    """Estado del servidor"""
    return jsonify({
        'status': 'online',
        'message': 'Servidor funcionando correctamente'
    })

@api_bp.route('/generate-complete-routes', methods=['POST'])
def generate_complete_routes():
    """Generar rutas completas"""
    try:
        data = request.get_json()
        MapValidator.validate_map_request(data)
        
        state = data['estado']
        n_nodes = data['n_nodos']
        
        # Generar nodos
        nodes_data = geo_service.generate_secondary_nodes(state, n_nodes)
        
        # Calcular rutas
        routes_data = maps_service.calculate_complete_routes(
            nodes_data['nodo_principal'],
            nodes_data['nodos_secundarios']
        )
        
        # Guardar en sesión
        session['mapa_data'] = {
            'punto_inicio': state,
            'nodos_secundarios': nodes_data['nodos_secundarios'],
            'rutas_data': routes_data
        }
        
        logger.info(f"Rutas generadas para {state}: {len(routes_data)} destinos")
        
        return jsonify({
            'success': True,
            'nodo_principal': nodes_data['nodo_principal'],
            'nodos_secundarios': nodes_data['nodos_secundarios'],
            'rutas_data': routes_data
        })
        
    except ValidationError as e:
        logger.warning(f"Error de validación: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400
    except RouteCalculationError as e:
        logger.error(f"Error calculando rutas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500

@api_bp.route('/entities/<entity_type>')
def get_entity_data(entity_type):
    """Obtener datos de entidad específica"""
    try:
        entities = data_loader.load_all_entities()
        
        if entity_type not in entities:
            return jsonify({'success': False, 'error': 'Entidad no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'data': entities[entity_type]
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo entidad {entity_type}: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500