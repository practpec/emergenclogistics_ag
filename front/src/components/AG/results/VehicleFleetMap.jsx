// src/components/ag/results/VehicleFleetMap.jsx
import { useState, useMemo } from 'react';
import MapView from '../../map/MapView';
import { Card } from '../../common/Card';
import clsx from 'clsx';

// Sub-componente para la lista de vehículos
const VehicleListPanel = ({ assignments, highlightedVehicleId, onVehicleHighlight }) => (
    <div className="w-full md:w-80 lg:w-96 bg-gray-800 border border-gray-600 rounded-lg flex flex-col">
        <div className="p-3 border-b border-gray-600">
            <h3 className="font-semibold text-gray-100">Flota Asignada ({assignments.length} vehículos)</h3>
            <p className="text-xs text-gray-400">Pasa el cursor sobre un vehículo para ver su ruta.</p>
        </div>
        <div className="flex-1 overflow-y-auto">
            {assignments.map(asig => (
                <div
                    key={asig.vehiculo_id}
                    onMouseEnter={() => onVehicleHighlight(asig.vehiculo_id)}
                    onMouseLeave={() => onVehicleHighlight(null)}
                    className={clsx(
                        "p-3 border-b border-gray-700 last:border-b-0 cursor-pointer transition-colors",
                        highlightedVehicleId === asig.vehiculo_id ? "bg-blue-600/30" : "hover:bg-gray-700/50"
                    )}
                >
                    <p className="font-semibold text-sm">{asig.vehicle.modelo}</p>
                    <p className="text-xs text-gray-400">
                        ↳ Destino: <span className="text-gray-200">{asig.destinationName}</span>
                    </p>
                </div>
            ))}
        </div>
    </div>
);


const VehicleFleetMap = ({ solution, mapData, vehicleData }) => {
    const [highlightedVehicleId, setHighlightedVehicleId] = useState(null);

    const assignmentsWithDetails = useMemo(() => {
        return solution.asignaciones.map(asig => {
            const vehicle = vehicleData.find(v => v.id == asig.vehiculo_id) || {};
            let destinationName = 'N/A';
            let routeInfo = null;

            for (const destData of mapData.rutas_data) {
                const route = (destData.rutas || []).find(r => r.id == asig.ruta_id);
                if (route) {
                    destinationName = destData.destino.nombre.split(',')[0];
                    routeInfo = route;
                    break;
                }
            }
            return { ...asig, vehicle, destinationName, routeInfo };
        });
    }, [solution, mapData, vehicleData]);

    const { markers, polylines } = useMemo(() => {
        const { nodo_principal, nodos_secundarios } = mapData;
        const originMarker = {
            position: [nodo_principal.lat, nodo_principal.lng],
            iconConfig: { color: '#fbbf24', pulse: true },
            popup: { title: "Origen" }
        };

        const destinationMarkers = nodos_secundarios.map((nodo, i) => ({
            position: [nodo.lat, nodo.lng],
            iconConfig: { color: '#6b7280', label: i + 1 }, // Gris por defecto
            popup: { title: nodo.nombre.split(',')[0] }
        }));
        
        const routePolylines = assignmentsWithDetails.map((asig, index) => {
            if (!asig.routeInfo) return null;
            const isHighlighted = asig.vehiculo_id === highlightedVehicleId;
            return {
                positions: asig.routeInfo.puntos_ruta.map(p => [p.lat, p.lng]),
                options: {
                    color: isHighlighted ? '#3b82f6' : '#4b5563', // Azul si está destacado, gris si no
                    weight: isHighlighted ? 6 : 3,
                    opacity: isHighlighted ? 1.0 : 0.5,
                }
            };
        }).filter(Boolean);

        // Resaltar el marcador de destino de la ruta activa
        if (highlightedVehicleId) {
            const activeAssignment = assignmentsWithDetails.find(a => a.vehiculo_id === highlightedVehicleId);
            if(activeAssignment) {
                 const destIndex = nodos_secundarios.findIndex(n => n.nombre === activeAssignment.routeInfo.destino_nombre);
                 if (destIndex !== -1) {
                     destinationMarkers[destIndex].iconConfig.color = '#3b82f6';
                 }
            }
        }

        return { markers: [originMarker, ...destinationMarkers], polylines: routePolylines };
    }, [mapData, assignmentsWithDetails, highlightedVehicleId]);

    return (
        <Card className="p-0">
             <div className="flex flex-col md:flex-row gap-4 h-[70vh]">
                <VehicleListPanel 
                    assignments={assignmentsWithDetails}
                    highlightedVehicleId={highlightedVehicleId}
                    onVehicleHighlight={setHighlightedVehicleId}
                />
                <div className="flex-1 bg-gray-800 border border-gray-600 rounded-lg overflow-hidden">
                    <MapView
                        center={[mapData.nodo_principal.lat, mapData.nodo_principal.lng]}
                        zoom={9}
                        markers={markers}
                        polylines={polylines}
                    />
                </div>
            </div>
        </Card>
    );
};

export default VehicleFleetMap;