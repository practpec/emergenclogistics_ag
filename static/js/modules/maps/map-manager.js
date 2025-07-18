/**
 * Gestor del mapa Leaflet
 */
class MapManager extends BaseModule {
    constructor() {
        super('MapManager');
        this.map = null;
        this.markers = [];
        this.routeLayers = [];
        this.currentBounds = null;
    }
    
    /**
     * Inicializar mapa
     */
    async onInit() {
        await this.initializeMap();
        this.setupMapControls();
    }
    
    /**
     * Crear instancia del mapa
     */
    async initializeMap() {
        const mapElement = this.findElement('#map');
        
        this.map = L.map(mapElement).setView(
            AppConfig.map.defaultCenter, 
            AppConfig.map.defaultZoom
        );
        
        // Agregar capa de tiles
        L.tileLayer(AppConfig.map.tileLayer, {
            attribution: AppConfig.map.attribution,
            maxZoom: AppConfig.map.maxZoom,
        }).addTo(this.map);
        
        // Agregar control de escala
        L.control.scale().addTo(this.map);
        
        this.logger.info('Mapa inicializado correctamente');
    }
    
    /**
     * Configurar controles del mapa
     */
    setupMapControls() {
        // Agregar eventos del mapa si es necesario
        this.map.on('click', (e) => {
            this.logger.debug(`Click en mapa: ${e.latlng}`);
        });
    }
    
    /**
     * Limpiar todos los elementos del mapa
     */
    clearMap() {
        this.logger.debug('Limpiando mapa');
        
        // Remover marcadores
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];
        
        // Remover rutas
        this.routeLayers.forEach(layer => this.map.removeLayer(layer));
        this.routeLayers = [];
        
        // Resetear bounds
        this.currentBounds = null;
    }
    
    /**
     * Agregar nodo principal
     */
    addPrincipalNode(nodeData) {
        const principalIcon = L.divIcon({
            className: 'custom-div-icon',
            html: await templateLoader.render('components/map-marker.html', {
                type: 'principal',
                pulseClass: 'pulse'
            }),
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        const marker = L.marker(
            [nodeData.lat, nodeData.lng], 
            { icon: principalIcon }
        ).addTo(this.map);
        
        marker.bindPopup(await templateLoader.render('components/node-popup.html', {
            title: nodeData.nombre,
            type: 'Nodo Principal',
            coordinates: `${nodeData.lat.toFixed(4)}, ${nodeData.lng.toFixed(4)}`
        }));
        
        this.markers.push(marker);
        this.updateBounds([nodeData.lat, nodeData.lng]);
        
        this.logger.debug(`Nodo principal agregado: ${nodeData.nombre}`);
        return marker;
    }
    
    /**
     * Agregar nodo secundario
     */
    addSecondaryNode(nodeData, index) {
        const secondaryIcon = L.divIcon({
            className: 'custom-div-icon',
            html: await templateLoader.render('components/map-marker.html', {
                type: 'secondary',
                index: index + 1
            }),
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });
        
        const marker = L.marker(
            [nodeData.lat, nodeData.lng], 
            { icon: secondaryIcon }
        ).addTo(this.map);
        
        marker.bindPopup(await templateLoader.render('components/node-popup.html', {
            title: `Destino ${index + 1}`,
            type: 'Destino',
            coordinates: `${nodeData.lat.toFixed(4)}, ${nodeData.lng.toFixed(4)}`,
            distance: `${nodeData.distancia_directa} km`
        }));
        
        this.markers.push(marker);
        this.updateBounds([nodeData.lat, nodeData.lng]);
        
        this.logger.debug(`Nodo secundario agregado: ${index + 1}`);
        return marker;
    }
    
    /**
     * Agregar ruta al mapa
     */
    addRoute(routeData, destinationIndex, routeIndex) {
        if (!routeData.puntos_ruta || routeData.puntos_ruta.length === 0) {
            this.logger.warn(`Ruta sin puntos: destino ${destinationIndex}, ruta ${routeIndex}`);
            return null;
        }
        
        const routePoints = routeData.puntos_ruta.map(punto => [punto.lat, punto.lng]);
        const color = Utils.getRouteColor(destinationIndex * 3 + routeIndex);
        
        const polyline = L.polyline(routePoints, {
            color: color,
            weight: 4,
            opacity: 0.7,
            dashArray: routeIndex % 2 === 0 ? null : '10, 5',
            className: `route-${destinationIndex}-${routeIndex}`
        }).addTo(this.map);
        
        polyline.bindPopup(await templateLoader.render('components/route-popup.html', {
            routeNumber: routeIndex + 1,
            destinationNumber: destinationIndex + 1,
            distance: routeData.distancia.text,
            type: routeData.tipo || 'Ruta'
        }));
        
        this.routeLayers.push(polyline);
        
        // Actualizar bounds con todos los puntos de la ruta
        routePoints.forEach(point => this.updateBounds(point));
        
        this.logger.debug(`Ruta agregada: destino ${destinationIndex}, ruta ${routeIndex}`);
        return polyline;
    }
    
    /**
     * Resaltar ruta específica
     */
    highlightRoute(destinationIndex, routeIndex) {
        this.logger.debug(`Resaltando ruta: destino ${destinationIndex}, ruta ${routeIndex}`);
        
        // Reducir opacidad de todas las rutas
        this.routeLayers.forEach(layer => {
            layer.setStyle({ opacity: 0.3, weight: 2 });
        });
        
        // Resaltar ruta específica
        const targetClass = `route-${destinationIndex}-${routeIndex}`;
        this.routeLayers.forEach(layer => {
            if (layer.options.className === targetClass) {
                layer.setStyle({ 
                    opacity: 1, 
                    weight: 6,
                    color: AppConfig.colors.danger
                });
                layer.bringToFront();
            }
        });
        
        // Emitir evento
        eventBus.emit('map:route-highlighted', { destinationIndex, routeIndex });
    }
    
    /**
     * Resetear resaltado de rutas
     */
    resetRouteHighlight() {
        this.logger.debug('Reseteando resaltado de rutas');
        
        this.routeLayers.forEach((layer, index) => {
            const originalColor = Utils.getRouteColor(index);
            layer.setStyle({ 
                opacity: 0.7, 
                weight: 4,
                color: originalColor
            });
        });
        
        // Emitir evento
        eventBus.emit('map:route-highlight-reset');
    }
    
    /**
     * Ajustar vista para mostrar todas las rutas
     */
    fitToRoutes() {
        if (this.currentBounds && this.currentBounds.isValid()) {
            this.map.fitBounds(this.currentBounds, { padding: [20, 20] });
            this.logger.debug('Vista ajustada a rutas');
        }
    }
    
    /**
     * Actualizar bounds del mapa
     */
    updateBounds(latLng) {
        if (!this.currentBounds) {
            this.currentBounds = L.latLngBounds();
        }
        this.currentBounds.extend(latLng);
    }
    
    /**
     * Obtener estadísticas del mapa
     */
    getMapStats() {
        return {
            markers: this.markers.length,
            routes: this.routeLayers.length,
            bounds: this.currentBounds ? this.currentBounds.toBBoxString() : null,
            center: this.map ? this.map.getCenter() : null,
            zoom: this.map ? this.map.getZoom() : null
        };
    }
    
    /**
     * Destruir mapa
     */
    destroy() {
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
        super.destroy();
    }
}

// Registrar módulo globalmente
window.MapManager = MapManager;