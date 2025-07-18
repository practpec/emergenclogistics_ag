/**
 * Clase base para módulos del sistema
 */
import { Logger } from './logger.js';

export class BaseModule {
    constructor(app, name) {
        this.app = app;
        this.name = name;
        this.logger = new Logger(`Module:${name}`);
        this.isInitialized = false;
        this.isVisible = false;
    }
    
    async init() {
        if (this.isInitialized) {
            this.logger.warn('Módulo ya inicializado');
            return;
        }
        
        this.logger.info('Inicializando módulo');
        this.isInitialized = true;
    }
    
    show() {
        if (!this.isInitialized) {
            this.logger.error('Módulo no inicializado');
            return;
        }
        
        // Ocultar todos los módulos
        document.querySelectorAll('.module').forEach(m => 
            m.classList.remove('active')
        );
        
        // Mostrar este módulo
        const moduleElement = document.getElementById(`module-${this.name}`);
        if (moduleElement) {
            moduleElement.classList.add('active');
            this.isVisible = true;
            this.onShow();
        }
        
        this.logger.info('Módulo mostrado');
    }
    
    hide() {
        const moduleElement = document.getElementById(`module-${this.name}`);
        if (moduleElement) {
            moduleElement.classList.remove('active');
            this.isVisible = false;
            this.onHide();
        }
        
        this.logger.info('Módulo oculto');
    }
    
    // Hooks para extensión
    onShow() {
        // Override en clases hijas
    }
    
    onHide() {
        // Override en clases hijas
    }
    
    destroy() {
        this.hide();
        this.isInitialized = false;
        this.logger.info('Módulo destruido');
    }
    
    // Getters
    get initialized() {
        return this.isInitialized;
    }
    
    get visible() {
        return this.isVisible;
    }
}