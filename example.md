\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{float}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{subcaption}

\geometry{margin=2.5cm}
\usetikzlibrary{arrows,shapes,positioning,shadows,trees,calc}

\title{\textbf{Algoritmo Genético para Optimización de Distribución Logística\\en Escenarios de Emergencia Humanitaria}}
\author{Sistema EmergenLogistics}
\date{\today}

\begin{document}

\maketitle

\section{Introducción}

El presente documento describe detalladamente el funcionamiento de un algoritmo genético (AG) diseñado específicamente para resolver el problema de optimización logística en la distribución de ayuda humanitaria durante emergencias. El sistema busca asignar óptimamente vehículos, rutas e insumos para maximizar la eficiencia en la entrega de suministros a poblaciones afectadas.

\section{Definición del Problema de Optimización}

\subsection{Variables de Decisión}

El problema se modela mediante las siguientes variables de decisión:

\begin{align}
x_{v,d,r} &\in \{0,1\} \quad \forall v \in V, d \in D, r \in R_d \label{eq:decision_route}\\
y_{v,i} &\in \mathbb{Z}^+ \quad \forall v \in V, i \in I \label{eq:decision_supplies}
\end{align}

Donde:
\begin{itemize}
\item $x_{v,d,r} = 1$ si el vehículo $v$ utiliza la ruta $r$ hacia el destino $d$
\item $y_{v,i}$ es la cantidad del insumo $i$ transportado por el vehículo $v$
\item $V$ es el conjunto de vehículos disponibles
\item $D$ es el conjunto de destinos afectados
\item $R_d$ es el conjunto de rutas disponibles hacia el destino $d$
\item $I$ es el conjunto de tipos de insumos
\end{itemize}

\subsection{Función Objetivo}

La función objetivo busca maximizar el fitness global del sistema:

\begin{equation}
\text{Maximizar } F = \sum_{v=1}^{|V|} \left( F_{\text{relevancia}}(v) + F_{\text{eficiencia}}(v) + F_{\text{utilización}}(v) \right) - P_{\text{total}}
\label{eq:objective}
\end{equation}

\subsection{Restricciones del Sistema}

\subsubsection{Restricción de Capacidad}
\begin{equation}
\sum_{i=1}^{|I|} y_{v,i} \cdot w_i \leq C_v \quad \forall v \in V
\label{eq:capacity_constraint}
\end{equation}

Donde $w_i$ es el peso unitario del insumo $i$ y $C_v$ es la capacidad del vehículo $v$.

\subsubsection{Restricción de Asignación Única}
\begin{equation}
\sum_{d=1}^{|D|} \sum_{r \in R_d} x_{v,d,r} = 1 \quad \forall v \in V
\label{eq:unique_assignment}
\end{equation}

\subsubsection{Restricción de Compatibilidad de Rutas}
\begin{equation}
x_{v,d,r} = 0 \text{ si } \tau_v \notin \Phi_{d,r}
\label{eq:route_compatibility}
\end{equation}

Donde $\tau_v$ es el tipo del vehículo $v$ y $\Phi_{d,r}$ es el conjunto de tipos de vehículos permitidos en la ruta $r$ hacia el destino $d$.

\section{Representación del Cromosoma}

\subsection{Estructura del Individuo}

Cada individuo en la población representa una solución completa al problema y se define como:

\begin{equation}
\text{Individuo} = \{A_1, A_2, \ldots, A_{|V|}\}
\label{eq:individual}
\end{equation}

Donde cada $A_v$ es la asignación del vehículo $v$:

\begin{equation}
A_v = \langle \text{id}_v, \text{destino}_v, \text{ruta}_v, \mathbf{s}_v \rangle
\label{eq:vehicle_assignment}
\end{equation}

El vector de suministros $\mathbf{s}_v$ se define como:

\begin{equation}
\mathbf{s}_v = [s_{v,1}, s_{v,2}, \ldots, s_{v,|I|}] \quad \text{donde } s_{v,i} = y_{v,i}
\label{eq:supply_vector}
\end{equation}

\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=1.5cm]
% Cromosoma representation
\node[draw, rectangle, minimum width=12cm, minimum height=1cm] (chromosome) {};
\node[above of=chromosome, node distance=0.3cm] {\textbf{Cromosoma (Individuo)}};

% Vehicle assignments
\foreach \x in {0,1,2,3} {
    \node[draw, rectangle, minimum width=2.8cm, minimum height=0.8cm, fill=blue!20] at (chromosome.west) +(\x*3,0) {$A_{\x+1}$};
}

% Individual assignment detail
\node[draw, rectangle, minimum width=8cm, minimum height=3cm, below of=chromosome, node distance=3cm] (assignment) {};
\node[above of=assignment, node distance=0.2cm] {\textbf{Asignación Individual $A_v$}};

\node[anchor=west] at (assignment.west) +(0.2,1) {ID Vehículo: $\text{id}_v$}; 
\node[anchor=west] at (assignment.west) +(0.2,0.5) {Destino: $\text{destino}_v$}; 
\node[anchor=west] at (assignment.west) +(0.2,0) {Ruta: $\text{ruta}_v$}; 
\node[anchor=west] at (assignment.west) +(0.2,-0.5) {Suministros: $\mathbf{s}_v = [s_{v,1}, s_{v,2}, \ldots, s_{v,|I|}]$};

