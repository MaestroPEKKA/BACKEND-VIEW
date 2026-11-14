"""Indicadores de solo lectura para el monitoreo BACKEND-VIEW."""
import streamlit as st


def estados_monitoreo(alertas, calibrado, camara_conectada):
    """Devuelve estados presentables sin modificar la lógica de detección."""
    alertas = set(alertas or [])
    if not camara_conectada:
        return ('Desconectada', 'Sin datos', 'Sin datos')
    if not calibrado:
        return ('Conectada', 'Calibrando', 'Calibrando')
    postura = 'Alerta de postura' if 'ESPALDA_CURVA' in alertas else 'Sin alerta de postura'
    fatiga = ('Posible somnolencia' if alertas.intersection({
        'DORMIDO_SOMNOLENCIA_CRITICA', 'CABECEO_SOMNOLENCIA'})
        else 'Sin alerta de somnolencia')
    return ('Conectada', postura, fatiga)


def mostrar_panel(ubicacion, alertas=(), calibrado=False, camara_conectada=False):
    """Actualiza los tres indicadores en un contenedor Streamlit."""
    camara, postura, fatiga = estados_monitoreo(alertas, calibrado, camara_conectada)
    with ubicacion.container():
        st.markdown('#### 📡 Estado del monitoreo')
        c1, c2, c3 = st.columns(3)
        c1.metric('📷 Cámara', camara)
        c2.metric('🧍 Postura', postura)
        c3.metric('👁️ Fatiga', fatiga)
        if not camara_conectada:
            st.info('Inicia una sesión para activar la cámara.')
        elif not calibrado:
            st.info('Mantente visible y en posición estable mientras se calibra el sistema.')
        elif alertas:
            st.warning('Alertas actuales: ' + ', '.join(alertas))
        else:
            st.success('No se detectan alertas en este fotograma.')
