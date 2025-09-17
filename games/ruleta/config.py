
# games/ruleta/config.py
# -*- coding: utf-8 -*-

FONT_NAME = "assets/fonts/DejaVuSans-Bold.ttf"
WHEEL_SIZE = 560       # o 600 para más grande


PRIMARY = "#4F46E5"
BORDER  = "#E5E7EB"

POINTER_SIZE = 52       # ▲ tamaño de la flecha (ajústalo si quieres)
ANIMATION_MS = 2500

SCALE = 3

# Anillo donde va el texto (entre el 40% y 92% del radio)
INNER_RATIO = 0.40
OUTER_RATIO = 0.92

# Fuente base (sube si aún lo ves pequeño)
BASE_FONT_SIZE = 44
MIN_FONT_SIZE  = 18

# Estilo de texto
TEXT_STYLE = "tangent"   # "tangent" (a lo largo del arco) | "radial"




SEGMENTS = [
    "Seguridad", "Tecnología", "Arte y cultura", "Comunicación",
    "Cs. Exactas", "Cs. Humanas", "Cs. Naturales", "Educación", "Oficios", "Salud",
]

PALETTE = [
    "#8b5cf6", "#60a5fa", "#0ea5e9", "#ef4444",
    "#f97316", "#22c55e", "#a855f7", "#1d4ed8", "#10b981", "#f59e0b",
]

ORIENTATION_MAP = {
    "Salud": "vertical",
    "Oficios": "vertical",
    "Educación": "vertical",
    "Seguridad": "vertical",
}
