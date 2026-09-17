#!/usr/bin/env python3
"""
Combina los PDF descargados por `buscar_examenes.py` en un único cuadernillo
por organismo/puesto, con una portada que indica la fuente oficial de cada
documento (para que quede constancia de que no es material inventado).

Uso:
    python generar_pdf_resumen.py --entrada descargas --salida cuadernillos
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

from pypdf import PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def portada_pdf(ruta: Path, titulo: str, lineas: list[str]) -> None:
    c = canvas.Canvas(str(ruta), pagesize=A4)
    ancho, alto = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, alto - 80, titulo)
    c.setFont("Helvetica", 10)
    y = alto - 120
    for linea in lineas:
        for sub in [linea[i:i + 95] for i in range(0, len(linea), 95)] or [""]:
            c.drawString(50, y, sub)
            y -= 14
        y -= 6
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = alto - 60
    c.save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", default="descargas")
    parser.add_argument("--salida", default="cuadernillos")
    args = parser.parse_args()

    entrada = Path(args.entrada)
    manifiesto = entrada / "manifiesto.csv"
    if not manifiesto.exists():
        print(f"No existe {manifiesto}. Ejecuta antes buscar_examenes.py")
        return

    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)

    grupos: dict[tuple[str, str], list[dict]] = defaultdict(list)
    with manifiesto.open(encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            grupos[(fila["organismo"], fila["puesto"])].append(fila)

    for (organismo, puesto), filas in grupos.items():
        nombre_base = f"{organismo} - {puesto}".replace("/", "-")
        portada_tmp = salida / f"_portada_{nombre_base}.pdf"
        lineas = [
            f"Organismo: {organismo}",
            f"Puesto: {puesto}",
            "",
            "Documentos incluidos y fuente oficial:",
        ]
        for fila in filas:
            lineas.append(f"- [{fila['tipo']}] {fila['texto_enlace']}")
            lineas.append(f"  Fuente: {fila['url_origen']}")
        portada_pdf(portada_tmp, f"Oposición {puesto} - {organismo}", lineas)

        writer = PdfWriter()
        writer.append(str(portada_tmp))
        for fila in filas:
            ruta_pdf = Path(fila["archivo_local"])
            if ruta_pdf.exists():
                try:
                    writer.append(str(ruta_pdf))
                except Exception as exc:
                    print(f"  [aviso] no se pudo añadir {ruta_pdf}: {exc}")

        destino = salida / f"{nombre_base}.pdf"
        with destino.open("wb") as f:
            writer.write(f)
        portada_tmp.unlink(missing_ok=True)
        print(f"[ok] {destino}")


if __name__ == "__main__":
    main()
