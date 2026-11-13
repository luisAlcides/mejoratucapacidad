"""Vocabulario diario de inglés: qué entradas tocan hoy y cómo se marcan.

Cada día se reparten unas pocas entradas nuevas de `palabras.py`. El usuario marca
cada una como sabida (no vuelve, y si era nueva sale otra en su lugar) o para repasar
(vuelve tras un intervalo creciente).
"""

from datetime import timedelta

from . import palabras
from .models import Vocabulario

# (letra de la clave, etiqueta, lista, entradas nuevas por día)
TIPOS = [
    ("p", "Palabra", palabras.PALABRAS, 3),
    ("v", "Verbo", palabras.VERBOS, 2),
    ("f", "Phrasal verb", palabras.PHRASALS, 1),
]
# Días de espera cada vez que se pide repasar una entrada; la última se repite.
INTERVALOS = [1, 3, 7, 14, 30]
# Con este número de entradas por aprender en el día no se reparten nuevas ni se muestran más.
TOPE = 12
# Cuántas de las marcadas hoy como sabidas siguen a la vista para poder deshacer.
SABIDAS_VISIBLES = 3

ENTRADAS = {
    f"{letra}:{ingles}": {
        "tipo": etiqueta,
        "ingles": f"to {ingles}" if letra == "v" else ingles,
        "espanol": espanol,
        "ejemplo": ejemplo,
    }
    for letra, etiqueta, lista, _ in TIPOS
    for ingles, espanol, ejemplo in lista
}


def _filas(usuario):
    return list(Vocabulario.objects.filter(usuario=usuario))


def _repartir(usuario, fecha, filas, libres):
    """Completa el cupo de nuevas del día; devuelve si creó alguna.

    Una entrada nueva marcada como sabida no gasta cupo: quien ya la conocía recibe
    otra en su lugar, y así las nuevas del día son siempre palabras por aprender.
    """
    vistas = {f.clave for f in filas}
    nuevas = []
    for letra, _, lista, cuantas in TIPOS:
        de_hoy = sum(
            1 for f in filas
            if f.presentada == fecha and not f.sabida and f.clave.startswith(f"{letra}:")
        )
        hueco = min(cuantas - de_hoy, libres - len(nuevas))
        if hueco <= 0:
            continue
        claves = (f"{letra}:{entrada[0]}" for entrada in lista)
        nuevas += [
            Vocabulario(usuario=usuario, clave=clave, presentada=fecha, proxima=fecha)
            for clave in [c for c in claves if c not in vistas][:hueco]
        ]
    # ignore_conflicts: dos pestañas abiertas a la vez no deben romper la página.
    Vocabulario.objects.bulk_create(nuevas, ignore_conflicts=True)
    return bool(nuevas)


def del_dia(usuario, fecha):
    """Entradas de hoy: `pendientes` por marcar y `hechas` ya marcadas hoy."""
    filas = _filas(usuario)

    def separar():
        validas = [f for f in filas if f.clave in ENTRADAS]
        hechas = [f for f in validas if f.respondida_el == fecha]
        pendientes = [
            f for f in validas
            if not f.sabida and f.proxima <= fecha and f.respondida_el != fecha
        ]
        return validas, pendientes, hechas

    validas, pendientes, hechas = separar()
    # Lo que hoy pide esfuerzo: lo pendiente y lo que se mandó a repasar.
    carga = len(pendientes) + sum(1 for f in hechas if not f.sabida)
    if carga < TOPE and _repartir(usuario, fecha, filas, TOPE - carga):
        filas = _filas(usuario)
        validas, pendientes, hechas = separar()

    hechas.sort(key=lambda f: f.id)
    sabidas_hoy = [f for f in hechas if f.sabida]
    # De las sabidas de hoy solo se enseñan las últimas, por si hay que deshacer.
    visibles = [f for f in hechas if not f.sabida or f in sabidas_hoy[-SABIDAS_VISIBLES:]]
    for fila in pendientes + visibles:
        fila.entrada = ENTRADAS[fila.clave]
        fila.es_repaso = fila.presentada < fecha
    return {
        "pendientes": pendientes[:TOPE],
        "en_espera": max(len(pendientes) - TOPE, 0),
        "hechas": visibles,
        "sabidas_hoy": len(sabidas_hoy),
        "sabidas": sum(1 for f in validas if f.sabida),
        "total": len(ENTRADAS),
    }


def para_prompt(usuario, fecha):
    """Las entradas pendientes de hoy, en inglés, para el prompt del tutor."""
    return [f.entrada["ingles"] for f in del_dia(usuario, fecha)["pendientes"]]


def responder(fila, sabe, fecha):
    """Marca una entrada: sabida no vuelve; si no, se programa el siguiente repaso."""
    if sabe:
        fila.sabida = True
    else:
        ultimo = len(INTERVALOS) - 1
        fila.proxima = fecha + timedelta(days=INTERVALOS[min(fila.nivel, ultimo)])
        fila.nivel = min(fila.nivel + 1, ultimo + 1)
    fila.respondida_el = fecha
    fila.save()


def deshacer(fila, fecha):
    """Deshace la marca de hoy y devuelve la entrada a las pendientes."""
    if fila.respondida_el != fecha:
        return
    if fila.sabida:
        fila.sabida = False
    else:
        fila.nivel = max(fila.nivel - 1, 0)
    fila.proxima = fecha
    fila.respondida_el = None
    fila.save()
