MAX_CALIB_FRAMES = 30  # Fotogramas necesarios para calibración inicial (~1 seg)

# --- DETECCIÓN DE ESPALDA CURVA (POSTURA) ---
# Ratio de caída de los hombros respecto a la altura base calibrada.
# Si la altura actual supera (base / DROP_THRESHOLD_RATIO), se activa la alerta.
DROP_THRESHOLD_RATIO = 0.92

# --- DETECCIÓN DE FATIGA / SOMNOLENCIA (EAR - Eye Aspect Ratio) ---
# Multiplicador sobre el promedio de apertura de ojos calibrado.
# Por debajo de este porcentaje se considera cierre de ojos.
EAR_MULTIPLIER_THRESHOLD = 0.75

# Cantidad de fotogramas consecutivos con ojos cerrados para disparar alerta crítica
CONSECUTIVE_FRAMES_FATIGUE = 30

# --- DETECCIÓN DE CABECEO ---
# Diferencia de altura entre la nariz y el centro de los hombros
CABECEO_RATIO_FACTOR = 0.12

# --- CONFIGURACIÓN DE CÁMARA ---
CAMERA_INDEX = 0
USE_DIRECT_SHOW = True  # True para forzar DirectShow en Windows y evitar pantallas negras