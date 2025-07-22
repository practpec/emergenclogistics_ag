/**
 * Archivo principal del frontend - Inicialización y coordinación
 */

// Variables globales para módulos principales
let mapManager;
let routeManager;
let uiManager;
let agModule;

/**
 * Inicializar aplicación cuando el DOM esté listo
 */
document.addEventListener('DOMContentLoaded', async function() {
    try {
        logger.info('Iniciando aplicación frontend');
        
        // Inicializar aplicación principal
        await app.init();
        
        // Inicializar módulos específicos
        await initializeModules();
        
        // Configurar manejadores de eventos globales
        setupGlobalEventHandlers();
        
        logger.info('Aplicación frontend inicializada correctamente');
        
    } catch (error) {
        logger.error('Error inicializando aplicación:', error);
        showCriticalError('Error fatal al inicializar la aplicación');
    }
});

/**
 * Inicializar módulos específicos
 */
async function initializeModules() {
    try {
        // Inicializar gestor de mapas
        mapManager = new MapManager();
        await mapManager.init();
        app.registerModule('map', mapManager);
        
        // Inicializar gestor de rutas (se crea cuando se necesite)
        routeManager = new RouteManager();
        app.registerModule('route', routeManager);
        
        // Inicializar gestor de UI
        uiManager = new UIManager();
        await uiManager.init();
        app.registerModule('ui', uiManager);
        
        // Inicializar módulo de AG (si existe)
        if (typeof AGModule !== 'undefined') {
            agModule = new AGModule();
            await agModule.init();
            app.registerModule('ag', agModule);
        }
        
        logger.info('Módulos específicos inicializados');
        
    } catch (error) {
        logger.error('Error inicializando módulos:', error);
        throw error;
    }
}

/**
 * Configurar manejadores de eventos globales
 */
function setupGlobalEventHandlers() {
    // Evento cuando se actualizan datos del mapa
    eventBus.on('data:map-updated', (data) => {
        logger.info('Datos de mapa actualizados');
        
        // Notificar al módulo AG si existe
        if (agModule) {
            agModule.setMapData(data);
        }
    });
    
    // Evento cuando se cambia de módulo
    eventBus.on('module:changed', (data) => {
        logger.info(`Cambio a módulo: ${data.module}`);
        
        // Acciones específicas por módulo
        if (data.module === 'algoritmo' && agModule) {
            agModule.updateFromCurrentData();
        }
    });
    
    // Manejar errores de red
    eventBus.on('network:error', (error) => {
        logger.error('Error de red:', error);
        showError('Error de conexión con el servidor');
    });
}

/**
 * Generar mapa completo
 */
async function generarMapa() {
    try {
        // Validar formulario
        if (!uiManager.validateMapForm()) {
            return;
        }
        
        const formData = uiManager.getMapFormData();
        
        // Mostrar loading
        uiManager.showLoading(AppConfig.messages.loading.map);
        
        // Limpiar mapa anterior
        mapManager.clearMap();
        
        // Generar rutas con municipio específico
        const data = await apiClient.generateCompleteRoutes(
            formData.estado, 
            formData.nNodos,
            formData.municipio  // Asegurar que se pase el municipio
        );
        
        // Actualizar datos en la aplicación
        app.setMapData(data);
        
        // Mostrar resultados en el mapa
        await displayMapResults(data);
        
        // Actualizar panel de rutas
        uiManager.updateRoutesPanel(data.rutas_data);
        
        // Ajustar vista del mapa
        mapManager.fitToRoutes();
        
        // Mostrar mensaje de éxito
        app.showNotification(AppConfig.messages.success.map, 'success');
        
        logger.info(`Mapa generado: ${data.nodos_secundarios.length} destinos`);
        
    } catch (error) {
        logger.error('Error generando mapa:', error);
        showError(AppConfig.messages.error.map + ': ' + error.message);
    } finally {
        uiManager.hideLoading();
    }
}

/**
 * Mostrar resultados del mapa
 */
async function displayMapResults(data) {
    // Agregar nodo principal
    await mapManager.addPrincipalNode(data.nodo_principal);
    
    // Agregar nodos secundarios y rutas
    for (let i = 0; i < data.rutas_data.length; i++) {
        const destinoData = data.rutas_data[i];
        
        // Agregar nodo secundario
        await mapManager.addSecondaryNode(destinoData.destino, i);
        
        // Agregar rutas para este destino
        if (destinoData.rutas) {
            for (let j = 0; j < destinoData.rutas.length; j++) {
                await mapManager.addRoute(destinoData.rutas[j], i, j);
            }
        }
    }
}

