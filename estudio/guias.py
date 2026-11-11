"""Chuletas de consulta rápida (sección «Guía»).

Cada guía tiene secciones de cuatro tipos:
    lista   → items: [(término, explicación)] o [texto]
    tabla   → columnas: [...], filas: [[...], ...]
    pasos   → items: [texto] numerados
    codigo  → codigo: "texto monoespaciado"
"""

GUIAS = [
    {
        "slug": "como-estudiar",
        "titulo": "Cómo estudiar",
        "descripcion": "Las técnicas con más evidencia y cómo aplicarlas en 30 minutos.",
        "grupo": "estudio",
        "color": "indigo",
        "secciones": [
            {"titulo": "Tu sesión de 30 minutos", "tipo": "tabla",
             "columnas": ["Fase", "Minutos", "Qué hacer"],
             "filas": [
                 ["Repasar", "5", "Recuerda sin mirar lo de la sesión anterior."],
                 ["Aprender", "10", "Una explicación corta de un solo concepto nuevo."],
                 ["Practicar", "10", "Ejercicios o análisis sin ayuda. Corrige tus errores."],
                 ["Recordar", "5", "Cierra todo y explícalo con tus palabras en el cuaderno."],
             ]},
            {"titulo": "Lo que funciona", "tipo": "lista", "items": [
                ("Práctica de recuperación", "Recordar sin mirar fortalece la memoria más que releer. Hazte preguntas."),
                ("Repaso espaciado", "Repasa a intervalos crecientes: 1, 2, 4, 7, 15 días. La app lo hace por ti."),
                ("Práctica intercalada", "Mezcla tipos de ejercicios para aprender a elegir el método, no solo a aplicarlo."),
                ("Técnica Feynman", "Explícalo como a un niño de 12 años. Donde te trabes, ahí está el hueco."),
                ("Elaboración", "Pregúntate por qué y cómo se conecta con lo que ya sabes. Inventa un ejemplo propio."),
                ("Ejemplos resueltos", "Al empezar un tema, estudia un ejemplo resuelto antes de resolver tú."),
                ("Dormir", "El sueño consolida lo aprendido. Estudiar cansado rinde poco."),
            ]},
            {"titulo": "Lo que parece útil pero rinde poco", "tipo": "lista", "items": [
                ("Releer y subrayar", "Da sensación de dominio (ilusión de competencia) sin fijar el recuerdo."),
                ("Ver videos sin practicar", "Entender una explicación no es lo mismo que poder resolver."),
                ("Estudiar todo de golpe", "El atracón antes de un examen se olvida rápido."),
                ("Multitarea", "El teléfono cerca reduce tu concentración aunque no lo mires."),
            ]},
            {"titulo": "Regla del 80 %", "tipo": "pasos", "items": [
                "Resuelve 10 ejercicios básicos del tema sin mirar la solución.",
                "Si aciertas 8 o más, avanza al siguiente tema.",
                "Si no, analiza por qué te equivocaste y haz una sesión de práctica extra.",
                "Es mejor dominar cinco temas que haber visto veinte sin poder aplicarlos.",
            ]},
            {"titulo": "Si llegas cansado o te atascas", "tipo": "lista", "items": [
                "15 minutos bien aprovechados valen más que una hora sin concentración.",
                "Haz solo la fase Repasar y la de Recordar, y tacha la lectura.",
                "Atascado más de 10 minutos: aléjate, camina, y vuelve (modo difuso).",
                "Escribe en el cuaderno la pregunta exacta que no entiendes: ya es progreso.",
                "Si faltas días, no pasa nada: la app no acumula tareas y retomas donde quedaste.",
            ]},
        ],
    },
    {
        "slug": "como-usar",
        "titulo": "Cómo usar la app",
        "descripcion": "Qué significa cada botón y cómo avanza tu plan.",
        "grupo": "estudio",
        "color": "slate",
        "secciones": [
            {"titulo": "Tu día", "tipo": "lista", "items": [
                ("Lun, mié, vie", "Materia principal de la etapa."),
                ("Mar, jue", "Materia complementaria (en la etapa 1, los jueves son de Aprendiendo a aprender hasta terminarlo)."),
                ("Sábado", "Repaso y ejercicios de la semana."),
                ("Domingo", "Descanso: lectura por placer opcional."),
                ("Todos los días", "8–10 min de lectura; entre semana, 10 min de inglés opcional."),
            ]},
            {"titulo": "Cómo avanza un tema", "tipo": "pasos", "items": [
                "Sesión 1 · Comprender: estudias la explicación.",
                "Sesión 2 · Practicar: 10 ejercicios y corriges errores.",
                "Sesión 3 · Aplicar: problemas escritos o casos reales.",
                "Comprobación: «Sí, lo domino» pasa al siguiente tema; «Aún no» añade práctica extra.",
                "Si ya dominas un tema, en su página pulsa «Ya lo domino: saltar este tema».",
            ]},
            {"titulo": "Repasos", "tipo": "tabla",
             "columnas": ["Respuesta", "Qué pasa"],
             "filas": [
                 ["😕 Lo olvidé", "Vuelve a empezar: repaso mañana."],
                 ["🤔 Me costó", "Repite el mismo intervalo."],
                 ["😄 Fácil", "El siguiente repaso se aleja más."],
             ]},
            {"titulo": "Detalles útiles", "tipo": "lista", "items": [
                ("Nada se acumula", "Lo que no tachas se quita al día siguiente, pero el tema no avanza hasta que lo estudias."),
                ("+ Materia", "En «¿Con energía extra?» adelantas la siguiente sesión."),
                ("Deshacer", "Si tachaste algo por error, puedes deshacerlo en «Tachado hoy»."),
                ("Libros", "La lectura diaria es el primer libro sin terminar de la lista. «Leer este ahora» elige otro; «Lo tengo» marca los que tienes."),
                ("Ajustes", "Duración de la sesión (20, 30 o 45 min), zona horaria, inglés y modo oscuro."),
            ]},
        ],
    },
    {
        "slug": "sesgos",
        "titulo": "Sesgos y cómo evitarlos",
        "descripcion": "Los errores de pensamiento más comunes y su antídoto.",
        "grupo": "estudio",
        "color": "cyan",
        "materia": "psicologia",
        "secciones": [
            {"titulo": "Sesgos frecuentes", "tipo": "tabla",
             "columnas": ["Sesgo", "Qué es", "Antídoto"],
             "filas": [
                 ["Confirmación", "Buscar solo lo que confirma lo que ya crees.", "Busca activamente la mejor evidencia en contra."],
                 ["Anclaje", "El primer número que oyes condiciona tu estimación.", "Estima tú primero, antes de ver otras cifras."],
                 ["Disponibilidad", "Juzgar la frecuencia por lo fácil que viene a la mente.", "Busca los datos reales, no los casos llamativos."],
                 ["Exceso de confianza", "Creer que sabes más de lo que sabes.", "Ponle un porcentaje a tu certeza y compruébalo."],
                 ["Costo hundido", "Seguir con algo por lo que ya invertiste.", "Pregúntate: si empezara hoy, ¿lo elegiría?"],
                 ["Aversión a la pérdida", "Perder duele más que ganar lo mismo.", "Reformula la decisión en términos de ganancia."],
                 ["Efecto marco", "La forma de presentar algo cambia tu decisión.", "Presenta la opción de dos maneras y compara."],
                 ["Supervivencia", "Ver solo los casos que «sobrevivieron».", "Pregunta: ¿qué casos no estoy viendo?"],
                 ["Retrospectiva", "«Ya lo sabía» después de que ocurre.", "Anota tus predicciones antes de los resultados."],
                 ["Halo", "Una cualidad buena tiñe el juicio de todo lo demás.", "Evalúa cada aspecto por separado."],
                 ["Ilusión de competencia", "Confundir familiaridad con dominio.", "Ponte a prueba sin mirar."],
                 ["Planificación", "Subestimar cuánto tardarás.", "Mira cuánto tardaste en tareas parecidas."],
             ]},
        ],
    },
    {
        "slug": "logica",
        "titulo": "Lógica y pensamiento crítico",
        "descripcion": "Conectores, formas válidas, falacias y cómo evaluar una afirmación.",
        "grupo": "materia",
        "materia": "logica",
        "color": "violet",
        "secciones": [
            {"titulo": "Conectores", "tipo": "tabla",
             "columnas": ["Símbolo", "Se lee", "Es falso solo si…"],
             "filas": [
                 ["¬p", "no p", "p es verdadero"],
                 ["p ∧ q", "p y q", "alguno es falso"],
                 ["p ∨ q", "p o q", "ambos son falsos"],
                 ["p → q", "si p, entonces q", "p verdadero y q falso"],
                 ["p ↔ q", "p si y solo si q", "tienen distinto valor"],
             ]},
            {"titulo": "Equivalencias clave", "tipo": "lista", "items": [
                ("De Morgan", "¬(p ∧ q) ≡ ¬p ∨ ¬q   ·   ¬(p ∨ q) ≡ ¬p ∧ ¬q"),
                ("Contrarrecíproco", "p → q ≡ ¬q → ¬p (el recíproco q → p NO equivale)"),
                ("Condicional", "p → q ≡ ¬p ∨ q"),
                ("Negar «todos»", "¬(todos son A) ≡ algunos no son A"),
                ("Negar «algunos»", "¬(algunos son A) ≡ ninguno es A"),
                ("Necesaria / suficiente", "En p → q: p es suficiente para q; q es necesaria para p."),
            ]},
            {"titulo": "Formas de razonar", "tipo": "tabla",
             "columnas": ["Forma", "Esquema", "¿Válida?"],
             "filas": [
                 ["Modus ponens", "p → q; p ⊢ q", "Sí"],
                 ["Modus tollens", "p → q; ¬q ⊢ ¬p", "Sí"],
                 ["Silogismo hipotético", "p → q; q → r ⊢ p → r", "Sí"],
                 ["Silogismo disyuntivo", "p ∨ q; ¬p ⊢ q", "Sí"],
                 ["Afirmar el consecuente", "p → q; q ⊢ p", "No (falacia)"],
                 ["Negar el antecedente", "p → q; ¬p ⊢ ¬q", "No (falacia)"],
             ]},
            {"titulo": "Falacias más comunes", "tipo": "lista", "items": [
                ("Ad hominem", "Atacar a la persona en lugar del argumento."),
                ("Hombre de paja", "Refutar una versión deformada de lo que el otro dijo."),
                ("Falso dilema", "Presentar dos opciones cuando hay más."),
                ("Pendiente resbaladiza", "Suponer sin pruebas una cadena de consecuencias extremas."),
                ("Petición de principio", "La conclusión ya está escondida en las premisas."),
                ("Generalización apresurada", "Concluir sobre todos a partir de pocos casos."),
                ("Post hoc", "Ocurrió después, luego fue la causa."),
                ("Apelación a la autoridad", "Citar a alguien que no es experto en el tema, o como única prueba."),
                ("Apelación a la mayoría", "Es verdad porque mucha gente lo cree."),
                ("Apelación a la ignorancia", "Es verdad porque nadie ha demostrado lo contrario."),
                ("Apelación a la emoción", "Sustituir razones por miedo, lástima o indignación."),
                ("Tu quoque", "«Tú también lo haces» no refuta el argumento."),
            ]},
            {"titulo": "Evaluar una afirmación", "tipo": "pasos", "items": [
                "¿Qué se afirma exactamente? Reescríbelo en una frase clara.",
                "¿Cuál es la evidencia? ¿Es un dato, una anécdota o una opinión?",
                "¿Quién lo dice y qué gana con ello? Busca la fuente original.",
                "Lectura lateral: ¿qué dicen otras fuentes fiables sobre lo mismo?",
                "¿Hay otra explicación más simple? (navaja de Ockham)",
                "¿Qué evidencia te haría cambiar de opinión?",
            ]},
        ],
    },
    {
        "slug": "matematicas",
        "titulo": "Matemáticas",
        "descripcion": "Reglas y fórmulas que más vas a usar, del álgebra al cálculo.",
        "grupo": "materia",
        "materia": "matematicas",
        "color": "blue",
        "secciones": [
            {"titulo": "Orden de operaciones", "tipo": "pasos", "items": [
                "Paréntesis y corchetes.",
                "Potencias y raíces.",
                "Multiplicación y división, de izquierda a derecha.",
                "Suma y resta, de izquierda a derecha.",
            ]},
            {"titulo": "Fracciones y porcentajes", "tipo": "lista", "items": [
                ("Sumar", "a/b + c/d = (ad + bc) / bd"),
                ("Multiplicar", "a/b · c/d = ac / bd"),
                ("Dividir", "a/b ÷ c/d = a/b · d/c"),
                ("Porcentaje", "x % de N = N · x / 100"),
                ("Aumento de x %", "N · (1 + x/100)   ·   Descuento: N · (1 − x/100)"),
                ("Cambio porcentual", "(nuevo − viejo) / viejo · 100"),
            ]},
            {"titulo": "Potencias y raíces", "tipo": "lista", "items": [
                ("Producto", "aᵐ · aⁿ = aᵐ⁺ⁿ"),
                ("Cociente", "aᵐ / aⁿ = aᵐ⁻ⁿ"),
                ("Potencia de potencia", "(aᵐ)ⁿ = aᵐⁿ"),
                ("Exponente cero y negativo", "a⁰ = 1   ·   a⁻ⁿ = 1 / aⁿ"),
                ("Raíz como potencia", "ⁿ√a = a^(1/n)"),
            ]},
            {"titulo": "Álgebra", "tipo": "lista", "items": [
                ("Cuadrado de un binomio", "(a ± b)² = a² ± 2ab + b²"),
                ("Diferencia de cuadrados", "a² − b² = (a + b)(a − b)"),
                ("Ecuación lineal", "Agrupa términos con x en un lado, números en el otro, y divide."),
                ("Fórmula cuadrática", "ax² + bx + c = 0  →  x = (−b ± √(b² − 4ac)) / 2a"),
                ("Discriminante", "b² − 4ac > 0: dos soluciones · = 0: una · < 0: ninguna real"),
                ("Desigualdades", "Al multiplicar o dividir por un negativo, se invierte el signo."),
            ]},
            {"titulo": "Funciones y geometría", "tipo": "lista", "items": [
                ("Recta", "y = mx + b   ·   pendiente m = (y₂ − y₁) / (x₂ − x₁)"),
                ("Pitágoras", "c² = a² + b²"),
                ("Áreas", "Rectángulo b·h · Triángulo b·h/2 · Círculo πr²"),
                ("Volúmenes", "Prisma A_base·h · Cilindro πr²h · Esfera 4/3·πr³"),
                ("Trigonometría", "sen = opuesto/hipotenusa · cos = adyacente/hipotenusa · tan = opuesto/adyacente"),
                ("Logaritmo", "log_b(x) = y  ⇔  bʸ = x   ·   log(ab) = log a + log b"),
                ("Interés compuesto", "C · (1 + r)ⁿ"),
            ]},
            {"titulo": "Cálculo", "tipo": "tabla",
             "columnas": ["Función", "Derivada"],
             "filas": [
                 ["c (constante)", "0"],
                 ["xⁿ", "n·xⁿ⁻¹"],
                 ["eˣ", "eˣ"],
                 ["ln x", "1/x"],
                 ["sen x", "cos x"],
                 ["cos x", "−sen x"],
                 ["f(g(x))", "f′(g(x)) · g′(x)  (regla de la cadena)"],
                 ["f · g", "f′g + fg′"],
             ]},
        ],
    },
    {
        "slug": "estadistica",
        "titulo": "Estadística y probabilidad",
        "descripcion": "Medidas, probabilidad, distribuciones e inferencia de un vistazo.",
        "grupo": "materia",
        "materia": "estadistica",
        "color": "emerald",
        "secciones": [
            {"titulo": "Medidas", "tipo": "lista", "items": [
                ("Media", "x̄ = Σx / n. Sensible a valores extremos."),
                ("Mediana", "El valor del medio al ordenar. Robusta ante extremos."),
                ("Moda", "El valor más frecuente."),
                ("Varianza", "s² = Σ(x − x̄)² / (n − 1)"),
                ("Desviación estándar", "s = √s². Dispersión típica respecto a la media."),
                ("Puntuación z", "z = (x − media) / desviación. Cuántas desviaciones se aleja un dato."),
            ]},
            {"titulo": "Probabilidad", "tipo": "lista", "items": [
                ("Básica", "P(A) = casos favorables / casos posibles"),
                ("Complemento", "P(no A) = 1 − P(A)"),
                ("Suma", "P(A o B) = P(A) + P(B) − P(A y B)"),
                ("Independientes", "P(A y B) = P(A) · P(B)"),
                ("Condicional", "P(A | B) = P(A y B) / P(B)"),
                ("Bayes", "P(A | B) = P(B | A) · P(A) / P(B)"),
                ("Valor esperado", "E[X] = Σ x · P(x)"),
            ]},
            {"titulo": "Conteo", "tipo": "tabla",
             "columnas": ["¿Importa el orden?", "Fórmula", "Ejemplo"],
             "filas": [
                 ["Sí (permutaciones)", "n! / (n − k)!", "Podio de 3 entre 10: 720"],
                 ["No (combinaciones)", "n! / (k!(n − k)!)", "Comité de 3 entre 10: 120"],
             ]},
            {"titulo": "Distribución normal", "tipo": "lista", "items": [
                ("Regla 68-95-99,7", "≈68 % a ±1 desviación, ≈95 % a ±2, ≈99,7 % a ±3."),
                ("Teorema central del límite", "La media de muchas muestras se distribuye casi normal."),
            ]},
            {"titulo": "Leer resultados sin equivocarte", "tipo": "lista", "items": [
                ("Valor p", "Probabilidad de datos así de extremos si la hipótesis nula fuera cierta. NO es la probabilidad de que la hipótesis sea cierta."),
                ("Significativo ≠ importante", "Un efecto puede ser real pero diminuto. Mira el tamaño del efecto."),
                ("Intervalo de confianza", "Rango plausible del valor real; más datos lo hacen más estrecho."),
                ("Correlación ≠ causalidad", "Pregunta: ¿causa común?, ¿causalidad inversa?, ¿azar?"),
                ("Riesgo relativo vs. absoluto", "«Duplica el riesgo» puede ser pasar de 1 a 2 en 10 000."),
                ("Muestra", "¿Es representativa? ¿Cuántos casos? ¿Quién quedó fuera?"),
            ]},
        ],
    },
    {
        "slug": "fisica",
        "titulo": "Física",
        "descripcion": "Fórmulas esenciales de mecánica, energía y electricidad.",
        "grupo": "materia",
        "materia": "fisica",
        "color": "sky",
        "secciones": [
            {"titulo": "Movimiento", "tipo": "lista", "items": [
                ("Velocidad media", "v = Δx / Δt"),
                ("Aceleración", "a = Δv / Δt"),
                ("Con aceleración constante", "v = v₀ + at   ·   x = x₀ + v₀t + ½at²   ·   v² = v₀² + 2aΔx"),
                ("Caída libre", "g ≈ 9,8 m/s² hacia abajo"),
                ("Circular", "a_c = v² / r"),
            ]},
            {"titulo": "Fuerza y energía", "tipo": "lista", "items": [
                ("Segunda ley de Newton", "F = m · a"),
                ("Peso", "P = m · g"),
                ("Fricción", "f = μ · N"),
                ("Trabajo", "W = F · d · cos θ"),
                ("Energía cinética", "Ec = ½ m v²"),
                ("Energía potencial", "Ep = m g h"),
                ("Momento", "p = m · v (se conserva en choques)"),
                ("Potencia", "P = W / t"),
            ]},
            {"titulo": "Electricidad, ondas y más", "tipo": "lista", "items": [
                ("Ley de Ohm", "V = I · R"),
                ("Potencia eléctrica", "P = V · I"),
                ("Resistencias en serie", "R = R₁ + R₂ + …"),
                ("En paralelo", "1/R = 1/R₁ + 1/R₂ + …"),
                ("Ondas", "v = λ · f"),
                ("Energía y masa", "E = m c²"),
            ]},
            {"titulo": "Resolver un problema", "tipo": "pasos", "items": [
                "Dibuja la situación y anota los datos con sus unidades.",
                "Escribe qué te piden.",
                "Elige la ley o fórmula que relaciona datos e incógnita.",
                "Despeja en símbolos antes de poner números.",
                "Comprueba unidades y si el resultado tiene sentido.",
            ]},
        ],
    },
    {
        "slug": "python",
        "titulo": "Python y pandas",
        "descripcion": "Sintaxis básica de Python y las operaciones de pandas que más se usan.",
        "grupo": "materia",
        "materia": "programacion",
        "color": "slate",
        "secciones": [
            {"titulo": "Lo básico", "tipo": "codigo", "codigo": """nombre = "Luis"            # str
edad = 30                  # int
precio = 9.99              # float
activo = True              # bool

print(f"Hola, {nombre}. Tienes {edad} años.")
int("5") + 3               # 8 (convertir antes de operar)
7 // 2, 7 % 2              # (3, 1): división entera y resto"""},
            {"titulo": "Control de flujo", "tipo": "codigo", "codigo": """if edad >= 18:
    print("mayor")
elif edad >= 13:
    print("adolescente")
else:
    print("niño")

for i in range(5):         # 0, 1, 2, 3, 4
    print(i)

while n > 0:
    n -= 1"""},
            {"titulo": "Colecciones", "tipo": "codigo", "codigo": """lista = [3, 1, 2]
lista.append(4); lista.sort(); lista[0]; lista[-1]; lista[1:3]

dic = {"nombre": "Ana", "edad": 25}
dic["edad"]; dic.get("ciudad", "—"); dic.items()

unicos = set([1, 1, 2])               # {1, 2}
cuadrados = [x**2 for x in range(10) if x % 2 == 0]"""},
            {"titulo": "Funciones, archivos y errores", "tipo": "codigo", "codigo": """def promedio(numeros):
    \"\"\"Devuelve la media de una lista.\"\"\"
    return sum(numeros) / len(numeros)

with open("datos.txt", encoding="utf-8") as f:
    lineas = f.readlines()

try:
    n = int(input("Número: "))
except ValueError:
    print("Eso no es un número")"""},
            {"titulo": "pandas", "tipo": "codigo", "codigo": """import pandas as pd

df = pd.read_csv("datos.csv")
df.head(); df.info(); df.describe()
df["columna"]                          # una columna
df[df["edad"] > 30]                    # filtrar filas
df.sort_values("ventas", ascending=False)
df.groupby("ciudad")["ventas"].sum()   # agrupar
df.isna().sum(); df.dropna(); df.fillna(0)
df.merge(otro, on="id", how="left")    # unir tablas
df.to_csv("salida.csv", index=False)"""},
            {"titulo": "Cuando algo falla", "tipo": "pasos", "items": [
                "Lee el error de abajo hacia arriba: la última línea dice qué pasó.",
                "Busca la línea de TU código en el traceback.",
                "Imprime las variables justo antes del error.",
                "Reduce el problema al mínimo código que lo reproduce.",
                "Busca el mensaje exacto del error en internet.",
            ]},
        ],
    },
    {
        "slug": "datos-ml",
        "titulo": "Ciencia de datos y machine learning",
        "descripcion": "El flujo de un proyecto, métricas y scikit-learn en una página.",
        "grupo": "materia",
        "materia": "ciencia-datos",
        "materias": ["ciencia-datos", "machine-learning"],
        "color": "indigo",
        "secciones": [
            {"titulo": "Flujo de un proyecto", "tipo": "pasos", "items": [
                "Pregunta: ¿qué decisión se tomará con el resultado?",
                "Datos: obtener, entender cada columna, revisar calidad.",
                "Limpieza: tipos, faltantes, duplicados, valores atípicos.",
                "Exploración: distribuciones, relaciones, primeras hipótesis.",
                "Modelo o análisis: empieza por lo más simple que pueda funcionar.",
                "Evaluación: con datos que el modelo no vio.",
                "Comunicación: hallazgo, evidencia, recomendación y limitaciones.",
            ]},
            {"titulo": "Métricas", "tipo": "tabla",
             "columnas": ["Métrica", "Fórmula", "Úsala cuando…"],
             "filas": [
                 ["Exactitud", "aciertos / total", "Las clases están equilibradas."],
                 ["Precisión", "VP / (VP + FP)", "Un falso positivo es caro (spam)."],
                 ["Recall", "VP / (VP + FN)", "Un falso negativo es caro (fraude, enfermedad)."],
                 ["F1", "2·P·R / (P + R)", "Quieres equilibrar precisión y recall."],
                 ["MAE", "media de |real − predicho|", "Error fácil de interpretar en unidades."],
                 ["RMSE", "√ media de (real − predicho)²", "Los errores grandes importan más."],
             ]},
            {"titulo": "Señales de alerta", "tipo": "lista", "items": [
                ("Sobreajuste", "Muy bien en entrenamiento, mal en prueba. Simplifica o regulariza."),
                ("Fuga de datos", "Usar información que no tendrías al predecir. Resultados «demasiado buenos»."),
                ("Clases desbalanceadas", "Un 99 % de exactitud puede ser inútil. Mira precisión y recall."),
                ("Sesgo en los datos", "El modelo aprende las injusticias del pasado."),
            ]},
            {"titulo": "scikit-learn mínimo", "tipo": "codigo", "codigo": """from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

modelo = RandomForestClassifier(random_state=42)
modelo.fit(X_train, y_train)
print(classification_report(y_test, modelo.predict(X_test)))"""},
        ],
    },
    {
        "slug": "ingles",
        "titulo": "Inglés",
        "descripcion": "Tiempos verbales, verbos irregulares y frases útiles.",
        "grupo": "materia",
        "materia": "ingles",
        "color": "rose",
        "secciones": [
            {"titulo": "Tiempos verbales", "tipo": "tabla",
             "columnas": ["Tiempo", "Uso", "Ejemplo"],
             "filas": [
                 ["Present simple", "Hábitos y hechos", "She works every day."],
                 ["Present continuous", "Ahora mismo", "I am studying now."],
                 ["Past simple", "Pasado terminado", "I visited Lima in 2020."],
                 ["Past continuous", "Acción en curso en el pasado", "I was reading when you called."],
                 ["Present perfect", "Experiencia o pasado conectado al presente", "I have finished the book."],
                 ["Future: will", "Decisión espontánea o predicción", "I will help you."],
                 ["Future: going to", "Plan ya decidido", "I am going to study tonight."],
             ]},
            {"titulo": "Condicionales", "tipo": "tabla",
             "columnas": ["Tipo", "Estructura", "Ejemplo"],
             "filas": [
                 ["0", "If + presente, presente", "If you heat ice, it melts."],
                 ["1", "If + presente, will + verbo", "If I study, I will pass."],
                 ["2", "If + pasado, would + verbo", "If I had time, I would travel."],
                 ["3", "If + had + participio, would have + participio", "If I had known, I would have come."],
             ]},
            {"titulo": "Verbos irregulares frecuentes", "tipo": "tabla",
             "columnas": ["Verbo", "Pasado", "Participio", "Significado"],
             "filas": [
                 ["be", "was/were", "been", "ser/estar"],
                 ["have", "had", "had", "tener"],
                 ["do", "did", "done", "hacer"],
                 ["go", "went", "gone", "ir"],
                 ["get", "got", "got/gotten", "obtener"],
                 ["make", "made", "made", "hacer/fabricar"],
                 ["take", "took", "taken", "tomar"],
                 ["see", "saw", "seen", "ver"],
                 ["know", "knew", "known", "saber/conocer"],
                 ["think", "thought", "thought", "pensar"],
                 ["come", "came", "come", "venir"],
                 ["give", "gave", "given", "dar"],
                 ["find", "found", "found", "encontrar"],
                 ["tell", "told", "told", "decir/contar"],
                 ["write", "wrote", "written", "escribir"],
                 ["read", "read", "read", "leer"],
                 ["learn", "learnt/learned", "learnt/learned", "aprender"],
                 ["begin", "began", "begun", "empezar"],
             ]},
            {"titulo": "Conectores", "tipo": "lista", "items": [
                ("Añadir", "and, also, moreover, in addition"),
                ("Contrastar", "but, however, although, whereas"),
                ("Causa", "because, since, due to"),
                ("Consecuencia", "so, therefore, as a result"),
                ("Ejemplificar", "for example, for instance, such as"),
            ]},
            {"titulo": "Frases útiles", "tipo": "lista", "items": [
                ("No entiendo", "Sorry, could you repeat that? · Could you speak more slowly?"),
                ("Pedir significado", "What does … mean? · How do you say … in English?"),
                ("Opinar", "I think… · In my opinion… · I'm not sure, but…"),
                ("Estar en desacuerdo", "I see your point, but… · I'm not sure I agree."),
            ]},
            {"titulo": "Falsos amigos", "tipo": "lista", "items": [
                ("actually", "en realidad (no «actualmente» = currently)"),
                ("library", "biblioteca (no «librería» = bookstore)"),
                ("realize", "darse cuenta (no «realizar» = carry out)"),
                ("embarrassed", "avergonzado (no «embarazada» = pregnant)"),
                ("assist", "ayudar (no «asistir» = attend)"),
            ]},
        ],
    },
    {
        "slug": "escritura",
        "titulo": "Leer y escribir mejor",
        "descripcion": "Estructuras, resúmenes y una lista para revisar tus textos.",
        "grupo": "materia",
        "materia": "lectura",
        "color": "amber",
        "secciones": [
            {"titulo": "Leer un texto difícil", "tipo": "pasos", "items": [
                "Antes: mira títulos y conclusión; escribe tres preguntas.",
                "Durante: identifica la tesis y marca cada argumento.",
                "Después: cierra el texto y resume de memoria en 5 líneas.",
                "Compara tu resumen con el texto y corrige lo que faltó.",
            ]},
            {"titulo": "Estructura de un ensayo", "tipo": "lista", "items": [
                ("Introducción", "Contexto breve y tu tesis en una frase."),
                ("Desarrollo", "Un párrafo por argumento, con evidencia o ejemplo."),
                ("Objeción", "La mejor crítica a tu tesis y tu respuesta."),
                ("Conclusión", "Qué demostraste y por qué importa. Nada nuevo."),
            ]},
            {"titulo": "Un buen párrafo", "tipo": "pasos", "items": [
                "Oración temática: la idea del párrafo.",
                "Desarrollo: explicación, evidencia o ejemplo.",
                "Cierre o transición al siguiente párrafo.",
            ]},
            {"titulo": "Lista de revisión", "tipo": "lista", "items": [
                "¿Se entiende la tesis en la primera lectura?",
                "¿Cada párrafo tiene una sola idea?",
                "¿Sobran palabras? Elimina «muy», «realmente», «básicamente»…",
                "¿Hay frases de más de 30 palabras? Divídelas.",
                "¿Usas voz activa? «El equipo decidió» mejor que «fue decidido por el equipo».",
                "¿Citaste tus fuentes?",
                "Léelo en voz alta: donde tropiezas, hay que reescribir.",
            ]},
        ],
    },
    {
        "slug": "economia",
        "titulo": "Economía y finanzas personales",
        "descripcion": "Conceptos clave para entender noticias y decidir con tu dinero.",
        "grupo": "materia",
        "materia": "economia",
        "color": "lime",
        "secciones": [
            {"titulo": "Conceptos clave", "tipo": "lista", "items": [
                ("Costo de oportunidad", "Lo mejor a lo que renuncias al elegir."),
                ("Pensar en el margen", "Decide comparando el beneficio y el costo de una unidad más."),
                ("Costo hundido", "Lo ya gastado no debe influir en decisiones futuras."),
                ("Oferta y demanda", "Más demanda sube el precio; más oferta lo baja."),
                ("Elasticidad", "Cuánto cambia la cantidad cuando cambia el precio."),
                ("Inflación", "Subida general de precios: tu dinero compra menos."),
                ("PIB real", "Producción ajustada por inflación."),
                ("Externalidad", "Efecto sobre terceros que el precio no refleja."),
            ]},
            {"titulo": "Finanzas personales", "tipo": "lista", "items": [
                ("Regla 50/30/20", "50 % necesidades, 30 % gustos, 20 % ahorro y deudas."),
                ("Fondo de emergencia", "De 3 a 6 meses de gastos básicos."),
                ("Interés compuesto", "C · (1 + r)ⁿ: el tiempo es tu mejor aliado."),
                ("Regla del 72", "72 / tasa anual ≈ años para duplicar el dinero."),
                ("Deuda cara primero", "Paga antes la de mayor interés (tarjetas de crédito)."),
                ("Diversificar", "No pongas todo en una sola inversión."),
                ("Riesgo y rentabilidad", "Más rentabilidad esperada implica más riesgo."),
            ]},
        ],
    },
]

GRUPOS = [
    ("estudio", "Para estudiar mejor"),
    ("materia", "Chuletas por materia"),
]


def por_slug(slug):
    return next((g for g in GUIAS if g["slug"] == slug), None)


def de_materia(materia_slug):
    """La guía asociada a una materia, si existe."""
    for g in GUIAS:
        if materia_slug in g.get("materias", [g.get("materia")]):
            return g
    return None


def preparar(guia):
    """Copia de la guía con los ítems de lista normalizados a {termino, texto}."""
    secciones = []
    for sec in guia["secciones"]:
        sec = dict(sec)
        if sec["tipo"] == "lista":
            sec["items"] = [
                {"termino": i[0], "texto": i[1]} if isinstance(i, tuple) else {"termino": "", "texto": i}
                for i in sec["items"]
            ]
        secciones.append(sec)
    return {**guia, "secciones": secciones}
