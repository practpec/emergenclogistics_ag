/**
 * Módulo del Algoritmo Genético
 */
class AGModule extends BaseModule {
    constructor() {
        super('AGModule');
        this.currentMapData = null;
        this.currentScenario = null;
        this.vehiculosDisponibles = [];
        this.tiposDesastre = [];
        this.categoriasInsumos = [];
    }
    
    async onInit() {
        this.loadEntityData();
        this.setupEventHandlers();
    }
    
    async loadEntityData() {
        try {
            this.vehiculosDisponibles = await apiClient.getEntityData('vehiculos');
            this.tiposDesastre = await apiClient.getEntityData('desastres');
            this.categoriasInsumos = await apiClient.getEntityData('categorias_insumos');
        } catch (error) {
            this.logger.error('Error cargando datos de entidades:', error);
        }
    }
    
    setupEventHandlers() {
        eventBus.on('data:map-updated', (data) => {
            this.setMapData(data.data);
        });
        
        const generarEscenarioBtn = this.findElement('#generar-escenario-btn', false);
        if (generarEscenarioBtn) {
            this.addEventListener(generarEscenarioBtn, 'click', this.generarEscenario);
        }
        
        const ejecutarAGBtn = this.findElement('#ejecutar-ag-btn', false);
        if (ejecutarAGBtn) {
            this.addEventListener(ejecutarAGBtn, 'click', this.ejecutarAlgoritmoGenetico);
        }
    }
    
    setMapData(mapData) {
        this.currentMapData = mapData;
        this.updateMapDataDisplay();
        this.enableScenarioGeneration();
    }
    
