from flask import Blueprint, render_template, request, jsonify, session, current_app
from core.exceptions import EmergencLogisticsException, ValidationError
from core.validators import RouteValidator
from services.geo.geo_service import GeoService
from services.geo.maps_service import OSRMService
from services.data.data_loader import DataLoader
from utils.helpers import ResponseFormatter

maps_bp = Blueprint('maps', __name__)

# Servicios
geo_service = GeoService()
osrm_service = OSRMService()
data_loader = DataLoader()

@maps_bp.route('/')
def index():
    """Página principal con generador de mapas y algoritmo genético"""
    try:
        estados = geo_service.get_estados()
        entities = data_loader.get_all_entities()
        
        return render_template('index.html',
                             estados=estados,
                             tipos_desastre=entities['desastres'],
                             tipos_vehiculos=entities['vehiculos'],
                             categorias_insumos=entities['categorias_insumos'])
                             
    except Exception as e:
        current_app.logger.error(f"Error cargando página principal: {e}")
        return render_template('pages/error.html', 
                             error="Error cargando la aplicación"), 500

@maps_bp.route('/api/generate-complete-routes', methods=['POST'])
def generate_complete_routes():
    """Generar rutas completas para todos los destinos"""
    try:
        data = request.get_json()
        
        # Validar datos de entrada
        RouteValidator.validate_route_data({
            'origen': {'lat': 0, 'lng': 0},  # Validación básica
            'destinos': [{}] * data.get('n_nodos', 1)
        })
        
        estado = data.get('estado', 'Chiapas')
        n_nodos = data.get('n_nodos', 5)
        
        # Validar parámetros
        if n_nodos < 1 or n_nodos > 15:
            raise ValidationError("Número de nodos debe estar entre 1 y 15")
        
        # Generar nodos
        nodos_data = geo_service.generar_nodos_secundarios(estado, n_nodos)
        
        # Obtener rutas usando OSRM
        rutas_completas = osrm_service.obtener_rutas_completas(
            nodos_data['nodo_principal'], 
            nodos_data['nodos_secundarios']
        )
        
        # Guardar datos en sesión para uso posterior en AG
        session['mapa_data'] = {
            'punto_inicio': estado,
            'nodos_secundarios': nodos_data['nodos_secundarios'],
            'rutas_data': rutas_completas
        }
        
        result = {
            'nodo_principal': nodos_data['nodo_principal'],
            'nodos_secundarios': nodos_data['nodos_secundarios'],
            'rutas_data': rutas_completas
        }
        
        return jsonify(ResponseFormatter.success(
            data=result,
            message=f"Rutas generadas para {n_nodos} destinos"
        ))
        
    except ValidationError as e:
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="VALIDATION_ERROR"
        )), 400
        
    except EmergencLogisticsException as e:
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="ROUTE_GENERATION_ERROR"
        )), 500
        
    except Exception as e:
        maps_bp.logger.error(f"Error generando rutas: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error interno generando rutas",
            error_code="INTERNAL_ERROR"
        )), 500

@maps_bp.route('/maps')
def maps_page():
    """Página dedicada solo a mapas"""
    try:
        estados = geo_service.get_estados()
        return render_template('pages/maps.html', estados=estados)
    except Exception as e:
        maps_bp.logger.error(f"Error cargando página de mapas: {e}")
        return render_template('pages/error.html', 
                             error="Error cargando mapas"), 500

@maps_bp.errorhandler(404)
def not_found(error):
    """Manejar páginas no encontradas"""
    return render_template('pages/error.html', 
                         error="Página no encontrada"), 404

@maps_bp.errorhandler(500)
def internal_error(error):
    """Manejar errores internos"""
    return render_template('pages/error.html', 
                         error="Error interno del servidor"), 500