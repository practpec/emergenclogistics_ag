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

    // Crear un mapa de rutas por ID para búsqueda más eficiente
    const rutasPorId = {};
    rutas_data.forEach((destinoData, destIndex) => {
      if (destinoData.rutas) {
        destinoData.rutas.forEach((ruta, rutaIndex) => {
          // Crear un ID único basado en la posición y datos de la ruta
          const routeId = `${destIndex}_${rutaIndex}`;
          rutasPorId[routeId] = {
            ...ruta,
            destino: destinoData.destino,
            destIndex,
            rutaIndex
          };
        });
      }
    });

    (solution.asignaciones || []).forEach((assignment, index) => {
      // Buscar la ruta que coincida con la distancia y ruta_id
      let routeInfo = null;
      let routeKey = null;

      // Primero intentar buscar por ruta_id si existe en el mapping
      for (const [key, ruta] in Object.entries(rutasPorId)) {
        const distanciaRuta = ruta.distancia?.value ? ruta.distancia.value / 1000 : 0;
        if (Math.abs(distanciaRuta - assignment.distancia_km) < 0.1) {
          routeInfo = ruta;
          routeKey = key;
          break;
        }
      }

      // Si no encontramos por distancia, buscar por ruta_id directo
      if (!routeInfo && assignment.ruta_id) {
        for (const [key, ruta] of Object.entries(rutasPorId)) {
          if (key.includes(`_${assignment.ruta_id - 1}`) || ruta.ruta_id === assignment.ruta_id) {
            routeInfo = ruta;
            routeKey = key;
            break;
          }
        }
      }

      if (routeInfo && routeInfo.puntos_ruta) {
        const isHighlighted = highlightedRoute === index;
        const isAnyHighlighted = highlightedRoute !== null;

        // Agregar polilínea
        allPolylines.push({
          positions: routeInfo.puntos_ruta.map(p => [p.lat, p.lng]),
          options: {
            color: getRouteColor(index, isHighlighted),
            weight: isHighlighted ? 7 : 4,
            opacity: isAnyHighlighted && !isHighlighted ? 0.3 : 0.9,
          }
        });
        
        // Agregar marcador de destino si no existe
        const destination = routeInfo.destino;
        if (destination && !allMarkers.some(m => 
          Math.abs(m.position[0] - destination.lat) < 0.0001 && 
          Math.abs(m.position[1] - destination.lng) < 0.0001
        )) {
          allMarkers.push({
            position: [destination.lat, destination.lng],
            iconConfig: { color: getRouteColor(index, false), label: routeInfo.destIndex + 1 },
            popup: { 
              title: destination.nombre.split(',')[0], 
              content: [`Población: ${parseInt(destination.poblacion).toLocaleString()}`] 
            }
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
          
          // Buscar destino de manera más robusta
          let destination = null;
          for (const destinoData of mapData.rutas_data) {
            if (destinoData.rutas) {
              const rutaEncontrada = destinoData.rutas.find(r => {
                const distanciaRuta = r.distancia?.value ? r.distancia.value / 1000 : 0;
                return Math.abs(distanciaRuta - assignment.distancia_km) < 0.1;
              });
              if (rutaEncontrada) {
                destination = destinoData.destino;
                break;
              }
            }
          }
          
          return (
            <AssignmentCard
              key={index}
              assignment={assignment}
              vehicle={vehicle}
              destination={destination}
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