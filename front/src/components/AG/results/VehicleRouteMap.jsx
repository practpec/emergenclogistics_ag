// src/components/ag/results/VehicleRouteMap.jsx
import { useMemo, useState } from 'react';
import { Card } from '../../common/Card';
import MapView from '../../map/MapView';
import { Select } from '../../common/Select';

const VehicleRouteMap = ({ solution, mapData, vehicleData }) => {
    const [selectedVehicleId, setSelectedVehicleId] = useState('');

    const assignments = useMemo(() => {
        return solution.asignaciones.map(asig => {
            const vehicle = vehicleData.find(v => v.id == asig.vehiculo_id) || {};
            return { ...asig, vehicle };
        });
    }, [solution, vehicleData]);

    // Establecer el primer vehículo como seleccionado por defecto
    useState(() => {
        if (assignments.length > 0) {
            setSelectedVehicleId(assignments[0].vehiculo_id);
        }
    }, [assignments]);

    const { markers, polylines, center, zoom } = useMemo(() => {
        if (!mapData || !selectedVehicleId) {
            return { markers: [], polylines: [], center: [23.6345, -102.5528], zoom: 5 };
        }

        const assignment = assignments.find(a => a.vehiculo_id == selectedVehicleId);
        if (!assignment) return { markers: [], polylines: [], center: [23.6345, -102.5528], zoom: 5 };

        const { nodo_principal, rutas_data, nodos_secundarios } = mapData;
        let routeInfo = null;
        let destinationNode = null;

        for (let i = 0; i < rutas_data.length; i++) {
            const route = (rutas_data[i].rutas || []).find(r => r.id == assignment.ruta_id);
            if (route) {
                routeInfo = route;
                destinationNode = nodos_secundarios[i];
                break;
            }
        }

        if (!routeInfo || !destinationNode) {
             return { markers: [], polylines: [], center: [23.6345, -102.5528], zoom: 5 };
        }

        const originMarker = {
            position: [nodo_principal.lat, nodo_principal.lng],
            iconConfig: { color: '#fbbf24', pulse: true },
            popup: { title: "Origen", content: [nodo_principal.nombre.split(',')[0]] }
        };

        const destinationMarker = {
            position: [destinationNode.lat, destinationNode.lng],
            iconConfig: { color: '#3498db' },
            popup: { title: "Destino", content: [destinationNode.nombre.split(',')[0]] }
        };

        const routePolyline = {
            positions: routeInfo.puntos_ruta.map(p => [p.lat, p.lng]),
            options: { color: '#3498db', weight: 6, opacity: 0.9 }
        };

        return {
            markers: [originMarker, destinationMarker],
            polylines: [routePolyline],
            center: [destinationNode.lat, destinationNode.lng],
            zoom: 10
        };

    }, [selectedVehicleId, assignments, mapData]);

    return (
        <Card className="flex flex-col p-0">
            <div className="p-4 border-b border-gray-700">
                <h2 className="text-xl font-semibold text-blue-400 mb-2">Visualización de Ruta por Vehículo</h2>
                <Select
                    value={selectedVehicleId}
                    onChange={(e) => setSelectedVehicleId(e.target.value)}
                    options={assignments.map(a => ({
                        value: a.vehiculo_id,
                        label: `${a.vehicle.modelo || `ID ${a.vehiculo_id}`}`
                    }))}
                />
            </div>
            <div className="flex-grow h-96 md:h-[600px]">
                <MapView center={center} zoom={zoom} markers={markers} polylines={polylines} />
            </div>
        </Card>
    );
};

export default VehicleRouteMap;