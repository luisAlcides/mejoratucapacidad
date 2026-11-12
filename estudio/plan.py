"""Reglas del plan de estudio.

Cada día se genera un checklist según el día de la semana:

    Lun / Mié / Vie  → materia principal de la etapa + lectura
    Mar / Jue        → materia complementaria + lectura
    Sábado           → repaso de la semana + lectura
    Domingo          → descanso (lectura por placer, opcional)

Nada se acumula: al empezar un día nuevo, lo que quedó sin tachar de días
anteriores se quita del checklist. Pero no se pierde el lugar: el avance vive
en ProgresoTema, así que un tema solo pasa a la siguiente sesión (o al
siguiente tema) cuando de verdad lo estudias. Si faltas varios días, retomas
exactamente donde te quedaste.

Los repasos espaciados tampoco se apilan: se muestran como máximo
MAX_REPASOS_DIA por día, empezando por los más antiguos.
"""

import re
from urllib.parse import quote
from datetime import timedelta

from django.db import transaction
from django.db.models import F

from .models import (
    DiaPlan,
    Etapa,
    LecturaLibro,
    Libro,
    Materia,
    Perfil,
    ProgresoTema,
    Repaso,
    Tarea,
    Tema,
)

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DIAS_PRINCIPAL = {0, 2, 4}
DIAS_COMPLEMENTARIA = {1, 3}
SABADO, DOMINGO = 5, 6
MAX_REPASOS_DIA = 3
# Materia que avanza a diario en paralelo, como práctica breve y opcional.
MATERIA_PARALELA = "ingles"
MINUTOS_PARALELA = 10


def fases_sesion(minutos):
    """Reparto de la sesión: repasar, aprender, practicar y recordar (5/10/10/5 en 30 min)."""
    proporciones = [("Repasar", "Recuerda lo que aprendiste en la sesión anterior.", 1),
                    ("Aprender", "Estudia una explicación corta del concepto nuevo.", 2),
                    ("Practicar", "Resuelve ejercicios o analiza argumentos sin ayuda.", 2),
                    ("Recordar", "Cierra el material y explícalo con tus palabras.", 1)]
    return [
        {"nombre": n, "texto": t, "minutos": round(minutos * p / 6)}
        for n, t, p in proporciones
    ]


CHATGPT_URL = "https://chatgpt.com/"


def minutos_de(tarea, perfil):
    return MINUTOS_PARALELA if tarea.tipo == Tarea.INGLES else perfil.minutos_sesion


def prompt_chatgpt(tarea, minutos, progreso=None):
    """Prompt para que ChatGPT haga de tutor durante una sesión de estudio."""
    tema = tarea.tema
    total = tema.sesiones + (progreso.sesiones_extra if progreso else 0)
    fases = " → ".join(f"{f['nombre']} {f['minutos']} min" for f in fases_sesion(minutos))
    lineas = [
        "Quiero que seas mi profesor particular en esta sesión de estudio. Enséñame paso a paso, "
        "con ejemplos sencillos, una idea cada vez, y espera a que yo responda antes de seguir. "
        "Hazme preguntas para comprobar que lo entendí y corrígeme si me equivoco. Respóndeme en español.",
        "",
        f"Materia: {tema.materia.nombre}",
        f"Tema: {tema.titulo} ({tema.get_nivel_display()})",
    ]
    if tema.descripcion:
        lineas.append(f"De qué trata: {tema.descripcion}")
    if tarea.numero_sesion:
        lineas.append(f"Es mi sesión {tarea.numero_sesion} de {total} sobre este tema.")
    lineas.append(f"Tengo {minutos} minutos, repartidos así: {fases}.")
    if tema.recurso:
        lineas.append(f"Material de referencia: {tema.recurso}")
    if progreso:
        if progreso.concepto.strip():
            lineas.append(f"Lo que ya aprendí: {progreso.concepto.strip()[:300]}")
        if progreso.errores.strip():
            lineas.append(f"Errores que cometí antes: {progreso.errores.strip()[:300]}")
        if progreso.preguntas.strip():
            lineas.append(f"Dudas que me quedaron: {progreso.preguntas.strip()[:300]}")
    preguntas = tema.lista_preguntas()[:5]
    if preguntas:
        lineas += ["", "Al final debería poder responder sin ayuda:"] + [f"- {p}" for p in preguntas]
    if tarea.tipo == Tarea.INGLES:
        lineas += ["", "Es práctica de inglés: explícame en español, pero hazme practicar en inglés."]
    if (tarea.numero_sesion or 1) > 1:
        lineas += ["", "Empieza con una pregunta corta para ver qué recuerdo de la sesión anterior."]
    else:
        lineas += ["", "Empieza con una pregunta corta para ver qué sé ya de este tema."]
    return "\n".join(lineas)


