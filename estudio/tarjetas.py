"""Tarjetas propias: qué toca repasar hoy y cómo se programa cada respuesta.

Cada tarjeta sube por `INTERVALOS` cuando se recuerda con facilidad. La que se olvida
vuelve al principio y sigue en la cola del día hasta que se marque de otra forma.
"""

from datetime import timedelta

from django.utils import timezone

from .models import Mazo, Tarjeta

# Días de espera según el nivel de la tarjeta; el último se repite.
INTERVALOS = [1, 2, 4, 7, 15, 30, 60, 120]
# Tarjetas nuevas que se estrenan al día entre todos los mazos.
NUEVAS_POR_DIA = 20

OLVIDE, ME_COSTO, FACIL = "olvide", "costo", "facil"
RESULTADOS = [(OLVIDE, "Lo olvidé"), (ME_COSTO, "Me costó"), (FACIL, "Fácil")]


def _del_usuario(usuario):
    return list(Tarjeta.objects.filter(mazo__usuario=usuario).select_related("mazo"))


def _cola(todas, fecha, mazo=None):
    """Ordena lo que toca hoy a partir de todas las tarjetas del usuario.

    El cupo de nuevas se cuenta entre todos los mazos aunque se pida uno solo.
    """
    cupo = NUEVAS_POR_DIA - sum(1 for t in todas if t.primer_repaso == fecha)
    propias = [t for t in todas if mazo is None or t.mazo_id == mazo.pk]
    vistas = [t for t in propias if t.primer_repaso and t.proxima <= fecha]
    olvidadas = [t for t in vistas if t.respondida_el == fecha]
    tocan = [t for t in vistas if t.respondida_el != fecha]
    nuevas = [t for t in propias if not t.primer_repaso]
    tocan.sort(key=lambda t: (t.proxima, t.id))
    nuevas.sort(key=lambda t: (t.creada, t.id))
    olvidadas.sort(key=lambda t: (t.respondida, t.id))
    return tocan + nuevas[:max(cupo, 0)] + olvidadas


def cola(usuario, fecha, mazo=None):
    """Tarjetas por repasar hoy, en orden: las que tocan, las nuevas y las olvidadas hoy."""
    return _cola(_del_usuario(usuario), fecha, mazo)


def responder(tarjeta, resultado, fecha):
    """Programa la tarjeta según cómo se recordó."""
    ultimo = len(INTERVALOS) - 1
    if resultado == OLVIDE:
        tarjeta.nivel = 0
        tarjeta.proxima = fecha
    else:
        if resultado == FACIL:
            tarjeta.nivel = min(tarjeta.nivel + 1, ultimo)
        tarjeta.proxima = fecha + timedelta(days=INTERVALOS[min(tarjeta.nivel, ultimo)])
    tarjeta.primer_repaso = tarjeta.primer_repaso or fecha
    tarjeta.respondida_el = fecha
    tarjeta.respondida = timezone.now()
    tarjeta.save()


def resumen(usuario, fecha):
    """Mazos del usuario con su total y lo que toca hoy, más el total del día."""
    todas = _del_usuario(usuario)
    mazos = list(Mazo.objects.filter(usuario=usuario))
    for mazo in mazos:
        mazo.total = sum(1 for t in todas if t.mazo_id == mazo.pk)
        mazo.tocan = len(_cola(todas, fecha, mazo))
    return {"mazos": mazos, "tocan": len(_cola(todas, fecha))}


def repasadas_hoy(usuario, fecha, mazo=None):
    """Cuántas tarjetas se respondieron hoy y ya no están en la cola."""
    filtro = {"mazo": mazo} if mazo else {"mazo__usuario": usuario}
    return Tarjeta.objects.filter(respondida_el=fecha, proxima__gt=fecha, **filtro).count()


def separar(texto):
    """Convierte líneas «pregunta ; respuesta» en pares; devuelve también las inválidas."""
    pares, malas = [], []
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        frente, _, reverso = (parte.strip() for parte in linea.partition(";"))
        if frente and reverso:
            pares.append((frente, reverso))
        else:
            malas.append(linea)
    return pares, malas
