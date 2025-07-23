import { create } from 'zustand'

const useAppStore = create((set, get) => ({
  // Estado del mapa
  mapData: null,
  isLoadingMap: false,
  selectedEstado: '',
  selectedMunicipio: '',
  municipios: [],
  
  // Estado del algoritmo genético
  scenario: null,
  agResult: null,
  isLoadingAG: false,
  
  // Estado de entities
  entities: {
    vehiculos: [],
    desastres: [],
    categorias_insumos: []
  },
  
  // Acciones del mapa
  setMapData: (data) => set({ mapData: data }),
  
  setLoadingMap: (loading) => set({ isLoadingMap: loading }),
  
  setSelectedEstado: (estado) => set({ 
    selectedEstado: estado,
    selectedMunicipio: '',
    municipios: []
  }),
  
  setMunicipios: (municipios) => set({ municipios }),
  
  setSelectedMunicipio: (municipio) => set({ selectedMunicipio: municipio }),
  
  clearMapData: () => set({ 
    mapData: null,
    selectedEstado: '',
    selectedMunicipio: '',
    municipios: []
  }),
  
  // Acciones del algoritmo genético
  setScenario: (scenario) => set({ scenario }),
  
  setAGResult: (result) => set({ agResult: result }),
  
  setLoadingAG: (loading) => set({ isLoadingAG: loading }),
  
  clearAGData: () => set({ 
    scenario: null,
    agResult: null
  }),
  
  // Acciones de entities
  setEntities: (entities) => set({ entities }),
  
  // Getters derivados
  getCurrentMapStats: () => {
    const { mapData } = get()
    if (!mapData) return null
    
    const totalRutas = mapData.rutas_data?.reduce((sum, d) => 
      sum + (d.rutas?.length || 0), 0) || 0
    
    return {
      totalDestinos: mapData.nodos_secundarios?.length || 0,
      totalRutas,
      estado: mapData.punto_inicio,
      municipio: mapData.municipio_info?.nombre_municipio
    }
  },
  
  hasMapData: () => {
    const { mapData } = get()
    return mapData && mapData.nodos_secundarios?.length > 0
  },
  
  canCreateScenario: () => {
    const { mapData } = get()
    return mapData && mapData.rutas_data?.length > 0
  },
  
  canExecuteAG: () => {
    const { scenario } = get()
    return scenario && scenario.rutas_estado?.length > 0
  }
}))

export default useAppStore