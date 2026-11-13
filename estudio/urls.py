from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EntrarForm

urlpatterns = [
    path("", views.hoy, name="hoy"),
    path("tarea/<int:pk>/completar/", views.completar, name="completar"),
    path("tarea/<int:pk>/deshacer/", views.deshacer, name="deshacer"),
    path("tarea/<int:pk>/sesion/", views.sesion, name="sesion"),
    path("repaso/<int:pk>/", views.completar_repaso, name="completar_repaso"),
    path("vocabulario/<int:pk>/", views.marcar_vocabulario, name="vocabulario"),
    path("materia/<slug:slug>/otra-sesion/", views.estudiar_otra, name="estudiar_otra"),
    path("temario/", views.temario, name="temario"),
    path("temario/<slug:materia>/<slug:slug>/", views.tema, name="tema"),
    path("calendario/", views.calendario, name="calendario"),
    path("progreso/", views.progreso, name="progreso"),
    path("libros/", views.libros, name="libros"),
    path("libro/<int:pk>/elegir/", views.elegir_libro, name="elegir_libro"),
    path("libro/<int:pk>/tengo/", views.libro_tengo, name="libro_tengo"),
    path("libro/<int:pk>/terminado/", views.libro_terminado, name="libro_terminado"),
    path("tarjetas/", views.lista_mazos, name="tarjetas"),
    path("tarjetas/repasar/", views.repasar, name="repasar_tarjetas"),
    path("tarjetas/tarjeta/<int:pk>/", views.tarjeta, name="tarjeta"),
    path("tarjetas/<int:pk>/", views.mazo, name="mazo"),
    path("tarjetas/<int:pk>/repasar/", views.repasar, name="repasar_mazo"),
    path("guia/", views.guia, name="guia"),
    path("guia/<slug:slug>/", views.guia_detalle, name="guia_detalle"),
    path("ajustes/", views.ajustes, name="ajustes"),
    path("ajustes/apariencia/", views.cambiar_apariencia, name="cambiar_apariencia"),
    path("ajustes/booktracker/", views.booktracker_conectar, name="booktracker_conectar"),
    path("ajustes/booktracker/desconectar/", views.booktracker_desconectar, name="booktracker_desconectar"),
    path("cuenta/registro/", views.registro, name="registro"),
    path("cuenta/entrar/", auth_views.LoginView.as_view(authentication_form=EntrarForm), name="login"),
    path("cuenta/salir/", auth_views.LogoutView.as_view(), name="logout"),
]
