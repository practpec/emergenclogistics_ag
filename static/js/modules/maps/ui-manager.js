/**
 * Gestor de interfaz de usuario para el módulo de mapas
 */
class UIManager extends BaseModule {
    constructor() {
        super('UIManager');
        this.isLoading = false;
        this.isPanelCollapsed = false;
        this.activeDestination = null;
        this.highlightedRoute = null;
    }
    
    /**
     * Inicializar UI Manager
     */
    async onInit() {
        this.setupEventHandlers();
        this.logger.info('UI Manager inicializado');
    }
    
    /**
     * Configurar manejadores de eventos
     */
    setupEventHandlers() {
        // Eventos de teclado
        this.addEventListener(document, 'keydown', this.handleKeyboardShortcuts);
        
        // Eventos de redimensionamiento
        this.addEventListener(window, 'resize', Utils.debounce(this.handleResize.bind(this), 300));
    }
    
    /**
     * Manejar atajos de teclado
     */
    handleKeyboardShortcuts(event) {
        // Escape para limpiar resaltados
        if (event.key === 'Escape') {
            this.clearAllHighlights();
            event.preventDefault();
        }
        
        // Ctrl/Cmd + G para generar mapa
        if ((event.ctrlKey || event.metaKey) && event.key === 'g') {
            if (typeof generarMapa === 'function') {
                generarMapa();
            }
            event.preventDefault();
        }
    }
    
    /**
     * Manejar redimensionamiento de ventana
     */
    handleResize() {
        // Ajustar panel en móviles
        if (window.innerWidth <= 1024) {
            this.isPanelCollapsed = false;
            this.updatePanelState();
        }
    }
    
