"""Cliente de solo lectura para la API de BookTracker (listalibros).

Solo se usa ``POST /api/auth/token/`` para obtener el token una vez y
``GET /api/books/`` para leer los libros. Nunca se escribe nada en BookTracker.
"""

import json
import unicodedata
import urllib.error
import urllib.request

from django.conf import settings
from django.core.cache import cache

TIMEOUT = 6
CACHE_SEGUNDOS = 300


class BookTrackerError(Exception):
    """BookTracker no respondió o respondió algo inesperado."""


class CredencialesInvalidas(BookTrackerError):
    pass


class TokenInvalido(BookTrackerError):
    pass


def base_url():
    return getattr(settings, "BOOKTRACKER_URL", "https://booktracker.up.railway.app").rstrip("/")


def _peticion(metodo, ruta, token=None, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(f"{base_url()}/api/{ruta}", data=datos, method=metodo)
    req.add_header("Accept", "application/json")
    if datos is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Token {token}")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 400 and ruta == "auth/token/":
            raise CredencialesInvalidas("Usuario o contraseña incorrectos.") from e
        if e.code in (401, 403):
            raise TokenInvalido("El token de BookTracker ya no es válido.") from e
        raise BookTrackerError(f"BookTracker respondió {e.code}.") from e
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise BookTrackerError("No se pudo conectar con BookTracker.") from e


def obtener_token(usuario, contrasena):
    datos = _peticion("POST", "auth/token/", cuerpo={"username": usuario, "password": contrasena})
    token = datos.get("token") if isinstance(datos, dict) else None
    if not token:
        raise BookTrackerError("BookTracker no devolvió un token.")
    return token


def _clave_cache(token):
    return f"booktracker:libros:{token[:12]}"


def libros(token):
    """Lista de libros del usuario en BookTracker (en caché unos minutos)."""
    clave = _clave_cache(token)
    datos = cache.get(clave)
    if datos is None:
        datos = _peticion("GET", "books/", token=token)
        if isinstance(datos, dict):  # por si algún día se activa la paginación
            datos = datos.get("results", [])
        for b in datos:
            b["portada"] = portada_segura(b.get("cover_url"))
        cache.set(clave, datos, CACHE_SEGUNDOS)
    return datos


def portada_segura(url):
    """Solo se aceptan portadas http(s); cualquier otra cosa se descarta."""
    url = (url or "").strip()
    return url if url.lower().startswith(("https://", "http://")) else ""


def olvidar(token):
    if token:
        cache.delete(_clave_cache(token))


def normalizar(texto):
    """Título comparable: sin acentos, mayúsculas ni signos."""
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c)).casefold()
    return " ".join("".join(c if c.isalnum() else " " for c in texto).split())


def por_titulo(lista):
    return {normalizar(b.get("title")): b for b in lista if b.get("title")}
