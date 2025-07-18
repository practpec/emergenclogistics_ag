/**
 * Interfaz de usuario para Algoritmo Genético
 */
import { Logger } from '../../core/logger.js';

export class AGUI {
    constructor(templateLoader) {
        this.templateLoader = templateLoader;
        this.logger = new Logger('AGUI');
        this.currentMapData = null;
        this.activeTab = 'resumen';
    }

    async init() {
        await this.loadAGContent();
        this.logger.info('UI del AG inicializada');
    }

    async loadAGContent() {
        const agContent = document.getElementById('ag-content');
        if (!agContent) {
            this.logger.warn('Contenedor AG no encontrado');
            return;
        }

        agContent.innerHTML = `
            <!-- Datos del Mapa Base -->
            <div class="ag-summary" id="map-summary">
                <h3>Datos del Mapa Base</h3>
                <div class="summary-content" id="summary-content">
                    <div class="no-map-data">
                        <div class="empty-state">
                            <p class="warning-text">No hay datos de mapa disponibles</p>
                            <p>Para usar el algoritmo genético, primero debes generar un mapa en la pestaña correspondiente.</p>
                            <button onclick="window.app.showModule('maps')" class="btn btn-primary">
                                Ir a Generar Mapa
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Configuración del Escenario -->
            <div class="scenario-config" id="scenario-config" style="display: none;">
                <h3>Configuración del Escenario de Emergencia</h3>
                
                <div class="config-grid">
                    <!-- Columna izquierda: Tipo de Desastre -->
                    <div class="config-column">
                        <div class="config-section">
                            <h4>Tipo de Desastre</h4>
                            <select id="tipo-desastre" class="form-control" onchange="mostrarDetallesDesastre()">
                                ${this.getDisasterOptions()}
                            </select>
                            
                            <div class="disaster-details" id="disaster-details">
                                <!-- Detalles del desastre seleccionado -->
                            </div>
                        </div>
                    </div>

                    <!-- Columna derecha: Configuración de Vehículos -->
                    <div class="config-column">
                        <div class="config-section">
                            <h4>Configuración de Vehículos</h4>
                            
                            <div class="vehicle-controls-grid">
                                <div class="control-group">
                                    <label for="cantidad-vehiculos">Cantidad total:</label>
                                    <input type="number" id="cantidad-vehiculos" min="1" max="10" value="3" 
                                           onchange="actualizarVehiculos()" class="form-control">
                                </div>
                                
                                <div class="control-group">
                                    <button type="button" onclick="agregarVehiculo()" class="btn btn-secondary">
                                        Agregar Vehículo
                                    </button>
                                </div>
                                
                                <div class="control-group">
                                    <button type="button" onclick="configuracionAutomatica()" class="btn btn-info">
                                        Auto Configurar
                                    </button>
                                </div>
                            </div>

                            <div class="vehicles-table-container" id="vehicles-list">
                                <!-- Tabla de vehículos generada dinámicamente -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Botón Generar -->
                <div class="actions">
                    <button onclick="generarEscenario()" class="btn btn-primary btn-large" id="btn-generar-escenario">
                        Generar Escenario Completo
                    </button>
                </div>
            </div>

            <!-- Resultado del Escenario -->
            <div class="scenario-result" id="scenario-result" style="display: none;">
                <h3>Escenario de Emergencia Generado</h3>
                
                <div class="scenario-overview" id="scenario-overview">
                    <!-- Resumen general -->
                </div>
                
                <div class="scenario-tabs">
                    <button class="tab-btn active" onclick="showTab('resumen')">Resumen</button>
                    <button class="tab-btn" onclick="showTab('vehiculos')">Vehículos</button>
                    <button class="tab-btn" onclick="showTab('rutas')">Rutas</button>
                    <button class="tab-btn" onclick="showTab('prioridades')">Prioridades</button>
                </div>
                
                <div class="tab-content">
                    <div id="tab-resumen" class="tab-panel active">
                        <!-- Contenido de resumen -->
                    </div>
                    <div id="tab-vehiculos" class="tab-panel">
                        <!-- Contenido de vehículos -->
                    </div>
                    <div id="tab-rutas" class="tab-panel">
                        <!-- Contenido de rutas -->
                    </div>
                    <div id="tab-prioridades" class="tab-panel">
                        <!-- Contenido de prioridades -->
                    </div>
                </div>
                
                <div class="actions">
                    <button onclick="ejecutarAG()" class="btn btn-success">
                        Ejecutar Algoritmo Genético
                    </button>
                    <button onclick="exportarEscenario()" class="btn btn-secondary">
                        Exportar Escenario JSON
                    </button>
                    <button onclick="resetearEscenario()" class="btn btn-warning">
                        Regenerar Escenario
                    </button>
                </div>
            </div>
        `;
    }

