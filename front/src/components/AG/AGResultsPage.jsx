import { useState, useEffect } from 'react';
import { Card, Button, Badge, LoadingSpinner } from '../UI';
import { LineChart, BarChart, PieChart, MetricCard, DataTable } from './ChartComponents';
import ResultsMapComponent from './ResultsMapComponent';
import VideoGenerator from './VideoGenerator';

  // Registrar componentes de Chart.js (comentado ya que usamos componentes custom)
  // ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend);

const AGResultsPage = ({ scenarioResult, mapData, onNavigateBack, onNavigateToMap }) => {
  
  const [selectedTab, setSelectedTab] = useState('overview');
  const [selectedIndividual, setSelectedIndividual] = useState(0);

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
    mejores_soluciones, 
    analisis_rendimiento, 
    distribucion_carga, 
    panel_control, 
    rutas_optimizadas,
    reportes_optimizacion,
    evolucion_fitness,
    mapeo_asignaciones 
  } = scenarioResult;

  // Generar datos para gráficas
  const fitnessData = {
    labels: evolucion_fitness?.map(g => `Gen ${g.generacion}`) || [],
    datasets: [
      {
        label: 'Mejor Fitness',
        data: evolucion_fitness?.map(g => g.mejor) || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
      },
      {
        label: 'Promedio',
        data: evolucion_fitness?.map(g => g.promedio) || [],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
      }
    ]
  };

  const vehicleUtilizationData = {
    labels: distribucion_carga?.vehiculos?.map(v => v.modelo) || [],
    datasets: [{
      label: 'Utilización (%)',
      data: distribucion_carga?.vehiculos?.map(v => v.utilizacion_porcentual) || [],
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(34, 197, 94, 0.8)',
        'rgba(251, 191, 36, 0.8)',
        'rgba(239, 68, 68, 0.8)'
      ]
    }]
  };

  const supplyDistributionData = {
    labels: Object.keys(distribucion_carga?.vehiculos?.[0]?.carga_por_categoria || {}),
    datasets: [{
      data: Object.values(distribucion_carga?.vehiculos?.[0]?.carga_por_categoria || {}).map(cat => cat.peso_kg),
      backgroundColor: [
        '#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'
      ]
    }]
  };

  // Remover funciones de video que no se necesitan aquí

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

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Evolución del Fitness</h3>
        <LineChart 
          data={fitnessData} 
          width={800} 
          height={300}
          className="w-full"
        />
      </Card>

      {/* Tabla resumen de las mejores soluciones */}
      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Resumen Top 3 Soluciones</h3>
        <DataTable
          headers={['Posición', 'Fitness', 'Peso Total', 'Combustible', 'Localidades', 'Eficiencia']}
          rows={mejores_soluciones.slice(0, 3).map((sol, index) => [
            `#${index + 1}`,
            sol.fitness?.toFixed(2) || '0',
            `${sol.resumen?.peso_total?.toFixed(1) || '0'} kg`,
            `${sol.resumen?.combustible_total?.toFixed(1) || '0'} L`,
            sol.resumen?.localidades_atendidas || '0',
            <Badge key={index} variant={sol.fitness > 800 ? 'success' : sol.fitness > 500 ? 'warning' : 'danger'}>
              {sol.fitness > 800 ? 'Excelente' : sol.fitness > 500 ? 'Buena' : 'Regular'}
            </Badge>
          ])}
        />
      </Card>
    </div>
  );

  const renderTopSolutions = () => (
    <div className="space-y-6">
      <div className="flex space-x-2 mb-4">
        {mejores_soluciones.map((_, index) => (
          <Button
            key={index}
            onClick={() => setSelectedIndividual(index)}
            variant={selectedIndividual === index ? 'primary' : 'secondary'}
            size="sm"
          >
            Solución #{index + 1}
          </Button>
        ))}
      </div>

      {mejores_soluciones[selectedIndividual] && (
        <div className="space-y-4">
          <Card>
            <h3 className="text-xl font-semibold text-yellow-400 mb-4">
              Solución #{selectedIndividual + 1} - Fitness: {mejores_soluciones[selectedIndividual].fitness.toFixed(2)}
            </h3>
            
            <DataTable
              headers={['Vehículo', 'Destino', 'Población', 'Distancia', 'Peso Carga', 'Utilización', 'Combustible']}
              rows={mejores_soluciones[selectedIndividual].vehiculos.map((vehiculo, index) => [
                vehiculo.modelo,
                vehiculo.destino_nombre,
                vehiculo.destino_poblacion.toLocaleString(),
                `${vehiculo.distancia_km.toFixed(1)} km`,
                `${vehiculo.peso_total_kg.toFixed(1)} kg`,
                <Badge key={index} variant={vehiculo.utilizacion_capacidad > 0.7 ? 'success' : vehiculo.utilizacion_capacidad > 0.5 ? 'warning' : 'danger'}>
                  {(vehiculo.utilizacion_capacidad * 100).toFixed(1)}%
                </Badge>,
                `${vehiculo.combustible_litros.toFixed(1)} L`
              ])}
            />
          </Card>

          <Card>
            <h4 className="text-lg font-semibold text-blue-400 mb-4">Detalles de Insumos por Vehículo</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mejores_soluciones[selectedIndividual].vehiculos.map((vehiculo, vIndex) => (
                <div key={vIndex} className="bg-gray-700 p-4 rounded">
                  <h5 className="font-semibold text-yellow-400 mb-2">{vehiculo.modelo} → {vehiculo.destino_nombre}</h5>
                  <div className="space-y-1 text-sm">
                    {vehiculo.insumos_detalle.map((insumo, iIndex) => (
                      <div key={iIndex} className="flex justify-between">
                        <span>{insumo.nombre}</span>
                        <span>{insumo.cantidad} ({insumo.peso_total_kg.toFixed(1)} kg)</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );

  const renderDistributionAnalysis = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-xl font-semibold text-yellow-400 mb-4">Utilización por Vehículo</h3>
          <BarChart 
            data={vehicleUtilizationData} 
            width={400} 
            height={250}
            className="w-full"
          />
        </Card>

        <Card>
          <h3 className="text-xl font-semibold text-yellow-400 mb-4">Distribución de Insumos</h3>
          <PieChart 
            data={supplyDistributionData} 
            width={300} 
            height={250}
            className="w-full"
          />
        </Card>
      </div>

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
    </div>
  );

  const renderMapView = () => (
    <ResultsMapComponent 
      mapData={mapData}
      assignedVehicles={mejores_soluciones[0]?.vehiculos}
      className="h-96"
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
            entrega.destino,
            `${entrega.tiempo_estimado_horas?.toFixed(1)}h`,
            <Badge key={index} variant={entrega.estado === 'COMPLETADA' ? 'success' : 'danger'}>
              {entrega.estado}
            </Badge>,
            `${entrega.peso_entregado_kg?.toFixed(1)} kg`,
            entrega.poblacion_beneficiada?.toLocaleString() || '0'
          ]) || []}
        />
      </Card>
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
    { id: 'video', label: 'Generar Video', content: renderVideoGeneration }
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-yellow-400 mb-2">Resultados del Algoritmo Genético</h1>
        <p className="text-gray-300">Análisis completo de la optimización logística</p>
      </div>

      {/* Tabs */}
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

      {/* Content */}
      <div className="min-h-96">
        {tabs.find(tab => tab.id === selectedTab)?.content()}
      </div>

      {/* Navigation */}
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