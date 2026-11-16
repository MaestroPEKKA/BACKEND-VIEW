"""Apertura, validación y lectura robusta de la webcam (OpenCV)."""
import cv2

class CameraError(RuntimeError):
    """Problema controlable de acceso a webcam."""

def abrir_camara(indice=1, directshow=True, capture_factory=None):
    if isinstance(indice, bool) or not isinstance(indice,int) or indice < 0:
        raise ValueError("CAMERA_INDEX debe ser un entero no negativo")
    factory=capture_factory or cv2.VideoCapture
    cap=factory(indice,cv2.CAP_DSHOW) if directshow else factory(indice)
    if cap is None or not cap.isOpened():
        if cap is not None:
            cap.release()
        raise CameraError(f"No fue posible abrir la cámara {indice}. Revisa permisos y aplicaciones en uso.")
    return cap

def leer_fotograma(cap, reintentos=3):
    if not isinstance(reintentos,int) or isinstance(reintentos,bool) or reintentos < 1:
        raise ValueError("reintentos debe ser >= 1")
    if cap is None or not cap.isOpened():
        raise CameraError("La cámara está desconectada o cerrada")
    for _ in range(reintentos):
        ok, frame=cap.read()
        if ok and frame is not None and getattr(frame,'size',0)>0:
            return frame
    raise CameraError(f"No se recibieron fotogramas válidos tras {reintentos} intentos")
