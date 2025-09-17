# -*- coding: utf-8 -*-
# games/ruleta/draw.py
import io, base64, math
from typing import Tuple, List
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os
from pathlib import Path
from PIL import ImageFont, __file__ as PIL_FILE

def _font(size: int) -> ImageFont.FreeTypeFont:
    size = int(size)
    here = Path(__file__).resolve()
    project_root = here.parents[2]

    candidates = [
        project_root / "assets" / "fonts" / "Arial-Bold.ttf",          # 👈 tu copia
        project_root / "assets" / "fonts" / "DejaVuSans-Bold.ttf",     # 👈 si usaste la de Pillow
        r"C:\Windows\Fonts\arialbd.ttf",                               # Windows
        (Path(PIL_FILE).parent / "fonts" / "DejaVuSans-Bold.ttf"),     # fallback Pillow
    ]

    for c in candidates:
        try:
            return ImageFont.truetype(str(c), size)
        except Exception:
            pass

    return ImageFont.load_default()   # si llega aquí verás “puntitos”

# ---------------------------------------------
# Config (usa lo que haya en config; si falta, fallback)
# ---------------------------------------------
try:
    from .config import WHEEL_SIZE, PALETTE, FONT_NAME, BASE_FONT_SIZE, MIN_FONT_SIZE
except Exception:
    WHEEL_SIZE = 560
    PALETTE = [
        "#1e90ff", "#2ecc71", "#f39c12", "#9b59b6",
        "#27ae60", "#3498db", "#e74c3c", "#95a5a6",
        "#8e44ad", "#16a085"
    ]
    FONT_NAME = "DejaVuSans-Bold.ttf"   # si no existe, caemos a fallback
    BASE_FONT_SIZE = 44
    MIN_FONT_SIZE  = 18

# ---------------------------------------------
# Parámetros de render
# ---------------------------------------------
SCALE = 3  # render ×3 para nitidez

# Anillo donde va el texto (entre 40% y 92% del radio)
INNER_RATIO = 0.40
OUTER_RATIO = 0.92

# Estilo: "tangent" (curvado a lo largo del arco) | "radial"
TEXT_STYLE = "tangent"


# ---------------------------------------------
# Utilidades
# ---------------------------------------------
def _font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_NAME, int(size))
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", int(size))
        except Exception:
            return ImageFont.load_default()

def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    # tamaño de UNA línea
    b = draw.textbbox((0, 0), text, font=font, anchor="lt")
    return int(b[2]-b[0]), int(b[3]-b[1])


