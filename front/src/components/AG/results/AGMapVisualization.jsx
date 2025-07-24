import { Card } from '../../common/Card';
import MapView from '../../map/MapView';
import { useMemo, useState } from 'react';
import { Button } from '../../common/Button';

const AGMapVisualization = ({ solutions, mapData }) => {
    const [selectedSolutionIndex, setSelectedSolutionIndex] = useState(0);
    const solution = solutions[selectedSolutionIndex];
    
    const { markers, polylines } = useMemo(() => {
        if (!mapData || !solution) return { markers: [], polylines: [] };

        const { nodo_principal, nodos_secundarios, rutas_data } = mapData;
        const routeColors = ['#6366F1', '#EC4899', '#10B981', '#F59E0B', '#3B82F6', '#EF4444'];

        const principal = {
          position: [nodo_principal.lat, nodo_principal.lng],
          iconConfig: { color: '#fbbf24', pulse: true },
          popup: { title: nodo_principal.nombre.split(',')[0], content: [] }
        };
        
        const destinos = nodos_secundarios.map((nodo, i) => ({
             position: [nodo.lat, nodo.lng],
             iconConfig: { color: '#4B5563', label: i + 1 },
             popup: { title: `Destino ${i+1}`, content: [nodo.nombre.split(',')[0]] }
        }));

        const lineas = solution.asignaciones.map((asig, index) => {
            let rutaInfo = null;
            let destinoIndex = -1;
            
            for(let i = 0; i < rutas_data.length; i++) {
                const route = (rutas_data[i].rutas || []).find(r => r.id == asig.ruta_id);
                if (route) {
                    rutaInfo = route;
                    destinoIndex = i;
                    break;
                }
            }

            if (!rutaInfo) return null;
            
            if (destinos[destinoIndex]) {
                destinos[destinoIndex].iconConfig.color = routeColors[index % routeColors.length];
            }

            return {
                positions: rutaInfo.puntos_ruta.map(p => [p.lat, p.lng]),
                options: { color: routeColors[index % routeColors.length], weight: 5, opacity: 0.8 }
            };
        }).filter(Boolean);

        return { markers: [principal, ...destinos], polylines: lineas };
    }, [mapData, solution]);

    return (
        <Card className="flex flex-col p-0">
            <div className="p-4 flex justify-between items-center border-b border-gray-700">
                <h2 className="text-xl font-semibold text-blue-400">Mapa de Distribución</h2>
                <div className="flex gap-2">
                    {solutions.map((_, index) => (
                        <Button key={index} size="sm" variant={selectedSolutionIndex === index ? 'primary' : 'secondary'} onClick={() => setSelectedSolutionIndex(index)}>
                            Sol. #{index + 1}
                        </Button>
                    ))}
                </div>
            </div>
            <div className="flex-grow h-96">
                <MapView center={[mapData.nodo_principal.lat, mapData.nodo_principal.lng]} zoom={9} markers={markers} polylines={polylines} />
            </div>
        </Card>
    );
};

export default AGMapVisualization;