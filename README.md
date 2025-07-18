
# 🚨 EmergenLogistics

**Sistema inteligente de distribución de ayuda humanitaria** utilizando algoritmos genéticos para optimización logística.

---

## 🔍 Características

- 🗺️ Generación automática de rutas usando OpenStreetMap + OSRM
- 🧬 Algoritmo genético para optimizar distribución de ayuda
- 💻 Interfaz web moderna con Leaflet y JS modular
- 🧱 Arquitectura limpia y modular para fácil mantenimiento y escalabilidad

---

## ⚙️ Instalación

### ✅ Requisitos

- Python 3.8+
- pip
- (opcional) Node.js si compilas assets personalizados

### 🔒 Crear entorno virtual

> Se recomienda usar un entorno virtual para evitar conflictos de dependencias globales:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
````

### 📦 Instalar dependencias

```bash
pip install -r requirements.txt
```

### ⚙️ Configurar variables de entorno

```bash
cp .env.example .env
# Edita el archivo .env con tus valores personalizados
```

### 🚀 Ejecutar aplicación en modo desarrollo

```bash
python main.py
```

La aplicación estará disponible en:
👉 [http://localhost:5000](http://localhost:5000)

---

## 🧱 Estructura del Proyecto

```
emergenclogistics/
├── app/                # Configuración y creación de la app Flask
├── core/               # Núcleo del sistema (AG, validaciones, excepciones)
├── services/           # Lógica de negocio (escenarios, distribución, rutas)
├── entities/           # Modelos de datos (vehículos, insumos, destinos)
├── utils/              # Helpers compartidos (formato, cálculos, config)
├── static/             # Archivos frontend: JS, CSS, imágenes
├── templates/          # HTML templates renderizados por Flask
├── logs/               # Archivos de log del sistema
└── main.py             # Entry point de la aplicación
```

---

## 🧩 Módulos Principales

### 1. 🌍 Generador de Mapas

* Selección de nodo base (estado o ciudad)
* Generación automática de destinos
* Cálculo de rutas con restricciones por tipo de vehículo
* Visualización en mapa (Leaflet + OpenStreetMap)

### 2. 🧬 Algoritmo Genético

* Configuración de escenarios (tipo de desastre, insumos, flota)
* Asignación y optimización de recursos
* Respeto a restricciones logísticas (peso, distancia, tipo de vehículo)
* Exportación de resultados (PDF, JSON)

---

## 📡 API REST

| Método | Endpoint                        | Descripción                                               |
| ------ | ------------------------------- | --------------------------------------------------------- |
| POST   | `/api/generate-complete-routes` | Generar rutas para todos los destinos                     |
| POST   | `/api/ag/create-scenario`       | Crear escenario de emergencia                             |
| POST   | `/api/ag/execute`               | Ejecutar algoritmo genético                               |
| GET    | `/api/entities/{type}`          | Obtener datos de entidades (`vehicles`, `supplies`, etc.) |
| GET    | `/api/status`                   | Verificar estado del servidor                             |

---

## 🧠 Arquitectura

### Backend (Python + Flask)

* `app/`: Factory pattern, configuración y blueprints
* `core/`: Motor AG, validaciones y excepciones personalizadas
* `services/`: Lógica de negocio modular y casos de uso
* `utils/`: Funciones utilitarias, helpers y configuración global

### Frontend (JavaScript + HTML + CSS)

* Código modular por componente
* Carga dinámica de templates
* Comunicación entre módulos con EventBus
* Cache local de respuestas y plantillas
* Estilos reutilizables y diseño responsive

---

## 🧪 Desarrollo y Testing

### 📋 Logs

Los logs se almacenan en:

```
logs/app.log
```

Se rota automáticamente por tamaño.

### 🚦 Ejecutar pruebas

```bash
pytest tests/
```

### 🎨 Lint y Formato

```bash
black . && flake8 .
```

---

## 🚀 Despliegue en Producción

1. Configurar `.env`:

```env
DEBUG=False
LOG_LEVEL=ERROR
SECRET_KEY=una-clave-segura
```

2. Ejecutar con Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

3. (Opcional) Usar `systemd`, `supervisor` o `docker` para producción persistente.

---

## 🤝 Contribuciones

¡Son bienvenidas! Sigue estos pasos:

1. Haz un fork del repositorio
2. Crea una nueva rama:

   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. Haz tus cambios y commitea:

   ```bash
   git commit -am "Agregar nueva funcionalidad"
   ```
4. Haz push a tu rama:

   ```bash
   git push origin feature/nueva-funcionalidad
   ```
5. Abre un Pull Request describiendo tu cambio

---

## 📄 Licencia

MIT License — consulta el archivo `LICENSE` para más detalles.

