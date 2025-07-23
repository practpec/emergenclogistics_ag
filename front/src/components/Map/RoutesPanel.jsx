"use client"

import { useState, useEffect } from "react"
import { Button, Badge } from "../UI"
import clsx from "clsx"

const RoutesPanel = ({ routesData = [], municipioInfo, getRouteColor, onRouteHighlight }) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [expandedDestinations, setExpandedDestinations] = useState(new Set())

  useEffect(() => {
    console.log("RoutesPanel - routesData actualizado:", routesData)
    if (routesData.length > 0) {
      console.log("RoutesPanel - Estructura del primer destino:", routesData[0])
      // Auto-expandir el primer destino
      setExpandedDestinations(new Set([0]))
    }
  }, [routesData])

  const toggleDestination = (destinationIndex) => {
    console.log("RoutesPanel - Toggle destino:", destinationIndex)

    const newExpanded = new Set(expandedDestinations)
    if (newExpanded.has(destinationIndex)) {
      newExpanded.delete(destinationIndex)
      console.log("RoutesPanel - Colapsando destino:", destinationIndex)
      if (onRouteHighlight) {
        onRouteHighlight(null)
      }
    } else {
      newExpanded.add(destinationIndex)
      console.log("RoutesPanel - Expandiendo destino:", destinationIndex)
    }

    setExpandedDestinations(newExpanded)
    console.log("RoutesPanel - Destinos expandidos:", Array.from(newExpanded))
  }

  const handleRouteClick = (destinationIndex, routeIndex) => {
    console.log("RoutesPanel - Click en ruta:", { destinationIndex, routeIndex })
    if (onRouteHighlight) {
      onRouteHighlight({ destinationIndex, routeIndex })
    }
  }

  const extractLocalidadName = (destinoCompleto) => {
    if (typeof destinoCompleto === "object") {
      if (destinoCompleto.nombre) return destinoCompleto.nombre
      if (destinoCompleto.nombre_localidad) return destinoCompleto.nombre_localidad
      return JSON.stringify(destinoCompleto)
    }

    if (typeof destinoCompleto === "string") {
      const match = destinoCompleto.match(/^([^(,]+)/)
      if (match) {
        return match[1].trim()
      }
      return destinoCompleto
    }

    return "Destino"
  }

  const totalRoutes = routesData.reduce((sum, d) => sum + (d.rutas?.length || 0), 0)

  if (routesData.length === 0) {
    return (
      <div
        className={clsx(
          "routes-panel bg-gray-800 border border-gray-600 rounded-lg flex flex-col transition-all duration-300",
          isCollapsed ? "w-16" : "w-96",
        )}
      >
        <div className="panel-header p-4 border-b border-gray-600 bg-gray-700 rounded-t-lg flex justify-between items-center">
          <h3 className={clsx("text-yellow-400 font-semibold", isCollapsed && "hidden")}>Rutas</h3>
          <Button onClick={() => setIsCollapsed(!isCollapsed)} size="sm" variant="secondary" className="w-8 h-8 p-0">
            {isCollapsed ? "+" : "−"}
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
    <div
      className={clsx(
        "routes-panel bg-gray-800 border border-gray-600 rounded-lg flex flex-col transition-all duration-300",
        isCollapsed ? "w-16" : "w-96",
      )}
    >
      {/* Header */}
      <div className="panel-header p-4 border-b border-gray-600 bg-gray-700 rounded-t-lg flex justify-between items-center">
        <div className={clsx(isCollapsed && "hidden")}>
          <h3 className="text-yellow-400 font-semibold">
            {totalRoutes} Rutas para {routesData.length} Destinos
          </h3>
          {municipioInfo && <p className="text-sm text-gray-400 mt-1">{municipioInfo.nombre_municipio}</p>}
        </div>
        <Button onClick={() => setIsCollapsed(!isCollapsed)} size="sm" variant="secondary" className="w-8 h-8 p-0">
          {isCollapsed ? "+" : "−"}
        </Button>
      </div>

      {/* Content */}
      {!isCollapsed && (
        <div className="panel-content flex-1 overflow-y-auto">
          {routesData.map((destinoData, destinationIndex) => {
            console.log(`RoutesPanel - Renderizando destino ${destinationIndex}:`, destinoData)

            const rutas = destinoData.rutas || []
            const isExpanded = expandedDestinations.has(destinationIndex)

            let destinoNombre = "Destino"
            if (destinoData.destino) {
              destinoNombre = extractLocalidadName(destinoData.destino)
            } else if (destinoData.nombre) {
              destinoNombre = destinoData.nombre
            } else if (destinoData.nombre_localidad) {
              destinoNombre = destinoData.nombre_localidad
            }

            console.log(
              `RoutesPanel - Destino ${destinationIndex} - Nombre: ${destinoNombre}, Rutas: ${rutas.length}, Expandido: ${isExpanded}`,
            )

            return (
              <div key={destinationIndex} className="border-b border-gray-600">
                {/* Destination Header */}
                <div
                  className={clsx(
                    "p-4 cursor-pointer flex justify-between items-center",
                    isExpanded ? "bg-blue-600 hover:bg-blue-700" : "bg-gray-700 hover:bg-gray-600",
                  )}
                  onClick={() => toggleDestination(destinationIndex)}
                >
                  <div className="flex-1">
                    <div className="font-semibold text-gray-100">
                      Destino {destinationIndex + 1}: {destinoNombre}
                    </div>
                    <div className="text-sm text-gray-300 mt-1">
                      {rutas.length} ruta{rutas.length !== 1 ? "s" : ""} disponible{rutas.length !== 1 ? "s" : ""}
                    </div>
                  </div>
                  <div
                    className={clsx(
                      "text-xl text-gray-300 transition-transform duration-200",
                      isExpanded && "transform rotate-180",
                    )}
                  >
                    ▼
                  </div>
                </div>

                {/* Routes List - RENDERIZADO SIMPLE SIN ANIMACIONES */}
                {isExpanded && (
                  <div className="bg-gray-800">
                    <div className="p-2 bg-gray-750 text-xs text-gray-400 border-t border-gray-600">
                      ✅ MOSTRANDO {rutas.length} ruta{rutas.length !== 1 ? "s" : ""}:
                    </div>

                    {rutas.length === 0 ? (
                      <div className="p-4 text-center text-gray-400">
                        <p>❌ Sin rutas disponibles</p>
                      </div>
                    ) : (
                      <div>
                        {rutas.map((ruta, routeIndex) => {
                          const routeColor = getRouteColor
                            ? getRouteColor(destinationIndex * 3 + routeIndex)
                            : "#3498db"

                          console.log(`RoutesPanel - Renderizando ruta ${routeIndex}:`, ruta)

                          return (
                            <div
                              key={routeIndex}
                              className="p-4 border-b border-gray-700 cursor-pointer hover:bg-gray-700"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleRouteClick(destinationIndex, routeIndex)
                              }}
                            >
                              {/* Route Header */}
                              <div className="flex justify-between items-center mb-2">
                                <div className="flex items-center space-x-3">
                                  <div
                                    className="w-4 h-4 rounded-full border-2 border-white"
                                    style={{ backgroundColor: routeColor }}
                                  />
                                  <span className="font-medium text-gray-100">
                                    {ruta.tipo || `Ruta ${routeIndex + 1}`}
                                  </span>
                                </div>
                                <Badge variant="info" className="text-xs">
                                  👁️ Ver
                                </Badge>
                              </div>

                              {/* Route Details */}
                              <div className="text-sm text-gray-400 mb-2">
                                {ruta.descripcion || "Camino hacia el destino"}
                              </div>

                              {/* Route Stats */}
                              <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                                <div className="flex items-center space-x-1">
                                  <span>📏</span>
                                  <span>{ruta.distancia?.text || "N/A"}</span>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <span>📍</span>
                                  <span>{ruta.puntos_ruta ? ruta.puntos_ruta.length : 0} puntos</span>
                                </div>
                                {ruta.tipo && (
                                  <div className="flex items-center space-x-1">
                                    <span>🛣️</span>
                                    <span>{ruta.tipo}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Debug Info */}
      {!isCollapsed && (
        <div className="p-2 bg-gray-900 text-xs text-gray-500 border-t border-gray-600">
          <div>🔍 Destinos expandidos: [{Array.from(expandedDestinations).join(", ")}]</div>
          <div>📊 Total rutas: {totalRoutes}</div>
          <div>🎯 Estado actual: {expandedDestinations.size > 0 ? "EXPANDIDO" : "COLAPSADO"}</div>
        </div>
      )}
    </div>
  )
}

export default RoutesPanel
