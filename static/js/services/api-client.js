/**
 * Cliente para comunicación con la API backend con soporte para base de datos
 */
class ApiClient extends BaseModule {
    constructor() {
        super('ApiClient');
        this.baseUrl = AppConfig.api.base;
        this.timeout = 30000; // 30 segundos
    }
    
    /**
     * Realizar petición HTTP genérica
     */
    async request(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        try {
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                },
                signal: controller.signal
            };
            
            const finalOptions = { ...defaultOptions, ...options };
            
            this.logger.debug(`Petición ${finalOptions.method || 'GET'}: ${url}`);
            
            const response = await fetch(url, finalOptions);
            
            clearTimeout(timeoutId);
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.logger.debug(`Respuesta exitosa: ${url}`);
            return data;
            
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Timeout: La petición tardó demasiado tiempo');
            }
            
            this.logger.error(`Error en petición ${url}:`, error);
            throw error;
        }
    }
    
    /**
     * GET request
     */
    async get(url) {
        return this.request(url, { method: 'GET' });
    }
    
    /**
     * POST request
     */
    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * PUT request
     */
    async put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * DELETE request
     */
    async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
    
    /**
     * Obtener estados desde base de datos
     */
    async getEstados() {
        try {
            const data = await this.get(AppConfig.api.estados);
            
            if (!data.success) {
                throw new Error(data.message || 'Error obteniendo estados');
            }
            
            return data.data;
            
        } catch (error) {
            this.logger.error('Error en getEstados:', error);
            throw error;
        }
    }
    
    /**
     * Obtener municipios de un estado
     */
    async getMunicipios(claveEstado) {
        try {
            const data = await this.get(`${AppConfig.api.municipios}/${claveEstado}`);
            
            if (!data.success) {
                throw new Error(data.message || 'Error obteniendo municipios');
            }
            
            return data.data;
            
        } catch (error) {
            this.logger.error('Error en getMunicipios:', error);
            throw error;
        }
    }
    
    /**
     * Obtener localidades de un municipio
     */
    async getLocalidades(claveEstado, claveMunicipio, options = {}) {
        try {
            let url = `${AppConfig.api.localidades}/${claveEstado}/${claveMunicipio}`;
            
            const params = new URLSearchParams();
            if (options.excluirLocalidad) {
                params.append('excluir_localidad', options.excluirLocalidad);
            }
            if (options.poblacionMinima) {
                params.append('poblacion_minima', options.poblacionMinima);
            }
            
            if (params.toString()) {
                url += `?${params.toString()}`;
            }
            
            const data = await this.get(url);
            
            if (!data.success) {
                throw new Error(data.message || 'Error obteniendo localidades');
            }
            
            return data.data;
            
        } catch (error) {
            this.logger.error('Error en getLocalidades:', error);
            throw error;
        }
    }
    
    /**
     * Buscar localidades por nombre
     */
    async searchLocalidades(nombre, options = {}) {
        try {
            if (!nombre || nombre.length < AppConfig.database.searchMinLength) {
                throw new Error(AppConfig.messages.error.searchTooShort);
            }
            
            const params = new URLSearchParams();
            params.append('q', nombre);
            
            if (options.estado) {
                params.append('estado', options.estado);
            }
            if (options.limite) {
                params.append('limite', options.limite);
            }
            
            const url = `${AppConfig.api.searchLocalidades}?${params.toString()}`;
            const data = await this.get(url);
            
            if (!data.success) {
                throw new Error(data.message || 'Error buscando localidades');
            }
            
            return data.data;
            
        } catch (error) {
            this.logger.error('Error en searchLocalidades:', error);
            throw error;
        }
    }
    
    /**
     * Generar rutas completas con datos reales
     */
    async generateCompleteRoutes(estado, nNodos, claveMunicipio = null) {
        try {
            console.log('=== API CLIENT DEBUG ===');
            console.log('Parámetros recibidos:');
            console.log('  estado:', estado);
            console.log('  nNodos:', nNodos);
            console.log('  claveMunicipio:', claveMunicipio);
            console.log('  typeof claveMunicipio:', typeof claveMunicipio);
            console.log('========================');
            
            const requestData = {
                estado: estado,
                n_nodos: nNodos
            };
            
            // Agregar municipio si se proporciona
            if (claveMunicipio) {
                requestData.clave_municipio = claveMunicipio;
                console.log('Municipio agregado a requestData');
            } else {
                console.log('NO se agregó municipio (valor falsy)');
            }
            
            console.log('API Client - Datos a enviar:', requestData);
            
            const data = await this.post(AppConfig.api.routes, requestData);
            
            if (!data.success) {
                throw new Error(data.message || 'Error generando rutas');
            }
            
            return data.data;
            
        } catch (error) {
            this.logger.error('Error en generateCompleteRoutes:', error);
            throw error;
        }
    }
    
    /**
     * Obtener coordenadas de un estado
     */
    async getCoordenadastEstado(estado) {
        try {
            const data = await this.get(`${AppConfig.api.coordenadas}/${encodeURIComponent(estado)}`);
            
            if (!data.success) {
                throw new Error(data.message || 'Error obteniendo coordenadas');
            }
            
            return data.data;
            
        } catch (error) {
            this.logger.error('Error en getCoordenadasEstado:', error);
            throw error;
        }
    }
    
    /**
     * Obtener información de la base de datos
     */
    async getDatabaseInfo() {
        try {
            const data = await this.get(AppConfig.api.databaseInfo);
            
            if (!data.success) {
                throw new Error(data.message || 'Error obteniendo información de BD');
            }
            
            return data.data;
            
        } catch (error) {
            this.logger.error('Error en getDatabaseInfo:', error);
            throw error;
        }
    }
    
    /**
     * Crear escenario de emergencia
     */
    async createScenario(scenarioData) {
        try {
            const data = await this.post(AppConfig.api.ag.create, scenarioData);
            
            if (!data.success) {
                throw new Error(data.message || 'Error creando escenario');
            }
            
            return data.data;
            
        } catch (error) {
            this.logger.error('Error en createScenario:', error);
            throw error;
        }
    }
    
    /**
     * Ejecutar algoritmo genético
     */
    async executeGeneticAlgorithm(scenarioData) {
        try {
            const data = await this.post(AppConfig.api.ag.execute, {
                escenario: scenarioData
            });
            
            return data; // Retornamos toda la respuesta (incluso si success es false)
            
        } catch (error) {
            this.logger.error('Error en executeGeneticAlgorithm:', error);
            throw error;
        }
    }
    
    /**
     * Obtener información del algoritmo genético
     */
    async getAlgorithmInfo() {
        try {
            const data = await this.get(AppConfig.api.ag.info);
            
            if (!data.success) {
                throw new Error(data.message || 'Error obteniendo información del algoritmo');
            }
            
            return data.data;
            
        } catch (error) {
            this.logger.error('Error en getAlgorithmInfo:', error);
            throw error;
        }
    }
    
    /**
     * Obtener datos de entidades
     */
    async getEntityData(entityType) {
        try {
            const data = await this.get(`${AppConfig.api.entities}/${entityType}`);
            
            if (!data.success) {
                throw new Error(data.message || `Error obteniendo datos de ${entityType}`);
            }
            
            return data.data;
            
        } catch (error) {
            this.logger.error(`Error en getEntityData(${entityType}):`, error);
            throw error;
        }
    }
    
    /**
     * Verificar estado del servidor y base de datos
     */
    async getServerStatus() {
        try {
            const data = await this.get(AppConfig.api.status);
            return data;
        } catch (error) {
            this.logger.error('Error verificando estado del servidor:', error);
            return { 
                success: false, 
                message: 'Error de conexión',
                error: error.message 
            };
        }
    }
    
    /**
     * Manejar respuesta con validación
     */
    validateResponse(response, expectedFields = []) {
        if (!response) {
            throw new Error('Respuesta vacía del servidor');
        }
        
        if (!response.success) {
            throw new Error(response.message || 'Error en respuesta del servidor');
        }
        
        // Validar campos esperados en data
        if (expectedFields.length > 0 && response.data) {
            const missingFields = expectedFields.filter(field => 
                !(field in response.data)
            );
            
            if (missingFields.length > 0) {
                this.logger.warn(`Campos faltantes en respuesta: ${missingFields.join(', ')}`);
            }
        }
        
        return response.data;
    }
    
    /**
     * Retry automático para peticiones
     */
    async requestWithRetry(url, options = {}, maxRetries = 3) {
        let lastError;
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await this.request(url, options);
            } catch (error) {
                lastError = error;
                this.logger.warn(`Intento ${attempt}/${maxRetries} falló para ${url}:`, error.message);
                
                if (attempt < maxRetries) {
                    // Esperar antes del siguiente intento (exponential backoff)
                    const delay = Math.pow(2, attempt) * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }
        
        throw lastError;
    }
}

// Crear instancia global
window.ApiClient = ApiClient;
window.apiClient = new ApiClient();