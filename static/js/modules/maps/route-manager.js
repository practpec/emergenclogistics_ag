/**
 * Gestor de rutas y datos de navegación
 */
class RouteManager extends BaseModule {
    constructor() {
        super('RouteManager');
        this.routesData = [];
        this.currentStats = null;
    }
    
    /**
     * Obtener rutas completas del servidor
     */
    async getCompleteRoutes(estado, nNodos) {
        try {
            this.logger.info(`Obteniendo rutas: ${estado}, ${nNodos} nodos`);
            
            const data = await apiClient.generateCompleteRoutes(estado, nNodos);
            this.routesData = data.rutas_data;
            this.currentStats = this.calculateRouteStats();
            
            this.logger.info(`Rutas obtenidas: ${this.currentStats.totalRoutes} rutas para ${this.currentStats.totalDestinations} destinos`);
            
            return data;
            
        } catch (error) {
            this.logger.error('Error obteniendo rutas completas:', error);
            throw error;
        }
    }
    
    /**
     * Obtener todas las rutas almacenadas
     */
    getAllRoutes() {
        return this.routesData;
    }
    
    /**
     * Obtener rutas para un destino específico
     */
    getRoutesForDestination(destinationIndex) {
        const destino = this.routesData.find(d => d.indice === destinationIndex);
        return destino ? destino.rutas : [];
    }
    
    /**
     * Obtener ruta específica
     */
    getRoute(destinationIndex, routeIndex) {
        const routes = this.getRoutesForDestination(destinationIndex);
        return routes[routeIndex] || null;
    }
    
    /**
     * Calcular estadísticas de rutas
     */
    calculateRouteStats() {
        let totalRoutes = 0;
        let totalDistance = 0;
        let longestRoute = 0;
        let shortestRoute = Infinity;
        
        this.routesData.forEach(destino => {
            if (destino.rutas) {
                destino.rutas.forEach(ruta => {
                    totalRoutes++;
                    const distanceKm = ruta.distancia.value / 1000;
                    
                    totalDistance += distanceKm;
                    
                    if (distanceKm > longestRoute) {
                        longestRoute = distanceKm;
                    }
                    
                    if (distanceKm < shortestRoute) {
                        shortestRoute = distanceKm;
                    }
                });
            }
        });
        
        if (shortestRoute === Infinity) shortestRoute = 0;
        
        const stats = {
            totalDestinations: this.routesData.length,
            totalRoutes,
            totalDistance: parseFloat(totalDistance.toFixed(1)),
            longestRoute: parseFloat(longestRoute.toFixed(1)),
            shortestRoute: parseFloat(shortestRoute.toFixed(1)),
            averageDistance: totalRoutes > 0 ? parseFloat((totalDistance / totalRoutes).toFixed(1)) : 0,
            averageRoutesPerDestination: this.routesData.length > 0 ? parseFloat((totalRoutes / this.routesData.length).toFixed(1)) : 0
        };
        
        this.logger.debug('Estadísticas calculadas:', stats);
        return stats;
    }
    
    /**
     * Obtener estadísticas actuales
     */
    getRouteStats() {
        return this.currentStats || this.calculateRouteStats();
    }
    
    /**
     * Buscar rutas por criterios
     */
    findRoutes(criteria = {}) {
        const results = [];
        
        this.routesData.forEach((destino, destinationIndex) => {
            if (destino.rutas) {
                destino.rutas.forEach((ruta, routeIndex) => {
                    let matches = true;
                    
                    // Filtrar por distancia mínima
                    if (criteria.minDistance) {
                        const distanceKm = ruta.distancia.value / 1000;
                        if (distanceKm < criteria.minDistance) {
                            matches = false;
                        }
                    }
                    
                    // Filtrar por distancia máxima
                    if (criteria.maxDistance) {
                        const distanceKm = ruta.distancia.value / 1000;
                        if (distanceKm > criteria.maxDistance) {
                            matches = false;
                        }
                    }
                    
                    // Filtrar por tipo de ruta
                    if (criteria.routeType && ruta.tipo !== criteria.routeType) {
                        matches = false;
                    }
                    
                    if (matches) {
                        results.push({
                            destinationIndex,
                            routeIndex,
                            route: ruta,
                            destination: destino
                        });
                    }
                });
            }
        });
        
        return results;
    }
    
