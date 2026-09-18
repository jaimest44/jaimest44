"""
Fuentes oficiales semilla para el agente de búsqueda de exámenes de oposición.

Cada entrada es una página oficial (ayuntamiento, diputación o portal de empleo
público) donde se publican convocatorias, exámenes y plantillas de respuestas.
El agente parte de estas páginas y sigue, hasta dos niveles, los enlaces
internos cuyo texto contenga palabras clave de oposiciones/empleo público, para
traerse TODAS las oposiciones que encuentre en cada ayuntamiento (no solo
Administrativo/Auxiliar Administrativo).

Amplía esta lista con más ayuntamientos andaluces según los vayas necesitando:
la mayoría de ayuntamientos publican sus procesos selectivos bajo una sección
de "Empleo público", "Oposiciones" o "Recursos Humanos / Selección de personal".

Cada fuente lleva un campo "poblacion" (habitantes, aproximado) que
`buscar_examenes.py` usa para ordenar el rastreo de mayor a menor: así se
prioriza a las capitales y grandes ciudades -que sí tienen oposiciones con
frecuencia- y se deja para el final, o se puede excluir directamente, a
ayuntamientos muy pequeños cuya sede electrónica probablemente no tenga
ningún proceso selectivo publicado. Los organismos que no son un único
municipio (diputaciones, Junta de Andalucía) llevan "poblacion": None y se
tratan como máxima prioridad, porque agregan convocatorias de muchos
ayuntamientos a la vez.
"""

# Población aproximada (habitantes, redondeada) solo a efectos de orden de
# rastreo; no hace falta que esté exactamente actualizada al padrón vigente.
FUENTES_ANDALUCIA = [
    # --- Organismos que no son un único municipio: máxima prioridad ---
    # (gestionan o agregan convocatorias de varios ayuntamientos a la vez)
    {
        "organismo": "Diputación de Almería",
        "url": "https://www.dipalme.es/Servicios/Informacion/Informacion.nsf",
        "poblacion": None,
    },
    {
        "organismo": "Junta de Andalucía - IAAP (C1 Administrativo)",
        "url": "https://www.juntadeandalucia.es/organismos/iaap/areas/empleo-publico/cuestionarios/detalle/13393.html",
        "poblacion": None,
    },
    {
        "organismo": "Junta de Andalucía - IAAP (C2 Auxiliar Administrativo)",
        "url": "https://www.juntadeandalucia.es/organismos/iaap/areas/empleo-publico/cuestionarios/detalle/13408.html",
        "poblacion": None,
    },
    # --- Capitales de provincia (de mayor a menor población) ---
    {
        "organismo": "Ayuntamiento de Sevilla",
        "url": "https://www.sevilla.org/servicios/empleo-publico/oferta-de-empleo-publico",
        "poblacion": 684_000,
    },
    {
        "organismo": "Ayuntamiento de Málaga",
        "url": "https://www.malaga.eu/es/ayuntamiento/empleo-publico/",
        "poblacion": 578_000,
    },
    {
        "organismo": "Ayuntamiento de Córdoba",
        "url": "https://www.cordoba.es/index.php/empleo-publico",
        "poblacion": 325_000,
    },
    {
        "organismo": "Ayuntamiento de Granada",
        "url": "https://www.granada.org/inet/wrecursoshumanos.nsf",
        "poblacion": 232_000,
    },
    {
        "organismo": "Ayuntamiento de Almería",
        "url": "https://almeriaciudad.es/transparencia-municipal/oferta-de-empleo-publico",
        "poblacion": 200_000,
    },
    {
        "organismo": "Ayuntamiento de Huelva",
        "url": "https://www.huelva.es/portal/es/procedimientosselectivos",
        "poblacion": 143_000,
    },
    {
        "organismo": "Ayuntamiento de Jaén",
        "url": "https://www.aytojaen.es/portal/sede/se_contenedor1.jsp?seccion=s_ldoc_d10_v4.jsp&codbusqueda=1431&codMenu=1017",
        "poblacion": 112_000,
    },
    {
        "organismo": "Ayuntamiento de Cádiz",
        "url": "https://institucional.cadiz.es/area/Oferta-de-Empleo-P%C3%BAblico/539",
        "poblacion": 111_000,
    },
    # --- Grandes ciudades no capitales de provincia ---
    {
        "organismo": "Ayuntamiento de Jerez de la Frontera (Cádiz)",
        "url": "https://www.jerez.es/webs_municipales/recursos_humanos/",
        "poblacion": 212_000,
    },
    {
        "organismo": "Ayuntamiento de Marbella (Málaga)",
        "url": "https://ayuntamiento.marbella.es/oferta-publica/empleo-publico.html",
        "poblacion": 150_000,
    },
    {
        "organismo": "Ayuntamiento de Dos Hermanas (Sevilla)",
        "url": "https://www.doshermanas.es/concejalias/relaciones-humanas/oposiciones/",
        "poblacion": 136_000,
    },
    {
        "organismo": "Ayuntamiento de Algeciras (Cádiz)",
        "url": "https://www.algeciras.es/es/temas/desarrollo-economico/seleccion-personal/",
        "poblacion": 123_000,
    },
    # --- Municipios medianos ---
    {
        "organismo": "Ayuntamiento de Maracena (Granada)",
        "url": "https://maracena.es/empleo-publico/",
        "poblacion": 24_000,
    },
]

# El orden importa: se usa la primera etiqueta que coincida. Se listan primero
# las que más suelen interesar (Administrativo) y luego el resto de cuerpos y
# categorías habituales en plantillas de ayuntamiento, para que cada oposición
# quede en su propia carpeta en vez de amontonarse en "sin_clasificar".
PALABRAS_CLAVE_PUESTO = {
    "administrativo": ["administrativo", "c1.1000", "cuerpo general de administrativos"],
    "auxiliar_administrativo": ["auxiliar administrativo", "aux. admtvo", "aux admtvo", "c2.1000"],
    "policia_local": ["policia local", "policía local"],
    "bombero": ["bombero", "bombera"],
    "tecnico": ["tecnico de administracion", "técnico de administración", "tecnico superior", "técnico superior", "tecnico medio", "técnico medio", "tag "],
    "arquitecto_ingeniero": ["arquitecto", "ingeniero", "ingeniera"],
    "trabajador_social": ["trabajador social", "trabajadora social", "educador social", "educadora social"],
    "letrado_juridico": ["letrado", "letrada", "jurista", "asesoria juridica", "asesoría jurídica"],
    "auxiliar_biblioteca_cultura": ["biblioteca", "cultura", "monitor deportivo", "monitora deportiva"],
    "conserje_ordenanza_notificador": ["conserje", "ordenanza", "notificador", "notificadora"],
    "oficial_operario": ["oficial", "operario", "peon", "peón", "electricista", "fontanero", "jardinero", "jardinera"],
    "administracion_general": ["administracion general", "administración general", "subgrupo", "escala"],
}

PALABRAS_CLAVE_TIPO = {
    "primer_ejercicio_test": [
        "primer ejercicio", "tipo test", "test", "cuestionario", "1er ejercicio",
    ],
    "segundo_ejercicio_preguntas_cortas": [
        "segundo ejercicio", "preguntas cortas", "supuesto practico", "supuesto práctico",
        "caso practico", "caso práctico", "ejercicio practico", "ejercicio práctico",
    ],
    "plantilla_respuestas": [
        "plantilla", "respuesta correcta", "solucionario", "con respuesta", "correccion", "corrección",
    ],
}
