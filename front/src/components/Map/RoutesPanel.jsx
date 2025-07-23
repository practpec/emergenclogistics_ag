import { useState } from 'react'
import { Card, Button, Badge } from '../UI'
import clsx from 'clsx'

const RoutesPanel = ({ routesData = [], municipioInfo, getRouteColor }) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [expandedDestinations, setExpandedDestinations] = useState(new Set())
  const [highlightedRoute, setHighlightedRoute] = useState(null)
  
  const toggleDestination = (destinationIndex) => {
    const newExpanded = new Set(expandedDestinations)
    if (newExpanded.has(destinationIndex)) {
      newExpanded.delete(destinationIndex)
    } else {
      newExpanded.add(destinationIndex)
    }
    setExpandedDestinations(newExpanded)
  }
  
  const highlightRoute = (destinationIndex, routeIndex) => {
    setHighlightedRoute({ destinationIndex, routeIndex })
    // Aquí podrías emitir un evento para que el mapa reaccione
  }
  
  const extractLocalidadName = (destinoCompleto) => {
    if (typeof destinoCompleto === 'object' && destinoCompleto.nombre) {
      return destinoCompleto.nombre
    }
    
    if (typeof destinoCompleto === 'string') {
      const match = destinoCompleto.match(/^([^(,]+)/)
      if (match) {
        return match[1].trim()
      }
    }
    
    return 'Destino'
  }
  
  const totalRoutes = routesData.reduce((sum, d) => sum + (d.rutas?.length || 0), 0)
  
  if (routesData.length === 0) {
    return (
      <div className={clsx(
        'routes-panel bg-gray-800 border border-gray-600 rounded-lg flex flex-col transition-all duration-300',
        isCollapsed ? 'w-16' : 'w-96'
      )}>
        <div className="panel-header p-4 border-b border-gray-600 bg-gray-700 rounded-t-lg flex justify-between items-center">
          <h3 className={clsx('text-yellow-400 font-semibold', isCollapsed && 'hidden')}>
            Rutas
          </h3>
          <Button
            onClick={() => setIsCollapsed(!isCollapsed)}
            size="sm"
            variant="secondary"
            className="w-8 h-8 p-0"
          >
            {isCollapsed ? '+' : '−'}
          </Button>
        </div>
        
        {!isCollapsed && (
          <div className="p-6 text-center text-gray-400">
            <div className="text-4xl mb-4">🗺️</div>
            <p>Selecciona estado y municipio para generar rutas</p>
            <small className="text-gray-500 block mt-2">
              Las rutas se generarán entre localidades del mismo municipio
            </small>
          </div>
        )}
      </div>
    )
  }
  
  return (
    <div className={clsx(
      'routes-panel bg-gray-800 border border-gray-600 rounded-lg flex flex-col transition-all duration-300',
      isCollapsed ? 'w-16' : 'w-96'
    )}>
      {/* Header */}
      <div className="panel-header p-4 border-b border-gray-600 bg-gray-700 rounded-t-lg flex justify-between items-center">
        <div className={clsx(isCollapsed && 'hidden')}>
          <h3 className="text-yellow-400 font-semibold">
            {totalRoutes} Rutas para {routesData.length} Destinos
          </h3>
          {municipioInfo && (
            <p className="text-sm text-gray-400 mt-1">
              {municipioInfo.nombre_municipio}
            </p>
          )}
        </div>
        <Button
          onClick={() => setIsCollapsed(!isCollapsed)}
          size="sm"
          variant="secondary"
          className="w-8 h-8 p-0"
        >
          {isCollapsed ? '+' : '−'}
        </Button>
      </div>
      
      {/* Content */}
      {!isCollapsed && (
        <div className="panel-content flex-1 overflow-y-auto">
          {routesData.map((destinoData, destinationIndex) => {
            const rutas = destinoData.rutas || []
            const isExpanded = expandedDestinations.has(destinationIndex)
            const destinoNombre = extractLocalidadName(destinoData.destino)
            
            return (
              <div key={destinationIndex} className="destination-item border-b border-gray-600">
                {/* Destination Header */}
                <div
                  className={clsx(
                    'destination-header p-4 bg-gray-700 cursor-pointer flex justify-between items-center transition-colors hover:bg-gray-600',
                    isExpanded && 'bg-blue-600 hover:bg-blue-600'
                  )}
                  onClick={() => toggleDestination(destinationIndex)}
                >
                  <div className="destination-title">
                    <div className="font-semibold text-gray-100">
                      {destinoNombre}
                    </div>
                    <div className="text-sm text-gray-400 mt-1">
                      {rutas.length} ruta{rutas.length !== 1 ? 's' : ''}
                    </div>
                  </div>
                  <div className={clsx(
                    'toggle-icon text-xl transition-transform',
                    isExpanded && 'rotate-180'
                  )}>
                    ▼
                  </div>
                </div>
                
                {/* Routes List */}
                {isExpanded && (
                  <div className="routes-list bg-gray-800">
                    {rutas.length === 0 ? (
                      <div className="p-4 text-center text-gray-400">
                        <p>Sin rutas disponibles</p>
                        <small>No se pudieron calcular rutas para este destino</small>
                      </div>
                    ) : (
                      rutas.map((ruta, routeIndex) => {
                        const isHighlighted = highlightedRoute?.destinationIndex === destinationIndex && 
                                            highlightedRoute?.routeIndex === routeIndex
                        const routeColor = getRouteColor ? getRouteColor(destinationIndex * 3 + routeIndex) : '#3498db'
                        
                        return (
                          <div
                            key={routeIndex}
                            className={clsx(
                              'route-item p-4 border-b border-gray-700 cursor-pointer transition-all',
                              isHighlighted 
                                ? 'bg-blue-600 border-l-4 border-l-yellow-400' 
                                : 'hover:bg-gray-700'
                            )}
                            onClick={() => highlightRoute(destinationIndex, routeIndex)}
                          >
                            {/* Route Header */}
                            <div className="route-header flex justify-between items-center mb-2">
                              <div className="flex items-center space-x-2">
                                <div 
                                  className="w-3 h-3 rounded-full" 
                                  style={{ backgroundColor: routeColor }}
                                />
                                <span className="route-type font-medium text-gray-100">
                                  Ruta {routeIndex + 1}
                                </span>
                              </div>
                              <Badge variant="info" className="text-xs">
                                Ver
                              </Badge>
                            </div>
                            
                            {/* Route Details */}
                            <div className="route-details text-sm text-gray-400 mb-2">
                              Camino hacia el destino
                            </div>
                            
                            {/* Route Stats */}
                            <div className="route-stats flex space-x-4 text-xs text-gray-500">
                              <div className="route-stat flex items-center space-x-1">
                                <span>📏</span>
                                <span>{ruta.distancia?.text || 'N/A'}</span>
                              </div>
                              <div className="route-stat flex items-center space-x-1">
                                <span>📍</span>
                                <span>
                                  {ruta.puntos_ruta ? ruta.puntos_ruta.length : 0} puntos
                                </span>
                              </div>
                            </div>
                          </div>
                        )
                      })
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default RoutesPanel