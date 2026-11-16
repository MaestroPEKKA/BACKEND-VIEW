"""Prueba manual en Windows. Ejecutar desde la raíz: python test_cam.py"""
import cv2
from src.camera.camera_validator import abrir_camara, leer_fotograma, CameraError
from src.utils.resource_manager import cerrar_recursos
from src.utils.config import CAMERA_INDEX, USE_DIRECT_SHOW

def main():
    cap=None
    try:
        cap=abrir_camara(CAMERA_INDEX,USE_DIRECT_SHOW)
        print(f"Cámara {CAMERA_INDEX} conectada. Presiona q para salir.")
        while True:
            frame=leer_fotograma(cap,3)
            cv2.imshow('BACKEND-VIEW - Prueba de camara',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except CameraError as e:
        print(f"FALLO DE CAMARA: {e}")
    finally:
        for error in cerrar_recursos(cap): print('Error al cerrar:',error)

if __name__=='__main__':main()
