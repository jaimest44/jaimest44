# Agente de exámenes de oposición (Ayuntamientos de Andalucía)

Herramienta para localizar y descargar, **solo de fuentes oficiales**
(ayuntamientos, diputaciones y Junta de Andalucía), exámenes reales de
oposición. Por defecto se trae **todas las oposiciones que encuentre en
cada ayuntamiento** (Administrativo, Auxiliar Administrativo, Policía
Local, Técnico, etc.), cada una en su propia carpeta; si solo te interesa
un puesto concreto, se puede filtrar con `--puesto`.

Para cada oposición encontrada, intenta traer:

- **Primer ejercicio**: examen tipo test, con su plantilla de respuestas.
- **Segundo ejercicio**: preguntas cortas / supuesto práctico, con la
  plantilla de corrección oficial si el organismo la ha publicado.

## Por qué no vienen ya PDFs descargados en este repositorio

Esta sesión se ejecutó en un entorno con salida a internet restringida
(proxy de red que solo permite búsquedas, no descarga directa de archivos
de webs municipales). Por eso el repositorio contiene el **agente listo
para usar**, no los PDF ya descargados. Ejecútalo tú en tu propio
ordenador (con internet normal) y descargará los documentos reales.

## Uso

```bash
cd agente_oposiciones
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Buscar y descargar TODAS las oposiciones de TODOS los ayuntamientos de
# fuentes.py (tarda más, precisamente porque no se limita a un puesto)
python buscar_examenes.py

# Solo de un ayuntamiento concreto, pero con todos sus puestos
python buscar_examenes.py --organismo "Dos Hermanas"

# Si además quieres quedarte solo con un puesto en concreto
python buscar_examenes.py --organismo "Dos Hermanas" --puesto auxiliar_administrativo

# Unir lo descargado en un cuadernillo PDF por organismo/puesto, con
# portada que cita la fuente oficial de cada examen
python generar_pdf_resumen.py
```

Al no limitarse a un puesto, el rastreo visita más páginas por ayuntamiento
(controlable con `--profundidad` y `--max-paginas-por-nivel`), así que
tardará más y generará más carpetas en `descargas/` — una por cada
oposición distinta que encuentre.

## Orden de rastreo: capitales y ciudades grandes primero

`fuentes.py` guarda la población aproximada de cada ayuntamiento, y el
script rastrea siempre de mayor a menor población: primero las
diputaciones/Junta de Andalucía (agregan convocatorias de muchos
ayuntamientos a la vez), luego las capitales de provincia y grandes
ciudades, y al final los municipios pequeños — que es donde es más
probable perder el tiempo entrando en una sede electrónica que ni
siquiera tiene procesos selectivos.

Si quieres saltarte directamente los pueblos pequeños en vez de esperar a
que les toque el turno:

```bash
# Ignora cualquier ayuntamiento con menos de 50.000 habitantes
python buscar_examenes.py --poblacion-minima 50000
```

Para añadir más ayuntamientos a `fuentes.py`, incluye también su
`"poblacion"` (habitantes, aproximado) para que se ordenen bien; los
organismos que no son un único municipio (diputaciones, Junta de
Andalucía) llevan `"poblacion": None` y siempre van primero.

## Pausar y reanudar sin repetir trabajo

El script lleva un registro en `descargas/progreso.json` de qué
ayuntamientos ha terminado de rastrear **por completo**. Si lo paras
(`Ctrl+C`) y vuelves a lanzar exactamente el mismo comando, se salta
automáticamente los ayuntamientos ya completados y continúa por donde lo
dejaste:

```bash
python buscar_examenes.py
# ... Ctrl+C en cualquier momento ...
python buscar_examenes.py   # mismo comando: retoma donde lo dejó
```

Notas sobre cómo funciona:

- Un ayuntamiento solo se marca como "completado" cuando se ha terminado
  de rastrear entero. Si lo paras a mitad de un ayuntamiento, esa
  ejecución siguiente lo vuelve a rastrear entero (pero sin volver a
  **descargar** los PDF que ya tuviera guardados en disco, eso ya lo
  comprueba archivo a archivo).
- `descargas/manifiesto.csv` se va escribiendo línea a línea según se
  descarga cada PDF (no al final), así que aunque lo interrumpas nunca se
  pierde lo ya conseguido.
- `--forzar` vuelve a rastrear ayuntamientos que ya estaban marcados como
  completados (útil si quieres comprobar si ha salido una convocatoria
  nueva).
- `--reset-progreso` borra `progreso.json` y empieza de cero para todos.
- El progreso se guarda por el **nombre del organismo** tal como aparece
  en `fuentes.py`; si cambias ese nombre, el script lo tratará como uno
  nuevo.

