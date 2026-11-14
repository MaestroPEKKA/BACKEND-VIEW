import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from src.data.episode_tracker import EpisodeTracker
from src.data.storage import StorageManager

class Reloj:
    def __init__(self):
        self.t=0
        self.fecha=datetime(2026,1,1,12)
    def monotonic(self):return self.t
    def now(self):return self.fecha+timedelta(seconds=self.t)
    def avanzar(self,s):self.t+=s

class Pruebas(unittest.TestCase):
    def test_un_episodio_por_alerta_continua(self):
        reloj=Reloj()
        tr=EpisodeTracker(reloj.monotonic,reloj.now)
        self.assertEqual(tr.actualizar(['ESPALDA_CURVA'])[0],['ESPALDA_CURVA'])
        reloj.avanzar(3)
        self.assertEqual(tr.actualizar(['ESPALDA_CURVA'])[0],[])
        reloj.avanzar(2)
        ep=tr.actualizar([])[1]
        self.assertEqual(len(ep),1)
        self.assertEqual(ep[0].duracion_segundos,5)

    def test_alertas_simultaneas_y_cierre(self):
        r=Reloj(); tr=EpisodeTracker(r.monotonic,r.now)
        tr.actualizar(['ESPALDA_CURVA','DORMIDO_SOMNOLENCIA_CRITICA'])
        r.avanzar(4)
        self.assertEqual(len(tr.finalizar_todos()),2)
        self.assertEqual(tr.finalizar_todos(),[])

    def test_almacenamiento_y_csv(self):
        with tempfile.TemporaryDirectory() as td:
            db=StorageManager(Path(td)/'prueba.db')
            sesion=db.iniciar_sesion()
            r=Reloj(); tr=EpisodeTracker(r.monotonic,r.now)
            tr.actualizar(['DORMIDO_SOMNOLENCIA_CRITICA'])
            db.registrar_alerta(sesion,'DORMIDO_SOMNOLENCIA_CRITICA','Inicio')
            r.avanzar(2.5)
            db.registrar_episodio(sesion,tr.finalizar_todos()[0])
            db.finalizar_sesion(sesion)
            self.assertEqual(len(db.obtener_episodios(sesion)),1)
            self.assertEqual(len(db.obtener_resumen_alertas()),1)
            self.assertTrue((Path(td)/f'historial_sesion_{sesion}.csv').exists())
            self.assertTrue((Path(td)/'historial_general_ergo.csv').exists())
            self.assertEqual(float(db.obtener_episodios(sesion).iloc[0]['duracion_segundos']),2.5)

if __name__=='__main__':unittest.main()
