import zoneinfo

from django.utils import timezone


class ZonaHorariaMiddleware:
    """Activa la zona horaria del perfil para que «hoy» sea el día local del usuario."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        perfil = getattr(request.user, "perfil", None) if request.user.is_authenticated else None
        if perfil:
            try:
                timezone.activate(zoneinfo.ZoneInfo(perfil.zona_horaria))
            except (zoneinfo.ZoneInfoNotFoundError, ValueError):
                timezone.deactivate()
        else:
            timezone.deactivate()
        return self.get_response(request)
