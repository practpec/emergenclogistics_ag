import { useState } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';

const TopSolutionsAnalysis = ({ solutions, mapData, vehicleData }) => {
  const [selected, setSelected] = useState(0);

  // --- VALIDACIÓN CORREGIDA ---
  // Si no hay soluciones o la seleccionada no existe, no intentar renderizar nada.
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
    const vehicle = vehicleData.find(v => v.vehiculo_id == assignment.vehiculo_id) || {};
    let destinationName = `Ruta ID ${assignment.ruta_id}`;
    let distance = 'N/A';
    
    for (const destData of mapData.rutas_data) {
        const route = (destData.rutas || []).find(r => r.id == assignment.ruta_id);
        if (route) {
            destinationName = destData.destino.nombre.split(',')[0];
            distance = route.distancia.text;
            break;
        }
    }

    return {
      vehicleModel: vehicle.modelo || `ID ${assignment.vehiculo_id}`,
      destinationName,
      distance,
      ...assignment
    };
  };

  const detailedAssignments = currentSol.asignaciones.map(getAssignmentDetails);

  return (
    <Card>
      <div className="flex flex-col md:flex-row justify-between md:items-center mb-4 gap-4">
        <h2 className="text-xl font-semibold text-blue-400">Análisis de las Mejores Soluciones</h2>
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
              <th className="p-2">Destino</th>
              <th className="p-2">Distancia</th>
              <th className="p-2">Peso Carga (kg)</th>
              <th className="p-2">Combustible (L)</th>
              <th className="p-2">Tiempo (hrs)</th>
            </tr>
          </thead>
          <tbody>
            {detailedAssignments.map((asig, index) => (
              <tr key={index} className="border-b border-gray-700 hover:bg-gray-800">
                <td className="p-2 font-medium">{asig.vehicleModel}</td>
                <td className="p-2">{asig.destinationName}</td>
                <td className="p-2">{asig.distance}</td>
                <td className="p-2">{asig.peso_total_kg.toFixed(2)}</td>
                <td className="p-2">{asig.combustible_litros.toFixed(2)}</td>
                <td className="p-2">{asig.tiempo_horas.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

export default TopSolutionsAnalysis;