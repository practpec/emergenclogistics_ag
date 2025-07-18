/**
 * Gestor de interfaz de usuario para mapas
 */
import { Logger } from '../../core/logger.js';

export class UIManager {
    constructor(mapManager, templateLoader) {
        this.mapManager = mapManager;
        this.templateLoader = templateLoader;
        this.logger = new Logger('UIManager');
        this.isLoading = false;
        this.isPanelCollapsed = false;
    }

    toggleLoading(show) {
        const loading = document.getElementById('loading');
        const btn = document.getElementById('generar-btn');
        
        this.isLoading = show;
        
        if (show) {
            loading?.classList.add('show');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = 'Generando...';
            }
        } else {
            loading?.classList.remove('show');
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = 'Generar Mapa';
            }
        }
        
        this.logger.debug(`Loading: ${show ? 'mostrado' : 'oculto'}`);
    }

    showError(message) {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.innerHTML = `<strong>Error:</strong> ${message}`;
            errorDiv.classList.add('show');
            
            setTimeout(() => {
                errorDiv.classList.remove('show');
            }, 6000);
        }
        
        this.logger.warn(`Error mostrado: ${message}`);
    }

    async updateRoutesPanel(routesData) {
        const panelContent = document.getElementById('panel-content');
        
        if (!panelContent) {
            this.logger.warn('Panel de contenido no encontrado');
            return;
        }
        
        if (!routesData || routesData.length === 0) {
            panelContent.innerHTML = `
                <div class="no-routes">
                    <p>No se encontraron rutas</p>
                </div>
            `;
            return;
        }

        let html = '';
        
        for (const [index, destinoData] of routesData.entries()) {
            const rutas = destinoData.rutas || [];
            
            html += `
                <div class="destination-item">
                    <div class="destination-header" onclick="window.app.getModule('maps').toggleDestination(${index})" data-destination="${index}">
                        <div class="destination-title">
                            Destino ${index + 1}
                            <div style="font-size: 0.8em; font-weight: normal; margin-top: 2px;">
                                ${rutas.length} ruta${rutas.length !== 1 ? 's' : ''} disponible${rutas.length !== 1 ? 's' : ''}
                            </div>
                        </div>
                        <div class="toggle-icon">▼</div>
                    </div>
                    <div class="routes-list" id="routes-${index}">
                        ${await this._generateRoutesHTML(rutas, index)}
                    </div>
                </div>
            `;
        }
        
        panelContent.innerHTML = html;
        this.logger.debug(`Panel actualizado con ${routesData.length} destinos`);
    }

    async _generateRoutesHTML(rutas, destinationIndex) {
        if (rutas.length === 0) {
            return `
                <div class="route-item">
                    <div class="route-header">
                        <span class="route-type">Sin rutas disponibles</span>
                    </div>
                    <div class="route-details">
                        No se pudieron calcular rutas para este destino
                    </div>
                </div>
            `;
        }

        let html = '';
        
        for (const [routeIndex, ruta] of rutas.entries()) {
            const routeId = `route-${destinationIndex}-${routeIndex}`;
            
            html += `
                <div class="route-item" id="${routeId}" data-destination="${destinationIndex}" data-route="${routeIndex}">
                    <div class="route-header">
                        <span class="route-type">${ruta.tipo || 'Ruta ' + (routeIndex + 1)}</span>
                        <div class="route-controls">
                            <button class="route-btn" onclick="window.app.getModule('maps').highlightRoute(${destinationIndex}, ${routeIndex})" title="Ver en mapa">
                                Ver Ruta
                            </button>
                        </div>
                    </div>
                    
                    <div class="route-details">
                        ${ruta.descripcion || 'Camino hacia el destino'}
                    </div>
                    
                    <div class="route-stats">
                        <div class="route-stat">
                            <span>Distancia</span>
                            <span>${ruta.distancia.text}</span>
                        </div>
                        <div class="route-stat">
                            <span>Puntos</span>
                            <span>${ruta.puntos_ruta ? ruta.puntos_ruta.length : 0} puntos</span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        return html;
    }

    highlightRouteInPanel(destinationIndex, routeIndex) {
        document.querySelectorAll('.route-item').forEach(item => {
            item.classList.remove('highlighted');
        });

        const routeElement = document.getElementById(`route-${destinationIndex}-${routeIndex}`);
        if (routeElement) {
            routeElement.classList.add('highlighted');
            
            routeElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }
    }

    expandDestination(destinationIndex) {
        const header = document.querySelector(`[data-destination="${destinationIndex}"]`);
        const routesList = document.getElementById(`routes-${destinationIndex}`);
        
        if (header && routesList) {
            header.classList.add('active');
            routesList.classList.add('show');
        }
    }

    collapseAllDestinations() {
        document.querySelectorAll('.destination-header').forEach(header => {
            header.classList.remove('active');
        });
        document.querySelectorAll('.routes-list').forEach(list => {
            list.classList.remove('show');
        });
    }

    togglePanel() {
        const panel = document.querySelector('.routes-panel');
        const btn = document.querySelector('.collapse-btn');
        
        this.isPanelCollapsed = !this.isPanelCollapsed;
        
        if (panel && btn) {
            if (this.isPanelCollapsed) {
                panel.classList.add('collapsed');
                btn.innerHTML = '+';
            } else {
                panel.classList.remove('collapsed');
                btn.innerHTML = '−';
            }
        }
    }

    updatePanelHeader(stats) {
        const headerTitle = document.querySelector('.panel-header h3');
        if (headerTitle && stats) {
            headerTitle.innerHTML = `${stats.totalRoutes} Rutas para ${stats.totalDestinations} Destinos`;
        }
    }

    validateForm() {
        const estado = document.getElementById('estado')?.value;
        const nNodos = parseInt(document.getElementById('n_nodos')?.value);

        if (!estado) {
            this.showError('Por favor selecciona un estado');
            return false;
        }

        if (nNodos < 1 || nNodos > 15) {
            this.showError('El número de destinos debe estar entre 1 y 15');
            return false;
        }

        return true;
    }

    getFormValues() {
        return {
            estado: document.getElementById('estado')?.value,
            nNodos: parseInt(document.getElementById('n_nodos')?.value)
        };
    }
}