"""
Rutas para funcionalidad de mapas
"""
from flask import Blueprint, render_template, session
from services.data.data_loader import DataLoader
from services.geo.geo_service import GeoService
from app.config import Config
from utils.logger import get_logger

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
        
        return render_template(
            'pages/index.html',
            estados=states,
            tipos_desastre=entities['desastres'],
            tipos_vehiculos=entities['vehiculos'],
            categorias_insumos=entities['categorias_insumos']
        )
    except Exception as e:
        logger.error(f"Error cargando página principal: {e}")
        return render_template('pages/error.html', error="Error interno del servidor"), 500