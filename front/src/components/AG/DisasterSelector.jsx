import { Select } from '../common/Select';

const DisasterSelector = ({ disasters, selectedDisaster, setSelectedDisaster }) => {
  return (
    <div>
      <h3 className="text-xl font-semibold text-gray-200 mb-2">Tipo de Desastre</h3>
      <Select
        value={selectedDisaster}
        onChange={(e) => setSelectedDisaster(e.target.value)}
        options={[
          { value: '', label: 'Selecciona un tipo de desastre...' },
          ...disasters.map(d => ({ value: d.tipo, label: d.tipo.charAt(0).toUpperCase() + d.tipo.slice(1) }))
        ]}
      />
    </div>
  );
};

export default DisasterSelector;