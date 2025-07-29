import { useState, useMemo } from 'react';
import MapView from '../../../components/map/MapView';
import AssignmentCard from './AssignmentCard';

const SolutionDetail = ({ solution, mapData, vehicleData, suppliesData }) => {
  const [highlightedRoute, setHighlightedRoute] = useState(null);

  const getRouteColor = (index, isHighlighted) => {
    if (isHighlighted) return '#facc15'; // Yellow-400
    const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#ef4444', '#f97316'];
    return colors[index % colors.length];
  };

  const { markers, polylines } = useMemo(() => {
    const { nodo_principal, rutas_data } = mapData;
    
    const principal = {
      position: [nodo_principal.lat, nodo_principal.lng],
      iconConfig: { color: '#fbbf24', pulse: true },
      popup: { title: 'Origen', content: [nodo_principal.nombre] }
    };

    const allMarkers = [principal];
    const allPolylines = [];

    (solution.asignaciones || []).forEach((assignment, index) => {
      // Encontrar la ruta original por ID
      const routeInfo = rutas_data.find(rd => rd.rutas.some(r => r.distancia.value / 1000 === assignment.distancia_km));

      if (routeInfo) {
        const routePath = routeInfo.rutas.find(r => r.distancia.value / 1000 === assignment.distancia_km);
        
        const isHighlighted = highlightedRoute === index;
        const isAnyHighlighted = highlightedRoute !== null;

        allPolylines.push({
          positions: routePath.puntos_ruta.map(p => [p.lat, p.lng]),
          options: {
            color: getRouteColor(index, isHighlighted),
            weight: isHighlighted ? 7 : 4,
            opacity: isAnyHighlighted && !isHighlighted ? 0.3 : 0.9,
          }
        });
        
        // Añadir marcador de destino si no existe
        const destination = routeInfo.destino;
        if (!allMarkers.some(m => m.position[0] === destination.lat && m.position[1] === destination.lng)) {
          allMarkers.push({
            position: [destination.lat, destination.lng],
            iconConfig: { color: getRouteColor(index, false), label: index + 1 },
            popup: { title: destination.nombre.split(',')[0], content: [] }
          });
        }
      }
    });

    return { markers: allMarkers, polylines: allPolylines };
  }, [solution, mapData, highlightedRoute]);


  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Columna de Asignaciones */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
        {(solution.asignaciones || []).map((assignment, index) => {
          const vehicle = vehicleData.find(v => v.id === assignment.vehiculo_id);
          const routeInfo = mapData.rutas_data.find(rd => rd.rutas.some(r => r.distancia.value / 1000 === assignment.distancia_km));
          
          return (
            <AssignmentCard
              key={index}
              assignment={assignment}
              vehicle={vehicle}
              destination={routeInfo?.destino}
              supplies={suppliesData}
              isHighlighted={highlightedRoute === index}
              onHighlight={(isHighlighting) => setHighlightedRoute(isHighlighting ? index : null)}
            />
          );
        })}
      </div>
      
      {/* Columna del Mapa */}
      <div className="h-[600px] bg-gray-800 rounded-lg overflow-hidden border border-gray-700">
        <MapView
          center={[mapData.nodo_principal.lat, mapData.nodo_principal.lng]}
          zoom={11}
          markers={markers}
          polylines={polylines}
        />
      </div>
    </div>
  );
};

export default SolutionDetail;