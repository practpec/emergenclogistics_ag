import { useState, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { Card, Button, LoadingSpinner } from '../components/UI';
import { useAG } from '../hooks/useAG';
import apiService, { handleApiError } from '../services/apiService';
import toast from 'react-hot-toast';

import VehicleSelector from '../components/AG/VehicleSelector';
import DisasterSelector from '../components/AG/DisasterSelector';
import RouteConfigurator from '../components/AG/RouteConfigurator';
import ScenarioPreview from '../components/AG/ScenarioPreview';

const AGPage = () => {
  const location = useLocation();
  const { mapData } = location.state || {};
  const { vehicles, disasters, isLoading: isLoadingInitialData } = useAG();

  // Estados para la configuración
  const [selectedVehicles, setSelectedVehicles] = useState({});
  const [customVehicles, setCustomVehicles] = useState([]);
  const [selectedDisaster, setSelectedDisaster] = useState('');
  const [routeStates, setRouteStates] = useState({});
  
  // Estados para el envío a la API
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [scenarioResult, setScenarioResult] = useState(null);

  const allVehicles = useMemo(() => [...vehicles, ...customVehicles], [vehicles, customVehicles]);
  const isVehicleSelected = useMemo(() => Object.values(selectedVehicles).some(q => q > 0), [selectedVehicles]);
  const vehicleTypes = useMemo(() => [...new Set(allVehicles.map(v => v.tipo))], [allVehicles]);

  const expandedFleet = useMemo(() => {
    return Object.entries(selectedVehicles).flatMap(([id, quantity]) => {
      const vehicleInfo = allVehicles.find(v => v.vehiculo_id == id);
      if (!vehicleInfo || !quantity || quantity < 1) return [];

      const vehiclesList = [];
      for (let i = 1; i <= quantity; i++) {
        const modelPrefix = (vehicleInfo.modelo || 'VEHICULO').replace(/[^A-Z0-9]/ig, '').substring(0, 6).toUpperCase();
        const uniqueMatricula = `${modelPrefix}-${vehicleInfo.vehiculo_id}-${i}`;
        vehiclesList.push({ ...vehicleInfo, matricula: uniqueMatricula });
      }
      return vehiclesList;
    });
  }, [selectedVehicles, allVehicles]);

  const handleRunScenario = async () => {
    if (!mapData) {
        toast.error("Faltan los datos del mapa. Por favor, genera un mapa primero.");
        return;
    }

    const scenarioData = {
      map_data: {
        nodo_principal: mapData.nodo_principal,
        nodos_secundarios: mapData.nodos_secundarios,
        rutas_data: mapData.rutas_data,
        municipio_info: mapData.municipio_info,
      },
      scenario_config: {
        tipo_desastre: selectedDisaster,
        vehiculos_disponibles: expandedFleet.map(({ vehiculo_id, ...rest }) => rest),
        rutas_estado: Object.values(routeStates).flat(),
      }
    };
    
    setIsSubmitting(true);
    setScenarioResult(null);
    toast.loading('Procesando escenario... Esto puede tardar un momento.');

    try {
      const result = await apiService.runAGScenario(scenarioData);
      toast.dismiss();
      if (result.success) {
        toast.success(result.message || 'Escenario procesado con éxito!');
        setScenarioResult(result.data);
      } else {
        toast.error(result.message || 'Hubo un error al procesar el escenario.');
      }
    } catch (error) {
      toast.dismiss();
      const apiError = handleApiError(error);
      toast.error(`Error de API: ${apiError.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingInitialData) {
    return (
      <div className="flex justify-center items-center h-64"><LoadingSpinner size="lg" /></div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-yellow-400 mb-6 text-center">
        Configuración del Escenario Logístico
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <Card>
            <h2 className="text-2xl font-semibold text-blue-400 mb-4">1. Flota de Vehículos</h2>
            <VehicleSelector {...{ vehicles, customVehicles, setCustomVehicles, selectedVehicles, setSelectedVehicles }} />
          </Card>
        </div>
        <div className="space-y-6">
          <Card className={!isVehicleSelected ? 'opacity-50 pointer-events-none' : ''}>
            <h2 className="text-2xl font-semibold text-blue-400 mb-4">2. Escenario y Rutas</h2>
            {!isVehicleSelected && <p className="text-yellow-400 text-center">Selecciona al menos un vehículo para continuar.</p>}
            <div className="space-y-6">
              <DisasterSelector {...{ disasters, selectedDisaster, setSelectedDisaster }} />
              {mapData?.rutas_data && <RouteConfigurator {...{ routesData: mapData.rutas_data, vehicleTypes, routeStates, setRouteStates }} />}
            </div>
          </Card>
        </div>
      </div>

      {isVehicleSelected && selectedDisaster && (
        <ScenarioPreview {...{ expandedFleet, selectedDisaster, routeStates, onGenerate: handleRunScenario, isSubmitting }} />
      )}

      {scenarioResult && (
        <Card>
          <h2 className="text-2xl font-semibold text-green-400 mb-4">Resultado del Escenario</h2>
          <pre className="bg-gray-900 p-4 rounded-md text-gray-200 overflow-x-auto">
            {JSON.stringify(scenarioResult, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  );
};

export default AGPage;