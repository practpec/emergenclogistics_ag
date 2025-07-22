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

@maps_bp.route('/api/estados')
def get_estados():
    """Obtener lista de estados con información completa"""
    try:
        estados = geo_service.get_estados_completos()
        return jsonify(ResponseFormatter.success(
            data=estados,
            message=f"Estados obtenidos: {len(estados)}"
        ))
    except Exception as e:
        current_app.logger.error(f"Error obteniendo estados: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo estados",
            error_code="ESTADOS_ERROR"
        )), 500

@maps_bp.route('/api/municipios/<nombre_estado>')
def get_municipios_estado(nombre_estado):
    """Obtener municipios de un estado"""
    try:
        municipios = geo_service.get_municipios_por_estado(nombre_estado)
        
        return jsonify(ResponseFormatter.success(
            data=municipios,
            message=f"Municipios obtenidos para {nombre_estado}: {len(municipios)}"
        ))
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo municipios para estado {nombre_estado}: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo municipios",
            error_code="MUNICIPIOS_ERROR"
        )), 500

@maps_bp.route('/api/nodo-inicial/<nombre_estado>/<clave_municipio>')
def get_nodo_inicial(nombre_estado, clave_municipio):
    """Obtener nodo inicial de un municipio (localidad principal por población)"""
    try:
        from services.data.database_service import DatabaseService
        db_service = DatabaseService()
        
        # Obtener estado
        estado = geo_service.get_estado_by_nombre(nombre_estado)
        nodo_inicial = db_service.get_nodo_inicial_municipio(estado['clave'], clave_municipio)
        
        if not nodo_inicial:
            return jsonify(ResponseFormatter.error(
                message="No se encontró nodo inicial para el municipio",
                error_code="NODO_NOT_FOUND"
            )), 404
        
        return jsonify(ResponseFormatter.success(
            data=nodo_inicial,
            message="Nodo inicial obtenido correctamente"
        ))
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo nodo inicial: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error obteniendo nodo inicial",
            error_code="NODO_ERROR"
        )), 500

@maps_bp.route('/api/generate-complete-routes', methods=['POST'])
def generate_complete_routes():
    """Generar rutas entre localidades del mismo municipio"""
    try:
        data = request.get_json()
        
        # Debug: imprimir datos recibidos
        current_app.logger.info(f"Datos recibidos: {data}")
        
        # Obtener parámetros
        estado = data.get('estado')
        clave_municipio = data.get('clave_municipio') or data.get('municipio')
        n_nodos = data.get('n_nodos', 5)
        
        # Debug: imprimir parámetros extraídos
        current_app.logger.info(f"Estado: {estado}, Municipio: {clave_municipio}, N_nodos: {n_nodos}")
        
        # Validar parámetros
        if not estado:
            raise ValidationError("Estado es requerido")
        if not clave_municipio:
            raise ValidationError(f"Municipio es requerido. Recibido: {clave_municipio}")
        
        RouteValidator.validate_route_request(estado, n_nodos)
        
        # Generar nodos del mismo municipio
        nodos_data = geo_service.generar_con_municipio_seleccionado(
            estado, clave_municipio, n_nodos
        )
        
        # Obtener rutas usando OSRM
        rutas_completas = osrm_service.obtener_rutas_completas(
            nodos_data['nodo_principal'], 
            nodos_data['nodos_secundarios']
        )
        
        # Guardar datos en sesión para uso posterior en AG
        session['mapa_data'] = {
            'punto_inicio': estado,
            'municipio_seleccionado': clave_municipio,
            'nodo_principal': nodos_data['nodo_principal'],
            'nodos_secundarios': nodos_data['nodos_secundarios'],
            'rutas_data': rutas_completas,
            'municipio_info': nodos_data['municipio_info']
        }
        
        result = {
            'nodo_principal': nodos_data['nodo_principal'],
            'nodos_secundarios': nodos_data['nodos_secundarios'],
            'rutas_data': rutas_completas,
            'municipio_info': nodos_data['municipio_info'],
            'metadata': {
                'total_destinos': len(nodos_data['nodos_secundarios']),
                'total_rutas': sum(len(destino.get('rutas', [])) for destino in rutas_completas),
                'estado_origen': estado,
                'municipio_origen': clave_municipio,
                'usando_datos_reales': True,
                'mismo_municipio': True
            }
        }
        
        return jsonify(ResponseFormatter.success(
            data=result,
            message=f"Rutas generadas para {n_nodos} localidades del municipio {nodos_data['municipio_info']['nombre_municipio']}"
        ))
        
    except ValidationError as e:
        current_app.logger.error(f"Error de validación: {e}")
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="VALIDATION_ERROR"
        )), 400
        
    except EmergencLogisticsException as e:
        current_app.logger.error(f"Error de sistema: {e}")
        return jsonify(ResponseFormatter.error(
            message=str(e),
            error_code="ROUTE_GENERATION_ERROR"
        )), 500
        
    except Exception as e:
        current_app.logger.error(f"Error generando rutas: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error interno generando rutas",
            error_code="INTERNAL_ERROR"
        )), 500

@maps_bp.route('/api/search-localidades')
def search_localidades():
    """Buscar localidades por nombre"""
    try:
        nombre = request.args.get('q', '').strip()
        estado = request.args.get('estado')
        limite = int(request.args.get('limite', 10))
        
        if not nombre or len(nombre) < 2:
            return jsonify(ResponseFormatter.error(
                message="El término de búsqueda debe tener al menos 2 caracteres",
                error_code="SEARCH_TOO_SHORT"
            )), 400
        
        localidades = geo_service.buscar_localidades(nombre, estado, limite)
        
        return jsonify(ResponseFormatter.success(
            data=localidades,
            message=f"Localidades encontradas: {len(localidades)}"
        ))
        
    except Exception as e:
        current_app.logger.error(f"Error buscando localidades: {e}")
        return jsonify(ResponseFormatter.error(
            message="Error en búsqueda de localidades",
            error_code="SEARCH_ERROR"
        )), 500

@maps_bp.route('/maps')
def maps_page():
    """Página dedicada solo a mapas"""
    try:
        estados = geo_service.get_estados()
        return render_template('pages/maps.html', estados=estados)
    except Exception as e:
        current_app.logger.error(f"Error cargando página de mapas: {e}")
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