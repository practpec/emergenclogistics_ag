import { Card } from '../../../components/common/Card';

// Helper para el estado de una ruta individual (sin cambios)
const RouteStatusDetail = ({ route, routeInfo }) => {
    const isClosed = route.estado === 'cerrada';
    
    return (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-2 bg-gray-900/50 rounded-md">
            <div className="flex items-center">
                <span className={`w-3 h-3 rounded-full mr-2 ${isClosed ? 'bg-red-500' : 'bg-green-500'}`}></span>
                <span className="font-semibold text-gray-300">{routeInfo.tipo || 'Ruta'}</span>
                <span className="text-xs text-gray-500 ml-2">({routeInfo.distancia.text})</span>
            </div>
            <div className={`text-sm mt-1 sm:mt-0 ${isClosed ? 'text-red-400' : 'text-green-400'}`}>
                <span className="font-bold">{isClosed ? 'Cerrada' : 'Abierta'}</span>
                {!isClosed && route.vehiculos_permitidos.length > 0 && (
                    <span className="text-xs text-yellow-400 ml-2">(Permite: {route.vehiculos_permitidos.join(', ')})</span>
                )}
            </div>
        </div>
    );
};

// --- Componente Principal Actualizado ---
const ScenarioSummary = ({ mapData, vehicleData, selectedDisaster, scenarioConfig, routeStates }) => {
  const { nodo_principal, nodos_secundarios } = mapData;
  const { vehiculos_disponibles } = scenarioConfig;

  // --- LÓGICA PARA AGRUPAR VEHÍCULOS ---
  const groupedFleet = vehiculos_disponibles.reduce((acc, currentVehicle) => {
    const details = vehicleData.find(v => v.modelo === currentVehicle.modelo);
    if (!details) return acc;

    if (!acc[details.modelo]) {
      acc[details.modelo] = { ...details, count: 0 };
    }
    acc[details.modelo].count += 1;
    return acc;
  }, {});


  return (
    <Card>
      <h2 className="text-xl font-bold text-yellow-400 mb-4 text-center">Resumen del Escenario Ejecutado</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* --- TARJETA 1: Información General --- */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex flex-col">
            <h3 className="font-semibold text-blue-400 mb-2 text-center">📍 Información Geográfica y de Desastre</h3>
            <div className="bg-gray-700/50 p-3 rounded-md mb-3">
                <p className="font-medium text-gray-400">Origen:</p>
                <p className="text-sm text-gray-200 pl-2">{nodo_principal.nombre}</p>
            </div>
            <div className="bg-gray-700/50 p-3 rounded-md mb-3">
                 <p className="font-medium text-gray-400 mb-1">Destinos ({nodos_secundarios.length}):</p>
                <div className="space-y-1 text-sm text-gray-300 max-h-32 overflow-y-auto pr-2">
                    {nodos_secundarios.map((destino, i) => (
                        <p key={i} className="pl-2">{i+1}. {destino.nombre.split(',')[0]} <span className="text-xs text-gray-400">(Pob: {parseInt(destino.poblacion).toLocaleString()})</span></p>
                    ))}
                </div>
            </div>
             <div className="bg-gray-700/50 p-3 rounded-md flex-grow">
                <p className="font-medium text-gray-400">Condiciones del Desastre:</p>
                <p className="capitalize text-gray-300 pl-2">Tipo: {scenarioConfig.tipo_desastre.replace('_', ' ')}</p>
                <p className="text-xs mt-1 pl-2 font-semibold text-gray-200">Prioridades:</p>
                <ul className="list-disc list-inside pl-4 text-xs text-gray-400">
                  {selectedDisaster?.prioridades.map(p => ( <li key={p.categoria} className="capitalize">{p.categoria}: <span className="font-bold">{p.nivel}</span></li> ))}
                </ul>
            </div>
        </div>

        {/* --- TARJETA 2: Flota y Estado de Rutas (CON FLOTA AGRUPADA) --- */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex flex-col">
             <h3 className="font-semibold text-blue-400 mb-2 text-center">🚚 Recursos y Accesibilidad</h3>
             <div className="bg-gray-700/50 p-3 rounded-md mb-3">
                <p className="font-medium text-gray-400 mb-2">Flota Asignada ({vehiculos_disponibles.length} en total):</p>
                <div className="space-y-3 max-h-32 overflow-y-auto pr-1">
                    {Object.values(groupedFleet).map((vehicle) => (
                        <div key={vehicle.id} className="text-xs p-2 bg-gray-900/50 rounded">
                            <div className="flex justify-between items-baseline">
                                <p className="font-bold text-gray-200">{vehicle.modelo}</p>
                                <p className="text-purple-300 font-semibold">{vehicle.count}x {vehicle.tipo}</p>
                            </div>
                            <div className="grid grid-cols-3 text-center mt-1 pt-1 border-t border-gray-700 text-gray-400">
                                <span><span className="font-semibold text-gray-200">{vehicle.maximo_peso_ton}</span> T</span>
                                <span><span className="font-semibold text-gray-200">{vehicle.velocidad_kmh}</span> km/h</span>
                                <span><span className="font-semibold text-gray-200">{vehicle.consumo_litros_km}</span> L/km</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            <div className="bg-gray-700/50 p-3 rounded-md flex-grow">
                <p className="font-medium text-gray-400 mb-2">Estado de Rutas por Destino:</p>
                 <div className="space-y-3 max-h-48 overflow-y-auto pr-2">
                    {nodos_secundarios.map((destino, i) => (
                        <div key={i} className="text-sm">
                            <p className="text-gray-300 font-semibold border-b border-gray-600 pb-1 mb-2">{i+1}. Hacia {destino.nombre.split(',')[0]}</p>
                            <div className="space-y-2 pl-2">
                                {(routeStates[i] || []).map((route, rIndex) => (
                                     <RouteStatusDetail 
                                         key={rIndex} 
                                         route={route}
                                         routeInfo={mapData.rutas_data[i].rutas[rIndex]}
                                     />
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
      </div>
    </Card>
  );
};

export default ScenarioSummary;