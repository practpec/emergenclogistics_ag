import { useState, useEffect } from 'react';
import apiService from '../../../services/apiService';
import toast from 'react-hot-toast';

export const useAG = () => {
  const [vehicles, setVehicles] = useState([]);
  const [disasters, setDisasters] = useState([]);
  // const [supplies, setSupplies] = useState([]); // Descomentar si usas insumos
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Cargar todos los datos en paralelo para mayor eficiencia
        const [vehiclesRes, disastersRes] = await Promise.all([
          apiService.getVehicles(),
          apiService.getDisasters(),
          // apiService.getSupplies() // Descomentar si usas insumos
        ]);

        if (vehiclesRes.success) setVehicles(vehiclesRes.data);
        else toast.error('No se pudieron cargar los vehículos.');

        if (disastersRes.success) setDisasters(disastersRes.data);
        else toast.error('No se pudieron cargar los tipos de desastre.');

        // if (suppliesRes.success) setSupplies(suppliesRes.data);

      } catch (error) {
        toast.error(`Error al cargar datos iniciales: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, []);

  return {
    vehicles,
    disasters,
    // supplies,
    isLoading,
  };
};