def chatgpt_url(prompt):
    return f"{CHATGPT_URL}?q={quote(prompt[:3000])}"


def minutos_lectura(perfil):
    if perfil.minutos_lectura:
        return perfil.minutos_lectura
    return {20: 5, 30: 8, 45: 12}.get(perfil.minutos_sesion, 8)


def actualizar_minutos_lectura(usuario):
    """Ajusta los minutos de la tarea de lectura pendiente al valor actual del perfil."""
    minutos = minutos_lectura(perfil_de(usuario))
    for tarea in Tarea.objects.filter(usuario=usuario, tipo=Tarea.LECTURA, hecha=False, opcional=False):
        nuevo = re.sub(r"^Leer \d+ min:", f"Leer {minutos} min:", tarea.titulo)
        if nuevo != tarea.titulo:
            tarea.titulo = nuevo
            tarea.save(update_fields=["titulo"])


def perfil_de(usuario):
    perfil, _ = Perfil.objects.get_or_create(usuario=usuario)
    return perfil


def materia_del_dia(etapa, fecha, usuario=None):
    if etapa is None:
        return None
    dia = fecha.weekday()
    if (
        usuario is not None
        and etapa.sustituta_id
        and etapa.dia_sustituto == dia
        and siguiente_sesion(usuario, etapa.sustituta) is not None
    ):
        return etapa.sustituta
    if dia in DIAS_PRINCIPAL:
        return etapa.principal
    if dia in DIAS_COMPLEMENTARIA:
        return etapa.complementaria
    return None


def progresos_de(usuario, materia):
    return {
        p.tema_id: p
        for p in ProgresoTema.objects.filter(usuario=usuario, tema__materia=materia)
    }


def siguiente_sesion(usuario, materia, progresos=None):
    """Devuelve (tema, número de sesión, es_comprobación) de lo próximo a estudiar, o None."""
    progresos = progresos if progresos is not None else progresos_de(usuario, materia)
    for tema in materia.temas.all():
        prog = progresos.get(tema.id)
        if prog and prog.estado == ProgresoTema.DOMINADO:
            continue
        hechas = prog.sesiones_hechas if prog else 0
        extra = prog.sesiones_extra if prog else 0
        if hechas < tema.sesiones + extra:
            return tema, hechas + 1, False
        return tema, hechas + 1, True
    return None


def titulo_sesion(tema, numero, comprobacion):
    if comprobacion:
        paso = Tarea.PASO_COMPROBAR
    elif numero <= min(tema.sesiones, len(Tarea.PASOS)):
        paso = Tarea.PASOS[numero - 1]
    else:
        paso = Tarea.PASO_EXTRA
    return tema.titulo, paso


def crear_tarea_estudio(usuario, materia, fecha, tipo=Tarea.ESTUDIO, opcional=False):
    """Crea la próxima sesión de una materia, salvo que ya haya una pendiente."""
    pendiente = Tarea.objects.filter(
        usuario=usuario, tema__materia=materia, hecha=False
    ).exists()
    if pendiente:
        return None
    siguiente = siguiente_sesion(usuario, materia)
    if siguiente is None:
        return None
    tema, numero, comprobacion = siguiente
    titulo, paso = titulo_sesion(tema, numero, comprobacion)
    return Tarea.objects.create(
        usuario=usuario,
        fecha=fecha,
        tipo=tipo,
        opcional=opcional,
        tema=tema,
        numero_sesion=numero,
        es_comprobacion=comprobacion,
        titulo=titulo,
        detalle=paso,
    )


def libro_actual(usuario):
    """El libro elegido si no está terminado; si no, el primero sin terminar de la lista."""
    terminados = LecturaLibro.objects.filter(usuario=usuario, terminado__isnull=False).values(
        "libro_id"
    )
    elegido = perfil_de(usuario).libro_actual
    if elegido and not LecturaLibro.objects.filter(
        usuario=usuario, libro=elegido, terminado__isnull=False
    ).exists():
        return elegido
    return Libro.objects.exclude(id__in=terminados).order_by("orden", "id").first()


def cambiar_lectura_pendiente(usuario, anterior, nuevo):
    """Apunta la tarea de lectura pendiente al nuevo libro (o la quita si no queda ninguno)."""
    for tarea in Tarea.objects.filter(usuario=usuario, tipo=Tarea.LECTURA, hecha=False):
        if nuevo is None:
            tarea.delete()
            continue
        if anterior:
            tarea.titulo = tarea.titulo.replace(anterior.titulo, nuevo.titulo)
            tarea.detalle = tarea.detalle.replace(anterior.titulo, nuevo.titulo)
        tarea.libro = nuevo
        tarea.save()


