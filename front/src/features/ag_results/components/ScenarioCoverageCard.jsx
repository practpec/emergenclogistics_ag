import { Card } from '../../../components/common/Card';

// Pequeño componente helper para mostrar estadísticas con iconos
const StatItem = ({ label, value, icon }) => (
  <div className="flex items-start p-2 bg-gray-900/50 rounded-md">
    <div className="text-xl mr-3 text-blue-400">{icon}</div>
    <div>
      <p className="text-sm font-bold text-gray-200">{value}</p>
      <p className="text-xs text-gray-400">{label}</p>
    </div>
  </div>
);

const ScenarioCoverageCard = ({ data }) => {
  const {
    cobertura_rutas,
    eficiencia_vehiculos,
    rutas_cubiertas,
    total_rutas_abiertas,
    vehiculos_utilizados,
    total_vehiculos_disponibles,
    tipo_desastre
  } = data;

  return (
    <Card className="h-full">
      <h3 className="font-bold text-blue-400 mb-3 text-base text-center">Cobertura del Escenario</h3>
      <div className="space-y-3">
        <StatItem 
          icon="🗺️" 
          label="Rutas Cubiertas" 
          value={`${rutas_cubiertas} de ${total_rutas_abiertas}`} 
        />
        <StatItem 
          icon="✅" 
          label="Tasa de Cobertura de Rutas" 
          value={`${(cobertura_rutas * 100).toFixed(0)}%`}
        />
        <StatItem 
          icon="🚚" 
          label="Vehículos Utilizados" 
          value={`${vehiculos_utilizados} de ${total_vehiculos_disponibles}`} 
        />
        <StatItem 
          icon="⚙️" 
          label="Eficiencia de Uso de Flota" 
          value={`${(eficiencia_vehiculos * 100).toFixed(0)}%`}
        />
         <StatItem 
          icon="🌊" 
          label="Tipo de Desastre" 
          value={<span className="capitalize">{tipo_desastre.replace('_', ' ')}</span>}
        />
      </div>
    </Card>
  );
};

export default ScenarioCoverageCard;