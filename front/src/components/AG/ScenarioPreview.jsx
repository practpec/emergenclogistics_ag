import { Button,  } from '../common/Button';
import { LoadingSpinner } from '../common/LoadingSpinner';
import AGSettingsForm from './AGSettingsForm';

const ScenarioPreview = ({ 
  expandedFleet, 
  selectedDisaster, 
  routeStates, 
  activeVehicleTypes, 
  onGenerate, 
  isSubmitting,
  agParams,
  setAgParams
}) => {
  const totalVehicles = expandedFleet.length;

  const getRoutePermissionSummary = (route) => {
    if (route.estado === 'cerrada') return <span className="text-red-400">Cerrada</span>;
    if (!route.vehiculos_permitidos || activeVehicleTypes.length === 0) return <span className="text-yellow-400">Abierta (Ninguno)</span>;
    if (route.vehiculos_permitidos.length === activeVehicleTypes.length) return <span className="text-green-400">Abierta (Todos)</span>;
    return <span className="text-green-400">Abierta ({route.vehiculos_permitidos.join(', ')})</span>;
  };

  const routeEntries = Object.entries(routeStates || {});
  
  const agLimits = {
    poblacion_size: { min: 20, max: 100 },
    generaciones: { min: 50, max: 500 },
    prob_cruza: { min: 0.5, max: 1.0 },
    prob_mutacion: { min: 0.05, max: 0.4 },
    elitismo_rate: { min: 0.05, max: 0.3 }
  };

  // --- LÓGICA DE RENDERIZADO CORREGIDA ---
  // Se extrae la lista de rutas a una variable para simplificar el JSX
  const routesSummary = routeEntries.length > 0 
    ? routeEntries.flatMap(([destIndex, routes]) =>
        (routes || []).map((route, routeIndex) => (
          <div key={`${destIndex}-${routeIndex}`}>
            <span className="font-semibold text-gray-300">R{parseInt(destIndex) + 1}-{routeIndex + 1}: </span>
            {getRoutePermissionSummary(route)}
          </div>
        ))
      )
    : <p>Esperando configuración...</p>;

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <h2 className="text-xl font-semibold text-yellow-400 mb-3 text-center">3. Confirmar Escenario y Parámetros</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
        {/* Columna 1: Flota */}
        <div>
          <h3 className="font-bold text-blue-400">Resumen de la Flota</h3>
          <p className="text-gray-300"><strong>Total:</strong> {totalVehicles} vehículo(s)</p>
          <ul className="text-xs text-gray-400 list-disc list-inside">
            {Object.entries(expandedFleet.reduce((acc, v) => ({ ...acc, [v.modelo]: (acc[v.modelo] || 0) + 1 }), {})).map(([modelo, count]) => (
              <li key={modelo}>{count}x {modelo}</li>
            ))}
          </ul>
        </div>

        {/* Columna 2: Condiciones */}
        <div>
          <h3 className="font-bold text-blue-400">Condiciones Generales</h3>
          <p className="text-gray-300"><strong>Desastre:</strong> <span className="capitalize">{selectedDisaster.replace('_', ' ')}</span></p>
        </div>

        {/* Columna 3: Rutas */}
        <div>
          <h3 className="font-bold text-blue-400">Configuración de Rutas</h3>
          <div className="text-xs text-gray-400 max-h-24 overflow-y-auto pr-2">
            {routesSummary}
          </div>
        </div>

        {/* Columna 4: Parámetros AG */}
        <div>
          <AGSettingsForm 
            agParams={agParams}
            setAgParams={setAgParams}
            limits={agLimits}
          />
        </div>
      </div>

      <div className="text-center mt-4 border-t border-gray-700 pt-4">
        <Button onClick={onGenerate} size="lg" variant="success" disabled={isSubmitting}>
          {isSubmitting ? <><LoadingSpinner size="sm" className="mr-2" /> Procesando...</> : 'Confirmar y Ejecutar Algoritmo'}
        </Button>
      </div>
    </div>
  );
};

export default ScenarioPreview;