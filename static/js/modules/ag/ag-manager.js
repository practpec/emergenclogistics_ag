/**
 * Gestor del Algoritmo Genético
 */
import { Logger } from '../../core/logger.js';

export class AGManager {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.logger = new Logger('AGManager');
    }

    async createScenario(scenarioData) {
        try {
            this.logger.debug('Creando escenario:', scenarioData);
            
            const response = await this.apiClient.createScenario(scenarioData);
            
            if (response.success) {
                this.logger.info('Escenario creado exitosamente');
                return response.escenario;
            } else {
                throw new Error(response.error || 'Error desconocido');
            }
            
        } catch (error) {
            this.logger.error('Error creando escenario:', error);
            throw error;
        }
    }

    async executeGeneticAlgorithm(scenario) {
        try {
            this.logger.info('Ejecutando algoritmo genético...');
            
            const response = await this.apiClient.executeGeneticAlgorithm(scenario);
            
            if (response.success) {
                this.logger.info('Algoritmo genético ejecutado exitosamente');
                return response.resultado;
            } else {
                throw new Error(response.error || 'Error en la ejecución');
            }
            
        } catch (error) {
            this.logger.error('Error ejecutando AG:', error);
            throw error;
        }
    }

    exportScenario(scenario, filename = null) {
        try {
            const dataStr = JSON.stringify(scenario, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            
            link.href = url;
            link.download = filename || `escenario_${scenario.tipo_desastre}_${Date.now()}.json`;
            link.click();
            
            URL.revokeObjectURL(url);
            
            this.logger.info('Escenario exportado exitosamente');
            
        } catch (error) {
            this.logger.error('Error exportando escenario:', error);
            throw error;
        }
    }
}