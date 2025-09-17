# -*- coding: utf-8 -*-
# Datos del dominio: áreas, profesiones, preguntas, keywords y favoritas seed

from typing import Dict, List, Tuple

AREAS: Dict[str, List[str]] = {
    "Tecnología": [
        "Desarrollador/a de Software", "Científico/a de Datos",
        "Especialista en Ciberseguridad", "Desarrollador/a Web", "Administrador/a de Redes"
    ],
    "Salud": [
        "Enfermería", "Tecnología Médica", "Nutrición", "Psicología Clínica", "Medicina"
    ],
    "Negocios": [
        "Marketing Digital", "Analista de Negocios", "Finanzas", "Comercio Internacional", "Emprendimiento"
    ],
    "Arte y Diseño": [
        "Diseño Gráfico", "Diseño UX/UI", "Animación", "Arquitectura", "Fotografía"
    ],
    "Educación y Sociales": [
        "Docencia", "Trabajo Social", "Psicología Educativa", "Gestión Pública", "Relaciones Internacionales"
    ],
    "Ambiente y Agro": [
        "Ingeniería Ambiental", "Biología", "Gestión de Recursos Naturales", "Agroindustria", "Forestal"
    ],
    "Oficios e Ingeniería": [
        "Ingeniería Civil", "Electricidad/Electrónica", "Mecánica", "Carpintería", "Topografía"
    ],
}

SMART_KEYWORDS: Dict[str, List[str]] = {
    "Tecnología": ["program", "código", "software", "datos", "app", "web", "api", "ciberseg", "redes", "automat"],
    "Salud": ["salud", "hospital", "paciente", "enfermer", "medicin", "nutric", "terapia"],
    "Negocios": ["marketing", "ventas", "negocio", "empresa", "finanzas", "analista", "comercial"],
    "Arte y Diseño": ["diseño", "ux", "ui", "ilustr", "animación", "arquitect", "fotograf"],
    "Educación y Sociales": ["educa", "enseñar", "docen", "social", "comunidad", "psicolog"],
    "Ambiente y Agro": ["ambiente", "ecolog", "sosten", "biolog", "campo", "agro", "bosque"],
    "Oficios e Ingeniería": ["constru", "mecán", "electric", "solda", "taller", "instalar", "repar", "planos"],
}

Question = Dict[str, List[Tuple[str, str]]]

QUESTIONS: List[Question] = [
    {"q": "¿Qué te entusiasma más hacer?",
     "opts": [("Crear apps o automatizar tareas", "Tecnología"),
              ("Ayudar a personas en temas de salud", "Salud"),
              ("Liderar un proyecto o vender una idea", "Negocios")]},
    {"q": "¿Qué actividad te suena más divertida?",
     "opts": [("Diseñar una interfaz o ilustración", "Arte y Diseño"),
              ("Explicar un tema difícil a alguien", "Educación y Sociales"),
              ("Organizar una feria o campaña", "Negocios")]},
    {"q": "Si hoy tuvieras una tarde libre, preferirías…",
     "opts": [("Explorar hardware o reparar algo", "Oficios e Ingeniería"),
              ("Hacer trabajo de campo al aire libre", "Ambiente y Agro"),
              ("Probar una API y unir datos", "Tecnología")]},
    {"q": "¿Qué problema te gustaría resolver?",
     "opts": [("Contaminación y cambio climático", "Ambiente y Agro"),
              ("Acceso a salud y bienestar", "Salud"),
              ("Experiencias digitales más intuitivas", "Arte y Diseño")]},
    {"q": "En un equipo, sueles…",
     "opts": [("Coordinar tareas y metas", "Negocios"),
              ("Enseñar/explicar a quien lo necesita", "Educación y Sociales"),
              ("Investigar soluciones técnicas", "Tecnología")]},
    {"q": "Elige la que más te identifica:",
     "opts": [("Manos a la obra: construir/instalar", "Oficios e Ingeniería"),
              ("Creatividad visual y narrativa", "Arte y Diseño"),
              ("Análisis de datos y lógica", "Tecnología")]},
]

# Profesiones favoritas de ejemplo (el usuario las puede cambiar en “Mis Favoritas”)
SEED_FAVORITES: List[str] = ["Desarrollador/a de Software", "Diseño UX/UI", "Enfermería"]
