# BACKEND-VIEW

## Descripción del proyecto

BACKEND-VIEW es un sistema desarrollado en Python que utiliza visión artificial para monitorear la postura corporal y detectar posibles señales de somnolencia en tiempo real.

El proyecto busca ayudar a identificar malas posturas y signos de fatiga mediante alertas visuales y sonoras, además de almacenar los resultados para su posterior análisis.

## Tecnologías utilizadas

- Python
- OpenCV
- MediaPipe
- Streamlit
- SQLite
- NumPy
- Pandas
- Pygame

## Funcionalidades desarrolladas

Hasta el momento, el proyecto cuenta con las siguientes funcionalidades:

1. Detección de postura corporal mediante cámara.
2. Detección de posibles señales de somnolencia y cabeceo.
3. Calibración inicial del sistema.
4. Alertas visuales y sonoras.
5. Interfaz gráfica desarrollada con Streamlit.
6. Inicio y finalización de sesiones de monitoreo.
7. Registro de alertas en una base de datos SQLite.
8. Visualización de estadísticas y exportación de reportes CSV.

## Mejoras realizadas

### Interfaz y visualización

Se mejoró la interfaz gráfica del sistema, incorporando indicadores visuales para mostrar el estado de la cámara, la postura corporal y las posibles señales de fatiga.

### Registro de alertas y sesiones

Se optimizó el almacenamiento de información, incorporando el seguimiento de episodios continuos para evitar registros duplicados y calcular su duración.

También se realizaron mejoras en el historial de sesiones, la base de datos SQLite y la generación de reportes CSV.

### Pruebas del sistema

Se incorporaron pruebas automatizadas para verificar el registro de episodios y su almacenamiento.

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/MaestroPEKKA/BACKEND-VIEW.git
```

Entrar a la carpeta:

```bash
cd BACKEND-VIEW
```

Crear el entorno virtual:

```bash
python -m venv .venv
```

Activar el entorno en Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Iniciar la aplicación:

```bash
python -m streamlit run Main.py
```

Acceder desde el navegador:

[http://localhost:8501](http://localhost:8501)

Para iniciar el monitoreo, presionar el botón **Iniciar**. Para detener el análisis desde la ventana de OpenCV, presionar la tecla `q`.

## Pruebas automatizadas

Ejecutar:

```bash
python -m unittest discover -s tests -v
```

## Organización del equipo

El proyecto se desarrolla mediante la colaboración de seis integrantes.

- Integrantes 1, 2 y 3: desarrollo inicial del sistema y sus funcionalidades principales.
- Integrante 4: mejoras en la interfaz y visualización del monitoreo.
- Integrante 5: optimización del registro de alertas, episodios e historial de sesiones.
- Integrante 6: validaciones, manejo de errores y pruebas de estabilidad.

## Estado actual

El proyecto se encuentra en su primer avance de desarrollo.

Se han trabajado las funcionalidades principales de monitoreo, detección, alertas, interfaz gráfica y almacenamiento de información.

Actualmente se continúa con la integración, validación y optimización del sistema para mejorar su funcionamiento y estabilidad.

## Mejoras pendientes

- Mejorar el control de conexión de la cámara.
- Fortalecer el manejo de errores.
- Garantizar el cierre seguro de sesiones.
- Ampliar las pruebas automatizadas.
- Optimizar el rendimiento y la estabilidad general.

## Autores

Abdias Aminadab Argueta Argueta

Anderson Oziel Cruz MedinaAilthon Aldahir Cruz Flores

Albert Josue Gomez Membreño

Robert Gabriel Perez Campos

Maria Fernanda Pérez Benitez

Proyecto académico, 2026.
