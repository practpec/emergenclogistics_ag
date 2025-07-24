import { useState, useMemo, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAG } from '../features/ag_scenario/hooks/useAG.js';
import toast from 'react-hot-toast';
import apiService from '../services/apiService.js';

import MapSummary from '../components/ag/MapSummary.jsx';
import VehicleSelector from '../components/ag/VehicleSelector.jsx';
import DisasterSelector from '../components/ag/DisasterSelector.jsx';
import RouteConfigurator from '../components/ag/RouteConfigurator.jsx';
import ScenarioPreview from '../components/ag/ScenarioPreview.jsx';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Button } from '../components/common/Button';

const AGPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { mapData } = location.state || {};
  
  const { vehicles, disasters, isLoading: isLoadingInitialData } = useAG();

  const [selectedVehicles, setSelectedVehicles] = useState({});
  const [selectedDisaster, setSelectedDisaster] = useState('');
  const [routeStates, setRouteStates] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // --- NUEVO ESTADO PARA PARÁMETROS DEL AG ---
  const [agParams, setAgParams] = useState({
    poblacion_size: 80,
    generaciones: 200, 
    prob_cruza: 0.85, 
    prob_mutacion: 0.20, 
    elitismo_rate: 0.15
  });

  const expandedFleet = useMemo(() => {
    return Object.entries(selectedVehicles).flatMap(([id, quantity]) => {
      const vehicleInfo = vehicles.find(v => String(v.vehiculo_id) === id);
      if (!vehicleInfo || !quantity || quantity <= 0) return [];
      return Array.from({ length: quantity }, (_, i) => ({
        ...vehicleInfo,
        matricula: `${vehicleInfo.modelo.substring(0, 3).toUpperCase()}${id}-${i + 1}`
      }));
    });
  }, [selectedVehicles, vehicles]);
  
  const activeVehicleTypes = useMemo(() => {
    const activeVehicles = vehicles.filter(v => (selectedVehicles[v.vehiculo_id] || 0) > 0);
    return [...new Set(activeVehicles.map(v => v.tipo))];
  }, [selectedVehicles, vehicles]);

  // --- LÓGICA DE ESTADO CORREGIDA Y SIMPLIFICADA ---
  useEffect(() => {
    if (!mapData || vehicles.length === 0) return;

    const newRouteStates = {};
    mapData.rutas_data.forEach((destinoData, destIndex) => {
      if (destinoData.rutas) {
        newRouteStates[destIndex] = destinoData.rutas.map(() => ({
          estado: 'abierta',
          vehiculos_permitidos: [...activeVehicleTypes],
        }));
      }
    });
    setRouteStates(newRouteStates);
    
  }, [mapData, activeVehicleTypes, vehicles]);

  const isReadyForPreview = useMemo(() => {
    return selectedDisaster !== '' && expandedFleet.length > 0;
  }, [selectedDisaster, expandedFleet]);

  const handleRunScenario = async () => {
    setIsSubmitting(true);
    toast.loading('Procesando escenario... Esto puede tardar varios minutos.');

    const scenarioData = {
        map_data: mapData,
        scenario_config: {
            tipo_desastre: selectedDisaster,
            vehiculos_disponibles: expandedFleet,
            rutas_estado: Object.values(routeStates).flat(),
            ag_params: agParams // Se añaden los nuevos parámetros
        }
    };

    console.log("Enviando al backend:", scenarioData);

    try {
      const result = await apiService.runAGScenario(scenarioData);
      toast.dismiss();
      if (result.success) {
        toast.success('Escenario procesado con éxito!');
        console.log("Resultados del AG:", result.data);
      } else {
        toast.error(result.message || 'Error al procesar el escenario.');
      }
    } catch (error) {
      toast.dismiss();
      toast.error(`Error de API: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingInitialData) {
    return <div className="h-screen flex justify-center items-center"><LoadingSpinner size="lg" /></div>;
  }
  
  if (!mapData) {
      return (
          <div className="h-screen flex flex-col justify-center items-center text-center p-4">
              <h2 className="text-2xl font-bold text-red-400">Error: No hay datos de mapa</h2>
              <p className="text-gray-400 mt-2">Debes generar un mapa antes de poder configurar un escenario.</p>
              <Button onClick={() => navigate('/map-generator')} className="mt-6">Volver al Generador de Mapas</Button>
          </div>
      );
  }

  return (
    <div className="p-4 max-w-screen-2xl mx-auto space-y-4">
      <div className="text-center">
        <h1 className="text-2xl md:text-3xl font-bold text-yellow-400">Configuración del Escenario Logístico</h1>
        <p className="text-sm md:text-base text-gray-300">Define los parámetros para la optimización.</p>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4" style={{ height: 'calc(100vh - 230px)' }}>
        <div className="flex flex-col min-h-0"><MapSummary mapData={mapData} /></div>
        <div className="flex flex-col min-h-0"><VehicleSelector vehicles={vehicles} selectedVehicles={selectedVehicles} setSelectedVehicles={setSelectedVehicles} /></div>
        <div className="flex flex-col min-h-0 gap-4">
            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <h2 className="text-xl font-bold text-blue-400 border-b border-gray-600 pb-2 mb-3">2. Condiciones</h2>
                <DisasterSelector disasters={disasters} selectedDisaster={selectedDisaster} setSelectedDisaster={setSelectedDisaster} />
            </div>
            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 flex-grow min-h-0">
                <RouteConfigurator 
                    routesData={mapData.rutas_data} 
                    activeVehicleTypes={activeVehicleTypes} 
                    routeStates={routeStates} 
                    setRouteStates={setRouteStates} 
                />
            </div>
        </div>
      </div>
      {isReadyForPreview && (
          <ScenarioPreview
            expandedFleet={expandedFleet}
            selectedDisaster={selectedDisaster}
            routeStates={routeStates}
            activeVehicleTypes={activeVehicleTypes}
            onGenerate={handleRunScenario}
            isSubmitting={isSubmitting}
            agParams={agParams}
            setAgParams={setAgParams}
          />
      )}
    </div>
  );
};

export default AGPage;