# ✈️ Travel Pro AI - Agente de Planificación de Vacaciones

> Tu asistente personal impulsado por IA para planificar el viaje perfecto

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![LangChain](https://img.shields.io/badge/LangChain-0.3-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-red)

## 🌟 Características Principales

Travel Pro AI es un agente inteligente que te ayuda a planificar vacaciones de principio a fin:

### 👥 Gestión de Viajeros
- Registra adultos, niños y bebés
- Clasificación automática por edad
- Cálculo de precios diferenciados

### ✈️ Búsqueda de Vuelos
- **API Real**: Integración con Amadeus API (opcional)
- **Precios Reales**: Datos actualizados de 400+ aerolíneas
- **Fallback Inteligente**: Datos simulados si no hay API configurada
- Soporte para viajes de ida y vuelta
- Cálculo automático para grupos
- Información de escalas y duración

### 🌍 Información de Destinos
- Integración con Wikipedia
- Datos de clima en tiempo real
- Información de población y geografía

### 🗓️ Recomendaciones por Temporada
- Actividades según el clima
- Consejos de viaje personalizados
- Adaptación hemisferio norte/sur

### 📅 Generador de Itinerarios
- Planes día a día personalizados
- 3 niveles de presupuesto: económico, medio, lujo
- Estimación de gastos diarios
- Actividades adaptadas al perfil del viajero

### 💰 Calculadora de Presupuesto
- Desglose completo de costos
- Incluye vuelos, alojamiento, comidas, actividades
- Cálculo por persona y total del grupo
- Descuentos automáticos para niños y bebés

## 🚀 Instalación

### Requisitos Previos
- Python 3.11 o superior
- Cuenta OpenAI con API Key

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd ia-assistant-pro
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**

En Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

En Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**

Crea un archivo `.env` en la raíz del proyecto:

```env
# Configuración OpenAI (OBLIGATORIO)
OPENAI_API_KEY=tu-api-key-aqui
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
THREAD_ID=travel001

# Amadeus API (OPCIONAL - para vuelos reales)
# AMADEUS_API_KEY=tu_api_key_aqui
# AMADEUS_API_SECRET=tu_api_secret_aqui
```

### 🎯 Configuración Avanzada: Amadeus API (Opcional)

Para obtener **precios reales de vuelos**, puedes configurar Amadeus API:

1. **Regístrate gratis** en: https://developers.amadeus.com/register
2. **Crea una app** y obtén tus credenciales (API Key + Secret)
3. **Agrégalas** a tu archivo `.env`
4. Lee la guía completa en: [`AMADEUS_SETUP.md`](AMADEUS_SETUP.md)

**Beneficios**:
- ✅ 2,000 búsquedas gratis/mes
- ✅ Precios reales de 400+ aerolíneas
- ✅ Horarios y escalas actualizadas

**Sin Amadeus API**: El sistema usa datos simulados realistas automáticamente.

## 🎮 Uso

### Iniciar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8502`

### Ejemplos de Uso

#### 1. **Planificar un viaje familiar**
```
Usuario: "Quiero planear vacaciones a Cancún para 2 adultos y 1 niño de 8 años"
```

#### 2. **Buscar vuelos**
```
Usuario: "Busca vuelos de Lima a Madrid del 15 de diciembre al 22 de diciembre"
```

#### 3. **Obtener información del destino**
```
Usuario: "Cuéntame sobre París"
```

#### 4. **Generar itinerario**
```
Usuario: "Genera un itinerario de 7 días en Barcelona con presupuesto medio"
```

#### 5. **Calcular presupuesto total**
```
Usuario: "Calcula el presupuesto total para 5 días en Roma, nivel lujo"
```

## 🛠️ Tecnologías Utilizadas

- **LangChain 0.3**: Framework para aplicaciones con LLM
- **LangGraph 0.2**: Orquestación de agentes
- **OpenAI GPT-4o-mini**: Modelo de lenguaje
- **Streamlit 1.41**: Interfaz web interactiva
- **Python 3.11**: Lenguaje de programación
- **Wikipedia API**: Información de destinos
- **Open-Meteo API**: Datos meteorológicos

## 📁 Estructura del Proyecto

```
ia-assistant-pro/
│
├── app.py                 # Interfaz web con Streamlit
├── asistente.py          # Lógica del agente y herramientas
├── requirements.txt      # Dependencias Python
├── .env                  # Variables de entorno (no incluido)
├── env.example          # Ejemplo de configuración
│
├── README.md            # Este archivo
├── GUIA_RAPIDA.md       # Guía rápida de uso
└── ESTRUCTURA.txt       # Documentación técnica
```

## 🎯 Herramientas del Agente

El agente cuenta con 6 herramientas especializadas:

1. **gestionar_viajeros**: Administra la lista de viajeros
2. **buscar_vuelos**: Encuentra opciones de vuelos
3. **info_destino**: Proporciona información de ciudades
4. **recomendaciones_temporada**: Sugiere actividades por época
5. **generar_itinerario**: Crea planes día a día
6. **calcular_presupuesto**: Estima costos totales

## 🎨 Interfaz de Usuario

- **Diseño moderno**: Gradientes y animaciones CSS
- **Tema oscuro optimizado**: Para mejor experiencia visual
- **Responsive**: Adaptable a diferentes tamaños de pantalla
- **Sidebar informativo**: Estadísticas y ejemplos rápidos
- **Chat interactivo**: Conversación natural con el agente

## 🔐 Seguridad

- Las API keys se almacenan en variables de entorno
- El archivo `.env` está excluido del control de versiones
- Validación de inputs para prevenir inyecciones

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Autor

Desarrollado con ❤️ usando LangChain y Streamlit

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa la documentación en `GUIA_RAPIDA.md`
2. Verifica que tu `.env` esté configurado correctamente
3. Asegúrate de tener todas las dependencias instaladas

## 🔄 Actualizaciones

### Versión 3.0 (Actual)
- ✨ Transformación completa a agente de viajes
- 🎨 Nueva interfaz Travel Pro AI
- 🛠️ 6 herramientas especializadas en planificación de vacaciones
- 💰 Sistema avanzado de presupuestos
- 📅 Generador de itinerarios personalizados

---

**¡Felices viajes! ✈️🌴**