    getDisasterOptions() {
        if (!window.ENTITIES_DATA?.tipos_desastre) {
            return '<option value="inundacion">Inundación</option>';
        }

        return window.ENTITIES_DATA.tipos_desastre.map(disaster => 
            `<option value="${disaster.tipo}">${disaster.tipo.charAt(0).toUpperCase() + disaster.tipo.slice(1)}</option>`
        ).join('');
    }

    setMapData(mapData) {
        this.currentMapData = mapData;
        this.updateMapSummary();
    }

    updateMapSummary() {
        const summaryContent = document.getElementById('summary-content');
        const scenarioConfig = document.getElementById('scenario-config');
        
        if (!summaryContent) return;
        
        if (this.currentMapData) {
            let totalRutas = 0;
            if (this.currentMapData.rutas_data) {
                this.currentMapData.rutas_data.forEach(destino => {
                    totalRutas += destino.rutas ? destino.rutas.length : 0;
                });
            }
            
            summaryContent.innerHTML = `
                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="summary-label">Punto de Inicio</span>
                        <span class="summary-value">${this.currentMapData.punto_inicio || 'No definido'}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Destinos</span>
                        <span class="summary-value">${this.currentMapData.nodos_secundarios ? this.currentMapData.nodos_secundarios.length : 0}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Rutas Generadas</span>
                        <span class="summary-value">${totalRutas}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Estado</span>
                        <span class="summary-value">Listo</span>
                    </div>
                </div>
            `;
            
            if (scenarioConfig) {
                scenarioConfig.style.display = 'block';
                this.showDisasterDetails();
                this.updateVehicles();
            }
        } else {
            summaryContent.innerHTML = `
                <div class="no-map-data">
                    <div class="empty-state">
                        <p class="warning-text">No hay datos de mapa disponibles</p>
                        <p>Para usar el algoritmo genético, primero debes generar un mapa en la pestaña correspondiente.</p>
                        <button onclick="window.app.showModule('maps')" class="btn btn-primary">
                            Ir a Generar Mapa
                        </button>
                    </div>
                </div>
            `;
            if (scenarioConfig) {
                scenarioConfig.style.display = 'none';
            }
        }
    }

    showDisasterDetails() {
        const select = document.getElementById('tipo-desastre');
        const detailsDiv = document.getElementById('disaster-details');
        
        if (!select || !detailsDiv) return;

        const selectedType = select.value;
        const disasters = window.ENTITIES_DATA?.tipos_desastre || [];
        const disaster = disasters.find(d => d.tipo === selectedType);
        
        if (disaster) {
            const prioritiesTable = disaster.prioridad.map(p => `
                <tr>
                    <td>${p.categoria}</td>
                    <td><span class="priority-level ${p.nivel}">${p.nivel}</span></td>
                </tr>
            `).join('');

            detailsDiv.innerHTML = `
                <h5>Prioridades de Insumos - ${disaster.tipo.charAt(0).toUpperCase() + disaster.tipo.slice(1)}</h5>
                <p style="margin-bottom: 15px; color: var(--color-text-secondary); font-size: 0.9em;">
                    El algoritmo genético utilizará estas prioridades para optimizar la distribución:
                </p>
                <table class="priority-table">
                    <thead>
                        <tr>
                            <th>Categoría de Insumo</th>
                            <th>Nivel de Prioridad</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${prioritiesTable}
                    </tbody>
                </table>
            `;
        }
    }

    updateVehicles() {
        const cantidad = parseInt(document.getElementById('cantidad-vehiculos')?.value) || 3;
        const vehiclesList = document.getElementById('vehicles-list');
        
        if (!vehiclesList) return;

        if (cantidad === 0) {
            vehiclesList.innerHTML = '<p style="text-align: center; color: var(--color-text-muted); padding: 20px;">No hay vehículos configurados</p>';
            return;
        }

        const vehicleTypes = window.ENTITIES_DATA?.tipos_vehiculos || [];
        
        let tableRows = '';
        for (let i = 0; i < cantidad; i++) {
            const vehicleOptions = vehicleTypes.map(v => 
                `<option value="${v.tipo}" data-modelo="${v.modelo}" data-capacidad="${v.maximo_peso_ton}" data-velocidad="${v.velocidad_kmh}" data-consumo="${v.consumo_litros_km}">
                    ${v.modelo} (${v.tipo})
                </option>`
            ).join('');

            tableRows += `
                <tr>
                    <td>Vehículo ${i + 1}</td>
                    <td>
                        <select class="vehicle-select vehicle-type" data-index="${i}" onchange="updateVehicleDetails(${i})">
                            ${vehicleOptions}
                        </select>
                    </td>
                    <td id="vehicle-specs-${i}">-</td>
                    <td>
                        <button type="button" onclick="removeVehicle(${i})" class="btn btn-danger btn-small">
                            Eliminar
                        </button>
                    </td>
                </tr>
            `;
        }
        
        vehiclesList.innerHTML = `
            <table class="vehicles-table">
                <thead>
                    <tr>
                        <th>Identificador</th>
                        <th>Tipo de Vehículo</th>
                        <th>Especificaciones</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableRows}
                </tbody>
            </table>
        `;
        
        // Actualizar especificaciones de todos los vehículos
        for (let i = 0; i < cantidad; i++) {
            this.updateVehicleDetails(i);
        }
    }

