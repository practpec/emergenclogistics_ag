import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import useAppStore from '../store/useAppStore'
import apiService, { handleApiError } from '../services/apiService'
import { Button, LoadingSpinner, Select, Checkbox } from '../components/UI'
import MapSummary from '../components/AG/MapSummary'
import ScenarioDisplay from '../components/AG/ScenarioDisplay'
import AGResults from '../components/AG/AGResults'

const AGModule = () => {
  const {
    mapData,
    scenario,
    agResult,
    isLoadingAG,
    entities,
    hasMapData,
    canCreateScenario,
    canExecuteAG,
    setScenario,
    setAGResult,
    setLoadingAG,
    setEntities
  } = useAppStore()
  
  const [currentStep, setCurrentStep] = useState('summary')
  
  const { register, handleSubmit, formState: { errors }, watch } = useForm({
    defaultValues: {
      tipo_desastre: '',
      vehiculos: []
    }
  })
  
  // Cargar entities al montar
  useEffect(() => {
    loadEntities()
  }, [])
  
  // Actualizar step basado en datos disponibles
  useEffect(() => {
    if (!hasMapData()) {
      setCurrentStep('summary')
    } else if (!scenario) {
      setCurrentStep('scenario')
    } else if (!agResult) {
      setCurrentStep('algorithm')
    } else {
      setCurrentStep('results')
    }
  }, [mapData, scenario, agResult, hasMapData])
  
  const loadEntities = async () => {
    try {
      const entitiesData = await apiService.getAllEntities()
      setEntities(entitiesData)
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    }
  }
  
  const onCreateScenario = async (data) => {
    if (!canCreateScenario()) {
      toast.error('No hay datos de mapa disponibles')
      return
    }
    
    setLoadingAG(true)
    
    try {
      const scenarioData = {
        tipo_desastre: data.tipo_desastre,
        vehiculos: data.vehiculos
          .filter(vehiculo => vehiculo.selected)
          .map(vehiculo => ({ tipo: vehiculo.tipo }))
      }
      
      if (scenarioData.vehiculos.length === 0) {
        toast.error('Selecciona al menos un vehículo')
        return
      }
      
      const response = await apiService.createScenario(scenarioData)
      
      if (response.success) {
        setScenario(response.data.escenario)
        setCurrentStep('algorithm')
        toast.success('Escenario creado exitosamente')
      }
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setLoadingAG(false)
    }
  }
  
  const onExecuteAG = async () => {
    if (!canExecuteAG()) {
      toast.error('No hay escenario disponible')
      return
    }
    
    setLoadingAG(true)
    
    try {
      const response = await apiService.executeGeneticAlgorithm(scenario)
      setAGResult(response)
      setCurrentStep('results')
      
      if (response.success) {
        toast.success('Algoritmo ejecutado exitosamente')
      } else {
        toast.info(response.message || 'Algoritmo genético en desarrollo')
      }
    } catch (error) {
      const apiError = handleApiError(error)
      toast.error(apiError.message)
    } finally {
      setLoadingAG(false)
    }
  }
  
  const resetScenario = () => {
    setScenario(null)
    setAGResult(null)
    setCurrentStep('scenario')
  }
  
  return (
    <div className="ag-module">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-light text-yellow-400 mb-2">
          Algoritmo Genético
        </h1>
        <p className="text-gray-300 text-lg">
          Optimización inteligente de distribución de ayuda humanitaria
        </p>
      </div>
      
      {/* Progress indicator */}
      <div className="mb-8">
        <div className="flex justify-center space-x-8">
          {[
            { key: 'summary', label: 'Datos del Mapa', icon: '🗺️' },
            { key: 'scenario', label: 'Crear Escenario', icon: '⚙️' },
            { key: 'algorithm', label: 'Ejecutar AG', icon: '🧬' },
            { key: 'results', label: 'Resultados', icon: '📊' }
          ].map((step, index) => (
            <div
              key={step.key}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${
                currentStep === step.key
                  ? 'bg-blue-600 border-blue-400 text-white'
                  : 'bg-gray-800 border-gray-600 text-gray-400'
              }`}
            >
              <span className="text-xl">{step.icon}</span>
              <span className="font-medium">{step.label}</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Contenido basado en step */}
      {currentStep === 'summary' && (
        <div className="space-y-6">
          <div className="bg-gray-800 border border-gray-600 rounded-lg p-6">
            <h2 className="text-yellow-400 text-xl font-semibold mb-4">
              Datos del Mapa Base
            </h2>
            
            {!hasMapData() ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg mb-4">
                  <span className="text-6xl block mb-4">🗺️</span>
                  <strong>No hay datos de mapa disponibles</strong>
                </div>
                <p className="text-gray-500 mb-6">
                  Para usar el algoritmo genético, primero debes generar un mapa con localidades del mismo municipio.
                </p>
                <Link to="/mapas">
                  <Button className="bg-blue-600 hover:bg-blue-700">
                    Ir a Generar Mapa
                  </Button>
                </Link>
              </div>
            ) : (
              <MapSummary mapData={mapData} />
            )}
          </div>
          
          {hasMapData() && (
            <div className="text-center">
              <Button
                onClick={() => setCurrentStep('scenario')}
                className="bg-green-600 hover:bg-green-700"
              >
                Continuar a Crear Escenario
              </Button>
            </div>
          )}
        </div>
      )}
      
      {currentStep === 'scenario' && (
        <div className="space-y-6">
          <div className="bg-gray-800 border border-gray-600 rounded-lg p-6">
            <h2 className="text-yellow-400 text-xl font-semibold mb-4">
              Configuración de Escenario
            </h2>
            
            <form onSubmit={handleSubmit(onCreateScenario)} className="space-y-6">
              {/* Tipo de desastre */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tipo de Desastre:
                </label>
                <Select
                  {...register('tipo_desastre', { required: 'Tipo de desastre es requerido' })}
                  options={[
                    { value: '', label: 'Selecciona tipo de desastre...' },
                    ...entities.desastres.map(desastre => ({
                      value: desastre.tipo,
                      label: desastre.tipo.charAt(0).toUpperCase() + desastre.tipo.slice(1)
                    }))
                  ]}
                  error={errors.tipo_desastre?.message}
                />
              </div>
              
              {/* Selección de vehículos */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Vehículos Disponibles:
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {entities.vehiculos.map((vehiculo, index) => (
                    <div key={vehiculo.id} className="bg-gray-700 p-4 rounded-lg">
                      <Checkbox
                        {...register(`vehiculos.${index}.selected`)}
                        label={
                          <div>
                            <div className="font-medium">{vehiculo.modelo}</div>
                            <div className="text-sm text-gray-400">
                              {vehiculo.tipo} - {vehiculo.maximo_peso_ton}t
                            </div>
                          </div>
                        }
                      />
                      <input
                        type="hidden"
                        {...register(`vehiculos.${index}.tipo`)}
                        value={vehiculo.tipo}
                      />
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex space-x-4">
                <Button
                  type="button"
                  onClick={() => setCurrentStep('summary')}
                  variant="secondary"
                >
                  Volver
                </Button>
                <Button
                  type="submit"
                  disabled={isLoadingAG}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {isLoadingAG ? <LoadingSpinner size="sm" /> : 'Crear Escenario'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {currentStep === 'algorithm' && (
        <div className="space-y-6">
          <div className="bg-gray-800 border border-gray-600 rounded-lg p-6">
            <h2 className="text-yellow-400 text-xl font-semibold mb-4">
              Escenario Generado
            </h2>
            
            {scenario && <ScenarioDisplay scenario={scenario} />}
            
            <div className="mt-6 flex space-x-4">
              <Button
                onClick={resetScenario}
                variant="secondary"
              >
                Nuevo Escenario
              </Button>
              <Button
                onClick={onExecuteAG}
                disabled={isLoadingAG || !canExecuteAG()}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {isLoadingAG ? <LoadingSpinner size="sm" /> : 'Ejecutar Algoritmo Genético'}
              </Button>
            </div>
          </div>
        </div>
      )}
      
      {currentStep === 'results' && (
        <div className="space-y-6">
          <div className="bg-gray-800 border border-gray-600 rounded-lg p-6">
            <h2 className="text-yellow-400 text-xl font-semibold mb-4">
              Resultados del Algoritmo Genético
            </h2>
            
            {agResult && <AGResults result={agResult} scenario={scenario} />}
            
            <div className="mt-6 flex space-x-4">
              <Button
                onClick={resetScenario}
                variant="secondary"
              >
                Nuevo Análisis
              </Button>
              <Button
                onClick={() => setCurrentStep('summary')}
                className="bg-blue-600 hover:bg-blue-700"
              >
                Volver al Inicio
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AGModule