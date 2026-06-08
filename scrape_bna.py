#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lee la Cotizacion Divisas del Banco de la Nacion Argentina (BNA)
y genera cotizacion.json con compra, venta y fecha.
Corre automaticamente via GitHub Actions varias veces al dia.
"""
import re, json, sys, datetime, urllib.request

URL = "https://www.bna.com.ar/Personas"
UA  = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")

def parse(html):
    # La pagina trae 2 tablas: "Cotizacion Billetes" y "Cotizacion Divisas".
    # La tabla de DIVISAS es la que necesita Handel (operaciones de comercio exterior).
    # Tomamos la ULTIMA aparicion de "Dolar U.S.A", que corresponde a Divisas.
    matches = list(re.finditer(r"Dolar U\.S\.A", html))
    if not matches:
        raise ValueError("No se encontro 'Dolar U.S.A' en la pagina del BNA")
    seg = html[matches[-1].start(): matches[-1].start() + 200]
    nums = re.findall(r"(\d{1,4}[.,]\d{4})", seg)
    if len(nums) < 2:
        raise ValueError("No se pudieron extraer compra/venta")
    compra = float(nums[0].replace(",", "."))
    venta  = float(nums[1].replace(",", "."))
    fm = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", html)
    fecha = fm.group(1) if fm else ""
    return compra, venta, fecha

def main():
    html = fetch(URL)
    compra, venta, fecha = parse(html)
    # validacion de cordura: el dolar tiene que estar en un rango razonable
    if not (100 < compra < 100000 and 100 < venta < 100000):
        raise ValueError(f"Valores fuera de rango: {compra}/{venta}")
    data = {
        "compra": compra,
        "venta": venta,
        "fecha": fecha,
        "fuente": "Banco de la Nacion Argentina - Cotizacion Divisas",
        "actualizado": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    with open("cotizacion.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("OK:", json.dumps(data, ensure_ascii=False))

if __name__ == "__main__":
    main()