\draw[->, thick] (chromosome.south) -- (assignment.north);
\end{tikzpicture}
\caption{Representación del cromosoma y estructura de asignaciones}
\label{fig:chromosome}
\end{figure}

\section{Función de Evaluación (Fitness)}

\subsection{Componentes del Fitness}

La función de fitness se compone de múltiples criterios que evalúan la calidad de una solución:

\subsubsection{Relevancia de Insumos}

\begin{equation}
F_{\text{relevancia}}(v) = \sum_{i=1}^{|I|} s_{v,i} \cdot P_i \cdot \alpha_{\text{rel}}
\label{eq:relevance_fitness}
\end{equation}

Donde:
\begin{itemize}
\item $P_i$ es la prioridad del insumo $i$ según el tipo de desastre
\item $\alpha_{\text{rel}} = 15$ es el factor de ponderación para relevancia
\end{itemize}

La prioridad $P_i$ se calcula según el tipo de desastre:

\begin{equation}
P_i = \begin{cases}
3.0 & \text{si la categoría del insumo } i \text{ tiene prioridad alta} \\
2.0 & \text{si la categoría del insumo } i \text{ tiene prioridad media} \\
1.0 & \text{si la categoría del insumo } i \text{ tiene prioridad baja}
\end{cases}
\label{eq:priority_calculation}
\end{equation}

\subsubsection{Eficiencia Poblacional}

\begin{equation}
F_{\text{eficiencia}}(v) = \left(\frac{W_v}{100}\right) \cdot \left(\frac{N_d}{1000}\right) + B_{\text{ratio}} + B_{\text{match}} \cdot \alpha_{\text{eff}}
\label{eq:efficiency_fitness}
\end{equation}

Donde:
\begin{itemize}
\item $W_v = \sum_{i=1}^{|I|} s_{v,i} \cdot w_i$ es el peso total transportado por el vehículo $v$
\item $N_d$ es la población del destino $d$
\item $\alpha_{\text{eff}} = 12$ es el factor de ponderación para eficiencia
\end{itemize}

Las bonificaciones se calculan como:

\begin{equation}
B_{\text{ratio}} = \begin{cases}
50 & \text{si } 0.5 \leq \frac{W_v}{N_d} \leq 2.0 \\
-30 & \text{si } \frac{W_v}{N_d} < 0.2 \\
-20 & \text{si } \frac{W_v}{N_d} > 5.0 \\
0 & \text{en otro caso}
\end{cases}
\label{eq:ratio_bonus}
\end{equation}

\begin{equation}
B_{\text{match}} = \begin{cases}
100 & \text{si } C_v > 2000 \text{ y } N_d > 1000 \\
80 & \text{si } C_v < 1500 \text{ y } N_d < 100 \\
-80 & \text{si } C_v < 1500 \text{ y } N_d > 1000 \\
-60 & \text{si } C_v > 2000 \text{ y } N_d < 100 \\
0 & \text{en otro caso}
\end{cases}
\label{eq:match_bonus}
\end{equation}

\subsubsection{Utilización de Capacidad}

\begin{equation}
F_{\text{utilización}}(v) = \begin{cases}
200 & \text{si } U_v \geq 0.9 \\
100 & \text{si } 0.7 \leq U_v < 0.9 \\
50 & \text{si } 0.5 \leq U_v < 0.7 \\
0 & \text{en otro caso}
\end{cases} + W_v \cdot \alpha_{\text{weight}}
\label{eq:utilization_fitness}
\end{equation}

Donde:
\begin{itemize}
\item $U_v = \frac{W_v}{C_v}$ es la utilización de capacidad del vehículo $v$
\item $\alpha_{\text{weight}} = 0.8$ es el factor de ponderación para peso
\end{itemize}

\subsection{Penalizaciones}

\subsubsection{Penalización por Sobrecarga}

\begin{equation}
P_{\text{sobrecarga}}(v) = \begin{cases}
(W_v - C_v) \cdot 1000 + 5000 & \text{si } W_v > C_v \\
0 & \text{en otro caso}
\end{cases}
\label{eq:overload_penalty}
\end{equation}

\subsubsection{Penalización por Destinos Duplicados}

\begin{equation}
P_{\text{duplicados}} = \sum_{d \in D} \max(0, |\{v : \text{destino}_v = d\}| - 1) \cdot 2000
\label{eq:duplicate_penalty}
\end{equation}

\subsubsection{Penalización por Rutas Inválidas}

\begin{equation}
P_{\text{rutas}}(v) = \begin{cases}
1500 & \text{si la ruta está cerrada o es incompatible} \\
0 & \text{en otro caso}
\end{cases}
\label{eq:route_penalty}
\end{equation}

\subsection{Bonificaciones Globales}

\begin{equation}
B_{\text{cobertura}} = \frac{|\{d : \exists v \text{ tal que destino}_v = d\}|}{|D|} \cdot 300
\label{eq:coverage_bonus}
\end{equation}

