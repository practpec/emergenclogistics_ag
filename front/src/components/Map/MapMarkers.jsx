import { Marker, Popup } from 'react-leaflet'
import L from 'leaflet'

// Configurar iconos de Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

// Icono para nodo principal
const principalIcon = new L.DivIcon({
  className: 'custom-div-icon',
  html: `
    <div class="marker-pin principal-marker">
      <div class="pulse"></div>
    </div>
  `,
  iconSize: [30, 30],
  iconAnchor: [15, 15]
})

// Función para crear icono de nodo secundario
const createSecondaryIcon = (index) => new L.DivIcon({
  className: 'custom-div-icon',
  html: `
    <div class="marker-pin secondary-marker">
      <span class="marker-number">${index + 1}</span>
    </div>
  `,
  iconSize: [30, 30],
  iconAnchor: [15, 15]
})

const MapMarkers = ({ nodoPrincipal, nodosSecundarios = [] }) => {
  return (
    <>
      {/* Nodo Principal */}
      {nodoPrincipal && (
        <Marker
          position={[nodoPrincipal.lat, nodoPrincipal.lng]}
          icon={principalIcon}
        >
          <Popup>
            <div className="text-center min-w-[150px]">
              <h4 className="font-semibold text-yellow-400 mb-2">
                {nodoPrincipal.nombre_localidad || nodoPrincipal.nombre}
              </h4>
              <div className="text-sm text-gray-600">
                <p><strong>Tipo:</strong> Nodo Principal</p>
                <p><strong>Coordenadas:</strong><br/>{nodoPrincipal.lat.toFixed(4)}, {nodoPrincipal.lng.toFixed(4)}</p>
                {nodoPrincipal.poblacion && (
                  <p><strong>Población:</strong> {nodoPrincipal.poblacion.toLocaleString()}</p>
                )}
              </div>
            </div>
          </Popup>
        </Marker>
      )}
      
      {/* Nodos Secundarios */}
      {nodosSecundarios.map((nodo, index) => (
        <Marker
          key={`secondary-${index}`}
          position={[nodo.lat, nodo.lng]}
          icon={createSecondaryIcon(index)}
        >
          <Popup>
            <div className="text-center min-w-[150px]">
              <h4 className="font-semibold text-blue-400 mb-2">
                Destino {index + 1}
              </h4>
              <div className="text-sm text-gray-600">
                <p><strong>Localidad:</strong> {nodo.nombre_localidad || nodo.nombre}</p>
                <p><strong>Coordenadas:</strong><br/>{nodo.lat.toFixed(4)}, {nodo.lng.toFixed(4)}</p>
                {nodo.poblacion && (
                  <p><strong>Población:</strong> {nodo.poblacion.toLocaleString()}</p>
                )}
                {nodo.distancia_directa && (
                  <p><strong>Distancia directa:</strong> {nodo.distancia_directa} km</p>
                )}
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  )
}

export default MapMarkers