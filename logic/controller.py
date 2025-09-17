# -*- coding: utf-8 -*-
# Orquesta el flujo: menú, test, favoritas, texto libre, resultados

import json
import datetime
import flet as ft
from ui.widgets import HEX, bubble, primary_btn
from data.catalog import AREAS, QUESTIONS, SEED_FAVORITES
from logic.engine import smart_infer_area, suggest_profession, normalized_scores
from services.exporter import export_all
from games.debug_runner import build_debug_runner
from games.color_quest import build_color_quest
from games.ruleta import open_ruleta_dialog

class AssistantController:
    def __init__(self, page: ft.Page):
        self.page = page

        # -------- Estado --------
        self.stage = "menu"   # menu | test | result | favorites
        self.q_index = 0
        self.scores = {a: 0 for a in AREAS}
        self.game_scores = {a: 0.0 for a in AREAS}   # suma de puntajes
        self.game_counts = {a: 0   for a in AREAS}   # cuántos juegos por área
        self.last_area = None
        self.last_prof_index = 0
        self.last_result = None
        self.favorites: list[str] = SEED_FAVORITES.copy()

        # -------- UI (chat principal) --------
        self.chat = ft.ListView(expand=True, spacing=8, auto_scroll=True, padding=12)
        self.quick = ft.Row(spacing=8, wrap=True, alignment=ft.MainAxisAlignment.START)
        self.entry = ft.TextField(
            hint_text="Escribe aquí… (o usa los botones)",
            expand=True, border_radius=22, bgcolor="#FFFFFF", border_color=HEX["BORDER"]
        )
        self.send = ft.FloatingActionButton(icon=ft.Icons.SEND, bgcolor=HEX["PRIMARY"], mini=True)
        self.entry.on_submit = self.on_send
        self.send.on_click = self.on_send

        # -------- Panel de estado del test --------
        self.progress_label = ft.Text("", size=12, color="#555")
        self.progress_bar = ft.ProgressBar(width=740, value=0)
        self.area_rows = {a: ft.ProgressBar(width=740, value=0) for a in AREAS}
        self.status_container = ft.Container(
            content=ft.Column(
                [self.progress_label, self.progress_bar, ft.Divider()] +
                [ft.Column([ft.Text(a, size=12), self.area_rows[a]], spacing=4) for a in AREAS],
                spacing=6
            ),
            visible=False,
            padding=8,
            border=ft.border.all(1, HEX["BORDER"]),
            border_radius=12,
            bgcolor="#FFFFFF",
        )

        # Para atajos con teclado (1..5)
        self.current_handlers: list = []
        self.page.on_keyboard_event = self.on_key

    # ---------- Montaje ----------
    def mount(self):
        self.page.appbar = ft.AppBar(title=ft.Text("Chatbot de Orientación Vocacional"))
        self.page.add(
            ft.Container(
                ft.Column(
                    [
                        self.chat,
                        self.status_container,  # aparece solo en test
                        self.quick,
                        ft.Row([self.entry, self.send]),
                    ],
                    expand=True,
                    spacing=10,
                ),
                expand=True,
                padding=10,
            )
        )
        self.welcome()

    # ---------- Helpers UI ----------
    def add_bot(self, text: str):
        self.chat.controls.append(bubble(text, user=False))
        self.page.update()

    def add_user(self, text: str):
        self.chat.controls.append(bubble(text, user=True))
        self.page.update()

    def set_quick(self, buttons: list[ft.Control]):
        self.quick.controls.clear()
        self.quick.controls.extend(buttons)
        self.page.update()

    def show_status(self, show: bool):
        self.status_container.visible = show
        self.page.update()

    def update_status(self):
        total = len(QUESTIONS)
        cur = min(self.q_index, total)
        self.progress_label.value = f"Progreso del test: {cur}/{total}"
        self.progress_bar.value = (cur / total) if total else 0

        norm = normalized_scores(self.scores)
        for a in AREAS:
            self.area_rows[a].value = max(0.0, min(1.0, norm[a]))
        self.page.update()

    # ---------- Pantallas ----------
    def menu_buttons(self):
        return [
            primary_btn("Jugar minijuegos", lambda e: self.open_games_menu()),
            primary_btn("Test vocacional", lambda e: self.go_test()),
            ft.OutlinedButton(text="Contarte mis intereses", on_click=lambda e: self.explain_free_text()),
            ft.OutlinedButton(text="Mis favoritas", on_click=lambda e: self.open_favorites()),
            ft.OutlinedButton(text="Exportar resultado", on_click=lambda e: self.export_result()),
        ]

    def welcome(self):
        self.add_bot("¡Hola 👋 Soy tu asistente virtual!")
        # Recuperar último resultado (si existe)
        try:
            raw = self.page.client_storage.get("last_result")
            if raw:
                self.last_result = json.loads(raw)
                if self.last_result.get("top3"):
                    self.add_bot(f"Última vez tu Top fue: {', '.join(self.last_result['top3'])}.")
        except Exception:
            pass
        # Recuperar favoritas personalizadas
        try:
            fav_raw = self.page.client_storage.get("favorites")
            if fav_raw:
                self.favorites = json.loads(fav_raw)
        except Exception:
            pass
        self.add_bot("¿Qué te gustaría hacer?")
        self.set_quick(self.menu_buttons())

    # ---------- Favoritas ----------
    def open_favorites(self):
        self.stage = "favorites"
        self.add_bot("Selecciona / deselecciona tus profesiones favoritas y guarda cambios.")
        # UI simple con Checkboxes
        checks = []
        # Listado plano a partir de todas las áreas
        all_roles = [r for roles in AREAS.values() for r in roles]
        self._fav_checks = {}
        for r in all_roles:
            cb = ft.Checkbox(label=r, value=(r in self.favorites))
            self._fav_checks[r] = cb
            checks.append(cb)

        def save_favs(e):
            self.favorites = [role for role, cb in self._fav_checks.items() if cb.value]
            self.page.client_storage.set("favorites", json.dumps(self.favorites, ensure_ascii=False))
            self.add_bot("✅ Guardé tus favoritas. ¡Listo!")
            self.back_to_menu()

        self.set_quick([
            primary_btn("Guardar favoritas", save_favs),
            ft.OutlinedButton(text="Volver al menú", on_click=lambda e: self.back_to_menu()),
        ])

        # Mostrar lista dentro del chat como bloque (scroll interno del chat)
        self.chat.controls.append(
            ft.Container(
                content=ft.Column(checks, tight=True, spacing=4),
                padding=10,
                border=ft.border.all(1, HEX["BORDER"]),
                border_radius=12,
                bgcolor="#FFFFFF",
            )
        )
        self.page.update()

    # ---------- Test ----------
    def go_test(self):
        self.stage = "test"
        self.q_index = 0
        for k in self.scores: self.scores[k] = 0
        self.add_bot("Haré preguntas rápidas; elige **1 opción** por pregunta.")
        self.show_status(True)
        self.update_status()
        self.ask_question()

    def ask_question(self):
        i = self.q_index
        if i >= len(QUESTIONS):
            self.finish_test(); return

        qd = QUESTIONS[i]
        self.add_bot(f"{i+1:02d}. {qd['q']}")

        self.current_handlers = []
        opts = []
        for label, area in qd["opts"]:
            def make(area_name, label_text):
                def _h(e):
                    self.add_user(label_text)
                    self.scores[area_name] += 1
                    self.q_index += 1
                    self.update_status()
                    self.ask_question()
                return _h
            h = make(area, label)
            self.current_handlers.append(h)
            opts.append(primary_btn(label, h))
        self.set_quick(opts)

    def finish_test(self):
        self.stage = "result"
        self.show_status(False)

        # --- 1) Normalizados del TEST (0..1) ---
        test_norm = normalized_scores(self.scores)  # dict área -> float

        # --- 2) Promedio de JUEGOS por área (0..100) ---
        def _avg_game(a: str) -> float:
            return (self.game_scores[a] / self.game_counts[a]) if self.game_counts[a] else 0.0

        any_games = sum(self.game_counts.values()) > 0
        w_test = 0.7 if any_games else 1.0
        w_games = 0.3 if any_games else 0.0

        # --- 3) Mezcla (blended) ---
        blended = {
            a: w_test * test_norm[a] + w_games * (_avg_game(a) / 100.0)
            for a in AREAS
        }
        blended_ranked = sorted(blended.items(), key=lambda kv: kv[1], reverse=True)

        # Área ganadora y Top3 según mezcla
        area = blended_ranked[0][0]
        top3 = [a for a, _ in blended_ranked[:3]]
        self.last_area = area
        self.last_prof_index = 0

        # Profesión sugerida (fav si existe en el área ganadora)
        base_prof = self._pick_profession_with_favorites(area) or area

        # --- 4) Guardar resultado (incluye info del blend) ---
        self.last_result = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scores": self.scores.copy(),  # crudos del test (conteos)
            "normalized_test": {k: round(v, 2) for k, v in test_norm.items()},  # 0..1
            "games_avg": {a: round(_avg_game(a), 1) for a in AREAS},            # 0..100
            "weights": {"test": w_test, "games": w_games},
            "blended": {k: round(v, 2) for k, v in blended.items()},            # 0..1
            "top3": top3,
            "area": area,
            "profession": base_prof,
            "favorites": self.favorites,
        }
        self.page.client_storage.set("last_result", json.dumps(self.last_result, ensure_ascii=False))

        # --- 5) Mensaje al usuario + acciones ---
        if any_games:
            self.add_bot("Usé mezcla **70% Test + 30% Juegos** (promedios).")
        else:
            self.add_bot("No jugaste minijuegos; el resultado es **solo del Test**.")

        self.add_bot(f"🎯 Tu área con mayor afinidad es: **{area}**")
        self.show_profession(area)
        self.set_quick([
            primary_btn("Otra profesión del área", lambda e: self.show_profession(area, next_one=True)),
            ft.OutlinedButton(text="Exportar resultado", on_click=lambda e: self.export_result()),
            ft.OutlinedButton(text="Repetir test", on_click=lambda e: self.go_test()),
            ft.OutlinedButton(text="Volver al menú", on_click=lambda e: self.back_to_menu()),
        ])



    def _pick_profession_with_favorites(self, area: str) -> str | None:
        roles = AREAS.get(area, [])
        if not roles:
            return None
        # Si alguna favorita pertenece al área ganadora, sugiérela primero
        for fav in self.favorites:
            if fav in roles:
                return fav
        return roles[0]

    def show_profession(self, area: str, next_one: bool = False):
        roles = AREAS.get(area, [])
        if not roles:
            self.add_bot("No tengo profesiones cargadas para esa área 😅."); return
        if next_one:
            self.last_prof_index = (self.last_prof_index + 1) % len(roles)
        else:
            # Si hay favorita del área, posiciona el índice en ella
            for idx, r in enumerate(roles):
                if r in self.favorites:
                    self.last_prof_index = idx
                    break
        prof = roles[self.last_prof_index]
        self.add_bot(f"💡 Profesión sugerida: **{prof}**")
        self.add_bot("¿Quieres ver otra opción, exportar, repetir el test o volver al menú?")

    # ---------- Texto libre “inteligente” ----------
    def explain_free_text(self):
        self.add_bot("Cuéntame qué te gusta (ej.: 'me encanta diseñar interfaces y dibujar').")
        self.set_quick([primary_btn("Iniciar Test", lambda e: self.go_test())])

    # ---------- Export ----------
    def export_result(self):
        if not self.last_result:
            self.add_bot("Aún no tengo un resultado. Inicia el **Test** o cuéntame tus intereses.")
            return
        created = export_all(self.last_result)
        self.add_bot("Archivos generados:\n- " + "\n- ".join(created))

    # ---------- Entrada de texto ----------
    def on_send(self, e=None):
        msg = self.entry.value.strip()
        if not msg: return
        self.entry.value = ""
        self.add_user(msg)
        low = msg.lower()

        if "test" in low:
            self.go_test(); return
        if "menu" in low or "volver" in low:
            self.back_to_menu(); return
        if "otra" in low and self.last_area:
            self.show_profession(self.last_area, next_one=True); return
        if "export" in low or "pdf" in low or "json" in low:
            self.export_result(); return

        if self.stage == "test":
            self.add_bot("Usa los **botones** para elegir la opción de la pregunta.")
            return

        # Inteligencia simple para texto libre
        area, pts, tokens = smart_infer_area(msg)
        if pts == 0:
            self.add_bot("Puedo iniciar un **Test vocacional** o entender mejor si me cuentas lo que te gusta.")
            return
        # Sugerencia con ligero sesgo a favoritas
        prof = self._pick_profession_with_favorites(area) or suggest_profession(area)
        why = f"(detecté: {', '.join(tokens)})" if tokens else ""
        self.add_bot(f"Por lo que dices, suena a **{area}** {why}")
        self.add_bot(f"💡 Profesión sugerida: **{prof}**. ¿Quieres correr el **test** para confirmarlo?")

    # ---------- Navegación ----------
    def back_to_menu(self):
        self.stage = "menu"
        self.add_bot("¿Qué te gustaría hacer ahora?")
        self.set_quick(self.menu_buttons())

    # ---------- Atajos de teclado (1..5) ----------
    def on_key(self, e: ft.KeyboardEvent):
        if self.stage != "test":
            return
        key = (e.key or "").strip()
        mapping = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4}
        if key in mapping:
            idx = mapping[key]
            if 0 <= idx < len(self.current_handlers):
                self.current_handlers[idx](None)

    def open_games_menu(self):
        self.add_bot("Elige un minijuego (60–90 s). Suma afinidad por área.")
        self.set_quick([
            primary_btn("🔧 Debug Runner (Tecno)", lambda e: self.play_debug()),
            primary_btn("🎨 Color Quest (Arte)",  lambda e: self.play_color()),
            primary_btn("🎯 Ruleta Vocacional",   lambda e: self.play_ruleta()),
            ft.OutlinedButton(text="Volver al menú", on_click=lambda e: self.back_to_menu()),
        ])


    def play_debug(self):
        self.add_bot("Iniciando Debug Runner…")
        game = build_debug_runner(self.on_game_finish)
        self.chat.controls.append(game); self.page.update()
        self.set_quick([])

    def play_color(self):
        self.add_bot("Iniciando Color Quest…")
        game = build_color_quest(self.on_game_finish)
        self.chat.controls.append(game); self.page.update()
        self.set_quick([])
    
    def play_ruleta(self):
        self.add_bot("Iniciando Ruleta Vocacional…")
        open_ruleta_dialog(self.page, self.on_game_finish)  # abre modal animado
        self.set_quick([])  # opcional: limpiar botones mientras está el modal



    def on_game_finish(self, result: dict):
        # result: {"game": "...", "area": "Tecnología", "score": 0..100, "why": "..."}
        area = result.get("area")
        score = float(result.get("score", 0))
        why = result.get("why", "")

        # Acumula afinidad por área a partir de juegos
        if area in self.game_scores:
            self.game_scores[area] += score
            self.game_counts[area] += 1

        self.add_bot(f"🏁 Fin del juego **{result.get('game')}** → {area}: {int(score)} puntos. {why}")

        # Ranking parcial por juegos
        parts = []
        for a in AREAS:
            avg = (self.game_scores[a] / self.game_counts[a]) if self.game_counts[a] else 0.0
            parts.append(f"{a}: {avg:.0f}")
        self.add_bot("Afinidad por juegos (promedios): " + " | ".join(parts))

        # Sugerencia rápida
        best_area = max(
            AREAS.keys(),
            key=lambda a: (self.game_scores[a] / self.game_counts[a]) if self.game_counts[a] else 0
        )
        self.add_bot(f"🎯 Con lo jugado, tu área más fuerte parece **{best_area}**.")
        self.add_bot("¿Quieres jugar otro, correr el Test vocacional, o ver profesión sugerida?")
        self.set_quick([
            primary_btn("Otro juego", lambda e: self.open_games_menu()),
            primary_btn("Correr Test", lambda e: self.go_test()),
            ft.OutlinedButton(text="Profesión sugerida",
                            on_click=lambda e, A=best_area: self.show_profession(A)),
            ft.OutlinedButton(text="Volver al menú", on_click=lambda e: self.back_to_menu()),
        ])

