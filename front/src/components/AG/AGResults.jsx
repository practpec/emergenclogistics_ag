import { Card, Badge } from '../UI'

const AGResults = ({ result, scenario }) => {
  if (!result) return null
  
  const isSuccess = result.success
  const resultData = result.data || {}
  
  return (
    <div className="space-y-6">
      {/* Estado del resultado */}
      <Card className={isSuccess ? 'bg-green-900 border-green-700' : 'bg-yellow-900 border-yellow-700'}>
        <div className="flex items-center space-x-3 mb-4">
          <span className="text-3xl">
            {isSuccess ? '✅' : 'ℹ️'}
          </span>
          <div>
            <h3 className={`text-xl font-semibold ${isSuccess ? 'text-green-300' : 'text-yellow-300'}`}>
              {isSuccess ? 'Algoritmo Ejecutado Exitosamente' : 'Información del Sistema'}
            </h3>
            <p className={`text-sm ${isSuccess ? 'text-green-200' : 'text-yellow-200'}`}>
              {result.message || 'Resultado obtenido'}
            </p>
          </div>
        </div>
        
        {!isSuccess && (
          <div className="bg-yellow-800 bg-opacity-50 p-4 rounded-lg">
            <h4 className="text-yellow-200 font-medium mb-2">
              Estado Actual del Algoritmo Genético
            </h4>
            <p className="text-yellow-100 text-sm">
              El algoritmo genético está en desarrollo. Actualmente se puede generar el escenario
              con datos reales de localidades mexicanas y analizar la conectividad entre destinos.
            </p>
          </div>
        )}
      </Card>
      
      {/* Resumen del escenario procesado */}
      {resultData.scenario_summary && (
        <Card>
          <h4 className="text-blue-400 font-semibold mb-3">
            📋 Resumen del Escenario Procesado
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {resultData.scenario_summary.tipo_desastre && (
              <div>
                <div className="text-gray-400 text-sm">Tipo de Desastre</div>
                <div className="text-gray-100 font-medium">
                  {resultData.scenario_summary.tipo_desastre}
                </div>
              </div>
            )}
            {resultData.scenario_summary.total_vehiculos && (
              <div>
                <div className="text-gray-400 text-sm">Total Vehículos</div>
                <div className="text-gray-100 font-medium">
                  {resultData.scenario_summary.total_vehiculos}
                </div>
              </div>
            )}
            {resultData.scenario_summary.total_destinos && (
              <div>
                <div className="text-gray-400 text-sm">Total Destinos</div>
                <div className="text-gray-100 font-medium">
                  {resultData.scenario_summary.total_destinos}
                </div>
              </div>
            )}
            {resultData.scenario_summary.rutas_disponibles && (
              <div>
                <div className="text-gray-400 text-sm">Rutas Disponibles</div>
                <div className="text-gray-100 font-medium">
                  {resultData.scenario_summary.rutas_disponibles}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
      
      {/* Análisis de conectividad */}
      {scenario && (
        <Card>
          <h4 className="text-purple-400 font-semibold mb-3">
            🔗 Análisis de Conectividad
          </h4>
          <div className="space-y-4">
            {/* Estadísticas de rutas */}
            {scenario.rutas_estado && (
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-300">Estado de Rutas</span>
                  <span className="text-gray-400 text-sm">
                    {scenario.rutas_estado.length} rutas evaluadas
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-green-800 bg-opacity-30 p-3 rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-400">
                      {scenario.rutas_estado.filter(r => r.estado === 'abierta').length}
                    </div>
                    <div className="text-sm text-green-300">Rutas Abiertas</div>
                  </div>
                  <div className="bg-red-800 bg-opacity-30 p-3 rounded-lg text-center">
                    <div className="text-2xl font-bold text-red-400">
                      {scenario.rutas_estado.filter(r => r.estado === 'cerrada').length}
                    </div>
                    <div className="text-sm text-red-300">Rutas Bloqueadas</div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Análisis de vehículos */}
            {scenario.vehiculos_disponibles && (
              <div>
                <div className="text-gray-300 mb-2">Capacidad de Transporte</div>
                <div className="space-y-2">
                  {scenario.vehiculos_disponibles.map((vehiculo, index) => {
                    const rutasCompatibles = scenario.rutas_estado?.filter(ruta => 
                      ruta.estado === 'abierta' && 
                      ruta.vehiculos_permitidos?.includes(vehiculo.tipo)
                    ).length || 0
                    
                    return (
                      <div key={index} className="flex justify-between items-center p-2 bg-gray-700 rounded">
                        <div>
                          <span className="text-gray-100 font-medium">{vehiculo.modelo}</span>
                          <span className="text-gray-400 text-sm ml-2">({vehiculo.tipo})</span>
                        </div>
                        <div className="text-right">
                          <Badge variant={rutasCompatibles > 0 ? 'success' : 'warning'}>
                            {rutasCompatibles} rutas accesibles
                          </Badge>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
      
      {/* Métricas del municipio */}
      {scenario?.estadisticas && (
        <Card>
          <h4 className="text-indigo-400 font-semibold mb-3">
            🏘️ Métricas del Municipio
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {scenario.estadisticas.poblacion_total_destinos && (
              <div className="bg-indigo-800 bg-opacity-30 p-4 rounded-lg">
                <div className="text-indigo-300 text-sm">Población Total Destinos</div>
                <div className="text-2xl font-bold text-indigo-100">
                  {scenario.estadisticas.poblacion_total_destinos.toLocaleString()}
                </div>
                <div className="text-indigo-300 text-xs mt-1">habitantes</div>
              </div>
            )}
            
            {scenario.estadisticas.porcentaje_rutas_abiertas !== undefined && (
              <div className="bg-indigo-800 bg-opacity-30 p-4 rounded-lg">
                <div className="text-indigo-300 text-sm">Conectividad</div>
                <div className="text-2xl font-bold text-indigo-100">
                  {scenario.estadisticas.porcentaje_rutas_abiertas}%
                </div>
                <div className="text-indigo-300 text-xs mt-1">rutas operativas</div>
              </div>
            )}
          </div>
        </Card>
      )}
      
      {/* Próximos pasos */}
      <Card className="bg-blue-900 border-blue-700">
        <h4 className="text-blue-300 font-semibold mb-3">
          🚀 Próximos Pasos de Desarrollo
        </h4>
        <div className="space-y-3 text-sm text-blue-200">
          <div className="flex items-center space-x-2">
            <span className="text-yellow-400">⚠️</span>
            <span>Implementación del motor de optimización genética</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-yellow-400">⚠️</span>
            <span>Algoritmos de asignación de recursos por prioridad</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-yellow-400">⚠️</span>
            <span>Optimización de rutas considerando capacidad vehicular</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-yellow-400">⚠️</span>
            <span>Reportes y visualizaciones de soluciones óptimas</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-green-400">✅</span>
            <span>Generación de escenarios con datos reales INEGI</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-green-400">✅</span>
            <span>Análisis de conectividad entre localidades</span>
          </div>
        </div>
      </Card>
      
      {/* Debug info (solo en desarrollo) */}
      {import.meta.env.DEV && result && (
        <Card className="bg-gray-900 border-gray-700">
          <h4 className="text-gray-400 font-semibold mb-3">
            🔧 Información de Debug
          </h4>
          <pre className="text-xs text-gray-500 overflow-auto max-h-40">
            {JSON.stringify(result, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  )
}

export default AGResults