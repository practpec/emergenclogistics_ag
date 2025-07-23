import { useState } from 'react';
import { Button, Input, Select } from '../UI';

const VehicleSelector = ({ vehicles, customVehicles, setCustomVehicles, selectedVehicles, setSelectedVehicles }) => {
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [newVehicle, setNewVehicle] = useState({ 
    modelo: '', 
    tipo: '', 
    velocidad_kmh: '',
    consumo_litros_km: '',
    maximo_peso_ton: '',
    capacidad_kg: '' 
  });

  const allAvailableVehicles = [...vehicles, ...customVehicles];
  const activeVehicleIds = Object.keys(selectedVehicles);
  const availableToAdd = allAvailableVehicles.filter(v => !activeVehicleIds.includes(v.vehiculo_id.toString()));

  const handleAddVehicleToFleet = (vehicleId) => {
    if (!vehicleId || selectedVehicles[vehicleId] !== undefined) return;
    setSelectedVehicles(prev => ({ ...prev, [vehicleId]: 1 }));
  };
  
  const handleRemoveVehicleFromFleet = (vehicleId) => {
    const newSelected = { ...selectedVehicles };
    delete newSelected[vehicleId];
    setSelectedVehicles(newSelected);
  };

  const handleQuantityChange = (id, quantity) => {
    const numQuantity = parseInt(quantity, 10);
    if (isNaN(numQuantity) || numQuantity < 1) {
      setSelectedVehicles(prev => ({ ...prev, [id]: 1 }));
    } else {
      setSelectedVehicles(prev => ({ ...prev, [id]: numQuantity }));
    }
  };

  const validateNumericInput = (value, fieldName) => {
    const num = parseFloat(value);
    if (isNaN(num) || num <= 0) {
      alert(`${fieldName} debe ser un número válido mayor a 0`);
      return false;
    }
    return true;
  };

  const handleAddCustomVehicle = () => {
    if (!newVehicle.modelo || !newVehicle.tipo) {
      alert('Modelo y tipo son obligatorios.');
      return;
    }

    // Validar campos numéricos
    const numericFields = {
      velocidad_kmh: 'Velocidad',
      consumo_litros_km: 'Consumo',
      maximo_peso_ton: 'Peso máximo',
      capacidad_kg: 'Capacidad'
    };

    for (const [field, label] of Object.entries(numericFields)) {
      if (newVehicle[field] && !validateNumericInput(newVehicle[field], label)) {
        return;
      }
    }

    const newId = `custom-${Date.now()}`;
    const vehicleToAdd = { 
      ...newVehicle, 
      vehiculo_id: newId,
      // Convertir a números con valores por defecto
      velocidad_kmh: parseFloat(newVehicle.velocidad_kmh) || 60,
      consumo_litros_km: parseFloat(newVehicle.consumo_litros_km) || 0.1,
      maximo_peso_ton: parseFloat(newVehicle.maximo_peso_ton) || 1,
      capacidad_kg: parseFloat(newVehicle.capacidad_kg) || parseFloat(newVehicle.maximo_peso_ton) * 1000 || 1000
    };

    setCustomVehicles(prev => [...prev, vehicleToAdd]);
    setSelectedVehicles(prev => ({ ...prev, [newId]: 1 }));
    setNewVehicle({ 
      modelo: '', 
      tipo: '', 
      velocidad_kmh: '',
      consumo_litros_km: '',
      maximo_peso_ton: '',
      capacidad_kg: '' 
    });
    setShowCustomForm(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-1">Añadir vehículo a la flota:</label>
        <div className="flex gap-2">
          <Select
            value=""
            onChange={(e) => handleAddVehicleToFleet(e.target.value)}
            options={[{ value: '', label: 'Selecciona un modelo...' }, ...availableToAdd.map(v => ({ value: v.vehiculo_id, label: v.modelo }))]}
            className="flex-grow"
          />
          <Button onClick={() => setShowCustomForm(true)} variant="secondary" className="flex-shrink-0">+ Nuevo</Button>
        </div>
      </div>

      {showCustomForm && (
        <div className="p-4 bg-gray-700 rounded-md space-y-3">
          <h4 className="font-semibold text-lg text-yellow-400">Crear Nuevo Vehículo</h4>
          <Input 
            placeholder="Modelo (e.g., Nissan NP300)" 
            value={newVehicle.modelo} 
            onChange={e => setNewVehicle(p => ({...p, modelo: e.target.value}))} 
          />
          <Input 
            placeholder="Tipo (e.g., camioneta pickup)" 
            value={newVehicle.tipo} 
            onChange={e => setNewVehicle(p => ({...p, tipo: e.target.value}))} 
          />
          <div className="grid grid-cols-2 gap-2">
            <Input 
              type="number" 
              step="0.1"
              placeholder="Velocidad (km/h)" 
              value={newVehicle.velocidad_kmh} 
              onChange={e => setNewVehicle(p => ({...p, velocidad_kmh: e.target.value}))} 
            />
            <Input 
              type="number" 
              step="0.01"
              placeholder="Consumo (L/km)" 
              value={newVehicle.consumo_litros_km} 
              onChange={e => setNewVehicle(p => ({...p, consumo_litros_km: e.target.value}))} 
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <Input 
              type="number" 
              step="0.1"
              placeholder="Peso máximo (ton)" 
              value={newVehicle.maximo_peso_ton} 
              onChange={e => setNewVehicle(p => ({...p, maximo_peso_ton: e.target.value}))} 
            />
            <Input 
              type="number" 
              placeholder="Capacidad (kg)" 
              value={newVehicle.capacidad_kg} 
              onChange={e => setNewVehicle(p => ({...p, capacidad_kg: e.target.value}))} 
            />
          </div>
          <div className="text-xs text-gray-400">
            <p>* Si no especificas capacidad, se calculará automáticamente desde peso máximo</p>
            <p>* Valores por defecto: Velocidad 60 km/h, Consumo 0.1 L/km</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleAddCustomVehicle}>Guardar y Añadir</Button>
            <Button onClick={() => setShowCustomForm(false)} variant="secondary">Cancelar</Button>
          </div>
        </div>
      )}
      
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-gray-200 border-b border-gray-600 pb-2">Flota Activa</h3>
        {activeVehicleIds.length === 0 ? (
          <p className="text-gray-400 text-center py-4">No has añadido ningún vehículo a la flota.</p>
        ) : (
          activeVehicleIds.map(id => {
            const vehicle = allAvailableVehicles.find(v => v.vehiculo_id == id);
            if (!vehicle) return null;
            
            // Asegurar valores numéricos para la visualización
            const capacidad = parseFloat(vehicle.capacidad_kg) || parseFloat(vehicle.maximo_peso_ton) * 1000 || 1000;
            
            return (
              <div key={id} className="flex items-center gap-4 p-3 bg-gray-700 rounded-md">
                <div className="flex-grow">
                  <p className="font-semibold text-gray-200">{vehicle.modelo}</p>
                  <p className="text-sm text-gray-400 capitalize">
                    {vehicle.tipo} - {capacidad.toFixed(0)}kg
                    {vehicle.velocidad_kmh && ` - ${parseFloat(vehicle.velocidad_kmh)}km/h`}
                  </p>
                </div>
                <Input 
                  type="number" 
                  min="1" 
                  placeholder="Cant." 
                  className="w-20" 
                  value={selectedVehicles[id]} 
                  onChange={(e) => handleQuantityChange(id, e.target.value)} 
                />
                <Button 
                  onClick={() => handleRemoveVehicleFromFleet(id)} 
                  variant="danger" 
                  size="sm" 
                  className="w-8 h-8 p-0"
                >
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