/**
 * Configuración global de la aplicación frontend
 */
const AppConfig = {
    // URLs de la API
    api: {
        base: '',
        routes: '/api/generate-complete-routes',
        entities: '/api/entities',
        status: '/api/status',
        ag: {
            create: '/api/ag/create-scenario',
            execute: '/api/ag/execute',
            info: '/api/ag/info'
        }
    },
    
    // Configuración del mapa
    map: {
        defaultCenter: [23.6345, -102.5528],
        defaultZoom: 6,
        maxZoom: 18,
        tileLayer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '© OpenStreetMap contributors'
    },
    
    // Límites del sistema
    limits: {
        maxDestinations: 15,
        minDestinations: 1,
        maxVehicles: 10,
        minVehicles: 1
    },
    
    // Configuración de UI
    ui: {
        loadingDelay: 300,
        animationDuration: 300,
        toastDuration: 5000
    },
    
    // Colores para rutas
    colors: {
        routes: [
            '#e74c3c', '#3498db', '#f39c12', '#27ae60', '#9b59b6',
            '#e67e22', '#1abc9c', '#34495e', '#f1c40f', '#95a5a6',
            '#e91e63', '#ff5722', '#607d8b', '#795548', '#009688'
        ],
        primary: '#2b6cb0',
        secondary: '#4a5568',
        success: '#38a169',
        warning: '#d69e2e',
        danger: '#e53e3e',
        info: '#3182ce'
    },
    
    // Mensajes del sistema
    messages: {
        loading: {
            map: 'Generando rutas...',
            scenario: 'Creando escenario...',
            algorithm: 'Ejecutando algoritmo genético...'
        },
        success: {
            map: 'Mapa generado correctamente',
            scenario: 'Escenario creado exitosamente',
            algorithm: 'Algoritmo ejecutado exitosamente'
        },
        error: {
            map: 'Error generando mapa',
            scenario: 'Error creando escenario',
            algorithm: 'Error ejecutando algoritmo',
            network: 'Error de conexión',
            validation: 'Datos inválidos'
        }
    }
};

// Hacer configuración global disponible
window.AppConfig = AppConfig;