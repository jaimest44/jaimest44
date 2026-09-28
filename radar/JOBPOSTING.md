# Datos estructurados JobPosting — qué cambiar en la web

Search Console avisó el 28/09/2026 de 7 problemas en `plazasconvocatorias.es`: faltaban
`description` y `jobLocation` (críticos) y `baseSalary`, `validThrough`, `streetAddress`,
`postalCode` y `addressRegion` (no críticos).

El marcado que se estaba emitiendo era este (ficha de Utiel):

```json
{"@type":"JobPosting","title":"Técnico/a de Juventud","datePosted":"2026-09-14",
 "employmentType":"FULL_TIME","hiringOrganization":{...},"validThrough":"2026-09-28",
 "totalJobOpenings":1,"jobLocation":{...}}
```

Faltaba `description`, que Google exige **siempre**, y `jobLocation` en las convocatorias
estatales y autonómicas, que no tienen municipio.

## Lo que hay que hacer

`radar/seo.py` genera el marcado correcto a partir de `salida/radar.json`. Dos opciones:

**a) Importarlo en el generador de páginas** (preferible):

```python
import seo

marcado = seo.jobposting(convocatoria, 'https://plazasconvocatorias.es')
texto, html_descripcion = seo.descripcion(convocatoria)
# marcado is None  ->  la ficha se publica SIN JobPosting (ver más abajo por qué)
```

**b) Consumir el fichero ya generado**, si el generador no es Python:

```bash
python radar/seo.py salida/radar.json https://plazasconvocatorias.es salida/jobposting.json
```

`salida/jobposting.json` es un diccionario `id de convocatoria -> marcado`. Los ids son los
mismos que ya usan las URLs (`/convocatoria/<id>/`).

## Importante: la descripción tiene que verse en la página

Google pide que el marcado coincida con lo que lee el visitante. `seo.descripcion()` devuelve
el mismo contenido en texto y en HTML: hay que **pintar esos párrafos en la ficha**, encima
de la tabla de datos, y usar el HTML tal cual en `description`. Hoy la ficha enseña los datos
sueltos (organismo, municipio, plazas…) pero no el texto.

## Fichas que van sin JobPosting (y por qué)

De 15.123 convocatorias, 9.817 llevan marcado y 5.306 no. Se quedan fuera:

- **Sin fecha de fin de plazo** (el boletín aún no la da: bases publicadas sin extracto en el
  BOE, tribunales, listas de admitidos). Google exige `validThrough` para poder retirar las
  ofertas caducadas y no se va a inventar una fecha.
- **Sin organismo identificado**: `hiringOrganization` es obligatorio.
- **Provisión de puestos** (libre designación, concursos de traslados, comisiones de
  servicio, jefaturas): no son ofertas abiertas, solo pueden concurrir quienes ya son
  funcionarios de ese cuerpo. Marcarlas como oferta de empleo sería engañoso.

Una página sin marcado no da error en Search Console: simplemente no opta a aparecer como
oferta de empleo. La página sigue indexándose como página normal.

## Las convocatorias ya cerradas se quedan como están

Google admite tres formas de retirar una oferta caducada: `validThrough` en el pasado,
devolver 404/410, o quitar el marcado. Usamos la primera, que es la única que **conserva la
página**: el histórico por municipio es tráfico SEO y alimenta el "qué cayó en cada examen".

## Lo que seguimos sin publicar, a propósito

- `baseSalary`: el extracto del BOE no dice el sueldo. Depende de la RPT de cada ayuntamiento.
- `streetAddress` y `postalCode`: el boletín no publica la dirección del puesto.
- `employmentType`: el boletín no dice la jornada. **Esto había que quitarlo**: se estaba
  emitiendo `FULL_TIME` sin que ningún boletín lo diga.

Son avisos no críticos y no impiden aparecer en la Búsqueda. Rellenarlos a ojo sí sería un
problema: Google penaliza el marcado que no se corresponde con la realidad de la página.

## Después de desplegar

1. Search Console → *Mejoras* → *Ofertas de trabajo* → **Validar corrección**. La validación
   tarda entre unos días y dos semanas.
2. Comprobar dos o tres fichas en la Prueba de resultados enriquecidos
   (`https://search.google.com/test/rich-results`): una con municipio, una estatal y una
   cerrada.
3. El número de "ofertas válidas" bajará (de ~14.600 a ~9.800) y eso es lo correcto: lo que
   desaparece no era una oferta a la que nadie pudiera presentarse.
