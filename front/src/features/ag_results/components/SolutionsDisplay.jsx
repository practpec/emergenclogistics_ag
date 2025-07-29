import { useState } from 'react';
import { Card } from '../../../components/common/Card';
import SolutionDetail from './SolutionDetail';
import clsx from 'clsx';

const SolutionsDisplay = ({ results, mapData, vehicleData, suppliesData }) => {
  const [activeTab, setActiveTab] = useState(0);
  const solutions = results.alternativas.slice(0, 3);

  const getTabClass = (index) => clsx(
    "px-4 py-2 font-semibold text-sm rounded-t-lg transition-colors",
    activeTab === index 
      ? "bg-gray-800 border-b-2 border-yellow-400 text-yellow-400"
      : "bg-gray-900 text-gray-400 hover:bg-gray-700"
  );

  return (
    <Card>
      <h2 className="text-xl font-bold text-yellow-400 mb-4 text-center">
        Análisis de las Mejores Soluciones Encontradas
      </h2>
      <div className="border-b border-gray-700">
        <nav className="-mb-px flex space-x-2">
          {solutions.map((sol, index) => (
            <button key={index} onClick={() => setActiveTab(index)} className={getTabClass(index)}>
              {index === 0 ? '🏆 Solución Óptima' : `🥈 Alternativa ${index + 1}`}
            </button>
          ))}
        </nav>
      </div>

      <div className="pt-4 bg-gray-800 rounded-b-lg p-4">
        {solutions.map((sol, index) => (
          <div key={index} className={activeTab === index ? 'block' : 'hidden'}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4 text-center text-xs bg-gray-900/50 p-2 rounded-lg">
                <div><span className="font-bold text-gray-300 block">Fitness</span> <span className="text-green-400">{sol.fitness.toFixed(4)}</span></div>
                <div><span className="font-bold text-gray-300 block">Peso Total</span> <span className="text-blue-400">{results.solucion_optima.metricas.peso_total} kg</span></div>
                <div><span className="font-bold text-gray-300 block">Combustible</span> <span className="text-red-400">{results.solucion_optima.metricas.combustible_total.toFixed(2)} L</span></div>
                <div><span className="font-bold text-gray-300 block">Vehículos</span> <span className="text-purple-400">{results.solucion_optima.metricas.vehiculos_utilizados}</span></div>
            </div>
            <SolutionDetail
              solution={sol}
              mapData={mapData}
              vehicleData={vehicleData}
              suppliesData={suppliesData}
            />
          </div>
        ))}
      </div>
    </Card>
  );
};

export default SolutionsDisplay;