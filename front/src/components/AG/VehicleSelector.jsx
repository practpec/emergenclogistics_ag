import { Card } from '../common/Card.jsx';
import { Input } from '../common/Input.jsx';

const VehicleSelector = ({ vehicles, selectedVehicles, setSelectedVehicles }) => {
  const handleQuantityChange = (id, quantity) => {
    const numQuantity = Math.max(0, parseInt(quantity, 10) || 0);
    setSelectedVehicles(prev => ({ ...prev, [id]: numQuantity }));
  };

  return (
    <Card className="h-full flex flex-col">
      <h2 className="text-xl font-bold text-blue-400 border-b border-gray-600 pb-2 mb-3">
        1. Flota de Vehículos
      </h2>
      <div className="flex-grow overflow-y-auto pr-2 space-y-2">
        {vehicles.map(vehicle => (
            <div key={vehicle.vehiculo_id} className="bg-gray-700/50 p-2.5 rounded-lg border border-gray-600">
                <div className="flex justify-between items-center">
                    <div>
                        <p className="font-semibold text-base text-gray-100">{vehicle.modelo}</p>
                        <p className="text-xs text-yellow-400 capitalize">{vehicle.tipo}</p>
                    </div>
                    <Input
                        type="number"
                        min="0"
                        className="w-16 text-center text-base"
                        placeholder="0"
                        value={selectedVehicles[vehicle.vehiculo_id] || ''}
                        onChange={(e) => handleQuantityChange(vehicle.vehiculo_id, e.target.value)}
                    />
                </div>
                <div className="mt-2 grid grid-cols-3 gap-x-2 text-xs border-t border-gray-600 pt-1.5">
                    <div className="text-gray-300 text-center">
                        <span className="text-gray-500 block text-[10px]">CAPACIDAD</span>
                        {parseFloat(vehicle.capacidad_kg).toLocaleString()} kg
                    </div>
                    <div className="text-gray-300 text-center">
                        <span className="text-gray-500 block text-[10px]">VELOCIDAD</span>
                        {vehicle.velocidad_kmh} km/h
                    </div>
                    <div className="text-gray-300 text-center">
                        <span className="text-gray-500 block text-[10px]">CONSUMO</span>
                        {vehicle.consumo_litros_km} L/km
                    </div>
                </div>
            </div>
        ))}
      </div>
    </Card>
  );
};

export default VehicleSelector;