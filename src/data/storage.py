import sqlite3
import pandas as pd
import os
from datetime import datetime

class StorageManager:
    def __init__(self, db_path="data/backend_view.db"):
        os.makedirs("data", exist_ok=True)
        self.db_path = db_path
        self._inicializar_db()

    def _inicializar_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Tabla de sesiones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inicio TIMESTAMP,
                fin TIMESTAMP,
                duracion_total_segundos INTEGER
            )
        ''')
        # Tabla de alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sesion_id INTEGER,
                tipo_alerta TEXT,
                timestamp TIMESTAMP,
                detalle TEXT,
                FOREIGN KEY(sesion_id) REFERENCES sesiones(id)
            )
        ''')
        conn.commit()
        conn.close()

    def iniciar_sesion(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now()
        cursor.execute("INSERT INTO sesiones (inicio) VALUES (?)", (now,))
        sesion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return sesion_id

    def finalizar_sesion(self, sesion_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now()
        
        # Obtener tiempo de inicio
        cursor.execute("SELECT inicio FROM sesiones WHERE id = ?", (sesion_id,))
        row = cursor.fetchone()
        if row:
            inicio = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f" if "." in row[0] else "%Y-%m-%d %H:%M:%S")
            duracion = int((now - inicio).total_seconds())
            cursor.execute("UPDATE sesiones SET fin = ?, duracion_total_segundos = ? WHERE id = ?", (now, duracion, sesion_id))
            conn.commit()
        conn.close()
        
        # Generar el reporte CSV detallado de esta sesión
        return self.exportar_historial_detallado(sesion_id)

    def registrar_alerta(self, sesion_id, tipo_alerta, detalle=""):
        if not sesion_id:
            return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now()
        cursor.execute("INSERT INTO alertas (sesion_id, tipo_alerta, timestamp, detalle) VALUES (?, ?, ?, ?)",
                       (sesion_id, tipo_alerta, now, detalle))
        conn.commit()
        conn.close()

    def exportar_historial_detallado(self, sesion_id):
        """Calcula métricas de la sesión y genera un CSV con el historial detallado."""
        conn = sqlite3.connect(self.db_path)
        
        # Consultar datos de la sesión
        sesion_df = pd.read_sql_query(f"SELECT * FROM sesiones WHERE id = {sesion_id}", conn)
        # Consultar alertas de la sesión
        alertas_df = pd.read_sql_query(f"SELECT * FROM alertas WHERE sesion_id = {sesion_id}", conn)
        conn.close()
        
        if sesion_df.empty:
            return None

        duracion_total = sesion_df.loc[0, 'duracion_total_segundos'] or 0
        
        # Conteo de eventos
        veces_espalda_curva = len(alertas_df[alertas_df['tipo_alerta'] == 'ESPALDA_CURVA'])
        episodios_somnolencia = len(alertas_df[alertas_df['tipo_alerta'] == 'DORMIDO_SOMNOLENCIA_CRITICA'])
        
        # Estimación de tiempo dormido (asumiendo ~1 segundo por fotograma de alerta crítica detectada consecutiva)
        tiempo_dormido_seg = episodios_somnolencia * 2  # Aproximación basada en los fotogramas de disparo
        tiempo_despierto_seg = max(0, duracion_total - tiempo_dormido_seg)
        
        # Crear estructura de resumen para el CSV
        resumen_data = [{
            "Sesion_ID": sesion_id,
            "Inicio": sesion_df.loc[0, 'inicio'],
            "Fin": sesion_df.loc[0, 'fin'],
            "Duracion_Total_Segundos": duracion_total,
            "Veces_Espalda_Curva (Me agache)": veces_espalda_curva,
            "Episodios_Somnolencia (Me dormi)": episodios_somnolencia,
            "Tiempo_Dormido_Segundos": tiempo_dormido_seg,
            "Tiempo_Despierto_Segundos": tiempo_despierto_seg
        }]
        
        resumen_df = pd.DataFrame(resumen_data)
        
        # Guardar en archivo CSV específico de la sesión y un acumulado general
        os.makedirs("data", exist_ok=True)
        path_sesion = f"data/historial_sesion_{sesion_id}.csv"
        resumen_df.to_csv(path_sesion, index=False)
        
        # También agregarlo a un historial general maestro
        path_general = "data/historial_general_ergo.csv"
        if os.path.exists(path_general):
            resumen_df.to_csv(path_general, mode='a', header=False, index=False)
        else:
            resumen_df.to_csv(path_general, index=False)
            
        return path_sesion

    def exportar_sesiones_a_csv(self):
        """Exporta todas las sesiones registradas a un archivo CSV consolidado."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM sesiones", conn)
        conn.close()
        
        path_out = "data/todas_las_sesiones.csv"
        os.makedirs("data", exist_ok=True)
        df.to_csv(path_out, index=False)
        return path_out

    def exportar_alertas_a_csv(self):
        """Exporta todas las alertas registradas a un archivo CSV consolidado."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM alertas", conn)
        conn.close()
        
        path_out = "data/todas_las_alertas.csv"
        os.makedirs("data", exist_ok=True)
        df.to_csv(path_out, index=False)
        return path_out

    def obtener_resumen_alertas(self):
        """Obtiene un resumen agrupado de alertas para los gráficos del panel principal."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT tipo_alerta, COUNT(*) as total FROM alertas GROUP BY tipo_alerta", conn)
        conn.close()
        
        if df.empty:
            return None
        # Convertir a formato de diccionario o serie para st.bar_chart
        return df.set_index("tipo_alerta")["total"]