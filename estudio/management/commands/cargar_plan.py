from django.core.management.base import BaseCommand
from django.db import transaction

from estudio import temario
from estudio.models import Etapa, Libro, Materia, Tema


class Command(BaseCommand):
    help = "Carga o actualiza materias, temas, etapas y libros del plan (sin borrar progreso)."

    @transaction.atomic
    def handle(self, *args, **options):
        for orden, datos in enumerate(temario.MATERIAS, start=1):
            materia, _ = Materia.objects.update_or_create(
                slug=datos["slug"],
                defaults={
                    "nombre": datos["nombre"],
                    "descripcion": datos["descripcion"],
                    "color": datos["color"],
                    "orden": orden,
                },
            )
            slugs = []
            temas = [(t, Tema.BASICO) for t in datos["temas"]]
            for nivel, extra in [(Tema.AVANZADO, temario.AVANZADOS), (Tema.EXPERTO, temario.EXPERTOS)]:
                temas += [(t, nivel) for t in extra.get(datos["slug"], [])]
            for i, ((slug, titulo, descripcion, *resto), nivel) in enumerate(temas, start=1):
                slugs.append(slug)
                preguntas = "\n".join(resto[0]) if resto else ""
                Tema.objects.update_or_create(
                    materia=materia,
                    slug=slug,
                    defaults={
                        "orden": i,
                        "titulo": titulo,
                        "descripcion": descripcion,
                        "recurso": datos["recurso"],
                        "recurso_url": datos["url"],
                        "sesiones": datos.get("sesiones", 3),
                        "preguntas": preguntas,
                        "nivel": nivel,
                    },
                )
            # No se borran temas retirados (guardan progreso); solo se avisa.
            for tema in materia.temas.exclude(slug__in=slugs):
                self.stdout.write(self.style.WARNING(f"Tema fuera del temario: {tema}"))

        materias = {m.slug: m for m in Materia.objects.all()}
        for orden, nombre, principal, complementaria, sustituta, dia in temario.ETAPAS:
            Etapa.objects.update_or_create(
                orden=orden,
                defaults={
                    "nombre": nombre,
                    "principal": materias[principal],
                    "complementaria": materias[complementaria],
                    "sustituta": materias.get(sustituta) if sustituta else None,
                    "dia_sustituto": dia,
                },
            )

        titulos = []
        for orden, (titulo, autor, para_que, materia, anio) in enumerate(temario.LIBROS, start=1):
            titulos.append(titulo)
            Libro.objects.update_or_create(
                titulo=titulo,
                defaults={
                    "orden": orden, "autor": autor, "para_que": para_que,
                    "materia": materias.get(materia), "anio": anio,
                },
            )
        for libro in Libro.objects.exclude(titulo__in=titulos):
            self.stdout.write(self.style.WARNING(f"Libro fuera de la lista: {libro}"))

        self.stdout.write(self.style.SUCCESS(
            f"Plan cargado: {Materia.objects.count()} materias, {Tema.objects.count()} temas, "
            f"{Etapa.objects.count()} etapas, {Libro.objects.count()} libros."
        ))
