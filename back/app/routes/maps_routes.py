from flask import Blueprint, request, jsonify, session, current_app
from core.exceptions import ValidationError
from core.helpers import ResponseFormatter
from services.geo.geo_service import GeoService
from services.geo.maps_service import OSRMService

maps_bp = Blueprint('maps', __name__)

geo_service = GeoService()
osrm_service = OSRMService()

@maps_bp.route('/estados')
def get_estados():
    """Obtener lista de estados"""
    try:
        estados = geo_service.get_estados_completos()
        return jsonify(ResponseFormatter.success(
            data=estados,
            message=f"Estados obtenidos: {len(estados)}"
        ))
    except Exception as e:
        current_app.logger.error(f"Error obteniendo estados: {e}")
        return jsonify(ResponseFormatter.error(
            "Error obteniendo estados", "ESTADOS_ERROR"
        )), 500

@maps_bp.route('/municipios/<nombre_estado>')
def get_municipios_estado(nombre_estado):
    """Obtener municipios de un estado"""
    try:
        municipios = geo_service.get_municipios_por_estado(nombre_estado)
        return jsonify(ResponseFormatter.success(
            data=municipios,
            message=f"Municipios obtenidos para {nombre_estado}: {len(municipios)}"
        ))
    except Exception as e:
        current_app.logger.error(f"Error obteniendo municipios para {nombre_estado}: {e}")
        return jsonify(ResponseFormatter.error(
            "Error obteniendo municipios", "MUNICIPIOS_ERROR"
        )), 500

@maps_bp.route('/nodo-inicial/<nombre_estado>/<clave_municipio>')
def get_nodo_inicial(nombre_estado, clave_municipio):
    """Obtener nodo inicial de un municipio con información completa"""
    try:
        from services.data.database_service import DatabaseService
        db_service = DatabaseService()
        
        estado = geo_service.get_estado_by_nombre(nombre_estado)
        nodo_inicial = db_service.get_nodo_inicial_municipio(estado['clave'], clave_municipio)
        
        if not nodo_inicial:
            return jsonify(ResponseFormatter.error(
                "No se encontró nodo inicial para el municipio", "NODO_NOT_FOUND"
            )), 404
        
        # Contar total de localidades en el municipio
        total_localidades = db_service.count_localidades_municipio(
            estado['clave'], clave_municipio
        )
        
        result = {
            'nodo_principal': nodo_inicial,
            'municipio_info': {
                'clave_municipio': clave_municipio,
                'nombre_municipio': nodo_inicial['nombre_municipio'],
                'total_localidades': total_localidades
            }
        }
        
        return jsonify(ResponseFormatter.success(
            data=result,
            message="Nodo inicial obtenido correctamente"
        ))
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo nodo inicial: {e}")
        return jsonify(ResponseFormatter.error(
            "Error obteniendo nodo inicial", "NODO_ERROR"
        )), 500

@maps_bp.route('/maps/generate-complete-routes', methods=['POST'])
def generate_complete_routes():
    """Generar rutas entre localidades del mismo municipio"""
    try:
        data = request.get_json()
        
        estado = data.get('estado')
        clave_municipio = data.get('clave_municipio') or data.get('municipio')
        n_nodos = data.get('n_nodos', 5)
        
        if not estado:
            raise ValidationError("Estado es requerido")
        if not clave_municipio:
            raise ValidationError("Municipio es requerido")
        if not (1 <= n_nodos <= 15):
            raise ValidationError("Número de nodos debe estar entre 1 y 15")
        
        nodos_data = geo_service.generar_nodos_secundarios(estado, n_nodos, clave_municipio)
        
        rutas_completas = osrm_service.obtener_rutas_completas(
            nodos_data['nodo_principal'], 
            nodos_data['nodos_secundarios']
        )
        
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
            message=f"Rutas generadas para {n_nodos} localidades"
        ))
        
    except ValidationError as e:
        current_app.logger.error(f"Error de validación: {e}")
        return jsonify(ResponseFormatter.error(str(e), "VALIDATION_ERROR")), 400
        
    except Exception as e:
        current_app.logger.error(f"Error generando rutas: {e}")
        return jsonify(ResponseFormatter.error(
            "Error interno generando rutas", "INTERNAL_ERROR"
        )), 500