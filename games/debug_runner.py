# -*- coding: utf-8 -*-
# Minijuego: "Debug Runner" — Encuentra la secuencia con error (3 rondas)

import flet as ft

ROUNDS = [
    # cada ronda: lista de 4 secuencias (texto) y el índice (0-based) de la que tiene "error"
    (["2, 4, 6, 8", "1, 3, 5, 7", "10, 12, 14, 17", "0, 5, 10, 15"], 2),
    (["5, 10, 15, 21", "3, 6, 9, 12", "7, 14, 21, 28", "4, 8, 12, 16"], 0),
    (["1, 2, 3, 5", "2, 4, 8, 16", "9, 7, 5, 3", "10, 20, 30, 40"], 0),
]

def build_debug_runner(on_finish):
    """Devuelve un Container con el juego. Llamará a on_finish(result_dict)."""
    title = ft.Text("🔧 Debug Runner (Tecnología)", weight=ft.FontWeight.W_600, size=16)
    info  = ft.Text("Toca la SECUENCIA con ERROR en el patrón. 3 rondas.", size=12)

    i = {"round": 0, "correct": 0}  # estado mutable simple

    seqs_col = ft.Column(spacing=8)
    feedback = ft.Text("", size=12)

    def render_round():
        seqs_col.controls.clear()
        feedback.value = ""
        seqs, bad_idx = ROUNDS[i["round"]]
        for idx, s in enumerate(seqs):
            btn = ft.ElevatedButton(
                content=ft.Text(f"Secuencia {idx+1}: {s}"),
                on_click=lambda e, k=idx, b=bad_idx: choose(k, b),
                bgcolor="#4F46E5", style=ft.ButtonStyle(color={"": "#FFFFFF"}),
                width=680
            )
            seqs_col.controls.append(btn)

    def choose(k, bad_idx):
        if k == bad_idx:
            i["correct"] += 1
            feedback.value = "✅ ¡Bien visto! +1"
        else:
            feedback.value = "❌ Esa no era. Observa el patrón."
        next_round()

    def next_round():
        i["round"] += 1
        if i["round"] >= len(ROUNDS):
            score = int(i["correct"] / len(ROUNDS) * 100)
            on_finish({
                "game": "debug_runner",
                "area": "Tecnología",
                "score": score,
                "why": f"Aciertos: {i['correct']} / {len(ROUNDS)}"
            })
            return
        render_round()
        container.update()

    container = ft.Container(
        content=ft.Column([title, info, seqs_col, feedback], spacing=8),
        padding=10, border=ft.border.all(1, "#E5E7EB"), border_radius=12, bgcolor="#FFFFFF"
    )
    render_round()
    return container