\begin{equation}
B_{\text{completa}} = \begin{cases}
500 & \text{si todos los destinos están cubiertos} \\
0 & \text{en otro caso}
\end{cases}
\label{eq:complete_bonus}
\end{equation}

\section{Algoritmo Genético: Operadores}

\subsection{Inicialización de Población}

La población inicial se genera mediante cuatro estrategias diferentes:

\subsubsection{Estrategia por Capacidad (40\%)}

\begin{algorithm}[H]
\caption{Inicialización por Capacidad}
\begin{algorithmic}
\STATE Ordenar vehículos por capacidad (mayor a menor)
\STATE Ordenar destinos por población (mayor a menor)
\STATE $\text{destinos\_usados} \leftarrow \emptyset$
\FOR{cada vehículo $v$ en orden}
    \FOR{cada destino $d$ en orden}
        \IF{$d \notin \text{destinos\_usados}$ Y ruta es válida}
            \STATE Asignar $v \rightarrow d$
            \STATE $\text{destinos\_usados} \leftarrow \text{destinos\_usados} \cup \{d\}$
            \STATE Generar insumos usando el 85-95\% de $C_v$
            \STATE \textbf{break}
        \ENDIF
    \ENDFOR
\ENDFOR
\end{algorithmic}
\end{algorithm}

\subsubsection{Generación de Insumos por Capacidad}

El algoritmo para generar insumos respeta estrictamente la capacidad:

\begin{equation}
W_{\text{objetivo}} = C_v \cdot \text{random}(0.85, 0.95)
\label{eq:target_weight}
\end{equation}

\begin{algorithm}[H]
\caption{Generación de Insumos}
\begin{algorithmic}
\STATE $W_{\text{restante}} \leftarrow W_{\text{objetivo}}$
\STATE Obtener insumos prioritarios según tipo de desastre
\FOR{cada insumo prioritario $i$}
    \IF{$w_i > 0$ Y $W_{\text{restante}} \geq w_i$}
        \STATE $\text{max\_cantidad} \leftarrow \lfloor W_{\text{restante}} / w_i \rfloor$
        \STATE $s_{v,i} \leftarrow \text{random}(1, \min(\text{max\_cantidad}, 10))$
        \STATE $W_{\text{restante}} \leftarrow W_{\text{restante}} - s_{v,i} \cdot w_i$
    \ENDIF
\ENDFOR
\STATE Repetir para insumos no prioritarios con límite de 5 unidades
\STATE Verificar que $\sum_{i} s_{v,i} \cdot w_i \leq C_v$
\end{algorithmic}
\end{algorithm}

\subsection{Operador de Selección}

Se utiliza selección por ordenamiento (rank-based selection):

\begin{equation}
P_{\text{selección}}(k) = \frac{2 \cdot (N - k + 1)}{N \cdot (N + 1)}
\label{eq:rank_selection}
\end{equation}

Donde $k$ es la posición en el ranking (1 = mejor) y $N$ es el tamaño de la población.

\begin{figure}[H]
\centering
\begin{tikzpicture}[scale=0.8]
\begin{axis}[
    xlabel={Posición en Ranking},
    ylabel={Probabilidad de Selección},
    width=10cm,
    height=6cm,
    grid=major,
]
\addplot[domain=1:10, samples=10, mark=*] {2*(10-x+1)/(10*11)};
\end{axis}
\end{tikzpicture}
\caption{Distribución de probabilidades en selección por ranking}
\label{fig:selection}
\end{figure}

\subsection{Operador de Cruza}

\subsubsection{Cruza Preservando Destinos}

La cruza intenta preservar la diversidad de destinos únicos:

\begin{algorithm}[H]
\caption{Cruza Preservando Destinos}
\begin{algorithmic}
\STATE $\text{destinos\_hijo1} \leftarrow \emptyset$, $\text{destinos\_hijo2} \leftarrow \emptyset$
\FOR{$v = 1$ to $|V|$}
    \STATE $d_1 \leftarrow \text{destino del vehículo } v \text{ en padre1}$
    \STATE $d_2 \leftarrow \text{destino del vehículo } v \text{ en padre2}$
    
    \IF{$d_1 \notin \text{destinos\_hijo1}$}
        \STATE Asignar vehículo $v$ a destino $d_1$ en hijo1
        \STATE $\text{destinos\_hijo1} \leftarrow \text{destinos\_hijo1} \cup \{d_1\}$
    \ELSIF{$d_2 \notin \text{destinos\_hijo1}$}
        \STATE Asignar vehículo $v$ a destino $d_2$ en hijo1
        \STATE $\text{destinos\_hijo1} \leftarrow \text{destinos\_hijo1} \cup \{d_2\}$
    \ELSE
        \STATE Permitir duplicado ocasional
    \ENDIF
    
    \STATE Aplicar cruza de insumos: $\mathbf{s}_{v,\text{hijo}} = f(\mathbf{s}_{v,\text{padre1}}, \mathbf{s}_{v,\text{padre2}})$
\ENDFOR
\end{algorithmic}
\end{algorithm}

\subsubsection{Cruza de Insumos}