    updateMapDataDisplay() {
        const summaryContent = this.findElement('#summary-content');
        
        if (!this.currentMapData) {
            summaryContent.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #718096;">
                    <p>No hay datos de mapa disponibles</p>
                    <button onclick="showModule('mapas')" class="btn btn-primary">Ir a Generar Mapa</button>
                </div>
            `;
            return;
        }
        
        const data = this.currentMapData;
        const totalRutas = data.rutas_data ? data.rutas_data.reduce((sum, d) => sum + (d.rutas ? d.rutas.length : 0), 0) : 0;
        
        summaryContent.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div>
                    <p><strong>Estado:</strong> ${data.punto_inicio || 'N/A'}</p>
                    <p><strong>Municipio:</strong> ${data.municipio_info?.nombre_municipio || 'N/A'}</p>
                    <p><strong>Punto de Salida:</strong> ${data.nodo_principal?.nombre_localidad || 'N/A'}</p>
                    <p><strong>Coordenadas:</strong> ${data.nodo_principal ? `${data.nodo_principal.lat.toFixed(4)}, ${data.nodo_principal.lng.toFixed(4)}` : 'N/A'}</p>
                </div>
                <div>
                    <p><strong>Total Destinos:</strong> ${data.nodos_secundarios?.length || 0}</p>
                    <p><strong>Total Rutas:</strong> ${totalRutas}</p>
                    <p><strong>Población Base:</strong> ${data.nodo_principal?.poblacion ? data.nodo_principal.poblacion.toLocaleString() : 'N/A'}</p>
                </div>
            </div>
            
            <div style="border-top: 1px solid #333; padding-top: 15px;">
                <h4 style="margin-bottom: 10px; color: #ffd700;">Destinos Disponibles</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    ${this.generateDestinosGrid()}
                </div>
            </div>
        `;
    }
    
    generateDestinosGrid() {
        if (!this.currentMapData?.nodos_secundarios) return '<p>No hay destinos</p>';
        
        return this.currentMapData.nodos_secundarios.map((nodo, index) => {
            const rutasCount = this.currentMapData.rutas_data[index]?.rutas?.length || 0;
            return `
                <div style="background: #2d3748; padding: 8px; border-radius: 4px; font-size: 0.85em;">
                    <div style="font-weight: bold; margin-bottom: 3px;">${nodo.nombre_localidad}</div>
                    <div style="color: #a0aec0;">Rutas: ${rutasCount}</div>
                    <div style="color: #a0aec0;">Población: ${nodo.poblacion?.toLocaleString() || 'N/A'}</div>
                </div>
            `;
        }).join('');
    }
    
    enableScenarioGeneration() {
        const generarBtn = this.findElement('#generar-escenario-btn', false);
        const form = this.findElement('#scenario-form', false);
        
        if (generarBtn) generarBtn.disabled = false;
        if (form) form.style.display = 'block';
    }
    
    async generarEscenario() {
        try {
            const scenarioData = this.getScenarioFormData();
            
            this.showLoading('Generando escenario...');
            
            const scenario = await apiClient.createScenario(scenarioData);
            this.currentScenario = scenario.escenario;
            
            this.updateScenarioDisplay();
            this.enableAlgorithmExecution();
            
        } catch (error) {
            this.showError('Error generando escenario: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    getScenarioFormData() {
        return {
            tipo_desastre: this.findElement('#tipo-desastre').value,
            vehiculos: this.getSelectedVehicles()
        };
    }
    
    getSelectedVehicles() {
        const vehicleCheckboxes = this.findElements('input[name="vehiculos"]:checked');
        return vehicleCheckboxes.map(cb => ({ tipo: cb.value }));
    }
    
    updateScenarioDisplay() {
        const scenarioContent = this.findElement('#scenario-content');
        
        if (!this.currentScenario) {
            scenarioContent.innerHTML = '<p>No hay escenario generado</p>';
            return;
        }
        
        const rutas = this.currentScenario.rutas_estado || [];
        const rutasAbiertas = rutas.filter(r => r.estado === 'abierta').length;
        const rutasCerradas = rutas.filter(r => r.estado === 'cerrada').length;
        
        scenarioContent.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div>
                    <p><strong>Tipo Desastre:</strong> ${this.currentScenario.tipo_desastre}</p>
                    <p><strong>Vehículos:</strong> ${this.currentScenario.vehiculos_disponibles?.length || 0}</p>
                </div>
                <div>
                    <p><strong>Rutas Abiertas:</strong> ${rutasAbiertas}</p>
                    <p><strong>Rutas Cerradas:</strong> ${rutasCerradas}</p>
                </div>
            </div>
            
            <div style="border-top: 1px solid #333; padding-top: 10px;">
                <h5 style="margin-bottom: 8px;">Estado de Rutas</h5>
                <div style="max-height: 200px; overflow-y: auto;">
                    ${this.generateRutasEstado()}
                </div>
            </div>
        `;
    }
    
    generateRutasEstado() {
        if (!this.currentScenario?.rutas_estado) return '<p>No hay rutas</p>';
        
        return this.currentScenario.rutas_estado.map(ruta => `
            <div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #444; font-size: 0.8em;">
                <span>${this.extractDestinationName(ruta.destino)}</span>
                <span style="color: ${ruta.estado === 'abierta' ? '#68d391' : '#fc8181'};">
                    ${ruta.estado === 'abierta' ? 'Abierta' : 'Cerrada'}
                    ${ruta.estado === 'cerrada' && ruta.razon_bloqueo ? ` (${ruta.razon_bloqueo})` : ''}
                </span>
            </div>
        `).join('');
    }
    
    extractDestinationName(destino) {
        if (typeof destino === 'string') {
            const match = destino.match(/^([^(,]+)/);
            return match ? match[1].trim() : destino;
        }
        return destino;
    }
    
    enableAlgorithmExecution() {
        const ejecutarBtn = this.findElement('#ejecutar-ag-btn', false);
        if (ejecutarBtn) ejecutarBtn.disabled = false;
    }
    
    async ejecutarAlgoritmoGenetico() {
        try {
            this.showLoading('Ejecutando algoritmo genético...');
            
            const resultado = await apiClient.executeGeneticAlgorithm(this.currentScenario);
            
            this.updateResultDisplay(resultado);
            
        } catch (error) {
            this.showError('Error ejecutando algoritmo: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    updateResultDisplay(resultado) {
        const resultContent = this.findElement('#result-content');
        
        if (resultado.success) {
            resultContent.innerHTML = `
                <div style="color: #68d391; margin-bottom: 10px;">
                    <strong>✓ Algoritmo ejecutado exitosamente</strong>
                </div>
                <div>${JSON.stringify(resultado.data, null, 2)}</div>
            `;
        } else {
            resultContent.innerHTML = `
                <div style="color: #ffd700; margin-bottom: 10px;">
                    <strong>ℹ ${resultado.message}</strong>
                </div>
                <p style="font-size: 0.9em; color: #a0aec0;">
                    El algoritmo genético está en desarrollo. Actualmente se puede generar el escenario
                    con datos reales de localidades mexicanas.
                </p>
            `;
        }
    }
}

window.AGModule = AGModule;