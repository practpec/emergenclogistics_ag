import { useState } from 'react';
import { Card, Button, Badge } from '../UI';
import { DataTable } from './ChartComponents';

const TopSolutionsAnalysis = ({ mejoresSoluciones }) => {
  const [selectedIndividual, setSelectedIndividual] = useState(0);

  if (!mejoresSoluciones || mejoresSoluciones.length === 0) {
    return (
      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Top 3 Soluciones</h3>
        <div className="text-center text-gray-400 py-8">
          <p>No hay soluciones disponibles para mostrar</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Resumen comparativo */}
      <Card>
        <h3 className="text-xl font-semibold text-yellow-400 mb-4">Comparativo Top 3 Soluciones</h3>
        <DataTable
          headers={['Posición', 'Fitness', 'Peso Total', 'Combustible', 'Localidades', 'Eficiencia']}
          rows={mejoresSoluciones.slice(0, 3).map((sol, index) => [
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

      {/* Selector de solución individual */}
      <div className="flex space-x-2 mb-4">
        {mejoresSoluciones.slice(0, 3).map((_, index) => (
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

      {/* Análisis detallado de la solución seleccionada */}
      {mejoresSoluciones[selectedIndividual] && (
        <div className="space-y-4">
          <Card>
            <h3 className="text-xl font-semibold text-yellow-400 mb-4">
              Solución #{selectedIndividual + 1} - Fitness: {mejoresSoluciones[selectedIndividual].fitness?.toFixed(2) || '0'}
            </h3>
            
            <DataTable
              headers={['Vehículo', 'Destino', 'Población', 'Distancia', 'Peso Carga', 'Utilización', 'Combustible']}
              rows={mejoresSoluciones[selectedIndividual].vehiculos?.map((vehiculo, index) => [
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
              {mejoresSoluciones[selectedIndividual].vehiculos?.map((vehiculo, vIndex) => (
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

          {/* Métricas específicas de esta solución */}
          <Card>
            <h4 className="text-lg font-semibold text-blue-400 mb-4">Métricas de Rendimiento</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="bg-gray-700 p-3 rounded text-center">
                <p className="text-sm text-gray-400">Eficiencia Total</p>
                <p className="text-lg font-bold text-green-400">
                  {((mejoresSoluciones[selectedIndividual].fitness || 0) / 1000 * 100).toFixed(1)}%
                </p>
              </div>
              <div className="bg-gray-700 p-3 rounded text-center">
                <p className="text-sm text-gray-400">Kg por Vehículo</p>
                <p className="text-lg font-bold text-yellow-400">
                  {((mejoresSoluciones[selectedIndividual].resumen?.peso_total || 0) / (mejoresSoluciones[selectedIndividual].vehiculos?.length || 1)).toFixed(1)}
                </p>
              </div>
              <div className="bg-gray-700 p-3 rounded text-center">
                <p className="text-sm text-gray-400">Población por Kg</p>
                <p className="text-lg font-bold text-purple-400">
                  {((mejoresSoluciones[selectedIndividual].vehiculos?.reduce((sum, v) => sum + (v.destino_poblacion || 0), 0) || 0) / (mejoresSoluciones[selectedIndividual].resumen?.peso_total || 1)).toFixed(0)}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default TopSolutionsAnalysis;