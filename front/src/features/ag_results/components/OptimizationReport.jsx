import { Card } from '../../../components/common/Card';
import ScenarioCoverageCard from './ScenarioCoverageCard';

const EfficiencyCard = ({ data }) => (
  <Card className="h-full">
    <h3 className="font-bold text-blue-400 mb-3 text-base text-center">Métricas de Eficiencia</h3>
    <div className="space-y-2">
      <div className="flex justify-between p-2 bg-gray-900/50 rounded-md">
        <span className="text-gray-400">Combustible Promedio</span>
        <span className="font-semibold text-gray-200">{data.combustible_promedio.toFixed(2)} L/viaje</span>
      </div>
      <div className="flex justify-between p-2 bg-gray-900/50 rounded-md">
        <span className="text-gray-400">Distancia Promedio</span>
        <span className="font-semibold text-gray-200">{data.distancia_promedio.toFixed(2)} km/viaje</span>
      </div>
      <div className="flex justify-between p-2 bg-gray-900/50 rounded-md">
        <span className="text-gray-400">Peso Promedio</span>
        <span className="font-semibold text-gray-200">{data.peso_promedio.toFixed(2)} kg/viaje</span>
      </div>
    </div>
  </Card>
);

const LoadDistributionCard = ({ data }) => (
    <Card className="h-full">
        <h3 className="font-bold text-blue-400 mb-3 text-base text-center">Distribución de Carga</h3>
        <div className="space-y-2 text-sm">
            <div className="flex justify-between p-1.5 bg-gray-900/50 rounded-md">
                <span className="text-gray-400">Capacidad Total</span>
                <span className="font-semibold text-gray-200">{data.capacidad_total_disponible.toLocaleString()} kg</span>
            </div>
            <div className="flex justify-between p-1.5 bg-gray-900/50 rounded-md">
                <span className="text-gray-400">Peso Transportado</span>
                <span className="font-semibold text-gray-200">{data.peso_total_transportado.toLocaleString()} kg</span>
            </div>
             <div className="flex justify-between p-1.5 bg-gray-900/50 rounded-md">
                <span className="text-gray-400">Utilización Total</span>
                <span className="font-bold text-green-400">{data.utilizacion_total.toFixed(1)}%</span>
            </div>
            <hr className="border-gray-700"/>
            <div className="flex justify-between p-1.5 bg-gray-900/50 rounded-md">
                <span className="text-gray-400">Vehículos Óptimos</span>
                <span className="font-semibold text-gray-200">{data.vehiculos_optimos}</span>
            </div>
             <div className="flex justify-between p-1.5 bg-gray-900/50 rounded-md">
                <span className="text-gray-400">Vehículos Subutilizados</span>
                <span className="font-semibold text-gray-200">{data.vehiculos_subutilizados}</span>
            </div>
        </div>
    </Card>
);

const FitnessChart = ({ evolutionData }) => {
    const { datos } = evolutionData;
    const minFitness = Math.min(...datos);
    const maxFitness = Math.max(...datos);
    const avgFitness = datos.reduce((a, b) => a + b, 0) / datos.length;
    const midFitness = (minFitness + maxFitness) / 2;

    const normalizeY = (value) => {
      const range = maxFitness - minFitness;
      if (range === 0) return 75;
      return 150 - ((value - minFitness) / range) * 140 - 5;
    };

    const pathData = datos.map((p, i) => 
        `${i === 0 ? 'M' : 'L'} ${(i / (datos.length - 1)) * 450 + 50} ${normalizeY(p)}`
    ).join(' ');

    return (
        <Card className="h-full flex flex-col">
            <h3 className="font-bold text-blue-400 mb-2 text-base text-center">Evolución del Fitness por Generación</h3>
            <div className="flex-grow bg-gray-900/50 p-2 rounded-md overflow-hidden relative">
                <svg width="100%" height="100%" viewBox="0 0 500 160" preserveAspectRatio="none">
                    <line x1="50" y1="10" x2="50" y2="150" stroke="#4b5563" strokeWidth="1"/>
                    <line x1="45" y1="150" x2="500" y2="150" stroke="#4b5563" strokeWidth="1"/>
                    <text x="45" y={normalizeY(maxFitness)} dy="3" textAnchor="end" fill="#a0aec0" fontSize="10">{maxFitness.toFixed(3)}</text>
                    <text x="45" y={normalizeY(midFitness)} dy="3" textAnchor="end" fill="#a0aec0" fontSize="10">{midFitness.toFixed(3)}</text>
                    <text x="45" y={normalizeY(minFitness)} dy="3" textAnchor="end" fill="#a0aec0" fontSize="10">{minFitness.toFixed(3)}</text>
                    <line x1="50" y1={normalizeY(maxFitness)} x2="500" y2={normalizeY(maxFitness)} stroke="#4b5563" strokeDasharray="2" strokeWidth="0.5"/>
                    <line x1="50" y1={normalizeY(midFitness)} x2="500" y2={normalizeY(midFitness)} stroke="#4b5563" strokeDasharray="2" strokeWidth="0.5"/>
                    <line x1="50" y1={normalizeY(minFitness)} x2="500" y2={normalizeY(minFitness)} stroke="#4b5563" strokeDasharray="2" strokeWidth="0.5"/>
                    <path d={pathData} fill="none" stroke="#facc15" strokeWidth="2.5" />
                </svg>
            </div>
            {/* --- DETALLES RESTAURADOS --- */}
            <div className="grid grid-cols-3 gap-2 text-center text-xs mt-3">
                <div className="bg-gray-700 p-2 rounded">
                    <span className="text-gray-400 block">Peor Fitness</span>
                    <span className="font-bold text-red-400 text-sm">{minFitness.toFixed(4)}</span>
                </div>
                <div className="bg-gray-700 p-2 rounded">
                    <span className="text-gray-400 block">Fitness Promedio</span>
                    <span className="font-bold text-blue-400 text-sm">{avgFitness.toFixed(4)}</span>
                </div>
                <div className="bg-gray-700 p-2 rounded">
                    <span className="text-gray-400 block">Mejor Fitness</span>
                    <span className="font-bold text-green-400 text-sm">{maxFitness.toFixed(4)}</span>
                </div>
            </div>
        </Card>
    );
};

const OptimizationReport = ({ reports, visualizations }) => {
  return (
    <Card>
      <h2 className="text-xl font-bold text-yellow-400 mb-4 text-center">Reportes de Rendimiento y Optimización</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ScenarioCoverageCard data={reports.escenario} />
        <EfficiencyCard data={reports.eficiencia} />
        <LoadDistributionCard data={visualizations.distribucion_carga} />
        <FitnessChart evolutionData={visualizations.evolucion_fitness} />
      </div>
    </Card>
  );
};

export default OptimizationReport;