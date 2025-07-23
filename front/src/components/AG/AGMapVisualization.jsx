import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import { Card, Button, Badge } from '../UI';
import 'leaflet/dist/leaflet.css';

// Configurar iconos de Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const AGMapVisualization = ({ mapData, mejoresSoluciones, className = '' }) => {
  const [selectedSolution, setSelectedSolution] = useState(0);
  const [mapError, setMapError] = useState(false);
  const [routeColors] = useState([
    '#e74c3c', '#3498db', '#f39c12', '#27ae60', '#9b59b6',
    '#e67e22', '#1abc9c', '#34495e', '#f1c40f', '#95a5a6',
  ]);

  // Icono para nodo principal
  const principalIcon = new L.DivIcon({
    className: 'custom-div-icon',
    html: `
      <div class="marker-pin principal-marker">
        <div class="pulse"></div>
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15]
  });

  // Función para crear icono de destino con vehículo asignado
  const createDestinationIcon = (vehiculo, index) => {
    const utilizacion = vehiculo?.utilizacion_capacidad || 0;
    const color = utilizacion > 0.7 ? '#22c55e' : utilizacion > 0.5 ? '#f59e0b' : '#ef4444';
    
    return new L.DivIcon({
      className: 'custom-div-icon',
      html: `
        <div class="marker-pin" style="background-color: ${color}">
          <span class="marker-number">${index + 1}</span>
        </div>
      `,
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    });
  };

  // Obtener la solución seleccionada
  const currentSolution = mejoresSoluciones?.[selectedSolution];
  const assignedVehicles = currentSolution?.vehiculos || [];

  // Función para encontrar la ruta utilizada por un vehículo
  const findVehicleRoute = (vehiculo) => {
    if (!mapData?.rutas_data || !vehiculo?.destino_nombre) return null;
    
    // Buscar el destino correspondiente por múltiples criterios
    const destinoData = mapData.rutas_data.find(d => {
      const destino = d.destino;
      if (!destino) return false;
      
      return (
        destino.nombre_localidad === vehiculo.destino_nombre ||
        destino.nombre === vehiculo.destino_nombre ||
        destino.nombre_localidad?.includes(vehiculo.destino_nombre) ||
        vehiculo.destino_nombre?.includes(destino.nombre_localidad)
      );
    });
    
    if (!destinoData?.rutas || destinoData.rutas.length === 0) return null;
    
    // Si el vehículo tiene información de ruta específica, usarla
    if (vehiculo.ruta_utilizada_id !== undefined) {
      const rutaEspecifica = destinoData.rutas.find(r => r.id === vehiculo.ruta_utilizada_id);
      if (rutaEspecifica) return rutaEspecifica;
    }
    
    // Si no, usar la primera ruta disponible
    return destinoData.rutas[0];
  };

  // Renderizar las rutas de los vehículos asignados
  const renderAssignedRoutes = () => {
    if (!assignedVehicles || assignedVehicles.length === 0) return null;
    
    return assignedVehicles.map((vehiculo, index) => {
      const ruta = findVehicleRoute(vehiculo);
      if (!ruta?.puntos_ruta || ruta.puntos_ruta.length === 0) return null;

      const positions = ruta.puntos_ruta.map(punto => [punto.lat, punto.lng]);
      const color = routeColors[index % routeColors.length];
      
      return (
        <Polyline
          key={`vehicle-route-${index}`}
          positions={positions}
          pathOptions={{
            color,
            weight: 4,
            opacity: 0.8,
            dashArray: '10, 5'
          }}
        />
      );
    });
  };

  // Renderizar marcadores de destinos con vehículos asignados
  const renderDestinationMarkers = () => {
    if (!assignedVehicles || assignedVehicles.length === 0) return null;
    
    return assignedVehicles.map((vehiculo, index) => {
      // Buscar las coordenadas del destino en múltiples fuentes
      let destinoCoords = null;
      
      // Primero buscar en nodos secundarios
      if (mapData?.nodos_secundarios) {
        const nodoSecundario = mapData.nodos_secundarios.find(nodo => 
          nodo.nombre_localidad === vehiculo.destino_nombre ||
          nodo.nombre === vehiculo.destino_nombre ||
          nodo.nombre_localidad?.includes(vehiculo.destino_nombre) ||
          vehiculo.destino_nombre?.includes(nodo.nombre_localidad)
        );
        if (nodoSecundario) {
          destinoCoords = [nodoSecundario.lat, nodoSecundario.lng];
        }
      }
      
      // Si no se encuentra, buscar en rutas_data
      if (!destinoCoords && mapData?.rutas_data) {
        const destinoData = mapData.rutas_data.find(d => {
          const destino = d.destino;
          return destino && (
            destino.nombre_localidad === vehiculo.destino_nombre ||
            destino.nombre === vehiculo.destino_nombre ||
            destino.nombre_localidad?.includes(vehiculo.destino_nombre) ||
            vehiculo.destino_nombre?.includes(destino.nombre_localidad)
          );
        });
        
        if (destinoData?.destino) {
          destinoCoords = [destinoData.destino.lat, destinoData.destino.lng];
        }
      }
      
      if (!destinoCoords) {
        console.warn(`No se encontraron coordenadas para: ${vehiculo.destino_nombre}`);
        return null;
      }
      
      return (
        <Marker
          key={`vehicle-marker-${index}`}
          position={destinoCoords}
          icon={createDestinationIcon(vehiculo, index)}
        >
          <Popup>
            <div className="text-center min-w-[200px]">
              <h4 className="font-semibold text-blue-400 mb-2">
                Destino {index + 1}: {vehiculo.destino_nombre}
              </h4>
              <div className="text-sm text-gray-600 space-y-1">
                <p><strong>Vehículo:</strong> {vehiculo.modelo}</p>
                <p><strong>Matrícula:</strong> {vehiculo.matricula || 'N/A'}</p>
                <p><strong>Población:</strong> {vehiculo.destino_poblacion?.toLocaleString()}</p>
                <p><strong>Distancia:</strong> {vehiculo.distancia_km?.toFixed(1)} km</p>
                <p><strong>Carga:</strong> {vehiculo.peso_total_kg?.toFixed(1)} kg</p>
                <p><strong>Utilización:</strong> 
                  <Badge variant={vehiculo.utilizacion_capacidad > 0.7 ? 'success' : vehiculo.utilizacion_capacidad > 0.5 ? 'warning' : 'danger'}>
                    {((vehiculo.utilizacion_capacidad || 0) * 100).toFixed(1)}%
                  </Badge>
                </p>
                <p><strong>Combustible:</strong> {vehiculo.combustible_litros?.toFixed(1)} L</p>
              </div>
            </div>
          </Popup>
        </Marker>
      );
    });
  };

  if (mapError || !mapData) {
    return (
      <Card className={className}>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Mapa de Distribución</h3>
        <div className="bg-gray-800 border border-gray-600 rounded-lg p-6 text-center">
          <div className="text-gray-400">
            <p className="mb-2">Mapa no disponible</p>
            <p className="text-sm">Se mostrará información en formato de tabla</p>
          </div>
          
          {assignedVehicles && assignedVehicles.length > 0 && (
            <div className="mt-4 space-y-2">
              <h4 className="font-semibold text-yellow-400">Asignaciones de Vehículos</h4>
              {assignedVehicles.map((vehiculo, index) => (
                <div key={index} className="bg-gray-700 p-3 rounded text-left">
                  <p><span className="font-medium">Vehículo:</span> {vehiculo.modelo}</p>
                  <p><span className="font-medium">Destino:</span> {vehiculo.destino_nombre}</p>
                  <p><span className="font-medium">Distancia:</span> {vehiculo.distancia_km?.toFixed(1)} km</p>
                  <p><span className="font-medium">Carga:</span> {vehiculo.peso_total_kg?.toFixed(1)} kg</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    );
  }

  // Calcular el centro del mapa
  const mapCenter = mapData.nodo_principal 
    ? [mapData.nodo_principal.lat, mapData.nodo_principal.lng]
    : [23.6345, -102.5528];

  return (
    <Card className={className}>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-semibold text-yellow-400">Mapa de Distribución Optimizada</h3>
          
          {/* Selector de solución */}
          <div className="flex space-x-2">
            {mejoresSoluciones?.slice(0, 3).map((_, index) => (
              <Button
                key={index}
                onClick={() => setSelectedSolution(index)}
                variant={selectedSolution === index ? 'primary' : 'secondary'}
                size="sm"
              >
                Sol. #{index + 1}
              </Button>
            ))}
          </div>
        </div>

        {/* Información de la solución actual */}
        {currentSolution && (
          <div className="bg-gray-700 p-3 rounded">
            <div className="flex justify-between items-center text-sm">
              <div className="text-gray-300">
                <span className="font-medium">Fitness:</span> {currentSolution.fitness?.toFixed(2)}
              </div>
              <div className="text-gray-300">
                <span className="font-medium">Vehículos:</span> {assignedVehicles.length}
              </div>
              <div className="text-gray-300">
                <span className="font-medium">Peso total:</span> {currentSolution.resumen?.peso_total?.toFixed(1)} kg
              </div>
              <div className="text-gray-300">
                <span className="font-medium">Combustible:</span> {currentSolution.resumen?.combustible_total?.toFixed(1)} L
              </div>
            </div>
          </div>
        )}

        {/* Mapa */}
        <div className="h-96 rounded-lg overflow-hidden border border-gray-600">
          <MapContainer
            center={mapCenter}
            zoom={10}
            className="w-full h-full"
            style={{ background: '#1a1a1a' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; OpenStreetMap contributors'
            />
            
            {/* Nodo Principal */}
            {mapData.nodo_principal && (
              <Marker
                position={[mapData.nodo_principal.lat, mapData.nodo_principal.lng]}
                icon={principalIcon}
              >
                <Popup>
                  <div className="text-center min-w-[150px]">
                    <h4 className="font-semibold text-yellow-400 mb-2">
                      {mapData.nodo_principal.nombre_localidad || mapData.nodo_principal.nombre}
                    </h4>
                    <div className="text-sm text-gray-600">
                      <p><strong>Tipo:</strong> Centro de Distribución</p>
                      <p><strong>Coordenadas:</strong><br/>{mapData.nodo_principal.lat.toFixed(4)}, {mapData.nodo_principal.lng.toFixed(4)}</p>
                      {mapData.nodo_principal.poblacion && (
                        <p><strong>Población:</strong> {mapData.nodo_principal.poblacion.toLocaleString()}</p>
                      )}
                    </div>
                  </div>
                </Popup>
              </Marker>
            )}
            
            {/* Rutas de vehículos asignados */}
            {renderAssignedRoutes()}
            
            {/* Marcadores de destinos con vehículos */}
            {renderDestinationMarkers()}
          </MapContainer>
        </div>

        {/* Leyenda */}
        <div className="bg-gray-700 p-3 rounded">
          <h4 className="font-semibold text-blue-400 mb-2">Leyenda</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-yellow-400 rounded-full"></div>
              <span>Centro de Distribución</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-500 rounded-full"></div>
              <span>Utilización Alta (&gt;70%)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
              <span>Utilización Media (50-70%)</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-500 rounded-full"></div>
              <span>Utilización Baja (&lt;50%)</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default AGMapVisualization;