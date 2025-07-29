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
  
  const { vehicles, disasters, supplies, isLoading: isLoadingInitialData } = useAG();

  const [selectedVehicles, setSelectedVehicles] = useState({});
  const [selectedDisaster, setSelectedDisaster] = useState('');
  const [routeStates, setRouteStates] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [agParams, setAgParams] = useState({
    poblacion_size: 80,
    generaciones: 200, 
    prob_cruza: 0.85, 
    prob_mutacion: 0.20, 
    elitismo_rate: 0.15
  });

  const expandedFleet = useMemo(() => {
    return Object.entries(selectedVehicles).flatMap(([vehicleId, quantity]) => {
      const vehicleInfo = vehicles.find(v => String(v.id) === vehicleId);
      if (!vehicleInfo || !quantity || quantity <= 0) return [];
      return Array.from({ length: quantity }, () => ({
        modelo: vehicleInfo.modelo,
        tipo: vehicleInfo.tipo,
        cantidad: 1
      }));
    });
  }, [selectedVehicles, vehicles]);
  
  const activeVehicleTypes = useMemo(() => {
    const activeVehicleIds = Object.keys(selectedVehicles).filter(id => selectedVehicles[id] > 0);
    const activeVehicles = vehicles.filter(v => activeVehicleIds.includes(String(v.id)));
    return [...new Set(activeVehicles.map(v => v.tipo))];
  }, [selectedVehicles, vehicles]);
  
  const selectedDisasterObject = useMemo(() => {
    return disasters.find(d => d.tipo === selectedDisaster);
  }, [selectedDisaster, disasters]);

  useEffect(() => {
    if (!mapData) return;
    const newRouteStates = {};
    let globalRouteId = 1;
    mapData.rutas_data.forEach((destinoData, destIndex) => {
      if (destinoData.rutas) {
        newRouteStates[destIndex] = destinoData.rutas.map((ruta, routeIndex) => ({
          id: globalRouteId++,  // ✅ ID secuencial único
          distancia_km: ruta.distancia?.value / 1000 || 10,
          clave_localidad: destinoData.destino?.clave_localidad || `LOC${destIndex + 1}`,
          estado: 'abierta',
          vehiculos_permitidos: [...activeVehicleTypes]
        }));
      }
    });
    setRouteStates(newRouteStates);
  }, [mapData, activeVehicleTypes]);

  const isReadyForPreview = useMemo(() => {
    const hasOpenRoute = Object.values(routeStates).flat().some(r => r.estado === 'abierta');
    return selectedDisaster !== '' && expandedFleet.length > 0 && hasOpenRoute;
  }, [selectedDisaster, expandedFleet, routeStates]);

  const handleRunScenario = async () => {
    setIsSubmitting(true);
    toast.loading('Procesando escenario...');
    
    const rutasDataFlat = Object.values(routeStates).flat();
    
    const scenarioData = {
        datos_actuales_frontend_a_backend: {
            map_data: {
                rutas_data: rutasDataFlat
            },
            scenario_config: {
                tipo_desastre: selectedDisaster,
                vehiculos_disponibles: expandedFleet,
                configuracion: agParams
            }
        }
    };

    try {
      const result = await apiService.runAGScenario(scenarioData);
      toast.dismiss();
      if (result.success) {
        toast.success('Escenario procesado con éxito!');
        navigate('/ag-results', { 
            state: { 
                results: result.data, 
                mapData: mapData,
                vehicleData: vehicles,
                suppliesData: supplies,
                scenarioConfig: scenarioData.datos_actuales_frontend_a_backend.scenario_config,
                selectedDisaster: selectedDisasterObject,
                routeStates: routeStates
            } 
        });
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
            selectedDisaster={selectedDisasterObject}
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