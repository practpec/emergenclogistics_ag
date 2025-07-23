import { useState, useEffect } from "react";
import { Button, Badge } from "../UI";
import clsx from "clsx";

const RoutesPanel = ({ routesData = [], municipioInfo, getRouteColor, onRouteHighlight }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedDestinations, setExpandedDestinations] = useState(new Set());

  useEffect(() => {
    if (routesData.length > 0) {
      setExpandedDestinations(new Set([0])); // Auto-expandir el primer destino
    } else {
      setExpandedDestinations(new Set());
    }
  }, [routesData]);

  const toggleDestination = (destinationIndex) => {
    const newExpanded = new Set(expandedDestinations);
    if (newExpanded.has(destinationIndex)) {
      newExpanded.delete(destinationIndex);
      if (onRouteHighlight) {
        onRouteHighlight(null);
      }
    } else {
      newExpanded.add(destinationIndex);
    }
    setExpandedDestinations(newExpanded);
  };

  const extractLocalidadName = (destino) => {
    if (typeof destino === "object" && destino !== null) {
      return destino.nombre_localidad || destino.nombre || JSON.stringify(destino);
    }
    if (typeof destino === "string") {
      const match = destino.match(/^([^(,]+)/);
      return match ? match[1].trim() : destino;
    }
    return "Destino";
  };

  const totalRoutes = routesData.reduce((sum, d) => sum + (d.rutas?.length || 0), 0);

  if (routesData.length === 0 && !isCollapsed) {
    return (
      <div className="w-full md:w-96 bg-gray-800 border border-gray-600 rounded-lg p-6 text-center text-gray-400">
        <p className="text-lg">Sin datos de mapa</p>
        <p className="mt-2 text-sm">Selecciona un estado y municipio para generar las rutas.</p>
      </div>
    );
  }

  return (
    <div
      className={clsx(
        "bg-gray-800 border border-gray-600 rounded-lg flex flex-col transition-all duration-300",
        isCollapsed ? "w-16" : "w-full md:w-96",
      )}
    >
      <div className="p-4 border-b border-gray-600 bg-gray-700 rounded-t-lg flex justify-between items-center">
        <div className={clsx("flex-1", isCollapsed && "hidden")}>
          <h3 className="text-yellow-400 font-semibold">
            {totalRoutes} Rutas para {routesData.length} Destinos
          </h3>
          {municipioInfo && <p className="text-sm text-gray-400 mt-1">{municipioInfo.nombre_municipio}</p>}
        </div>
        <Button onClick={() => setIsCollapsed(!isCollapsed)} size="sm" variant="secondary" className="w-8 h-8 p-0 flex-shrink-0">
          {isCollapsed ? "+" : "−"}
        </Button>
      </div>

      {!isCollapsed && (
        <div className="flex-1 overflow-y-auto">
          {routesData.map((destinoData, destinationIndex) => {
            const isExpanded = expandedDestinations.has(destinationIndex);
            const destinoNombre = extractLocalidadName(destinoData.destino);
            const rutas = destinoData.rutas || [];

            return (
              <div key={destinationIndex} className="border-b border-gray-600">
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
                  <div className={clsx("text-xl text-gray-300 transition-transform duration-200", isExpanded && "transform rotate-180")}>
                    ▼
                  </div>
                </div>

                {isExpanded && (
                  <div className="bg-gray-800">
                    {rutas.length === 0 ? (
                      <div className="p-4 text-center text-gray-400">
                        <p>Sin rutas disponibles para este destino.</p>
                      </div>
                    ) : (
                      rutas.map((ruta, routeIndex) => (
                        <div
                          key={routeIndex}
                          className="p-4 border-t border-gray-700 cursor-pointer hover:bg-gray-700"
                          onClick={(e) => {
                            e.stopPropagation();
                            onRouteHighlight({ destinationIndex, routeIndex });
                          }}
                        >
                          <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center space-x-3">
                              <div
                                className="w-4 h-4 rounded-full border-2 border-white"
                                style={{ backgroundColor: getRouteColor(destinationIndex * 3 + routeIndex) }}
                              />
                              <span className="font-medium text-gray-100">
                                {ruta.tipo || `Ruta ${routeIndex + 1}`}
                              </span>
                            </div>
                            <Badge variant="info">Ver Ruta</Badge>
                          </div>
                          <div className="text-sm text-gray-400 flex flex-wrap gap-x-4 gap-y-1">
                            <span>Distancia: {ruta.distancia?.text || "N/A"}</span>
                            <span>Puntos: {ruta.puntos_ruta?.length || 0}</span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RoutesPanel;