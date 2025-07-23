import { Card, Button } from '../UI';

const ScenarioPreview = ({ selectedVehicles, allVehicles, selectedDisaster, routeStates, onGenerate }) => {
  const getVehicleName = (id) => {
    // FIX: Use == to handle potential type mismatch (string vs number) for IDs
    const vehicle = allVehicles.find(v => v.vehiculo_id == id);
    return vehicle?.modelo || 'Vehículo Desconocido';
  }

  return (
    <Card>
      <h2 className="text-2xl font-semibold text-yellow-400 mb-4 text-center">Resumen del Escenario</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Resumen de Vehículos */}
        <div>
          <h3 className="text-xl font-bold text-blue-400 mb-2">Vehículos Seleccionados</h3>
          <ul className="list-disc list-inside space-y-1 text-gray-300">
            {Object.entries(selectedVehicles)
              .filter(([, qty]) => qty > 0)
              .map(([id, qty]) => (
                <li key={id}>
                  <strong>{qty}x</strong> {getVehicleName(id)}
                </li>
              ))}
          </ul>
        </div>

        {/* Resumen de Desastre y Rutas */}
        <div>
          <h3 className="text-xl font-bold text-blue-400 mb-2">Desastre y Rutas</h3>
          <p className="text-gray-300">
            <strong>Desastre:</strong> <span className="capitalize">{selectedDisaster}</span>
          </p>
          <div className="mt-2">
            <h4 className="font-semibold text-gray-300">Estado de Rutas Múltiples:</h4>
            {Object.keys(routeStates).length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-400">
                {Object.values(routeStates).flat().map(route => (
                    <li key={route.ruta_id}>
                    {route.ruta_id}: <span className={route.estado === 'cerrada' ? 'text-red-400' : 'text-green-400'}>{route.estado}</span>
                    {route.estado === 'abierta' && ` (${route.vehiculos_permitidos.length > 0 ? route.vehiculos_permitidos.join(', ') : 'Todos'})`}
                    </li>
                ))}
                </ul>
            ) : (
                <p className="text-sm text-gray-400">No hay destinos con rutas múltiples para configurar.</p>
            )}
          </div>
        </div>
      </div>
      <div className="text-center mt-6">
        <Button onClick={onGenerate} size="lg" variant="success">
          Confirmar y Generar JSON
        </Button>
      </div>
    </Card>
  );
};

export default ScenarioPreview;