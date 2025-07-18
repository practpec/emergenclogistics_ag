/**
 * Cargador de templates HTML externos
 */
import { Logger } from './logger.js';

export class TemplateLoader {
    constructor() {
        this.logger = new Logger('TemplateLoader');
        this.cache = new Map();
        this.basePath = '/static/templates';
    }
    
    async init() {
        // Pre-cargar templates críticos
        const criticalTemplates = [
            'components/loading.html',
            'components/error-message.html'
        ];
        
        await Promise.all(
            criticalTemplates.map(template => this.preloadTemplate(template))
        );
        
        this.logger.info('Templates críticos pre-cargados');
    }
    
    async preloadTemplate(templatePath) {
        try {
            await this.loadTemplate(templatePath);
        } catch (error) {
            this.logger.warn(`Error pre-cargando template ${templatePath}:`, error);
        }
    }
    
    async loadTemplate(templatePath) {
        // Verificar cache
        if (this.cache.has(templatePath)) {
            return this.cache.get(templatePath);
        }
        
        try {
            const url = `${this.basePath}/${templatePath}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const html = await response.text();
            
            // Guardar en cache
            this.cache.set(templatePath, html);
            
            this.logger.debug(`Template cargado: ${templatePath}`);
            return html;
            
        } catch (error) {
            this.logger.error(`Error cargando template ${templatePath}:`, error);
            throw error;
        }
    }
    
    async renderTemplate(templatePath, data = {}) {
        try {
            let html = await this.loadTemplate(templatePath);
            
            // Reemplazar variables simples: {{variable}}
            html = this.interpolateVariables(html, data);
            
            return html;
            
        } catch (error) {
            this.logger.error(`Error renderizando template ${templatePath}:`, error);
            return this.getErrorTemplate(error.message);
        }
    }
    
    interpolateVariables(html, data) {
        return html.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return data.hasOwnProperty(key) ? data[key] : match;
        });
    }
    
    getErrorTemplate(errorMessage) {
        return `
            <div class="error-template">
                <p>Error cargando contenido: ${errorMessage}</p>
            </div>
        `;
    }
    
    // Métodos de conveniencia para templates específicos
    async getRouteItemTemplate(routeData) {
        return this.renderTemplate('components/route-item.html', routeData);
    }
    
    async getVehicleRowTemplate(vehicleData) {
        return this.renderTemplate('components/vehicle-row.html', vehicleData);
    }
    
    async getLoadingTemplate() {
        return this.renderTemplate('components/loading.html');
    }
    
    async getErrorTemplate(errorData) {
        return this.renderTemplate('components/error-message.html', errorData);
    }
    
    clearCache() {
        this.cache.clear();
        this.logger.info('Cache de templates limpiado');
    }
    
    getCacheSize() {
        return this.cache.size;
    }
}