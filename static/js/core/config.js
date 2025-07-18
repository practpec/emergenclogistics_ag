/**
 * Configuración del frontend
 */
export class Config {
    constructor() {
        this.api = {
            baseUrl: this.getBaseUrl(),
            timeout: 30000,
            retries: 3
        };
        
        this.maps = {
            defaultZoom: 6,
            defaultCenter: [23.6345, -102.5528], // México
            maxDestinations: 15,
            routeColors: [
                '#e74c3c', '#3498db', '#f39c12', '#27ae60', '#9b59b6',
                '#e67e22', '#1abc9c', '#34495e', '#f1c40f', '#95a5a6',
                '#e91e63', '#ff5722', '#607d8b', '#795548', '#009688'
            ]
        };
        
        this.ui = {
            animationDuration: 300,
            debounceDelay: 500,
            toastDuration: 6000
        };
        
        this.cache = {
            maxAge: 5 * 60 * 1000, // 5 minutos
            maxSize: 100
        };
    }
    
    getBaseUrl() {
        const { protocol, host } = window.location;
        return `${protocol}//${host}`;
    }
    
    get isDevelopment() {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1';
    }
    
    get isProduction() {
        return !this.isDevelopment;
    }
    
    // Configuración de logging
    get logLevel() {
        return this.isDevelopment ? 'DEBUG' : 'ERROR';
    }
    
    // URLs de API
    getApiUrl(endpoint) {
        return `${this.api.baseUrl}/api/${endpoint}`;
    }
    
    // Configuración de mapas
    getRouteColor(index) {
        return this.maps.routeColors[index % this.maps.routeColors.length];
    }
    
    // Configuración de UI
    getAnimationDuration(type = 'normal') {
        const durations = {
            fast: this.ui.animationDuration * 0.5,
            normal: this.ui.animationDuration,
            slow: this.ui.animationDuration * 2
        };
        return durations[type] || durations.normal;
    }
}