import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import useAppStore from '../store/useAppStore';
import apiService, { handleApiError } from '../services/apiService';

export const useMap = () => {
  const {
    mapData,
    isLoadingMap,
    selectedEstado,
    municipios,
    setMapData,
    setLoadingMap,
    setSelectedEstado,
    setMunicipios,
    setSelectedMunicipio,
    clearMapData,
  } = useAppStore();

  const [estados, setEstados] = useState([]);
  const [highlightedRoute, setHighlightedRoute] = useState(null);
  const [municipioInfo, setMunicipioInfo] = useState(null);
  const [maxNodos, setMaxNodos] = useState(15);
  const [routeColors] = useState([
    '#e74c3c', '#3498db', '#f39c12', '#27ae60', '#9b59b6',
    '#e67e22', '#1abc9c', '#34495e', '#f1c40f', '#95a5a6',
  ]);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm({
    defaultValues: {
      estado: '',
      municipio: '',
      n_nodos: 5,
    },
  });

  const watchedEstado = watch('estado');
  const watchedMunicipio = watch('municipio');
  const watchedNNodos = watch('n_nodos');

  useEffect(() => {
    const loadEstados = async () => {
      try {
        const response = await apiService.getEstados();
        if (response.success) {
          const estadosSimples = response.data.map(estado => estado.nombre);
          setEstados(estadosSimples);
        }
      } catch (error) {
        const apiError = handleApiError(error);
        toast.error(apiError.message);
      }
    };
    loadEstados();
  }, []);

  useEffect(() => {
    const loadMunicipios = async (estado) => {
      try {
        const response = await apiService.getMunicipios(estado);
        if (response.success) {
          setMunicipios(response.data);
        }
      } catch (error) {
        const apiError = handleApiError(error);
        toast.error(apiError.message);
      }
    };

    if (watchedEstado && watchedEstado !== selectedEstado) {
      setSelectedEstado(watchedEstado);
      setSelectedMunicipio('');
      setValue('municipio', '');
      setMunicipioInfo(null);
      setMaxNodos(15);
      setValue('n_nodos', 5);
      if (watchedEstado) {
        loadMunicipios(watchedEstado);
      }
    }
  }, [watchedEstado, selectedEstado, setSelectedEstado, setSelectedMunicipio, setValue, setMunicipios]);

  useEffect(() => {
    const loadMunicipioInfo = async (estado, claveMunicipio) => {
      try {
        const response = await apiService.getNodoInicialMunicipio(estado, claveMunicipio);
        if (response.success && response.data.municipio_info) {
          const info = response.data.municipio_info;
          setMunicipioInfo(info);
          
          const localidadesDisponibles = info.total_localidades || 15;
          const maxPermitido = Math.min(localidadesDisponibles - 1, 15);
          setMaxNodos(Math.max(1, maxPermitido));
          
          const currentNNodos = parseInt(watchedNNodos);
          if (currentNNodos > maxPermitido) {
            setValue('n_nodos', Math.min(5, maxPermitido));
          }
          
          toast.info(`${info.nombre_municipio}: ${localidadesDisponibles} localidades disponibles`);
        }
      } catch (error) {
        setMaxNodos(15);
      }
    };

    if (watchedMunicipio) {
      setSelectedMunicipio(watchedMunicipio);
      loadMunicipioInfo(watchedEstado, watchedMunicipio);
    }
  }, [watchedMunicipio, watchedEstado, setSelectedMunicipio, setValue, watchedNNodos]);
  
  useEffect(() => {
    if (watchedNNodos && maxNodos > 0) {
      const nNodos = parseInt(watchedNNodos, 10);
      if (nNodos > maxNodos) {
        setValue('n_nodos', maxNodos);
        toast.warning(`Máximo ${maxNodos} destinos para este municipio.`);
      }
    }
  }, [watchedNNodos, maxNodos, setValue]);

  const onSubmit = async (data) => {
    if (!data.estado || !data.municipio) {
      toast.error('Por favor selecciona un estado y un municipio.');
      return;
    }
    
    setLoadingMap(true);
    clearMapData();
    setHighlightedRoute(null);
    
    try {
      const response = await apiService.generateCompleteRoutes(
        data.estado,
        parseInt(data.n_nodos, 10),
        data.municipio
      );
      
      if (response.success) {
        setMapData(response.data);
        toast.success('Mapa generado exitosamente.');
      }
    } catch (error) {
      const apiError = handleApiError(error);
      toast.error(apiError.message);
    } finally {
      setLoadingMap(false);
    }
  };

  const getRouteColor = (index) => routeColors[index % routeColors.length];

  return {
    mapData,
    isLoadingMap,
    estados,
    municipios,
    maxNodos,
    highlightedRoute,
    register,
    handleSubmit,
    errors,
    watchedEstado,
    watchedMunicipio,
    onSubmit,
    getRouteColor,
    handleRouteHighlight: setHighlightedRoute,
  };
};