import { useEffect } from 'react';
import { Checkbox } from '../UI';

const RouteConfigurator = ({ routesData, vehicleTypes, routeStates, setRouteStates }) => {

  useEffect(() => {
    // FIX: Añadir verificación para evitar loop infinito
    if (Object.keys(routeStates).length > 0 || !routesData || routesData.length === 0) return;

    const initialStates = {};
    routesData.forEach((destinoData, destIndex) => {
      if (destinoData.rutas && destinoData.rutas.length > 1) {
        const numRoutes = destinoData.rutas.length;
        let closedRouteIndex = -1;

        if (Math.random() < 0.5) {
          closedRouteIndex = Math.floor(Math.random() * numRoutes);
        }

        initialStates[destIndex] = destinoData.rutas.map((ruta, routeIndex) => {
          const isClosed = routeIndex === closedRouteIndex;
          let permissions = [];

          if (!isClosed && Math.random() < 0.6 && vehicleTypes.length > 0) {
            permissions = vehicleTypes.filter(() => Math.random() > 0.5);
            if (permissions.length === 0) {
              permissions.push(vehicleTypes[Math.floor(Math.random() * vehicleTypes.length)]);
            }
          }

          return {
            ruta_id: `Destino${destIndex + 1}-Ruta${routeIndex + 1}`,
            estado: isClosed ? 'cerrada' : 'abierta',
            vehiculos_permitidos: permissions,
          };
        });
      }
    });
    
    // Solo actualizar si hay cambios reales
    if (Object.keys(initialStates).length > 0) {
      setRouteStates(initialStates);
    }
  }, [routesData, vehicleTypes.join(',')]); // FIX: Dependencias correctas

  const handleStateChange = (destIndex, routeIndex, newState) => {
    setRouteStates(prevStates => {
      const newStates = { ...prevStates };
      const allRoutesForDest = [...newStates[destIndex]];
      
      allRoutesForDest.forEach((r, i) => {
        r.estado = (i === routeIndex && newState === 'cerrada') ? 'cerrada' : 'abierta';
      });
      
      if (newState === 'cerrada') {
        allRoutesForDest[routeIndex].vehiculos_permitidos = [];
      }
      
      newStates[destIndex] = allRoutesForDest;
      return newStates;
    });
  };
  
  const handleVehiclePermissionChange = (destIndex, routeIndex, vehicleType) => {
    setRouteStates(prevStates => {
      const newStates = { ...prevStates };
      const route = newStates[destIndex][routeIndex];
      const currentPermissions = route.vehiculos_permitidos;
      const newPermissions = currentPermissions.includes(vehicleType) 
        ? currentPermissions.filter(vt => vt !== vehicleType) 
        : [...currentPermissions, vehicleType];
      
      route.vehiculos_permitidos = newPermissions;
      return newStates;
    });
  };

  const destinationsToConfigure = routesData?.filter(d => d.rutas && d.rutas.length > 1) || [];

  if (destinationsToConfigure.length === 0) {
    return <p className="text-sm text-center text-gray-400">No hay destinos con rutas múltiples para configurar.</p>;
  }

  return (
    <div>
      <h3 className="text-xl font-semibold text-gray-200 mb-3">Estado de las Rutas</h3>
      <div className="space-y-4">
        {routesData.map((destinoData, destIndex) => {
          if (destinoData.rutas?.length > 1 && routeStates[destIndex]) {
            return (
              <div key={destIndex} className="p-4 bg-gray-700 rounded-md">
                <h4 className="font-semibold text-yellow-400">
                  Destino {destIndex + 1}: {destinoData.destino?.nombre_localidad || 'Sin nombre'}
                </h4>
                <div className="mt-3 space-y-3">
                  {routeStates[destIndex].map((routeState, routeIndex) => (
                    <div key={routeIndex} className="p-3 bg-gray-800 rounded">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">Ruta {routeIndex + 1}</span>
                        <div className="flex gap-4">
                          <label className="flex items-center gap-1 cursor-pointer">
                            <input 
                              type="radio" 
                              name={`route-${destIndex}-${routeIndex}`} 
                              value="abierta" 
                              checked={routeState.estado === 'abierta'} 
                              onChange={() => handleStateChange(destIndex, routeIndex, 'abierta')} 
                            /> 
                            Abierta
                          </label>
                          <label className="flex items-center gap-1 cursor-pointer">
                            <input 
                              type="radio" 
                              name={`route-${destIndex}-${routeIndex}`} 
                              value="cerrada" 
                              checked={routeState.estado === 'cerrada'} 
                              onChange={() => handleStateChange(destIndex, routeIndex, 'cerrada')} 
                            /> 
                            Cerrada
                          </label>
                        </div>
                      </div>
                      {routeState.estado === 'abierta' && (
                        <div className="mt-2 pt-2 pl-4 border-l-2 border-gray-600">
                          <p className="text-sm text-gray-400 mb-1">
                            Permitir tipos de vehículo (si no se selecciona, todos pasan):
                          </p>
                          <div className="flex flex-wrap gap-x-4 gap-y-1">
                            {vehicleTypes.map(type => (
                              <Checkbox 
                                key={type} 
                                label={type} 
                                checked={routeState.vehiculos_permitidos.includes(type)} 
                                onChange={() => handleVehiclePermissionChange(destIndex, routeIndex, type)} 
                              />
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
};

export default RouteConfigurator;