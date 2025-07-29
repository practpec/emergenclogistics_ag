# EmergenLogistics

Sistema inteligente de distribución de ayuda humanitaria utilizando algoritmos genéticos para optimización logística y datos geográficos del INEGI.

## Características

- Generación automática de mapas y rutas usando OpenStreetMap + OSRM
- Sistema de creación de escenarios de emergencia configurable
- Base de datos de localidades reales mexicanas (INEGI)
- Interfaz web moderna con visualización de mapas
- Arquitectura modular backend/frontend

## Instalación

### Requisitos

- Python 3.8+
- pip

### Configuración del entorno

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con valores personalizados
```

### Ejecutar aplicación

```bash
python main.py
```

La aplicación estará disponible en: http://localhost:5000

## Estructura del Proyecto

```
emergenclogistics/
├── back/                   # Backend Flask
│   ├── app/               # Configuración Flask
│   ├── core/              # Núcleo del sistema (validaciones, excepciones)
|   ├── data/                  # Base de datos de localidades INEGI
│   ├── services/          # Lógica de negocio (escenarios, distribución, rutas)
│   ├── entities/          # Modelos de datos y entidades
│   ├── utils/             # Helpers y configuración
│   └── main.py           # Entry point
├── front/                 # Frontend React + Vite
├── docs/                  # Documentación técnica
└── logs/                  # Archivos de log
```

## Módulos Principales

### 1. Generador de Mapas
- Selección de nodo base (estado/municipio)
- Generación automática de destinos usando datos INEGI
- Cálculo de rutas con OpenStreetMap/OSRM
- Visualización interactiva con Leaflet

### 2. Sistema de Escenarios
- Configuración de tipos de desastre
- Selección de vehículos disponibles
- Definición de insumos necesarios
- Gestión de rutas y estados

### 3. Frontend (En desarrollo)
- Visualización de mapas y rutas
- Interfaz de configuración de escenarios
- Panel de resultados y estadísticas

## Base de Datos de Localidades

El sistema utiliza la base de datos oficial del INEGI con más de 170,000 localidades mexicanas. Para información detallada, consulta la [documentación de datos INEGI](./docs/datos-inegi.md).

## API REST

| Método | Endpoint                        | Descripción                           |
|--------|---------------------------------|---------------------------------------|
| POST   | `/api/generate-complete-routes` | Generar mapa y rutas                 |
| POST   | `/api/ag/create-scenario`       | Crear escenario de emergencia        |
| GET    | `/api/entities/{type}`          | Obtener datos de entidades           |
| GET    | `/api/status`                   | Estado del servidor                  |

## Arquitectura

### Backend (Python + Flask)
- Patrón factory para configuración Flask
- Servicios modulares para lógica de negocio
- Modelos de datos con dataclasses
- Sistema de logging estructurado

### Frontend (React + Vite)
- Componentes modulares
- Hooks personalizados para lógica
- Gestión de estado con Context API
- Comunicación con API REST

## Desarrollo

### Logs
Los logs se almacenan en `logs/app.log` con rotación automática.

### Testing
```bash
pytest tests/
```

### Formato de código
```bash
black . && flake8 .
```

## Despliegue en Producción

1. Configurar variables de entorno:
```env
DEBUG=False
LOG_LEVEL=ERROR
SECRET_KEY=clave-segura-produccion
```

2. Ejecutar con Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## Documentación Técnica

Para información detallada sobre:
- [Datos del INEGI](./docs/datos-inegi.md)
- [Algoritmos y fórmulas](./docs/algoritmos.md)
- [Estructura de entidades](./docs/entidades.md)
- [API y endpoints](./docs/api.md)

## Estado del Proyecto

### Completo
- Generación de mapas y rutas
- Creación de escenarios de emergencia
- Base de datos de localidades INEGI
- API REST backend

### En desarrollo
- Algoritmo genético de optimización
- Visualización completa de resultados frontend
- Sistema de reportes

## Contribuciones

1. Fork del repositorio
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am "Agregar nueva funcionalidad"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Licencia

MIT License - consulta el archivo `LICENSE` para más detalles.







