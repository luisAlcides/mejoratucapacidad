import zoneinfo

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone

from .models import Mazo, Perfil, ProgresoTema, Tarjeta

ZONAS = [
    "America/Mexico_City", "America/Bogota", "America/Lima", "America/Guayaquil",
    "America/Caracas", "America/Santiago", "America/Argentina/Buenos_Aires",
    "America/Montevideo", "America/Asuncion", "America/La_Paz", "America/Managua",
    "America/Tegucigalpa", "America/El_Salvador", "America/Guatemala", "America/Costa_Rica",
    "America/Panama", "America/Santo_Domingo", "America/Havana", "America/Puerto_Rico",
    "America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/Madrid", "UTC",
]
OPCIONES_ZONA = [(z, z.split("/")[-1].replace("_", " ")) for z in ZONAS]

ENTRADA = (
    "w-full rounded-lg border border-borde bg-superficie px-3 py-2 text-texto "
    "focus:border-acento focus:outline-none focus:ring-2 focus:ring-acento/30"
)


class EstiloMixin:
    def aplicar_estilo(self):
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs["class"] = "h-5 w-5 rounded accent-acento"
            else:
                campo.widget.attrs["class"] = ENTRADA


class EntrarForm(EstiloMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nombre de usuario"
        self.aplicar_estilo()


class RegistroForm(EstiloMixin, UserCreationForm):
    zona_horaria = forms.ChoiceField(
        label="Tu zona horaria", choices=OPCIONES_ZONA, initial="America/Mexico_City"
    )

    class Meta(UserCreationForm.Meta):
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nombre de usuario"
        self.fields["username"].help_text = ""
        self.aplicar_estilo()

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            zona = self.cleaned_data["zona_horaria"]
            Perfil.objects.create(
                usuario=usuario,
                zona_horaria=zona,
                fecha_inicio=timezone.localtime(timezone=zoneinfo.ZoneInfo(zona)).date(),
            )
        return usuario


class PerfilForm(EstiloMixin, forms.ModelForm):
    zona_horaria = forms.ChoiceField(label="Zona horaria", choices=OPCIONES_ZONA)

    class Meta:
        model = Perfil
        fields = ["fecha_inicio", "minutos_sesion", "minutos_lectura", "zona_horaria", "apariencia", "ingles", "minutos_ingles", "etapa_manual"]
        labels = {
            "fecha_inicio": "Fecha en que empezaste el plan",
            "minutos_sesion": "Duración de cada sesión",
            "etapa_manual": "Fijar etapa",
        }
        widgets = {"fecha_inicio": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["etapa_manual"].empty_label = "Automática (avanza cada dos meses)"
        self.fields["minutos_lectura"].choices = [("", "Automática (según la sesión)")] + Perfil.LECTURAS
        self.aplicar_estilo()


class BookTrackerForm(EstiloMixin, forms.Form):
    usuario = forms.CharField(label="Usuario de BookTracker", max_length=150)
    contrasena = forms.CharField(
        label="Contraseña", widget=forms.PasswordInput,
        help_text="Solo se usa para obtener el token; no se guarda.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilo()


class CuadernoForm(EstiloMixin, forms.ModelForm):
    class Meta:
        model = ProgresoTema
        fields = ["concepto", "explicacion", "errores", "preguntas"]
        widgets = {f: forms.Textarea(attrs={"rows": 3}) for f in fields}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["concepto"].widget.attrs["placeholder"] = "¿Qué aprendí hoy, en una frase?"
        self.fields["explicacion"].widget.attrs["placeholder"] = (
            "Sin mirar el material: explícalo como si se lo contaras a alguien."
        )
        self.fields["errores"].widget.attrs["placeholder"] = "¿En qué me equivoqué y por qué?"
        self.fields["preguntas"].widget.attrs["placeholder"] = "Lo que todavía no entiendo."
        self.aplicar_estilo()


class MazoForm(EstiloMixin, forms.ModelForm):
    class Meta:
        model = Mazo
        fields = ["nombre"]
        labels = {"nombre": "Nombre del mazo"}

    def __init__(self, *args, usuario, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        self.fields["nombre"].widget.attrs["placeholder"] = "Por ejemplo: Anatomía"
        self.aplicar_estilo()

    def clean_nombre(self):
        nombre = " ".join(self.cleaned_data["nombre"].split())
        repetido = Mazo.objects.filter(usuario=self.usuario, nombre__iexact=nombre)
        if repetido.exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya tienes un mazo con ese nombre.")
        return nombre


class TarjetaForm(EstiloMixin, forms.ModelForm):
    class Meta:
        model = Tarjeta
        fields = ["frente", "reverso"]
        widgets = {f: forms.Textarea(attrs={"rows": 2}) for f in fields}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilo()
