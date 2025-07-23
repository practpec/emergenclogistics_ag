import { create } from 'zustand';

const useAppStore = create((set) => ({
  // Estado del mapa
  mapData: null,
  isLoadingMap: false,
  selectedEstado: '',
  selectedMunicipio: '',
  municipios: [],
  
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
  }),
}));

export default useAppStore;