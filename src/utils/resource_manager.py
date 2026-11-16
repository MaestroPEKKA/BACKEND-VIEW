"""Cierra recursos aun si alguno produce una excepción."""
import cv2

def cerrar_recursos(cap=None, detener_audio=None, modelos=(), cerrar_ventanas=True):
    errores=[]
    if detener_audio:
        try: detener_audio()
        except Exception as e: errores.append(f"audio: {e}")
    for i,modelo in enumerate(modelos or ()):
        if modelo is not None:
            try: modelo.close()
            except Exception as e: errores.append(f"modelo {i}: {e}")
    if cap is not None:
        try: cap.release()
        except Exception as e: errores.append(f"cámara: {e}")
    if cerrar_ventanas:
        try: cv2.destroyAllWindows()
        except Exception as e: errores.append(f"ventanas: {e}")
    return errores

def cerrar_sesion_con_episodios(db, sesion_id, tracker=None):
    """Conserva datos incluso ante error; genera lista de mensajes de error."""
    errores=[]
    if not sesion_id:
        return errores
    if tracker is not None:
        try: pendientes=tracker.finalizar_todos()
        except Exception as e:
            pendientes=[]
            errores.append(f"seguimiento: {e}")
        for episodio in pendientes:
            try: db.registrar_episodio(sesion_id,episodio)
            except Exception as e: errores.append(f"episodio: {e}")
    try: db.finalizar_sesion(sesion_id)
    except Exception as e: errores.append(f"sesión: {e}")
    return errores
