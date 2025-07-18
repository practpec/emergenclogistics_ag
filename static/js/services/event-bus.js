/**
 * Bus de eventos para comunicación entre módulos
 */
import { Logger } from '../core/logger.js';

export class EventBus {
    constructor() {
        this.logger = new Logger('EventBus');
        this.events = new Map();
    }
    
    on(event, callback) {
        if (!this.events.has(event)) {
            this.events.set(event, []);
        }
        
        this.events.get(event).push(callback);
        this.logger.debug(`Listener agregado para evento: ${event}`);
    }
    
    off(event, callback) {
        if (!this.events.has(event)) {
            return;
        }
        
        const callbacks = this.events.get(event);
        const index = callbacks.indexOf(callback);
        
        if (index > -1) {
            callbacks.splice(index, 1);
            this.logger.debug(`Listener removido para evento: ${event}`);
        }
    }
    
    emit(event, data = null) {
        if (!this.events.has(event)) {
            this.logger.debug(`Evento sin listeners: ${event}`);
            return;
        }
        
        const callbacks = this.events.get(event);
        this.logger.debug(`Emitiendo evento: ${event} (${callbacks.length} listeners)`);
        
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                this.logger.error(`Error en callback de evento ${event}:`, error);
            }
        });
    }
    
    once(event, callback) {
        const onceWrapper = (data) => {
            callback(data);
            this.off(event, onceWrapper);
        };
        
        this.on(event, onceWrapper);
    }
    
    clear() {
        this.events.clear();
        this.logger.info('Todos los eventos limpiados');
    }
    
    getEventCount() {
        return this.events.size;
    }
    
    getListenerCount(event) {
        return this.events.has(event) ? this.events.get(event).length : 0;
    }
}