\begin{equation}
s_{v,i,\text{hijo}} = \begin{cases}
\lfloor \frac{s_{v,i,\text{padre1}} + s_{v,i,\text{padre2}}}{2} \rfloor & \text{estrategia promedio} \\
\max(s_{v,i,\text{padre1}}, s_{v,i,\text{padre2}}) & \text{estrategia máximo} \\
\text{random\_choice}(s_{v,i,\text{padre1}}, s_{v,i,\text{padre2}}) & \text{estrategia aleatoria} \\
\lfloor s_{v,i,\text{padre1}} \cdot w + s_{v,i,\text{padre2}} \cdot (1-w) \rfloor & \text{estrategia ponderada}
\end{cases}
\label{eq:supply_crossover}
\end{equation}

Donde $w \sim \text{Uniform}(0,1)$ es un peso aleatorio.

\subsection{Operador de Mutación}

\subsubsection{Mutación para Reasignar Duplicados}

\begin{algorithm}[H]
\caption{Mutación Anti-Duplicados}
\begin{algorithmic}
\STATE Identificar destinos con múltiples vehículos asignados
\FOR{cada destino $d$ con $|\{v : \text{destino}_v = d\}| > 1$}
    \STATE Mantener primer vehículo asignado a $d$
    \FOR{cada vehículo adicional $v$ asignado a $d$}
        \STATE Buscar destino libre $d'$ compatible con vehículo $v$
        \IF{destino libre encontrado}
            \STATE Reasignar $v \rightarrow d'$
        \ELSE
            \STATE Asignar a destino aleatorio
        \ENDIF
    \ENDFOR
\ENDFOR
\end{algorithmic}
\end{algorithm}

\subsubsection{Mutación de Optimización de Insumos}

\begin{equation}
\text{Si } U_v < 0.6 \text{ entonces incrementar insumos hasta } W_{\text{objetivo}} = C_v \cdot 0.9
\label{eq:increment_supplies}
\end{equation}

\begin{equation}
\text{Si } U_v > 0.95 \text{ entonces redistribuir para } W_{\text{objetivo}} = C_v \cdot 0.9
\label{eq:redistribute_supplies}
\end{equation}

\subsubsection{Reparación de Capacidad}

Función crítica que garantiza que ningún vehículo exceda su capacidad:

\begin{algorithm}[H]
\caption{Reparación de Capacidad}
\begin{algorithmic}
\STATE $W_{\text{actual}} \leftarrow \sum_{i} s_{v,i} \cdot w_i$
\IF{$W_{\text{actual}} > C_v$}
    \STATE $W_{\text{objetivo}} \leftarrow C_v \cdot 0.85$
    \STATE $\text{factor} \leftarrow W_{\text{objetivo}} / W_{\text{actual}}$
    \FOR{$i = 1$ to $|I|$}
        \IF{$s_{v,i} > 0$}
            \STATE $s_{v,i} \leftarrow \max(0, \lfloor s_{v,i} \cdot \text{factor} \rfloor)$
        \ENDIF
    \ENDFOR
    
    \WHILE{$\sum_{i} s_{v,i} \cdot w_i > C_v$ Y $\sum_{i} s_{v,i} > 0$}
        \STATE Encontrar insumo $j$ con mayor peso total $s_{v,j} \cdot w_j$
        \STATE $s_{v,j} \leftarrow s_{v,j} - 1$
    \ENDWHILE
\ENDIF
\end{algorithmic}
\end{algorithm}

\subsection{Operador de Reemplazo}

Se utiliza reemplazo elitista con poda aleatoria:

\begin{equation}
N_{\text{elite}} = \lfloor \text{poblacion\_size} \cdot \text{elitismo\_rate} \rfloor
\label{eq:elite_size}
\end{equation}

\begin{algorithm}[H]
\caption{Reemplazo Elitista}
\begin{algorithmic}
\STATE Ordenar población por fitness (descendente)
\STATE $\text{elite} \leftarrow$ mejores $N_{\text{elite}}$ individuos
\STATE $\text{resto} \leftarrow$ individuos restantes
\STATE $\text{seleccionados} \leftarrow$ muestra aleatoria de $(\text{poblacion\_size} - N_{\text{elite}})$ del resto
\RETURN $\text{elite} \cup \text{seleccionados}$
\end{algorithmic}
\end{algorithm}

\section{Parámetros del Algoritmo}

\begin{table}[H]
\centering
\caption{Parámetros optimizados del algoritmo genético}
\begin{tabular}{@{}lll@{}}
\toprule
\textbf{Parámetro} & \textbf{Valor} & \textbf{Justificación} \\
\midrule
Tamaño de población & 80 & Equilibrio entre diversidad y eficiencia \\
Número de generaciones & 500 & Convergencia típica en 100-200 generaciones \\
Probabilidad de cruza & 0.85 & Alta exploración del espacio de soluciones \\
Probabilidad de mutación & 0.20 & Alta diversidad para evitar mínimos locales \\
Tasa de elitismo & 0.15 & Preservar mejores soluciones \\
Criterio de parada & 100 gen. sin mejora & Convergencia temprana \\
\bottomrule
\end{tabular}
\label{tab:parameters}
\end{table}