/**
 * Resaltar ruta específica
 */
function highlightRoute(destinationIndex, routeIndex) {
    try {
        mapManager.highlightRoute(destinationIndex, routeIndex);
        uiManager.highlightRouteInPanel(destinationIndex, routeIndex);
        uiManager.expandDestination(destinationIndex);
        
        logger.debug(`Ruta resaltada: ${destinationIndex}-${routeIndex}`);
        
    } catch (error) {
        logger.error('Error resaltando ruta:', error);
    }
}

/**
 * Toggle de destino en panel
 */
function toggleDestination(destinationIndex) {
    try {
        const isExpanded = uiManager.toggleDestination(destinationIndex);
        
        if (!isExpanded) {
            mapManager.resetRouteHighlight();
        }
        
    } catch (error) {
        logger.error('Error en toggle de destino:', error);
    }
}

/**
 * Toggle del panel de rutas
 */
function togglePanel() {
    try {
        uiManager.toggleRoutesPanel();
    } catch (error) {
        logger.error('Error en toggle de panel:', error);
    }
}

/**
 * Limpiar resaltado de rutas
 */
function clearHighlight() {
    try {
        mapManager.resetRouteHighlight();
        uiManager.clearAllHighlights();
    } catch (error) {
        logger.error('Error limpiando resaltados:', error);
    }
}

/**
 * Cambiar módulo activo
 */
function showModule(moduleName) {
    try {
        app.showModule(moduleName);
    } catch (error) {
        logger.error(`Error cambiando a módulo ${moduleName}:`, error);
        showError(`Error cambiando a ${moduleName}`);
    }
}

/**
 * Obtener datos actuales (para uso en otros módulos)
 */
function getCurrentMapData() {
    return app.getCurrentData().mapData;
}

function getCurrentScenarioData() {
    return app.getCurrentData().scenario;
}

/**
 * Mostrar error global
 */
function showError(message, duration = 5000) {
    if (uiManager) {
        uiManager.showError(message, duration);
    } else {
        // Fallback si UI Manager no está disponible
        console.error(message);
        alert(message);
    }
}

/**
 * Mostrar error crítico
 */
function showCriticalError(message) {
    logger.error('Error crítico:', message);
    
    // Crear elemento de error crítico
    const errorDiv = document.createElement('div');
    errorDiv.className = 'critical-error';
    errorDiv.innerHTML = `
        <div class="critical-error-content">
            <h2>Error Crítico</h2>
            <p>${message}</p>
            <button onclick="location.reload()">Recargar Página</button>
        </div>
    `;
    
    document.body.appendChild(errorDiv);
}

/**
 * Función llamada cuando se genera un mapa exitosamente
 */
function onMapGenerated(data) {
    app.setMapData(data);
    
    // Emitir evento para otros módulos
    eventBus.emit('map:generated', data);
}

/**
 * Manejadores de errores globales del navegador
 */
window.addEventListener('error', function(event) {
    logger.error('Error global JavaScript:', event.error);
    
    if (event.error && event.error.stack) {
        logger.error('Stack trace:', event.error.stack);
    }
    
    // Solo mostrar al usuario si es un error crítico
    if (event.error && event.error.message.includes('Critical')) {
        showError('Ha ocurrido un error inesperado');
    }
});

window.addEventListener('unhandledrejection', function(event) {
    logger.error('Promesa rechazada:', event.reason);
    
    // Mostrar error de conexión si parece ser un problema de red
    if (event.reason && (
        event.reason.message.includes('fetch') ||
        event.reason.message.includes('network') ||
        event.reason.message.includes('timeout')
    )) {
        showError(AppConfig.messages.error.network);
    }
    
    event.preventDefault();
});

// Exponer funciones globales necesarias
window.generarMapa = generarMapa;
window.highlightRoute = highlightRoute;
window.toggleDestination = toggleDestination;
window.togglePanel = togglePanel;
window.clearHighlight = clearHighlight;
window.showModule = showModule;
window.getCurrentMapData = getCurrentMapData;
window.getCurrentScenarioData = getCurrentScenarioData;
window.onMapGenerated = onMapGenerated;