    updateVehicleDetails(index) {
        const select = document.querySelector(`[data-index="${index}"]`);
        const specsCell = document.getElementById(`vehicle-specs-${index}`);
        
        if (!select || !specsCell) return;

        const selectedOption = select.selectedOptions[0];
        if (selectedOption) {
            const capacidad = selectedOption.dataset.capacidad;
            const velocidad = selectedOption.dataset.velocidad;
            const consumo = selectedOption.dataset.consumo;

            specsCell.innerHTML = `${capacidad}t • ${velocidad}km/h • ${consumo}L/km`;
        }
    }

    addVehicle() {
        const cantidadInput = document.getElementById('cantidad-vehiculos');
        if (cantidadInput) {
            const nuevaCantidad = parseInt(cantidadInput.value) + 1;
            
            if (nuevaCantidad <= 10) {
                cantidadInput.value = nuevaCantidad;
                this.updateVehicles();
            } else {
                alert('Máximo 10 vehículos permitidos');
            }
        }
    }

    removeVehicle(index) {
        const cantidadInput = document.getElementById('cantidad-vehiculos');
        if (cantidadInput) {
            const nuevaCantidad = Math.max(1, parseInt(cantidadInput.value) - 1);
            cantidadInput.value = nuevaCantidad;
            this.updateVehicles();
        }
    }

    autoConfigureVehicles() {
        if (!this.currentMapData?.nodos_secundarios) {
            alert('Genera un mapa primero para usar la configuración automática');
            return;
        }

        const numDestinos = this.currentMapData.nodos_secundarios.length;
        const cantidadInput = document.getElementById('cantidad-vehiculos');
        
        if (cantidadInput) {
            // Configurar cantidad óptima (igual al número de destinos)
            cantidadInput.value = Math.min(numDestinos, 10);
            this.updateVehicles();
            
            // Distribución automática de tipos de vehículos
            const vehicleSelects = document.querySelectorAll('.vehicle-type');
            const tipos = ['camion', 'van', 'auto'];
            
            vehicleSelects.forEach((select, index) => {
                const tipoIndex = index % tipos.length;
                select.value = tipos[tipoIndex];
                this.updateVehicleDetails(index);
            });

            alert(`Configuración automática aplicada:\n- ${cantidadInput.value} vehículos\n- Distribución equilibrada de tipos`);
        }
    }

    getScenarioFormData() {
        const tipoDesastre = document.getElementById('tipo-desastre')?.value;
        const vehiculos = [];
        
        document.querySelectorAll('.vehicle-type').forEach((select, index) => {
            vehiculos.push({
                vehiculo_id: index + 1,
                tipo: select.value
            });
        });

        return {
            tipo_desastre: tipoDesastre,
            vehiculos: vehiculos
        };
    }

    showScenarioResult(escenario) {
        const resultDiv = document.getElementById('scenario-result');
        const overviewDiv = document.getElementById('scenario-overview');
        
        if (!resultDiv || !overviewDiv) return;
        
        // Mostrar resumen general
        overviewDiv.innerHTML = `
            <h4>Escenario: ${escenario.tipo_desastre.charAt(0).toUpperCase() + escenario.tipo_desastre.slice(1)}</h4>
            <div class="overview-stats">
                <div class="stat-item">
                    <span class="stat-value">${escenario.estadisticas.total_destinos}</span>
                    <span class="stat-label">Destinos</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${escenario.estadisticas.total_vehiculos}</span>
                    <span class="stat-label">Vehículos</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${escenario.estadisticas.rutas_abiertas}</span>
                    <span class="stat-label">Rutas Abiertas</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${escenario.estadisticas.rutas_cerradas}</span>
                    <span class="stat-label">Rutas Bloqueadas</span>
                </div>
            </div>
        `;

        // Actualizar contenido de tabs
        this.updateTabContent(escenario);
        
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({ behavior: 'smooth' });
        
        this.logger.info('Resultado del escenario mostrado');
    }

