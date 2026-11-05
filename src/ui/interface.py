import streamlit as st
import subprocess
import sys
import os

# Configuración de la página
st.set_page_config(
    page_title="BACKEND-VIEW - Monitoreo de Postura",
    page_icon="🛡️",
    layout="wide"
)

# Título principal del sistema
st.title("🛡️ BACKEND-VIEW: Panel de Control y Monitoreo")
st.markdown("Sistema inteligente de visión artificial para la supervisión en tiempo real de postura y fatiga laboral.")

# --- BARRA LATERAL PARA ENTRADAS Y CONFIGURACIÓN ---
st.sidebar.header("⚙️ Configuración de Parámetros")
st.sidebar.markdown("Ajusta los umbrales de detección según tus necesidades:")

# Sliders e inputs para las entradas del sistema
sensibilidad_ear = st.sidebar.slider(
    "Umbral de Fatiga (EAR)", 
    min_value=0.10, 
    max_value=0.30, 
    value=0.20, 
    step=0.01,
    help="Define la apertura mínima de los ojos antes de considerar somnolencia."
)

limite_frames = st.sidebar.slider(
    "Fotogramas para Alerta", 
    min_value=5, 
    max_value=40, 
    value=15, 
    step=1,
    help="Número de fotogramas consecutivos con ojos cerrados para disparar la alerta."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🚀 Control de Sesión")

# Botón para iniciar el script de la cámara
if st.sidebar.button("Iniciar Monitoreo con Cámara", type="primary"):
    st.success("¡Señal enviada! Iniciando el módulo de visión artificial...")
    
    # Ruta absoluta hacia posture_detector.py
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "camera", "posture_detector.py"))
    
    try:
        # Ejecutar el detector en un proceso independiente para no bloquear la interfaz web
        subprocess.Popen([sys.executable, script_path])
        st.info("💡 La ventana de la cámara se ha abierto. Presiona la tecla **'q'** dentro de la ventana de video para detener el monitoreo.")
    except Exception as e:
        st.error(f"No se pudo iniciar el módulo de cámara: {e}")

# --- PANEL PRINCIPAL (MÉTRICAS Y ESTADO) ---
st.markdown("### 📊 Resumen de Actividad Actual")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Estado del Servidor / UI", value="Activo", delta="En línea")

with col2:
    st.metric(label="Alertas de Postura (Sesión)", value="0", delta="Óptimo")

with col3:
    st.metric(label="Nivel de Fatiga", value="Normal", delta="Sin riesgo")

st.markdown("---")
st.subheader("ℹ️ Instrucciones de Uso")
st.markdown("""
1. Utiliza los controles de la **barra lateral** para ajustar la sensibilidad de detección de los ojos.
2. Haz clic en el botón **'Iniciar Monitoreo con Cámara'** para activar el sistema.
3. Mantén una postura recta frente a la cámara web. El sistema te alertará visualmente si detecta inclinaciones de riesgo o signos de somnolencia.
""")