/**
 * Gestor de rutas y cálculos
 */
import { Logger } from '../../core/logger.js';

export class RouteManager {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.logger = new Logger('RouteManager');
        this.routesData = [];
    }

    async getCompleteRoutes(estado, nNodos) {
        try {
            this.logger.debug(`Obteniendo rutas: ${estado}, ${nNodos} destinos`);
            
            const data = await this.apiClient.generateCompleteRoutes(estado, nNodos);
            this.routesData = data.rutas_data;
            
            this.logger.info(`Rutas calculadas exitosamente: ${this.routesData.length} destinos`);
            return data;
            
        } catch (error) {
            this.logger.error('Error obteniendo rutas:', error);
            throw error;
        }
    }

    getAllRoutes() {
        return this.routesData;
    }

    getRoutesForDestination(destinationIndex) {
        const destino = this.routesData.find(d => d.indice === destinationIndex);
        return destino ? destino.rutas : [];
    }

    getRouteStats() {
        let totalRoutes = 0;
        let totalDistance = 0;
        let longestRoute = 0;

        this.routesData.forEach(destino => {
            if (destino.rutas) {
                destino.rutas.forEach(ruta => {
                    totalRoutes++;
                    const distanceKm = ruta.distancia.value / 1000;
                    
                    totalDistance += distanceKm;
                    
                    if (distanceKm > longestRoute) {
                        longestRoute = distanceKm;
                    }
                });
            }
        });

        const stats = {
            totalDestinations: this.routesData.length,
            totalRoutes,
            totalDistance: totalDistance.toFixed(1),
            longestRoute: longestRoute.toFixed(1),
            averageRoutesPerDestination: this.routesData.length > 0 ? 
                (totalRoutes / this.routesData.length).toFixed(1) : '0'
        };
        
        this.logger.debug('Estadísticas calculadas:', stats);
        return stats;
    }
}