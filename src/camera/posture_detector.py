import cv2
import math
import numpy as np
import mediapipe as mp

class PostureDetector:
    def __init__(self, consecutive_frames_fatigue=30, drop_threshold_ratio=0.92):
        self.consecutive_frames_fatigue = consecutive_frames_fatigue
        self.drop_threshold_ratio = drop_threshold_ratio
        
        self.counter_eyes_closed = 0
        self.calibrated = False
        
        # Variables de calibración dinámica
        self.base_shoulder_height = None
        self.baseline_ears = []
        self.ear_threshold = 0.21  # Se ajustará automáticamente tras calibrar
        self.calib_frames_count = 0
        self.max_calib_frames = 30  # Reducido ligeramente a 30 para agilizar la calibración (~1 segundo)
        
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [363, 385, 387, 263, 373, 380]

    def _calculate_ear(self, landmarks, eye_indices, image_width, image_height):
        try:
            p = []
            for idx in eye_indices:
                lm = landmarks[idx]
                p.append(np.array([lm.x * image_width, lm.y * image_height]))
            v1 = np.linalg.norm(p[1] - p[5])
            v2 = np.linalg.norm(p[2] - p[4])
            h = np.linalg.norm(p[0] - p[3])
            return (v1 + v2) / (2.0 * h)
        except Exception:
            return 0.35

    def analizar_y_dibujar(self, frame, pose_result, face_result):
        """
        Analiza la postura, calibra dinámicamente y dibuja los puntos clave sobre el fotograma.
        """
        h, w, _ = frame.shape
        alertas_detectadas = []
        
        pose_landmarks = pose_result.pose_landmarks[0] if pose_result and pose_result.pose_landmarks else None
        face_landmarks = face_result.face_landmarks[0] if face_result and face_result.face_landmarks else None

        # --- FASE DE CALIBRACIÓN DINÁMICA ---
        if not self.calibrated:
            if pose_landmarks and face_landmarks:
                try:
                    hombro_izq = pose_landmarks[11].y * h
                    hombro_der = pose_landmarks[12].y * h
                    shoulder_avg = (hombro_izq + hombro_der) / 2.0
                    
                    ear_izq = self._calculate_ear(face_landmarks, self.LEFT_EYE, w, h)
                    ear_der = self._calculate_ear(face_landmarks, self.RIGHT_EYE, w, h)
                    ear_prom = (ear_izq + ear_der) / 2.0
                    
                    if self.base_shoulder_height is None:
                        self.base_shoulder_height = shoulder_avg
                    else:
                        self.base_shoulder_height = (self.base_shoulder_height * self.calib_frames_count + shoulder_avg) / (self.calib_frames_count + 1)
                    
                    self.baseline_ears.append(ear_prom)
                    self.calib_frames_count += 1
                    
                    if self.calib_frames_count >= self.max_calib_frames:
                        avg_open_ear = np.mean(self.baseline_ears)
                        self.ear_threshold = avg_open_ear * 0.75  
                        self.calibrated = True
                except Exception:
                    pass # Evita que un cálculo fallido rompa el fotograma en negro

        # 1. Dibujar y evaluar Espalda Curva
        if pose_landmarks:
            for lm in pose_landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)  # Puntos verdes para pose
            
            if self.calibrated and self.base_shoulder_height is not None:
                hombro_izq = pose_landmarks[11].y * h
                hombro_der = pose_landmarks[12].y * h
                altura_actual = (hombro_izq + hombro_der) / 2.0
                if altura_actual > (self.base_shoulder_height / self.drop_threshold_ratio):
                    alertas_detectadas.append("ESPALDA_CURVA")

        # 2. Dibujar y evaluar Ojos / Fatiga (EAR Dinámico)
        if face_landmarks:
            for lm in face_landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 1, (255, 0, 0), -1)  # Puntos azules para la cara

            if self.calibrated:
                try:
                    ear_izq = self._calculate_ear(face_landmarks, self.LEFT_EYE, w, h)
                    ear_der = self._calculate_ear(face_landmarks, self.RIGHT_EYE, w, h)
                    ear_promedio = (ear_izq + ear_der) / 2.0

                    if ear_promedio < self.ear_threshold:
                        self.counter_eyes_closed += 1
                        if self.counter_eyes_closed >= self.consecutive_frames_fatigue:
                            alertas_detectadas.append("DORMIDO_SOMNOLENCIA_CRITICA")
                    else:
                        self.counter_eyes_closed = 0
                except Exception:
                    pass

            # 3. Cabeceo
            if pose_landmarks and self.calibrated:
                try:
                    nariz_y = pose_landmarks[0].y * h
                    centro_hombros_y = (pose_landmarks[11].y * h + pose_landmarks[12].y * h) / 2.0
                    if (centro_hombros_y - nariz_y) < (h * 0.12):
                        alertas_detectadas.append("CABECEO_SOMNOLENCIA")
                except Exception:
                    pass

        # Texto de estado de calibración en el frame
        if self.calibrated:
            estado_texto = f"Calibrado OK (Umbral: {self.ear_threshold:.2f}) ✅"
            color_estado = (0, 255, 0)
        else:
            progreso = int((self.calib_frames_count / self.max_calib_frames) * 100)
            estado_texto = f"Colocate frente a camara... {progreso}% ⏳"
            color_estado = (0, 255, 255)

        cv2.putText(frame, estado_texto, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_estado, 2)

        if alertas_detectadas:
            cv2.putText(frame, "ALERTA ACTIVADA", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return alertas_detectadas, self.calibrated, frame