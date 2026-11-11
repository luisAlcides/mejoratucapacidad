from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import plan
from .forms import CuadernoForm, PerfilForm, RegistroForm
from .models import (
    Etapa,
    LecturaLibro,
    Libro,
    Materia,
    ProgresoTema,
    Repaso,
    Tarea,
    Tema,
)


def hoy_local():
    return timezone.localdate()


def registro(request):
    if request.user.is_authenticated:
        return redirect("hoy")
    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, "¡Bienvenido! Este es tu primer día del plan.")
        return redirect("hoy")
    return render(request, "registration/registro.html", {"form": form})


@login_required
def hoy(request):
    fecha = hoy_local()
    perfil = plan.perfil_de(request.user)
    pendientes, hechas, repasos, repasos_hechos = plan.checklist(request.user, fecha)
    repasos_en_espera = Repaso.objects.filter(
        usuario=request.user, hecho_el__isnull=True, fecha__lte=fecha
    ).count() - len(repasos)
    etapa = perfil.etapa_actual(fecha)
    materia = plan.materia_del_dia(etapa, fecha, request.user)

    total = len(pendientes) + len(hechas) + len(repasos) + len(repasos_hechos)
    obligatorias_pendientes = [t for t in pendientes if not t.opcional]
    completadas = len(hechas) + len(repasos_hechos)

    materias_etapa = [m for m in [etapa.principal, etapa.complementaria] if m] if etapa else []
    return render(request, "estudio/hoy.html", {
        "fecha": fecha,
        "dia": plan.DIAS[fecha.weekday()],
        "etapa": etapa,
        "materia": materia,
        "pendientes": pendientes,
        "hechas": hechas,
        "repasos": repasos,
        "repasos_hechos": repasos_hechos,
        "repasos_en_espera": repasos_en_espera,
        "total": total,
        "completadas": completadas,
        "todo_listo": not obligatorias_pendientes and not repasos,
        "materias_etapa": materias_etapa,
        "racha": racha(request.user, fecha),
        "manana": plan.proyeccion(request.user, fecha + timedelta(days=1), dias=1)[0],
        "resultados": Repaso.RESULTADOS,
    })


@login_required
@require_POST
def completar(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, usuario=request.user)
    logrado = request.POST.get("logrado", "1") == "1"
    minutos = int(request.POST.get("minutos") or 0)
    plan.completar_tarea(tarea, hoy_local(), logrado=logrado, minutos=min(minutos, 240))
    if tarea.es_comprobacion:
        if logrado:
            messages.success(request, f"¡Dominaste «{tarea.tema.titulo}»! Pasas al siguiente tema.")
        else:
            messages.info(request, "Sin problema: se añade una sesión de práctica extra.")
    return redirect(request.POST.get("siguiente") or "hoy")


@login_required
@require_POST
def deshacer(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, usuario=request.user)
    plan.deshacer_tarea(tarea)
    return redirect("hoy")


@login_required
@require_POST
def completar_repaso(request, pk):
    repaso = get_object_or_404(Repaso, pk=pk, usuario=request.user, hecho_el__isnull=True)
    resultado = request.POST.get("resultado")
    if resultado in dict(Repaso.RESULTADOS):
        siguiente = repaso.completar(resultado, hoy_local())
        messages.info(
            request,
            f"Próximo repaso de «{repaso.tema.titulo}»: {siguiente.fecha:%d/%m}.",
        )
    return redirect("hoy")


@login_required
@require_POST
def estudiar_otra(request, slug):
    materia = get_object_or_404(Materia, slug=slug)
    tarea = plan.estudiar_otra(request.user, materia, hoy_local())
    if tarea is None:
        messages.info(request, f"Ya tienes una sesión pendiente de {materia.nombre}.")
    return redirect("hoy")


@login_required
def sesion(request, pk):
    tarea = get_object_or_404(
        Tarea.objects.select_related("tema__materia"),
        pk=pk, usuario=request.user, tema__isnull=False,
    )
    perfil = plan.perfil_de(request.user)
    minutos = plan.MINUTOS_PARALELA if tarea.tipo == Tarea.INGLES else perfil.minutos_sesion
    progreso, _ = ProgresoTema.objects.get_or_create(usuario=request.user, tema=tarea.tema)
    form = CuadernoForm(request.POST or None, instance=progreso)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cuaderno guardado.")
        return redirect("sesion", pk=tarea.pk)
    return render(request, "estudio/sesion.html", {
        "tarea": tarea,
        "tema": tarea.tema,
        "progreso": progreso,
        "form": form,
        "fases": plan.fases_sesion(minutos),
        "minutos": minutos,
    })


