import { useState, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { Card, Button, LoadingSpinner } from '../components/UI';
import { useAG } from '../hooks/useAG';
import VehicleSelector from '../components/AG/VehicleSelector';
import DisasterSelector from '../components/AG/DisasterSelector';
import RouteConfigurator from '../components/AG/RouteConfigurator';
import ScenarioPreview from '../components/AG/ScenarioPreview';

const AGPage = () => {
  const location = useLocation();
  const { mapData } = location.state || {};
  const { vehicles, disasters, isLoading } = useAG();

  // Estados para la configuración
  const [selectedVehicles, setSelectedVehicles] = useState({});
  const [customVehicles, setCustomVehicles] = useState([]);
  const [selectedDisaster, setSelectedDisaster] = useState('');
  const [routeStates, setRouteStates] = useState({});
  const [generatedJson, setGeneratedJson] = useState(null);

  const allVehicles = useMemo(() => [...vehicles, ...customVehicles], [vehicles, customVehicles]);
  const isVehicleSelected = useMemo(() => Object.values(selectedVehicles).some(q => q > 0), [selectedVehicles]);

  // FIX: Memoize vehicleTypes to prevent re-creating the array on every render.
  // This breaks the infinite loop in RouteConfigurator.
  const vehicleTypes = useMemo(() => [...new Set(allVehicles.map(v => v.tipo))], [allVehicles]);


  const handleGenerateJson = () => {
    const scenario = {
      punto_partida: mapData?.nodo_principal,
      tipo_desastre: selectedDisaster,
      vehiculos_disponibles: allVehicles
        .map(v => ({ ...v, cantidad: selectedVehicles[v.vehiculo_id] || 0 }))
        .filter(v => v.cantidad > 0),
      rutas_estado: Object.values(routeStates).flat(),
    };
    setGeneratedJson(JSON.stringify(scenario, null, 2));
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-yellow-400 mb-6 text-center">
        Configuración del Escenario Logístico
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Columna Izquierda: Vehículos */}
        <div className="space-y-6">
          <Card>
            <h2 className="text-2xl font-semibold text-blue-400 mb-4">1. Flota de Vehículos</h2>
            <VehicleSelector
              vehicles={vehicles}
              customVehicles={customVehicles}
              setCustomVehicles={setCustomVehicles}
              selectedVehicles={selectedVehicles}
              setSelectedVehicles={setSelectedVehicles}
            />
          </Card>
        </div>

        {/* Columna Derecha: Desastre y Rutas (condicional) */}
        <div className="space-y-6">
          <Card className={!isVehicleSelected ? 'opacity-50 pointer-events-none' : ''}>
            <h2 className="text-2xl font-semibold text-blue-400 mb-4">2. Escenario y Rutas</h2>
            {!isVehicleSelected && (
              <p className="text-yellow-400 text-center">Selecciona al menos un vehículo para continuar.</p>
            )}
            <div className="space-y-6">
              <DisasterSelector
                disasters={disasters}
                selectedDisaster={selectedDisaster}
                setSelectedDisaster={setSelectedDisaster}
              />
              {mapData?.rutas_data && (
                <RouteConfigurator
                  routesData={mapData.rutas_data}
                  vehicleTypes={vehicleTypes} // Pasamos la versión optimizada
                  routeStates={routeStates}
                  setRouteStates={setRouteStates}
                />
              )}
            </div>
          </Card>
        </div>
      </div>

      {/* Preview y Generación de JSON (condicional) */}
      {isVehicleSelected && selectedDisaster && (
        <ScenarioPreview
            selectedVehicles={selectedVehicles}
            allVehicles={allVehicles}
            selectedDisaster={selectedDisaster}
            routeStates={routeStates}
            onGenerate={handleGenerateJson}
        />
      )}

      {generatedJson && (
        <Card>
          <h2 className="text-2xl font-semibold text-green-400 mb-4">Escenario Generado</h2>
          <pre className="bg-gray-900 p-4 rounded-md text-gray-200 overflow-x-auto">
            {generatedJson}
          </pre>
        </Card>
      )}
    </div>
  );
};

export default AGPage;