# -*- coding: utf-8 -*-
# Punto de entrada (Page) y montaje del controlador

import flet as ft
from logic.controller import AssistantController

def app(page: ft.Page):
    page.title = "Chatbot de Orientación Vocacional"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START

    controller = AssistantController(page)
    controller.mount()  # Construye layout y lanza el saludo


if __name__ == "__main__":
    ft.app(target=app, assets_dir="assets")


