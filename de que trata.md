# DormiGuard UGB
### Sistema Inteligente de Monitoreo de Postura y Fatiga para Estudiantes de Sistemas

**BAKENDVIEW** es una aplicación desarrollada en Python que utiliza visión artificial para monitorear en tiempo real la postura y los signos de fatiga de estudiantes que pasan largas horas frente a la computadora. El sistema analiza la imagen de la cámara web, detecta malas posturas y cabeceos por somnolencia, emite alertas sutiles y genera reportes diarios con estadísticas.

---

## Características principales

- Detección en tiempo real de postura (espalda encorvada y cabeza inclinada)
- Detección de signos de somnolencia (cabeceo)
- Alertas visuales y sonoras configurables
- Contador de tiempo frente a la pantalla
- Registro histórico de sesiones
- Generación de reporte diario con gráficos
- Interfaz sencilla e intuitiva

---

## Tecnologías utilizadas

| Tecnología       | Justificación |
|------------------|---------------|
| **Python 3.10+** | Lenguaje principal del proyecto |
| **OpenCV**       | Captura y procesamiento de video de la cámara |
| **MediaPipe**    | Detección precisa de puntos corporales y faciales (pose y face mesh) |
| **NumPy**        | Cálculos numéricos para ángulos y posiciones |
| **Pandas**       | Manejo y análisis de datos históricos |
| **Matplotlib / Plotly** | Generación de gráficos para los reportes |
| **SQLite**       | Almacenamiento local de sesiones y estadísticas |
| **Streamlit**    | Interfaz gráfica moderna y fácil de usar |
| **Pygame**       | Reproducción de alertas sonoras |

---

## Requisitos previos

- Python 3.10 o superior
- Cámara web funcional
- Sistema operativo: Windows, Linux o macOS
- Conexión a internet (solo para la instalación de dependencias)

---

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/DormiGuard-UGB.git
cd DormiGuard-UGB
```

2. Crea y activa un entorno virtual:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

---

## Cómo ejecutar la aplicación

Con el entorno virtual activado, ejecuta:

```bash
streamlit run main.py
```

La aplicación se abrirá automáticamente en tu navegador.

---

## Estructura del proyecto

```
BAKEND VIEW/
├── main.py                     # Punto de entrada de la aplicación
├── camera/
│   └── posture_detector.py     # Lógica de detección con MediaPipe y OpenCV
├── alerts/
│   └── alert_manager.py        # Manejo de alertas visuales y sonoras
├── data/
│   └── storage.py              # Gestión de base de datos SQLite
├── reports/
│   └── report_generator.py     # Generación de reportes y gráficos
├── ui/
│   └── interface.py            # Componentes de la interfaz
├── utils/
│   └── config.py               # Configuraciones generales
├── assets/                     # Sonidos e imágenes
├── requirements.txt
└── README.md
```

---

## Manual de usuario breve

1. Al abrir la aplicación, concede permiso para usar la cámara.
2. Siéntate en una posición normal frente a la cámara.
3. El sistema comenzará a analizar tu postura automáticamente.
4. Si detecta que llevas mucho tiempo encorvado o cabeceando, emitirá una alerta.
5. Al finalizar tu sesión, puedes generar el reporte del día desde el botón correspondiente.
6. Los reportes se guardan automáticamente y puedes consultar el historial.

**Recomendaciones de uso:**
- Usa buena iluminación.
- Mantén la cámara a la altura de los ojos aproximadamente.
- Evita fondos muy saturados para mejorar la precisión.

---

## Arquitectura y decisiones de diseño

El sistema sigue una arquitectura modular:

- **Capa de Captura y Detección** (`camera/`): Se encarga exclusivamente del procesamiento de video y la detección de puntos clave mediante MediaPipe.
- **Capa de Lógica de Alertas** (`alerts/`): Decide cuándo y cómo emitir las notificaciones, separando esta responsabilidad de la detección.
- **Capa de Persistencia** (`data/`): Almacena la información de cada sesión en una base de datos SQLite para mantener el historial.
- **Capa de Reportes** (`reports/`): Genera visualizaciones y resúmenes a partir de los datos almacenados.
- **Capa de Presentación** (`ui/`): Interfaz desarrollada con Streamlit para facilitar la interacción con el usuario.

**Decisiones importantes:**
- Se eligió **MediaPipe** por su alto rendimiento en tiempo real y facilidad de uso comparado con modelos más pesados.
- Se optó por **SQLite** para evitar la necesidad de instalar un servidor de base de datos.
- La interfaz se desarrolló con **Streamlit** para lograr una experiencia visual moderna con poco código.

---

## Integrantes del equipo

- Nombre 1 - Rol (ej. Detección de postura)
- Nombre 2 - Rol (ej. Sistema de alertas)
- Nombre 3 - Rol (ej. Base de datos y reportes)
- Nombre 4 - Rol (ej. Interfaz de usuario)
- Nombre 5 - Rol (ej. Documentación y pruebas)

---

## Licencia

Este proyecto fue desarrollado con fines académicos para la materia **Programación Computacional III** - Universidad Gerardo Barrios.
```

---

¿Quieres que también te genere el archivo `requirements.txt` correspondiente a este README?