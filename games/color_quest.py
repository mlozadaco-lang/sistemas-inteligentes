# -*- coding: utf-8 -*-
# Minijuego: "Color Quest" — Elige la mejor combinación de color (3 rondas)

import flet as ft

# Cada ronda: target color + 3 opciones + índice correcto
ROUNDS = [
    ("#3B82F6", ["#EF4444", "#0EA5E9", "#F59E0B"], 0),  # Complementario aprox a azul ~ rojo
    ("#10B981", ["#6B7280", "#FDE68A", "#059669"], 1),  # Verde con acento cálido claro
    ("#9333EA", ["#A78BFA", "#22C55E", "#111827"], 0),  # Monocromático/luz
]

def swatch(hex_color, label=None, width=160, height=50):
    t = ft.Text(label or hex_color, color="#FFFFFF" if hex_color != "#FDE68A" else "#111111")
    return ft.Container(content=ft.Row([t], alignment=ft.MainAxisAlignment.CENTER),
                        width=width, height=height, bgcolor=hex_color, border_radius=8)

def build_color_quest(on_finish):
    title = ft.Text("🎨 Color Quest (Arte y Diseño)", weight=ft.FontWeight.W_600, size=16)
    info  = ft.Text("Elige la opción que MEJOR combina con el color objetivo. 3 rondas.", size=12)

    i = {"round": 0, "correct": 0}
    target = ft.Container(width=680, height=40, border_radius=8)
    opts_row = ft.Column(spacing=8)
    feedback = ft.Text("", size=12)

    def render_round():
        feedback.value = ""
        base, opts, good = ROUNDS[i["round"]]
        target.bgcolor = base
        opts_row.controls.clear()
        for idx, oc in enumerate(opts):
            btn = ft.ElevatedButton(
                content=ft.Row([swatch(oc)], alignment=ft.MainAxisAlignment.START),
                on_click=lambda e, k=idx, g=good: choose(k, g),
                bgcolor=oc, style=ft.ButtonStyle(color={"": "#FFFFFF"}), width=680
            )
            opts_row.controls.append(btn)

    def choose(k, good):
        if k == good:
            i["correct"] += 1
            feedback.value = "✅ ¡Buen ojo!"
        else:
            feedback.value = "❌ Hay otra opción que armoniza mejor."
        next_round()

    def next_round():
        i["round"] += 1
        if i["round"] >= len(ROUNDS):
            score = int(i["correct"] / len(ROUNDS) * 100)
            on_finish({
                "game": "color_quest",
                "area": "Arte y Diseño",
                "score": score,
                "why": f"Aciertos: {i['correct']} / {len(ROUNDS)}"
            })
            return
        render_round()
        container.update()

    container = ft.Container(
        content=ft.Column([title, info, ft.Text("Objetivo:"), target, opts_row, feedback], spacing=8),
        padding=10, border=ft.border.all(1, "#E5E7EB"), border_radius=12, bgcolor="#FFFFFF"
    )
    render_round()
    return container