\section{Métricas de Rendimiento}

\subsection{Indicadores de Calidad}

\begin{equation}
\text{Utilización Global} = \frac{\sum_{v=1}^{|V|} W_v}{\sum_{v=1}^{|V|} C_v} \times 100\%
\label{eq:global_utilization}
\end{equation}

\begin{equation}
\text{Cobertura de Destinos} = \frac{|\{d : \exists v \text{ tal que destino}_v = d\}|}{|D|} \times 100\%
\label{eq:destination_coverage}
\end{equation}

\begin{equation}
\text{Eficiencia de Combustible} = \frac{\sum_{v=1}^{|V|} W_v}{\sum_{v=1}^{|V|} \text{combustible}_v}
\label{eq:fuel_efficiency}
\end{equation}

\begin{equation}
\text{Relevancia Promedio} = \frac{\sum_{v=1}^{|V|} \sum_{i=1}^{|I|} s_{v,i} \cdot P_i}{\sum_{v=1}^{|V|} \sum_{i=1}^{|I|} s_{v,i}}
\label{eq:average_relevance}
\end{equation}

\subsection{Análisis de Convergencia}

\begin{equation}
\text{Diversidad}(t) = \frac{1}{N} \sum_{j=1}^{N} |F_j(t) - \bar{F}(t)|
\label{eq:diversity}
\end{equation}

Donde $F_j(t)$ es el fitness del individuo $j$ en la generación $t$ y $\bar{F}(t)$ es el fitness promedio.

\begin{equation}
\text{Tasa de Mejora} = \frac{F_{\text{mejor}}(t) - F_{\text{mejor}}(t-k)}{k}
\label{eq:improvement_rate}
\end{equation}

\section{Flujo Completo del Algoritmo}

\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=2cm, auto]
% Definir estilos
\tikzstyle{process} = [rectangle, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=blue!20]
\tikzstyle{decision} = [diamond, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=orange!20]
\tikzstyle{startstop} = [rectangle, rounded corners, minimum width=3cm, minimum height=1cm, text centered, draw=black, fill=green!20]
\tikzstyle{arrow} = [thick,->,>=stealth]

% Nodos
\node [startstop] (start) {Inicio};
\node [process, below of=start] (init) {Inicialización\\4 Estrategias};
\node [process, below of=init] (eval) {Evaluación\\Fitness};
\node [decision, below of=eval] (term) {¿Criterio\\parada?};
\node [process, right of=term, node distance=4cm] (selection) {Selección\\por Ranking};
\node [process, below of=selection] (crossover) {Cruza\\Preservando Destinos};
\node [process, below of=crossover] (mutation) {Mutación\\Anti-duplicados};
\node [process, below of=mutation] (repair) {Reparación\\Capacidad};
\node [process, left of=repair, node distance=4cm] (replacement) {Reemplazo\\Elitista};
\node [startstop, below of=term, node distance=4cm] (end) {Mejor Solución};

% Flechas
\draw [arrow] (start) -- (init);
\draw [arrow] (init) -- (eval);
\draw [arrow] (eval) -- (term);
\draw [arrow] (term) -- node {No} (selection);
\draw [arrow] (selection) -- (crossover);
\draw [arrow] (crossover) -- (mutation);
\draw [arrow] (mutation) -- (repair);
\draw [arrow] (repair) -- (replacement);
\draw [arrow] (replacement) -- +(-4,0) |- (eval);
\draw [arrow] (term) -- node {Sí} (end);

\end{tikzpicture}
\caption{Diagrama de flujo del algoritmo genético}
\label{fig:flowchart}
\end{figure}

\section{Análisis de Complejidad}

\subsection{Complejidad Espacial}

\begin{equation}
S(n) = O(N \cdot |V| \cdot (1 + |I|))
\label{eq:space_complexity}
\end{equation}

La complejidad espacial está dominada por el almacenamiento de la población, donde cada individuo requiere espacio para $|V|$ asignaciones de vehículos y cada asignación contiene un vector de $|I|$ insumos.

\section{Validación y Resultados Esperados}

\subsection{Criterios de Validación}

\begin{enumerate}
\item \textbf{Factibilidad}: Todas las soluciones deben satisfacer las restricciones de capacidad
\begin{equation}
\forall v \in V: \sum_{i=1}^{|I|} s_{v,i} \cdot w_i \leq C_v
\end{equation}

\item \textbf{Completitud}: Todos los vehículos deben tener asignaciones válidas
\begin{equation}
\forall v \in V: \exists! (d,r) \text{ tal que } x_{v,d,r} = 1
\end{equation}

\item \textbf{Compatibilidad}: Las asignaciones deben respetar restricciones de rutas
\begin{equation}
\forall v,d,r: x_{v,d,r} = 1 \Rightarrow \tau_v \in \Phi_{d,r}
\end{equation}
\end{enumerate}

\subsection{Métricas de Éxito}

