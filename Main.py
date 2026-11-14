import os
import random
import time
import cv2
import pandas as pd
import pygame  # Librería para manejo eficiente de audios MP3
from src.camera.posture_detector import PostureDetector
from src.data.storage import StorageManager
from src.ui.monitor_panel import mostrar_panel
from src.utils.config import CAMERA_INDEX, USE_DIRECT_SHOW
import streamlit as st

# Inicializar el mezclador de audio de pygame
pygame.mixer.init()

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="BACKEND-VIEW | Dashboard Ergonómico", page_icon="🛡️", layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS (MODO PREMIUM DASHBOARD) ---
st.markdown(
    """
    <style>
        /* Fondo general y paleta de colores moderna */
        .stApp {
            background-color: #0b0f19;
            color: #f3f4f6;
        }
        
        /* Ocultar elementos predeterminados molestos si es necesario */
        header {visibility: hidden;}
        
        /* Contenedores tipo Tarjeta (Glassmorphism / Clean Dark) */
        .css-1r7sldb, .element-container, div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        
        /* Tarjetas de Métricas Personalizadas */
        .metric-container {
            background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
            border: 1px solid #374151;
            padding: 20px;
            border-radius: 14px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -4px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .metric-container:hover {
            border-color: #3b82f6;
            transform: translateY(-2px);
        }
        
        /* Estilos de Botones */
        .stButton button {
            border-radius: 10px;
            font-weight: 600;
            padding: 0.5rem 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        /* Sidebar mejorado */
        section[data-testid="stSidebar"] {
            background-color: #030712;
            border-right: 1px solid #1f2937;
        }
        
        /* Títulos y textos */
        h1, h2, h3 {
            color: #f9fafb;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }
        
        /* Divisores elegantes */
        hr {
            border-color: #1f2937;
            margin: 2rem 0;
        }
    </style>
""",
    unsafe_allow_html=True,
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
        pygame.mixer.music.play(
            loops=-1
        )  # Bucle continuo hasta que cese la alerta
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
  # Encabezado Principal Moderno con Estilo Banner
  st.markdown(
      """
        <div style='background: linear-gradient(90deg, #1e3a8a 0%, #312e81 100%); padding: 30px; border-radius: 16px; margin-bottom: 30px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);'>
            <div style='display: flex; align-items: center; justify-content: space-between;'>
                <div>
                    <h1 style='color: white; margin: 0; font-size: 2.4rem; letter-spacing: -0.5px;'>🛡️ BACKEND-VIEW</h1>
                    <p style='color: #93c5fd; font-size: 1.1rem; margin-top: 8px; margin-bottom: 0;'>Sistema Inteligente de Monitoreo Ergonómico y Fatiga en Tiempo Real</p>
                </div>
                <div>
                    <span style='background-color: rgba(255, 255, 255, 0.1); color: #e0e7ff; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; border: 1px solid rgba(255, 255, 255, 0.2);'>v2.0 Pro</span>
                </div>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  # Sidebar para controles de sesión
  with st.sidebar:
    st.markdown("### ⚙️ Centro de Control")
    st.markdown(
        "<p style='color: #9ca3af; font-size: 0.85rem;'>Gestiona tu sesión de"
        " trabajo y exporta tus reportes de salud.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Estado de sesión en Streamlit
    if "sesion_activa_id" not in st.session_state:
      st.session_state.sesion_activa_id = None
    if "monitoreando" not in st.session_state:
      st.session_state.monitoreando = False

    st.markdown("#### Estado de Sesión")
    col1, col2 = st.columns(2)

    with col1:
      if st.button("▶️ Iniciar", use_container_width=True):
        if not st.session_state.monitoreando:
          st.session_state.sesion_activa_id = db.iniciar_sesion()
          st.session_state.monitoreando = True
          st.success(f"Sesión #{st.session_state.sesion_activa_id} iniciada.")

    with col2:
      if st.button("⏹️ Finalizar", use_container_width=True):
        if st.session_state.monitoreando and st.session_state.sesion_activa_id:
          path_csv = db.finalizar_sesion(st.session_state.sesion_activa_id)
          st.session_state.monitoreando = False
          st.warning(f"Sesión finalizada. Guardada en: {path_csv}")
          st.rerun()

    st.markdown("---")
    st.markdown("#### 📊 Exportación")
    if st.button("📥 Exportar Datos CSV", use_container_width=True):
      path_sesiones = db.exportar_sesiones_a_csv()
      path_alertas = db.exportar_alertas_a_csv()
      st.success("¡Datos exportados con éxito en `data/`!")

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #4b5563; font-size: 0.75rem;"
        " margin-top: 50px;'>BACKEND-VIEW Engine &copy; 2026</div>",
        unsafe_allow_html=True,
    )

  # Panel Principal
  if st.session_state.monitoreando:
    st.markdown(
        f"""
            <div style='background-color: #1e1b4b; border-left: 5px solid #6366f1; padding: 15px 20px; border-radius: 0 10px 10px 0; margin-bottom: 20px;'>
                <h4 style='color: #818cf8; margin: 0 0 5px 0;'>🔴 Monitoreo Activo (Sesión ID: {st.session_state.sesion_activa_id})</h4>
                <p style='color: #c7d2fe; margin: 0; font-size: 0.95rem;'>La cámara está activa en una ventana flotante independiente. Presiona la tecla <code style='background-color: #312e81; color: #fff; padding: 2px 6px; border-radius: 4px;'>'q'</code> en dicha ventana para detener el análisis de forma segura.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Inicializar MediaPipe solutions para extraer landmarks
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    # Rutas de los modelos .task
    base_options_pose = python.BaseOptions(
        model_asset_path="src/camera/pose_landmarker.task"
    )
    options_pose = vision.PoseLandmarkerOptions(
        base_options=base_options_pose, running_mode=vision.RunningMode.IMAGE
    )
    pose_landmarker = vision.PoseLandmarker.create_from_options(options_pose)

    base_options_face = python.BaseOptions(
        model_asset_path="src/camera/face_landmarker.task"
    )
    options_face = vision.FaceLandmarkerOptions(
        base_options=base_options_face,
        running_mode=vision.RunningMode.IMAGE,
        output_face_blendshapes=True,
    )
    face_landmarker = vision.FaceLandmarker.create_from_options(options_face)

    # Instancia del detector (utiliza calibración automática)
    detector = PostureDetector(consecutive_frames_fatigue=30)

    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    panel_estado = st.empty()
    alerta_placeholder = st.empty()
    mostrar_panel(panel_estado, camara_conectada=cap.isOpened())

    try:
      while cap.isOpened() and st.session_state.monitoreando:
        ret, frame = cap.read()
        if not ret:
          st.error(
              "No se pudo acceder a la cámara. Verifica que no esté ocupada"
              " por otra aplicación."
          )
          break

        # Voltear horizontalmente para efecto espejo natural
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Ejecutar modelos de MediaPipe
        pose_result = pose_landmarker.detect(mp_image)
        face_result = face_landmarker.detect(mp_image)

        # Analizar e incluir el renderizado de los puntos en pantalla
        alertas, calibrado, frame_procesado = detector.analizar_y_dibujar(
            frame, pose_result, face_result
        )

        mostrar_panel(
            panel_estado, alertas=alertas, calibrado=calibrado,
            camara_conectada=True
        )

        # Registrar alertas y controlar las alarmas de audio dinámicas
        if alertas:
          for alerta in alertas:
            db.registrar_alerta(
                st.session_state.sesion_activa_id,
                alerta,
                "Detectado en tiempo real",
            )

          reproducir_alerta_continua(alertas[0])
          alerta_placeholder.error(
              f"⚠️ ¡ALERTA DETECTADA!: {', '.join(alertas)}"
          )
        else:
          detener_alerta_sonora()
          alerta_placeholder.success("🟢 Postura y estado óptimos.")

        # 🪟 Desplegar la ventana flotante nativa de OpenCV
        cv2.imshow("BACKEND-VIEW - Monitoreo Ergonomico", frame_procesado)

        # Capturar tecla 'q' para salir de la ventana flotante
        if cv2.waitKey(1) & 0xFF == ord("q"):
          st.session_state.monitoreando = False
          db.finalizar_sesion(st.session_state.sesion_activa_id)
          break

    finally:
      cap.release()
      cv2.destroyAllWindows()
      detener_alerta_sonora()
      time.sleep(
          1.0
      )  # Pausa requerida por el driver de Windows para liberar el puerto USB
      if not st.session_state.monitoreando:
        st.rerun()
  else:
    mostrar_panel(st.empty())
    st.markdown(
        """
            <div style='background-color: #111827; border: 1px solid #374151; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 25px;'>
                <h3 style='color: #f3f4f6; margin-bottom: 8px;'>⚠️ Sistema en Pausa</h3>
                <p style='color: #9ca3af; margin: 0;'>Haz clic en el botón <strong style='color: #60a5fa;'>'Iniciar'</strong> en la barra lateral izquierda para habilitar la cámara y comenzar el seguimiento de postura.</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📊 Panel de Estadísticas y Analítica General")

    path_general = "data/historial_general_ergo.csv"

    if os.path.exists(path_general):
      try:
        df_historial = pd.read_csv(path_general)

        # KPIs principales con estructura visual limpia estilo dashboard
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

        total_sesiones = len(df_historial)
        tiempo_total_min = int(
            df_historial["Duracion_Total_Segundos"].sum() / 60
        )
        total_encorvamientos = int(
            df_historial["Veces_Espalda_Curva (Me agache)"].sum()
        )
        total_sueño = int(
            df_historial["Episodios_Somnolencia (Me dormi)"].sum()
        )

        with col_kpi1:
          st.metric(
              label="📁 Sesiones Registradas",
              value=total_sesiones,
              delta="Histórico",
          )
        with col_kpi2:
          st.metric(
              label="⏱️ Tiempo Total",
              value=f"{tiempo_total_min} min",
              delta="Acumulado",
          )
        with col_kpi3:
          st.metric(
              label="📉 Total Encorvamientos",
              value=total_encorvamientos,
              delta_color="inverse",
          )
        with col_kpi4:
          st.metric(
              label="💤 Alertas de Somnolencia",
              value=total_sueño,
              delta_color="inverse",
          )

        st.markdown("<br>", unsafe_allow_html=True)

        # Pestañas limpias para alternar vistas (Mucho más moderno que botones repetidos)
        tab_grafico, tab_tabla = st.tabs(
            ["📈 Gráfico de Incidencias", "📋 Registro Histórico Detallado"]
        )

        with tab_grafico:
          st.markdown(
              "#### Comparativa de Mala Postura vs Somnolencia por Sesión"
          )
          if not df_historial.empty:
            df_chart = df_historial[[
                "Sesion_ID",
                "Veces_Espalda_Curva (Me agache)",
                "Episodios_Somnolencia (Me dormi)",
            ]].set_index("Sesion_ID")
            st.bar_chart(df_chart, use_container_width=True)
          else:
            st.info("Aún hay muy pocos datos registrados para graficar.")

        with tab_tabla:
          st.markdown("#### Historial Analítico Completo de Sesiones")
          st.dataframe(df_historial, use_container_width=True)

      except Exception as e:
        st.error(f"Error cargando el historial de datos: {e}")
    else:
      st.info(
          "📁 Aún no se detectan archivos de historial en la carpeta `data/`."
          " Finaliza tu primera sesión de monitoreo para generar analíticas"
          " automáticas."
      )

      # Respaldo con base de datos
      st.markdown("---")
      st.subheader("📈 Resumen Rápido desde Base de Datos")
      try:
        resumen = db.obtener_resumen_alertas()
        if resumen:
          st.bar_chart(resumen, use_container_width=True)
        else:
          st.info("Aún no hay registros de alertas en la base de datos.")
      except Exception:
        st.info("Inicia una sesión para ver las métricas reflejadas.")


if __name__ == "__main__":
  main()

 