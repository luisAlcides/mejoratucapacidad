from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


# --- Temario común a todos los usuarios ------------------------------------


class Materia(models.Model):
    slug = models.SlugField(unique=True)
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=20, default="indigo")
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return self.nombre


class Tema(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="temas")
    slug = models.SlugField()
    orden = models.PositiveSmallIntegerField()
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    recurso = models.CharField(max_length=200, blank=True)
    recurso_url = models.URLField(blank=True)
    sesiones = models.PositiveSmallIntegerField(
        default=3, help_text="Sesiones antes de la comprobación del 80 %."
    )
    preguntas = models.TextField(
        blank=True, help_text="Preguntas de autoevaluación, una por línea."
    )
    BASICO, AVANZADO, EXPERTO = 1, 2, 3
    NIVELES = [
        (BASICO, "Nivel 1 · Fundamentos"),
        (AVANZADO, "Nivel 2 · Avanzado"),
        (EXPERTO, "Nivel 3 · Experto"),
    ]
    nivel = models.PositiveSmallIntegerField(choices=NIVELES, default=BASICO)

    class Meta:
        ordering = ["materia__orden", "orden"]
        unique_together = [("materia", "slug")]

    def __str__(self):
        return f"{self.materia.nombre}: {self.titulo}"

    def lista_preguntas(self):
        return [p for p in self.preguntas.splitlines() if p.strip()]


class Etapa(models.Model):
    """Bloque de dos meses del plan anual: una materia principal y una complementaria."""

    orden = models.PositiveSmallIntegerField(unique=True)
    nombre = models.CharField(max_length=60)
    principal = models.ForeignKey(Materia, on_delete=models.PROTECT, related_name="+")
    complementaria = models.ForeignKey(Materia, on_delete=models.PROTECT, related_name="+")
    meses = models.PositiveSmallIntegerField(default=2)
    sustituta = models.ForeignKey(
        Materia, null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        help_text="Materia que reemplaza temporalmente un día hasta completarse.",
    )
    DIAS_SEMANA = [
        (0, "lunes"), (1, "martes"), (2, "miércoles"), (3, "jueves"),
        (4, "viernes"), (5, "sábados"), (6, "domingos"),
    ]
    dia_sustituto = models.PositiveSmallIntegerField(null=True, blank=True, choices=DIAS_SEMANA)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    ANIOS = [(1, "Año 1"), (2, "Año 2"), (3, "Año 3")]

    orden = models.PositiveSmallIntegerField()
    titulo = models.CharField(max_length=150, unique=True)
    autor = models.CharField(max_length=120)
    para_que = models.CharField(max_length=250)
    materia = models.ForeignKey(
        Materia, null=True, blank=True, on_delete=models.SET_NULL, related_name="libros"
    )
    anio = models.PositiveSmallIntegerField("Año del plan", choices=ANIOS, default=1)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return self.titulo


# --- Datos de cada usuario ----------------------------------------------------


class Perfil(models.Model):
    DURACIONES = [(20, "20 minutos"), (30, "30 minutos"), (45, "45 minutos")]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil"
    )
    fecha_inicio = models.DateField(default=timezone.localdate)
    minutos_sesion = models.PositiveSmallIntegerField(choices=DURACIONES, default=30)
    zona_horaria = models.CharField(max_length=50, default=settings.TIME_ZONE)
    ingles = models.BooleanField("Incluir práctica breve de inglés", default=True)
    CLARO, OSCURO = "claro", "oscuro"
    APARIENCIAS = [(CLARO, "Claro"), (OSCURO, "Oscuro")]
    apariencia = models.CharField(max_length=10, choices=APARIENCIAS, default=CLARO)
    libro_actual = models.ForeignKey(
        "Libro", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
        help_text="Libro elegido para la lectura diaria. Vacío = el siguiente de la lista.",
    )
    etapa_manual = models.ForeignKey(
        Etapa,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Déjalo vacío para que la etapa avance sola cada dos meses.",
    )

    def __str__(self):
        return f"Perfil de {self.usuario}"

    def etapa_actual(self, hoy):
        if self.etapa_manual_id:
            return self.etapa_manual
        meses = (hoy.year - self.fecha_inicio.year) * 12 + hoy.month - self.fecha_inicio.month
        if hoy.day < self.fecha_inicio.day:
            meses -= 1
        acumulado = 0
        etapas = list(Etapa.objects.select_related("principal", "complementaria"))
        for etapa in etapas:
            acumulado += etapa.meses
            if meses < acumulado:
                return etapa
        return etapas[-1] if etapas else None


