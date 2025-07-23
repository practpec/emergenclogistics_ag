import { useState, useEffect } from 'react';
import { Card, Button, Badge, LoadingSpinner } from '../UI';
import { LineChart, BarChart, PieChart, MetricCard, DataTable } from './ChartComponents';
import ResultsMapComponent from './ResultsMapComponent';
import VideoGenerator from './VideoGenerator';

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
    mejores_soluciones = [], 
    analisis_rendimiento = {}, 
    distribucion_carga = {}, 
    panel_control = {}, 
    rutas_optimizadas = {},
    reportes_optimizacion = {},
    evolucion_fitness = [],
    mapeo_asignaciones = [],
    parametros_ag = {},
    configuracion_insumos = []
  } = scenarioResult;

  // Datos para gráficas
  const fitnessData = {
    labels: evolucion_fitness?.map(g => g.generacion?.toString() || '') || [],
    datasets: [
      {
        label: 'Mejor Fitness',
        data: evolucion_fitness?.map(g => parseFloat(g.mejor) || 0) || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
      },
      {
        label: 'Promedio',
        data: evolucion_fitness?.map(g => parseFloat(g.promedio) || 0) || [],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
      }
    ]
  };

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

  const supplyDistributionData = {
    labels: configuracion_insumos?.map(cat => cat.categoria) || [],
    datasets: [{
      data: configuracion_insumos?.map(cat => parseFloat(cat.peso_kg) || 0) || [],
      backgroundColor: [
        '#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'
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

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Evolución del Fitness</h3>
        <LineChart 
          data={fitnessData} 
          width={800} 
          height={300}
          className="w-full"
        />
      </Card>

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
              Solución #{selectedIndividual + 1} - Fitness: {mejores_soluciones[selectedIndividual].fitness?.toFixed(2) || '0'}
            </h3>
            
            <DataTable
              headers={['Vehículo', 'Destino', 'Población', 'Distancia', 'Peso Carga', 'Utilización', 'Combustible']}
              rows={mejores_soluciones[selectedIndividual].vehiculos?.map((vehiculo, index) => [
                vehiculo.modelo || 'N/A',
                vehiculo.destino_nombre || 'N/A',
                (vehiculo.destino_poblacion || 0).toLocaleString(),
                `${vehiculo.distancia_km?.toFixed(1) || '0'} km`,
                `${vehiculo.peso_total_kg?.toFixed(1) || '0'} kg`,
                <Badge key={index} variant={vehiculo.utilizacion_capacidad > 0.7 ? 'success' : vehiculo.utilizacion_capacidad > 0.5 ? 'warning' : 'danger'}>
                  {((vehiculo.utilizacion_capacidad || 0) * 100).toFixed(1)}%
                </Badge>,
                `${vehiculo.combustible_litros?.toFixed(1) || '0'} L`
              ]) || []}
            />
          </Card>

          <Card>
            <h4 className="text-lg font-semibold text-blue-400 mb-4">Detalles de Insumos por Vehículo</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mejores_soluciones[selectedIndividual].vehiculos?.map((vehiculo, vIndex) => (
                <div key={vIndex} className="bg-gray-700 p-4 rounded">
                  <h5 className="font-semibold text-yellow-400 mb-2">
                    {vehiculo.modelo || 'Vehículo'} → {vehiculo.destino_nombre || 'Destino'}
                  </h5>
                  <div className="space-y-1 text-sm">
                    {vehiculo.insumos_detalle?.map((insumo, iIndex) => (
                      <div key={iIndex} className="flex justify-between">
                        <span>{insumo.nombre || 'Insumo'}</span>
                        <span>{insumo.cantidad || 0} ({insumo.peso_total_kg?.toFixed(1) || '0'} kg)</span>
                      </div>
                    )) || <p className="text-gray-400">Sin insumos detallados</p>}
                  </div>
                </div>
              )) || <p className="text-gray-400">Sin vehículos asignados</p>}
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
          <h3 className="text-xl font-semibold text-yellow-400 mb-4">Categorías de Insumos</h3>
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

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Estados por Destino</h3>
        <DataTable
          headers={['Destino', 'Población', 'Vehículos Asignados', 'Peso Total', 'Entregas Exitosas', 'Entregas Fallidas']}
          rows={panel_control?.estados_destinos?.map((destino, index) => [
            destino.nombre || 'N/A',
            destino.poblacion?.toLocaleString() || '0',
            destino.vehiculos_asignados || '0',
            `${destino.peso_total_kg?.toFixed(1) || '0'} kg`,
            destino.entregas_exitosas || '0',
            destino.entregas_fallidas || '0'
          ]) || []}
        />
      </Card>
    </div>
  );

  const renderAnalysisReport = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Análisis de Rendimiento</h3>
        <DataTable
          headers={['Individuo', 'Fitness', 'Tiempo Total', 'Distancia Total', 'Nodos Visitados', 'Combustible', 'Eficiencia']}
          rows={analisis_rendimiento?.comparacion_top_3?.map((comp, index) => [
            `Solución ${comp.individuo || index + 1}`,
            comp.fitness?.toFixed(2) || '0',
            `${comp.tiempo_total_horas?.toFixed(1) || '0'}h`,
            `${comp.distancia_total_km?.toFixed(1) || '0'} km`,
            comp.nodos_visitados || '0',
            `${comp.combustible_total_litros?.toFixed(1) || '0'} L`,
            comp.eficiencia_tiempo?.toFixed(2) || '0'
          ]) || []}
        />
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
      </div>

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Rutas Optimizadas</h3>
        <div className="space-y-4">
          {Object.entries(rutas_optimizadas?.rutas_por_destino || {}).map(([destinoId, ruta]) => (
            <div key={destinoId} className="bg-gray-700 p-4 rounded">
              <h4 className="font-semibold text-blue-400 mb-2">{ruta.destino_nombre || `Destino ${destinoId}`}</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p><span className="font-medium">Ruta Seleccionada:</span> {ruta.ruta_seleccionada + 1 || 'N/A'}</p>
                  <p><span className="font-medium">Distancia:</span> {ruta.distancia_seleccionada?.toFixed(1) || '0'} km</p>
                </div>
                <div>
                  <p><span className="font-medium">Rutas Disponibles:</span> {ruta.rutas_disponibles || '0'}</p>
                  <p><span className="font-medium">Alternativas:</span> {ruta.alternativas?.length || '0'}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Evolución del Algoritmo</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            title="Generaciones"
            value={reportes_optimizacion?.analisis_evolucion?.generaciones_totales || '0'}
            variant="info"
          />
          <MetricCard
            title="Fitness Inicial"
            value={reportes_optimizacion?.analisis_evolucion?.fitness_inicial?.toFixed(2) || '0'}
            variant="warning"
          />
          <MetricCard
            title="Fitness Final"
            value={reportes_optimizacion?.analisis_evolucion?.fitness_final?.toFixed(2) || '0'}
            variant="success"
          />
          <MetricCard
            title="Mejora %"
            value={`${reportes_optimizacion?.analisis_evolucion?.mejora_porcentual?.toFixed(1) || '0'}%`}
            variant="success"
          />
        </div>
      </Card>
    </div>
  );

  const renderVideoGeneration = () => (
    <VideoGenerator 
      evolutionData={evolucion_fitness}
      className="w-full"
    />
  );

  const renderRawData = () => (
    <div className="space-y-6">
      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Datos Completos del Resultado</h3>
        <div className="bg-gray-900 p-4 rounded-md max-h-96 overflow-y-auto">
          <pre className="text-gray-200 text-sm whitespace-pre-wrap">
            {JSON.stringify(scenarioResult, null, 2)}
          </pre>
        </div>
      </Card>

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Mapeo de Asignaciones</h3>
        <DataTable
          headers={['ID Asignación', 'Destino ID', 'Ruta ID', 'Destino Nombre', 'Distancia', 'Población']}
          rows={mapeo_asignaciones?.map((mapeo, index) => [
            mapeo.id_asignacion_unica || index,
            mapeo.id_destino_perteneciente || 'N/A',
            mapeo.id_ruta_en_destino || 'N/A',
            mapeo.destino_nombre || 'N/A',
            `${mapeo.distancia_km?.toFixed(1) || '0'} km`,
            mapeo.poblacion?.toLocaleString() || '0'
          ]) || []}
        />
      </Card>

      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Configuración de Insumos</h3>
        <DataTable
          headers={['ID', 'Nombre', 'Categoría', 'Peso (kg)']}
          rows={configuracion_insumos?.map((insumo, index) => [
            insumo.id_insumo ?? index,
            insumo.nombre || 'N/A',
            insumo.categoria || 'N/A',
            insumo.peso_kg?.toFixed(2) || '0'
          ]) || []}
        />
      </Card>
    </div>
  );

  const tabs = [
    { id: 'overview', label: 'Resumen General', content: renderOverview },
    { id: 'solutions', label: 'Top 3 Soluciones', content: renderTopSolutions },
    { id: 'distribution', label: 'Análisis de Carga', content: renderDistributionAnalysis },
    { id: 'map', label: 'Mapa de Resultados', content: renderMapView },
    { id: 'control', label: 'Panel de Control', content: renderControlPanel },
    { id: 'analysis', label: 'Análisis Completo', content: renderAnalysisReport },
    { id: 'video', label: 'Generar Video', content: renderVideoGeneration },
    { id: 'data', label: 'Datos Raw', content: renderRawData }
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