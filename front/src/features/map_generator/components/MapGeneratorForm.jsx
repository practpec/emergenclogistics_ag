import { Button } from '../../../components/common/Button';
import { Input} from '../../../components/common/Input';
import {Select} from '../../../components/common/Select';
import { LoadingSpinner } from '../../../components/common/LoadingSpinner';

const MapGeneratorForm = ({
  isLoading,
  onSubmit,
  register,
  errors,
  estados,
  municipios,
  watchedEstado,
  watchedMunicipio,
  maxNodos,
}) => {
  return (
    <div className="bg-gray-800 border border-gray-600 rounded-lg p-6">
      <h2 className="text-yellow-400 text-xl font-semibold mb-4">
        1. Define el Origen y los Destinos
      </h2>
      <form onSubmit={onSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Estado:</label>
            <Select
              {...register('estado', { required: 'El estado es requerido' })}
              options={[
                { value: '', label: 'Selecciona un estado...' },
                ...estados.map(e => ({ value: e.nombre, label: e.nombre }))
              ]}
              error={errors.estado?.message}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Municipio:</label>
            <Select
              {...register('municipio', { required: 'El municipio es requerido' })}
              options={[
                { value: '', label: watchedEstado ? 'Selecciona un municipio...' : 'Elige un estado' },
                ...municipios.map(m => ({ value: m.clave_municipio, label: m.nombre_municipio }))
              ]}
              disabled={!watchedEstado || municipios.length === 0}
              error={errors.municipio?.message}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1"># de Destinos:</label>
            <Input
              type="number"
              min="1"
              max={maxNodos}
              {...register('n_nodos', {
                required: 'Campo requerido',
                valueAsNumber: true,
                min: { value: 1, message: 'Mínimo 1' },
                max: { value: maxNodos, message: `Máx. ${maxNodos}` }
              })}
              disabled={!watchedMunicipio}
              error={errors.n_nodos?.message}
            />
             {watchedMunicipio && <p className="text-xs text-gray-400 mt-1">Máximo disponible: {maxNodos}</p>}
          </div>
          <div className="self-end">
            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading ? <LoadingSpinner size="sm" /> : 'Generar Mapa'}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default MapGeneratorForm;