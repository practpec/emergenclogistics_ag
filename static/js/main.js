/**
 * Punto de entrada principal del frontend
 */
import { app } from './core/app.js';

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', async function() {
    try {
        await app.init();
        
        // Configurar datos globales si existen
        if (typeof ENTITIES_DATA !== 'undefined') {
            window.entitiesData = ENTITIES_DATA;
        }
        
        console.info('EmergenLogistics iniciado correctamente');
        
    } catch (error) {
        console.error('Error inicializando aplicación:', error);
    }
});

// Exportar para acceso global
window.app = app;