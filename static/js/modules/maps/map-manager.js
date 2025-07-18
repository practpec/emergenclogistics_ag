/**
 * Gestor del mapa Leaflet
 */
import { Logger } from '../../core/logger.js';

export class MapManager {
    constructor(config) {
        this.config = config;
        this.logger = new Logger('MapManager');
        this.map = null;
        this.markers = [];
        this.routeLayers = [];
        this.currentBounds = null;
    }
    
    init() {
        this.map = L.map('map').setView(
            this.config.maps.defaultCenter, 
            this.config.maps.defaultZoom
        );

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18,
        }).addTo(this.map);

        L.control.scale().addTo(this.map);
        
        this.logger.info('Mapa inicializado');
    }

    clearMap() {
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];

        this.routeLayers.forEach(layer => this.map.removeLayer(layer));
        this.routeLayers = [];

        this.currentBounds = null;
        this.logger.debug('Mapa limpiado');
    }

    addPrincipalNode(nodeData) {
        const principalIcon = L.divIcon({
            className: 'custom-div-icon',
            html: `
                <div class="marker-pin">
                    <div class="pulse"></div>
                </div>
            `,
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        const marker = L.marker(
            [nodeData.lat, nodeData.lng], 
            { icon: principalIcon }
        ).addTo(this.map);

        marker.bindPopup(`
            <div style="text-align: center; padding: 10px;">
                <h4>${nodeData.nombre}</h4>
                <p><strong>Nodo Principal</strong></p>
                <p>Coordenadas: ${nodeData.lat.toFixed(4)}, ${nodeData.lng.toFixed(4)}</p>
            </div>
        `);

        this.markers.push(marker);
        this._updateBounds([nodeData.lat, nodeData.lng]);
        
        this.logger.debug(`Nodo principal agregado: ${nodeData.nombre}`);
        return marker;
    }

    addSecondaryNode(nodeData, index) {
        const secondaryIcon = L.divIcon({
            className: 'custom-div-icon',
            html: `
                <div class="marker-pin secondary-marker" data-destination="${index}">
                    <div style="
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%) rotate(45deg);
                        color: white;
                        font-weight: bold;
                        font-size: 12px;
                    ">${index + 1}</div>
                </div>
            `,
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        const marker = L.marker(
            [nodeData.lat, nodeData.lng], 
            { icon: secondaryIcon }
        ).addTo(this.map);

        marker.bindPopup(`
            <div style="padding: 15px;">
                <h4>Destino ${index + 1}</h4>
                <hr style="margin: 10px 0;">
                <p><strong>Coordenadas:</strong><br>${nodeData.lat.toFixed(4)}, ${nodeData.lng.toFixed(4)}</p>
                <p><strong>Distancia:</strong> ${nodeData.distancia_directa} km</p>
            </div>
        `);

        this.markers.push(marker);
        this._updateBounds([nodeData.lat, nodeData.lng]);
        
        this.logger.debug(`Nodo secundario agregado: ${index + 1}`);
        return marker;
    }

    addRoute(routeData, destinationIndex, routeIndex) {
        if (!routeData.puntos_ruta || routeData.puntos_ruta.length === 0) {
            this.logger.warn(`Ruta sin puntos: destino ${destinationIndex}, ruta ${routeIndex}`);
            return null;
        }

        const routePoints = routeData.puntos_ruta.map(punto => [punto.lat, punto.lng]);
        
        const polyline = L.polyline(routePoints, {
            color: this.config.getRouteColor(destinationIndex * 3 + routeIndex),
            weight: 4,
            opacity: 0.7,
            dashArray: routeIndex % 2 === 0 ? null : '10, 5',
            className: `route-${destinationIndex}-${routeIndex}`
        }).addTo(this.map);

        polyline.bindPopup(`
            <div style="text-align: center;">
                <h4>Ruta ${routeIndex + 1} hacia Destino ${destinationIndex + 1}</h4>
                <p><strong>${routeData.distancia.text}</strong></p>
                <p><strong>Tipo:</strong> ${routeData.tipo || 'Ruta'}</p>
            </div>
        `);

        this.routeLayers.push(polyline);
        routePoints.forEach(point => this._updateBounds(point));
        
        this.logger.debug(`Ruta agregada: ${destinationIndex}-${routeIndex}`);
        return polyline;
    }

    highlightRoute(destinationIndex, routeIndex) {
        // Resetear todas las rutas
        this.routeLayers.forEach(layer => {
            layer.setStyle({ opacity: 0.3, weight: 2 });
        });

        // Destacar ruta específica
        const targetClass = `route-${destinationIndex}-${routeIndex}`;
        this.routeLayers.forEach(layer => {
            if (layer.options.className === targetClass) {
                layer.setStyle({ 
                    opacity: 1, 
                    weight: 6,
                    color: '#e74c3c'
                });
                layer.bringToFront();
            }
        });
        
        this.logger.debug(`Ruta destacada: ${destinationIndex}-${routeIndex}`);
    }

    resetRouteHighlight() {
        this.routeLayers.forEach((layer, index) => {
            const originalColor = this.config.getRouteColor(index);
            layer.setStyle({ 
                opacity: 0.7, 
                weight: 4,
                color: originalColor
            });
        });
    }

    fitToRoutes() {
        if (this.currentBounds) {
            this.map.fitBounds(this.currentBounds, { padding: [20, 20] });
            this.logger.debug('Vista ajustada a rutas');
        }
    }

    _updateBounds(latLng) {
        if (!this.currentBounds) {
            this.currentBounds = L.latLngBounds();
        }
        this.currentBounds.extend(latLng);
    }
}