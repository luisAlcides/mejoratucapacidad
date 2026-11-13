# Mejora tu capacidad

Plan de estudio diario: 30 minutos, una materia, un tema. Cada día tienes un
checklist para ir tachando la sesión de estudio, la lectura, los repasos y el inglés.

- **Hoy**: checklist del día. Lun/Mié/Vie materia principal, Mar/Jue complementaria,
  sábado repaso de la semana, domingo descanso.
- **Nada se acumula**: lo que no tachaste se quita al día siguiente, pero un tema solo
  avanza cuando lo estudias de verdad. Si faltas varios días, retomas donde quedaste.
- **Sesión guiada**: temporizador Repasar → Aprender → Practicar → Recordar y cuaderno
  (concepto, explicación propia, errores, preguntas).
- **Regla del 80 %**: tras las sesiones de un tema viene una comprobación; si no la
  superas, se añade práctica extra.
- **Repaso espaciado**: +1, +2, +4, +7, +15… días según cómo lo recordaste (máx. 3 al día).
- **Inglés de hoy**: cada día 3 palabras, 2 verbos y 1 phrasal verb con traducción y
  ejemplo (traducción oculta tras un toque). «Ya me la sé» la cambia por otra nueva;
  «Repasar otro día» la trae de vuelta tras 1, 3, 7, 14 y 30 días.
- **Temario** completo (14 materias, 437 temas en tres niveles, con preguntas de
  autoevaluación), inglés diario en paralelo, **calendario** de 14 días, plan de
  tres años y **progreso** (racha, mapa de 12 semanas, libros).

## Desarrollo local

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # en macOS/Linux: .venv/bin/pip
cp .env.example .env                            # y pon tu SECRET_KEY
python manage.py migrate
python manage.py cargar_plan
python manage.py runserver
```

Estilos (Tailwind v4): el CSS compilado `static/css/app.css` se guarda en el repo,
así Railway no necesita Node. Si cambias clases en las plantillas, recompila:

```bash
npm install
npm run css        # o npm run css:watch mientras desarrollas
```

Pruebas: `python manage.py test estudio`

El temario está en `estudio/temario.py`; tras editarlo ejecuta `cargar_plan`
(actualiza sin borrar el progreso).

El vocabulario diario de inglés está en `estudio/palabras.py` (no necesita carga).

## Desplegar en Railway

1. Sube el repo a GitHub (`.env` y `.env.railway` no se suben: están en `.gitignore`).
2. En Railway: **New Project → Deploy from GitHub repo** y elige este repositorio.
3. En el mismo proyecto: **+ New → Database → PostgreSQL**. Debe llamarse `Postgres`
   (si le pones otro nombre, cámbialo también en `DATABASE_URL`).
4. En el servicio web: **Variables → Raw Editor**, pega el contenido de `.env.railway`
   y guarda. Incluye `SECRET_KEY`, `DEBUG=False`,
   `DATABASE_URL=${{Postgres.DATABASE_URL}}` y `TIME_ZONE`.
5. **Settings → Networking → Generate Domain**. `ALLOWED_HOSTS` y
   `CSRF_TRUSTED_ORIGINS` se configuran solos con `RAILWAY_PUBLIC_DOMAIN`.
6. Abre el dominio, crea tu cuenta y, en **Libros**, marca «Lo tengo» en los tuyos.

`railway.json` ya define: `collectstatic` al construir, `preparar` (migraciones +
`cargar_plan`) antes de cada despliegue, `gunicorn` para arrancar y `/salud/` como healthcheck.

Para entrar al panel `/admin/`: `railway run python manage.py createsuperuser`
(con la CLI de Railway) o desde la consola del servicio.

Si no tienes `.env.railway`, crea uno a partir de `.env.example` con una
`SECRET_KEY` nueva y `DEBUG=False`.
