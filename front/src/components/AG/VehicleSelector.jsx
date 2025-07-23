import { useState } from 'react';
import { Button, Input, Select } from '../UI';

const VehicleSelector = ({ vehicles, customVehicles, setCustomVehicles, selectedVehicles, setSelectedVehicles }) => {
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [newVehicle, setNewVehicle] = useState({ modelo: '', tipo: '', capacidad_kg: '' });

  const allAvailableVehicles = [...vehicles, ...customVehicles];
  
  // Vehículos que ya han sido añadidos a la flota
  const activeVehicleIds = Object.keys(selectedVehicles);

  // Vehículos disponibles para añadir (los que no están ya en la flota)
  const availableToAdd = allAvailableVehicles.filter(v => !activeVehicleIds.includes(v.vehiculo_id));

  const handleAddVehicleToFleet = (vehicleId) => {
    if (!vehicleId || selectedVehicles[vehicleId] !== undefined) return;
    // La cantidad por defecto al añadir es 1
    setSelectedVehicles(prev => ({ ...prev, [vehicleId]: 1 }));
  };
  
  const handleRemoveVehicleFromFleet = (vehicleId) => {
    const newSelected = { ...selectedVehicles };
    delete newSelected[vehicleId];
    setSelectedVehicles(newSelected);
  };

  const handleQuantityChange = (id, quantity) => {
    const numQuantity = parseInt(quantity, 10);
    // Si la cantidad no es un número o es menor que 1, se establece en 1.
    if (isNaN(numQuantity) || numQuantity < 1) {
      setSelectedVehicles(prev => ({ ...prev, [id]: 1 }));
    } else {
      setSelectedVehicles(prev => ({ ...prev, [id]: numQuantity }));
    }
  };

  const handleAddCustomVehicle = () => {
    if (newVehicle.modelo && newVehicle.tipo && newVehicle.capacidad_kg) {
      const newId = `custom-${Date.now()}`;
      const vehicleToAdd = { ...newVehicle, vehiculo_id: newId, capacidad_kg: parseInt(newVehicle.capacidad_kg) };
      setCustomVehicles(prev => [...prev, vehicleToAdd]);
      // Añade el nuevo vehículo directamente a la flota con cantidad 1
      setSelectedVehicles(prev => ({ ...prev, [newId]: 1 }));
      setNewVehicle({ modelo: '', tipo: '', capacidad_kg: '' });
      setShowCustomForm(false);
    } else {
      alert('Por favor, completa todos los campos del nuevo vehículo.');
    }
  };

  return (
    <div className="space-y-6">
      {/* --- SELECCIÓN PARA AÑADIR VEHÍCULO --- */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">
          Añadir vehículo a la flota:
        </label>
        <div className="flex gap-2">
            <Select
                value=""
                onChange={(e) => handleAddVehicleToFleet(e.target.value)}
                options={[
                    { value: '', label: 'Selecciona un modelo...' },
                    ...availableToAdd.map(v => ({ value: v.vehiculo_id, label: v.modelo }))
                ]}
                className="flex-grow"
            />
            <Button onClick={() => setShowCustomForm(true)} variant="secondary" className="flex-shrink-0">
                + Nuevo
            </Button>
        </div>
      </div>

      {/* --- FORMULARIO PARA VEHÍCULO PERSONALIZADO (OCULTO) --- */}
      {showCustomForm && (
        <div className="p-4 bg-gray-700 rounded-md space-y-3">
          <h4 className="font-semibold text-lg text-yellow-400">Crear Nuevo Vehículo</h4>
          <Input placeholder="Modelo (e.g., Nissan NP300)" value={newVehicle.modelo} onChange={e => setNewVehicle(p => ({...p, modelo: e.target.value}))} />
          <Input placeholder="Tipo (e.g., camioneta pickup)" value={newVehicle.tipo} onChange={e => setNewVehicle(p => ({...p, tipo: e.target.value}))} />
          <Input type="number" placeholder="Capacidad (kg)" value={newVehicle.capacidad_kg} onChange={e => setNewVehicle(p => ({...p, capacidad_kg: e.target.value}))} />
          <div className="flex gap-2">
            <Button onClick={handleAddCustomVehicle}>Guardar y Añadir</Button>
            <Button onClick={() => setShowCustomForm(false)} variant="secondary">Cancelar</Button>
          </div>
        </div>
      )}
      
      {/* --- FLOTA ACTIVA --- */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-200 border-b border-gray-600 pb-2">
          Flota Activa
        </h3>
        {activeVehicleIds.length === 0 ? (
          <p className="text-gray-400 text-center py-4">No has añadido ningún vehículo a la flota.</p>
        ) : (
          activeVehicleIds.map(id => {
            // FIX: Use == to compare string from ID with number from vehicle data
            const vehicle = allAvailableVehicles.find(v => v.vehiculo_id == id);
            if (!vehicle) return null; // Previene errores si el vehículo no se encuentra

            return (
              <div key={id} className="flex items-center gap-4 p-3 bg-gray-700 rounded-md">
                <div className="flex-grow">
                    <p className="font-semibold text-gray-200">{vehicle.modelo}</p>
                    <p className="text-sm text-gray-400 capitalize">{vehicle.tipo} - {vehicle.capacidad_kg}kg</p>
                </div>
                <Input
                  type="number"
                  min="1"
                  placeholder="Cant."
                  className="w-20"
                  value={selectedVehicles[id]}
                  onChange={(e) => handleQuantityChange(id, e.target.value)}
                />
                <Button onClick={() => handleRemoveVehicleFromFleet(id)} variant="danger" size="sm" className="w-8 h-8 p-0">
                  ✕
                </Button>
              </div>
            )
          })
        )}
      </div>
    </div>
  );
};

export default VehicleSelector;