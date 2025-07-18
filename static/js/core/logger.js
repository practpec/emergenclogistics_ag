/**
 * Sistema de logging para el frontend
 */
class Logger {
    constructor(context = 'App') {
        this.context = context;
        this.levels = {
            ERROR: 0,
            WARN: 1,
            INFO: 2,
            DEBUG: 3
        };
        this.currentLevel = this.levels.INFO;
    }
    
    setLevel(level) {
        if (typeof level === 'string') {
            this.currentLevel = this.levels[level.toUpperCase()] || this.levels.INFO;
        } else {
            this.currentLevel = level;
        }
    }
    
    error(message, ...args) {
        if (this.currentLevel >= this.levels.ERROR) {
            console.error(`[${this.context}] ERROR:`, message, ...args);
        }
    }
    
    warn(message, ...args) {
        if (this.currentLevel >= this.levels.WARN) {
            console.warn(`[${this.context}] WARN:`, message, ...args);
        }
    }
    
    info(message, ...args) {
        if (this.currentLevel >= this.levels.INFO) {
            console.info(`[${this.context}] INFO:`, message, ...args);
        }
    }
    
    debug(message, ...args) {
        if (this.currentLevel >= this.levels.DEBUG) {
            console.debug(`[${this.context}] DEBUG:`, message, ...args);
        }
    }
    
    group(label) {
        if (this.currentLevel >= this.levels.DEBUG) {
            console.group(`[${this.context}] ${label}`);
        }
    }
    
    groupEnd() {
        if (this.currentLevel >= this.levels.DEBUG) {
            console.groupEnd();
        }
    }
    
    time(label) {
        console.time(`[${this.context}] ${label}`);
    }
    
    timeEnd(label) {
        console.timeEnd(`[${this.context}] ${label}`);
    }
}

// Logger global
window.Logger = Logger;
window.logger = new Logger('EmergenLogistics');