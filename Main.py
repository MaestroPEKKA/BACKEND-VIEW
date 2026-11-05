import streamlit as st
import cv2
import time
import os
import pandas as pd
import random
import pygame  # Librería para manejo eficiente de audios MP3
from src.camera.posture_detector import PostureDetector
from src.data.storage import StorageManager

# Inicializar el mezclador de audio de pygame
pygame.mixer.init()

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="BACKEND-VIEW - Monitoreo Ergonómico y Fatiga",
    page_icon="💻",
    layout="wide"
)

# Inicializar gestores de base de datos y detector
@st.cache_resource
def get_storage():
    return StorageManager()

db = get_storage()

# Función para iniciar la reproducción continua y aleatoria del audio correspondiente
def reproducir_alerta_continua(tipo):
    try:
        if not pygame.mixer.music.get_busy():
            if tipo == "ESPALDA_CURVA":
                num = random.choice(["", "2", "3"])
                nombre_archivo = f"advertencia{num}.mp3"
            elif tipo in ["DORMIDO_SOMNOLENCIA_CRITICA", "CABECEO_SOMNOLENCIA"]:
                num = random.choice(["", "2", "3"])
                nombre_archivo = f"weakup{num}.mp3"
            else:
                return

            ruta_audio = os.path.abspath(os.path.join("src", "alerts", nombre_archivo))
            if os.path.exists(ruta_audio):
                pygame.mixer.music.load(ruta_audio)
                pygame.mixer.music.play(loops=-1)  # Bucle continuo hasta que cese la alerta
            else:
                print(f"⚠️ No se encontró el archivo de audio: {ruta_audio}")
    except Exception as e:
        print(f"Error reproduciendo audio: {e}")

# Función para detener el audio de forma inmediata al cesar la alerta
def detener_alerta_sonora():
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
    except Exception as e:
        print(f"Error deteniendo audio: {e}")

