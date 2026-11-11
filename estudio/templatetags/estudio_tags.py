from django import template

from estudio.colores import COLORES

register = template.Library()


@register.filter
def color(materia, parte="chip"):
    """Clases de Tailwind del color de una materia: {{ materia|color:"punto" }}."""
    nombre = getattr(materia, "color", materia) or "indigo"
    return COLORES.get(nombre, COLORES["indigo"])[parte]


@register.filter
def porcentaje(parte, total):
    return round(100 * parte / total) if total else 0
