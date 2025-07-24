import { Marker, Popup } from 'react-leaflet'
import L from 'leaflet'

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const createCustomIcon = (iconConfig) => {
  return new L.DivIcon({
    className: 'custom-div-icon',
    html: `
      <div class="marker-pin" style="background-color: ${iconConfig.color};">
        ${iconConfig.pulse ? '<div class="pulse"></div>' : ''}
        ${iconConfig.label ? `<span class="marker-number">${iconConfig.label}</span>` : ''}
      </div>
    `,
    iconSize: [30, 42],
    iconAnchor: [15, 42],
    popupAnchor: [0, -45]
  });
};

const MapMarkers = ({ markers = [] }) => {
  return (
    <>
      {markers.map((markerInfo, index) => (
        <Marker
          key={index}
          position={markerInfo.position}
          icon={createCustomIcon(markerInfo.iconConfig)}
        >
          <Popup>
            <div className="min-w-[200px] text-sm text-gray-200">
              <h4 className="font-bold text-base mb-2" style={{ color: markerInfo.iconConfig.color }}>
                {markerInfo.popup.title}
              </h4>
              <div className="space-y-1 text-gray-400">
                {markerInfo.popup.content.map((line, i) => (
                  <p key={i} dangerouslySetInnerHTML={{ __html: line }} />
                ))}
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  )
}

export default MapMarkers;