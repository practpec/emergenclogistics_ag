/**
 * Módulo de Algoritmo Genético
 */
import { Logger } from '../../core/logger.js';
import { BaseModule } from '../../core/base-module.js';
import { AGManager } from './ag-manager.js';
import { AGUI } from './ag-ui.js';

export class AGModule extends BaseModule {
    constructor(app) {
        super(app, 'algoritmo');
        this.logger = new Logger('AGModule');
        
        this.agManager = new AGManager(app.apiClient);
        this.agUI = new AGUI(app.templateLoader);
        
        this.currentMapData = null;
        this.currentScenario = null;
    }
    
    async init() {
        await super.init();
        
        // Configurar eventos
        this.setupEvents();
        
        // Inicializar UI
        await this.agUI.init();
        
        this.logger.info('Módulo AG inicializado');
    }
    
    setupEvents() {
        // Escuchar cuando se genere un mapa
        this.app.eventBus.on('map-generated', (mapData) => {
            this.setMapData(mapData);
        });
        
        // Funciones globales para compatibilidad con HTML
        window.mostrarDetallesDesastre = () => this.agUI.showDisasterDetails();
        window.actualizarVehiculos = () => this.agUI.updateVehicles();
        window.updateVehicleDetails = (index) => this.agUI.updateVehicleDetails(index);
        window.agregarVehiculo = () => this.agUI.addVehicle();
        window.removeVehicle = (index) => this.agUI.removeVehicle(index);
        window.configuracionAutomatica = () => this.agUI.autoConfigureVehicles();
        window.generarEscenario = () => this.generateScenario();
        window.showTab = (tabName) => this.agUI.showTab(tabName);
        window.exportarEscenario = () => this.exportScenario();
        window.resetearEscenario = () => this.resetScenario();
        window.ejecutarAG = () => this.executeAG();
    }
    
    setMapData(mapData) {
        this.currentMapData = mapData;
        this.agUI.setMapData(mapData);
        this.logger.info('Datos de mapa actualizados en AG');
    }
    
    async generateScenario() {
        if (!this.currentMapData) {
            alert('No hay datos de mapa. Genera un mapa primero.');
            return;
        }

        try {
            const scenarioData = this.agUI.getScenarioFormData();
            
            this.logger.debug('Generando escenario:', scenarioData);
            
            const scenario = await this.agManager.createScenario(scenarioData);
            this.currentScenario = scenario;
            
            this.agUI.showScenarioResult(scenario);
            
            this.logger.info('Escenario generado exitosamente');
            
        } catch (error) {
            this.logger.error('Error generando escenario:', error);
            alert('Error al generar escenario: ' + error.message);
        }
    }
    
    async executeAG() {
        if (!this.currentScenario) {
            alert('Genera un escenario primero');
            return;
        }

        try {
            this.logger.info('Ejecutando algoritmo genético...');
            
            const result = await this.agManager.executeGeneticAlgorithm(this.currentScenario);
            
            this.agUI.showAGResults(result);
            
            this.logger.info('Algoritmo genético ejecutado exitosamente');
            
        } catch (error) {
            this.logger.error('Error ejecutando AG:', error);
            alert('Error ejecutando algoritmo genético: ' + error.message);
        }
    }
    
    exportScenario() {
        if (this.currentScenario) {
            this.agManager.exportScenario(this.currentScenario);
        } else {
            alert('No hay escenario para exportar');
        }
    }
    
    resetScenario() {
        if (confirm('¿Estás seguro de que quieres regenerar el escenario?')) {
            this.generateScenario();
        }
    }
    
    onShow() {
        // Actualizar resumen del mapa cuando se muestre el módulo
        this.agUI.updateMapSummary();
    }
    
    getCurrentScenario() {
        return this.currentScenario;
    }
    
    getCurrentMapData() {
        return this.currentMapData;
    }
}