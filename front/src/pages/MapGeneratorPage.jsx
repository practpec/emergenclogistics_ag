import { useMapGenerator } from '../features/map_generator/hooks/useMapGenerator';
import MapView from '../components/map/MapView';
import MapGeneratorForm from '../features/map_generator/components/MapGeneratorForm';
import RoutesPanel from '../features/map_generator/components/RoutesPanel';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/common/Button';

const MapGeneratorPage = () => {
  const navigate = useNavigate();
  const {
    isLoading,
    mapData,
    markers,
    polylines,
    // Props para el formulario
    register,
    handleSubmit,
    errors,
    onSubmit,
    estados,
    municipios,
    watchedEstado,
    watchedMunicipio,
    maxNodos,
    // Handlers de interacción
    handleRouteHighlight,
    getRouteColor,
  } = useMapGenerator();

  return (
    <div className="p-4 md:p-8 space-y-6">
      <div className="text-center">
        <h1 className="text-4xl font-light text-yellow-400 mb-2">EmergenLogistics</h1>
        <p className="text-gray-300 text-lg">Sistema inteligente de distribución de ayuda humanitaria</p>
      </div>

      <MapGeneratorForm
        isLoading={isLoading}
        onSubmit={handleSubmit(onSubmit)}
        register={register}
        errors={errors}
        estados={estados}
        municipios={municipios}
        watchedEstado={watchedEstado}
        watchedMunicipio={watchedMunicipio}
        maxNodos={maxNodos}
      />

      <div className="flex flex-col md:flex-row gap-6 h-[700px]">
        <div className="flex-1 bg-gray-800 border border-gray-600 rounded-lg overflow-hidden relative">
          {isLoading && (
            <div className="absolute inset-0 bg-black bg-opacity-70 flex flex-col items-center justify-center z-[1000]">
              <LoadingSpinner size="lg" />
              <p className="mt-4 text-gray-200 font-semibold">Generando rutas, por favor espera...</p>
              <p className="text-sm text-gray-400">Esto puede tomar un momento.</p>
            </div>
          )}
          <MapView
            center={[23.6345, -102.5528]} // Centro inicial de México
            zoom={5}
            markers={markers}
            polylines={polylines}
          />
        </div>
        <RoutesPanel
          routesData={mapData?.rutas_data || []}
          municipioInfo={mapData?.municipio_info}
          onRouteHighlight={handleRouteHighlight}
          getRouteColor={getRouteColor}
        />
      </div>
      {mapData && (
            <div className="text-center mt-6">
                <Button 
                    size="lg" 
                    variant="success"
                    onClick={() => navigate('/ag-scenario', { state: { mapData } })}
                >
                    Continuar a Configuración del Escenario →
                </Button>
            </div>
        )}
    </div>
  );
};

export default MapGeneratorPage;