    /**
     * Mostrar loading
     */
    showLoading(message = AppConfig.messages.loading.map) {
        const loadingEl = this.findElement('#loading', false);
        const btn = this.findElement('#generar-btn', false);
        
        this.isLoading = true;
        
        if (loadingEl) {
            const messageEl = loadingEl.querySelector('p strong');
            if (messageEl) {
                messageEl.textContent = message;
            }
            loadingEl.classList.add('show');
        }
        
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = 'Generando...';
        }
    }
    
    /**
     * Ocultar loading
     */
    hideLoading() {
        const loadingEl = this.findElement('#loading', false);
        const btn = this.findElement('#generar-btn', false);
        
        this.isLoading = false;
        
        if (loadingEl) {
            loadingEl.classList.remove('show');
        }
        
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = 'Generar Rutas';
        }
    }
    
    /**
     * Validar formulario de mapa
     */
    validateMapForm() {
        const estado = this.findElement('#estado');
        const municipio = this.findElement('#municipio');
        const nNodos = this.findElement('#n_nodos');
        
        if (!estado || !estado.value) {
            this.showError('Por favor selecciona un estado');
            return false;
        }
        
        if (!municipio || !municipio.value) {
            this.showError('Por favor selecciona un municipio');
            return false;
        }
        
        const nNodosValue = parseInt(nNodos.value);
        if (!nNodos || nNodosValue < 1 || nNodosValue > 15) {
            this.showError('El número de destinos debe estar entre 1 y 15');
            return false;
        }
        
        return true;
    }
    
    /**
     * Obtener datos del formulario de mapa
     */
    getMapFormData() {
        return {
            estado: this.findElement('#estado').value,
            municipio: this.findElement('#municipio').value,
            nNodos: parseInt(this.findElement('#n_nodos').value)
        };
    }
    
    /**
     * Actualizar panel de rutas con nombres de localidades
     */
    async updateRoutesPanel(routesData) {
        const panelContent = this.findElement('#panel-content');
        
        if (!routesData || routesData.length === 0) {
            panelContent.innerHTML = `
                <div class="no-routes" style="padding: 40px 20px; text-align: center; color: #718096;">
                    <p>No se encontraron rutas</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        
        for (let i = 0; i < routesData.length; i++) {
            const destinoData = routesData[i];
            const rutas = destinoData.rutas || [];
            
            // Extraer nombre de la localidad del destino
            const destinoNombre = this.extractLocalidadName(destinoData.destino);
            
            html += `
                <div class="destination-item">
                    <div class="destination-header" onclick="toggleDestination(${i})" data-destination="${i}">
                        <div class="destination-title">
                            ${destinoNombre}
                            <div style="font-size: 0.8em; font-weight: normal; margin-top: 2px; color: #a0aec0;">
                                ${rutas.length} ruta${rutas.length !== 1 ? 's' : ''} • Población: ${this.formatPopulation(destinoData.destino)}
                            </div>
                        </div>
                        <div class="toggle-icon">▼</div>
                    </div>
                    <div class="routes-list" id="routes-${i}">
                        ${await this.generateRoutesHTML(rutas, i)}
                    </div>
                </div>
            `;
        }
        
        panelContent.innerHTML = html;
    }
    
    /**
     * Extraer nombre de localidad de la cadena completa
     */
    extractLocalidadName(destinoCompleto) {
        // El formato es: "NOMBRE_LOCALIDAD (Clave: XX-XXX-XXXX)"
        const match = destinoCompleto.match(/^([^(]+)/);
        if (match) {
            return match[1].trim();
        }
        return destinoCompleto;
    }
    
    /**
     * Formatear población desde la cadena de destino
     */
    formatPopulation(destinoCompleto) {
        // Intentar extraer población si está disponible en los datos
        // Por ahora retornar un placeholder
        return "N/A";
    }
    
    /**
     * Generar HTML para rutas
     */
    async generateRoutesHTML(rutas, destinationIndex) {
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
        
        for (let routeIndex = 0; routeIndex < rutas.length; routeIndex++) {
            const ruta = rutas[routeIndex];
            const routeId = `route-${destinationIndex}-${routeIndex}`;
            
            html += `
                <div class="route-item" id="${routeId}" 
                     data-destination="${destinationIndex}" data-route="${routeIndex}">
                    <div class="route-header">
                        <span class="route-type">${ruta.tipo || `Ruta ${routeIndex + 1}`}</span>
                        <div class="route-controls">
                            <button class="route-btn" onclick="highlightRoute(${destinationIndex}, ${routeIndex})" 
                                    title="Ver en mapa">
                                Ver
                            </button>
                        </div>
                    </div>
                    
                    <div class="route-details">
                        ${ruta.descripcion || 'Camino hacia el destino'}
                    </div>
                    
                    <div class="route-stats">
                        <div class="route-stat">
                            <span class="stat-icon">📏</span>
                            <span>${ruta.distancia.text}</span>
                        </div>
                        <div class="route-stat">
                            <span class="stat-icon">📍</span>
                            <span>${ruta.puntos_ruta ? ruta.puntos_ruta.length : 0} puntos</span>
                        </div>
                    </div>
                </div>
            `;
        }
        
        return html;
    }
    
    /**
     * Resaltar ruta en panel
     */
    highlightRouteInPanel(destinationIndex, routeIndex) {
        // Limpiar resaltados anteriores
        this.clearAllHighlights();
        
        const routeElement = this.findElement(`#route-${destinationIndex}-${routeIndex}`, false);
        if (routeElement) {
            routeElement.classList.add('highlighted');
            
            // Scroll hacia el elemento
            routeElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
            
            this.highlightedRoute = { destinationIndex, routeIndex };
        }
    }
    
    /**
     * Expandir destino en panel
     */
    expandDestination(destinationIndex) {
        const header = this.findElement(`[data-destination="${destinationIndex}"]`, false);
        const routesList = this.findElement(`#routes-${destinationIndex}`, false);
        
        if (header && routesList) {
            header.classList.add('active');
            routesList.classList.add('show');
            
            this.activeDestination = destinationIndex;
        }
    }
    
    /**
     * Toggle destino
     */
    toggleDestination(destinationIndex) {
        const header = this.findElement(`[data-destination="${destinationIndex}"]`, false);
        const routesList = this.findElement(`#routes-${destinationIndex}`, false);
        
        if (header && routesList) {
            const isActive = header.classList.contains('active');
            
            if (isActive) {
                header.classList.remove('active');
                routesList.classList.remove('show');
                this.activeDestination = null;
                return false;
            } else {
                // Colapsar otros destinos
                this.collapseAllDestinations();
                
                header.classList.add('active');
                routesList.classList.add('show');
                this.activeDestination = destinationIndex;
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Colapsar todos los destinos
     */
    collapseAllDestinations() {
        this.findElements('.destination-header').forEach(header => {
            header.classList.remove('active');
        });
        this.findElements('.routes-list').forEach(list => {
            list.classList.remove('show');
        });
        
        this.activeDestination = null;
    }
    
    /**
     * Toggle panel de rutas
     */
    toggleRoutesPanel() {
        const panel = this.findElement('.routes-panel', false);
        const btn = this.findElement('.collapse-btn', false);
        
        this.isPanelCollapsed = !this.isPanelCollapsed;
        this.updatePanelState();
        
        return this.isPanelCollapsed;
    }
    
    /**
     * Actualizar estado del panel
     */
    updatePanelState() {
        const panel = this.findElement('.routes-panel', false);
        const btn = this.findElement('.collapse-btn', false);
        
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
    
    /**
     * Actualizar encabezado del panel
     */
    updatePanelHeader(stats) {
        const headerTitle = this.findElement('.panel-header h3', false);
        
        if (headerTitle && stats) {
            headerTitle.innerHTML = `${stats.totalRoutes} Rutas para ${stats.totalDestinations} Destinos`;
        }
    }
    
    /**
     * Limpiar todos los resaltados
     */
    clearAllHighlights() {
        this.findElements('.route-item').forEach(item => {
            item.classList.remove('highlighted');
        });
        
        this.highlightedRoute = null;
    }
    
    /**
     * Mostrar estadísticas en UI
     */
    showRouteStatistics(stats) {
        // Crear elemento de estadísticas si no existe
        let statsElement = this.findElement('#route-stats', false);
        
        if (!statsElement) {
            const panelContent = this.findElement('#panel-content');
            statsElement = Utils.createElement('div', 'route-statistics');
            statsElement.id = 'route-stats';
            panelContent.insertBefore(statsElement, panelContent.firstChild);
        }
        
        statsElement.innerHTML = `
            <div class="stats-header">
                <h4>Estadísticas de Rutas</h4>
            </div>
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-label">Total Rutas</span>
                    <span class="stat-value">${stats.totalRoutes}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Distancia Total</span>
                    <span class="stat-value">${stats.totalDistance} km</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Ruta Más Larga</span>
                    <span class="stat-value">${stats.longestRoute} km</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Promedio</span>
                    <span class="stat-value">${stats.averageDistance} km</span>
                </div>
            </div>
        `;
    }
    
    /**
     * Obtener estado actual de la UI
     */
    getUIState() {
        return {
            isLoading: this.isLoading,
            isPanelCollapsed: this.isPanelCollapsed,
            activeDestination: this.activeDestination,
            highlightedRoute: this.highlightedRoute
        };
    }
}

// Registrar módulo globalmente
window.UIManager = UIManager;