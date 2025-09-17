# -*- coding: utf-8 -*-

DEFAULT_Q = ("¿Qué tan identificado/a te sientes con esta área?",
             [("Mucho", 1.0), ("Un poco", 0.5), ("Nada", 0.0)])

QBANK = {
    "Tecnología": ("¿Te motiva programar apps/juegos sencillos?",
                   [("Mucho",1.0),("Un poco",0.5),("Nada",0.0)]),
    "Educación": ("¿Te ves enseñando o acompañando a otros a aprender?",
                  [("Mucho",1.0),("Un poco",0.5),("Nada",0.0)]),
    "Salud": ("¿Te gustaría aprender primeros auxilios y anatomía?",
              [("Mucho",1.0),("Un poco",0.5),("Nada",0.0)]),
    # añade más si quieres… (Arte y cultura, Oficios, etc.)
}

def get_question(area: str):
    return QBANK.get(area, DEFAULT_Q)
