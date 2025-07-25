// src/components/ag/results/ScenarioSummary.jsx
import { Card } from '../../common/Card';

const Column = ({ title, children }) => (
    <div className="bg-gray-900/50 p-3 rounded-lg h-full">
        <h3 className="text-base font-semibold text-blue-400 border-b border-gray-700 pb-2 mb-2">{title}</h3>
        <div className="space-y-2 text-xs text-gray-300">{children}</div>
    </div>
);

const InfoPair = ({ label, value }) => (
    <div>
        <p className="text-gray-500">{label}</p>
        <p className="font-semibold">{value}</p>
    </div>
);

const ScenarioSummary = ({ mapData, scenarioConfig, selectedDisaster }) => {
    if (!mapData || !scenarioConfig || !selectedDisaster) return null;

    const { municipio_info, rutas_data } = mapData;
    const { vehiculos_disponibles, ag_params, rutas_estado } = scenarioConfig;
    const { tipo, prioridades } = selectedDisaster;

    const getOriginName = () => {
        if (!municipio_info) return 'N/A';
        const parts = mapData.nodo_principal.nombre.split(',');
        const state = parts.length > 1 ? parts[1].trim() : 'N/A';
        return `${municipio_info.nombre_municipio}, ${state}`;
    };

    const structuredRouteStates = (() => {
        const states = [];
        let currentIndex = 0;
        rutas_data.forEach(destino => {
            const routesForDest = (destino.rutas || []).map(() => rutas_estado[currentIndex++]);
            states.push(routesForDest);
        });
        return states;
    })();

    return (
        <Card>
            <h2 className="text-xl font-semibold text-yellow-400 mb-3 text-center">Resumen de la Configuración</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* --- Columna 1: Configuración General --- */}
                <Column title="General y Flota">
                    <InfoPair label="Origen" value={getOriginName()} />
                    <InfoPair label="Total Vehículos" value={vehiculos_disponibles.length} />
                    <div className="pt-1">
                        <p className="text-gray-500">Composición de Flota:</p>
                        <ul className="list-disc list-inside pl-2">
                            {Object.entries(vehiculos_disponibles.reduce((acc, v) => ({ ...acc, [v.modelo]: (acc[v.modelo] || 0) + 1 }), {})).map(([modelo, count]) => (
                                <li key={modelo}>{count}x {modelo}</li>
                            ))}
                        </ul>
                    </div>
                </Column>

                {/* --- Columna 2: Condiciones del Desastre --- */}
                <Column title="Condiciones del Desastre">
                    <InfoPair label="Tipo de Desastre" value={<span className="capitalize">{tipo.replace('_', ' ')}</span>} />
                    <div className="pt-1">
                        <p className="text-gray-500">Artículos Prioritarios:</p>
                        <ul className="list-disc list-inside pl-2">
                            {(prioridades || []).map(p => (
                                <li key={p.categoria}>{p.categoria}: <strong className="capitalize">{p.nivel}</strong></li>
                            ))}
                        </ul>
                    </div>
                </Column>

                {/* --- Columna 3: Parámetros del Algoritmo --- */}
                <Column title="Parámetros del AG">
                    <InfoPair label="Tamaño Población" value={ag_params.poblacion_size} />
                    <InfoPair label="Generaciones" value={ag_params.generaciones} />
                    <InfoPair label="Prob. de Cruza" value={ag_params.prob_cruza} />
                    <InfoPair label="Prob. de Mutación" value={ag_params.prob_mutacion} />
                    <InfoPair label="Tasa de Elitismo" value={ag_params.elitismo_rate} />
                </Column>
                
                {/* --- Columna 4: Estado de Rutas del Mapa --- */}
                <Column title="Estado de Rutas">
                    <div className="max-h-48 overflow-y-auto pr-2 space-y-2">
                        {rutas_data.map((destinoData, dIndex) => (
                            <div key={dIndex}>
                                <p className="font-semibold text-gray-200 text-sm">Destino {dIndex + 1}:</p>
                                <div className="pl-2 border-l border-gray-600 space-y-1 mt-1">
                                    {structuredRouteStates[dIndex]?.map((routeState, rIndex) => (
                                        <div key={rIndex}>
                                            <span className="font-medium text-gray-400">Ruta {rIndex+1}: </span>
                                            {routeState.estado === 'abierta' ? (
                                                <span className="text-green-400">Abierta</span>
                                            ) : (
                                                <span className="text-red-400">Cerrada</span>
                                            )}
                                            {routeState.estado === 'abierta' && (
                                                <p className="text-gray-500 pl-2">↳ Permitidos: <span className="text-gray-300">{routeState.vehiculos_permitidos.join(', ') || 'Ninguno'}</span></p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </Column>
            </div>
        </Card>
    );
};

export default ScenarioSummary;