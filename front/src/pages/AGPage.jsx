import { useState, useMemo } from 'react';
import { Card, Button, LoadingSpinner } from '../components/UI';
import { useAG } from '../hooks/useAG';
import apiService, { handleApiError } from '../services/apiService';
import toast from 'react-hot-toast';
import { useLocation } from 'react-router-dom';

import VehicleSelector from '../components/AG/VehicleSelector';
import DisasterSelector from '../components/AG/DisasterSelector';
import RouteConfigurator from '../components/AG/RouteConfigurator';
import ScenarioPreview from '../components/AG/ScenarioPreview';
import AGResultsPage from '../components/AG/AGResultsPage';

const AGPage = () => {
  const location = useLocation();
  const { mapData } = location.state || {};
  
  const { vehicles, disasters, isLoading: isLoadingInitialData } = useAG();

  const [selectedVehicles, setSelectedVehicles] = useState({});
  const [customVehicles, setCustomVehicles] = useState([]);
  const [selectedDisaster, setSelectedDisaster] = useState('');
  const [routeStates, setRouteStates] = useState({});
  
  const [currentView, setCurrentView] = useState('config');
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
        vehiclesList.push({ 
          ...vehicleInfo, 
          matricula: uniqueMatricula,
          velocidad_kmh: parseFloat(vehicleInfo.velocidad_kmh) || 60,
          consumo_litros_km: parseFloat(vehicleInfo.consumo_litros_km) || 0.1,
          maximo_peso_ton: parseFloat(vehicleInfo.maximo_peso_ton) || 1,
          capacidad_kg: parseFloat(vehicleInfo.capacidad_kg) || parseFloat(vehicleInfo.maximo_peso_ton) * 1000 || 1000
        });
      }
      return vehiclesList;
    });
  }, [selectedVehicles, allVehicles]);

  const normalizeMapData = (mapData) => {
    if (!mapData || !mapData.rutas_data) return mapData;

    return {
      ...mapData,
      rutas_data: mapData.rutas_data.map((destino, index) => ({
        ...destino,
        indice: index,
        destino: {
          ...destino.destino,
          poblacion: parseInt(destino.destino.poblacion) || 100,
          clave_localidad: parseInt(destino.destino.clave_localidad) || index + 1,
          lat: parseFloat(destino.destino.lat) || 0,
          lng: parseFloat(destino.destino.lng) || 0
        },
        rutas: (destino.rutas || []).map(ruta => ({
          ...ruta,
          distancia: {
            ...ruta.distancia,
            value: parseFloat(ruta.distancia?.value) || 0
          }
        }))
      }))
    };
  };

  const handleRunScenario = async () => {
    if (!mapData) {
        toast.error("Faltan los datos del mapa. Por favor, genera un mapa primero.");
        return;
    }

    const normalizedMapData = normalizeMapData(mapData);

    const scenarioData = {
      map_data: {
        nodo_principal: {
          ...normalizedMapData.nodo_principal,
          lat: parseFloat(normalizedMapData.nodo_principal.lat) || 0,
          lng: parseFloat(normalizedMapData.nodo_principal.lng) || 0,
          poblacion: parseInt(normalizedMapData.nodo_principal.poblacion) || 100
        },
        nodos_secundarios: (normalizedMapData.nodos_secundarios || []).map(nodo => ({
          ...nodo,
          lat: parseFloat(nodo.lat) || 0,
          lng: parseFloat(nodo.lng) || 0,
          poblacion: parseInt(nodo.poblacion) || 100,
          distancia_directa: parseFloat(nodo.distancia_directa) || 0
        })),
        rutas_data: normalizedMapData.rutas_data,
        municipio_info: normalizedMapData.municipio_info,
      },
      scenario_config: {
        tipo_desastre: selectedDisaster,
        vehiculos_disponibles: expandedFleet.map(({ vehiculo_id, ...rest }) => ({
          ...rest,
          velocidad_kmh: parseFloat(rest.velocidad_kmh) || 60,
          consumo_litros_km: parseFloat(rest.consumo_litros_km) || 0.1,
          maximo_peso_ton: parseFloat(rest.maximo_peso_ton) || 1,
          capacidad_kg: parseFloat(rest.capacidad_kg) || 1000
        })),
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
        setCurrentView('results');
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

  const handleBackToConfig = () => {
    setCurrentView('config');
  };

  const handleNavigateToMap = () => {
    window.location.href = '/mapas';
  };

  if (isLoadingInitialData) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Mostrar página de resultados completa
  if (currentView === 'results' && scenarioResult) {
    return (
      <AGResultsPage 
        scenarioResult={scenarioResult}
        mapData={mapData}
        onNavigateBack={handleBackToConfig}
        onNavigateToMap={handleNavigateToMap}
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-yellow-400 mb-2">
          Configuración del Escenario Logístico
        </h1>
        <p className="text-gray-300">
          Configura vehículos, tipo de desastre y estado de rutas para ejecutar el algoritmo genético
        </p>
      </div>

      {!mapData && (
        <div className="bg-red-900 border border-red-700 rounded-lg p-4 text-center">
          <p className="text-red-300 mb-2">⚠️ No hay datos de mapa disponibles</p>
          <p className="text-sm text-red-400">
            Por favor, ve al generador de mapas y crea un escenario antes de continuar.
          </p>
          <Button 
            onClick={handleNavigateToMap}
            variant="danger"
            className="mt-3"
          >
            Ir al Generador de Mapas
          </Button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
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

        <div className="space-y-6">
          <Card className={!isVehicleSelected ? 'opacity-50 pointer-events-none' : ''}>
            <h2 className="text-2xl font-semibold text-blue-400 mb-4">2. Escenario y Rutas</h2>
            {!isVehicleSelected && (
              <p className="text-yellow-400 text-center mb-4">
                Selecciona al menos un vehículo para continuar.
              </p>
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
                  vehicleTypes={vehicleTypes}
                  routeStates={routeStates}
                  setRouteStates={setRouteStates}
                />
              )}
            </div>
          </Card>
        </div>
      </div>

      {mapData && (
        <Card>
          <h3 className="text-xl font-semibold text-green-400 mb-3">📍 Datos del Mapa Cargado</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <p><span className="font-medium text-gray-300">Origen:</span></p>
              <p className="text-gray-400">{mapData.nodo_principal?.nombre}</p>
            </div>
            <div>
              <p><span className="font-medium text-gray-300">Destinos:</span> {mapData.nodos_secundarios?.length || 0}</p>
              <p><span className="font-medium text-gray-300">Rutas totales:</span> {
                mapData.rutas_data?.reduce((sum, d) => sum + (d.rutas?.length || 0), 0) || 0
              }</p>
            </div>
            <div>
              <p><span className="font-medium text-gray-300">Municipio:</span></p>
              <p className="text-gray-400">{mapData.municipio_info?.nombre_municipio}</p>
            </div>
          </div>
        </Card>
      )}

      {isVehicleSelected && selectedDisaster && mapData && (
        <ScenarioPreview 
          expandedFleet={expandedFleet}
          selectedDisaster={selectedDisaster}
          routeStates={routeStates}
          onGenerate={handleRunScenario}
          isSubmitting={isSubmitting}
        />
      )}

      {scenarioResult && currentView === 'config' && (
        <Card>
          <div className="text-center">
            <h3 className="text-lg font-semibold text-green-400 mb-2">
              ✅ Resultados Disponibles
            </h3>
            <p className="text-gray-300 mb-4">
              Ya tienes resultados generados. Puedes verlos o ejecutar un nuevo escenario.
            </p>
            <Button 
              onClick={() => setCurrentView('results')}
              variant="success"
            >
              Ver Resultados Anteriores
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default AGPage;