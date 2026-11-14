import cv2

print("Intentando abrir la cámara con DirectShow...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ Error: No se pudo abrir la cámara.")
else:
    print("✅ ¡Cámara abierta con éxito! Presiona 'q' en la ventana de video para salir.")
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("⚠️ Fotograma en negro o sin señal...")
            break
            
        cv2.imshow("Prueba de Camara Windows", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Prueba finalizada.")