# ---------------------------------------------
# Texto tangente al arco (como tu referencia)
# ---------------------------------------------
def _render_label_tangent(base_img: Image.Image,
                          label: str,
                          center: Tuple[int, int],
                          mid_deg: float,
                          r: int,
                          slice_deg: float):
    """
    Dibuja la etiqueta siguiendo el arco del sector (tangente),
    centrada en el sector y siempre legible (nunca cabeza abajo).
    """
    cx, cy = center

    # radio donde apoyamos el texto (centro del anillo, sesgo leve hacia fuera)
    base_ratio = (INNER_RATIO * 0.45 + OUTER_RATIO * 0.55)
    radius = float(base_ratio * r)

    # fuente grande para empezar
    font = _font(int(BASE_FONT_SIZE * SCALE))

    # lienzo para medir
    probe = Image.new("RGBA", (int(2*radius)+200, int(2*radius)+200), (0, 0, 0, 0))
    d = ImageDraw.Draw(probe)

    # construir lista de (char, ancho_px)
    chars: List[Tuple[str, int]] = []
    space_w = _text_size(d, " ", font)[0]
    for ch in label:
        if ch == "\n":
            w = int(space_w * 1.2)
        else:
            w = _text_size(d, ch, font)[0]
        w += int(1.2 * SCALE)  # pequeña separación extra
        chars.append((ch, w))

    # longitud total del texto en píxeles y en radianes sobre este radio
    total_px = sum(w for _, w in chars)
    total_theta = total_px / radius  # radianes

    mid_rad = math.radians(mid_deg)

    # Tangente en el centro = mid_rad + 90°
    rot_deg_mid = math.degrees(mid_rad) + 90.0
    # si estaría al revés, invertimos el orden para escribir “desde el otro lado”
    flip = 90.0 < (rot_deg_mid % 360.0) < 270.0
    if flip:
        chars = list(reversed(chars))

    # ángulo inicial para centrar el texto en el sector
    start_angle = mid_rad - (total_theta / 2.0)

    acc = 0.0
    for ch, w in chars:
        # ángulo en radianes para este carácter (en el centro del bloque del char)
        ang = start_angle + (acc + w / 2.0) / radius
        acc += w

        # posición sobre el arco
        px = int(cx + radius * math.cos(ang))
        py = int(cy - radius * math.sin(ang))

        # rotación tangente a la circunferencia
        rot = math.degrees(ang) + 90.0
        if flip:
            rot -= 180.0  # enderezar

        # canvas temporal para el carácter
        ch_w, ch_h = _text_size(d, ch, font)
        cw = max(int(8 * SCALE), int(ch_w + 12 * SCALE))
        chh = max(int(8 * SCALE), int(ch_h + 12 * SCALE))

        tmp = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        td.text(
            (cw // 2, chh // 2),
            ch,
            font=font,
            fill="white",
            anchor="mm",
            stroke_width=int(5 * SCALE),
            stroke_fill=(0, 0, 0, 220),
        )
        tmp = tmp.rotate(rot, expand=True, resample=Image.BICUBIC)

        base_img.alpha_composite(tmp, (int(px - tmp.width // 2), int(py - tmp.height // 2)))


# ---------------------------------------------
# (opcional) texto radial, por si quisieras alternar
# ---------------------------------------------
def _render_label_radial(base_img: Image.Image,
                         label: str,
                         center: Tuple[int, int],
                         mid_deg: float,
                         r: int,
                         slice_deg: float):
    cx, cy = center
    mid_rad = math.radians(mid_deg)

    # caja disponible pensando en texto radial (menos usado ahora)
    thickness = int((OUTER_RATIO - INNER_RATIO) * r)
    mid_radius = ((INNER_RATIO + OUTER_RATIO) / 2.0) * r
    arc_span = 2.0 * mid_radius * math.sin(math.radians(slice_deg) / 2.0)

    max_w = int(thickness * 0.95)   # ancho radial
    max_h = int(arc_span * 0.92)    # alto a lo largo del arco

    # fuente grande
    font = _font(int(BASE_FONT_SIZE * SCALE))
    # medir “label” en una fila (si no encaja, el texto quedará más pequeño)
    probe = Image.new("RGBA", (int(2*mid_radius)+200, int(2*mid_radius)+200), (0, 0, 0, 0))
    d = ImageDraw.Draw(probe)
    tw, th = _text_size(d, label, font)

    # lienzo del bloque
    bw = max(int(tw + 24 * SCALE), 12)
    bh = max(int(th + 24 * SCALE), 12)
    block = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(block)
    bd.text(
        (bw // 2, bh // 2),
        label,
        fill="white",
        font=font,
        anchor="mm",
        stroke_width=int(5 * SCALE),
        stroke_fill=(0, 0, 0, 220),
    )

    # rotación para alinear con el radio
    rot = mid_deg - 90.0
    if rot > 90:  rot -= 180
    if rot < -90: rot += 180
    block = block.rotate(rot, expand=True, resample=Image.BICUBIC)

    # posición del centro del bloque en el anillo
    mid_ratio = (INNER_RATIO + OUTER_RATIO) / 2.0
    rx = cx + int(mid_ratio * r * math.cos(mid_rad))
    ry = cy - int(mid_ratio * r * math.sin(mid_rad))

    px = int(rx - block.width // 2)
    py = int(ry - block.height // 2)
    base_img.alpha_composite(block, (px, py))


# ---------------------------------------------
# Construcción de la ruleta
# ---------------------------------------------
def make_wheel_base64(segments: List[str], size: int = WHEEL_SIZE) -> str:
    n = len(segments)
    assert n >= 3, "Se requieren al menos 3 segmentos"

    SIZE = int(size * SCALE)
    r = SIZE // 2
    img = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    bbox = (0, 0, SIZE, SIZE)

    # sombra suave
    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((10, 10, SIZE-10, SIZE-10), fill=(0, 0, 0, 40))
    img.alpha_composite(shadow, (0, 0))

    # fondo
    d.ellipse(bbox, fill="#f8fafc")

    # ángulo por sector
    slice_deg = 360.0 / n

    # sectores + separadores
    for i in range(n):
        start = i * slice_deg
        end   = (i + 1) * slice_deg
        color = PALETTE[i % len(PALETTE)]
        d.pieslice(bbox, start, end, fill=color, outline="white", width=int(3 * SCALE))

        a = math.radians(start)
        x = int(r + r * math.cos(a))
        y = int(r - r * math.sin(a))
        d.line((r, r, x, y), fill=(255, 255, 255, 255), width=int(2 * SCALE))

    # etiquetas
    center = (r, r)
    for i, label in enumerate(segments):
        start = i * slice_deg
        end   = (i + 1) * slice_deg
        mid_deg = (start + end) / 2.0

        if TEXT_STYLE == "tangent":
            _render_label_tangent(img, label, center, mid_deg, r, slice_deg)
        else:
            _render_label_radial(img, label, center, mid_deg, r, slice_deg)

    # aro y centro
    d.ellipse(bbox, outline="#ffffff", width=int(6 * SCALE))
    hub_r = int(r * 0.10)
    d.ellipse((r - hub_r, r - hub_r, r + hub_r, r + hub_r),
              fill="#ffffff", outline="#e5e7eb", width=int(3 * SCALE))

    # downscale para nitidez
    final = img.resize((int(size), int(size)), Image.LANCZOS)
    buf = io.BytesIO()
    final.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")
