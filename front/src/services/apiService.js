import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
});

const handleApiError = (error) => {
  if (error.response) {
    console.error("Error de API:", error.response.data);
    return error.response.data.message || 'Error del servidor. Intenta de nuevo.';
  } else if (error.request) {
    console.error("Error de red:", error.request);
    return 'No se pudo conectar con el servidor.';
  } else {
    console.error("Error de configuración:", error.message);
    return 'Ocurrió un error inesperado.';
  }
};

class ApiService {
  async getVehicles() {
    // LLAMADA REAL COMENTADA
    // try {
    //   const response = await api.get('/api/scenario/vehicles');
    //   return response.data;
    // } catch (error) {
    //   throw new Error(handleApiError(error));
    // }

    // --- DATOS SIMULADOS ---
    console.log("API SIMULADA: Obteniendo vehículos...");
    return Promise.resolve({
      success: true,
      data: [
        { vehiculo_id: 1, modelo: "Nissan NP300", tipo: "Camioneta Pickup", capacidad_kg: 1200, consumo_litros_km: 0.12, velocidad_kmh: 80 },
        { vehiculo_id: 2, modelo: "Ford Ranger", tipo: "Camioneta Pickup", capacidad_kg: 1100, consumo_litros_km: 0.14, velocidad_kmh: 85 },
        { vehiculo_id: 3, modelo: "Camión Ligero Hino", tipo: "Camión", capacidad_kg: 3500, consumo_litros_km: 0.20, velocidad_kmh: 70 },
        { vehiculo_id: 4, modelo: "Helicóptero Bell 206", tipo: "Helicóptero", capacidad_kg: 500, consumo_litros_km: 1.5, velocidad_kmh: 150 },
        { vehiculo_id: 5, modelo: "Lancha Rápida", tipo: "Lancha", capacidad_kg: 800, consumo_litros_km: 0.8, velocidad_kmh: 40 }
      ]
    });
  }

  async getDisasters() {
    // LLAMADA REAL COMENTADA
    // try {
    //   const response = await api.get('/api/scenario/disasters');
    //   return response.data;
    // } catch (error) {
    //   throw new Error(handleApiError(error));
    // }

    // --- DATOS SIMULADOS ---
    console.log("API SIMULADA: Obteniendo tipos de desastre...");
    return Promise.resolve({
      success: true,
      data: [
        { id: 1, tipo: "inundacion", descripcion: "Inundaciones severas que bloquean caminos terrestres." },
        { id: 2, tipo: "terremoto", descripcion: "Terremoto que daña infraestructura y carreteras." },
        { id: 3, tipo: "deslizamiento", descripcion: "Deslizamiento de tierra que aísla comunidades." },
        { id: 4, tipo: "incendio_forestal", descripcion: "Incendios que afectan la calidad del aire y la visibilidad." }
      ]
    });
  }

  async getSupplies() {
    // LLAMADA REAL COMENTADA
    // try {
    //   const response = await api.get('/api/scenario/supplies');
    //   return response.data;
    // } catch (error) {
    //   throw new Error(handleApiError(error));
    // }

    // --- DATOS SIMULADOS ---
    console.log("API SIMULADA: Obteniendo insumos...");
    return Promise.resolve({
        success: true,
        data: [
            { insumo_id: 101, nombre: "Agua embotellada", peso_kg: 1.0, categoria: "bebidas" },
            { insumo_id: 102, nombre: "Kit de alimentos no perecederos", peso_kg: 5.0, categoria: "alimentos" },
            { insumo_id: 103, nombre: "Kit de primeros auxilios", peso_kg: 2.5, categoria: "medico" },
            { insumo_id: 104, nombre: "Cobijas", peso_kg: 1.5, categoria: "refugio" }
        ]
    });
  }

  async getEstados() {
    // LLAMADA REAL COMENTADA
    // try {
    //   const response = await api.get('/api/estados');
    //   return response.data.data;
    // } catch (error) {
    //   throw new Error(handleApiError(error));
    // }

    // --- DATOS SIMULADOS ---
    console.log("API SIMULADA: Obteniendo estados...");
    return Promise.resolve([
      { clave_entidad: "07", nombre: "Chiapas" },
      { clave_entidad: "20", nombre: "Oaxaca" },
      { clave_entidad: "30", nombre: "Veracruz de Ignacio de la Llave" }
    ]);
  }

  async getMunicipios(nombreEstado) {
    // LLAMADA REAL COMENTADA
    // try {
    //   const response = await api.get(`/api/municipios/${encodeURIComponent(nombreEstado)}`);
    //   return response.data.data;
    // } catch (error) {
    //   throw new Error(handleApiError(error));
    // }

    // --- DATOS SIMULADOS ---
    console.log(`API SIMULADA: Obteniendo municipios para ${nombreEstado}...`);
    const municipiosSimulados = {
      "Chiapas": [
        { clave_municipio: "101", nombre_municipio: "Tuxtla Gutiérrez" },
        { clave_municipio: "083", nombre_municipio: "Suchiapa" },
        { clave_municipio: "054", nombre_municipio: "Ocozocoautla de Espinosa" }
      ],
      "Oaxaca": [
        { clave_municipio: "067", nombre_municipio: "Oaxaca de Juárez" },
        { clave_municipio: "570", nombre_municipio: "Salina Cruz" }
      ],
      "Veracruz de Ignacio de la Llave": [
        { clave_municipio: "087", nombre_municipio: "Xalapa" },
        { clave_municipio: "193", nombre_municipio: "Veracruz" }
      ]
    };

    // Devuelve los municipios para el estado seleccionado o un array vacío si no hay datos.
    return Promise.resolve(municipiosSimulados[nombreEstado] || []);
  }

  async getMunicipioInfo(estado, claveMunicipio) {
    // LLAMADA REAL COMENTADA
    // try {
    //   const response = await api.get(`/api/nodo-inicial/${encodeURIComponent(estado)}/${claveMunicipio}`);
    //   return response.data;
    // } catch (error) {
    //   throw new Error(handleApiError(error));
    // }

    // --- DATOS SIMULADOS ---
    console.log(`API SIMULADA: Obteniendo info para municipio ${claveMunicipio} en ${estado}...`);
    
    // Simular diferentes conteos de localidades según el municipio
    const conteoPorMunicipio = {
        "101": 257, // Tuxtla Gutiérrez
        "083": 50,  // Suchiapa
        "054": 120, // Ocozocoautla
        "067": 80,  // Oaxaca
        "570": 30,  // Salina Cruz
        "087": 150, // Xalapa
        "193": 200, // Veracruz
    };
    const totalLocalidades = conteoPorMunicipio[claveMunicipio] || 42; // Un valor por defecto

    const dataSimulada = {
      success: true,
      data: {
        nodo_principal: {
          clave_localidad: "0001",
          nombre: "Cabecera Municipal (Simulada)",
          lat: 16.75,
          lng: -93.11,
          poblacion: 150000
        },
        municipio_info: {
          clave_municipio: claveMunicipio,
          nombre_municipio: `Municipio ${claveMunicipio} (Simulado)`,
          total_localidades: totalLocalidades
        }
      }
    };
    return Promise.resolve(dataSimulada);
  }

  async generateCompleteRoutes(estado, nNodos, claveMunicipio) {
    try {
      const requestData = { estado, n_nodos: nNodos, clave_municipio: claveMunicipio };
      const response = await api.post('/api/maps/generate-complete-routes', requestData);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export default new ApiService();