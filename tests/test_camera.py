import unittest
from unittest.mock import MagicMock
import numpy as np
from src.camera.camera_validator import abrir_camara,leer_fotograma,CameraError
from src.utils.resource_manager import cerrar_sesion_con_episodios,cerrar_recursos

class TestCamara(unittest.TestCase):
    def test_camara_conectada(self):
        cap=MagicMock();cap.isOpened.return_value=True
        self.assertIs(abrir_camara(1,capture_factory=lambda *args:cap),cap)
    def test_camara_desconectada_libera(self):
        cap=MagicMock();cap.isOpened.return_value=False
        with self.assertRaises(CameraError):abrir_camara(1,capture_factory=lambda *args:cap)
        cap.release.assert_called_once()
    def test_indice_invalido(self):
        for indice in (-1,'0',True):
            with self.assertRaises(ValueError):abrir_camara(indice)
    def test_fotograma(self):
        cap=MagicMock();cap.isOpened.return_value=True
        frame=np.zeros((10,10,3),dtype=np.uint8)
        cap.read.return_value=(True,frame)
        self.assertIs(leer_fotograma(cap),frame)
    def test_reintentos(self):
        cap=MagicMock();cap.isOpened.return_value=True;cap.read.return_value=(False,None)
        with self.assertRaises(CameraError):leer_fotograma(cap,2)
        self.assertEqual(cap.read.call_count,2)
    def test_cierre_sesion_y_episodios(self):
        db=MagicMock();tracker=MagicMock();tracker.finalizar_todos.return_value=['episodio1']
        self.assertEqual(cerrar_sesion_con_episodios(db,2,tracker),[])
        db.registrar_episodio.assert_called_once_with(2,'episodio1')
        db.finalizar_sesion.assert_called_once_with(2)
    def test_libera_aunque_falle_audio(self):
        cap=MagicMock()
        def error():raise RuntimeError('sin audio')
        errors=cerrar_recursos(cap,detener_audio=error,cerrar_ventanas=False)
        self.assertTrue(errors)
        cap.release.assert_called_once()

if __name__=='__main__':unittest.main()
