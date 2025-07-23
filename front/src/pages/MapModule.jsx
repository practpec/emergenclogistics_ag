import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import useAppStore from '../store/useAppStore'
import apiService, { handleApiError } from '../services/apiService'
import { LoadingSpinner, Button, Select, Input } from '../components/UI'
import RoutesPanel from '../components/Map/RoutesPanel'
import MapMarkers from '../components/Map/MapMarkers'
import 'leaflet/dist/leaflet.css'

const MapModule = () => {
  const {
    mapData,
    isLoadingMap,
    selectedEstado,
    selectedMunicipio,
    municipios,
    setMapData,
    setLoadingMap,
    setSelectedEstado,
    setMunicipios,
    setSelectedMunicipio,
    clearMapData
  } = useAppStore()
  
  const [estados, setEstados] = useState([])
  const [highlightedRoute, setHighlightedRoute] = useState(null)
  const [municipioInfo, setMunicipioInfo] = useState(null)
  const [maxNodos, setMaxNodos] = useState(15)
  const [routeColors] = useState([
    '#e74c3c', '#3498db', '#f39c12', '#27ae60', '#9b59b6',
    '#e67e22', '#1abc9c', '#34495e', '#f1c40f', '#95a5a6'
  ])
  
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm({
    defaultValues: {
      estado: '',
      municipio: '',
      n_nodos: 5
    }
  })
  
  const watchedEstado = watch('estado')
  const watchedMunicipio = watch('municipio')
  const watchedNNodos = watch('n_nodos')
  
  // Cargar estados al montar
  useEffect(() => {
    loadEstados()
  }, [])
  
  // Cargar municipios cuando cambia el estado
  useEffect(() => {
    if (watchedEstado && watchedEstado !== selectedEstado) {
      setSelectedEstado(watchedEstado)
      setSelectedMunicipio('')
      setValue('municipio', '')
      setMunicipioInfo(null)
      setMaxNodos(15)
      setValue('n_nodos', 5)
      if (watchedEstado) {
        loadMunicipios(watchedEstado)
      }
    }
  }, [watchedEstado])
  
  // Cargar info del municipio cuando cambia
  useEffect(() => {
    if (watchedMunicipio && watchedMunicipio !== selectedMunicipio) {
      setSelectedMunicipio(watchedMunicipio)
      if (watchedMunicipio) {
        loadMunicipioInfo(watchedEstado, watchedMunicipio)
      }
    }
  }, [watchedMunicipio])
  
  // Validar número de nodos cuando cambia
  useEffect(() => {
    if (watchedNNodos && maxNodos > 0) {
      const nNodos = parseInt(watchedNNodos)
      if (nNodos > maxNodos) {
        setValue('n_nodos', maxNodos)
        toast.warning(`Máximo ${maxNodos} destinos para este municipio`)
      }
    }
  }, [watchedNNodos, maxNodos])
  
  const loadEstados = async () => {
    try {
      const response = await apiService.getEstados()
      if (response.success) {
        const estadosSimples = response.data.map(estado => estado.nombre)
        setEstados(estadosSimples)
      }
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    }
  }
  
  const loadMunicipios = async (estado) => {
    try {
      const response = await apiService.getMunicipios(estado)
      if (response.success) {
        setMunicipios(response.data)
      }
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    }
  }
  
  const loadMunicipioInfo = async (estado, claveMunicipio) => {
    try {
      const response = await apiService.getNodoInicialMunicipio(estado, claveMunicipio)
      if (response.success && response.data.municipio_info) {
        const info = response.data.municipio_info
        setMunicipioInfo(info)
        
        // Establecer límite máximo de nodos basado en localidades disponibles
        const localidadesDisponibles = info.total_localidades || 15
        const maxPermitido = Math.min(localidadesDisponibles - 1, 15) // -1 porque una será el nodo principal
        setMaxNodos(Math.max(1, maxPermitido))
        
        // Ajustar valor actual si excede el límite
        const currentNNodos = parseInt(watchedNNodos)
        if (currentNNodos > maxPermitido) {
          setValue('n_nodos', Math.min(5, maxPermitido))
        }
        
        toast.info(`${info.nombre_municipio}: ${localidadesDisponibles} localidades disponibles`)
      }
    } catch (error) {
      console.warn('No se pudo obtener información del municipio:', error)
      setMaxNodos(15)
    }
  }
  
  const onSubmit = async (data) => {
    if (!data.estado) {
      toast.error('Por favor selecciona un estado')
      return
    }
    
    if (!data.municipio) {
      toast.error('Por favor selecciona un municipio')
      return
    }
    
    setLoadingMap(true)
    clearMapData()
    setHighlightedRoute(null)
    
    try {
      const response = await apiService.generateCompleteRoutes(
        data.estado,
        parseInt(data.n_nodos),
        data.municipio
      )
      
      if (response.success) {
        setMapData(response.data)
        toast.success('Mapa generado exitosamente')
      }
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setLoadingMap(false)
    }
  }
  
  const getRouteColor = (index) => {
    return routeColors[index % routeColors.length]
  }
  
  const handleRouteHighlight = (routeInfo) => {
    setHighlightedRoute(routeInfo)
  }
  
  const renderRoutes = () => {
    if (!mapData?.rutas_data) return null
    
    const routes = []
    
    mapData.rutas_data.forEach((destino, destinoIndex) => {
      if (destino.rutas) {
        destino.rutas.forEach((ruta, rutaIndex) => {
          if (ruta.puntos_ruta && ruta.puntos_ruta.length > 0) {
            const positions = ruta.puntos_ruta.map(punto => [punto.lat, punto.lng])
            const color = getRouteColor(destinoIndex * 3 + rutaIndex)
            
            const isHighlighted = highlightedRoute && 
              highlightedRoute.destinationIndex === destinoIndex && 
              highlightedRoute.routeIndex === rutaIndex
            
            const isOtherHighlighted = highlightedRoute && !isHighlighted
            
            routes.push(
              <Polyline
                key={`route-${destinoIndex}-${rutaIndex}`}
                positions={positions}
                pathOptions={{
                  color: color,
                  weight: isHighlighted ? 6 : 4,
                  opacity: isOtherHighlighted ? 0.3 : (isHighlighted ? 1.0 : 0.7),
                  dashArray: isHighlighted ? '10, 5' : undefined
                }}
              />
            )
          }
        })
      }
    })
    
    return routes
  }
  
  return (
    <div className="map-module">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-light text-yellow-400 mb-2">
          EmergenLogistics
        </h1>
        <p className="text-gray-300 text-lg">
          Sistema inteligente de distribución de ayuda humanitaria
        </p>
      </div>
      
      {/* Controles */}
      <div className="bg-gray-800 border border-gray-600 rounded-lg p-6 mb-6">
        <h2 className="text-yellow-400 text-xl font-semibold mb-4">
          Generador de Mapas con Localidades Reales
        </h2>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Estado:
              </label>
              <Select
                {...register('estado', { required: 'Estado es requerido' })}
                options={[
                  { value: '', label: 'Selecciona un estado...' },
                  ...estados.map(estado => ({
                    value: estado,
                    label: estado
                  }))
                ]}
                error={errors.estado?.message}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Municipio:
              </label>
              <Select
                {...register('municipio', { required: 'Municipio es requerido' })}
                options={[
                  { value: '', label: watchedEstado ? 'Selecciona un municipio...' : 'Primero selecciona un estado' },
                  ...municipios.map(municipio => ({
                    value: municipio.clave_municipio,
                    label: municipio.nombre_municipio
                  }))
                ]}
                disabled={!watchedEstado || municipios.length === 0}
                error={errors.municipio?.message}
              />
              {municipioInfo && (
                <div className="text-xs text-gray-400 mt-1">
                  {municipioInfo.total_localidades} localidades disponibles
                </div>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Número de Destinos:
              </label>
              <Input
                type="number"
                min="1"
                max={maxNodos}
                {...register('n_nodos', { 
                  required: 'Número de destinos es requerido',
                  min: { value: 1, message: 'Mínimo 1 destino' },
                  max: { value: maxNodos, message: `Máximo ${maxNodos} destinos` }
                })}
                error={errors.n_nodos?.message}
                disabled={!watchedMunicipio}
              />
              <div className="text-xs text-gray-400 mt-1">
                Máximo: {maxNodos} destinos
              </div>
            </div>
            
            <div className="flex items-end">
              <Button
                type="submit"
                disabled={isLoadingMap || !watchedEstado || !watchedMunicipio}
                className="w-full"
              >
                {isLoadingMap ? <LoadingSpinner size="sm" /> : 'Generar Rutas'}
              </Button>
            </div>
          </div>
        </form>
      </div>
      
      {/* Indicador de ruta resaltada */}
      {highlightedRoute && (
        <div className="mb-4 bg-blue-900 border border-blue-700 rounded-lg p-3">
          <p className="text-blue-300 text-sm">
            📍 Mostrando: <strong>Destino {highlightedRoute.destinationIndex + 1}</strong> - 
            Ruta {highlightedRoute.routeIndex + 1}
          </p>
          <button 
            onClick={() => setHighlightedRoute(null)}
            className="text-blue-400 hover:text-blue-300 text-xs underline mt-1"
          >
            Mostrar todas las rutas
          </button>
        </div>
      )}
      
      {/* Contenido principal */}
      <div className="flex gap-6 h-[700px]">
        {/* Mapa */}
        <div className="flex-1 bg-gray-800 border border-gray-600 rounded-lg overflow-hidden relative">
          {isLoadingMap && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-gray-800 border border-gray-600 rounded-lg p-6 text-center">
                <LoadingSpinner size="lg" />
                <p className="mt-4 text-gray-300">
                  <strong>Generando rutas entre localidades...</strong>
                </p>
                <p className="text-sm text-gray-400 mt-2">
                  Calculando rutas del mismo municipio
                </p>
              </div>
            </div>
          )}
          
          <MapContainer
            center={[23.6345, -102.5528]}
            zoom={6}
            className="w-full h-full"
            style={{ background: '#1a1a1a' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='© OpenStreetMap contributors'
            />
            
            {mapData && (
              <>
                <MapMarkers 
                  nodoPrincipal={mapData.nodo_principal}
                  nodosSecundarios={mapData.nodos_secundarios}
                />
                {renderRoutes()}
              </>
            )}
          </MapContainer>
        </div>
        
        {/* Panel de rutas */}
        <RoutesPanel 
          routesData={mapData?.rutas_data || []}
          municipioInfo={mapData?.municipio_info}
          getRouteColor={getRouteColor}
          onRouteHighlight={handleRouteHighlight}
        />
      </div>
    </div>
  )
}

export default MapModule