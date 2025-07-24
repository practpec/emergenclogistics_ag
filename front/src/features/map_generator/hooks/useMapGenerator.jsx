import { useState, useEffect, useMemo, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import useAppStore from '../../../store/useAppStore';
import apiService from '../../../services/apiService';

export const useMapGenerator = () => {
  const { mapData, setMapData, isLoading, setLoading } = useAppStore();

  const [estados, setEstados] = useState([]);
  const [municipios, setMunicipios] = useState([]);
  const [maxNodos, setMaxNodos] = useState(15);
  const [highlightedRoute, setHighlightedRoute] = useState(null);

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm({
    defaultValues: { estado: '', municipio: '', n_nodos: 5 },
  });

  const watchedEstado = watch('estado');
  const watchedMunicipio = watch('municipio');

  useEffect(() => {
    const loadData = async () => {
      try {
        const estadosData = await apiService.getEstados();
        setEstados(estadosData);
      } catch (error) {
        toast.error("Error al cargar estados.");
      }
    };
    loadData();
  }, []);

  useEffect(() => {
    if (!watchedEstado) {
      setMunicipios([]);
      setValue('municipio', '');
      return;
    }
    const loadData = async () => {
      try {
        const municipiosData = await apiService.getMunicipios(watchedEstado);
        setMunicipios(municipiosData);
      } catch (error) {
        toast.error(`Error al cargar municipios de ${watchedEstado}.`);
      }
    };
    loadData();
  }, [watchedEstado, setValue]);

  useEffect(() => {
    if (!watchedMunicipio || !watchedEstado) {
      setMaxNodos(15);
      return;
    }
    const getLimit = async () => {
      setLoading(true);
      try {
        const response = await apiService.getMunicipioInfo(watchedEstado, watchedMunicipio);
        const info = response.data.municipio_info;
        const limit = info?.total_localidades ? info.total_localidades - 1 : 14;

        setMaxNodos(limit > 0 ? limit : 1);
        toast.success(`${info.nombre_municipio}: ${info.total_localidades} localidades. Máx. ${limit} destinos.`);

        if (parseInt(watch('n_nodos')) > limit) {
          setValue('n_nodos', limit);
        }
      } catch (error) {
        toast.error("No se pudo obtener el límite de localidades.");
        setMaxNodos(15);
      } finally {
        setLoading(false);
      }
    };
    getLimit();
  }, [watchedMunicipio, watchedEstado, setValue, setLoading, watch]);

  const onSubmit = async (data) => {
    setLoading(true);
    setMapData(null);
    setHighlightedRoute(null);
    try {
      // La respuesta de la API ya viene con la estructura { success, data, message }
      const response = await apiService.generateCompleteRoutes(data.estado, data.n_nodos, data.municipio);
      if (response.success) {
        // Guardamos el contenido de la clave "data" que contiene toda la información del mapa
        setMapData(response.data);
        toast.success(response.message || 'Mapa y rutas generadas con éxito.');
      } else {
        toast.error(response.message || 'Hubo un error al generar las rutas.');
      }
    } catch (error) {
      toast.error(error.message || 'Error crítico al generar las rutas.');
    } finally {
      setLoading(false);
    }
  };

  const getRouteColor = useCallback((index) => {
    const colors = ['#e74c3c', '#3498db', '#f39c12', '#27ae60', '#9b59b6', '#e67e22', '#1abc9c'];
    return colors[index % colors.length];
  }, []);

  // --- HOOK useMemo CORREGIDO ---
  const { markers, polylines } = useMemo(() => {
    if (!mapData) return { markers: [], polylines: [] };
    const { nodo_principal, nodos_secundarios, rutas_data } = mapData;

    // Helper para obtener el nombre corto de la localidad
    const getShortName = (fullName) => fullName.split(',')[0];

    // Marcador del Nodo Principal
    const principal = {
      position: [nodo_principal.lat, nodo_principal.lng],
      iconConfig: { color: '#fbbf24', pulse: true },
      popup: {
        title: getShortName(nodo_principal.nombre),
        content: [`Población: ${parseInt(nodo_principal.poblacion).toLocaleString()}`]
      }
    };

    // Marcadores de Nodos Secundarios
    const secundarios = (nodos_secundarios || []).map((nodo, i) => ({
      position: [nodo.lat, nodo.lng],
      iconConfig: { color: '#3b82f6', label: i + 1 },
      popup: {
        title: `Destino ${i + 1}: ${getShortName(nodo.nombre)}`,
        content: [`Población: ${parseInt(nodo.poblacion).toLocaleString()}`, `Distancia Directa: ${nodo.distancia_directa} km`]
      }
    }));

    // Polilíneas de las Rutas
    const rutas = (rutas_data || []).flatMap((destinoData, dIndex) =>
      (destinoData.rutas || []).map((ruta, rIndex) => {
        const isHighlighted = highlightedRoute?.dIndex === dIndex && highlightedRoute?.rIndex === rIndex;
        const isOtherRouteHighlighted = highlightedRoute && !isHighlighted;
        return {
          positions: ruta.puntos_ruta.map(p => [p.lat, p.lng]),
          options: {
            color: getRouteColor(dIndex * 3 + rIndex),
            weight: isHighlighted ? 6 : 4,
            opacity: isOtherRouteHighlighted ? 0.3 : 0.9,
          }
        };
      })
    );
    return { markers: [principal, ...secundarios], polylines: rutas };
  }, [mapData, highlightedRoute, getRouteColor]);

  return {
    isLoading, mapData, markers, polylines, register, handleSubmit, errors, onSubmit, estados, municipios,
    watchedEstado, watchedMunicipio, maxNodos, handleRouteHighlight: setHighlightedRoute, getRouteColor,
  };
};