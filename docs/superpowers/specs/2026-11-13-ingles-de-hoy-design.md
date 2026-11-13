# Inglés de hoy: vocabulario diario en la página Hoy

## Intención

Ampliar vocabulario de inglés poco a poco: cada día, al abrir **Hoy**, ver unas
pocas palabras, verbos y phrasal verbs nuevos de uso cotidiano, y poder marcarlos.

## Objetivos

- Tarjeta "Inglés de hoy" en la página Hoy con 3 palabras, 2 verbos y 1 phrasal
  verb nuevos al día, cada uno con traducción al español y una frase de ejemplo.
- Lista propia ordenada de más a menos frecuente (unas 300 palabras, 150 verbos,
  100 phrasal verbs).
- Cada entrada se puede marcar: **Ya me la sé** (no vuelve a salir) o **Repasar**
  (vuelve a salir tras 1, 3, 7, 14 y 30 días, hasta que se marque como sabida).
- Se puede deshacer una marca hecha hoy.
- Las entradas pendientes del día se añaden al prompt de ChatGPT de la sesión de
  inglés para que el tutor haga usarlas.
- La tarjeta muestra cuántas se saben del total.

## Fuera de alcance

- Audio o pronunciación.
- Una página aparte con toda la lista o con las palabras ya sabidas.
- Que el vocabulario cuente para la racha o para "X de Y tachadas".

## Lo que sería un fallo

- Que el usuario pase semanas viendo solo palabras que ya conoce.
- Que las entradas sin marcar se amontonen sin límite.
- Que aparezca a quien desactivó inglés en Ajustes.

## Restricciones

- La lista vive en código, como `temario.py`; en base de datos solo se guarda el
  progreso de cada usuario por entrada.
- Sigue el estilo visual de las tarjetas existentes de `hoy.html`.

## Enfoques

1. **Lista en código + una fila de progreso por usuario y entrada (elegido).**
   La lista no se carga en base de datos; un modelo `Vocabulario` guarda, por
   usuario y clave de entrada, cuándo se presentó, cuándo vuelve a tocar y si ya
   se sabe. Una migración, sin comando de carga.
2. **Lista en código y selección solo por fecha, sin guardar nada.** Más simple,
   pero no permite marcar: descartado al pedirse el marcado.
3. **Entradas y progreso en base de datos**, cargadas con `cargar_plan`. Añade un
   modelo y un paso de carga sin ganar nada: nadie edita la lista desde el admin.

## Decisiones

- Aparece todos los días (también fin de semana) si `perfil.ingles` está activo.
- Cupo diario de nuevas por aprender: 3 palabras, 2 verbos, 1 phrasal. Una nueva marcada
  "Ya me la sé" no gasta cupo y se cambia por otra (el usuario es A2 y ya conoce muchas);
  "Repasar" sí lo gasta y no trae más.
- La traducción va oculta tras "Ver traducción": primero se intenta entender por el ejemplo.
- Lo que no se marca sigue pendiente al día siguiente. Con 12 o más pendientes no
  se reparten nuevas ese día, y la tarjeta muestra como mucho 12.
- "Repasar" avanza por los intervalos 1, 3, 7, 14, 30 días y se queda en 30.
- La tarjeta va en Hoy después de "Por hacer".

## A criterio de quien lo construya

- El contenido exacto de las listas y sus frases de ejemplo.
- Nombres de funciones y detalle del marcado HTML.