def main():
    st.title("🛡️ BACKEND-VIEW: Monitoreo Ergonómico y Fatiga en Tiempo Real")
    st.markdown("Sistema inteligente para la detección de malas posturas, espalda curva y somnolencia en entornos de trabajo o estudio.")

    # Sidebar para controles de sesión
    st.sidebar.header("⚙️ Controles")
    
    # Estado de sesión en Streamlit
    if "sesion_activa_id" not in st.session_state:
        st.session_state.sesion_activa_id = None
    if "monitoreando" not in st.session_state:
        st.session_state.monitoreando = False

    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("▶️ Iniciar Sesión"):
            if not st.session_state.monitoreando:
                st.session_state.sesion_activa_id = db.iniciar_sesion()
                st.session_state.monitoreando = True
                st.success(f"Sesión #{st.session_state.sesion_activa_id} iniciada.")

    with col2:
        if st.button("⏹️ Finalizar"):
            if st.session_state.monitoreando and st.session_state.sesion_activa_id:
                path_csv = db.finalizar_sesion(st.session_state.sesion_activa_id)
                st.session_state.monitoreando = False
                st.warning(f"Sesión finalizada. Datos guardados en: {path_csv}")
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Reportes y Datos")
    if st.sidebar.button("📥 Exportar Datos a CSV"):
        path_sesiones = db.exportar_sesiones_a_csv()
        path_alertas = db.exportar_alertas_a_csv()
        st.sidebar.success(f"Exportado en carpeta `data/`")

    # Panel Principal
    if st.session_state.monitoreando:
        st.info(f"🔴 Monitoreo en curso (Sesión ID: {st.session_state.sesion_activa_id}). Presiona 'q' en la ventana emergente de la cámara para detener.")
        
        # Inicializar MediaPipe solutions para extraer landmarks
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        # Rutas de los modelos .task
        base_options_pose = python.BaseOptions(model_asset_path='src/camera/pose_landmarker.task')
        options_pose = vision.PoseLandmarkerOptions(base_options=base_options_pose, running_mode=vision.RunningMode.IMAGE)
        pose_landmarker = vision.PoseLandmarker.create_from_options(options_pose)

        base_options_face = python.BaseOptions(model_asset_path='src/camera/face_landmarker.task')
        options_face = vision.FaceLandmarkerOptions(base_options=base_options_face, running_mode=vision.RunningMode.IMAGE, output_face_blendshapes=True)
        face_landmarker = vision.FaceLandmarker.create_from_options(options_face)
        
        # Instancia del detector (utiliza calibración automática)
        detector = PostureDetector(consecutive_frames_fatigue=30)
        
        cap = cv2.VideoCapture(0)
        alerta_placeholder = st.empty()
        
        try:
            while cap.isOpened() and st.session_state.monitoreando:
                ret, frame = cap.read()
                if not ret:
                    st.error("No se pudo acceder a la cámara.")
                    break
                    
                # Voltear horizontalmente para efecto espejo natural
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                
                # Ejecutar modelos de MediaPipe
                pose_result = pose_landmarker.detect(mp_image)
                face_result = face_landmarker.detect(mp_image)
                
                # Analizar e incluir el renderizado de los puntos en pantalla
                alertas, calibrado, frame_procesado = detector.analizar_y_dibujar(frame, pose_result, face_result)
                
                # Registrar alertas y controlar las alarmas de audio dinámicas
                if alertas:
                    for alerta in alertas:
                        db.registrar_alerta(st.session_state.sesion_activa_id, alerta, "Detectado en tiempo real")
                        
                    # Llamada correcta a la función continua con variantes aleatorias
                    reproducir_alerta_continua(alertas[0])
                        
                    alerta_placeholder.error(f"⚠️ ¡ALERTA DETECTADA!: {', '.join(alertas)}")
                else:
                    # Detener el audio inmediatamente cuando se recupera la postura óptima
                    detener_alerta_sonora()
                    alerta_placeholder.success("🟢 Postura y estado óptimos.")

                # Mostrar ventana de la cámara
                cv2.imshow("BACKEND-VIEW - Monitoreo Ergonomico", frame_procesado)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    st.session_state.monitoreando = False
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
            time.sleep(1.5)  # Pausa requerida por el driver de Windows para liberar el puerto USB
            if not st.session_state.monitoreando:
                st.rerun()
    else:
        st.warning("⚠️ El monitoreo está pausado. Haz clic en **'Iniciar Sesión'** en la barra lateral para comenzar.")
        
        st.markdown("---")
        st.subheader("📊 Panel de Estadísticas y Analítica de Sesiones")
        
        path_general = "data/historial_general_ergo.csv"
        
        if os.path.exists(path_general):
            try:
                df_historial = pd.read_csv(path_general)
                
                # KPIs principales
                col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
                
                total_sesiones = len(df_historial)
                tiempo_total_min = int(df_historial["Duracion_Total_Segundos"].sum() / 60)
                total_encorvamientos = int(df_historial["Veces_Espalda_Curva (Me agache)"].sum())
                total_sueño = int(df_historial["Episodios_Somnolencia (Me dormi)"].sum())
                
                with col_kpi1:
                    st.metric("Sesiones Registradas", total_sesiones)
                with col_kpi2:
                    st.metric("Tiempo Total (min)", tiempo_total_min)
                with col_kpi3:
                    st.metric("Total Encorvamientos", total_encorvamientos)
                with col_kpi4:
                    st.metric("Alertas de Sueño", total_sueño)
                
                st.markdown("---")
                st.markdown("### 🎛️ Vista de Analítica")
                
                # Estado para alternar vistas mediante botones independientes
                if "vista_estadistica" not in st.session_state:
                    st.session_state.vista_estadistica = "grafico"

                b_col1, b_col2, _ = st.columns([1, 1, 2])
                with b_col1:
                    if st.button("📈 Ver Gráfico de Incidencias", use_container_width=True):
                        st.session_state.vista_estadistica = "grafico"
                with b_col2:
                    if st.button("📋 Ver Historial Tabular", use_container_width=True):
                        st.session_state.vista_estadistica = "tabla"

                st.markdown("")

                # Renderizar según el botón presionado
                if st.session_state.vista_estadistica == "grafico":
                    st.markdown("#### 📈 Comparativa de Mala Postura vs Somnolencia por Sesión")
                    if not df_historial.empty:
                        df_chart = df_historial[["Sesion_ID", "Veces_Espalda_Curva (Me agache)", "Episodios_Somnolencia (Me dormi)"]].set_index("Sesion_ID")
                        st.bar_chart(df_chart)
                    else:
                        st.info("Aún hay muy pocos datos registrados para graficar.")
                        
                elif st.session_state.vista_estadistica == "tabla":
                    st.markdown("#### 📋 Registro Histórico Detallado")
                    st.dataframe(df_historial, use_container_width=True)
                    
            except Exception as e:
                st.info(f"Cargando historial de datos... ({e})")
        else:
            st.info("📁 Aún no se detectan archivos de historial en la carpeta `data/`. Finaliza tu primera sesión de monitoreo para generar estadísticas automáticas.")
            
            # Respaldo con base de datos
            st.subheader("📈 Resumen General en Base de Datos")
            try:
                resumen = db.obtener_resumen_alertas()
                if resumen:
                    st.bar_chart(resumen)
                else:
                    st.info("Aún no hay registros de alertas en la base de datos.")
            except Exception:
                st.info("Inicia una sesión para ver las métricas reflejadas.")

if __name__ == "__main__":
    main()