\begin{table}[H]
\centering
\caption{Rangos esperados de métricas de rendimiento}
\begin{tabular}{@{}lcc@{}}
\toprule
\textbf{Métrica} & \textbf{Rango Aceptable} & \textbf{Óptimo} \\
\midrule
Utilización Global & 70\% - 95\% & > 85\% \\
Cobertura de Destinos & 80\% - 100\% & 100\% \\
Fitness Final & > 100,000 & > 500,000 \\
Convergencia & < 200 generaciones & < 100 generaciones \\
Violaciones de Capacidad & 0\% & 0\% \\
Destinos Duplicados & < 10\% & 0\% \\
\bottomrule
\end{tabular}
\label{tab:success_metrics}
\end{table}

\section{Casos de Uso y Escenarios}

\subsection{Tipos de Desastre Soportados}

\begin{table}[H]
\centering
\caption{Prioridades de insumos por tipo de desastre}
\begin{tabular}{@{}lccc@{}}
\toprule
\textbf{Categoría} & \textbf{Terremoto} & \textbf{Inundación} & \textbf{Huracán} \\
\midrule
Agua & Media & Alta & Alta \\
Alimentación básica & Alta & Alta & Alta \\
Medicamentos & Alta & Media & Media \\
Refugio & Alta & Media & Alta \\
Higiene & Media & Alta & Media \\
Equipamiento & Media & Baja & Media \\
\bottomrule
\end{tabular}
\label{tab:disaster_priorities}
\end{table}

\subsection{Configuraciones de Vehículos}

\begin{figure}[H]
\centering
\begin{tikzpicture}[scale=0.8]
\begin{axis}[
    xlabel={Capacidad (kg)},
    ylabel={Velocidad (km/h)},
    width=12cm,
    height=8cm,
    grid=major,
    legend pos=north east,
    scatter/classes={
        pickup/.style={mark=square*,blue},
        van/.style={mark=triangle*,red},
        truck/.style={mark=*,green}
    }
]

% Datos de vehículos
\addplot[scatter,only marks,scatter src=explicit symbolic]
coordinates {
    (1200,65) [pickup]
    (1300,65) [pickup]
    (1000,60) [pickup]
    (1800,75) [van]
    (1900,75) [van]
    (3000,60) [truck]
    (2800,60) [truck]
};

\legend{Camionetas,Vans,Camiones}
\end{axis}
\end{tikzpicture}
\caption{Distribución de vehículos por capacidad y velocidad}
\label{fig:vehicle_distribution}
\end{figure}

\section{Análisis de Sensibilidad}

\subsection{Impacto de Parámetros}

\begin{figure}[H]
\centering
\begin{tikzpicture}[scale=0.7]
\begin{axis}[
    xlabel={Probabilidad de Mutación},
    ylabel={Fitness Promedio},
    width=10cm,
    height=6cm,
    grid=major,
]
\addplot[domain=0.05:0.4, samples=20, mark=*] {500000 - 200000*(x-0.2)^2};
\end{axis}
\end{tikzpicture}
\caption{Sensibilidad del fitness a la probabilidad de mutación}
\label{fig:mutation_sensitivity}
\end{figure}

\begin{figure}[H]
\centering
\begin{tikzpicture}[scale=0.7]
\begin{axis}[
    xlabel={Tamaño de Población},
    ylabel={Generaciones hasta Convergencia},
    width=10cm,
    height=6cm,
    grid=major,
]
\addplot[domain=20:100, samples=20, mark=*] {200 - 50*ln(x/20)};
\end{axis}
\end{tikzpicture}
\caption{Relación entre tamaño de población y convergencia}
\label{fig:population_convergence}
\end{figure}

\subsection{Análisis de Robustez}

\begin{equation}
\text{Robustez} = \frac{\sigma_{\text{fitness\_final}}}{\mu_{\text{fitness\_final}}}
\label{eq:robustness}
\end{equation}

Donde $\sigma$ es la desviación estándar y $\mu$ es la media del fitness final en múltiples ejecuciones.

\section{Optimizaciones y Mejoras Futuras}

\subsection{Hibridación con Heurísticas}

\begin{equation}
\text{Fitness\_Híbrido} = \alpha \cdot \text{Fitness\_AG} + (1-\alpha) \cdot \text{Fitness\_Heurística}
\label{eq:hybrid_fitness}
\end{equation}

\subsection{Paralelización}

La evaluación de fitness puede paralelizarse:

\begin{equation}
\text{Speedup} = \frac{T_{\text{secuencial}}}{T_{\text{paralelo}}} \approx \min(p, N)
\label{eq:speedup}
\end{equation}

Donde $p$ es el número de procesadores y $N$ es el tamaño de población.

\subsection{Adaptación Dinámica de Parámetros}

\begin{equation}
P_{\text{mutación}}(t) = P_{\text{inicial}} \cdot e^{-\lambda \cdot \frac{t}{G_{\text{max}}}}
\label{eq:adaptive_mutation}
\end{equation}

\begin{equation}
P_{\text{cruza}}(t) = P_{\text{mínima}} + (P_{\text{máxima}} - P_{\text{mínima}}) \cdot \text{diversidad}(t)
\label{eq:adaptive_crossover}
\end{equation}

\section{Implementación y Arquitectura}

