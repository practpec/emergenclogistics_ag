/**
 * Módulo de mapas
 */
import { Logger } from '../../core/logger.js';
import { BaseModule } from '../../core/base-module.js';
import { MapManager } from './map-manager.js';
import { RouteManager } from './route-manager.js';
import { UIManager } from './ui-manager.js';

export class MapsModule extends BaseModule {
    constructor(app) {
        super(app, 'maps');
        this.logger = new Logger('MapsModule');
        
        this.mapManager = new MapManager(app.config);
        this.routeManager = new RouteManager(app.apiClient);
        this.uiManager = new UIManager(this.mapManager, app.templateLoader);
        
        this.currentData = null;
    }
    
    async init() {
        await super.init();
        
        // Inicializar mapa
        this.mapManager.init();
        
        // Configurar eventos
        this.setupEvents();
        
        this.logger.info('Módulo de mapas inicializado');
    }
    
    setupEvents() {
        // Evento para generar mapa
        this.app.eventBus.on('generate-map', async (data) => {
            await this.generateMap(data);
        });
        
        // Evento de highlight de ruta
        this.app.eventBus.on('highlight-route', (data) => {
            this.highlightRoute(data.destinationIndex, data.routeIndex);
        });
        
        // Funciones globales para compatibilidad
        window.generarMapa = () => this.handleGenerateMap();
        window.highlightRoute = (destIndex, routeIndex) => 
            this.highlightRoute(destIndex, routeIndex);
        window.toggleDestination = (destIndex) => 
            this.toggleDestination(destIndex);
        window.togglePanel = () => this.uiManager.togglePanel();
    }
    
    async handleGenerateMap() {
        if (!this.uiManager.validateForm()) {
            return;
        }
        
        const formData = this.uiManager.getFormValues();
        await this.generateMap(formData);
    }
    
    async generateMap(data) {
        const { estado, nNodos } = data;
        
        this.uiManager.toggleLoading(true);
        this.mapManager.clearMap();
        
        try {
            const result = await this.routeManager.getCompleteRoutes(estado, nNodos);
            
            this.currentData = {
                punto_inicio: estado,
                nodo_principal: result.nodo_principal,
                nodos_secundarios: result.nodos_secundarios,
                rutas_data: result.rutas_data
            };
            
            await this.displayResults(this.currentData);
            
            const stats = this.routeManager.getRouteStats();
            this.uiManager.updatePanelHeader(stats);
            
            // Notificar a otros módulos
            this.app.eventBus.emit('map-generated', this.currentData);
            
            this.logger.info(`Mapa generado: ${stats.totalRoutes} rutas para ${stats.totalDestinations} destinos`);
            
        } catch (error) {
            this.logger.error('Error generando mapa:', error);
            this.uiManager.showError(`No se pudo generar el mapa: ${error.message}`);
        } finally {
            this.uiManager.toggleLoading(false);
        }
    }
    
    async displayResults(data) {
        // Agregar nodo principal
        this.mapManager.addPrincipalNode(data.nodo_principal);
        
        // Agregar nodos secundarios y rutas
        data.rutas_data.forEach((destinoData, index) => {
            const destino = destinoData.destino;
            const rutas = destinoData.rutas || [];
            
            this.mapManager.addSecondaryNode(destino, index);
            
            rutas.forEach((ruta, routeIndex) => {
                this.mapManager.addRoute(ruta, index, routeIndex);
            });
        });
        
        // Ajustar vista del mapa
        this.mapManager.fitToRoutes();
        
        // Actualizar panel de rutas
        this.uiManager.updateRoutesPanel(data.rutas_data);
    }
    
    highlightRoute(destinationIndex, routeIndex) {
        this.mapManager.highlightRoute(destinationIndex, routeIndex);
        this.uiManager.highlightRouteInPanel(destinationIndex, routeIndex);
        this.uiManager.expandDestination(destinationIndex);
    }
    
    toggleDestination(destinationIndex) {
        const header = document.querySelector(`[data-destination="${destinationIndex}"]`);
        const routesList = document.getElementById(`routes-${destinationIndex}`);
        
        if (header && routesList) {
            const isActive = header.classList.contains('active');
            
            if (isActive) {
                header.classList.remove('active');
                routesList.classList.remove('show');
                this.mapManager.resetRouteHighlight();
            } else {
                this.uiManager.collapseAllDestinations();
                header.classList.add('active');
                routesList.classList.add('show');
            }
        }
    }
    
    getCurrentData() {
        return this.currentData;
    }
    
    show() {
        super.show();
        // Reinicializar mapa si es necesario
        if (this.mapManager.map) {
            setTimeout(() => {
                this.mapManager.map.invalidateSize();
            }, 100);
        }
    }
}