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
"""

FUENTES_ANDALUCIA = [
    # Sevilla
    {
        "organismo": "Ayuntamiento de Dos Hermanas (Sevilla)",
        "url": "https://www.doshermanas.es/concejalias/relaciones-humanas/oposiciones/",
    },
    {
        "organismo": "Ayuntamiento de Sevilla",
        "url": "https://www.sevilla.org/servicios/empleo-publico/oferta-de-empleo-publico",
    },
    # Granada
    {
        "organismo": "Ayuntamiento de Maracena (Granada)",
        "url": "https://maracena.es/empleo-publico/",
    },
    {
        "organismo": "Ayuntamiento de Granada",
        "url": "https://www.granada.org/inet/wrecursoshumanos.nsf",
    },
    # Almería (diputación provincial: gestiona bolsas de varios ayuntamientos)
    {
        "organismo": "Diputación de Almería",
        "url": "https://www.dipalme.es/Servicios/Informacion/Informacion.nsf",
    },
    # Málaga
    {
        "organismo": "Ayuntamiento de Málaga",
        "url": "https://www.malaga.eu/es/ayuntamiento/empleo-publico/",
    },
    # Córdoba
    {
        "organismo": "Ayuntamiento de Córdoba",
        "url": "https://www.cordoba.es/index.php/empleo-publico",
    },
    # Cádiz / Jerez
    {
        "organismo": "Ayuntamiento de Jerez de la Frontera",
        "url": "https://www.jerez.es/webs_municipales/recursos_humanos/",
    },
    # Junta de Andalucía (IAAP) - no es un ayuntamiento, pero publica el mayor
    # repositorio oficial de cuestionarios con plantilla de respuestas para
    # C1 (Administrativo) y C2 (Auxiliar Administrativo); útil como banco de
    # preguntas adicional y para contrastar formato.
    {
        "organismo": "Junta de Andalucía - IAAP (C1 Administrativo)",
        "url": "https://www.juntadeandalucia.es/organismos/iaap/areas/empleo-publico/cuestionarios/detalle/13393.html",
    },
    {
        "organismo": "Junta de Andalucía - IAAP (C2 Auxiliar Administrativo)",
        "url": "https://www.juntadeandalucia.es/organismos/iaap/areas/empleo-publico/cuestionarios/detalle/13408.html",
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