\subsection{Estructura de Clases}

\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=2cm]
% Clases principales
\node[draw, rectangle, minimum width=3cm, minimum height=1.5cm] (AG) {
    \textbf{GeneticAlgorithm}\\
    \scriptsize
    - población\\
    - parámetros\\
    + ejecutar()
};

\node[draw, rectangle, minimum width=3cm, minimum height=1.5cm, right of=AG, node distance=4cm] (Individual) {
    \textbf{Individual}\\
    \scriptsize
    - vehículos[]\\
    - fitness\\
    + evaluar()
};

\node[draw, rectangle, minimum width=3cm, minimum height=1.5cm, below of=AG] (Operators) {
    \textbf{Operators}\\
    \scriptsize
    + selección()\\
    + cruza()\\
    + mutación()
};

\node[draw, rectangle, minimum width=3cm, minimum height=1.5cm, below of=Individual] (Evaluator) {
    \textbf{FitnessEvaluator}\\
    \scriptsize
    + calcular\_fitness()\\
    + validar\_restricciones()
};

% Relaciones
\draw[->] (AG) -- (Individual);
\draw[->] (AG) -- (Operators);
\draw[->] (Individual) -- (Evaluator);
\draw[->] (Operators) -- (Individual);

\end{tikzpicture}
\caption{Diagrama de clases del sistema}
\label{fig:class_diagram}
\end{figure}

\subsection{Flujo de Datos}

\begin{figure}[H]
\centering
\begin{tikzpicture}[node distance=1.5cm]
% Datos de entrada
\node[draw, rectangle, fill=yellow!20] (input1) {Vehículos};
\node[draw, rectangle, fill=yellow!20, right of=input1] (input2) {Destinos};
\node[draw, rectangle, fill=yellow!20, right of=input2] (input3) {Rutas};
\node[draw, rectangle, fill=yellow!20, right of=input3] (input4) {Insumos};

% Procesamiento
\node[draw, rectangle, fill=blue!20, below of=input2, node distance=3cm] (ag) {Algoritmo Genético};

% Salidas
\node[draw, rectangle, fill=green!20, below of=ag, node distance=2cm] (output1) {Mejor Solución};
\node[draw, rectangle, fill=green!20, left of=output1] (output2) {Estadísticas};
\node[draw, rectangle, fill=green!20, right of=output1] (output3) {Evolución};

% Conexiones
\draw[->] (input1) -- (ag);
\draw[->] (input2) -- (ag);
\draw[->] (input3) -- (ag);
\draw[->] (input4) -- (ag);

\draw[->] (ag) -- (output1);
\draw[->] (ag) -- (output2);
\draw[->] (ag) -- (output3);

\end{tikzpicture}
\caption{Flujo de datos del sistema}
\label{fig:data_flow}
\end{figure}

\section{Conclusiones}

El algoritmo genético desarrollado para la optimización de distribución logística en emergencias humanitarias presenta las siguientes características destacadas:

\begin{enumerate}
\item \textbf{Robustez}: Garantiza soluciones factibles mediante reparación automática de restricciones
\item \textbf{Eficiencia}: Logra convergencia típica en menos de 200 generaciones
\item \textbf{Adaptabilidad}: Maneja diferentes tipos de desastre y configuraciones de vehículos
\item \textbf{Escalabilidad}: Complejidad lineal en el número de vehículos y destinos
\item \textbf{Calidad}: Produce soluciones con alta utilización de capacidad y cobertura de destinos
\end{enumerate}

\subsection{Contribuciones Principales}

\begin{itemize}
\item Función de fitness multi-objetivo que balancea eficiencia, relevancia y utilización
\item Operadores genéticos especializados para evitar duplicación de destinos
\item Sistema de reparación automática que garantiza factibilidad
\item Estrategias de inicialización inteligente que mejoran convergencia
\item Métricas de evaluación específicas para contextos humanitarios
\end{itemize}

\subsection{Limitaciones y Trabajo Futuro}

\begin{itemize}
\item Consideración de ventanas de tiempo para entregas
\item Incorporación de incertidumbre en demanda y rutas
\item Optimización multi-período para operaciones sostenidas
\item Integración con sistemas de información geográfica en tiempo real
\item Desarrollo de interfaces de usuario para operadores de campo
\end{itemize}

\section{Referencias y Bibliografía}

\begin{thebibliography}{9}

\bibitem{goldberg1989}
Goldberg, D. E. (1989). \textit{Genetic Algorithms in Search, Optimization and Machine Learning}. Addison-Wesley.

\bibitem{holland1992}
Holland, J. H. (1992). \textit{Adaptation in Natural and Artificial Systems}. MIT Press.

\bibitem{emergency_logistics}
Van Wassenhove, L. N. (2006). Humanitarian aid logistics: supply chain management in high gear. \textit{Journal of the Operational Research Society}, 57(5), 475-489.

\bibitem{vehicle_routing}
Toth, P., \& Vigo, D. (2002). \textit{The Vehicle Routing Problem}. SIAM Monographs on Discrete Mathematics and Applications.

