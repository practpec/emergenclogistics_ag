import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import { LoadingSpinner, Button, Select, Input } from '../components/UI';
import RoutesPanel from '../components/Map/RoutesPanel';
import MapMarkers from '../components/Map/MapMarkers';
import { useMap } from '../hooks/useMap';
import 'leaflet/dist/leaflet.css';

const MapModule = () => {
  const {
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
    handleRouteHighlight,
  } = useMap();

  const renderRoutes = () => {
    if (!mapData?.rutas_data) return null;
    
    return mapData.rutas_data.flatMap((destino, destinoIndex) => 
      (destino.rutas || []).map((ruta, rutaIndex) => {
        if (!ruta.puntos_ruta || ruta.puntos_ruta.length === 0) return null;

        const positions = ruta.puntos_ruta.map(punto => [punto.lat, punto.lng]);
        const color = getRouteColor(destinoIndex * 3 + rutaIndex);
        
        const isHighlighted = highlightedRoute && 
          highlightedRoute.destinationIndex === destinoIndex && 
          highlightedRoute.routeIndex === rutaIndex;
        
        const isOtherHighlighted = highlightedRoute && !isHighlighted;

        return (
          <Polyline
            key={`route-${destinoIndex}-${rutaIndex}`}
            positions={positions}
            pathOptions={{
              color,
              weight: isHighlighted ? 6 : 4,
              opacity: isOtherHighlighted ? 0.3 : (isHighlighted ? 1.0 : 0.7),
              dashArray: isHighlighted ? '10, 5' : undefined,
            }}
          />
        );
      })
    );
  };

  return (
    <div className="map-module">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-light text-yellow-400 mb-2">
          EmergenLogistics
        </h1>
        <p className="text-gray-300 text-lg">
          Sistema inteligente de distribución de ayuda humanitaria
        </p>
      </div>
      
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
                  ...estados.map(estado => ({ value: estado, label: estado }))
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
                  ...municipios.map(m => ({ value: m.clave_municipio, label: m.nombre_municipio }))
                ]}
                disabled={!watchedEstado || municipios.length === 0}
                error={errors.municipio?.message}
              />
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

      {highlightedRoute && (
        <div className="mb-4 bg-blue-900 border border-blue-700 rounded-lg p-3">
          <p className="text-blue-300 text-sm">
            Mostrando: <strong>Destino {highlightedRoute.destinationIndex + 1}</strong> - 
            Ruta {highlightedRoute.routeIndex + 1}
          </p>
          <button 
            onClick={() => handleRouteHighlight(null)}
            className="text-blue-400 hover:text-blue-300 text-xs underline mt-1"
          >
            Mostrar todas las rutas
          </button>
        </div>
      )}
      
      <div className="flex flex-col md:flex-row gap-6 h-[700px]">
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
              attribution='&copy; OpenStreetMap contributors'
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
        
        <RoutesPanel 
          routesData={mapData?.rutas_data || []}
          municipioInfo={mapData?.municipio_info}
          getRouteColor={getRouteColor}
          onRouteHighlight={handleRouteHighlight}
        />
      </div>
    </div>
  );
};

export default MapModule;