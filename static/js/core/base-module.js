/**
 * Clase base para todos los módulos de la aplicación
 */
class BaseModule {
    constructor(name) {
        this.name = name;
        this.logger = new Logger(name);
        this.isInitialized = false;
        this.eventListeners = new Map();
    }
    
    /**
     * Inicializar módulo
     */
    async init() {
        if (this.isInitialized) {
            this.logger.warn(`Módulo ${this.name} ya está inicializado`);
            return;
        }
        
        try {
            this.logger.info(`Inicializando módulo ${this.name}`);
            await this.onInit();
            this.isInitialized = true;
            this.logger.info(`Módulo ${this.name} inicializado correctamente`);
        } catch (error) {
            this.logger.error(`Error inicializando módulo ${this.name}:`, error);
            throw error;
        }
    }
    
    /**
     * Método para ser sobrescrito por los módulos hijos
     */
    async onInit() {
        // Override en clases hijas
    }
    
    /**
     * Destruir módulo y limpiar recursos
     */
    destroy() {
        this.logger.info(`Destruyendo módulo ${this.name}`);
        this.removeAllEventListeners();
        this.isInitialized = false;
    }
    
    /**
     * Agregar event listener con seguimiento
     */
    addEventListener(element, event, handler, options = {}) {
        const boundHandler = handler.bind(this);
        element.addEventListener(event, boundHandler, options);
        
        const key = `${element.constructor.name}_${event}_${Date.now()}`;
        this.eventListeners.set(key, {
            element,
            event,
            handler: boundHandler,
            options
        });
        
        return key;
    }
    
    /**
     * Remover event listener específico
     */
    removeEventListener(key) {
        const listener = this.eventListeners.get(key);
        if (listener) {
            listener.element.removeEventListener(
                listener.event, 
                listener.handler, 
                listener.options
            );
            this.eventListeners.delete(key);
        }
    }
    
    /**
     * Remover todos los event listeners
     */
    removeAllEventListeners() {
        for (const [key, listener] of this.eventListeners) {
            listener.element.removeEventListener(
                listener.event, 
                listener.handler, 
                listener.options
            );
        }
        this.eventListeners.clear();
    }
    
    /**
     * Encontrar elemento DOM con logging
     */
    findElement(selector, required = true) {
        const element = document.querySelector(selector);
        
        if (!element && required) {
            this.logger.error(`Elemento requerido no encontrado: ${selector}`);
            throw new Error(`Elemento no encontrado: ${selector}`);
        }
        
        if (!element) {
            this.logger.warn(`Elemento opcional no encontrado: ${selector}`);
        }
        
        return element;
    }
    
    /**
     * Encontrar múltiples elementos DOM
     */
    findElements(selector) {
        const elements = document.querySelectorAll(selector);
        this.logger.debug(`Encontrados ${elements.length} elementos para: ${selector}`);
        return Array.from(elements);
    }
    
    /**
     * Mostrar loading
     */
    showLoading(message = 'Cargando...') {
        const loadingEl = this.findElement('#loading', false);
        if (loadingEl) {
            const messageEl = loadingEl.querySelector('p');
            if (messageEl) {
                messageEl.textContent = message;
            }
            loadingEl.classList.add('show');
        }
    }
    
    /**
     * Ocultar loading
     */
    hideLoading() {
        const loadingEl = this.findElement('#loading', false);
        if (loadingEl) {
            loadingEl.classList.remove('show');
        }
    }
    
    /**
     * Mostrar error
     */
    showError(message, duration = 5000) {
        this.logger.error(message);
        
        const errorEl = this.findElement('#error-message', false);
        if (errorEl) {
            errorEl.innerHTML = `<strong>Error:</strong> ${message}`;
            errorEl.classList.add('show');
            
            if (duration > 0) {
                setTimeout(() => {
                    errorEl.classList.remove('show');
                }, duration);
            }
        } else {
            // Fallback a alert si no hay elemento de error
            alert(`Error: ${message}`);
        }
    }
    
    /**
     * Ocultar error
     */
    hideError() {
        const errorEl = this.findElement('#error-message', false);
        if (errorEl) {
            errorEl.classList.remove('show');
        }
    }
    
    /**
     * Validar que el módulo esté inicializado
     */
    requireInitialized() {
        if (!this.isInitialized) {
            throw new Error(`Módulo ${this.name} no está inicializado`);
        }
    }
    
    /**
     * Emitir evento personalizado
     */
    emit(eventName, data = {}) {
        const event = new CustomEvent(`${this.name}:${eventName}`, {
            detail: { module: this.name, ...data }
        });
        document.dispatchEvent(event);
        this.logger.debug(`Evento emitido: ${eventName}`, data);
    }
    
    /**
     * Escuchar eventos personalizados
     */
    on(eventName, handler) {
        const fullEventName = eventName.includes(':') ? eventName : `${this.name}:${eventName}`;
        return this.addEventListener(document, fullEventName, handler);
    }
    
    /**
     * Ejecutar con manejo de errores
     */
    async execute(operation, errorMessage = 'Operación falló') {
        try {
            return await operation();
        } catch (error) {
            this.logger.error(errorMessage, error);
            this.showError(`${errorMessage}: ${error.message}`);
            throw error;
        }
    }
}

// Hacer BaseModule global
window.BaseModule = BaseModule;