/**
 * Aplicación principal del sistema EmergenLogistics
 */
import { Logger } from './logger.js';
import { Config } from './config.js';
import { TemplateLoader } from './template-loader.js';
import { EventBus } from '../services/event-bus.js';
import { ApiClient } from '../services/api-client.js';

export class App {
    constructor() {
        this.logger = new Logger('App');
        this.config = new Config();
        this.templateLoader = new TemplateLoader();
        this.eventBus = new EventBus();
        this.apiClient = new ApiClient();
        
        this.modules = new Map();
        this.currentModule = null;
        
        this.logger.info('Aplicación inicializada');
    }
    
    async init() {
        try {
            // Inicializar template loader
            await this.templateLoader.init();
            
            // Cargar módulos dinámicamente
            await this.loadModules();
            
            // Configurar eventos globales
            this.setupGlobalEvents();
            
            // Activar módulo por defecto
            this.showModule('maps');
            
            this.logger.info('Aplicación lista');
            
        } catch (error) {
            this.logger.error('Error inicializando aplicación:', error);
        }
    }
    
    async loadModules() {
        // Cargar módulo de mapas
        const { MapsModule } = await import('../modules/maps/maps-module.js');
        this.modules.set('maps', new MapsModule(this));
        
        // Cargar módulo de algoritmo genético
        const { AGModule } = await import('../modules/ag/ag-module.js');
        this.modules.set('ag', new AGModule(this));
        
        this.logger.info(`Módulos cargados: ${this.modules.size}`);
    }
    
    setupGlobalEvents() {
        // Manejo de errores globales
        window.addEventListener('error', (event) => {
            this.logger.error('Error global:', event.error);
            this.eventBus.emit('global-error', { error: event.error });
        });
        
        // Promesas rechazadas
        window.addEventListener('unhandledrejection', (event) => {
            this.logger.error('Promesa rechazada:', event.reason);
            this.eventBus.emit('global-error', { error: event.reason });
            event.preventDefault();
        });
        
        // Navegación entre módulos
        this.eventBus.on('navigate-to-module', (data) => {
            this.showModule(data.module);
        });
    }
    
    showModule(moduleName) {
        // Ocultar módulo actual
        if (this.currentModule) {
            this.currentModule.hide();
            this.updateNavigation(null);
        }
        
        // Mostrar nuevo módulo
        const module = this.modules.get(moduleName);
        if (module) {
            module.show();
            this.currentModule = module;
            this.updateNavigation(moduleName);
            
            this.logger.info(`Módulo activo: ${moduleName}`);
        } else {
            this.logger.error(`Módulo no encontrado: ${moduleName}`);
        }
    }
    
    updateNavigation(activeModule) {
        // Actualizar botones de navegación
        document.querySelectorAll('.module').forEach(m => 
            m.classList.remove('active')
        );
        document.querySelectorAll('.module-nav .btn').forEach(b => 
            b.classList.remove('active')
        );
        
        if (activeModule) {
            const moduleElement = document.getElementById(`module-${activeModule}`);
            const navButton = document.getElementById(`btn-${activeModule}`);
            
            if (moduleElement) moduleElement.classList.add('active');
            if (navButton) navButton.classList.add('active');
        }
    }
    
    getModule(name) {
        return this.modules.get(name);
    }
    
    // Métodos públicos para acceso global
    get logger() { return this._logger; }
    set logger(value) { this._logger = value; }
    
    get eventBus() { return this._eventBus; }
    set eventBus(value) { this._eventBus = value; }
    
    get apiClient() { return this._apiClient; }
    set apiClient(value) { this._apiClient = value; }
    
    get templateLoader() { return this._templateLoader; }
    set templateLoader(value) { this._templateLoader = value; }
}

// Instancia global
export const app = new App();

// Funciones globales para compatibilidad
window.showModule = (moduleName) => app.showModule(moduleName);
window.app = app;