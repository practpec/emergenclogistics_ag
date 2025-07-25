import { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';

const TopSolutionsAnalysis = ({ solutions, mapData, vehicleData }) => {
  const [selected, setSelected] = useState(0);

  if (!solutions || solutions.length === 0 || !solutions[selected]) {
    return (
      <Card>
        <h2 className="text-xl font-semibold text-blue-400">Análisis de Soluciones</h2>
        <p className="text-gray-400 mt-4 text-center">No hay datos de soluciones para mostrar.</p>
      </Card>
    );
  }

  const currentSol = solutions[selected];

  const getAssignmentDetails = (assignment) => {
    const vehicle = vehicleData.find(v => v.id == assignment.vehiculo_id) || {};
    
    let destinationName = 'Desconocido';
    let routeName = 'N/A';
    let distance = '0 km';
    
    for (const destData of mapData.rutas_data) {
        const route = (destData.rutas || []).find(r => r.id == assignment.ruta_id);
        if (route) {
            destinationName = destData.destino.nombre.split(',')[0];
            routeName = route.tipo || 'Ruta';
            distance = route.distancia.text;
            break;
        }
    }
    
    const capacityKg = (vehicle.maximo_peso_ton || 0) * 1000;
    const utilization = capacityKg > 0 ? (assignment.peso_total_kg / capacityKg) * 100 : 0;

    return {
      vehicle,
      destinationName,
      routeName,
      distance,
      utilization,
      ...assignment
    };
  };

  const detailedAssignments = currentSol.asignaciones.map(getAssignmentDetails);

  return (
    <Card>
      <div className="flex flex-col md:flex-row justify-between md:items-center mb-4 gap-4">
        <h2 className="text-xl font-semibold text-blue-400">Tabla de Asignaciones por Vehículo</h2>
        <div className="flex gap-2">
          {solutions.map((_, index) => (
            <Button key={index} size="sm" variant={selected === index ? 'primary' : 'secondary'} onClick={() => setSelected(index)}>
              Solución #{index + 1}
            </Button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-700/50">
            <tr>
              <th className="p-2">Vehículo</th>
              <th className="p-2">Capacidad</th>
              <th className="p-2">Destino</th>
              <th className="p-2">Ruta</th>
              <th className="p-2">Distancia</th>
              <th className="p-2">Carga</th>
              <th className="p-2">Aprovechamiento</th>
            </tr>
          </thead>
          <tbody>
            {detailedAssignments.map((asig, index) => (
              <tr key={index} className="border-b border-gray-700 hover:bg-gray-800">
                <td className="p-2 font-medium">
                    <p>{asig.vehicle.modelo}</p>
                    <p className="text-xs text-gray-400 capitalize">{asig.vehicle.tipo}</p>
                </td>
                <td className="p-2">{((asig.vehicle.maximo_peso_ton || 0) * 1000).toLocaleString()} kg</td>
                <td className="p-2">{asig.destinationName}</td>
                <td className="p-2">{asig.routeName}</td>
                <td className="p-2">{asig.distance}</td>
                <td className="p-2">{asig.peso_total_kg.toFixed(2)} kg</td>
                <td className="p-2 font-bold text-yellow-300">{asig.utilization.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

export default TopSolutionsAnalysis;