@login_required
def temario(request):
    progresos = {
        p.tema_id: p for p in ProgresoTema.objects.filter(usuario=request.user)
    }
    perfil = plan.perfil_de(request.user)
    etapa = perfil.etapa_actual(hoy_local())
    activas = {etapa.principal_id, etapa.complementaria_id, etapa.sustituta_id} if etapa else set()
    if perfil.ingles:
        activas |= set(Materia.objects.filter(slug=plan.MATERIA_PARALELA).values_list("id", flat=True))
    materias = []
    for materia in Materia.objects.prefetch_related("temas"):
        temas = []
        siguiente = plan.siguiente_sesion(request.user, materia, progresos)
        for tema in materia.temas.all():
            temas.append({
                "tema": tema,
                "progreso": progresos.get(tema.id),
                "actual": siguiente is not None and siguiente[0].id == tema.id,
            })
        dominados = sum(
            1 for t in temas if t["progreso"] and t["progreso"].estado == ProgresoTema.DOMINADO
        )
        niveles = []
        for nivel, etiqueta in Tema.NIVELES:
            del_nivel = [t for t in temas if t["tema"].nivel == nivel]
            if del_nivel:
                niveles.append({"etiqueta": etiqueta, "temas": del_nivel})
        materias.append({
            "materia": materia, "temas": temas, "niveles": niveles, "dominados": dominados,
            "pct": round(100 * dominados / len(temas)) if temas else 0,
            "activa": materia.id in activas,
        })
    materias.sort(key=lambda m: not m["activa"])
    return render(request, "estudio/temario.html", {"materias": materias})


@login_required
def tema(request, materia, slug):
    tema = get_object_or_404(Tema.objects.select_related("materia"), materia__slug=materia, slug=slug)
    progreso, _ = ProgresoTema.objects.get_or_create(usuario=request.user, tema=tema)
    form = CuadernoForm(request.POST or None, instance=progreso)
    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "dominar":
            progreso.estado = ProgresoTema.DOMINADO
            progreso.dominado = hoy_local()
            progreso.save()
            borradas, _ = Tarea.objects.filter(usuario=request.user, tema=tema, hecha=False).delete()
            if borradas:
                # La sesión que tocaba hoy pasa al siguiente tema de la materia.
                plan.crear_tarea_estudio(request.user, tema.materia, hoy_local())
            if not Repaso.objects.filter(usuario=request.user, tema=tema, hecho_el__isnull=True).exists():
                Repaso.objects.create(
                    usuario=request.user, tema=tema, fecha=hoy_local() + timedelta(days=7), nivel=3
                )
            messages.success(request, "Tema marcado como dominado. Lo seguirás repasando.")
            return redirect("tema", materia=materia, slug=slug)
        if accion == "reiniciar":
            progreso.estado = ProgresoTema.EN_CURSO if progreso.sesiones_hechas else ProgresoTema.PENDIENTE
            progreso.dominado = None
            progreso.save()
            messages.info(request, "El tema vuelve a estar en curso.")
            return redirect("tema", materia=materia, slug=slug)
        if form.is_valid():
            form.save()
            messages.success(request, "Cuaderno guardado.")
            return redirect("tema", materia=materia, slug=slug)
    repasos = Repaso.objects.filter(usuario=request.user, tema=tema).order_by("-fecha")[:8]
    sesiones = Tarea.objects.filter(usuario=request.user, tema=tema, hecha=True).order_by("hecha_el")
    return render(request, "estudio/tema.html", {
        "tema": tema, "progreso": progreso, "form": form, "repasos": repasos,
        "sesiones": sesiones,
    })


