/**
 * Sistema de logging para frontend
 */
export class Logger {
    constructor(context = 'App') {
        this.context = context;
        this.logLevel = this.getLogLevel();
    }
    
    getLogLevel() {
        // Solo mostrar errores en producción
        const isDev = window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1';
        return isDev ? 'DEBUG' : 'ERROR';
    }
    
    shouldLog(level) {
        const levels = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };
        const currentLevel = levels[this.logLevel] || 3;
        const messageLevel = levels[level] || 0;
        
        return messageLevel >= currentLevel;
    }
    
    formatMessage(level, message, ...args) {
        const timestamp = new Date().toISOString();
        const prefix = `[${timestamp}] ${level} [${this.context}]`;
        
        if (args.length > 0) {
            return [prefix, message, ...args];
        }
        return [prefix, message];
    }
    
    debug(message, ...args) {
        if (this.shouldLog('DEBUG')) {
            console.debug(...this.formatMessage('DEBUG', message, ...args));
        }
    }
    
    info(message, ...args) {
        if (this.shouldLog('INFO')) {
            console.info(...this.formatMessage('INFO', message, ...args));
        }
    }
    
    warn(message, ...args) {
        if (this.shouldLog('WARN')) {
            console.warn(...this.formatMessage('WARN', message, ...args));
        }
    }
    
    error(message, ...args) {
        if (this.shouldLog('ERROR')) {
            console.error(...this.formatMessage('ERROR', message, ...args));
        }
    }
    
    // Método para logging de eventos importantes del usuario
    userAction(action, data = {}) {
        if (this.shouldLog('INFO')) {
            console.info(...this.formatMessage('USER_ACTION', action, data));
        }
    }
    
    // Método para performance
    time(label) {
        if (this.shouldLog('DEBUG')) {
            console.time(`${this.context}:${label}`);
        }
    }
    
    timeEnd(label) {
        if (this.shouldLog('DEBUG')) {
            console.timeEnd(`${this.context}:${label}`);
        }
    }
}