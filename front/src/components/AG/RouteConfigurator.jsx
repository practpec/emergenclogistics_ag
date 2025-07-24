import { Checkbox } from '../common/Checkbox.jsx';

const RouteConfigurator = ({ routesData = [], activeVehicleTypes = [], routeStates, setRouteStates }) => {

  // SE HA ELIMINADO EL useEffect DE ESTE COMPONENTE PARA CENTRALIZAR LA LÓGICA

  const handleStateChange = (destIndex, routeIndex, newState) => {
    setRouteStates(prev => {
      const newRoutesArray = [...(prev[destIndex] || [])];
      newRoutesArray[routeIndex] = {
        ...newRoutesArray[routeIndex],
        estado: newState,
        vehiculos_permitidos: newState === 'abierta' ? [...activeVehicleTypes] : [],
      };
      return { ...prev, [destIndex]: newRoutesArray };
    });
  };

  const handleVehiclePermissionChange = (destIndex, routeIndex, vehicleType) => {
    setRouteStates(prev => {
      const prevRoutes = prev[destIndex];
      const prevRouteState = prevRoutes[routeIndex];
      const currentPermissions = prevRouteState.vehiculos_permitidos;
      
      const newPermissions = currentPermissions.includes(vehicleType)
        ? currentPermissions.filter(vt => vt !== vehicleType)
        : [...currentPermissions, vehicleType];

      const newRouteState = { 
        ...prevRouteState, 
        vehiculos_permitidos: newPermissions,
        // Si no quedan vehículos permitidos, cierra la ruta automáticamente
        estado: newPermissions.length === 0 ? 'cerrada' : 'abierta'
      };
      
      const newRoutesArray = [...prevRoutes];
      newRoutesArray[routeIndex] = newRouteState;
      return { ...prev, [destIndex]: newRoutesArray };
    });
  };

  return (
    <div className="h-full flex flex-col">
      <h3 className="text-lg font-semibold text-gray-200 flex-shrink-0">Estado de Rutas</h3>
      <div className="flex-grow overflow-y-auto pr-2 space-y-2 mt-2">
        {routesData.map((destinoData, destIndex) => (
          <div key={destIndex} className="p-2 bg-gray-700/50 rounded-md">
            <h4 className="font-medium text-gray-100 text-sm">
              Destino {destIndex + 1}: {destinoData.destino?.nombre?.split(',')[0]}
            </h4>
            <div className="mt-1 space-y-2">
              {(routeStates[destIndex] || []).map((routeState, routeIndex) => (
                <div key={routeIndex} className="p-2 bg-gray-900/40 rounded">
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-xs text-gray-300">{destinoData.rutas[routeIndex].tipo || `Ruta ${routeIndex + 1}`}</span>
                    <div className="flex gap-3">
                      <label className="flex items-center gap-1 cursor-pointer">
                        <input type="radio" name={`route-${destIndex}-${routeIndex}`} value="abierta" checked={routeState.estado === 'abierta'} onChange={() => handleStateChange(destIndex, routeIndex, 'abierta')} />
                        <span className="text-green-400 text-xs font-semibold">Abierta</span>
                      </label>
                      <label className="flex items-center gap-1 cursor-pointer">
                        <input type="radio" name={`route-${destIndex}-${routeIndex}`} value="cerrada" checked={routeState.estado === 'cerrada'} onChange={() => handleStateChange(destIndex, routeIndex, 'cerrada')} />
                        <span className="text-red-400 text-xs font-semibold">Cerrada</span>
                      </label>
                    </div>
                  </div>
                  {routeState.estado === 'abierta' && activeVehicleTypes.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-600">
                      <p className="text-xs text-gray-400 mb-1">Permitir tránsito a:</p>
                      <div className="grid grid-cols-2 gap-x-2 gap-y-1">
                        {activeVehicleTypes.map(type => (
                          <Checkbox key={type} label={type} checked={routeState.vehiculos_permitidos.includes(type)} onChange={() => handleVehiclePermissionChange(destIndex, routeIndex, type)} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RouteConfigurator;