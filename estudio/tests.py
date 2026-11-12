from io import StringIO
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from . import plan
from .models import Libro, Perfil, ProgresoTema, Repaso, Tarea, Tema

LUNES = date(2026, 11, 9)


class PlanTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("cargar_plan", stdout=StringIO())

    def setUp(self):
        self.usuario = User.objects.create_user("ana", password="clave-segura-123")
        Perfil.objects.create(usuario=self.usuario, fecha_inicio=LUNES, ingles=False)

    def estudio_pendiente(self):
        return Tarea.objects.filter(usuario=self.usuario, tipo=Tarea.ESTUDIO, hecha=False)

    def test_lunes_toca_matematicas_y_lectura(self):
        pendientes, *_ = plan.checklist(self.usuario, LUNES)
        tipos = {t.tipo for t in pendientes}
        self.assertEqual(tipos, {Tarea.ESTUDIO, Tarea.LECTURA})
        estudio = next(t for t in pendientes if t.tipo == Tarea.ESTUDIO)
        self.assertEqual(estudio.tema.materia.slug, "matematicas")
        self.assertEqual(estudio.numero_sesion, 1)

    def test_generar_dos_veces_no_duplica(self):
        plan.checklist(self.usuario, LUNES)
        plan.checklist(self.usuario, LUNES)
        self.assertEqual(Tarea.objects.filter(usuario=self.usuario).count(), 2)

    def test_no_se_acumula_y_se_retoma_donde_quedo(self):
        plan.checklist(self.usuario, LUNES)
        # No estudia el lunes. El martes solo aparece lo del martes: lógica + una lectura.
        pendientes, *_ = plan.checklist(self.usuario, LUNES + timedelta(days=1))
        self.assertEqual(
            sorted(t.tema.materia.slug for t in pendientes if t.tipo == Tarea.ESTUDIO), ["logica"]
        )
        self.assertEqual(sum(t.tipo == Tarea.LECTURA for t in pendientes), 1)

        # Faltan varios días más. Al volver el lunes siguiente, nada está amontonado
        # y matemáticas sigue en el tema 1, sesión 1.
        pendientes, *_ = plan.checklist(self.usuario, LUNES + timedelta(days=7))
        estudios = [t for t in pendientes if t.tipo == Tarea.ESTUDIO]
        self.assertEqual(len(estudios), 1)
        self.assertEqual((estudios[0].tema.orden, estudios[0].numero_sesion), (1, 1))
        self.assertEqual(len(pendientes), 2)  # estudio + lectura
        self.assertFalse(Tarea.objects.filter(usuario=self.usuario, fecha__lt=LUNES + timedelta(days=7)).exists())

    def test_lo_hecho_se_conserva_y_avanza_solo_al_estudiar(self):
        pendientes, *_ = plan.checklist(self.usuario, LUNES)
        estudio = next(t for t in pendientes if t.tipo == Tarea.ESTUDIO)
        plan.completar_tarea(estudio, LUNES)
        # Se salta miércoles y viernes; el lunes siguiente toca la sesión 2 del tema 1.
        pendientes, *_ = plan.checklist(self.usuario, LUNES + timedelta(days=7))
        mate = next(t for t in pendientes if t.tipo == Tarea.ESTUDIO)
        self.assertEqual((mate.tema, mate.numero_sesion), (estudio.tema, 2))
        self.assertTrue(Tarea.objects.filter(pk=estudio.pk, hecha=True).exists())

    def test_repasos_no_se_amontonan(self):
        for tema in Tema.objects.filter(materia__slug="logica")[:6]:
            Repaso.objects.create(usuario=self.usuario, tema=tema, fecha=LUNES - timedelta(days=5))
        _, _, repasos, _ = plan.checklist(self.usuario, LUNES)
        self.assertEqual(len(repasos), plan.MAX_REPASOS_DIA)

    def test_completar_sesion_avanza_y_programa_repaso(self):
        pendientes, *_ = plan.checklist(self.usuario, LUNES)
        estudio = next(t for t in pendientes if t.tipo == Tarea.ESTUDIO)
        plan.completar_tarea(estudio, LUNES)
        prog = ProgresoTema.objects.get(usuario=self.usuario, tema=estudio.tema)
        self.assertEqual(prog.sesiones_hechas, 1)
        self.assertEqual(prog.estado, ProgresoTema.EN_CURSO)
        repaso = Repaso.objects.get(usuario=self.usuario, tema=estudio.tema)
        self.assertEqual(repaso.fecha, LUNES + timedelta(days=1))
        # El miércoles toca la sesión 2 del mismo tema.
        plan.checklist(self.usuario, LUNES + timedelta(days=2))
        mate = self.estudio_pendiente().get(tema__materia__slug="matematicas")
        self.assertEqual((mate.tema, mate.numero_sesion), (estudio.tema, 2))

    def test_comprobacion_del_80_por_ciento(self):
        tema = Tema.objects.get(materia__slug="matematicas", orden=1)
        ProgresoTema.objects.create(usuario=self.usuario, tema=tema, sesiones_hechas=3,
                                    estado=ProgresoTema.EN_CURSO)
        plan.checklist(self.usuario, LUNES)
        comprobar = self.estudio_pendiente().get()
        self.assertTrue(comprobar.es_comprobacion)

        # Aún no lo domina: se añade una sesión extra del mismo tema.
        plan.completar_tarea(comprobar, LUNES, logrado=False)
        extra = plan.crear_tarea_estudio(self.usuario, tema.materia, LUNES)
        self.assertEqual((extra.tema, extra.es_comprobacion), (tema, False))
        plan.completar_tarea(extra, LUNES)

        # Nueva comprobación, ahora sí lo domina: pasa al tema 2.
        comprobar = plan.crear_tarea_estudio(self.usuario, tema.materia, LUNES)
        self.assertTrue(comprobar.es_comprobacion)
        plan.completar_tarea(comprobar, LUNES, logrado=True)
        self.assertEqual(
            ProgresoTema.objects.get(usuario=self.usuario, tema=tema).estado, ProgresoTema.DOMINADO
        )
        siguiente = plan.crear_tarea_estudio(self.usuario, tema.materia, LUNES)
        self.assertEqual(siguiente.tema.orden, 2)

    def test_deshacer_revierte_el_progreso(self):
        pendientes, *_ = plan.checklist(self.usuario, LUNES)
        estudio = next(t for t in pendientes if t.tipo == Tarea.ESTUDIO)
        plan.completar_tarea(estudio, LUNES)
        plan.deshacer_tarea(estudio)
        estudio.refresh_from_db()
        self.assertFalse(estudio.hecha)
        self.assertEqual(
            ProgresoTema.objects.get(usuario=self.usuario, tema=estudio.tema).sesiones_hechas, 0
        )

    def test_repaso_espaciado(self):
        tema = Tema.objects.get(materia__slug="matematicas", orden=1)
        r = Repaso.objects.create(usuario=self.usuario, tema=tema, fecha=LUNES + timedelta(days=1))
        martes = LUNES + timedelta(days=1)
        r2 = r.completar(Repaso.FACIL, martes)
        self.assertEqual(r2.fecha, martes + timedelta(days=2))  # jueves
        r3 = r2.completar(Repaso.FACIL, r2.fecha)
        self.assertEqual(r3.fecha, LUNES + timedelta(days=7))  # lunes siguiente
        r4 = r3.completar(Repaso.OLVIDE, r3.fecha)
        self.assertEqual((r4.nivel, r4.fecha), (0, r3.fecha + timedelta(days=1)))

    def test_ingles_avanza_por_su_temario_en_paralelo(self):
        perfil = self.usuario.perfil
        perfil.ingles = True
        perfil.save()
        pendientes, *_ = plan.checklist(self.usuario, LUNES)
        ingles = next(t for t in pendientes if t.tipo == Tarea.INGLES)
        self.assertTrue(ingles.opcional)
        self.assertEqual((ingles.tema.materia.slug, ingles.tema.orden, ingles.numero_sesion), ("ingles", 1, 1))
        plan.completar_tarea(ingles, LUNES)
        pendientes, *_ = plan.checklist(self.usuario, LUNES + timedelta(days=1))
        ingles = next(t for t in pendientes if t.tipo == Tarea.INGLES)
        self.assertEqual(ingles.numero_sesion, 2)
        # La materia del día sigue apareciendo junto al inglés.
        self.assertTrue(any(t.tipo == Tarea.ESTUDIO for t in pendientes))

    def test_nivel_avanzado_va_despues_del_basico(self):
        temas = list(Tema.objects.filter(materia__slug="logica"))
        niveles = [t.nivel for t in temas]
        self.assertEqual(niveles, sorted(niveles))
        self.assertEqual(set(niveles), {Tema.BASICO, Tema.AVANZADO, Tema.EXPERTO})

    def test_elegir_y_terminar_libro_cambia_la_lectura_del_dia(self):
        pendientes, *_ = plan.checklist(self.usuario, LUNES)
        lectura = next(t for t in pendientes if t.tipo == Tarea.LECTURA)
        primero = Libro.objects.first()
        self.assertEqual(lectura.libro, primero)

        elegido = Libro.objects.get(titulo="Cosmos")
        self.client.force_login(self.usuario)
        self.client.post(reverse("elegir_libro", args=[elegido.pk]))
        lectura.refresh_from_db()
        self.assertEqual(lectura.libro, elegido)
        self.assertIn("Cosmos", lectura.titulo)

        # Al terminarlo, se vuelve al siguiente libro sin terminar de la lista.
        self.client.post(reverse("libro_terminado", args=[elegido.pk]))
        lectura.refresh_from_db()
        self.assertEqual(lectura.libro, primero)
        self.assertEqual(self.client.get(reverse("libros")).status_code, 200)

    def test_la_lectura_es_siempre_el_primero_de_la_lista(self):
        pendientes, *_ = plan.checklist(self.usuario, LUNES)
        lectura = next(t for t in pendientes if t.tipo == Tarea.LECTURA)
        primero = Libro.objects.first()
        self.assertEqual(lectura.libro, primero)
        holmes = Libro.objects.get(titulo="Las novelas completas de Sherlock Holmes")
        self.client.force_login(self.usuario)
        self.client.post(reverse("libro_tengo", args=[holmes.pk]))
        lectura.refresh_from_db()
        self.assertEqual(lectura.libro, primero)
        r = self.client.get(reverse("libros") + "?filtro=tengo")
        self.assertContains(r, "Sherlock Holmes")
        self.assertNotContains(r, "Las claves de la argumentación")

        # Una lectura pendiente con otro libro se corrige al abrir el día.
        lectura.libro = holmes
        lectura.save()
        for dia in range(3):
            pendientes, *_ = plan.checklist(self.usuario, LUNES + timedelta(days=dia))
            lectura = next(t for t in pendientes if t.tipo == Tarea.LECTURA)
            self.assertEqual(lectura.libro, primero)

    def test_jueves_de_la_etapa_1_es_aprender_a_aprender(self):
        jueves = LUNES + timedelta(days=3)
        etapa = self.usuario.perfil.etapa_actual(jueves)
        self.assertEqual(plan.materia_del_dia(etapa, jueves, self.usuario).slug, "aprender")
        # Al terminar el curso, el jueves vuelve a ser lógica.
        for tema in Tema.objects.filter(materia__slug="aprender"):
            ProgresoTema.objects.create(usuario=self.usuario, tema=tema, estado=ProgresoTema.DOMINADO)
        self.assertEqual(plan.materia_del_dia(etapa, jueves, self.usuario).slug, "logica")

    def test_etapa_avanza_cada_dos_meses(self):
        perfil = self.usuario.perfil
        self.assertEqual(perfil.etapa_actual(LUNES).orden, 1)
        self.assertEqual(perfil.etapa_actual(date(2027, 1, 8)).orden, 1)
        self.assertEqual(perfil.etapa_actual(date(2027, 1, 9)).orden, 2)
        self.assertEqual(perfil.etapa_actual(date(2027, 11, 9)).orden, 7)  # segundo año
        self.assertEqual(perfil.etapa_actual(date(2028, 11, 9)).orden, 13)  # tercer año
        self.assertEqual(perfil.etapa_actual(date(2035, 1, 1)).orden, 18)

    def test_proyeccion_cubre_dos_semanas(self):
        dias = plan.proyeccion(self.usuario, LUNES, dias=14)
        self.assertEqual(len(dias), 14)
        mates = [d["estudio"] for d in dias if d["materia"] and d["materia"].slug == "matematicas"]
        # Lun, Mié, Vie: sesiones 1, 2, 3 del tema 1; luego la comprobación.
        self.assertEqual(mates[0]["tema"], mates[2]["tema"])
        self.assertIn("Comprobar", mates[3]["paso"])


class VistasTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("cargar_plan", stdout=StringIO())

    def test_registro_y_paginas(self):
        r = self.client.post(reverse("registro"), {
            "username": "luis", "password1": "una-clave-larga-9", "password2": "una-clave-larga-9",
            "zona_horaria": "America/Managua",
        })
        self.assertRedirects(r, reverse("hoy"))
        for nombre in ["hoy", "temario", "calendario", "progreso", "libros", "guia", "ajustes"]:
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 200, nombre)

        tarea = Tarea.objects.filter(tipo=Tarea.ESTUDIO).first()
        if tarea:
            self.assertEqual(self.client.get(reverse("sesion", args=[tarea.pk])).status_code, 200)
            self.client.post(reverse("completar", args=[tarea.pk]), {"minutos": "30"})
            tarea.refresh_from_db()
            self.assertTrue(tarea.hecha)
            self.assertEqual(tarea.minutos, 30)
        tema = Tema.objects.first()
        url = reverse("tema", args=[tema.materia.slug, tema.slug])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_todas_las_guias_se_muestran(self):
        from .guias import GUIAS
        usuario = User.objects.create_user("gus", password="clave-segura-123")
        Perfil.objects.create(usuario=usuario)
        self.client.force_login(usuario)
        for g in GUIAS:
            r = self.client.get(reverse("guia_detalle", args=[g["slug"]]))
            self.assertContains(r, g["titulo"])
        self.assertEqual(self.client.get(reverse("guia_detalle", args=["no-existe"])).status_code, 404)

    def test_requiere_login(self):
        r = self.client.get(reverse("hoy"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("login"), r.url)
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)

    def test_modo_claro_por_defecto_y_cambio_a_oscuro(self):
        usuario = User.objects.create_user("eva", password="clave-segura-123")
        Perfil.objects.create(usuario=usuario)
        self.client.force_login(usuario)
        self.assertContains(self.client.get(reverse("temario")), 'data-theme="light"')
        r = self.client.post(reverse("cambiar_apariencia"), {"siguiente": reverse("temario")})
        self.assertRedirects(r, reverse("temario"))
        self.assertContains(self.client.get(reverse("temario")), 'data-theme="dark"')
        # Una redirección a otro sitio se ignora.
        r = self.client.post(reverse("cambiar_apariencia"), {"siguiente": "//malo.com"})
        self.assertRedirects(r, reverse("hoy"), fetch_redirect_response=False)


