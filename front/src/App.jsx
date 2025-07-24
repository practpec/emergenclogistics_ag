import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import MapGeneratorPage from './pages/MapGeneratorPage';
import AGPage from './pages/AGPage';
import AGResultsPage from './pages/AGResultsPage';

function App() {
  return (
    <Router>
      <div className="bg-gray-900 text-gray-100 min-h-screen">
        <Routes>
          <Route path="/map-generator" element={<MapGeneratorPage />} />
          <Route path="/ag-scenario" element={<AGPage />} />
          <Route path="/ag-results" element={<AGResultsPage />} />
          <Route path="*" element={<Navigate to="/map-generator" />} />
        </Routes>
      </div>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 5000,
          style: {
            background: '#1f2937',
            color: '#e5e7eb',
            border: '1px solid #374151',
          },
        }}
      />
    </Router>
  );
}

export default App;