def generar_dia(usuario, fecha):
    """Crea (una sola vez) las tareas del día y descarta lo no hecho de días anteriores."""
    with transaction.atomic():
        _, creado = DiaPlan.objects.get_or_create(usuario=usuario, fecha=fecha)
        if not creado:
            return
        # Lo no hecho de días anteriores se descarta; el progreso del tema no cambia.
        Tarea.objects.filter(usuario=usuario, hecha=False, fecha__lt=fecha).delete()
        perfil = perfil_de(usuario)
        etapa = perfil.etapa_actual(fecha)
        dia = fecha.weekday()

        materia = materia_del_dia(etapa, fecha, usuario)
        if materia:
            crear_tarea_estudio(usuario, materia, fecha)

        if dia == SABADO and not Tarea.objects.filter(
            usuario=usuario, tipo=Tarea.REPASO_SEMANAL, hecha=False
        ).exists():
            estudiados = (
                Tema.objects.filter(
                    tarea__usuario=usuario,
                    tarea__tipo=Tarea.ESTUDIO,
                    tarea__hecha=True,
                    tarea__hecha_el__gte=fecha - timedelta(days=6),
                )
                .distinct()
                .values_list("titulo", flat=True)
            )
            detalle = ", ".join(estudiados) or "Ejercicios de los temas de la semana"
            Tarea.objects.create(
                usuario=usuario,
                fecha=fecha,
                tipo=Tarea.REPASO_SEMANAL,
                titulo="Ejercicios de repaso de la semana",
                detalle=detalle[:250],
            )

        if not Tarea.objects.filter(usuario=usuario, tipo=Tarea.LECTURA, hecha=False).exists():
            libro = libro_actual(usuario)
            minutos = minutos_lectura(perfil)
            if dia == DOMINGO:
                Tarea.objects.create(
                    usuario=usuario, fecha=fecha, tipo=Tarea.LECTURA, libro=libro, opcional=True,
                    titulo="Lectura por placer",
                    detalle=f"Sin presión: {libro.titulo}" if libro else "Lo que te apetezca",
                )
            elif libro:
                Tarea.objects.create(
                    usuario=usuario, fecha=fecha, tipo=Tarea.LECTURA, libro=libro,
                    titulo=f"Leer {minutos} min: {libro.titulo}",
                    detalle="Al terminar, resume de memoria la idea principal.",
                )

        if perfil.ingles and dia < SABADO:
            # El inglés avanza por su propio temario, en paralelo y como opcional.
            ingles = Materia.objects.filter(slug=MATERIA_PARALELA).first()
            creada = ingles and crear_tarea_estudio(
                usuario, ingles, fecha, tipo=Tarea.INGLES, opcional=True
            )
            if not creada and not Tarea.objects.filter(
                usuario=usuario, tipo=Tarea.INGLES, hecha=False
            ).exists():
                Tarea.objects.create(
                    usuario=usuario, fecha=fecha, tipo=Tarea.INGLES, opcional=True,
                    titulo="Inglés: 10 min de práctica libre",
                    detalle="Un audio corto, una serie o leer un párrafo.",
                )


def checklist(usuario, hoy):
    """Tareas de hoy (pendientes y hechas) y los repasos que tocan, sin acumular."""
    generar_dia(usuario, hoy)
    # La lectura pendiente siempre es el libro que toca ahora, aunque la lista haya cambiado.
    pendiente = Tarea.objects.filter(
        usuario=usuario, tipo=Tarea.LECTURA, hecha=False
    ).select_related("libro").first()
    actual = libro_actual(usuario)
    if pendiente and pendiente.libro_id != (actual and actual.id):
        cambiar_lectura_pendiente(usuario, pendiente.libro, actual)
    tareas = Tarea.objects.filter(usuario=usuario, fecha__lte=hoy).select_related(
        "tema__materia", "libro"
    )
    pendientes = [t for t in tareas.filter(hecha=False)]
    hechas = list(tareas.filter(hecha=True, hecha_el=hoy))
    repasos = Repaso.objects.filter(
        usuario=usuario, hecho_el__isnull=True, fecha__lte=hoy
    ).select_related("tema__materia")[:MAX_REPASOS_DIA]
    repasos_hechos = Repaso.objects.filter(usuario=usuario, hecho_el=hoy).select_related(
        "tema__materia"
    )
    return pendientes, hechas, list(repasos), list(repasos_hechos)