class BookTrackerTests(TestCase):
    """Conexión de solo lectura con BookTracker (la API se simula)."""

    @classmethod
    def setUpTestData(cls):
        call_command("cargar_plan", stdout=StringIO())

    def setUp(self):
        self.usuario = User.objects.create_user("ana", password="clave-segura-123")
        Perfil.objects.create(usuario=self.usuario, fecha_inicio=LUNES, ingles=False)
        from django.core.cache import cache
        cache.clear()
        self.client.force_login(self.usuario)

    def test_conectar_guarda_token_y_no_la_contrasena(self):
        from unittest import mock
        with mock.patch("estudio.booktracker.obtener_token", return_value="abc123") as ot:
            r = self.client.post(reverse("booktracker_conectar"), {"usuario": "ana", "contrasena": "secreta"})
        self.assertRedirects(r, reverse("ajustes"))
        ot.assert_called_once_with("ana", "secreta")
        perfil = Perfil.objects.get(usuario=self.usuario)
        self.assertEqual((perfil.booktracker_usuario, perfil.booktracker_token), ("ana", "abc123"))

    def test_credenciales_invalidas_muestran_error(self):
        from unittest import mock
        from . import booktracker
        with mock.patch("estudio.booktracker.obtener_token",
                        side_effect=booktracker.CredencialesInvalidas("Usuario o contraseña incorrectos.")):
            r = self.client.post(reverse("booktracker_conectar"), {"usuario": "ana", "contrasena": "mal"})
        self.assertContains(r, "Usuario o contraseña incorrectos.")
        self.assertEqual(Perfil.objects.get(usuario=self.usuario).booktracker_token, "")

    def test_libros_muestra_progreso_y_empareja_titulos(self):
        from unittest import mock
        Perfil.objects.filter(usuario=self.usuario).update(booktracker_token="abc123")
        libro = Libro.objects.first()
        datos = [{"title": libro.titulo.upper(), "author": libro.autor, "status": "READING",
                  "pages_read": 40, "total_pages": 200, "progress_percentage": 20}]
        with mock.patch("estudio.booktracker._peticion", return_value=datos) as pet:
            r = self.client.get(reverse("libros"))
            self.client.get(reverse("libros"))  # segunda vez sale de la caché
        pet.assert_called_once_with("GET", "books/", token="abc123")
        self.assertContains(r, "Leyendo en BookTracker")
        self.assertContains(r, "40/200 pág")
        self.assertContains(r, "BookTracker · 20 %")

    def test_muestra_portadas_seguras(self):
        from unittest import mock
        Perfil.objects.filter(usuario=self.usuario).update(booktracker_token="abc123")
        libro = Libro.objects.first()
        datos = [
            {"title": libro.titulo, "author": "", "status": "READING", "pages_read": 1, "total_pages": 9,
             "progress_percentage": 11, "cover_url": "https://covers.example/a.jpg"},
            {"title": "Otro", "author": "", "status": "READING", "pages_read": 1, "total_pages": 9,
             "progress_percentage": 11, "cover_url": "javascript:alert(1)"},
        ]
        with mock.patch("estudio.booktracker._peticion", return_value=datos):
            r = self.client.get(reverse("libros"))
        self.assertContains(r, 'src="https://covers.example/a.jpg"', count=3)  # leyendo ahora + BookTracker + fila del plan
        self.assertNotContains(r, "javascript:alert")

    def _hoy_con_booktracker(self, sesiones):
        from unittest import mock
        Perfil.objects.filter(usuario=self.usuario).update(booktracker_token="abc123")
        libro = plan.libro_actual(self.usuario)
        libros_bt = [{"id": 7, "title": libro.titulo, "author": "Autora", "status": "READING",
                      "category_name": "Ensayo", "pages_read": 120, "total_pages": 300,
                      "progress_percentage": 40, "pages_remaining": 180, "total_time_read": "2h 5m",
                      "cover_url": "https://covers.example/hoy.jpg"}]

        def falsa(metodo, ruta, token=None, cuerpo=None):
            if ruta == "books/7/sessions/":
                if isinstance(sesiones, Exception):
                    raise sesiones
                return sesiones
            return libros_bt

        with mock.patch("estudio.views.hoy_local", return_value=LUNES), \
                mock.patch("estudio.booktracker._peticion", side_effect=falsa):
            return self.client.get(reverse("hoy"))

    def test_hoy_muestra_ficha_del_libro(self):
        r = self._hoy_con_booktracker([
            {"id": 2, "end_page": 120, "duration_minutes": "25.00", "date": "2026-11-08", "notes": "Idea clave"},
            {"id": 1, "end_page": 60, "duration_minutes": "30.00", "date": "2026-11-01", "notes": ""},
        ])
        for texto in ['src="https://covers.example/hoy.jpg"', "Ensayo", "Página 120 de 300", "180 páginas",
                      "2h 5m · 2 sesiones", "hasta la página 120 · 25 min", "Idea clave",
                      "https://booktracker.up.railway.app/book/7/"]:
            self.assertContains(r, texto)

    def test_hoy_sin_sesiones_sigue_mostrando_la_ficha(self):
        from . import booktracker
        r = self._hoy_con_booktracker(booktracker.BookTrackerError("caído"))
        self.assertContains(r, "Página 120 de 300")
        self.assertNotContains(r, "Última sesión")

    def test_token_invalido_desconecta_sin_romper(self):
        from unittest import mock
        from . import booktracker
        Perfil.objects.filter(usuario=self.usuario).update(booktracker_token="viejo")
        with mock.patch("estudio.booktracker._peticion", side_effect=booktracker.TokenInvalido("Token caducado.")):
            r = self.client.get(reverse("libros"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Vuelve a conectarlo en Ajustes")
        self.assertEqual(Perfil.objects.get(usuario=self.usuario).booktracker_token, "")

    def test_booktracker_caido_no_rompe_libros(self):
        from unittest import mock
        from . import booktracker
        Perfil.objects.filter(usuario=self.usuario).update(booktracker_token="abc123")
        with mock.patch("estudio.booktracker._peticion",
                        side_effect=booktracker.BookTrackerError("No se pudo conectar con BookTracker.")):
            r = self.client.get(reverse("libros"))
        self.assertContains(r, "No se pudo conectar con BookTracker.")
        self.assertEqual(Perfil.objects.get(usuario=self.usuario).booktracker_token, "abc123")

    def test_desconectar(self):
        Perfil.objects.filter(usuario=self.usuario).update(booktracker_token="abc123", booktracker_usuario="ana")
        self.client.post(reverse("booktracker_desconectar"))
        perfil = Perfil.objects.get(usuario=self.usuario)
        self.assertEqual((perfil.booktracker_usuario, perfil.booktracker_token), ("", ""))


class MinutosLecturaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("cargar_plan", stdout=StringIO())

    def setUp(self):
        self.usuario = User.objects.create_user("ana", password="clave-segura-123")
        self.perfil = Perfil.objects.create(usuario=self.usuario, fecha_inicio=LUNES, ingles=False)

    def lectura(self):
        return Tarea.objects.get(usuario=self.usuario, tipo=Tarea.LECTURA, hecha=False)

    def test_automatico_sigue_la_sesion(self):
        plan.checklist(self.usuario, LUNES)
        self.assertTrue(self.lectura().titulo.startswith("Leer 8 min:"))

    def test_elegido_en_perfil_se_usa_al_generar(self):
        Perfil.objects.filter(pk=self.perfil.pk).update(minutos_lectura=20)
        plan.checklist(self.usuario, LUNES)
        self.assertTrue(self.lectura().titulo.startswith("Leer 20 min:"))

    def test_cambiarlo_en_ajustes_actualiza_la_tarea_pendiente(self):
        plan.checklist(self.usuario, LUNES)
        self.client.force_login(self.usuario)
        r = self.client.post(reverse("ajustes"), {
            "fecha_inicio": "2026-11-09", "minutos_sesion": 30, "minutos_lectura": 15, "minutos_ingles": 10,
            "zona_horaria": "America/Mexico_City", "apariencia": "claro",
        })
        self.assertRedirects(r, reverse("ajustes"))
        self.assertEqual(Perfil.objects.get(pk=self.perfil.pk).minutos_lectura, 15)
        self.assertTrue(self.lectura().titulo.startswith("Leer 15 min:"))


class ChatGPTTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("cargar_plan", stdout=StringIO())

    def setUp(self):
        self.usuario = User.objects.create_user("ana", password="clave-segura-123")
        Perfil.objects.create(usuario=self.usuario, fecha_inicio=LUNES, ingles=False)
        self.client.force_login(self.usuario)

    def test_prompt_incluye_tema_y_cuaderno(self):
        plan.checklist(self.usuario, LUNES)
        tarea = Tarea.objects.get(usuario=self.usuario, tipo=Tarea.ESTUDIO)
        progreso = ProgresoTema.objects.create(usuario=self.usuario, tema=tarea.tema, preguntas="No entiendo X")
        prompt = plan.prompt_chatgpt(tarea, 30, progreso)
        self.assertIn("profesor particular", prompt)
        self.assertIn(tarea.tema.titulo, prompt)
        self.assertIn(tarea.tema.materia.nombre, prompt)
        self.assertIn("Tengo 30 minutos", prompt)
        self.assertIn("Dudas que me quedaron: No entiendo X", prompt)

    def test_hoy_y_sesion_enlazan_chatgpt(self):
        from unittest import mock
        from urllib.parse import quote
        with mock.patch("estudio.views.hoy_local", return_value=LUNES):
            r = self.client.get(reverse("hoy"))
        tarea = Tarea.objects.get(usuario=self.usuario, tipo=Tarea.ESTUDIO)
        self.assertContains(r, 'data-chatgpt="https://chatgpt.com/?q=')
        self.assertContains(r, quote(tarea.tema.titulo))
        r = self.client.get(reverse("sesion", args=[tarea.pk]))
        self.assertContains(r, "Abrir tutor en ChatGPT")

    def test_prompt_de_ingles_pide_explicar_en_ingles(self):
        tema = Tema.objects.filter(materia__slug="ingles").first()
        tarea = Tarea.objects.create(usuario=self.usuario, fecha=LUNES, tipo=Tarea.INGLES,
                                     tema=tema, numero_sesion=1, titulo="Inglés")
        prompt = plan.prompt_chatgpt(tarea, 10)
        self.assertIn("Explícame y respóndeme en inglés", prompt)
        self.assertNotIn("Respóndeme en español", prompt)
        self.assertNotIn("explícame en español", prompt)

    def test_prompt_normal_sigue_en_espanol(self):
        plan.checklist(self.usuario, LUNES)
        tarea = Tarea.objects.get(usuario=self.usuario, tipo=Tarea.ESTUDIO)
        prompt = plan.prompt_chatgpt(tarea, 30)
        self.assertIn("Respóndeme en español", prompt)
        self.assertNotIn("en inglés", prompt)


class MinutosInglesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("cargar_plan", stdout=StringIO())

    def setUp(self):
        self.usuario = User.objects.create_user("ana", password="clave-segura-123")
        self.perfil = Perfil.objects.create(usuario=self.usuario, fecha_inicio=LUNES, ingles=True)
        self.client.force_login(self.usuario)

    def test_por_defecto_son_10_minutos(self):
        plan.checklist(self.usuario, LUNES)
        tarea = Tarea.objects.get(usuario=self.usuario, tipo=Tarea.INGLES)
        self.assertEqual(plan.minutos_de(tarea, self.perfil), 10)

    def test_ajustes_cambia_la_sesion_y_el_prompt(self):
        plan.checklist(self.usuario, LUNES)
        r = self.client.post(reverse("ajustes"), {
            "fecha_inicio": "2026-11-09", "minutos_sesion": 30, "minutos_ingles": 20,
            "zona_horaria": "America/Mexico_City", "apariencia": "claro", "ingles": "on",
        })
        self.assertRedirects(r, reverse("ajustes"))
        tarea = Tarea.objects.get(usuario=self.usuario, tipo=Tarea.INGLES)
        r = self.client.get(reverse("sesion", args=[tarea.pk]))
        self.assertEqual(r.context["minutos"], 20)
        self.assertIn("Tengo 20 minutos", plan.prompt_chatgpt(tarea, r.context["minutos"]))

    def test_practica_libre_usa_los_minutos_elegidos(self):
        Perfil.objects.filter(pk=self.perfil.pk).update(minutos_ingles=15)
        Tarea.objects.create(usuario=self.usuario, fecha=LUNES, tipo=Tarea.INGLES, opcional=True,
                             titulo="Inglés: 10 min de práctica libre")
        Perfil.objects.filter(pk=self.perfil.pk).update(minutos_ingles=30)
        plan.actualizar_minutos(self.usuario)
        self.assertEqual(Tarea.objects.get(usuario=self.usuario, tipo=Tarea.INGLES).titulo,
                         "Inglés: 30 min de práctica libre")
