/**
 * Aplicación principal - Gestor de módulos y estado global
 */
class App extends BaseModule {
    constructor() {
        super('App');
        this.modules = new Map();
        this.currentData = {
            mapData: null,
            scenario: null
        };
        this.activeModule = 'mapas';
    }
    
    /**
     * Inicializar aplicación
     */
    async onInit() {
        this.logger.info('Iniciando EmergenLogistics');
        
        // Inicializar servicios core
        await this.initCoreServices();
        
        // Registrar módulos
        this.registerModules();
        
        // Configurar navegación
        this.setupNavigation();
        
        // Configurar manejo de errores global
        this.setupErrorHandling();
        
        // Verificar estado del servidor
        await this.checkServerStatus();
        
        this.logger.info('Aplicación inicializada correctamente');
    }
    
    /**
     * Inicializar servicios core
     */
    async initCoreServices() {
        // Precargar templates comunes
        await templateLoader.preloadTemplates([
            'components/loading.html',
            'components/error-message.html',
            'components/route-item.html',
            'components/vehicle-row.html'
        ]);
        
        this.logger.debug('Servicios core inicializados');
    }
    
    /**
     * Registrar módulos de la aplicación
     */
    registerModules() {
        // Los módulos se registrarán cuando se carguen sus scripts
        this.on('module:registered', (event) => {
            const { name, module } = event.detail;
            this.modules.set(name, module);
            this.logger.info(`Módulo registrado: ${name}`);
        });
    }
    
    /**
     * Registrar un módulo
     */
    registerModule(name, moduleInstance) {
        this.modules.set(name, moduleInstance);
        this.emit('module:registered', { name, module: moduleInstance });
    }
    
    /**
     * Obtener módulo
     */
    getModule(name) {
        return this.modules.get(name);
    }
    
    /**
     * Configurar navegación entre módulos
     */
    setupNavigation() {
        // Event listeners para botones de navegación
        this.findElements('.module-nav .btn').forEach(btn => {
            this.addEventListener(btn, 'click', (e) => {
                const moduleId = btn.id.replace('btn-', '');
                this.showModule(moduleId);
            });
        });
        
        // Mostrar módulo inicial
        this.showModule(this.activeModule);
    }
    
    /**
     * Mostrar módulo específico
     */
    showModule(moduleName) {
        this.logger.info(`Cambiando a módulo: ${moduleName}`);
        
        // Ocultar todos los módulos
        this.findElements('.module').forEach(m => m.classList.remove('active'));
        this.findElements('.module-nav .btn').forEach(b => b.classList.remove('active'));
        
        // Mostrar módulo seleccionado
        const moduleElement = this.findElement(`#module-${moduleName}`, false);
        const buttonElement = this.findElement(`#btn-${moduleName}`, false);
        
        if (moduleElement) {
            moduleElement.classList.add('active');
        }
        
        if (buttonElement) {
            buttonElement.classList.add('active');
        }
        
        // Actualizar estado
        this.activeModule = moduleName;
        
        // Notificar cambio de módulo
        this.emit('module:changed', { module: moduleName });
        
        // Acciones específicas por módulo
        if (moduleName === 'algoritmo') {
            this.updateAGModule();
        }
    }
    
    /**
     * Actualizar módulo de algoritmo genético
     */
    updateAGModule() {
        const agModule = this.getModule('ag');
        if (agModule && this.currentData.mapData) {
            agModule.setMapData(this.currentData.mapData);
        }
    }
    
    /**
     * Configurar manejo de errores global
     */
    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            this.logger.error('Error global:', event.error);
            this.showError('Ha ocurrido un error inesperado');
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            this.logger.error('Promesa rechazada:', event.reason);
            this.showError('Error de conexión o procesamiento');
            event.preventDefault();
        });
    }
    
    /**
     * Verificar estado del servidor
     */
    async checkServerStatus() {
        try {
            const response = await fetch(AppConfig.api.status);
            const data = await response.json();
            
            if (data.success) {
                this.logger.info('Servidor en línea');
            } else {
                this.logger.warn('Servidor reporta problemas');
            }
        } catch (error) {
            this.logger.error('Error verificando servidor:', error);
        }
    }
    
    /**
     * Establecer datos del mapa
     */
    setMapData(data) {
        this.currentData.mapData = data;
        this.emit('data:map-updated', { data });
        this.logger.info('Datos de mapa actualizados');
    }
    
    /**
     * Establecer datos del escenario
     */
    setScenarioData(data) {
        this.currentData.scenario = data;
        this.emit('data:scenario-updated', { data });
        this.logger.info('Datos de escenario actualizados');
    }
    
    /**
     * Obtener datos actuales
     */
    getCurrentData() {
        return { ...this.currentData };
    }
    
    /**
     * Limpiar datos
     */
    clearData() {
        this.currentData = {
            mapData: null,
            scenario: null
        };
        this.emit('data:cleared');
        this.logger.info('Datos limpiados');
    }
    
    /**
     * Mostrar notificación
     */
    showNotification(message, type = 'info', duration = 3000) {
        // Crear elemento de notificación si no existe
        let notificationContainer = this.findElement('#notifications', false);
        
        if (!notificationContainer) {
            notificationContainer = Utils.createElement('div', 'notifications');
            notificationContainer.id = 'notifications';
            document.body.appendChild(notificationContainer);
        }
        
        // Crear notificación
        const notification = Utils.createElement('div', `notification notification-${type}`, message);
        notificationContainer.appendChild(notification);
        
        // Auto-remover
        setTimeout(() => {
            Utils.fadeOut(notification, 300);
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }
}

// Crear instancia global de la aplicación
window.App = App;
window.app = new App();