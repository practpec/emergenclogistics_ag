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

const AGPage = () => {
  // Obtener mapData desde location.state en tu archivo real
  const location = useLocation();
  const { mapData } = location.state || {};
  
  // // Para este ejemplo, asumo que mapData se pasa como prop o está disponible
  // const mapData = window.location.state?.mapData || null;
  const { vehicles, disasters, isLoading: isLoadingInitialData } = useAG();

  // Estados para la configuración
  const [selectedVehicles, setSelectedVehicles] = useState({});
  const [customVehicles, setCustomVehicles] = useState([]);
  const [selectedDisaster, setSelectedDisaster] = useState('');
  const [routeStates, setRouteStates] = useState({});
  
  // Estados para el flujo de la aplicación
  const [currentView, setCurrentView] = useState('config'); // 'config' | 'results'
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
        setCurrentView('results');
      } else {
        toast.error(result.message || 'Hubo un error al procesar el escenario.');
      }
    } catch (error) {
      toast.dismiss();
      const apiError = handleApiError(error);
      toast.error(`Error de API: ${apiError.message}`);
      
      // Log para debug (temporal)
      console.error('Error completo:', error);
      console.error('Datos enviados:', scenarioData);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBackToConfig = () => {
    setCurrentView('config');
  };

  const handleNavigateToMap = () => {
    // Esto se manejaría con React Router en una implementación completa
    window.location.href = '/mapas';
  };

  if (isLoadingInitialData) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Mostrar resultados si están disponibles y la vista está en 'results'
  if (currentView === 'results' && scenarioResult) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-yellow-400 mb-2">Resultados del Algoritmo Genético</h1>
          <p className="text-gray-300">Análisis completo de la optimización logística</p>
        </div>

        {/* Mostrar datos del resultado */}
        <Card>
          <h2 className="text-xl font-semibold text-green-400 mb-4">✅ Escenario Procesado</h2>
          <div className="bg-gray-900 p-4 rounded-md">
            <pre className="text-gray-200 text-sm overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(scenarioResult, null, 2)}
            </pre>
          </div>
        </Card>

        {/* Botones de navegación */}
        <div className="flex justify-between">
          <Button onClick={handleBackToConfig} variant="secondary">
            ← Volver a Configuración
          </Button>
          <Button onClick={handleNavigateToMap} variant="secondary">
            Generar Nuevo Mapa →
          </Button>
        </div>
      </div>
    );
  }

  // Mostrar configuración
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

      {/* Información del mapa actual */}
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

      {/* Vista previa y ejecución */}
      {isVehicleSelected && selectedDisaster && mapData && (
        <ScenarioPreview 
          expandedFleet={expandedFleet}
          selectedDisaster={selectedDisaster}
          routeStates={routeStates}
          onGenerate={handleRunScenario}
          isSubmitting={isSubmitting}
        />
      )}

      {/* Botón para ver resultados anteriores si existen */}
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