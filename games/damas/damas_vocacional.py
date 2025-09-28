# -*- coding: utf-8 -*-
"""
Damas Vocacional
- Modo standalone (pygame): run_damas()
- Modo Flet (como ruleta): open_damas_dialog(page, on_finish)

on_finish recibe:
  {"game": "Damas Vocacional", "area": DAMAS_AREA, "score": 0..100, "why": "..."}
"""
from __future__ import annotations
import os, sys, json
from datetime import datetime

# --- pygame es opcional si solo usas el modal de Flet ---
try:
    import pygame
except Exception:  # no disponible en algunos entornos
    pygame = None

# -----------------------------
# Configuración / colores / área
# -----------------------------
ANCHO, ALTO = 1200, 800           # 800 tablero + panel lateral
TAB_W = 800
TAM_CASILLA = TAB_W // 8

BLANCO   = (255, 255, 255)
NEGRO    = (0, 0, 0)
ROJO     = (200, 50, 50)
AZUL     = (50, 50, 200)
VERDE    = (0, 200, 0)
AMARILLO = (200, 200, 0)
GRISUI   = (220, 220, 220)

# Ajusta al nombre exacto en tu catálogo AREAS
DAMAS_AREA = "Tecnología"

# -----------------------------
# Utilidades de rutas
# -----------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))  # raíz del proyecto

def _p(*parts: str) -> str:
    return os.path.join(ROOT, *parts)

# -----------------------------
# Preguntas desde JSON (opcional)
# -----------------------------
def cargar_preguntas(ruta: str | None = None):
    ruta = ruta or _p("games", "damas", "questions.json")
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and data:
                return data
    except FileNotFoundError:
        print("⚠️ No se encontró questions.json, usaré preguntas por defecto.")
    except Exception as e:
        print(f"⚠️ Error leyendo preguntas: {e}")

    return [
        {"pregunta": "¿Qué actividad disfrutas más?",
         "opciones": ["Resolver problemas", "Leer", "Trabajar en equipo", "Diseñar"]},
        {"pregunta": "¿Qué herramienta te atrae?",
         "opciones": ["Códigos", "Historias", "Microscopio", "Lienzo"]},
    ]

