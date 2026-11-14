"""Persistencia de sesiones, alertas únicas y episodios medidos."""
from pathlib import Path
import sqlite3
from datetime import datetime
import pandas as pd

class StorageManager:
    def __init__(self, db_path="data/backend_view.db"):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._inicializar_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _inicializar_db(self):
        with self._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT, inicio TIMESTAMP,
                fin TIMESTAMP, duracion_total_segundos INTEGER)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT, sesion_id INTEGER,
                tipo_alerta TEXT, timestamp TIMESTAMP, detalle TEXT,
                FOREIGN KEY(sesion_id) REFERENCES sesiones(id))""")
            conn.execute("""CREATE TABLE IF NOT EXISTS episodios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sesion_id INTEGER NOT NULL, tipo_alerta TEXT NOT NULL,
                inicio TIMESTAMP NOT NULL, fin TIMESTAMP NOT NULL,
                duracion_segundos REAL NOT NULL CHECK(duracion_segundos >= 0),
                FOREIGN KEY(sesion_id) REFERENCES sesiones(id))""")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_episodios_sesion ON episodios(sesion_id)")

    def iniciar_sesion(self):
        with self._connect() as conn:
            cur = conn.execute("INSERT INTO sesiones (inicio) VALUES (?)", (datetime.now().isoformat(sep=' '),))
            return cur.lastrowid

    def finalizar_sesion(self, sesion_id):
        if not sesion_id:
            return None
        with self._connect() as conn:
            row = conn.execute("SELECT inicio, fin FROM sesiones WHERE id=?", (sesion_id,)).fetchone()
            if row is None:
                return None
            if row[1] is None:
                ahora = datetime.now()
                inicio = datetime.fromisoformat(row[0])
                conn.execute("UPDATE sesiones SET fin=?, duracion_total_segundos=? WHERE id=?",
                             (ahora.isoformat(sep=' '), max(0,int((ahora-inicio).total_seconds())), sesion_id))
        return self.exportar_historial_detallado(sesion_id)

    def registrar_alerta(self, sesion_id, tipo_alerta, detalle=""):
        if not sesion_id:
            return
        with self._connect() as conn:
            conn.execute("INSERT INTO alertas(sesion_id,tipo_alerta,timestamp,detalle) VALUES (?,?,?,?)",
                         (sesion_id,tipo_alerta,datetime.now().isoformat(sep=' '),detalle))

    def registrar_episodio(self, sesion_id, episodio):
        if not sesion_id:
            return
        with self._connect() as conn:
            conn.execute("""INSERT INTO episodios(sesion_id,tipo_alerta,inicio,fin,duracion_segundos)
                VALUES(?,?,?,?,?)""", (sesion_id,episodio.tipo,
                episodio.inicio.isoformat(sep=' '), episodio.fin.isoformat(sep=' '),
                round(episodio.duracion_segundos,3)))

    def obtener_episodios(self, sesion_id=None):
        with self._connect() as conn:
            if sesion_id is None:
                return pd.read_sql_query("SELECT * FROM episodios ORDER BY id DESC",conn)
            return pd.read_sql_query("SELECT * FROM episodios WHERE sesion_id=? ORDER BY id",conn,params=(sesion_id,))

    def obtener_sesiones(self):
        with self._connect() as conn:
            return pd.read_sql_query("SELECT * FROM sesiones ORDER BY id DESC",conn)

    def exportar_historial_detallado(self, sesion_id):
        with self._connect() as conn:
            sesion = pd.read_sql_query("SELECT * FROM sesiones WHERE id=?",conn,params=(sesion_id,))
            episodios = pd.read_sql_query("SELECT * FROM episodios WHERE sesion_id=?",conn,params=(sesion_id,))
        if sesion.empty:
            return None
        curva = episodios[episodios.tipo_alerta == 'ESPALDA_CURVA']
        somnolencia = episodios[episodios.tipo_alerta == 'DORMIDO_SOMNOLENCIA_CRITICA']
        total = int(sesion.iloc[0]['duracion_total_segundos'] or 0)
        segundos = float(somnolencia.duracion_segundos.sum())
        resumen = pd.DataFrame([{
            'Sesion_ID':sesion_id,'Inicio':sesion.iloc[0]['inicio'],'Fin':sesion.iloc[0]['fin'],
            'Duracion_Total_Segundos':total,'Episodios_Espalda_Curva':len(curva),
            'Episodios_Somnolencia':len(somnolencia),
            'Tiempo_Alerta_Somnolencia_Segundos':round(segundos,3),
            'Total_Episodios':len(episodios)}])
        carpeta=Path(self.db_path).parent
        archivo=carpeta/f'historial_sesion_{sesion_id}.csv'
        resumen.to_csv(archivo,index=False)
        # Regenerar maestro desde sesiones finalizadas para evitar duplicados al reexportar.
        with self._connect() as conn:
            ids=[r[0] for r in conn.execute('SELECT id FROM sesiones WHERE fin IS NOT NULL ORDER BY id')]
            filas=[]
            for sid in ids:
                s=conn.execute('SELECT inicio,fin,duracion_total_segundos FROM sesiones WHERE id=?',(sid,)).fetchone()
                ep=conn.execute('SELECT tipo_alerta,duracion_segundos FROM episodios WHERE sesion_id=?',(sid,)).fetchall()
                filas.append({'Sesion_ID':sid,'Inicio':s[0],'Fin':s[1],
                  'Duracion_Total_Segundos':s[2] or 0,
                  'Episodios_Espalda_Curva':sum(t=='ESPALDA_CURVA' for t,d in ep),
                  'Episodios_Somnolencia':sum(t=='DORMIDO_SOMNOLENCIA_CRITICA' for t,d in ep),
                  'Tiempo_Alerta_Somnolencia_Segundos':round(sum(d for t,d in ep if t=='DORMIDO_SOMNOLENCIA_CRITICA'),3),
                  'Total_Episodios':len(ep)})
        pd.DataFrame(filas,columns=resumen.columns).to_csv(carpeta/'historial_general_ergo.csv',index=False)
        return str(archivo)

    def exportar_sesiones_a_csv(self):
        path=Path(self.db_path).parent/'todas_las_sesiones.csv'
        self.obtener_sesiones().to_csv(path,index=False)
        return str(path)

    def exportar_alertas_a_csv(self):
        path=Path(self.db_path).parent/'todas_las_alertas.csv'
        with self._connect() as conn:
            pd.read_sql_query('SELECT * FROM alertas',conn).to_csv(path,index=False)
        return str(path)

    def exportar_episodios_a_csv(self):
        path=Path(self.db_path).parent/'todos_los_episodios.csv'
        self.obtener_episodios().to_csv(path,index=False)
        return str(path)

    def obtener_resumen_alertas(self):
        with self._connect() as conn:
            df=pd.read_sql_query('SELECT tipo_alerta,COUNT(*) AS total FROM alertas GROUP BY tipo_alerta',conn)
        return None if df.empty else df.set_index('tipo_alerta')['total']