class ProgresoTema(models.Model):
    PENDIENTE, EN_CURSO, DOMINADO = "pendiente", "en_curso", "dominado"
    ESTADOS = [(PENDIENTE, "Pendiente"), (EN_CURSO, "En curso"), (DOMINADO, "Dominado")]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=ESTADOS, default=PENDIENTE)
    sesiones_hechas = models.PositiveSmallIntegerField(default=0)
    sesiones_extra = models.PositiveSmallIntegerField(default=0)
    iniciado = models.DateField(null=True, blank=True)
    dominado = models.DateField(null=True, blank=True)

    # Cuaderno: los cuatro apartados recomendados.
    concepto = models.TextField("Concepto aprendido", blank=True)
    explicacion = models.TextField("Explicación con mis palabras", blank=True)
    errores = models.TextField("Errores cometidos", blank=True)
    preguntas = models.TextField("Preguntas pendientes", blank=True)

    class Meta:
        unique_together = [("usuario", "tema")]

    def tiene_notas(self):
        return any([self.concepto, self.explicacion, self.errores, self.preguntas])


class DiaPlan(models.Model):
    """Marca que el checklist de un día ya se generó, para no duplicar tareas."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateField()

    class Meta:
        unique_together = [("usuario", "fecha")]


class Tarea(models.Model):
    """Una línea del checklist diario. Si no se marca, se descarta al día siguiente."""

    ESTUDIO, LECTURA, REPASO_SEMANAL, INGLES = "estudio", "lectura", "repaso_semanal", "ingles"
    TIPOS = [
        (ESTUDIO, "Sesión de estudio"),
        (LECTURA, "Lectura"),
        (REPASO_SEMANAL, "Repaso semanal"),
        (INGLES, "Inglés"),
    ]

    # Paso de cada sesión de un tema (sesión 1, 2, 3 y comprobación del 80 %).
    PASOS = [
        "Comprender: estudia la explicación del concepto",
        "Practicar: resuelve 10 ejercicios y corrige tus errores",
        "Aplicar: resuelve problemas escritos o casos reales",
    ]
    PASO_COMPROBAR = "Comprobar: ¿resuelves el 80 % de los ejercicios básicos sin mirar?"
    PASO_EXTRA = "Práctica extra: repite los ejercicios que fallaste"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateField(help_text="Día del checklist al que pertenece.")
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    detalle = models.CharField(max_length=250, blank=True)
    tema = models.ForeignKey(Tema, null=True, blank=True, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, null=True, blank=True, on_delete=models.SET_NULL)
    numero_sesion = models.PositiveSmallIntegerField(null=True, blank=True)
    es_comprobacion = models.BooleanField(default=False)
    opcional = models.BooleanField(default=False)
    hecha = models.BooleanField(default=False)
    hecha_el = models.DateField(null=True, blank=True)
    minutos = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["fecha", "id"]

    def __str__(self):
        return self.titulo


class Repaso(models.Model):
    """Repaso espaciado de un tema. Al completarlo se programa el siguiente."""

    # Días de espera tras cada repaso: aprender lunes → martes → jueves → lunes siguiente…
    INTERVALOS = [1, 2, 4, 7, 15, 30, 60]
    NOMBRES = ["Repasar", "Recordar", "Comprobar"]

    OLVIDE, ME_COSTO, FACIL = "olvide", "costo", "facil"
    RESULTADOS = [(OLVIDE, "Lo olvidé"), (ME_COSTO, "Me costó"), (FACIL, "Fácil")]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name="repasos")
    fecha = models.DateField()
    nivel = models.PositiveSmallIntegerField(default=0, help_text="Índice en INTERVALOS.")
    hecho_el = models.DateField(null=True, blank=True)
    resultado = models.CharField(max_length=10, choices=RESULTADOS, blank=True)

    class Meta:
        ordering = ["fecha", "id"]

    @property
    def nombre_paso(self):
        return self.NOMBRES[self.nivel] if self.nivel < len(self.NOMBRES) else "Mantener"

    def completar(self, resultado, hoy):
        """Marca este repaso y crea el siguiente según qué tan bien se recordó.

        Olvidado vuelve al principio, con esfuerzo repite el intervalo y fácil avanza.
        """
        self.resultado = resultado
        self.hecho_el = hoy
        self.save()
        ultimo = len(self.INTERVALOS) - 1
        if resultado == self.OLVIDE:
            nivel = 0
        elif resultado == self.ME_COSTO:
            nivel = self.nivel
        else:
            nivel = min(self.nivel + 1, ultimo)
        return Repaso.objects.create(
            usuario=self.usuario,
            tema=self.tema,
            nivel=nivel,
            fecha=hoy + timedelta(days=self.INTERVALOS[nivel]),
        )


class LecturaLibro(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    sesiones = models.PositiveIntegerField(default=0)
    terminado = models.DateField(null=True, blank=True)
    tengo = models.BooleanField("Lo tengo", default=False)

    class Meta:
        unique_together = [("usuario", "libro")]
