import { useState, useMemo } from 'react';
import { Card } from '../../../components/common/Card';
import SolutionDetail from './SolutionDetail';
import clsx from 'clsx';

// --- Componente Interno para la Barra de Progreso ---
const ProgressBar = ({ value, max, unit }) => {
    const percentage = max > 0 ? (value / max) * 100 : 0;
    return (
        <div>
            <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>{value.toLocaleString()} {unit}</span>
                <span>{max.toLocaleString()} {unit}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2.5">
                <div 
                    className="bg-green-600 h-2.5 rounded-full" 
                    style={{ width: `${percentage}%` }}
                ></div>
            </div>
        </div>
    );
};


const SolutionsDisplay = ({ results, mapData, vehicleData, suppliesData }) => {
  const [activeTab, setActiveTab] = useState(0);
  const solutions = results.alternativas.slice(0, 3);

  // --- Memoización de los Cálculos para Eficiencia ---
  const calculatedMetrics = useMemo(() => {
    return solutions.map(sol => {
      let distanciaTotal = 0;
      let tiempoMaximo = 0;
      let capacidadTotal = 0;

      sol.asignaciones.forEach(a => {
        distanciaTotal += a.distancia_km;
        
        const vehiculo = vehicleData.find(v => v.id === a.vehiculo_id);
        if (vehiculo) {
          const tiempoViaje = a.distancia_km / vehiculo.velocidad_kmh;
          if (tiempoViaje > tiempoMaximo) {
            tiempoMaximo = tiempoViaje;
          }
          capacidadTotal += vehiculo.maximo_peso_ton * 1000; // Convertir a kg
        }
      });

      return {
        distanciaTotal,
        tiempoMaximo,
        capacidadTotal
      };
    });
  }, [solutions, vehicleData]);


  const getTabClass = (index) => clsx(
    "px-4 py-2 font-semibold text-sm rounded-t-lg transition-colors cursor-pointer focus:outline-none",
    activeTab === index 
      ? "bg-gray-800 border-b-2 border-yellow-400 text-yellow-400"
      : "bg-gray-900/50 text-gray-400 hover:bg-gray-700"
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
          activeTab === index && (
            <div key={index}>
              {/* --- SECCIÓN DE RESUMEN ENRIQUECIDA --- */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-center text-xs bg-gray-900/50 p-3 rounded-lg">
                  <div>
                      <span className="font-bold text-gray-300 block mb-1">Fitness</span> 
                      <span className="text-green-400 text-lg font-semibold">{sol.fitness.toFixed(4)}</span>
                  </div>
                  <div>
                      <span className="font-bold text-gray-300 block mb-1">Distancia Total</span> 
                      <span className="text-blue-400 text-lg font-semibold">{calculatedMetrics[index].distanciaTotal.toFixed(1)} km</span>
                  </div>
                   <div>
                      <span className="font-bold text-gray-300 block mb-1">Tiempo de Operación</span> 
                      <span className="text-red-400 text-lg font-semibold">{calculatedMetrics[index].tiempoMaximo.toFixed(2)} hrs</span>
                  </div>
                  <div>
                      <span className="font-bold text-gray-300 block mb-1">Carga vs. Capacidad</span>
                      <ProgressBar 
                        value={sol.resumen.peso} 
                        max={calculatedMetrics[index].capacidadTotal} 
                        unit="kg" 
                      />
                  </div>
              </div>
              <SolutionDetail
                solution={sol}
                mapData={mapData}
                vehicleData={vehicleData}
                suppliesData={suppliesData}
              />
            </div>
          )
        ))}
      </div>
    </Card>
  );
};

export default SolutionsDisplay;