import { Card } from '../common/Card.jsx';

const MapSummary = ({ mapData }) => {
  if (!mapData) return null;

  const { nodo_principal, nodos_secundarios, rutas_data } = mapData;
  const getShortName = (fullName) => fullName ? fullName.split(',')[0] : 'N/A';

  return (
    <Card className="h-full flex flex-col">
      <h2 className="text-xl font-bold text-blue-400 border-b border-gray-600 pb-2 mb-3">
        Resumen del Mapa
      </h2>
      <div className="flex-grow overflow-y-auto pr-2 space-y-3 text-sm">
        <div>
          <h3 className="font-semibold text-yellow-400 text-base">Origen</h3>
          <div className="text-gray-300 pl-2">
            <p>{getShortName(nodo_principal.nombre)}</p>
            <p className="text-xs text-gray-400">Población: {parseInt(nodo_principal.poblacion).toLocaleString()}</p>
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-yellow-400 text-base">Destinos y Rutas</h3>
          <div className="space-y-2 mt-2">
            {nodos_secundarios.map((destino, index) => (
              <div key={index} className="pl-2 border-l-2 border-gray-700">
                <p className="font-medium text-gray-200">{index + 1}. {getShortName(destino.nombre)}</p>
                <p className="text-xs text-gray-400 ml-2">Población: {parseInt(destino.poblacion).toLocaleString()}</p>
                <div className="text-xs text-gray-400 ml-2">
                  <ul className="list-disc list-inside pl-1">
                    {rutas_data[index]?.rutas.map((ruta, rIndex) => (
                      <li key={rIndex}>{ruta.tipo || 'Ruta'} ({ruta.distancia.text})</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default MapSummary;