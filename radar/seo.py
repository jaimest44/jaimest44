"""Marcado JobPosting (schema.org) para las fichas de convocatoria.

Google pide cinco campos obligatorios: title, description, datePosted,
hiringOrganization y jobLocation. La web los estaba emitiendo sin `description` y, en las
convocatorias estatales y autonómicas, sin `jobLocation`: por eso Search Console las
rechaza.

Dos decisiones, en la línea del resto del proyecto:

1. **Solo lleva JobPosting lo que es una oferta con plazo.** Si el boletín no dice cuándo
   acaba el plazo (2.967 de 15.123 fichas: bases publicadas sin extracto en el BOE todavía,
   nombramientos, tribunales…), no hay oferta a la que presentarse y la ficha va sin
   JobPosting. Google exige `validThrough` para poder retirar las caducadas, y no se puede
   inventar una fecha.

2. **No se rellena lo que no sabemos.** `baseSalary`, `streetAddress` y `postalCode` los pide
   Google como recomendables, pero el boletín no los publica: se quedan fuera. Son avisos no
   críticos y no impiden aparecer en la Búsqueda. Tampoco se declara `employmentType`: el
   extracto no dice la jornada.

Una convocatoria caducada NO se despublica: se deja con su `validThrough` en el pasado, que
es una de las tres formas que admite Google para retirarla de los resultados de empleo, y la
que además conserva la página para el histórico.

    python radar/seo.py salida/radar.json https://plazasconvocatorias.es
"""
import datetime as dt, html, json, re, sys

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']
BOLETINES = {'BOE': 'Boletín Oficial del Estado', 'BOJA': 'Boletín Oficial de la Junta de Andalucía',
             'BOP': 'Boletín Oficial de la Provincia'}

def fecha_larga(f):
    d = dt.date.fromisoformat(f)
    return f'{d.day} de {MESES[d.month - 1]} de {d.year}'

def url_ficha(c, base):
    return f"{base.rstrip('/')}/convocatoria/{c['id']}/"

def descripcion(c):
    """Descripción de la convocatoria, frase a frase, solo con lo que publican los boletines.
    Devuelve (texto plano, HTML). El texto debe verse también en la página: Google exige que
    el marcado coincida con lo que lee el visitante."""
    p = []
    plazas = f"{c['plazas']} plaza{'s' if c['plazas'] != 1 else ''}" if c.get('plazas') else 'Plaza'
    titulo = c['titulo'].rstrip(' .')
    org = c.get('organismo') or ''
    # "del Ayuntamiento de X" / "de la Diputación de Y": el artículo depende del organismo.
    articulo = 'de la ' if org.startswith(('Diputación', 'Mancomunidad', 'Agencia', 'Gerencia',
                                           'Universidad', 'Entidad', 'Consejería')) else 'del '
    donde = c.get('municipio') or c.get('provincia') or c.get('ccaa') or ''
    sitio = f" ({c['provincia']})" if c.get('municipio') and c.get('provincia') else ''
    frase = f"{plazas} de {titulo}"
    if org: frase += f" {articulo}{org}"
    if donde and donde not in org: frase += f", {donde}{sitio}"
    p.append(frase + '.')
    if c.get('sistemas'):
        p.append('Sistema de acceso: ' + ', '.join(c['sistemas']).lower() + '.')
    if c.get('categoria_policia'):
        p.append(f"Categoría: {c['categoria_policia']} del Cuerpo de la Policía Local.")
    if c.get('inicio_plazo') and c.get('fin_plazo'):
        dur = f" ({c['plazo_txt']})" if c.get('plazo_txt') else ''
        p.append(f"El plazo de presentación de solicitudes se abrió el {fecha_larga(c['inicio_plazo'])}"
                 f"{dur} y termina el {fecha_larga(c['fin_plazo'])}.")
    b = c.get('bop') or {}
    if b.get('fecha'):
        num = f" número {b['numero']}" if b.get('numero') else ''
        p.append(f"Las bases se publicaron en el Boletín Oficial de la Provincia de {b['provincia']}"
                 f"{num}, de {fecha_larga(b['fecha'])}.")
    if c.get('anuncios'):
        vistas, pubs = set(), []
        for a in c['anuncios'][-6:]:
            linea = f"{a['tipo'].lower()} en el {BOLETINES.get(a['src'], a['src'])} el {fecha_larga(a['f'])}"
            if linea not in vistas:                 # el mismo trámite puede salir dos veces el mismo día
                vistas.add(linea); pubs.append(linea)
        p.append('Publicaciones oficiales: ' + ', '.join(pubs[-4:]) + '.')
    p.append('El fin de plazo es orientativo: se calcula a partir de la publicación que abre '
             'el plazo. Confírmalo siempre en las bases oficiales.')
    texto = ' '.join(p)
    cuerpo = ''.join(f'<p>{html.escape(x)}</p>' for x in p)
    return texto, cuerpo

