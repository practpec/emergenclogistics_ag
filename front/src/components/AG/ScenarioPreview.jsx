import { Card, Button, LoadingSpinner } from '../UI';

const ScenarioPreview = ({ expandedFleet, selectedDisaster, routeStates, onGenerate, isSubmitting }) => {

  const groupedVehicles = expandedFleet.reduce((acc, vehicle) => {
    const model = vehicle.modelo || 'Vehículo Desconocido';
    acc[model] = acc[model] || [];
    acc[model].push(vehicle.matricula);
    return acc;
  }, {});

  return (
    <Card>
      <h2 className="text-2xl font-semibold text-yellow-400 mb-4 text-center">Resumen del Escenario</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-xl font-bold text-blue-400 mb-2">Flota de Vehículos</h3>
          <div className="space-y-3">
            {Object.entries(groupedVehicles).map(([modelo, matriculas]) => (
              <div key={modelo}>
                <p className="font-semibold text-gray-200">{matriculas.length}x {modelo}</p>
                <ul className="list-disc list-inside pl-4 text-sm text-gray-400">{matriculas.map(m => <li key={m}>{m}</li>)}</ul>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h3 className="text-xl font-bold text-blue-400 mb-2">Desastre y Rutas</h3>
          <p className="text-gray-300"><strong>Desastre:</strong> <span className="capitalize">{selectedDisaster}</span></p>
          <div className="mt-2">
            <h4 className="font-semibold text-gray-300">Estado de Rutas Múltiples:</h4>
            {Object.keys(routeStates).length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-400">
                {Object.values(routeStates).flat().map(route => (
                    <li key={route.ruta_id}>{route.ruta_id}: <span className={route.estado === 'cerrada' ? 'text-red-400' : 'text-green-400'}>{route.estado}</span>{route.estado === 'abierta' && ` (${route.vehiculos_permitidos.length > 0 ? route.vehiculos_permitidos.join(', ') : 'Todos'})`}</li>
                ))}
                </ul>
            ) : <p className="text-sm text-gray-400">No hay destinos con rutas múltiples para configurar.</p>}
          </div>
        </div>
      </div>
      <div className="text-center mt-6">
        <Button onClick={onGenerate} size="lg" variant="success" disabled={isSubmitting}>
          {isSubmitting ? <><LoadingSpinner size="sm" /> Procesando...</> : 'Confirmar y Ejecutar Escenario'}
        </Button>
      </div>
    </Card>
  );
};

export default ScenarioPreview;