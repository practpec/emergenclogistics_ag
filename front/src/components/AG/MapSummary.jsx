import { Card, Badge } from '../UI'

const MapSummary = ({ mapData }) => {
  if (!mapData) return null
  
  const totalRutas = mapData.rutas_data?.reduce((sum, d) => 
    sum + (d.rutas?.length || 0), 0) || 0
  
  const totalLocalidades = mapData.nodos_secundarios?.length || 0
  const municipioInfo = mapData.municipio_info || {}
  const nodoPrincipal = mapData.nodo_principal || {}
  
  return (
    <div className="space-y-6">
      {/* Estadísticas principales */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center p-4">
          <div className="text-2xl font-bold text-yellow-400 mb-1">
            {mapData.punto_inicio || 'N/A'}
          </div>
          <div className="text-sm text-gray-400">Estado</div>
        </Card>
        
        <Card className="text-center p-4">
          <div className="text-2xl font-bold text-yellow-400 mb-1">
            {municipioInfo.nombre_municipio || 'N/A'}
          </div>
          <div className="text-sm text-gray-400">Municipio</div>
        </Card>
        
        <Card className="text-center p-4">
          <div className="text-2xl font-bold text-yellow-400 mb-1">
            {totalLocalidades}
          </div>
          <div className="text-sm text-gray-400">Destinos</div>
        </Card>
        
        <Card className="text-center p-4">
          <div className="text-2xl font-bold text-yellow-400 mb-1">
            {totalRutas}
          </div>
          <div className="text-sm text-gray-400">Rutas</div>
        </Card>
      </div>
      
      {/* Información del nodo principal */}
      {nodoPrincipal.nombre_localidad && (
        <Card>
          <h4 className="text-blue-400 font-semibold mb-3">
            Punto de Salida Principal
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-gray-300">
                <strong>Localidad:</strong> {nodoPrincipal.nombre_localidad}
              </p>
              <p className="text-gray-300">
                <strong>Coordenadas:</strong> {nodoPrincipal.lat?.toFixed(4)}, {nodoPrincipal.lng?.toFixed(4)}
              </p>
            </div>
            <div>
              {nodoPrincipal.poblacion && (
                <p className="text-gray-300">
                  <strong>Población:</strong> {nodoPrincipal.poblacion.toLocaleString()} habitantes
                </p>
              )}
              <p className="text-gray-300">
                <strong>Tipo:</strong> {nodoPrincipal.ambito || 'N/A'}
              </p>
            </div>
          </div>
        </Card>
      )}
      
      {/* Lista de destinos */}
      <Card>
        <h4 className="text-blue-400 font-semibold mb-3">
          Destinos Disponibles ({totalLocalidades})
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-64 overflow-y-auto">
          {mapData.nodos_secundarios?.map((nodo, index) => {
            const rutasCount = mapData.rutas_data[index]?.rutas?.length || 0
            
            return (
              <div
                key={index}
                className="bg-gray-700 p-3 rounded-lg flex justify-between items-center"
              >
                <div className="flex-1">
                  <div className="font-medium text-gray-100 text-sm">
                    {nodo.nombre_localidad || nodo.nombre || `Destino ${index + 1}`}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    Población: {nodo.poblacion?.toLocaleString() || 'N/A'}
                  </div>
                </div>
                <div className="text-right">
                  <Badge variant={rutasCount > 0 ? 'success' : 'warning'}>
                    {rutasCount} ruta{rutasCount !== 1 ? 's' : ''}
                  </Badge>
                  {nodo.distancia_directa && (
                    <div className="text-xs text-gray-400 mt-1">
                      {nodo.distancia_directa} km
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </Card>
      
      {/* Información adicional */}
      <Card className="bg-blue-900 border-blue-700">
        <h4 className="text-blue-300 font-semibold mb-3">
          ℹ️ Información del Análisis
        </h4>
        <div className="text-sm text-blue-200 space-y-2">
          <p>
            <strong>Tipo de análisis:</strong> Localidades del mismo municipio
          </p>
          <p>
            <strong>Fuente de datos:</strong> Base de datos oficial INEGI
          </p>
          <p>
            <strong>Total localidades municipales:</strong> {municipioInfo.total_localidades || 'N/A'}
          </p>
          <p>
            <strong>Estado:</strong> Datos listos para crear escenario de emergencia
          </p>
        </div>
      </Card>
    </div>
  )
}

export default MapSummary