Los archivos quedan en `descargas/<organismo>/<puesto>/<tipo>/*.pdf` y el
cuadernillo combinado en `cuadernillos/`. `descargas/manifiesto.csv` guarda
la URL oficial de origen de cada PDF, para poder verificarlo siempre.

## Añadir más ayuntamientos

Edita `fuentes.py` y añade la sección "Empleo público / Oposiciones /
Recursos Humanos" del ayuntamiento que te interese; el agente sigue un
nivel de enlaces desde ahí en busca de PDF.

## Honestidad sobre las respuestas

- El primer ejercicio (test) casi siempre tiene plantilla oficial de
  respuestas publicada por el propio ayuntamiento: el agente la descarga
  cuando existe.
- El segundo ejercicio (preguntas cortas / supuesto práctico) **muchas
  veces no tiene respuestas oficiales publicadas** — solo el enunciado, o
  a veces una plantilla de corrección con los criterios de puntuación (no
  las respuestas redactadas). El agente **no inventa respuestas**: si no
  hay documento oficial de respuestas, simplemente no lo genera, y el
  manifiesto deja claro qué se descargó de cada convocatoria.

## Enlaces oficiales ya verificados (búsqueda de hoy, 2026-09-17)

Comprobados por búsqueda web durante esta sesión — cárgalos directamente
en el navegador si no puedes ejecutar el script ahora mismo:

- **Ayuntamiento de Dos Hermanas (Sevilla)** — Auxiliar Administrativo,
  turno de reserva discapacidad (2024), examen tipo test **con respuestas**:
  `https://www.doshermanas.es/export/sites/ayto-dos-hermanas/concejalias/relaciones-humanas/.galleries/DOCUMENTOS-Oposiciones/2024/AUX.-ADMINISTRATIVO-A-DISCAP./EXAMEN-CON-RESPUESTA.pdf`
  Bases de la convocatoria (BOP):
  `https://www.doshermanas.es/export/sites/ayto-dos-hermanas/concejalias/relaciones-humanas/.galleries/DOCUMENTOS-Oposiciones/2024/AUX.-ADMINISTRATIVO-A-DISCAP./BASES-BOP.-AUXILIAR-ADMINISTRATIVO-A-DISCAPACIDAD.pdf`
  Modelo de test C2 funcionario:
  `https://www.doshermanas.es/export/sites/ayto-dos-hermanas/concejalias/relaciones-humanas/.galleries/DOCUMENTOS-Oposiciones/2024/MAS-SEVILLA/new_folder_00001/MODELO-TEST-PARA-EL-EXAMEN-DE-AUXILIAR-ADMINISTRATIVO-A-C2-FUNCIONARIO.pdf`

- **Ayuntamiento de Maracena (Granada)** — Auxiliar Administrativo (2017),
  examen tipo test (50 preguntas):
  `https://maracena.es/wp-content/uploads/2018/06/images_EMPLEO-PUBLICO_4_AUX_ADMTVO_2017_Examen_Aux._Admtvo._.pdf`

- **Diputación de Almería** (gestiona bolsas de trabajo para ayuntamientos
  de la provincia) — Auxiliar Administrativo, instrucciones y **plantilla
  de corrección del segundo ejercicio (supuesto práctico)**:
  `https://www.dipalme.es/Servicios/Informacion/Informacion.nsf/4C29E066167FDADDC12587ED0043DC2C/$file/Plantilla%20Correcci%C3%B3n%20Supuesto%20Pr%C3%A1ctico%20Bolsa%20Auxiliar%20Administrativo.pdf`

- **Junta de Andalucía — IAAP** (no es un ayuntamiento, pero es el mayor
  repositorio oficial de cuestionarios con plantilla de respuestas, C1
  Administrativo y C2 Auxiliar Administrativo, útil como banco adicional
  de preguntas con el mismo temario que usan muchos ayuntamientos):
  - C1.1000 Administrativos: `https://www.juntadeandalucia.es/organismos/iaap/areas/empleo-publico/cuestionarios/detalle/13393.html`
  - C2.1000 Auxiliares Administrativos: `https://www.juntadeandalucia.es/organismos/iaap/areas/empleo-publico/cuestionarios/detalle/13408.html`

Los enlaces a webs municipales cambian de ubicación con el tiempo; si
alguno de estos ya no responde, vuelve a ejecutar `buscar_examenes.py`
sobre `fuentes.py`, que apunta a la página índice de cada ayuntamiento en
lugar de al PDF concreto.
