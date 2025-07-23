import { useLocation } from 'react-router-dom';
import { Card } from '../components/UI';

const AGPage = () => {
  const location = useLocation();
  const { mapData } = location.state || {};

  if (!mapData) {
    return (
      <div className="text-center">
        <h1 className="text-2xl font-bold text-yellow-400">Página AG</h1>
        <p className="text-gray-400 mt-4">
          No se han pasado datos del mapa. Por favor, genera un mapa primero.
        </p>
      </div>
    );
  }

  const { nodo_principal, nodos_secundarios, rutas_data } = mapData;

  return (
    <div>
      <h1 className="text-3xl font-bold text-yellow-400 mb-6 text-center">
        Detalles del Algoritmo Genético
      </h1>

      <div className="space-y-8">
        {nodo_principal && (
          <Card>
            <h2 className="text-2xl font-semibold text-blue-400 mb-4">Nodo Principal</h2>
            <pre className="bg-gray-900 p-4 rounded-md text-gray-200 overflow-x-auto">
              {JSON.stringify(nodo_principal, null, 2)}
            </pre>
          </Card>
        )}

        {nodos_secundarios && nodos_secundarios.length > 0 && (
          <Card>
            <h2 className="text-2xl font-semibold text-blue-400 mb-4">Nodos de Destino</h2>
            <pre className="bg-gray-900 p-4 rounded-md text-gray-200 overflow-x-auto">
              {JSON.stringify(nodos_secundarios, null, 2)}
            </pre>
          </Card>
        )}

        {rutas_data && rutas_data.length > 0 && (
           <Card>
            <h2 className="text-2xl font-semibold text-blue-400 mb-4">Datos de Rutas</h2>
            <pre className="bg-gray-900 p-4 rounded-md text-gray-200 overflow-x-auto">
                {JSON.stringify(rutas_data, null, 2)}
            </pre>
           </Card>
        )}
      </div>
    </div>
  );
};

export default AGPage;