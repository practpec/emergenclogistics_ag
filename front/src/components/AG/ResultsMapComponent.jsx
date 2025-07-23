import { useState, useEffect } from 'react';

const ResultsMapComponent = ({ mapData, assignedVehicles, className = '' }) => {
  const [mapError, setMapError] = useState(false);

  // Crear iconos SVG para marcadores
  const createMarkerSVG = (color, text) => {
    return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
      <svg width="30" height="30" viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
        <circle cx="15" cy="15" r="12" fill="${color}" stroke="#fff" stroke-width="2"/>
        <text x="15" y="20" text-anchor="middle" fill="#fff" font-size="10" font-weight="bold">${text}</text>
      </svg>
    `)}`;
  };

  const startIconURL = createMarkerSVG('#fbbf24', '★');
  const destinationIconURL = (index) => createMarkerSVG('#3b82f6', index + 1);

  if (mapError || !mapData) {
    return (
      <div className={`bg-gray-800 border border-gray-600 rounded-lg p-6 text-center ${className}`}>
        <div className="text-gray-400">
          <p className="mb-2">Mapa no disponible</p>
          <p className="text-sm">Se mostrará información en formato de tabla</p>
        </div>
        
        {assignedVehicles && (
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
    );
  }

  return (
    <div className={`bg-gray-800 border border-gray-600 rounded-lg overflow-hidden ${className}`}>
      <div className="p-4 border-b border-gray-600">
        <h3 className="text-lg font-semibold text-yellow-400">Mapa de Distribución</h3>
        <p className="text-sm text-gray-400">Rutas optimizadas y asignaciones de vehículos</p>
      </div>
      
      <div className="relative">
        {/* Simulación de mapa con SVG */}
        <svg viewBox="0 0 800 400" className="w-full h-64 bg-gray-900">
          {/* Fondo del mapa */}
          <rect width="800" height="400" fill="#1a1a1a" />
          
          {/* Grid del mapa */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#374151" strokeWidth="1" opacity="0.3"/>
            </pattern>
          </defs>
          <rect width="800" height="400" fill="url(#grid)" />
          
          {/* Punto de origen */}
          {mapData.nodo_principal && (
            <g>
              <circle 
                cx="100" 
                cy="200" 
                r="15" 
                fill="#fbbf24" 
                stroke="#fff" 
                strokeWidth="2"
              />
              <text 
                x="100" 
                y="230" 
                textAnchor="middle" 
                fill="#fbbf24" 
                fontSize="12" 
                fontWeight="bold"
              >
                Origen
              </text>
              
              {/* Animación de pulso */}
              <circle cx="100" cy="200" r="15" fill="none" stroke="#fbbf24" strokeWidth="2" opacity="0.6">
                <animate attributeName="r" values="15;25;15" dur="2s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite"/>
              </circle>
            </g>
          )}
          
          {/* Destinos y rutas */}
          {assignedVehicles?.map((vehiculo, index) => {
            const angle = (index / assignedVehicles.length) * 2 * Math.PI;
            const destX = 400 + Math.cos(angle) * 250;
            const destY = 200 + Math.sin(angle) * 150;
            
            return (
              <g key={index}>
                {/* Línea de ruta */}
                <line
                  x1="100"
                  y1="200"
                  x2={destX}
                  y2={destY}
                  stroke="#3b82f6"
                  strokeWidth="2"
                  strokeDasharray="5,5"
                  opacity="0.7"
                >
                  <animate 
                    attributeName="stroke-dashoffset" 
                    values="0;10" 
                    dur="1s" 
                    repeatCount="indefinite"
                  />
                </line>
                
                {/* Destino */}
                <circle 
                  cx={destX} 
                  cy={destY} 
                  r="12" 
                  fill="#3b82f6" 
                  stroke="#fff" 
                  strokeWidth="2"
                />
                <text 
                  x={destX} 
                  y={destY + 4} 
                  textAnchor="middle" 
                  fill="#fff" 
                  fontSize="10" 
                  fontWeight="bold"
                >
                  {index + 1}
                </text>
                
                {/* Etiqueta del destino */}
                <text 
                  x={destX} 
                  y={destY + 25} 
                  textAnchor="middle" 
                  fill="#e5e7eb" 
                  fontSize="10"
                >
                  {vehiculo.destino_nombre?.split(',')[0] || `Destino ${index + 1}`}
                </text>
                
                {/* Información del vehículo */}
                <text 
                  x={destX} 
                  y={destY + 38} 
                  textAnchor="middle" 
                  fill="#9ca3af" 
                  fontSize="9"
                >
                  {vehiculo.modelo?.split(' ')[0]} - {vehiculo.peso_total_kg?.toFixed(0)}kg
                </text>
              </g>
            );
          })}
          
          {/* Leyenda */}
          <g transform="translate(650, 20)">
            <rect x="0" y="0" width="140" height="80" fill="#1f2937" stroke="#374151" strokeWidth="1" rx="4"/>
            <text x="70" y="15" textAnchor="middle" fill="#e5e7eb" fontSize="12" fontWeight="bold">Leyenda</text>
            
            <circle cx="15" cy="30" r="6" fill="#fbbf24"/>
            <text x="25" y="35" fill="#e5e7eb" fontSize="10">Punto de Origen</text>
            
            <circle cx="15" cy="50" r="6" fill="#3b82f6"/>
            <text x="25" y="55" fill="#e5e7eb" fontSize="10">Destinos</text>
            
            <line x1="10" y1="65" x2="25" y2="65" stroke="#3b82f6" strokeWidth="2" strokeDasharray="3,3"/>
            <text x="30" y="69" fill="#e5e7eb" fontSize="10">Rutas</text>
          </g>
        </svg>
        
        {/* Información adicional */}
        <div className="absolute bottom-0 left-0 right-0 bg-gray-800 bg-opacity-90 p-3">
          <div className="flex justify-between items-center text-sm">
            <div className="text-gray-300">
              <span className="font-medium">Total de rutas:</span> {assignedVehicles?.length || 0}
            </div>
            <div className="text-gray-300">
              <span className="font-medium">Peso total:</span> {
                assignedVehicles?.reduce((sum, v) => sum + (v.peso_total_kg || 0), 0).toFixed(1) || 0
              } kg
            </div>
            <div className="text-gray-300">
              <span className="font-medium">Distancia total:</span> {
                assignedVehicles?.reduce((sum, v) => sum + (v.distancia_km || 0), 0).toFixed(1) || 0
              } km
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsMapComponent;