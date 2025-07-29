import { useState } from 'react';
import clsx from 'clsx';

const AssignmentCard = ({ assignment, vehicle, destination, supplies, onHighlight, isHighlighted }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Calcular tiempo de viaje para esta asignación específica
  const travelTimeHours = vehicle ? (assignment.distancia_km / vehicle.velocidad_kmh) : 0;

  const detailedSupplies = assignment.insumos_cantidades.map(item => {
    const supplyInfo = supplies.find(s => s.id_insumo === item.id_insumo);
    return {
      ...item,
      nombre: supplyInfo?.nombre || 'Insumo Desconocido',
      peso_kg: supplyInfo?.peso_kg || 0,
      peso_total_item: (supplyInfo?.peso_kg || 0) * item.cantidad
    };
  });

  return (
    <div
      className={clsx(
        "bg-gray-900/70 border-l-4 rounded-r-md p-3 transition-all duration-300",
        isHighlighted ? "border-yellow-400 scale-105 shadow-lg" : "border-gray-600 hover:border-blue-500"
      )}
      onMouseEnter={() => onHighlight(true)}
      onMouseLeave={() => onHighlight(false)}
    >
      <div className="flex justify-between items-center">
        <div>
          <p className="font-bold text-gray-100">{vehicle?.modelo || 'Vehículo Desconocido'}</p>
          <p className="text-sm text-gray-400">
            Destino: <span className="font-semibold text-blue-300">{destination?.nombre.split(',')[0]}</span>
          </p>
        </div>
        <button onClick={() => setIsExpanded(!isExpanded)} className="text-xs text-yellow-400 hover:text-yellow-300">
          {isExpanded ? 'Ocultar Carga' : 'Ver Carga'} {isExpanded ? '▲' : '▼'}
        </button>
      </div>

      {/* --- DETALLES POR VIAJE AMPLIADOS --- */}
      <div className="grid grid-cols-4 gap-2 text-center text-xs mt-2 pt-2 border-t border-gray-700">
        <div><span className="text-gray-500 block">Distancia</span> {assignment.distancia_km.toFixed(2)} km</div>
        <div><span className="text-gray-500 block">Tiempo Viaje</span> {travelTimeHours.toFixed(2)} h</div>
        <div><span className="text-gray-500 block">Combustible</span> {assignment.combustible_usado.toFixed(2)} L</div>
        <div><span className="text-gray-500 block">Peso Total</span> {assignment.peso_total_kg} kg</div>
      </div>

      {isExpanded && (
        <div className="mt-3 pt-3 border-t border-gray-700">
          <h4 className="font-semibold text-sm text-gray-300 mb-2">Insumos Transportados:</h4>
          <ul className="space-y-1 text-xs text-gray-400 max-h-40 overflow-y-auto pr-2">
            {detailedSupplies.map(supply => (
              <li key={supply.id_insumo} className="flex justify-between p-1 bg-gray-800 rounded">
                <span>{supply.cantidad}x {supply.nombre}</span>
                <span className="font-medium text-gray-300">{supply.peso_total_item.toFixed(1)} kg</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AssignmentCard;