@transaction.atomic
def completar_tarea(tarea, hoy, logrado=True, minutos=0):
    """Marca una tarea y aplica sus efectos (avanzar tema, programar repasos, contar lectura)."""
    if tarea.hecha:
        return
    tarea.hecha = True
    tarea.hecha_el = hoy
    tarea.minutos = minutos
    tarea.save()

    if tarea.tema:
        prog, _ = ProgresoTema.objects.get_or_create(usuario=tarea.usuario, tema=tarea.tema)
        if tarea.es_comprobacion:
            if logrado:
                prog.estado = ProgresoTema.DOMINADO
                prog.dominado = hoy
            else:
                prog.sesiones_extra += 1
        else:
            prog.sesiones_hechas += 1
            prog.estado = ProgresoTema.EN_CURSO
            prog.iniciado = prog.iniciado or hoy
            if not Repaso.objects.filter(
                usuario=tarea.usuario, tema=tarea.tema, hecho_el__isnull=True
            ).exists():
                Repaso.objects.create(
                    usuario=tarea.usuario, tema=tarea.tema, fecha=hoy + timedelta(days=1)
                )
        prog.save()

    if tarea.tipo == Tarea.LECTURA and tarea.libro:
        lectura, _ = LecturaLibro.objects.get_or_create(usuario=tarea.usuario, libro=tarea.libro)
        lectura.sesiones += 1
        lectura.save()


@transaction.atomic
def deshacer_tarea(tarea):
    """Desmarca una tarea hecha por error y revierte su efecto sobre el progreso."""
    if not tarea.hecha:
        return
    if tarea.tema:
        prog = ProgresoTema.objects.filter(usuario=tarea.usuario, tema=tarea.tema).first()
        if prog:
            if tarea.es_comprobacion:
                if prog.estado == ProgresoTema.DOMINADO:
                    prog.estado = ProgresoTema.EN_CURSO
                    prog.dominado = None
                elif prog.sesiones_extra:
                    prog.sesiones_extra -= 1
            elif prog.sesiones_hechas:
                prog.sesiones_hechas -= 1
            prog.save()
        # Si al marcarla se creó la sesión siguiente, ya no corresponde.
        Tarea.objects.filter(
            usuario=tarea.usuario, tema__materia=tarea.tema.materia,
            hecha=False, id__gt=tarea.id,
        ).delete()
    if tarea.tipo == Tarea.LECTURA and tarea.libro:
        LecturaLibro.objects.filter(
            usuario=tarea.usuario, libro=tarea.libro, sesiones__gt=0
        ).update(sesiones=F("sesiones") - 1)
    tarea.hecha = False
    tarea.hecha_el = None
    tarea.minutos = 0
    tarea.save()


def estudiar_otra(usuario, materia, hoy):
    """Permite adelantar la siguiente sesión de una materia en el mismo día."""
    return crear_tarea_estudio(usuario, materia, hoy)


# --- Proyección: qué toca estudiar y repasar en los próximos días ------------------


def proyeccion(usuario, desde, dias=14):
    """Simula el plan día a día suponiendo que cada día se cumple lo programado."""
    perfil = perfil_de(usuario)
    cursores = {}
    repasos = list(
        Repaso.objects.filter(usuario=usuario, hecho_el__isnull=True).select_related("tema")
    )
    resultado = []
    for i in range(dias):
        fecha = desde + timedelta(days=i)
        etapa = perfil.etapa_actual(fecha)
        materia = materia_del_dia(etapa, fecha, usuario)
        estudio = None
        if materia:
            estudio = _avanzar_cursor(usuario, materia, cursores)
        resultado.append({
            "fecha": fecha,
            "dia": DIAS[fecha.weekday()],
            "etapa": etapa,
            "materia": materia,
            "estudio": estudio,
            "sabado": fecha.weekday() == SABADO,
            "domingo": fecha.weekday() == DOMINGO,
            "repasos": [r for r in repasos if (r.fecha == fecha) or (i == 0 and r.fecha < fecha)][:MAX_REPASOS_DIA],
        })
    return resultado


def _avanzar_cursor(usuario, materia, cursores):
    """Devuelve la sesión que tocaría y avanza el cursor simulado de esa materia."""
    if materia.id not in cursores:
        progresos = progresos_de(usuario, materia)
        estado = []
        for tema in materia.temas.all():
            prog = progresos.get(tema.id)
            if prog and prog.estado == ProgresoTema.DOMINADO:
                continue
            hechas = prog.sesiones_hechas if prog else 0
            total = (prog.sesiones_extra if prog else 0) + tema.sesiones
            estado.append([tema, hechas, total])
        cursores[materia.id] = estado
    estado = cursores[materia.id]
    if not estado:
        return None
    tema, hechas, total = estado[0]
    comprobacion = hechas >= total
    _, paso = titulo_sesion(tema, hechas + 1, comprobacion)
    if comprobacion:
        estado.pop(0)
    else:
        estado[0][1] += 1
    return {"tema": tema, "paso": paso}
