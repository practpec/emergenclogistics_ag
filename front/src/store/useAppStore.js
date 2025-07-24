import { create } from 'zustand';

const useAppStore = create((set) => ({
  mapData: null,
  isLoading: false,
  setMapData: (data) => set({ mapData: data, isLoading: false }),
  setLoading: (loading) => set({ isLoading: loading }),
}));

export default useAppStore;