import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

import ScenarioSummary from '../features/ag_results/components/ScenarioSummary';
import SolutionsDisplay from '../features/ag_results/components/SolutionsDisplay';
import OptimizationReport from '../features/ag_results/components/OptimizationReport';

const AGResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { 
    results, 
    mapData, 
    vehicleData, 
    suppliesData, 
    scenarioConfig, 
    selectedDisaster,
    routeStates // Se extrae el estado de las rutas
  } = location.state || {};

  if (!location.state || !results) {
    return (
      <div className="h-screen flex flex-col justify-center items-center text-center p-4">
        <h2 className="text-2xl font-bold text-red-400">Error: No hay datos de resultados</h2>
        <p className="text-gray-400 mt-2">No se pudo cargar la información. Por favor, genera un nuevo escenario.</p>
        <Button onClick={() => navigate('/map-generator')} className="mt-6">Volver al Inicio</Button>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 max-w-screen-xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-light text-yellow-400">Resultados de la Optimización</h1>
        <p className="text-gray-300">Análisis detallado de la simulación logística.</p>
      </div>
      
      <ScenarioSummary 
        mapData={mapData}
        vehicleData={vehicleData}
        scenarioConfig={scenarioConfig}
        selectedDisaster={selectedDisaster}
        routeStates={routeStates} // Se pasa como prop
      />
      
      <SolutionsDisplay 
        results={results}
        mapData={mapData}
        vehicleData={vehicleData}
        suppliesData={suppliesData}
      />
      
      <OptimizationReport 
        reports={results.reportes}
        visualizations={results.visualizaciones}
      />

      <div className="text-center py-6">
        <Button onClick={() => navigate('/map-generator')} variant="secondary" size="lg">
          Configurar un Nuevo Escenario
        </Button>
      </div>
    </div>
  );
};

export default AGResultsPage;