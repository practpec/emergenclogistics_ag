/**
 * Cargador y gestor de templates HTML
 */
class TemplateLoader {
    constructor() {
        this.cache = new Map();
        this.logger = new Logger('TemplateLoader');
    }
    
    /**
     * Cargar template desde archivo
     */
    async loadTemplate(templatePath) {
        // Verificar cache
        if (this.cache.has(templatePath)) {
            this.logger.debug(`Template cargado desde cache: ${templatePath}`);
            return this.cache.get(templatePath);
        }
        
        try {
            this.logger.debug(`Cargando template: ${templatePath}`);
            
            const response = await fetch(`/static/templates/${templatePath}`);
            
            if (!response.ok) {
                throw new Error(`Error cargando template: ${response.status} ${response.statusText}`);
            }
            
            const html = await response.text();
            
            // Guardar en cache
            this.cache.set(templatePath, html);
            
            this.logger.debug(`Template cargado exitosamente: ${templatePath}`);
            return html;
            
        } catch (error) {
            this.logger.error(`Error cargando template ${templatePath}:`, error);
            throw error;
        }
    }
    
    /**
     * Procesar template con variables
     */
    processTemplate(html, variables = {}) {
        let processedHtml = html;
        
        // Reemplazar variables con sintaxis {{variable}}
        for (const [key, value] of Object.entries(variables)) {
            const regex = new RegExp(`{{\\s*${key}\\s*}}`, 'g');
            processedHtml = processedHtml.replace(regex, value || '');
        }
        
        // Procesar condicionales {{#if condition}}...{{/if}}
        processedHtml = this.processConditionals(processedHtml, variables);
        
        // Procesar loops {{#each array}}...{{/each}}
        processedHtml = this.processLoops(processedHtml, variables);
        
        return processedHtml;
    }
    
    /**
     * Procesar condicionales en template
     */
    processConditionals(html, variables) {
        const conditionalRegex = /{{#if\s+(\w+)}}([\s\S]*?){{\/if}}/g;
        
        return html.replace(conditionalRegex, (match, condition, content) => {
            const value = variables[condition];
            return value ? content : '';
        });
    }
    
    /**
     * Procesar loops en template
     */
    processLoops(html, variables) {
        const loopRegex = /{{#each\s+(\w+)}}([\s\S]*?){{\/each}}/g;
        
        return html.replace(loopRegex, (match, arrayName, content) => {
            const array = variables[arrayName];
            
            if (!Array.isArray(array)) {
                return '';
            }
            
            return array.map((item, index) => {
                let itemContent = content;
                
                // Reemplazar {{this}} con el item actual
                itemContent = itemContent.replace(/{{this}}/g, item);
                
                // Reemplazar {{@index}} con el índice
                itemContent = itemContent.replace(/{{@index}}/g, index);
                
                // Si el item es un objeto, reemplazar sus propiedades
                if (typeof item === 'object' && item !== null) {
                    for (const [key, value] of Object.entries(item)) {
                        const regex = new RegExp(`{{${key}}}`, 'g');
                        itemContent = itemContent.replace(regex, value || '');
                    }
                }
                
                return itemContent;
            }).join('');
        });
    }
    
    /**
     * Cargar y procesar template
     */
    async render(templatePath, variables = {}) {
        try {
            const html = await this.loadTemplate(templatePath);
            return this.processTemplate(html, variables);
        } catch (error) {
            this.logger.error(`Error renderizando template ${templatePath}:`, error);
            throw error;
        }
    }
    
    /**
     * Renderizar template en elemento DOM
     */
    async renderTo(templatePath, targetElement, variables = {}) {
        try {
            const html = await this.render(templatePath, variables);
            
            if (typeof targetElement === 'string') {
                targetElement = document.querySelector(targetElement);
            }
            
            if (!targetElement) {
                throw new Error('Elemento target no encontrado');
            }
            
            targetElement.innerHTML = html;
            
            this.logger.debug(`Template renderizado en elemento: ${templatePath}`);
            
        } catch (error) {
            this.logger.error(`Error renderizando template en elemento:`, error);
            throw error;
        }
    }
    
    /**
     * Precargar templates
     */
    async preloadTemplates(templatePaths) {
        this.logger.info(`Precargando ${templatePaths.length} templates`);
        
        const promises = templatePaths.map(path => 
            this.loadTemplate(path).catch(error => {
                this.logger.warn(`Error precargando template ${path}:`, error);
                return null;
            })
        );
        
        await Promise.all(promises);
        
        this.logger.info('Templates precargados completamente');
    }
    
    /**
     * Limpiar cache
     */
    clearCache() {
        this.cache.clear();
        this.logger.info('Cache de templates limpiado');
    }
    
    /**
     * Obtener estadísticas del cache
     */
    getCacheStats() {
        return {
            size: this.cache.size,
            templates: Array.from(this.cache.keys())
        };
    }
}

// Instancia global
window.TemplateLoader = TemplateLoader;
window.templateLoader = new TemplateLoader();