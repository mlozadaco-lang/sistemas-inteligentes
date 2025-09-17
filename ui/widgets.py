# -*- coding: utf-8 -*-
# Componentes visuales reutilizables y paleta de colores

import flet as ft

HEX = {
    "BG": "#F5F5F7",
    "BOT": "#FFFFFF",
    "USER": "#DCF7C5",
    "TEXT": "#111111",
    "BORDER": "#E5E7EB",
    "PRIMARY": "#4F46E5",  # cámbialo para tu color principal
    "ACCENT": "#22C55E",
}

def primary_btn(texto: str, on_click, width: int | None = None):
    """Botón primario con texto visible en cualquier versión."""
    return ft.ElevatedButton(
        content=ft.Text(texto, color="#FFFFFF", weight=ft.FontWeight.W_600),
        on_click=on_click,
        bgcolor=HEX["PRIMARY"],
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=18),
            color={"": "#FFFFFF", "hovered": "#FFFFFF", "pressed": "#FFFFFF"},
        ),
        width=width,
    )

def bubble(text: str, user: bool = False):
    user_avatar = ft.CircleAvatar(content=ft.Text("🐣", size=20), bgcolor=HEX["ACCENT"])
    bot_avatar  = ft.CircleAvatar(content=ft.Text("🤖", size=20))
    return ft.Row(
        [
            ft.Container(
                ft.Row(
                    [user_avatar if user else bot_avatar, ft.Container(width=6), ft.Text(text, size=14, selectable=True)],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=HEX["USER"] if user else HEX["BOT"],
                padding=12,
                border=ft.border.all(1, HEX["BORDER"]),
                border_radius=16 if user else 12,
                width=740,
            )
        ],
        alignment=ft.MainAxisAlignment.END if user else ft.MainAxisAlignment.START,
    )