    /**
     * Obtener ruta más corta
     */
    getShortestRoute() {
        let shortestRoute = null;
        let minDistance = Infinity;
        
        this.routesData.forEach((destino, destinationIndex) => {
            if (destino.rutas) {
                destino.rutas.forEach((ruta, routeIndex) => {
                    const distanceKm = ruta.distancia.value / 1000;
                    if (distanceKm < minDistance) {
                        minDistance = distanceKm;
                        shortestRoute = {
                            destinationIndex,
                            routeIndex,
                            route: ruta,
                            distance: distanceKm
                        };
                    }
                });
            }
        });
        
        return shortestRoute;
    }
    
    /**
     * Obtener ruta más larga
     */
    getLongestRoute() {
        let longestRoute = null;
        let maxDistance = 0;
        
        this.routesData.forEach((destino, destinationIndex) => {
            if (destino.rutas) {
                destino.rutas.forEach((ruta, routeIndex) => {
                    const distanceKm = ruta.distancia.value / 1000;
                    if (distanceKm > maxDistance) {
                        maxDistance = distanceKm;
                        longestRoute = {
                            destinationIndex,
                            routeIndex,
                            route: ruta,
                            distance: distanceKm
                        };
                    }
                });
            }
        });
        
        return longestRoute;
    }
    
    /**
     * Exportar datos de rutas
     */
    exportRoutesData(format = 'json') {
        const data = {
            metadata: {
                timestamp: new Date().toISOString(),
                totalDestinations: this.routesData.length,
                stats: this.getRouteStats()
            },
            routes: this.routesData
        };
        
        if (format === 'json') {
            return JSON.stringify(data, null, 2);
        } else if (format === 'csv') {
            return this.convertToCSV(data);
        }
        
        return data;
    }
    
    /**
     * Convertir datos a CSV
     */
    convertToCSV(data) {
        const rows = ['Destino,Indice_Ruta,Tipo,Distancia_KM,Puntos_Ruta'];
        
        data.routes.forEach((destino, destinationIndex) => {
            if (destino.rutas) {
                destino.rutas.forEach((ruta, routeIndex) => {
                    const distanceKm = ruta.distancia.value / 1000;
                    const pointsCount = ruta.puntos_ruta ? ruta.puntos_ruta.length : 0;
                    
                    rows.push(`${destinationIndex + 1},${routeIndex + 1},${ruta.tipo || 'Ruta'},${distanceKm},${pointsCount}`);
                });
            }
        });
        
        return rows.join('\n');
    }
    
    /**
     * Limpiar datos de rutas
     */
    clearRoutes() {
        this.routesData = [];
        this.currentStats = null;
        this.logger.info('Datos de rutas limpiados');
    }
    
    /**
     * Validar integridad de datos de rutas
     */
    validateRoutesData() {
        const issues = [];
        
        this.routesData.forEach((destino, index) => {
            if (!destino.rutas || destino.rutas.length === 0) {
                issues.push(`Destino ${index + 1}: Sin rutas disponibles`);
            }
            
            if (destino.rutas) {
                destino.rutas.forEach((ruta, routeIndex) => {
                    if (!ruta.puntos_ruta || ruta.puntos_ruta.length < 2) {
                        issues.push(`Destino ${index + 1}, Ruta ${routeIndex + 1}: Puntos de ruta insuficientes`);
                    }
                    
                    if (!ruta.distancia || !ruta.distancia.value) {
                        issues.push(`Destino ${index + 1}, Ruta ${routeIndex + 1}: Distancia no definida`);
                    }
                });
            }
        });
        
        if (issues.length > 0) {
            this.logger.warn('Problemas encontrados en datos de rutas:', issues);
        }
        
        return {
            isValid: issues.length === 0,
            issues
        };
    }
}

// Registrar módulo globalmente
window.RouteManager = RouteManager;