@login_required
def calendario(request):
    fecha = hoy_local()
    perfil = plan.perfil_de(request.user)
    etapa = perfil.etapa_actual(fecha)
    lunes = fecha - timedelta(days=fecha.weekday())
    proyeccion = plan.proyeccion(request.user, fecha, dias=14)
    proximos_repasos = Repaso.objects.filter(
        usuario=request.user, hecho_el__isnull=True
    ).select_related("tema__materia")[:30]
    # Lo hecho esta semana antes de hoy, para ver la semana completa.
    pasados = []
    for i in range(fecha.weekday()):
        dia = lunes + timedelta(days=i)
        pasados.append({
            "fecha": dia,
            "dia": plan.DIAS[dia.weekday()],
            "tareas": Tarea.objects.filter(usuario=request.user, hecha_el=dia).select_related("tema__materia"),
        })
    return render(request, "estudio/calendario.html", {
        "fecha": fecha,
        "etapa": etapa,
        "etapas": Etapa.objects.select_related("principal", "complementaria", "sustituta"),
        "proyeccion": proyeccion,
        "pasados": pasados,
        "proximos_repasos": proximos_repasos,
    })


def racha(usuario, hoy):
    """Días seguidos con al menos una tarea o repaso hecho. Los domingos no rompen la racha."""
    dias = set(
        Tarea.objects.filter(usuario=usuario, hecha=True, hecha_el__gte=hoy - timedelta(days=400))
        .values_list("hecha_el", flat=True)
    ) | set(
        Repaso.objects.filter(usuario=usuario, hecho_el__gte=hoy - timedelta(days=400))
        .values_list("hecho_el", flat=True)
    )
    dia = hoy if hoy in dias else hoy - timedelta(days=1)
    cuenta = 0
    while True:
        if dia in dias:
            cuenta += 1
        elif dia.weekday() != plan.DOMINGO:
            break
        dia -= timedelta(days=1)
        if cuenta > 400 or (hoy - dia).days > 400:
            break
    return cuenta


@login_required
def progreso(request):
    fecha = hoy_local()
    usuario = request.user
    tareas_hechas = Tarea.objects.filter(usuario=usuario, hecha=True)
    sesiones = tareas_hechas.filter(tipo=Tarea.ESTUDIO).count()
    minutos = tareas_hechas.aggregate(m=Sum("minutos"))["m"] or 0

    materias = Materia.objects.annotate(
        total=Count("temas", distinct=True),
        dominados=Count(
            "temas__progresotema",
            filter=Q(temas__progresotema__usuario=usuario, temas__progresotema__estado=ProgresoTema.DOMINADO),
            distinct=True,
        ),
        en_curso=Count(
            "temas__progresotema",
            filter=Q(temas__progresotema__usuario=usuario, temas__progresotema__estado=ProgresoTema.EN_CURSO),
            distinct=True,
        ),
    )

    # Mapa de las últimas 12 semanas: cuántas cosas tachaste cada día.
    inicio = fecha - timedelta(days=fecha.weekday() + 7 * 11)
    conteo = {}
    for d in tareas_hechas.filter(hecha_el__gte=inicio).values_list("hecha_el", flat=True):
        conteo[d] = conteo.get(d, 0) + 1
    for d in Repaso.objects.filter(usuario=usuario, hecho_el__gte=inicio).values_list("hecho_el", flat=True):
        conteo[d] = conteo.get(d, 0) + 1
    semanas = []
    for s in range(12):
        semana = []
        for d in range(7):
            dia = inicio + timedelta(days=s * 7 + d)
            n = conteo.get(dia, 0)
            semana.append({"fecha": dia, "n": n, "futuro": dia > fecha,
                           "nivel": 0 if n == 0 else 1 if n == 1 else 2 if n <= 3 else 3})
        semanas.append(semana)


    return render(request, "estudio/progreso.html", {
        "racha": racha(usuario, fecha),
        "sesiones": sesiones,
        "horas": round(minutos / 60, 1),
        "dominados": ProgresoTema.objects.filter(usuario=usuario, estado=ProgresoTema.DOMINADO).count(),
        "repasos": Repaso.objects.filter(usuario=usuario, hecho_el__isnull=False).count(),
        "materias": materias,
        "semanas": semanas,
        "libro_actual": plan.libro_actual(usuario),
        "libros_terminados": LecturaLibro.objects.filter(usuario=usuario, terminado__isnull=False).count(),
        "libros_total": Libro.objects.count(),
        "dias_cortos": ["L", "M", "X", "J", "V", "S", "D"],
    })


