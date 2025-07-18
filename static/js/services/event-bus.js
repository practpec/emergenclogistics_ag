/**
 * Bus de eventos para comunicación entre módulos
 */
class EventBus {
    constructor() {
        this.events = new Map();
        this.logger = new Logger('EventBus');
    }
    
    /**
     * Suscribirse a un evento
     */
    on(eventName, callback, context = null) {
        if (!this.events.has(eventName)) {
            this.events.set(eventName, []);
        }
        
        const listener = {
            callback,
            context,
            id: this.generateId()
        };
        
        this.events.get(eventName).push(listener);
        
        this.logger.debug(`Suscripción registrada: ${eventName} (ID: ${listener.id})`);
        
        // Retornar función para desuscribirse
        return () => this.off(eventName, listener.id);
    }
    
    /**
     * Suscribirse a un evento una sola vez
     */
    once(eventName, callback, context = null) {
        const unsubscribe = this.on(eventName, (...args) => {
            unsubscribe();
            callback.apply(context, args);
        }, context);
        
        return unsubscribe;
    }
    
    /**
     * Desuscribirse de un evento
     */
    off(eventName, listenerId = null) {
        if (!this.events.has(eventName)) {
            return false;
        }
        
        const listeners = this.events.get(eventName);
        
        if (listenerId === null) {
            // Remover todos los listeners del evento
            this.events.delete(eventName);
            this.logger.debug(`Todos los listeners removidos para: ${eventName}`);
            return true;
        }
        
        // Remover listener específico
        const index = listeners.findIndex(listener => listener.id === listenerId);
        if (index !== -1) {
            listeners.splice(index, 1);
            this.logger.debug(`Listener removido: ${eventName} (ID: ${listenerId})`);
            
            // Si no quedan listeners, remover el evento
            if (listeners.length === 0) {
                this.events.delete(eventName);
            }
            
            return true;
        }
        
        return false;
    }
    
    /**
     * Emitir un evento
     */
    emit(eventName, ...args) {
        if (!this.events.has(eventName)) {
            this.logger.debug(`No hay listeners para evento: ${eventName}`);
            return false;
        }
        
        const listeners = this.events.get(eventName);
        let callbackCount = 0;
        
        for (const listener of listeners) {
            try {
                listener.callback.apply(listener.context, args);
                callbackCount++;
            } catch (error) {
                this.logger.error(`Error en callback para ${eventName}:`, error);
            }
        }
        
        this.logger.debug(`Evento emitido: ${eventName} (${callbackCount} callbacks ejecutados)`);
        return callbackCount > 0;
    }
    
    /**
     * Emitir evento de forma asíncrona
     */
    async emitAsync(eventName, ...args) {
        if (!this.events.has(eventName)) {
            this.logger.debug(`No hay listeners para evento: ${eventName}`);
            return false;
        }
        
        const listeners = this.events.get(eventName);
        const promises = [];
        
        for (const listener of listeners) {
            try {
                const result = listener.callback.apply(listener.context, args);
                if (result instanceof Promise) {
                    promises.push(result);
                }
            } catch (error) {
                this.logger.error(`Error en callback asíncrono para ${eventName}:`, error);
            }
        }
        
        if (promises.length > 0) {
            await Promise.allSettled(promises);
        }
        
        this.logger.debug(`Evento asíncrono emitido: ${eventName} (${listeners.length} callbacks ejecutados)`);
        return listeners.length > 0;
    }
    
    /**
     * Listar todos los eventos registrados
     */
    getRegisteredEvents() {
        const eventList = [];
        
        for (const [eventName, listeners] of this.events) {
            eventList.push({
                name: eventName,
                listenerCount: listeners.length,
                listeners: listeners.map(l => l.id)
            });
        }
        
        return eventList;
    }
    
    /**
     * Limpiar todos los eventos
     */
    clear() {
        const eventCount = this.events.size;
        this.events.clear();
        this.logger.info(`Bus de eventos limpiado (${eventCount} eventos removidos)`);
    }
    
    /**
     * Verificar si hay listeners para un evento
     */
    hasListeners(eventName) {
        return this.events.has(eventName) && this.events.get(eventName).length > 0;
    }
    
    /**
     * Obtener número de listeners para un evento
     */
    getListenerCount(eventName) {
        if (!this.events.has(eventName)) {
            return 0;
        }
        return this.events.get(eventName).length;
    }
    
    /**
     * Generar ID único para listeners
     */
    generateId() {
        return `listener_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Crear namespace para eventos
     */
    namespace(namespaceName) {
        return {
            on: (eventName, callback, context) => 
                this.on(`${namespaceName}:${eventName}`, callback, context),
            
            once: (eventName, callback, context) => 
                this.once(`${namespaceName}:${eventName}`, callback, context),
            
            off: (eventName, listenerId) => 
                this.off(`${namespaceName}:${eventName}`, listenerId),
            
            emit: (eventName, ...args) => 
                this.emit(`${namespaceName}:${eventName}`, ...args),
            
            emitAsync: (eventName, ...args) => 
                this.emitAsync(`${namespaceName}:${eventName}`, ...args)
        };
    }
}

// Crear instancia global
window.EventBus = EventBus;
window.eventBus = new EventBus();