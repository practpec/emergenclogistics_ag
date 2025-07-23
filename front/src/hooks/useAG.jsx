import { useState, useEffect } from 'react';
import apiService, { handleApiError } from '../services/apiService';
import toast from 'react-hot-toast';

export const useAG = () => {
  const [vehicles, setVehicles] = useState([]);
  const [disasters, setDisasters] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        const [vehiclesRes, disastersRes] = await Promise.all([
          apiService.getVehicles(),
          apiService.getDisasters(),
        ]);

        if (vehiclesRes.success) {
          setVehicles(vehiclesRes.data);
        }
        if (disastersRes.success) {
          setDisasters(disastersRes.data);
        }
      } catch (error) {
        const apiError = handleApiError(error);
        toast.error(apiError.message);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  return {
    vehicles,
    disasters,
    isLoading,
  };
};