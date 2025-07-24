import { Input } from '../common/Input';

const AGSettingsForm = ({ agParams, setAgParams, limits }) => {
  const handleChange = (e) => {
    const { name, value, type, min, max } = e.target;
    let finalValue = type === 'number' ? parseFloat(value) : value;

    // Validar límites para los campos numéricos
    if (type === 'number') {
      if (finalValue < parseFloat(min)) finalValue = parseFloat(min);
      if (finalValue > parseFloat(max)) finalValue = parseFloat(max);
    }
    
    setAgParams(prev => ({ ...prev, [name]: finalValue }));
  };

  return (
    <div>
      <h3 className="font-bold text-blue-400 mb-2">Parámetros del AG</h3>
      <div className="space-y-2 text-xs">
        {/* Tamaño de Población */}
        <div className="grid grid-cols-2 items-center gap-2">
          <label htmlFor="poblacion_size" className="text-gray-400">Población:</label>
          <Input type="number" name="poblacion_size" id="poblacion_size"
                 value={agParams.poblacion_size} onChange={handleChange}
                 min={limits.poblacion_size.min} max={limits.poblacion_size.max} step="10" 
                 className="p-1 text-center"/>
        </div>
        {/* Generaciones */}
        <div className="grid grid-cols-2 items-center gap-2">
          <label htmlFor="generaciones" className="text-gray-400">Generaciones:</label>
          <Input type="number" name="generaciones" id="generaciones"
                 value={agParams.generaciones} onChange={handleChange}
                 min={limits.generaciones.min} max={limits.generaciones.max} step="50"
                 className="p-1 text-center"/>
        </div>
        {/* Prob. Cruza */}
        <div className="grid grid-cols-2 items-center gap-2">
          <label htmlFor="prob_cruza" className="text-gray-400">Prob. Cruza:</label>
          <Input type="number" name="prob_cruza" id="prob_cruza"
                 value={agParams.prob_cruza} onChange={handleChange}
                 min={limits.prob_cruza.min} max={limits.prob_cruza.max} step="0.05"
                 className="p-1 text-center"/>
        </div>
        {/* Prob. Mutación */}
        <div className="grid grid-cols-2 items-center gap-2">
          <label htmlFor="prob_mutacion" className="text-gray-400">Prob. Mutación:</label>
          <Input type="number" name="prob_mutacion" id="prob_mutacion"
                 value={agParams.prob_mutacion} onChange={handleChange}
                 min={limits.prob_mutacion.min} max={limits.prob_mutacion.max} step="0.05"
                 className="p-1 text-center"/>
        </div>
        {/* Tasa de Elitismo */}
        <div className="grid grid-cols-2 items-center gap-2">
          <label htmlFor="elitismo_rate" className="text-gray-400">Elitismo:</label>
          <Input type="number" name="elitismo_rate" id="elitismo_rate"
                 value={agParams.elitismo_rate} onChange={handleChange}
                 min={limits.elitismo_rate.min} max={limits.elitismo_rate.max} step="0.05"
                 className="p-1 text-center"/>
        </div>
      </div>
    </div>
  );
};

export default AGSettingsForm;