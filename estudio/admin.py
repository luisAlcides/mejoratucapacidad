from django.contrib import admin

from .models import Etapa, Libro, Materia, Perfil, ProgresoTema, Repaso, Tarea, Tema, Vocabulario


class TemaInline(admin.TabularInline):
    model = Tema
    extra = 0
    fields = ["orden", "titulo", "slug", "sesiones"]


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "orden", "color"]
    inlines = [TemaInline]


@admin.register(Etapa)
class EtapaAdmin(admin.ModelAdmin):
    list_display = ["orden", "nombre", "principal", "complementaria", "sustituta"]


admin.site.register(Libro)
admin.site.register(Perfil)


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ["fecha", "usuario", "tipo", "titulo", "hecha", "hecha_el"]
    list_filter = ["tipo", "hecha"]


@admin.register(Repaso)
class RepasoAdmin(admin.ModelAdmin):
    list_display = ["fecha", "usuario", "tema", "nivel", "hecho_el", "resultado"]


@admin.register(ProgresoTema)
class ProgresoTemaAdmin(admin.ModelAdmin):
    list_display = ["usuario", "tema", "estado", "sesiones_hechas"]
    list_filter = ["estado"]


@admin.register(Vocabulario)
class VocabularioAdmin(admin.ModelAdmin):
    list_display = ["usuario", "clave", "presentada", "proxima", "nivel", "sabida"]
    list_filter = ["sabida"]
    search_fields = ["clave"]