# -----------------------------
# Registro de respuestas (Excel)
# -----------------------------
class VocationalRecorder:
    def __init__(self, archivo: str | None = None):
        self.archivo = archivo or _p("data", "Respuestas_Registradas.xlsx")
        os.makedirs(os.path.dirname(self.archivo), exist_ok=True)
        self.respuestas = []

    def registrar(self, jugador: int, pregunta: str, respuesta: str):
        self.respuestas.append({
            "jugador": jugador,
            "pregunta": pregunta,
            "respuesta": respuesta,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    def guardar(self):
        if not self.respuestas:
            return
        try:
            import pandas as pd
            nuevo = pd.DataFrame(self.respuestas)
            if os.path.exists(self.archivo):
                viejo = pd.read_excel(self.archivo)
                out = pd.concat([viejo, nuevo], ignore_index=True)
            else:
                out = nuevo
            out.to_excel(self.archivo, index=False)
            print(f"📂 Respuestas guardadas en {self.archivo}")
        except Exception as e:
            print(f"⚠️ No se pudo guardar Excel: {e}")

# =========================================================
# ==============   MODO PYGAME (standalone)   =============
# =========================================================
def crear_tablero():
    t = [[0]*8 for _ in range(8)]
    for fila in range(3):            # Jugador 2 (azul) arriba
        for col in range(8):
            if (fila+col) % 2 != 0:
                t[fila][col] = 2
    for fila in range(5, 8):         # Jugador 1 (rojo) abajo
        for col in range(8):
            if (fila+col) % 2 != 0:
                t[fila][col] = 1
    return t

def dibujar_tablero(s):
    s.fill(NEGRO)
    for f in range(8):
        for c in range(8):
            if (f + c) % 2 == 0:
                pygame.draw.rect(s, BLANCO, (c*TAM_CASILLA, f*TAM_CASILLA, TAM_CASILLA, TAM_CASILLA))

def dibujar_fichas(s, t):
    for f in range(8):
        for c in range(8):
            v = t[f][c]
            if v:
                color = ROJO if v == 1 else AZUL
                pygame.draw.circle(
                    s, color,
                    (c*TAM_CASILLA + TAM_CASILLA//2, f*TAM_CASILLA + TAM_CASILLA//2),
                    TAM_CASILLA//2 - 10
                )

def movimientos_validos(t, f, c):
    j = t[f][c]
    if j == 0:
        return []
    dirs = [(-1,-1), (-1,1), (1,-1), (1,1)]
    moves = []
    for df, dc in dirs:
        nf, nc = f+df, c+dc
        if 0 <= nf < 8 and 0 <= nc < 8:
            if t[nf][nc] == 0:
                moves.append((nf, nc, "normal"))
            elif t[nf][nc] != j:
                sf, sc = nf+df, nc+dc
                if 0 <= sf < 8 and 0 <= sc < 8 and t[sf][sc] == 0:
                    moves.append((sf, sc, "captura"))
    return moves

def resaltar_movs(s, moves):
    for f, c, tipo in moves:
        col = VERDE if tipo == "normal" else AMARILLO
        pygame.draw.rect(s, col, (c*TAM_CASILLA, f*TAM_CASILLA, TAM_CASILLA, TAM_CASILLA), 5)

def dibujar_panel(s, turno, puntos):
    font_t = pygame.font.SysFont(None, 40, bold=True)
    font_p = pygame.font.SysFont(None, 30)
    pygame.draw.rect(s, GRISUI, (TAB_W, 0, ANCHO-TAB_W, ALTO))
    s.blit(font_t.render("TEST DAMAS VOCACIONAL", True, NEGRO), (TAB_W+10, 30))
    s.blit(font_p.render(f"Turno: {'ROJO' if turno==1 else 'AZUL'}", True, NEGRO), (TAB_W+10, 100))
    s.blit(font_p.render(f"Rojo: {puntos[1]} pts", True, ROJO), (TAB_W+10, 160))
    s.blit(font_p.render(f"Azul: {puntos[2]} pts", True, AZUL), (TAB_W+10, 200))

def _pregunta_tk(pregunta: dict, jugador: int) -> str | None:
    """Muestra pregunta con Tkinter; si falla, devuelve 1ª opción."""
    try:
        import tkinter as tk
    except Exception:
        ops = pregunta.get("opciones") or []
        return ops[0] if ops else None

    resp = {"v": None}
    def sel(o): resp["v"] = o; root.destroy()

    root = tk.Tk()
    root.title(f"Pregunta Jugador {jugador}")
    root.geometry("420x320"); root.resizable(False, False)
    tk.Label(root, text=pregunta["pregunta"], wraplength=360, font=("Arial", 12)).pack(pady=20)
    for o in (pregunta.get("opciones") or []):
        tk.Button(root, text=o, width=32, command=lambda x=o: sel(x)).pack(pady=5)
    root.mainloop()
    return resp["v"]

def pantalla_final(s, ganador, perdedor):
    font = pygame.font.SysFont(None, 50, bold=True)
    s.fill(BLANCO)
    s.blit(font.render(f"Ganador: {'Rojo' if ganador==1 else 'Azul'}", True, NEGRO), (200, 300))
    carreras = ["Ingeniería", "Psicología", "Medicina", "Arte"]
    s.blit(font.render(f"Recomendación ganador: {carreras[ganador % len(carreras)]}", True, ROJO), (200, 380))
    s.blit(font.render(f"Recomendación perdedor: {carreras[perdedor % len(carreras)]}", True, AZUL), (200, 450))
    pygame.display.flip(); pygame.time.wait(3000)

def run_damas(questions_path: str | None = None, output_excel: str | None = None, use_tk: bool = True):
    """Ejecución del juego en pygame."""
    if pygame is None:
        print("⚠️ pygame no está disponible en este entorno.")
        return

    pygame.init()
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Damas test vocacional")

    questions = cargar_preguntas(questions_path)
    recorder  = VocationalRecorder(output_excel)

    tablero = crear_tablero()
    turno = 1
    reloj = pygame.time.Clock()
    seleccionado = None
    puntos = {1: 0, 2: 0}
    q_index = {1: 0, 2: 0}

    running = True
    while running:
        dibujar_tablero(ventana); dibujar_fichas(ventana, tablero)
        if seleccionado:
            resaltar_movs(ventana, movimientos_validos(tablero, *seleccionado))
        dibujar_panel(ventana, turno, puntos)
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                recorder.guardar(); running = False
            if ev.type == pygame.MOUSEBUTTONDOWN:
                x, y = ev.pos
                if x < TAB_W:
                    c, f = x // TAM_CASILLA, y // TAM_CASILLA
                    if tablero[f][c] == turno:
                        seleccionado = (f, c)
                    elif seleccionado:
                        f0, c0 = seleccionado
                        for nf, nc, tipo in movimientos_validos(tablero, f0, c0):
                            if (nf, nc) == (f, c):
                                tablero[f][c] = turno
                                tablero[f0][c0] = 0
                                if tipo == "captura":
                                    puntos[turno] += 1
                                    if q_index[turno] < len(questions):
                                        q = questions[q_index[turno]]
                                        resp = _pregunta_tk(q, turno) if use_tk else (q["opciones"][0] if q.get("opciones") else None)
                                        if resp: recorder.registrar(turno, q["pregunta"], resp)
                                        q_index[turno] += 1
                                turno = 2 if turno == 1 else 1
                                seleccionado = None
                                if puntos[1] >= 12 or puntos[2] >= 12:
                                    ganador = 1 if puntos[1] >= 12 else 2
                                    perdedor = 2 if ganador == 1 else 1
                                    recorder.guardar()
                                    pantalla_final(ventana, ganador, perdedor)
                                    running = False
                                break

        reloj.tick(30)

    pygame.quit()

# =========================================================
# ==============   MODO FLET (modal estilo ruleta)  =======
# =========================================================
def open_damas_dialog(page, on_finish):
    """
    Abre un diálogo tipo bottom-sheet para registrar el score de Damas.
    Compatible con Flet antiguo (BottomSheet) y nuevo (ModalBottomSheet).
    """
    import flet as ft

    score = ft.Slider(min=0, max=100, value=70, divisions=20, width=320)
    lbl = ft.Text("Valora tu desempeño en Damas (0–100): 70")

    def on_change(e):
        lbl.value = f"Valora tu desempeño en Damas (0–100): {int(score.value)}"
        page.update()
    score.on_change = on_change

    # UI del sheet
    content = ft.Container(
        padding=20,
        content=ft.Column(
            tight=True,
            spacing=12,
            controls=[
                ft.Text("♟ Damas Vocacional", size=18, weight=ft.FontWeight.W_600),
                ft.Text("Cuando termines el juego externo, registra tu puntaje aquí."),
                lbl, score,
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.ElevatedButton("Guardar puntaje"),
                        ft.OutlinedButton("Cancelar"),
                    ],
                ),
            ],
        ),
    )

    # Elegir componente según versión de Flet
    if hasattr(ft, "ModalBottomSheet"):
        sheet = ft.ModalBottomSheet(content=content)

        def _open():
            page.open(sheet)

        def _close():
            page.close(sheet)

        # conectar botones
        content.content.controls[-1].controls[0].on_click = lambda e: (
            _close(),
            on_finish({
                "game": "Damas Vocacional",
                "area": DAMAS_AREA,
                "score": int(score.value),
                "why": "Juego estratégico que evalúa razonamiento lógico y planificación.",
            })
        )
        content.content.controls[-1].controls[1].on_click = lambda e: _close()

        _open()

    else:
        # Flet clásico: BottomSheet + overlay
        sheet = ft.BottomSheet(content=content)

        def _open():
            if sheet not in page.overlay:
                page.overlay.append(sheet)
            sheet.open = True
            page.update()

        def _close():
            sheet.open = False
            page.update()

        # conectar botones
        content.content.controls[-1].controls[0].on_click = lambda e: (
            _close(),
            on_finish({
                "game": "Damas Vocacional",
                "area": DAMAS_AREA,
                "score": int(score.value),
                "why": "Juego estratégico que evalúa razonamiento lógico y planificación.",
            })
        )
        content.content.controls[-1].controls[1].on_click = lambda e: _close()

        _open()
        
if __name__ == "__main__":
    run_damas()