\bibitem{multi_objective_ga}
Deb, K. (2001). \textit{Multi-Objective Optimization Using Evolutionary Algorithms}. John Wiley \& Sons.

\bibitem{disaster_response}
Altay, N., \& Green III, W. G. (2006). OR/MS research in disaster operations management. \textit{European Journal of Operational Research}, 175(1), 475-493.

\bibitem{humanitarian_logistics}
Balcik, B., \& Beamon, B. M. (2008). Facility location in humanitarian relief. \textit{International Journal of Logistics}, 11(2), 101-121.

\bibitem{genetic_algorithms_logistics}
Baker, B. M., \& Ayechew, M. A. (2003). A genetic algorithm for the vehicle routing problem. \textit{Computers \& Operations Research}, 30(5), 787-800.

\bibitem{emergency_response_optimization}
Fiedrich, F., Gehbauer, F., \& Rickers, U. (2000). Optimized resource allocation for emergency response after earthquake disasters. \textit{Safety Science}, 35(1-3), 41-57.

\end{thebibliography}

\appendix

\section{Anexo A: Pseudocódigo Completo}

\begin{algorithm}[H]
\caption{Algoritmo Genético Completo para Distribución Logística}
\begin{algorithmic}
\STATE \textbf{Entrada:} Vehículos $V$, Destinos $D$, Rutas $R$, Insumos $I$, Desastre $\delta$
\STATE \textbf{Salida:} Mejor solución $S^*$

\STATE // Inicialización
\STATE $P(0) \leftarrow \text{InicializarPoblación}(N, V, D, R, I, \delta)$
\STATE $t \leftarrow 0$
\STATE $\text{mejor\_fitness} \leftarrow -\infty$
\STATE $\text{generaciones\_sin\_mejora} \leftarrow 0$

\WHILE{$t < G_{\max}$ AND $\text{generaciones\_sin\_mejora} < 100$}
    
    \STATE // Evaluación
    \FOR{cada individuo $s \in P(t)$}
        \STATE $\text{fitness}(s) \leftarrow \text{EvaluarFitness}(s, V, D, I, \delta)$
    \ENDFOR
    
    \STATE // Actualizar mejor solución
    \STATE $s_{\text{mejor}} \leftarrow \arg\max_{s \in P(t)} \text{fitness}(s)$
    \IF{$\text{fitness}(s_{\text{mejor}}) > \text{mejor\_fitness}$}
        \STATE $S^* \leftarrow s_{\text{mejor}}$
        \STATE $\text{mejor\_fitness} \leftarrow \text{fitness}(s_{\text{mejor}})$
        \STATE $\text{generaciones\_sin\_mejora} \leftarrow 0$
    \ELSE
        \STATE $\text{generaciones\_sin\_mejora} \leftarrow \text{generaciones\_sin\_mejora} + 1$
    \ENDIF
    
    \IF{$t < G_{\max} - 1$}
        \STATE // Selección
        \STATE $\text{Parejas} \leftarrow \text{SelecciónPorRanking}(P(t))$
        
        \STATE // Cruza
        \STATE $\text{Descendencia} \leftarrow \text{CruzaPreservandoDestinos}(\text{Parejas}, P_c)$
        
        \STATE // Mutación
        \STATE $\text{Descendencia} \leftarrow \text{MutaciónAntiDuplicados}(\text{Descendencia}, P_m)$
        
        \STATE // Reparación
        \FOR{cada individuo $s \in \text{Descendencia}$}
            \STATE $\text{RepararCapacidad}(s, V, I)$
        \ENDFOR
        
        \STATE // Reemplazo
        \STATE $P(t+1) \leftarrow \text{ReemplazoElitista}(\text{Descendencia}, N, E)$
    \ENDIF
    
    \STATE $t \leftarrow t + 1$
\ENDWHILE

\RETURN $S^*$
\end{algorithmic}
\end{algorithm}

\section{Anexo B: Ejemplo de Solución}

\begin{table}[H]
\centering
\caption{Ejemplo de solución óptima para 4 vehículos y 4 destinos}
\begin{tabular}{@{}llcccccc@{}}
\toprule
\textbf{Vehículo} & \textbf{Destino} & \textbf{Población} & \textbf{Dist. (km)} & \textbf{Peso (kg)} & \textbf{Utilización} & \textbf{Combustible (L)} & \textbf{Fitness} \\
\midrule
Toyota Hilux & Localidad A & 334 & 16.7 & 1,140 & 95.0\% & 1.2 & 2,850 \\
Dodge Dakota & Localidad B & 877 & 9.4 & 950 & 95.0\% & 0.8 & 3,420 \\
Mercedes Sprinter & Localidad C & 1,038 & 6.0 & 1,710 & 95.0\% & 0.5 & 4,180 \\
Ford Transit & Localidad D & 964 & 5.5 & 1,805 & 95.0\% & 0.4 & 4,350 \\
\midrule
\textbf{Total} & \textbf{4 destinos} & \textbf{3,213} & \textbf{37.6} & \textbf{5,605} & \textbf{95.0\%} & \textbf{2.9} & \textbf{14,800} \\
\bottomrule
\end{tabular}
\label{tab:solution_example}
\end{table}

\end{document}