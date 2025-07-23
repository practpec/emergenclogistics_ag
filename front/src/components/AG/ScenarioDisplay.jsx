import { Card, Badge } from '../UI'

const ScenarioDisplay = ({ scenario }) => {
  if (!scenario) return null
  
  const rutasEstado = scenario.rutas_estado || []
  const rutasAbiertas = rutasEstado.filter(r => r.estado === 'abierta').length
  const rutasCerradas = rutasEstado.filter(r => r.estado === 'cerrada').length
  const vehiculos = scenario.vehiculos_disponibles || []
  const estadisticas = scenario.estadisticas || {}
  
  const extractDestinationName = (destino) => {
    if (typeof destino === 'string') {
      const match = destino.match(/^([^(,]+)/)
      return match ? match[1].trim() : destino
    }
    return destino
  }
  
  return (
    <div className="space-y-6">
      {/* Resumen del escenario */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center p-4">
          <div className="text-2xl font-bold text-yellow-400 mb-1">
            {scenario.tipo_desastre}
          </div>
          <div className="text-sm text-gray-400">Tipo de Desastre</div>
        </Card>
        
        <Card className="text-center p-4">
          <div className="text-2xl font-bold text-green-400 mb-1">
            {vehiculos.length}
          </div>
          <div className="text-sm text-gray-400">Vehículos</div>
        </Card>
        
        <Card className="text-center p-4">
          <div className="text-2xl font-bold text-blue-400 mb-1">
            {rutasAbiertas}
          </div>
          <div className="text-sm text-gray-400">Rutas Abiertas</div>
        </Card>
        
        <Card className="text-center p-4">
          <div className="text-2xl font-bold text-red-400 mb-1">
            {rutasCerradas}
          </div>
          <div className="text-sm text-gray-400">Rutas Cerradas</div>
        </Card>
      </div>
      
      {/* Información del punto de partida */}
      <Card>
        <h4 className="text-blue-400 font-semibold mb-3">
          📍 Punto de Partida
        </h4>
        <p className="text-gray-300">
          {scenario.punto_partida || 'No definido'}
        </p>
      </Card>
      
      {/* Vehículos disponibles */}
      <Card>
        <h4 className="text-green-400 font-semibold mb-3">
          🚐 Vehículos Disponibles ({vehiculos.length})
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {vehiculos.map((vehiculo, index) => (
            <div
              key={index}
              className="bg-gray-700 p-3 rounded-lg flex justify-between items-center"
            >
              <div>
                <div className="font-medium text-gray-100">
                  {vehiculo.modelo}
                </div>
                <div className="text-sm text-gray-400">
                  {vehiculo.tipo}
                </div>
              </div>
              <div className="text-right text-sm">
                <div className="text-gray-300">
                  {vehiculo.maximo_peso_ton}t
                </div>
                <div className="text-gray-400">
                  {vehiculo.velocidad_kmh} km/h
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
      
      {/* Estado de rutas */}
      <Card>
        <h4 className="text-orange-400 font-semibold mb-3">
          🛣️ Estado de Rutas ({rutasEstado.length})
        </h4>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {rutasEstado.map((ruta, index) => (
            <div
              key={index}
              className="flex justify-between items-center p-3 bg-gray-700 rounded-lg"
            >
              <div className="flex-1">
                <div className="font-medium text-gray-100 text-sm">
                  {extractDestinationName(ruta.destino)}
                </div>
                {ruta.distancia_km && (
                  <div className="text-xs text-gray-400 mt-1">
                    {ruta.distancia_km} km
                  </div>
                )}
                {ruta.estado === 'cerrada' && ruta.razon_bloqueo && (
                  <div className="text-xs text-red-400 mt-1">
                    {ruta.razon_bloqueo}
                  </div>
                )}
              </div>
              <div className="text-right">
                <Badge 
                  variant={ruta.estado === 'abierta' ? 'success' : 'danger'}
                  className="mb-1"
                >
                  {ruta.estado === 'abierta' ? 'Abierta' : 'Cerrada'}
                </Badge>
                {ruta.vehiculos_permitidos && (
                  <div className="text-xs text-gray-400">
                    {ruta.vehiculos_permitidos.length} vehículo{ruta.vehiculos_permitidos.length !== 1 ? 's' : ''}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
      
      {/* Estadísticas del escenario */}
      {estadisticas && Object.keys(estadisticas).length > 0 && (
        <Card className="bg-purple-900 border-purple-700">
          <h4 className="text-purple-300 font-semibold mb-3">
            📊 Estadísticas del Escenario
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            {estadisticas.total_destinos && (
              <div>
                <div className="text-purple-200 font-medium">Total Destinos</div>
                <div className="text-purple-100">{estadisticas.total_destinos}</div>
              </div>
            )}
            {estadisticas.poblacion_total_destinos && (
              <div>
                <div className="text-purple-200 font-medium">Población Total</div>
                <div className="text-purple-100">
                  {estadisticas.poblacion_total_destinos.toLocaleString()}
                </div>
              </div>
            )}
            {estadisticas.porcentaje_rutas_abiertas !== undefined && (
              <div>
                <div className="text-purple-200 font-medium">% Rutas Abiertas</div>
                <div className="text-purple-100">{estadisticas.porcentaje_rutas_abiertas}%</div>
              </div>
            )}
            {estadisticas.usando_datos_reales && (
              <div className="col-span-2 md:col-span-3">
                <div className="text-purple-200 font-medium">Fuente de Datos</div>
                <div className="text-purple-100">
                  ✅ Datos reales de localidades mexicanas (INEGI)
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  )
}

export default ScenarioDisplay