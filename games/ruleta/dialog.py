# -*- coding: utf-8 -*-
import math, random, asyncio
import flet as ft
from .config import (
    PRIMARY, BORDER, WHEEL_SIZE, POINTER_SIZE, ANIMATION_MS,
    SEGMENTS,
)
from .draw import make_wheel_base64
from .questions import get_question

def open_ruleta_dialog(page: ft.Page, on_finish, spins_range=(5, 8)):
    """
    Muestra la ruleta animada y hace 1 pregunta por giro.
    on_finish recibe: {"game":"ruleta","area":..., "score":0..100, "why":...}
    """
    segments = SEGMENTS[:]                 # copia
    n = len(segments)
    slice_angle = 2 * math.pi / n
    BASE_OFFSET = -math.pi/2 + slice_angle/2  # sector 0 centrado bajo la flecha

    state = {"busy": False, "rounds": 0, "tally": {a: 0.0 for a in segments}}

    wheel = ft.Image(src_base64=make_wheel_base64(segments), width=WHEEL_SIZE, height=WHEEL_SIZE)
    wheel.rotate = ft.Rotate(angle=0.0, alignment=ft.alignment.center)
    wheel.animate_rotation = ft.Animation(ANIMATION_MS, ft.AnimationCurve.DECELERATE)

    pointer = ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=POINTER_SIZE, color="orange")

    lbl_rounds = ft.Text("Rondas respondidas: 0", size=12, color="#555")
    lbl_winner = ft.Text("", size=13, weight=ft.FontWeight.W_500)
    q_text = ft.Text("", size=14)
    opts_col = ft.Column(spacing=8)

    btn_spin = ft.ElevatedButton(text="Girar", icon=ft.Icons.CASINO, bgcolor=PRIMARY, color="white")
    btn_close = ft.OutlinedButton(text="Cerrar y enviar")

    stack = ft.Stack(
        controls=[
            wheel,
            ft.Container(
                content=ft.Row([pointer], alignment=ft.MainAxisAlignment.CENTER),
                width=WHEEL_SIZE, height=WHEEL_SIZE, alignment=ft.alignment.top_center
            ),
        ],
        width=WHEEL_SIZE, height=WHEEL_SIZE
    )

    panel = ft.Container(
        content=ft.Column(
            [
                ft.Text("🎡 Ruleta Vocacional", weight=ft.FontWeight.W_600, size=16),
                ft.Text("Gira la ruleta. El segmento bajo la flecha es el ganador.", size=12),
                lbl_rounds,
                stack,
                lbl_winner,
                q_text,
                opts_col,
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=16, border=ft.border.all(1, BORDER), border_radius=14, bgcolor="white",
        width=WHEEL_SIZE + 40,
    )

    dlg = ft.AlertDialog(
        modal=True,
        content=panel,
        actions=[btn_spin, btn_close],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )

    # --- helpers abrir/cerrar (compat) ---
    def open_dialog():
        try:
            page.open(dlg)
        except Exception:
            page.dialog = dlg
            dlg.open = True
            page.update()

    def close_dialog(_=None):
        try:
            page.close(dlg)
        except Exception:
            dlg.open = False
            page.update()

    # --- preguntas ---
    def render_question(area: str):
        q_text.value = ""
        opts_col.controls.clear()
        q, opts = get_question(area)
        q_text.value = f"❓ {q}"

        def pick(w: float):
            state["tally"][area] += float(w)
            state["rounds"] += 1
            lbl_rounds.value = f"Rondas respondidas: {state['rounds']}"
            btn_spin.disabled = False
            panel.update()

        for label, w in opts:
            opts_col.controls.append(
                ft.ElevatedButton(
                    text=label,
                    on_click=lambda e, ww=w: pick(ww),
                    width=360,
                    bgcolor=PRIMARY,
                    color="white",
                )
            )

    # --- giro ---
    async def spin_task():
        if state["busy"]:
            return
        state["busy"] = True
        btn_spin.disabled = True
        panel.update()

        idx = random.randrange(n)  # sector ganador
        full_turns = random.randint(*spins_range)
        final_angle = full_turns * 2 * math.pi + BASE_OFFSET + idx * slice_angle

        wheel.rotate = ft.Rotate(angle=final_angle, alignment=ft.alignment.center)
        page.update()
        await asyncio.sleep((wheel.animate_rotation.duration + 200) / 1000)

        winner = segments[idx]
        lbl_winner.value = f"Ganó: {winner} 🎯"
        render_question(winner)

        state["busy"] = False
        panel.update()

    # --- cerrar + enviar ---
    def finalize_and_send(_):
        r = state["rounds"]
        if r <= 0:
            close_dialog()
            on_finish({"game":"ruleta","area":"Sin datos","score":0,"why":"No se respondieron rondas."})
            return
        ranked = sorted(state["tally"].items(), key=lambda kv: kv[1], reverse=True)
        best_area, best = ranked[0]
        score = int((best / r) * 100)
        top3 = ", ".join([f"{a}:{v:.1f}" for a, v in ranked[:3]])
        close_dialog()
        on_finish({
            "game":"ruleta",
            "area":best_area,
            "score":score,
            "why": f"Afinidad acumulada → {top3} (de {r} rondas). Rueda procedural"
        })

    # wire-up
    btn_spin.on_click  = lambda e: page.run_task(spin_task)
    btn_close.on_click = finalize_and_send

    open_dialog()
