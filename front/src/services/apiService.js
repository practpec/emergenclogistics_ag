import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Configurar axios
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para logging de requests
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => Promise.reject(error)
)

// Interceptor para manejo de respuestas
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

class ApiService {
  // Estados y geografía
  async getEstados() {
    const response = await api.get('/api/estados')
    return response.data
  }
  
  async getMunicipios(nombreEstado) {
    const response = await api.get(`/api/municipios/${encodeURIComponent(nombreEstado)}`)
    return response.data
  }
  
  async getNodoInicialMunicipio(estado, claveMunicipio) {
    const response = await api.get(`/api/nodo-inicial/${encodeURIComponent(estado)}/${claveMunicipio}`)
    return response.data
  }
  
  async searchLocalidades(nombre, options = {}) {
    const params = new URLSearchParams()
    params.append('q', nombre)
    
    if (options.estado) params.append('estado', options.estado)
    if (options.limite) params.append('limite', options.limite)
    
    const response = await api.get(`/api/search-localidades?${params.toString()}`)
    return response.data
  }
  
  // Mapas y rutas
  async generateCompleteRoutes(estado, nNodos, claveMunicipio) {
    const requestData = {
      estado,
      n_nodos: nNodos
    }
    
    if (claveMunicipio && claveMunicipio !== 'null') {
      requestData.clave_municipio = claveMunicipio
    }
    
    const response = await api.post('/api/maps/generate-complete-routes', requestData)
    return response.data
  }
  
  async getCoordenadasEstado(estado) {
    const response = await api.get(`/api/geo/coordenadas/${encodeURIComponent(estado)}`)
    return response.data
  }
  
  // Algoritmo genético
  async createScenario(scenarioData) {
    const response = await api.post('/api/ag/create-scenario', scenarioData)
    return response.data
  }
  
  async executeGeneticAlgorithm(scenarioData) {
    const response = await api.post('/api/ag/execute', { escenario: scenarioData })
    return response.data
  }
  
  async getAlgorithmInfo() {
    const response = await api.get('/api/ag/info')
    return response.data
  }
  
  async validateScenario(scenarioData) {
    const response = await api.post('/api/ag/validate-scenario', scenarioData)
    return response.data
  }
  
  // Entities
  async getEntityData(entityType) {
    const response = await api.get(`/api/entities/${entityType}`)
    return response.data
  }
  
  async getAllEntities() {
    const [vehiculos, desastres, categorias] = await Promise.all([
      this.getEntityData('vehiculos'),
      this.getEntityData('desastres'),
      this.getEntityData('categorias_insumos')
    ])
    
    return {
      vehiculos: vehiculos.data,
      desastres: desastres.data,
      categorias_insumos: categorias.data
    }
  }
  
  // Sistema
  async getServerStatus() {
    try {
      const response = await api.get('/api/status')
      return response.data
    } catch (error) {
      return {
        success: false,
        message: 'Error de conexión',
        error: error.message
      }
    }
  }
  
  async getDatabaseInfo() {
    const response = await api.get('/api/database/info')
    return response.data
  }
  
  // Configuración
  async getConfig() {
    const response = await api.get('/api/config')
    return response.data
  }
}

// Función helper para manejar errores de API
export const handleApiError = (error) => {
  if (error.response) {
    // Error del servidor
    const message = error.response.data?.message || 'Error del servidor'
    return {
      type: 'server_error',
      message,
      status: error.response.status,
      data: error.response.data
    }
  } else if (error.request) {
    // Error de red/conexión
    return {
      type: 'network_error',
      message: 'Error de conexión con el servidor',
      error
    }
  } else {
    // Error de configuración
    return {
      type: 'config_error',
      message: error.message,
      error
    }
  }
}

export default new ApiService()