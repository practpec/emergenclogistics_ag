// src/pages/AGResultsPage.jsx
import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';

import EvolutionChart from '../components/ag/results/EvolutionChart';
import TopSolutionsAnalysis from '../components/ag/results/TopSolutionsAnalysis';
import AGMapVisualization from '../components/ag/results/AGMapVisualization';
import PerformanceAnalysis from '../components/ag/results/PerformanceAnalysis';
import ScenarioSummary from '../components/ag/results/ScenarioSummary';
import VehicleFleetMap from '../components/ag/results/VehicleFleetMap'; // <-- NUEVO COMPONENTE

const MetricCard = ({ title, value, subtext }) => (
  <div className="bg-gray-800 p-3 rounded-lg text-center border border-gray-700">
    <p className="text-sm text-gray-400">{title}</p>
    <p className="text-2xl font-bold text-yellow-400">{value}</p>
    {subtext && <p className="text-xs text-gray-500">{subtext}</p>}
  </div>
);

const AGResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { results, mapData, vehicleData, scenarioConfig, selectedDisaster } = location.state || {};
  
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedSolutionForMap, setSelectedSolutionForMap] = useState(0);

  if (!results || !results.mejores_soluciones || results.mejores_soluciones.length === 0 || !mapData || !vehicleData || !scenarioConfig || !selectedDisaster) {
    return (
      <div className="h-screen flex flex-col justify-center items-center text-center p-4">
        <h2 className="text-2xl font-bold text-red-400">Error: Datos de resultados inválidos o incompletos</h2>
        <p className="text-gray-400 mt-2">No se encontraron soluciones válidas. Intenta ejecutar el escenario de nuevo.</p>
        <Button onClick={() => navigate('/map-generator')} className="mt-6">Volver al Inicio</Button>
      </div>
    );
  }

  const { mejores_soluciones, evolucion_fitness, convergencia } = results;

  const tabs = [
    { id: 'overview', label: 'Resumen General' },
    { id: 'solutions', label: 'Análisis de Soluciones' },
    { id: 'map', label: 'Mapa de Distribución' },
    { id: 'fleetMap', label: 'Mapa de Flota' }, // <-- NUEVA PESTAÑA
    { id: 'performance', label: 'Análisis de Rendimiento' },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'solutions':
        return <TopSolutionsAnalysis solutions={mejores_soluciones} mapData={mapData} vehicleData={vehicleData} />;
      case 'map':
        return <AGMapVisualization solutions={mejores_soluciones} mapData={mapData} />;
      case 'fleetMap': // <-- RENDERIZADO DE LA NUEVA VISTA
        return (
            <div>
                <div className="mb-4 flex items-center gap-4 bg-gray-800 p-3 rounded-lg border border-gray-700">
                    <label className="text-gray-300 font-semibold">Selecciona una solución para explorar:</label>
                    <div className="flex gap-2">
                        {mejores_soluciones.map((_, index) => (
                            <Button key={index} size="sm" variant={selectedSolutionForMap === index ? 'primary' : 'secondary'} onClick={() => setSelectedSolutionForMap(index)}>
                                Solución #{index + 1}
                            </Button>
                        ))}
                    </div>
                </div>
                <VehicleFleetMap 
                    solution={mejores_soluciones[selectedSolutionForMap]} 
                    mapData={mapData} 
                    vehicleData={vehicleData} 
                />
            </div>
        );
      case 'performance':
        return <PerformanceAnalysis solutions={mejores_soluciones} vehicleData={vehicleData} />;
      case 'overview':
      default:
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <h2 className="text-xl font-semibold text-blue-400 mb-3">Métricas Globales</h2>
              <div className="grid grid-cols-2 gap-4 text-center">
                <MetricCard title="Mejor Fitness" value={mejores_soluciones[0].fitness.toFixed(2)} />
                <MetricCard title="Convergencia" value={`${convergencia.generaciones_ejecutadas} gen.`} subtext={`Mejora del ${convergencia.mejora_porcentual.toFixed(2)}%`} />
                <MetricCard title="Población Atendida" value={mejores_soluciones[0].resumen.poblacion_beneficiada.toLocaleString()} />
                <MetricCard title="Peso Entregado" value={`${(mejores_soluciones[0].resumen.peso_total_entregado / 1000).toFixed(2)} ton`} />
              </div>
            </Card>
            <EvolutionChart evolutionData={evolucion_fitness} />
          </div>
        );
    }
  };

  return (
    <div className="p-4 max-w-screen-2xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-yellow-400">Resultados de la Optimización</h1>
        <p className="text-gray-300">Análisis de las soluciones encontradas por el Algoritmo Genético.</p>
      </div>
      
      <ScenarioSummary 
        mapData={mapData} 
        scenarioConfig={scenarioConfig} 
        selectedDisaster={selectedDisaster}
      />

      <div className="flex gap-2 border-b border-gray-700 mt-6 overflow-x-auto pb-px">
        {tabs.map(tab => (
          <Button key={tab.id} onClick={() => setActiveTab(tab.id)} variant={activeTab === tab.id ? 'primary' : 'secondary'} size="sm" className="rounded-b-none flex-shrink-0">
            {tab.label}
          </Button>
        ))}
      </div>

      <div className="fade-in mt-4">{renderContent()}</div>

      <div className="text-center mt-4">
        <Button onClick={() => navigate('/map-generator')} variant="secondary">
          Configurar Nuevo Escenario
        </Button>
      </div>
    </div>
  );
};

export default AGResultsPage;