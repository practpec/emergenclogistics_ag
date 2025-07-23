import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout/Layout';
import MapModule from './pages/MapModule';
import AGPage from './pages/AGPage'; // Importar la nueva página
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Layout>
          <Routes>
            <Route path="/mapas" element={<MapModule />} />
            <Route path="/ag" element={<AGPage />} /> {/* Añadir la nueva ruta */}
            <Route path="*" element={<Navigate to="/mapas" />} />
          </Routes>
        </Layout>
        
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 5000,
            style: {
              background: '#1a1a1a',
              color: '#e2e8f0',
              border: '1px solid #333',
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;