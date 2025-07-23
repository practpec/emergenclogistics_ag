import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

class ApiService {
  // Estados y geografía
  async getEstados() {
    const response = await api.get('/api/estados');
    return response.data;
  }
  
  async getMunicipios(nombreEstado) {
    const response = await api.get(`/api/municipios/${encodeURIComponent(nombreEstado)}`);
    return response.data;
  }
  
  async getNodoInicialMunicipio(estado, claveMunicipio) {
    const response = await api.get(`/api/nodo-inicial/${encodeURIComponent(estado)}/${claveMunicipio}`);
    return response.data;
  }

  
  // Mapas y rutas
  async generateCompleteRoutes(estado, nNodos, claveMunicipio) {
    const requestData = {
      estado,
      n_nodos: nNodos
    };
    
    if (claveMunicipio && claveMunicipio !== 'null') {
      requestData.clave_municipio = claveMunicipio;
    }
    
    const response = await api.post('/api/maps/generate-complete-routes', requestData);
    return response.data;
  }

  async getVehicles() {
    const response = await api.get('/api/scenario/vehicles');
    return response.data;
  }

  async getDisasters() {
    const response = await api.get('/api/scenario/disasters');
    return response.data;
  }
}



// Función helper para manejar errores de API
export const handleApiError = (error) => {
  if (error.response) {
    const message = error.response.data?.message || 'Error del servidor';
    return {
      type: 'server_error',
      message,
      status: error.response.status,
      data: error.response.data
    };
  } else if (error.request) {
    return {
      type: 'network_error',
      message: 'Error de conexión con el servidor',
      error
    };
  } else {
    return {
      type: 'config_error',
      message: error.message,
      error
    };
  }
};

export default new ApiService();