    updateTabContent(escenario) {
        // Tab Resumen
        const tabResumen = document.getElementById('tab-resumen');
        if (tabResumen) {
            tabResumen.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Aspecto</th>
                            <th>Valor</th>
                            <th>Detalles</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Tipo de Desastre</td>
                            <td>${escenario.tipo_desastre.charAt(0).toUpperCase() + escenario.tipo_desastre.slice(1)}</td>
                            <td>Configuración de prioridades específicas</td>
                        </tr>
                        <tr>
                            <td>Punto de Partida</td>
                            <td>${escenario.punto_partida}</td>
                            <td>Ubicación base para distribución</td>
                        </tr>
                        <tr>
                            <td>Total Destinos</td>
                            <td>${escenario.estadisticas.total_destinos}</td>
                            <td>Ubicaciones que requieren ayuda</td>
                        </tr>
                        <tr>
                            <td>Total Rutas</td>
                            <td>${escenario.estadisticas.total_rutas}</td>
                            <td>Caminos disponibles generados</td>
                        </tr>
                        <tr>
                            <td>Rutas Disponibles</td>
                            <td>${escenario.estadisticas.rutas_abiertas}</td>
                            <td>Caminos transitables</td>
                        </tr>
                        <tr>
                            <td>Rutas Bloqueadas</td>
                            <td>${escenario.estadisticas.rutas_cerradas}</td>
                            <td>Caminos no disponibles</td>
                        </tr>
                    </tbody>
                </table>
            `;
        }

        // Tab Vehículos
        const tabVehiculos = document.getElementById('tab-vehiculos');
        if (tabVehiculos) {
            const vehiculosTable = escenario.vehiculos_disponibles.map(v => `
                <tr>
                    <td>Vehículo ${v.vehiculo_id}</td>
                    <td>${v.modelo}</td>
                    <td>${v.tipo}</td>
                    <td>${v.capacidad_kg} kg</td>
                    <td>${v.velocidad_kmh} km/h</td>
                    <td>${v.consumo_litros_km} L/km</td>
                </tr>
            `).join('');
            
            tabVehiculos.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Modelo</th>
                            <th>Tipo</th>
                            <th>Capacidad</th>
                            <th>Velocidad</th>
                            <th>Consumo</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${vehiculosTable}
                    </tbody>
                </table>
            `;
        }

        // Tab Rutas
        const tabRutas = document.getElementById('tab-rutas');
        if (tabRutas) {
            const rutasTable = escenario.rutas_estado.map(r => `
                <tr>
                    <td>Ruta ${r.id_destino_ruta}</td>
                    <td>${r.destino}</td>
                    <td>${r.distancia_km} km</td>
                    <td><span class="route-status ${r.estado}">${r.estado}</span></td>
                    <td>${r.razon_bloqueo || 'N/A'}</td>
                    <td>${r.vehiculos_permitidos.join(', ')}</td>
                </tr>
            `).join('');
            
            tabRutas.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Destino</th>
                            <th>Distancia</th>
                            <th>Estado</th>
                            <th>Razón Bloqueo</th>
                            <th>Vehículos Permitidos</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rutasTable}
                    </tbody>
                </table>
            `;
        }

        // Tab Prioridades
        const tabPrioridades = document.getElementById('tab-prioridades');
        if (tabPrioridades && escenario.desastre_detalles) {
            const prioridadesTable = escenario.desastre_detalles.prioridad.map(p => `
                <tr>
                    <td>${p.categoria}</td>
                    <td><span class="priority-level ${p.nivel}">${p.nivel}</span></td>
                    <td>${this.getPriorityDescription(p.nivel)}</td>
                </tr>
            `).join('');
            
            tabPrioridades.innerHTML = `
                <h4>Prioridades para ${escenario.tipo_desastre}</h4>
                <p style="margin-bottom: 20px; color: var(--color-text-secondary);">
                    El algoritmo genético utilizará estas prioridades para optimizar la distribución de insumos:
                </p>
                
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Categoría de Insumo</th>
                            <th>Nivel de Prioridad</th>
                            <th>Descripción</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${prioridadesTable}
                    </tbody>
                </table>
            `;
        }
    }

    getPriorityDescription(nivel) {
        switch(nivel) {
            case 'alta': return 'Crítico para la supervivencia inmediata';
            case 'media': return 'Importante para bienestar y recuperación';
            case 'baja': return 'Útil para mejorar condiciones generales';
            default: return 'Sin descripción';
        }
    }

    showTab(tabName) {
        // Ocultar todos los tabs
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Mostrar tab seleccionado
        const targetPanel = document.getElementById(`tab-${tabName}`);
        const targetBtn = document.querySelector(`[onclick="showTab('${tabName}')"]`);
        
        if (targetPanel) targetPanel.classList.add('active');
        if (targetBtn) targetBtn.classList.add('active');
        
        this.activeTab = tabName;
    }

    showAGResults(result) {
        // TODO: Implementar visualización de resultados del AG
        alert('Resultados del AG: ' + JSON.stringify(result, null, 2));
        this.logger.info('Resultados del AG mostrados');
    }
}