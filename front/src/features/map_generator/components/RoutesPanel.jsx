import { useState, useEffect } from "react";
import clsx from "clsx";

const RoutesPanel = ({ routesData = [], municipioInfo, getRouteColor, onRouteHighlight }) => {
  const [expanded, setExpanded] = useState(new Set());

  useEffect(() => {
    if (routesData.length > 0) setExpanded(new Set([0]));
  }, [routesData]);

  const toggle = (i) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });
  };

  const getShortName = (fullName) => fullName ? fullName.split(',')[0] : 'Destino desconocido';

  if (routesData.length === 0) {
    return (
      <div className="w-full md:w-96 bg-gray-800 border border-gray-600 rounded-lg p-6 text-center">
        <h3 className="text-lg font-semibold text-gray-200">Rutas Generadas</h3>
        <p className="mt-2 text-sm text-gray-400">Las rutas aparecerán aquí.</p>
      </div>
    );
  }

  return (
    <div className="w-full md:w-96 bg-gray-800 border border-gray-600 rounded-lg flex flex-col">
      <div className="p-4 border-b border-gray-600">
        <h3 className="text-yellow-400 font-semibold">{municipioInfo?.nombre_municipio}</h3>
        <p className="text-sm text-gray-400">{routesData.length} destinos encontrados</p>
      </div>
      <div className="flex-1 overflow-y-auto">
        {routesData.map((destinoData, dIndex) => (
          <div key={dIndex} className="border-b border-gray-700 last:border-b-0">
            <div onClick={() => toggle(dIndex)} className="p-3 cursor-pointer flex justify-between items-center hover:bg-gray-700">
              <p className="font-semibold text-gray-100 pr-2">
                {dIndex + 1}. {getShortName(destinoData.destino?.nombre)}
              </p>
              <span className={clsx("transition-transform text-gray-400", expanded.has(dIndex) && "rotate-180")}>▼</span>
            </div>
            {expanded.has(dIndex) && (
              <div className="bg-gray-900/50">
                {(destinoData.rutas || []).map((ruta, rIndex) => (
                  <div
                    key={rIndex}
                    className="p-3 border-t border-gray-700 flex items-center gap-3 hover:bg-gray-700/80 cursor-pointer"
                    onMouseEnter={() => onRouteHighlight({ dIndex, rIndex })}
                    onMouseLeave={() => onRouteHighlight(null)}
                  >
                    <div style={{ backgroundColor: getRouteColor(dIndex * 3 + rIndex) }} className="w-3 h-3 rounded-full flex-shrink-0" />
                    <div className="text-sm">
                        <p className="font-medium text-gray-200">{ruta.tipo || 'Ruta'}</p>
                        <p className="text-xs text-gray-400">{ruta.distancia?.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
export default RoutesPanel;