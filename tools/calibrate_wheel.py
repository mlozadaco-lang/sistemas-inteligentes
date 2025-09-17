# -*- coding: utf-8 -*-
import sys, math, cv2, numpy as np
import easyocr
from rapidfuzz import process, fuzz

EXPECTED = [
    "Seguridad","Tecnología","Arte y cultura","Comunicación",
    "Cs. Exactas","Cs. Humanas","Cs. Naturales",
    "Educación","Oficios","Salud",
]

def angle_from_top_clockwise(cx, cy, x, y):
    # 0 rad = arriba; sentido horario positivo
    return (math.atan2(x - cx, cy - y) % (2*math.pi))

def main(path):
    img = cv2.imread(path)
    if img is None:
        print(f"ERROR: no pude abrir {path}"); return
    h, w = img.shape[:2]
    cx, cy = w/2.0, h/2.0

    reader = easyocr.Reader(['es','en'], gpu=False)
    results = reader.readtext(img, detail=1, paragraph=False)  # [(box, text, conf), ...]

    items = []
    for box, text, conf in results:
        if conf < 0.25: 
            continue
        # centro del bbox
        xs = [p[0] for p in box]; ys = [p[1] for p in box]
        x, y = sum(xs)/4, sum(ys)/4
        theta = angle_from_top_clockwise(cx, cy, x, y)
        # emparejar con etiqueta esperada
        label, score, *_ = process.extractOne(text, EXPECTED, scorer=fuzz.WRatio)
        if score >= 60:
            items.append((theta, label))

    if not items:
        print("No se reconoció texto suficiente. Sube contraste o usa una imagen más nítida.")
        return

    # promediar ángulos por etiqueta
    by = {}
    for th, lab in items:
        by.setdefault(lab, []).append(th)
    labeled = []
    for lab, arr in by.items():
        arr.sort()
        labeled.append((sum(arr)/len(arr), lab))

    # ordenar horario desde la parte superior (0 rad)
    labeled.sort()
    segments = [lab for _, lab in labeled]
    n = len(segments)
    slice_angle = 2*math.pi/n

    # estimar OFFSET: diferencia media entre cada centro observado y el ideal i*slice
    diffs = []
    for i, (th, _) in enumerate(labeled):
        ideal = i * slice_angle
        d = (th - ideal + math.pi) % (2*math.pi) - math.pi  # a rango [-pi, pi]
        diffs.append(d)
    offset_rad = sum(diffs)/len(diffs)
    offset_deg = round(math.degrees(offset_rad), 1)

    print("\n✅ Sugerencias para pegar en games/ruleta_spin.py:\n")
    print("SEGMENTS = [")
    for s in segments:
        print(f'    "{s}",')
    print("]")
    print(f"OFFSET_DEG = {offset_deg}  # ajusta ±{round(180/n,1)} si queda medio sector corrido\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python tools/calibrate_wheel.py assets/ruleta_areas.png")
    else:
        main(sys.argv[1])
