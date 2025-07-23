import { useState, useEffect } from 'react';
import { Card, Button, Badge, LoadingSpinner } from '../UI';
import { BarChart, MetricCard, DataTable } from './ChartComponents';
import AGMapVisualization from './AGMapVisualization';
import VideoGenerator from './VideoGenerator';
import EvolutionChart from './EvolutionChart';
import TopSolutionsAnalysis from './TopSolutionsAnalysis';

const AGResultsPage = ({ scenarioResult, mapData, onNavigateBack, onNavigateToMap }) => {
  
  const [selectedTab, setSelectedTab] = useState('overview');

  useEffect(() => {
    if (!scenarioResult && onNavigateBack) {
      onNavigateBack();
    }
  }, [scenarioResult, onNavigateBack]);

  if (!scenarioResult) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const { 
    mejores_soluciones = [], 
    analisis_rendimiento = {}, 
    distribucion_carga = {}, 
    panel_control = {}, 
    evolucion_fitness = [],
    parametros_ag = {}
  } = scenarioResult;

  // Datos para gráficas optimizadas
  const vehicleUtilizationData = {
    labels: distribucion_carga?.vehiculos?.map(v => v.modelo || 'Vehículo') || [],
    datasets: [{
      label: 'Utilización (%)',
      data: distribucion_carga?.vehiculos?.map(v => parseFloat(v.utilizacion_porcentual) || 0) || [],
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(34, 197, 94, 0.8)',
        'rgba(251, 191, 36, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(139, 92, 246, 0.8)',
        'rgba(6, 182, 212, 0.8)'
      ]
    }]
  };

  const renderOverview = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Mejor Fitness"
          value={mejores_soluciones[0]?.fitness?.toFixed(2) || '0'}
          variant="success"
        />
        <MetricCard
          title="Localidades Atendidas"
          value={mejores_soluciones[0]?.resumen?.localidades_atendidas || '0'}
          variant="info"
        />
        <MetricCard
          title="Peso Total"
          value={`${mejores_soluciones[0]?.resumen?.peso_total?.toFixed(1) || '0'} kg`}
          variant="warning"
        />
        <MetricCard
          title="Combustible"
          value={`${mejores_soluciones[0]?.resumen?.combustible_total?.toFixed(1) || '0'} L`}
          variant="danger"
        />
      </div>

      <EvolutionChart evolutionData={evolucion_fitness} />

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Parámetros del Algoritmo Genético</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <MetricCard
            title="Población"
            value={parametros_ag.poblacion_size || 'N/A'}
            variant="info"
          />
          <MetricCard
            title="Generaciones"
            value={parametros_ag.generaciones || 'N/A'}
            variant="info"
          />
          <MetricCard
            title="Prob. Cruza"
            value={`${(parseFloat(parametros_ag.prob_cruza) * 100 || 0).toFixed(0)}%`}
            variant="info"
          />
          <MetricCard
            title="Prob. Mutación"
            value={`${(parseFloat(parametros_ag.prob_mutacion) * 100 || 0).toFixed(1)}%`}
            variant="info"
          />
          <MetricCard
            title="Elitismo"
            value={`${(parseFloat(parametros_ag.elitismo_rate) * 100 || 0).toFixed(1)}%`}
            variant="info"
          />
        </div>
      </Card>
    </div>
  );

  const renderTopSolutions = () => (
    <TopSolutionsAnalysis mejoresSoluciones={mejores_soluciones} />
  );

  const renderDistributionAnalysis = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Utilización por Vehículo</h3>
        <BarChart 
          data={vehicleUtilizationData} 
          width={800} 
          height={300}
          className="w-full"
        />
      </Card>

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Resumen Global de Carga</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            title="Capacidad Total"
            value={`${distribucion_carga?.resumen_global?.capacidad_total_kg?.toFixed(0) || '0'} kg`}
            variant="info"
          />
          <MetricCard
            title="Peso Utilizado"
            value={`${distribucion_carga?.resumen_global?.peso_total_utilizado_kg?.toFixed(0) || '0'} kg`}
            variant="success"
          />
          <MetricCard
            title="Utilización Global"
            value={`${distribucion_carga?.resumen_global?.utilizacion_global_porcentual?.toFixed(1) || '0'}%`}
            variant="warning"
          />
          <MetricCard
            title="Espacio Desperdiciado"
            value={`${distribucion_carga?.resumen_global?.espacio_desperdiciado_kg?.toFixed(0) || '0'} kg`}
            variant="danger"
          />
        </div>
      </Card>

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Análisis por Vehículo</h3>
        <DataTable
          headers={['Vehículo', 'Tipo', 'Capacidad', 'Peso Usado', 'Utilización', 'Eficiencia']}
          rows={distribucion_carga?.vehiculos?.map((vehiculo, index) => [
            vehiculo.modelo || 'N/A',
            vehiculo.tipo || 'N/A',
            `${vehiculo.capacidad_kg?.toFixed(0) || '0'} kg`,
            `${vehiculo.peso_utilizado_kg?.toFixed(0) || '0'} kg`,
            `${vehiculo.utilizacion_porcentual?.toFixed(1) || '0'}%`,
            <Badge key={index} variant={
              vehiculo.eficiencia_carga === 'OPTIMA' ? 'success' : 
              vehiculo.eficiencia_carga === 'BUENA' ? 'warning' : 'danger'
            }>
              {vehiculo.eficiencia_carga || 'N/A'}
            </Badge>
          ]) || []}
        />
      </Card>
    </div>
  );

  const renderMapView = () => (
    <AGMapVisualization 
      mapData={mapData}
      mejoresSoluciones={mejores_soluciones}
      className="h-auto"
    />
  );

  const renderControlPanel = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Métricas de Eficiencia</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            title="Tasa de Éxito"
            value={`${panel_control?.metricas_eficiencia?.tasa_exito_porcentual?.toFixed(1) || '0'}%`}
            variant="success"
          />
          <MetricCard
            title="Peso Entregado"
            value={`${panel_control?.metricas_eficiencia?.peso_total_entregado_kg?.toFixed(0) || '0'} kg`}
            variant="info"
          />
          <MetricCard
            title="Población Beneficiada"
            value={panel_control?.metricas_eficiencia?.poblacion_total_beneficiada?.toLocaleString() || '0'}
            variant="warning"
          />
          <MetricCard
            title="kg por Persona"
            value={`${panel_control?.metricas_eficiencia?.promedio_kg_por_persona?.toFixed(2) || '0'} kg`}
            variant="danger"
          />
        </div>
      </Card>

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Cronología de Entregas</h3>
        <DataTable
          headers={['Orden', 'Destino', 'Tiempo Estimado', 'Estado', 'Peso Entregado', 'Población Beneficiada']}
          rows={panel_control?.cronologia_entregas?.map((entrega, index) => [
            index + 1,
            entrega.destino || 'N/A',
            `${entrega.tiempo_estimado_horas?.toFixed(1) || '0'}h`,
            <Badge key={index} variant={entrega.estado === 'COMPLETADA' ? 'success' : 'danger'}>
              {entrega.estado || 'DESCONOCIDO'}
            </Badge>,
            `${entrega.peso_entregado_kg?.toFixed(1) || '0'} kg`,
            entrega.poblacion_beneficiada?.toLocaleString() || '0'
          ]) || []}
        />
      </Card>
    </div>
  );

  const renderPerformanceAnalysis = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Análisis de Rendimiento</h3>
        <DataTable
          headers={['Individuo', 'Fitness', 'Tiempo Total', 'Distancia Total', 'Nodos Visitados', 'Combustible', 'Peso Total', 'Eficiencia']}
          rows={analisis_rendimiento?.comparacion_top_3?.map((comp, index) => [
            `Solución ${comp.individuo || index + 1}`,
            comp.fitness?.toFixed(2) || '0',
            `${comp.tiempo_total_horas?.toFixed(1) || '0'}h`,
            `${comp.distancia_total_km?.toFixed(1) || '0'} km`,
            comp.nodos_visitados || '0',
            `${comp.combustible_total_litros?.toFixed(1) || '0'} L`,
            `${comp.peso_total_kg?.toFixed(1) || mejores_soluciones[index]?.resumen?.peso_total?.toFixed(1) || '0'} kg`,
            comp.eficiencia_tiempo?.toFixed(2) || '0'
          ]) || []}
        />
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <h4 className="text-lg font-semibold text-blue-400 mb-3">Mejor en Tiempo</h4>
          <div className="space-y-2 text-sm">
            <p><span className="font-medium">Individuo:</span> {analisis_rendimiento?.mejor_tiempo?.individuo || 'N/A'}</p>
            <p><span className="font-medium">Tiempo:</span> {analisis_rendimiento?.mejor_tiempo?.tiempo_total_horas?.toFixed(1) || '0'}h</p>
            <p><span className="font-medium">Fitness:</span> {analisis_rendimiento?.mejor_tiempo?.fitness?.toFixed(2) || '0'}</p>
          </div>
        </Card>

        <Card>
          <h4 className="text-lg font-semibold text-blue-400 mb-3">Mejor en Distancia</h4>
          <div className="space-y-2 text-sm">
            <p><span className="font-medium">Individuo:</span> {analisis_rendimiento?.mejor_distancia?.individuo || 'N/A'}</p>
            <p><span className="font-medium">Distancia:</span> {analisis_rendimiento?.mejor_distancia?.distancia_total_km?.toFixed(1) || '0'} km</p>
            <p><span className="font-medium">Fitness:</span> {analisis_rendimiento?.mejor_distancia?.fitness?.toFixed(2) || '0'}</p>
          </div>
        </Card>

        <Card>
          <h4 className="text-lg font-semibold text-blue-400 mb-3">Mejor en Combustible</h4>
          <div className="space-y-2 text-sm">
            <p><span className="font-medium">Individuo:</span> {analisis_rendimiento?.mejor_combustible?.individuo || 'N/A'}</p>
            <p><span className="font-medium">Combustible:</span> {analisis_rendimiento?.mejor_combustible?.combustible_total_litros?.toFixed(1) || '0'} L</p>
            <p><span className="font-medium">Fitness:</span> {analisis_rendimiento?.mejor_combustible?.fitness?.toFixed(2) || '0'}</p>
          </div>
        </Card>

        <Card>
          <h4 className="text-lg font-semibold text-blue-400 mb-3">Mejor en Carga</h4>
          <div className="space-y-2 text-sm">
            {(() => {
              // Encontrar el que llevó más peso
              const mejorCarga = mejores_soluciones.reduce((best, current, index) => {
                const pesoActual = current.resumen?.peso_total || 0;
                const pesoMejor = best.peso || 0;
                return pesoActual > pesoMejor ? { individuo: index + 1, peso: pesoActual, fitness: current.fitness } : best;
              }, { individuo: 1, peso: 0, fitness: 0 });
              
              return (
                <>
                  <p><span className="font-medium">Individuo:</span> {mejorCarga.individuo}</p>
                  <p><span className="font-medium">Peso Total:</span> {mejorCarga.peso.toFixed(1)} kg</p>
                  <p><span className="font-medium">Fitness:</span> {mejorCarga.fitness?.toFixed(2) || '0'}</p>
                </>
              );
            })()}
          </div>
        </Card>
      </div>
    </div>
  );

  const renderVideoGeneration = () => (
    <VideoGenerator 
      evolutionData={evolucion_fitness}
      className="w-full"
    />
  );

  const tabs = [
    { id: 'overview', label: 'Resumen General', content: renderOverview },
    { id: 'solutions', label: 'Top 3 Soluciones', content: renderTopSolutions },
    { id: 'distribution', label: 'Análisis de Carga', content: renderDistributionAnalysis },
    { id: 'map', label: 'Mapa de Resultados', content: renderMapView },
    { id: 'control', label: 'Panel de Control', content: renderControlPanel },
    { id: 'performance', label: 'Análisis de Rendimiento', content: renderPerformanceAnalysis },
    { id: 'video', label: 'Generar Video', content: renderVideoGeneration }
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-yellow-400 mb-2">Resultados del Algoritmo Genético</h1>
        <p className="text-gray-300">Análisis completo de la optimización logística</p>
      </div>

      <div className="flex flex-wrap gap-2 border-b border-gray-600">
        {tabs.map(tab => (
          <Button
            key={tab.id}
            onClick={() => setSelectedTab(tab.id)}
            variant={selectedTab === tab.id ? 'primary' : 'secondary'}
            size="sm"
            className="mb-2"
          >
            {tab.label}
          </Button>
        ))}
      </div>

      <div className="min-h-96">
        {tabs.find(tab => tab.id === selectedTab)?.content()}
      </div>

      <div className="flex justify-between">
        <button 
          onClick={onNavigateBack}
          className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
        >
          ← Volver a Configuración
        </button>
        <button 
          onClick={onNavigateToMap}
          className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
        >
          Generar Nuevo Mapa →
        </button>
      </div>
    </div>
  );
};

export default AGResultsPage;