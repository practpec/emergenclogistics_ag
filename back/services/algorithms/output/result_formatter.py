from typing import Dict, List, Any
from ..models import *


class ResultFormatter:
    """Formateador de resultados del algoritmo genético"""
    
    @staticmethod
    def formatear_para_frontend(resultado_ag: Dict[str, Any]) -> Dict[str, Any]:
        """Formatear resultados para el frontend"""
        
        return {
            "solucion_optima": {
                "asignaciones": resultado_ag["mejor_solucion"]["asignaciones"],
                "fitness": resultado_ag["mejor_solucion"]["fitness"],
                "metricas": {
                    "rutas_utilizadas": resultado_ag["mejor_solucion"]["rutas_utilizadas"],
                    "vehiculos_utilizados": resultado_ag["mejor_solucion"]["vehiculos_utilizados"],
                    "peso_total": resultado_ag["mejor_solucion"]["peso_total_transportado"],
                    "combustible_total": resultado_ag["mejor_solucion"]["combustible_total"]
                }
            },
            
            "alternativas": [
                {
                    "posicion": i + 1,
                    "fitness": solucion["fitness"],
                    "asignaciones": solucion["asignaciones"],
                    "resumen": {
                        "rutas": solucion["rutas_utilizadas"],
                        "vehiculos": solucion["vehiculos_utilizados"],
                        "peso": solucion["peso_total_transportado"]
                    }
                }
                for i, solucion in enumerate(resultado_ag["top_3_soluciones"])
            ],
            
            "visualizaciones": {
                "evolucion_fitness": {
                    "datos": resultado_ag["evolucion_fitness"],
                    "generaciones": list(range(1, len(resultado_ag["evolucion_fitness"]) + 1)),
                    "mejora_total": resultado_ag["metricas_optimizacion"]["mejora_total"]
                },
                
                "distribucion_carga": resultado_ag["distribucion_carga"],
                
                "mapa_entregas": {
                    "exitosas": resultado_ag["cronologia_entregas"]["entregas_exitosas"],
                    "fallidas": resultado_ag["cronologia_entregas"]["entregas_fallidas"],
                    "tasa_exito": resultado_ag["cronologia_entregas"]["tasa_exito"]
                }
            },
            
            "reportes": {
                "eficiencia": resultado_ag["analisis_eficiencia"],
                "escenario": resultado_ag["resumen_escenario"],
                "optimizacion": resultado_ag["metricas_optimizacion"]
            }
        }
    
    @staticmethod
    def generar_resumen_ejecutivo(resultado_ag: Dict[str, Any]) -> Dict[str, Any]:
        """Generar resumen ejecutivo para la toma de decisiones"""
        
        mejor_solucion = resultado_ag["mejor_solucion"]
        resumen_escenario = resultado_ag["resumen_escenario"]
        cronologia = resultado_ag["cronologia_entregas"]
        
        return {
            "resumen_ejecutivo": {
                "desastre": resumen_escenario["tipo_desastre"],
                "cobertura_lograda": f"{resumen_escenario['cobertura_rutas']*100:.1f}%",
                "poblacion_atendida": cronologia["poblacion_cubierta"],
                "poblacion_sin_atencion": cronologia["poblacion_no_cubierta"],
                "eficiencia_vehiculos": f"{resumen_escenario['eficiencia_vehiculos']*100:.1f}%",
                "fitness_final": mejor_solucion["fitness"]
            },
            
            "recomendaciones": ResultFormatter._generar_recomendaciones(resultado_ag),
            
            "alertas": ResultFormatter._generar_alertas(resultado_ag)
        }
    
    @staticmethod
    def _generar_recomendaciones(resultado_ag: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones basadas en los resultados"""
        recomendaciones = []
        
        distribucion = resultado_ag["distribucion_carga"]
        eficiencia_vehiculos = resultado_ag["resumen_escenario"]["eficiencia_vehiculos"]
        cobertura_rutas = resultado_ag["resumen_escenario"]["cobertura_rutas"]
        
        # Recomendaciones de eficiencia
        if distribucion["utilizacion_promedio"] < 70:
            recomendaciones.append("Considerar reducir el número de vehículos o aumentar la carga por vehículo")
        
        if eficiencia_vehiculos < 0.8:
            recomendaciones.append("Hay vehículos sin asignar, evaluar reasignación o rutas adicionales")
        
        if cobertura_rutas < 0.9:
            recomendaciones.append("Considerar vehículos adicionales para cubrir más destinos")
        
        # Recomendaciones de distribución
        vehiculos_subutilizados = distribucion["vehiculos_subutilizados"]
        if vehiculos_subutilizados > 0:
            recomendaciones.append(f"Optimizar carga de {vehiculos_subutilizados} vehículos subutilizados")
        
        return recomendaciones
    
    @staticmethod
    def _generar_alertas(resultado_ag: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar alertas críticas"""
        alertas = []
        
        cronologia = resultado_ag["cronologia_entregas"]
        distribucion = resultado_ag["distribucion_carga"]
        
        # Alertas de cobertura
        if cronologia["tasa_exito"] < 80:
            alertas.append({
                "tipo": "critico",
                "mensaje": f"Tasa de éxito baja: {cronologia['tasa_exito']:.1f}%",
                "accion": "Revisar disponibilidad de vehículos y rutas"
            })
        
        # Alertas de sobrecarga
        sobrecargas = [v for v in distribucion["vehiculos"] if v["estado_carga"] == "Sobrecarga"]
        if sobrecargas:
            alertas.append({
                "tipo": "advertencia",
                "mensaje": f"{len(sobrecargas)} vehículos con sobrecarga",
                "accion": "Redistribuir carga entre vehículos"
            })
        
        # Alertas de población sin atender
        poblacion_sin_atencion = cronologia["poblacion_no_cubierta"]
        if poblacion_sin_atencion > 1000:
            alertas.append({
                "tipo": "critico",
                "mensaje": f"{poblacion_sin_atencion} personas sin atención",
                "accion": "Priorizar recursos adicionales"
            })
        
        return alertas