def lugar(c):
    """jobLocation a partir de lo que sabemos: municipio, provincia o comunidad.
    Nunca se inventan calle ni código postal."""
    dir_ = {'@type': 'PostalAddress', 'addressCountry': 'ES'}
    if c.get('municipio'): dir_['addressLocality'] = c['municipio']
    if c.get('provincia'): dir_['addressRegion'] = c['provincia']
    elif c.get('ccaa'): dir_['addressRegion'] = c['ccaa']
    return {'@type': 'Place', 'address': dir_}

def jobposting(c, base):
    """Marcado de una convocatoria, o None si no es una oferta a la que quepa presentarse."""
    # Sin plazo no hay oferta; sin organismo no se puede declarar hiringOrganization, que
    # Google exige, y no se va a poner un nombre genérico. En ambos casos, ficha sin marcado.
    if not c.get('fin_plazo') or not c.get('inicio_plazo') or not c.get('organismo'):
        return None
    # La provisión de puestos (libre designación, concursos de traslados) no es una oferta
    # de empleo abierta: solo pueden concurrir quienes ya son funcionarios de ese cuerpo.
    if c.get('provision') or re.search(r'libre designaci|provisi[oó]n de(l)? puesto|comisi[oó]n de servicios|'
                                       r'concurso de traslados|jefatura', c['titulo'], re.I):
        return None
    texto, cuerpo = descripcion(c)
    d = {
        '@context': 'https://schema.org',
        '@type': 'JobPosting',
        'title': c['titulo'],
        'description': cuerpo,
        'datePosted': c['inicio_plazo'],
        'validThrough': c['fin_plazo'],
        'hiringOrganization': {'@type': 'Organization', 'name': c['organismo']},
        'jobLocation': lugar(c),
        'identifier': {'@type': 'PropertyValue', 'name': 'plazasconvocatorias.es', 'value': c['id']},
        'url': url_ficha(c, base),
        'directApply': False,          # la solicitud se presenta ante el organismo, no aquí
    }
    if c.get('plazas'): d['totalJobOpenings'] = c['plazas']
    if c.get('familia') and c['familia'] != 'Otras': d['occupationalCategory'] = c['familia']
    if not c.get('provincia') and not c.get('ccaa'):
        # Convocatoria estatal: el destino concreto se adjudica al final del proceso.
        d['applicantLocationRequirements'] = {'@type': 'Country', 'name': 'España'}
    return d

def revisar(convocatorias, base, hoy=None):
    hoy = hoy or dt.date.today().isoformat()
    con, sin, vigentes, faltan = 0, 0, 0, {}
    for c in convocatorias:
        j = jobposting(c, base)
        if not j:
            sin += 1; continue
        con += 1
        if j['validThrough'] >= hoy: vigentes += 1
        for campo in ('title', 'description', 'datePosted', 'hiringOrganization', 'jobLocation', 'validThrough'):
            if not j.get(campo): faltan[campo] = faltan.get(campo, 0) + 1
        if not j['jobLocation']['address'].get('addressRegion'):
            faltan['addressRegion (no crítico)'] = faltan.get('addressRegion (no crítico)', 0) + 1
    print(f'Fichas con JobPosting: {con}  (de ellas, {vigentes} con plazo vigente hoy)')
    print(f'Fichas sin JobPosting (el boletín no da plazo): {sin}')
    print('Campos obligatorios que faltarían:', faltan or 'ninguno')

if __name__ == '__main__':
    D = json.load(open(sys.argv[1], encoding='utf-8'))
    base = sys.argv[2] if len(sys.argv) > 2 else 'https://plazasconvocatorias.es'
    revisar(D['convocatorias'], base, D.get('generado'))
    salida = {c['id']: j for c in D['convocatorias'] if (j := jobposting(c, base))}
    ruta = sys.argv[3] if len(sys.argv) > 3 else 'salida/jobposting.json'
    json.dump(salida, open(ruta, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'{len(salida)} marcados escritos en {ruta}')
