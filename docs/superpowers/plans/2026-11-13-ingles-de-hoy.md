# Inglés de hoy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tarjeta diaria de vocabulario de inglés en Hoy, con marcado "Ya me la sé" / "Repasar".

**Architecture:** Las listas viven en código (`estudio/palabras.py`). Un modelo `Vocabulario` guarda el progreso por usuario y clave. `estudio/vocabulario.py` reparte las nuevas del día, decide qué toca y aplica las marcas; las vistas solo lo llaman.

**Tech Stack:** Django 5.2, plantillas con Tailwind v4 (CSS compilado en el repo).

**Spec:** `docs/superpowers/specs/2026-11-13-ingles-de-hoy-design.md`

## Global Constraints

- Nuevas al día: 3 palabras, 2 verbos, 1 phrasal verb.
- Intervalos de "Repasar": 1, 3, 7, 14, 30 días.
- Tope de pendientes: 12 (ni se muestran más ni se reparten nuevas a partir de ahí).
- Solo si `perfil.ingles` está activo.
- Pruebas: `python manage.py test estudio`.

## Review Focus

- Marcar una entrada no debe traer otra nueva el mismo día.
- Una fila cuya clave ya no existe en la lista se ignora, no rompe la página.
- Lista agotada: la tarjeta sigue funcionando solo con repasos.
- Un usuario no puede marcar entradas de otro (404).
- Claves duplicadas en las listas: una prueba lo impide.

---

### Task 1: Listas de vocabulario

**Files:** Create `estudio/palabras.py` · Test `estudio/tests.py`

**Interfaces:** Produces `PALABRAS`, `VERBOS`, `PHRASALS`: listas de tuplas `(ingles, espanol, ejemplo)`.

- [ ] Prueba `test_listas_sin_duplicados_y_completas`: sin repetidos dentro de cada lista, las tres partes no vacías, al menos 300 / 150 / 100 entradas.
- [ ] Escribir las listas, de más a menos frecuente.
- [ ] Pasar la prueba.

### Task 2: Modelo y lógica

**Files:** Modify `estudio/models.py`, `estudio/admin.py` · Create `estudio/vocabulario.py`, migración `0011` · Test `estudio/tests.py`

**Interfaces:**
- `Vocabulario(usuario, clave, presentada, proxima, nivel, sabida, respondida_el)`, único por `(usuario, clave)`. Clave: `"p:<ingles>"`, `"v:<ingles>"`, `"f:<ingles>"`.
- `vocabulario.del_dia(usuario, fecha) -> dict` con `pendientes`, `hechas` (filas con `.entrada` adjunta), `sabidas`, `total`.
- `vocabulario.responder(fila, sabe: bool, fecha)` y `vocabulario.deshacer(fila, fecha)`.
- `vocabulario.para_prompt(usuario, fecha) -> list[str]`.

- [ ] Pruebas: primer día reparte 3+2+1; llamar dos veces no duplica; marcar no trae nuevas; al día siguiente llegan 6 más y las sin marcar siguen; con 12 pendientes no se reparten nuevas; "Repasar" programa +1, luego +3; "Ya me la sé" no vuelve; deshacer la devuelve a pendientes; clave desconocida se ignora.
- [ ] Implementar modelo, migración y módulo.
- [ ] Pasar las pruebas.

### Task 3: Vistas, tarjeta y prompt

**Files:** Modify `estudio/views.py`, `estudio/urls.py`, `estudio/plan.py`, `templates/estudio/hoy.html`, `README.md`, `estudio/guias.py` · Test `estudio/tests.py`

**Interfaces:**
- `POST vocabulario/<pk>/` (`name="vocabulario"`), campo `accion` = `sabida` | `repasar` | `deshacer`; redirige a Hoy.
- `plan.prompt_chatgpt(tarea, minutos, progreso=None, vocabulario=None)`.

- [ ] Pruebas: Hoy muestra la tarjeta con inglés activo y no sin él; POST marca; POST sobre fila ajena da 404; el prompt de inglés incluye el vocabulario del día y el de otras materias no.
- [ ] Implementar y recompilar el CSS si hay clases nuevas.
- [ ] Suite completa en verde.
