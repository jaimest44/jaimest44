#!/usr/bin/env python3
"""
Agente de búsqueda y descarga de exámenes oficiales de oposición
(Administrativo / Auxiliar Administrativo) de ayuntamientos de Andalucía.

Qué hace:
  1. Visita las páginas semilla de `fuentes.py` (webs oficiales de empleo
     público de ayuntamientos/diputaciones andaluces).
  2. Sigue, un nivel, los enlaces internos relacionados con oposiciones.
  3. Recoge todos los enlaces a PDF y los clasifica por:
       - puesto: administrativo / auxiliar_administrativo / sin_clasificar
       - tipo: primer_ejercicio_test / segundo_ejercicio_preguntas_cortas /
               plantilla_respuestas / otros
  4. Descarga los PDF a `descargas/<organismo>/<puesto>/<tipo>/archivo.pdf`.
  5. Escribe un manifiesto `descargas/manifiesto.csv` con el origen de cada
     archivo (para poder citar la fuente oficial de cada examen).

IMPORTANTE:
  - Solo descarga de las webs oficiales listadas en fuentes.py (ayuntamientos,
    diputaciones, Junta de Andalucía). No usa academias privadas ni agregadores
    de terceros, para asegurar que el material es el examen real oficial.
  - Si un ayuntamiento no publica plantilla de respuestas para el segundo
    ejercicio (preguntas cortas/supuesto práctico), el agente NO inventa
    respuestas: simplemente no genera ese archivo y lo indica en el manifiesto.
  - Este script necesita salida a internet sin restricciones (ejecútalo en tu
    propio ordenador, no dentro de un sandbox con proxy de red restringido).

Uso:
    pip install -r requirements.txt
    python buscar_examenes.py --puesto auxiliar_administrativo
    python buscar_examenes.py --puesto administrativo --organismo "Dos Hermanas"
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from fuentes import FUENTES_ANDALUCIA, PALABRAS_CLAVE_PUESTO, PALABRAS_CLAVE_TIPO

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AgenteOposiciones/1.0; uso educativo)"}
TIMEOUT = 20
PAUSA_ENTRE_PETICIONES = 1.0  # segundos, para no saturar las webs municipales

ENLACES_RELEVANTES = re.compile(
    r"oposici|empleo.?p[uú]blico|selecci[oó]n de personal|bolsa|convocatoria|"
    r"recursos.?humanos|administrativ",
    re.IGNORECASE,
)


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return texto.lower()


def clasificar(texto: str, mapa: dict[str, list[str]], por_defecto: str) -> str:
    texto_norm = _normalizar(texto)
    for etiqueta, palabras in mapa.items():
        for palabra in palabras:
            if _normalizar(palabra) in texto_norm:
                return etiqueta
    return por_defecto


def obtener_html(url: str) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [aviso] no se pudo abrir {url}: {exc}", file=sys.stderr)
        return None
    return BeautifulSoup(resp.text, "html.parser")


def enlaces_de_pagina(url_base: str, soup: BeautifulSoup) -> list[tuple[str, str]]:
    enlaces = []
    for a in soup.find_all("a", href=True):
        href = urljoin(url_base, a["href"])
        texto = a.get_text(" ", strip=True) or href
        enlaces.append((href, texto))
    return enlaces


def recolectar_pdfs(
    fuente: dict, profundidad: int = 2, max_paginas_por_nivel: int = 30,
) -> list[tuple[str, str, str]]:
    """Devuelve lista de (url_pdf, texto_enlace, organismo) para una fuente semilla.

    Recorre la web del organismo en anchura, hasta `profundidad` niveles de
    enlaces internos relacionados con oposiciones/empleo público, para traerse
    TODAS las convocatorias que encuentre (no solo un puesto concreto). Las
    webs de ayuntamiento suelen anidar cada convocatoria bajo su propia
    carpeta/año, así que un solo nivel se queda corto.
    """
    organismo = fuente["organismo"]
    url_semilla = fuente["url"]
    print(f"[buscando] {organismo} -> {url_semilla}")

    mismo_dominio = urlparse(url_semilla).netloc
    encontrados: list[tuple[str, str, str]] = []
    visitadas = {url_semilla}
    nivel_actual = [url_semilla]

    for nivel in range(profundidad + 1):
        siguiente_nivel: list[str] = []
        for url_pagina in nivel_actual[:max_paginas_por_nivel]:
            if url_pagina != url_semilla:
                time.sleep(PAUSA_ENTRE_PETICIONES)
            soup = obtener_html(url_pagina)
            if soup is None:
                continue
            for href, texto in enlaces_de_pagina(url_pagina, soup):
                if href.lower().endswith(".pdf"):
                    encontrados.append((href, texto, organismo))
                    continue
                if (
                    nivel < profundidad
                    and urlparse(href).netloc == mismo_dominio
                    and href not in visitadas
                    and ENLACES_RELEVANTES.search(texto + " " + href)
                ):
                    visitadas.add(href)
                    siguiente_nivel.append(href)
        nivel_actual = siguiente_nivel
        if not nivel_actual:
            break

    return encontrados


def descargar_pdf(url: str, destino: Path) -> bool:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  [error] no se pudo descargar {url}: {exc}", file=sys.stderr)
        return False
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(resp.content)
    return True


def nombre_archivo_seguro(texto: str, url: str) -> str:
    base = texto.strip() or Path(urlparse(url).path).stem
    base = _normalizar(base)
    base = re.sub(r"[^a-z0-9]+", "_", base).strip("_")
    return (base or "documento")[:80] + ".pdf"


SEGMENTOS_URL_IGNORADOS = {
    "export", "sites", "concejalias", "relaciones-humanas", "galleries",
    "documentos-oposiciones", "servicios", "informacion", "wp-content",
    "uploads", "images", "empleo-publico", "recursos-humanos",
}


def derivar_puesto_de_url(url: str) -> str:
    """Si el nombre del puesto no coincide con ninguna palabra clave conocida,
    se usa el nombre de la carpeta de la convocatoria en la URL (los
    ayuntamientos casi siempre publican cada proceso selectivo en su propia
    carpeta), para no amontonar oposiciones distintas en "sin_clasificar"."""
    segmentos = [s for s in urlparse(url).path.split("/") if s]
    if segmentos:
        segmentos = segmentos[:-1]  # descarta el nombre del propio archivo
    candidatos = [
        s for s in segmentos
        if _normalizar(s).replace("-", "").replace("_", "") not in
        {s2.replace("-", "") for s2 in SEGMENTOS_URL_IGNORADOS}
        and not re.fullmatch(r"20\d{2}", s)  # años sueltos, ej. "2024"
        and not re.fullmatch(r"new_folder_\d+", s, re.IGNORECASE)
    ]
    if not candidatos:
        return "sin_clasificar"
    bruto = _normalizar(candidatos[-1])
    return re.sub(r"[^a-z0-9]+", "_", bruto).strip("_") or "sin_clasificar"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--puesto", default=None,
        help=(
            "Si se indica, filtra por puesto (coincidencia parcial, ej. "
            "'administrativo' o 'policia_local'). Por defecto: TODAS las "
            "oposiciones que se encuentren en cada ayuntamiento."
        ),
    )
    parser.add_argument(
        "--organismo", default=None,
        help="Filtra fuentes cuyo nombre contenga este texto (ej. 'Dos Hermanas')",
    )
    parser.add_argument(
        "--salida", default="descargas", help="Carpeta donde guardar los PDF descargados",
    )
    parser.add_argument(
        "--profundidad", type=int, default=2,
        help="Niveles de enlaces internos a seguir desde la página semilla (por defecto: 2)",
    )
    parser.add_argument(
        "--max-paginas-por-nivel", type=int, default=30,
        help="Límite de páginas a visitar en cada nivel, por fuente (por defecto: 30)",
    )
    args = parser.parse_args()

    fuentes = FUENTES_ANDALUCIA
    if args.organismo:
        fuentes = [f for f in fuentes if args.organismo.lower() in f["organismo"].lower()]
        if not fuentes:
            print(f"No hay ninguna fuente que coincida con '{args.organismo}' en fuentes.py")
            return

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    manifiesto_path = salida / "manifiesto.csv"
    filas_manifiesto = []

    for fuente in fuentes:
        pdfs = recolectar_pdfs(
            fuente, profundidad=args.profundidad, max_paginas_por_nivel=args.max_paginas_por_nivel,
        )
        for url_pdf, texto, organismo in pdfs:
            puesto = clasificar(texto + " " + url_pdf, PALABRAS_CLAVE_PUESTO, "sin_clasificar")
            if puesto == "sin_clasificar":
                puesto = derivar_puesto_de_url(url_pdf)
            if args.puesto and args.puesto.lower() not in puesto.lower():
                continue
            tipo = clasificar(texto + " " + url_pdf, PALABRAS_CLAVE_TIPO, "otros")

            nombre = nombre_archivo_seguro(texto, url_pdf)
            organismo_dir = re.sub(r"[^a-z0-9]+", "_", _normalizar(organismo)).strip("_")
            destino = salida / organismo_dir / puesto / tipo / nombre

            if destino.exists():
                print(f"  [ya existe] {destino}")
            else:
                time.sleep(PAUSA_ENTRE_PETICIONES)
                ok = descargar_pdf(url_pdf, destino)
                print(f"  [{'ok' if ok else 'fallo'}] {url_pdf} -> {destino}")
                if not ok:
                    continue

            filas_manifiesto.append({
                "organismo": organismo,
                "puesto": puesto,
                "tipo": tipo,
                "archivo_local": str(destino),
                "url_origen": url_pdf,
                "texto_enlace": texto,
            })

    if filas_manifiesto:
        with manifiesto_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(filas_manifiesto[0].keys()))
            writer.writeheader()
            writer.writerows(filas_manifiesto)
        print(f"\nManifiesto guardado en {manifiesto_path} ({len(filas_manifiesto)} documentos)")
    else:
        print("\nNo se ha descargado ningún documento con los filtros indicados.")


if __name__ == "__main__":
    main()
