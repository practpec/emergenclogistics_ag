"""
Rutas para funcionalidad de mapas
"""
from flask import Blueprint, render_template, jsonify
from services.data.data_loader import DataLoader
from services.geo.geo_service import GeoService
from app.config import Config
from utils.logger import get_logger
from core.exceptions import DataLoadError

maps_bp = Blueprint('maps', __name__)
logger = get_logger(__name__)

# Servicios
data_loader = DataLoader(Config.ENTITIES_PATH)
geo_service = GeoService()

@maps_bp.route('/')
def index():
    """Página principal"""
    try:
        entities = data_loader.load_all_entities()
        states = geo_service.get_states()
        
        logger.info("Página principal cargada correctamente")
        
        return render_template(
            'pages/index.html',
            estados=states,
            tipos_desastre=entities['desastres'],
            tipos_vehiculos=entities['vehiculos'],
            categorias_insumos=entities['categorias_insumos']
        )
    except DataLoadError as e:
        logger.error(f"Error cargando datos: {e}")
        # Fallback con datos mínimos
        return render_template(
            'pages/index.html',
            estados=['Chiapas', 'CDMX', 'Jalisco'],
            tipos_desastre=[{'tipo': 'inundacion', 'prioridad': []}],
            tipos_vehiculos=[{'tipo': 'auto', 'modelo': 'Genérico'}],
            categorias_insumos=[{'categoria': 'Alimentación básica', 'peso_unitario_kg': 10}]
        )
    except Exception as e:
        logger.error(f"Error inesperado en página principal: {e}")
        # Retornar respuesta JSON si el template de error no existe
        try:
            return render_template('pages/error.html', error="Error interno del servidor"), 500
        except:
            return jsonify({
                'error': 'Error interno del servidor',
                'message': 'La aplicación no pudo cargar correctamente. Verifica la configuración.',
                'details': str(e)
            }), 500

@maps_bp.route('/health')
def health_check():
    """Verificación de salud del módulo de mapas"""
    try:
        # Verificar servicios críticos
        states = geo_service.get_states()
        entities = data_loader.load_all_entities()
        
        return jsonify({
            'status': 'healthy',
            'states_count': len(states),
            'entities_loaded': len(entities),
            'module': 'maps'
        })
    except Exception as e:
        logger.error(f"Health check falló: {e}")
        return jsonify({
            'status': 'unhealthy', 
            'error': str(e),
            'module': 'maps'
        }), 500