def volver(request, por_defecto):
    """Redirige a «siguiente» si es una ruta de este sitio; si no, a la vista por defecto."""
    siguiente = request.POST.get("siguiente", "")
    if siguiente.startswith("/") and not siguiente.startswith("//"):
        return redirect(siguiente)
    return redirect(por_defecto)


@login_required
def libros(request):
    usuario = request.user
    lecturas = {l.libro_id: l for l in LecturaLibro.objects.filter(usuario=usuario)}
    actual = plan.libro_actual(usuario)
    solo_tengo = request.GET.get("filtro") == "tengo"
    anios = []
    for anio, etiqueta in Libro.ANIOS:
        filas = [
            {"libro": b, "lectura": lecturas.get(b.id), "actual": actual and b.id == actual.id}
            for b in Libro.objects.filter(anio=anio).select_related("materia")
        ]
        if solo_tengo:
            filas = [f for f in filas if f["lectura"] and f["lectura"].tengo]
        if filas:
            terminados = sum(1 for f in filas if f["lectura"] and f["lectura"].terminado)
            anios.append({"etiqueta": etiqueta, "filas": filas, "terminados": terminados})
    total = Libro.objects.count()
    terminados = sum(1 for l in lecturas.values() if l.terminado)
    return render(request, "estudio/libros.html", {
        "anios": anios,
        "actual": actual,
        "lectura_actual": lecturas.get(actual.id) if actual else None,
        "total": total,
        "terminados": terminados,
        "solo_tengo": solo_tengo,
        "cuantos_tengo": sum(1 for l in lecturas.values() if l.tengo),
    })


@login_required
@require_POST
def libro_tengo(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    lectura, _ = LecturaLibro.objects.get_or_create(usuario=request.user, libro=libro)
    lectura.tengo = not lectura.tengo
    lectura.save(update_fields=["tengo"])
    # Si la lectura de hoy no la elegiste tú, se ajusta para priorizar lo que tienes.
    if not plan.perfil_de(request.user).libro_actual_id:
        anterior = Tarea.objects.filter(
            usuario=request.user, tipo=Tarea.LECTURA, hecha=False
        ).select_related("libro").first()
        nuevo = plan.libro_actual(request.user)
        if anterior and anterior.libro_id != (nuevo and nuevo.id):
            plan.cambiar_lectura_pendiente(request.user, anterior.libro, nuevo)
    return volver(request, "libros")


@login_required
@require_POST
def elegir_libro(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    anterior = plan.libro_actual(request.user)
    perfil = plan.perfil_de(request.user)
    perfil.libro_actual = libro
    perfil.save(update_fields=["libro_actual"])
    LecturaLibro.objects.filter(usuario=request.user, libro=libro).update(terminado=None)
    plan.cambiar_lectura_pendiente(request.user, anterior, libro)
    messages.success(request, f"Ahora lees «{libro.titulo}».")
    return volver(request, "libros")


@login_required
@require_POST
def libro_terminado(request, pk):
    libro = get_object_or_404(Libro, pk=pk)
    lectura, _ = LecturaLibro.objects.get_or_create(usuario=request.user, libro=libro)
    lectura.terminado = None if lectura.terminado else hoy_local()
    lectura.save()
    if lectura.terminado:
        perfil = plan.perfil_de(request.user)
        if perfil.libro_actual_id == libro.id:
            perfil.libro_actual = None
            perfil.save(update_fields=["libro_actual"])
        # La tarea de lectura pendiente pasa al siguiente libro.
        plan.cambiar_lectura_pendiente(request.user, libro, plan.libro_actual(request.user))
        messages.success(request, f"¡Terminaste «{libro.titulo}»!")
    return volver(request, "libros")


@login_required
@require_POST
def cambiar_apariencia(request):
    perfil = plan.perfil_de(request.user)
    perfil.apariencia = perfil.OSCURO if perfil.apariencia == perfil.CLARO else perfil.CLARO
    perfil.save(update_fields=["apariencia"])
    return volver(request, "hoy")


@login_required
def ajustes(request):
    perfil = plan.perfil_de(request.user)
    form = PerfilForm(request.POST or None, instance=perfil)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Ajustes guardados.")
        return redirect("ajustes")
    return render(request, "estudio/ajustes.html", {"form": form})
