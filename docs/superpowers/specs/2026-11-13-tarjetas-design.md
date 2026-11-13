# Tarjetas: mazos propios con repaso espaciado

## Intención

Tener un "Anki propio" dentro de la app: el usuario escribe sus propias tarjetas
(pregunta y respuesta) sobre cualquier tema, las agrupa en mazos, y la app se las
hace repasar con intervalos crecientes. Hoy la app solo repasa contenido fijo
(temas del temario y la lista de `palabras.py`); esto abre el repaso a contenido
del usuario.

## Objetivos

- Sección nueva **Tarjetas** con la lista de mazos del usuario: nombre, número de
  tarjetas y cuántas tocan hoy.
- Crear, renombrar y borrar mazos. Los mazos son libres, sin relación con `Materia`.
- Añadir tarjetas a un mazo de dos formas:
  - de una en una (pregunta y respuesta);
  - pegando varias, una por línea, con el formato `pregunta ; respuesta`.
- Editar y borrar tarjetas desde la página del mazo.
- Repasar un mazo o todos a la vez: se ve la pregunta, se descubre la respuesta y
  se marca **Lo olvidé / Me costó / Fácil**.
- Aviso en **Hoy** con las tarjetas que tocan y enlace al repaso.

## Fuera de alcance

- Imágenes, audio, formato enriquecido o LaTeX: las tarjetas son texto plano.
- Importar o exportar mazos de Anki (`.apkg`) o CSV.
- Tarjetas invertidas automáticas, huecos (cloze), etiquetas o submazos.
- Compartir mazos entre usuarios.
- Estadísticas de retención o gráficas.
- Deshacer una respuesta ya marcada.
- Que las tarjetas cuenten para la racha o para "X de Y tachadas" de Hoy.

## Lo que sería un fallo

- Que un usuario vea, repase o modifique tarjetas de otro.
- Que pegar 200 tarjetas de golpe obligue a repasar las 200 ese mismo día.
- Que una tarjeta olvidada desaparezca hasta mañana sin volver a preguntarse hoy.
- Que una línea mal escrita al pegar haga perder todo lo pegado.

## Restricciones

- Django con plantillas del servidor y Tailwind, como el resto; sin framework de
  JavaScript. El estilo sigue las tarjetas existentes de `hoy.html`.
- Las fechas usan `hoy_local()` (zona horaria del perfil), como el resto de vistas.
- Todo pertenece al usuario autenticado; toda consulta filtra por `usuario`.

## Enfoques

1. **Sección propia con mazos y tarjetas en base de datos (elegido por el
   usuario).** Modelos nuevos `Mazo` y `Tarjeta`, vistas y plantillas propias.
   Independiente del temario y del vocabulario: admite cualquier tema y no toca lo
   que ya funciona.
2. **Ampliar "Inglés de hoy" (`Vocabulario`) para aceptar entradas del usuario.**
   Menos trabajo, pero su forma (palabra, traducción, ejemplo, "Ya me la sé") no
   sirve para otros temas. Descartado.
3. **Colgar las tarjetas de los `Tema` del temario.** Se integra con el plan, pero
   solo permitiría tarjetas sobre temas ya existentes. Descartado.

## Decisiones

Lo que sigue lo decidió quien escribe el diseño, salvo lo marcado como del usuario.

### Datos

- `Mazo`: `usuario`, `nombre` (único por usuario), `creado`.
- `Tarjeta`: `mazo`, `frente`, `reverso` (texto), `nivel` (índice en los
  intervalos), `proxima` (fecha desde la que toca), `primer_repaso` (fecha, vacío
  mientras es nueva), `respondida` (fecha y hora de la última respuesta, vacío si
  ninguna), `creada`.
- Borrar un mazo borra sus tarjetas.
- Ambos modelos se registran en el admin.

### Repaso

- Botones **Lo olvidé / Me costó / Fácil** (del usuario: iguales a los repasos de
  temas).
- Intervalos en días: 1, 2, 4, 7, 15, 30, 60, 120. La última se repite.
  - **Fácil**: sube un nivel y vuelve tras el intervalo de ese nivel.
  - **Me costó**: mantiene el nivel y vuelve tras su intervalo.
  - **Lo olvidé**: vuelve al nivel 0 y **sigue tocando hoy**, al final de la cola,
    hasta que se marque de otra forma.
- Una tarjeta nueva responde así la primera vez: Fácil → 2 días, Me costó → 1 día,
  Lo olvidé → sigue hoy.
- Cola del día: primero las ya vistas que tocan (`proxima <= hoy`), de la más
  atrasada a la menos; después las nuevas, por orden de creación. Las olvidadas hoy
  van al final, por orden de respuesta.
- **Tope de nuevas: 20 al día entre todos los mazos.** Una tarjeta gasta cupo el
  día de su primera respuesta. Las nuevas que no caben esperan a mañana. Las ya
  vistas no tienen tope.
- La respuesta se oculta hasta pulsar "Ver respuesta"; los tres botones aparecen
  solo entonces.
- Se repasa de una en una: cada respuesta es un POST que redirige a la siguiente.
  Al acabar, un mensaje de "terminado por hoy" con cuántas se repasaron.
- "Repasar todo" mezcla los mazos en una sola cola y muestra el nombre del mazo en
  cada tarjeta.

### Añadir varias a la vez

- Una tarjeta por línea; se parte por el **primer** `;`. Se recortan espacios y se
  ignoran las líneas vacías.
- Las líneas válidas se guardan. Las que no tienen `;` o tienen un lado vacío no se
  guardan y se devuelven en el cuadro de texto con un aviso, para corregirlas.
- No se detectan duplicados.

### Navegación y Hoy

- Enlace **Tarjetas** en el menú superior de escritorio.
- En móvil la barra inferior ya tiene cinco entradas y no se toca: se llega por la
  tarjeta de Hoy.
- Hoy muestra siempre una tarjeta "Tarjetas" después de "Inglés de hoy": con el
  número que toca y el botón **Repasar** si hay alguna, o un enlace a la sección si
  no hay ninguna. Aparece también si el usuario aún no tiene mazos (invita a crear
  el primero).

### Rutas

- `tarjetas/`: lista de mazos y formulario para crear uno.
- `tarjetas/<mazo>/`: tarjetas del mazo, añadir una, añadir varias, renombrar y
  borrar el mazo.
- `tarjetas/<mazo>/tarjeta/<id>/`: editar o borrar una tarjeta.
- `tarjetas/repasar/` y `tarjetas/<mazo>/repasar/`: repaso de todo o de un mazo.
- Borrar un mazo o una tarjeta pide confirmación.
- Editar una tarjeta no cambia su progreso.

## Pruebas

En `estudio/tests.py`, con el estilo de las existentes:

- Los tres resultados programan la fecha y el nivel esperados; "Lo olvidé" deja la
  tarjeta en la cola de hoy y al final.
- El tope de 20 nuevas se respeta y se libera al día siguiente.
- Pegar varias guarda las válidas y devuelve las inválidas.
- Un usuario no puede ver, repasar, editar ni borrar mazos o tarjetas de otro (404).
- Hoy muestra el número correcto de tarjetas que tocan.
- Las páginas requieren iniciar sesión.

## A criterio de quien lo construya

- Nombres de funciones, módulos y plantillas (se sugiere un módulo `tarjetas.py`
  para la lógica, como `vocabulario.py`).
- Cómo se oculta y descubre la respuesta (`<details>` o un poco de JavaScript).
- Marcado HTML, textos exactos e iconos.
- Límites de longitud de los campos.
