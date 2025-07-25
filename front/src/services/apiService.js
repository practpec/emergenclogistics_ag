import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
});

const handleApiError = (error) => {
  if (error.response) {
    console.error("Error de API:", error.response.data);
    return error.response.data.message || 'Error del servidor. Intenta de nuevo.';
  } else if (error.request) {
    console.error("Error de red:", error.request);
    return 'No se pudo conectar con el servidor.';
  } else {
    console.error("Error de configuración:", error.message);
    return 'Ocurrió un error inesperado.';
  }
};

class ApiService {
  async getVehicles() {
    try {
      const response = await api.get('/api/scenario/vehicles');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getDisasters() {
    try {
      const response = await api.get('/api/scenario/disasters');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getSupplies() {
    try {
      const response = await api.get('/api/scenario/supplies');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getEstados() {
    try {
      const response = await api.get('/api/estados');
      return response.data.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getMunicipios(nombreEstado) {
    try {
      const response = await api.get(`/api/municipios/${encodeURIComponent(nombreEstado)}`);
      return response.data.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async getMunicipioInfo(estado, claveMunicipio) {
    try {
      const response = await api.get(`/api/nodo-inicial/${encodeURIComponent(estado)}/${claveMunicipio}`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async generateCompleteRoutes(estado, nNodos, claveMunicipio) {
    try {
      const requestData = { estado, n_nodos: nNodos, clave_municipio: claveMunicipio };
      const response = await api.post('/api/maps/generate-complete-routes', requestData);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async runAGScenario(scenarioData) {
    try {
      const response = await api.post('/api/ag/run-scenario', scenarioData);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export default new ApiService();