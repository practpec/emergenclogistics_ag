/**
 * Cliente API optimizado con cache y retry
 */
import { Logger } from '../core/logger.js';
import { Config } from '../core/config.js';

export class ApiClient {
    constructor() {
        this.logger = new Logger('ApiClient');
        this.config = new Config();
        this.cache = new Map();
    }
    
    async request(endpoint, options = {}) {
        const {
            method = 'GET',
            data = null,
            cache = false,
            retries = this.config.api.retries
        } = options;
        
        const url = this.config.getApiUrl(endpoint);
        const cacheKey = `${method}:${url}:${JSON.stringify(data)}`;
        
        // Verificar cache
        if (cache && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.config.cache.maxAge) {
                this.logger.debug(`Cache hit: ${endpoint}`);
                return cached.data;
            }
        }
        
        const requestOptions = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            signal: AbortSignal.timeout(this.config.api.timeout)
        };
        
        if (data && method !== 'GET') {
            requestOptions.body = JSON.stringify(data);
        }
        
        let lastError;
        
        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                this.logger.debug(`Request: ${method} ${endpoint} (intento ${attempt + 1})`);
                
                const response = await fetch(url, requestOptions);
                const result = await response.json();
                
                if (!response.ok) {
                    throw new Error(result.error || `HTTP ${response.status}`);
                }
                
                // Guardar en cache si es necesario
                if (cache && method === 'GET') {
                    this.setCacheItem(cacheKey, result);
                }
                
                this.logger.debug(`Response exitoso: ${endpoint}`);
                return result;
                
            } catch (error) {
                lastError = error;
                this.logger.warn(`Intento ${attempt + 1} falló para ${endpoint}:`, error.message);
                
                if (attempt < retries) {
                    await this.delay(1000 * (attempt + 1)); // Backoff exponencial
                }
            }
        }
        
        this.logger.error(`Request falló después de ${retries + 1} intentos: ${endpoint}`);
        throw lastError;
    }
    
    // Métodos de conveniencia
    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }
    
    async post(endpoint, data, options = {}) {
        return this.request(endpoint, { ...options, method: 'POST', data });
    }
    
    async put(endpoint, data, options = {}) {
        return this.request(endpoint, { ...options, method: 'PUT', data });
    }
    
    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }
    
    // Métodos específicos de la API
    async generateCompleteRoutes(estado, nNodos) {
        return this.post('generate-complete-routes', {
            estado,
            n_nodos: nNodos
        });
    }
    
    async createScenario(scenarioData) {
        return this.post('ag/create-scenario', scenarioData);
    }
    
    async executeGeneticAlgorithm(scenario) {
        return this.post('ag/execute', { escenario: scenario });
    }
    
    async getEntityData(entityType) {
        return this.get(`entities/${entityType}`, { cache: true });
    }
    
    async getServerStatus() {
        return this.get('status');
    }
    
    // Utilidades
    setCacheItem(key, data) {
        // Limpiar cache si está lleno
        if (this.cache.size >= this.config.cache.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }
    
    clearCache() {
        this.cache.clear();
        this.logger.info('Cache de API limpiado');
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}