import { Card } from '../../common/Card';

const PerformanceAnalysis = ({ solutions, vehicleData }) => {
  const performanceMetrics = solutions.map((sol, index) => {
    const totalCapacity = sol.asignaciones.reduce((sum, asig) => {
      const vehicle = vehicleData.find(v => v.vehiculo_id == asig.vehiculo_id);
      return sum + (vehicle ? parseFloat(vehicle.capacidad_kg) : 0);
    }, 0);
    const utilization = totalCapacity > 0 ? (sol.resumen.peso_total_entregado / totalCapacity) * 100 : 0;
    const fuelEfficiency = sol.resumen.combustible_total > 0 ? (sol.resumen.peso_total_entregado / sol.resumen.combustible_total) : 0;
    return {
      solution: `Solución #${index + 1}`,
      fitness: sol.fitness.toFixed(2),
      utilization: utilization.toFixed(2) + '%',
      fuelEfficiency: fuelEfficiency.toFixed(2) + ' kg/L',
    };
  });
  
  return (
    <Card>
      <h2 className="text-xl font-semibold text-blue-400 mb-3">Análisis de Rendimiento Comparativo</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-700/50">
            <tr>
              <th className="p-2">Solución</th>
              <th className="p-2">Fitness</th>
              <th className="p-2">Utilización de Capacidad Total</th>
              <th className="p-2">Eficiencia de Combustible</th>
            </tr>
          </thead>
          <tbody>
            {performanceMetrics.map((metric, index) => (
              <tr key={index} className="border-b border-gray-700">
                <td className="p-2 font-medium">{metric.solution}</td>
                <td className="p-2 font-bold text-green-400">{metric.fitness}</td>
                <td className="p-2">{metric.utilization}</td>
                <td className="p-2">{metric.fuelEfficiency}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

export default PerformanceAnalysis;