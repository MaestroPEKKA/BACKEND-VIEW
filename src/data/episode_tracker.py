"""Seguimiento de episodios continuos; duración con reloj monotónico."""
from dataclasses import dataclass
from datetime import datetime
from time import monotonic

@dataclass(frozen=True)
class Episode:
    tipo: str
    inicio: datetime
    fin: datetime
    duracion_segundos: float

class EpisodeTracker:
    def __init__(self, clock=monotonic, wall_clock=datetime.now):
        self.clock = clock
        self.wall_clock = wall_clock
        self.activos = {}

    def actualizar(self, alertas):
        actuales = set(alertas or [])
        ahora = self.clock()
        fecha = self.wall_clock()
        iniciados = sorted(actuales - self.activos.keys())
        for tipo in iniciados:
            self.activos[tipo] = (ahora, fecha)
        terminados = []
        for tipo in sorted(set(self.activos) - actuales):
            instante, inicio = self.activos.pop(tipo)
            terminados.append(Episode(tipo, inicio, fecha, max(0.0, ahora - instante)))
        return iniciados, terminados

    def finalizar_todos(self):
        return self.actualizar([])[1]
