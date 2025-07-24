import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import MapMarkers from './MapMarkers';
import 'leaflet/dist/leaflet.css';

const MapView = ({ center, zoom, markers = [], polylines = [] }) => {
  return (
    <MapContainer
      center={center}
      zoom={zoom}
      className="w-full h-full"
      style={{ background: '#1a1a1a' }}
      scrollWheelZoom={true}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
      />
      
      <MapMarkers markers={markers} />
      
      {polylines.map((polyline, index) => (
        <Polyline
          key={index}
          positions={polyline.positions}
          pathOptions={polyline.options}
        />
      ))}
    </MapContainer>
  );
};

export default MapView;