#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lee la Cotizacion Divisas del Banco de la Nacion Argentina (BNA)
y genera cotizacion.json con compra, venta y fecha.
Reintenta el BNA varias veces (los cortes suelen ser intermitentes).
Solo si el BNA falla en todos los intentos, usa dolarapi.com como respaldo.
Corre automaticamente via GitHub Actions varias veces al dia.
"""
import re, json, sys, time, datetime, urllib.request, ssl

URL_BNA = "https://www.bna.com.ar/Personas"
URL_FALLBACK = "https://dolarapi.com/v1/dolares/oficial"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

REINTENTOS_BNA = 4      # cuantas veces intentar el BNA
ESPERA_SEG = 5          # pausa entre intentos

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    })
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="ignore")

def parse_bna(html):
    # La pagina trae 2 tablas: "Cotizacion Billetes" y "Cotizacion Divisas".
    # La tabla de DIVISAS es la que necesita Handel (comercio exterior).
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
    return compra, venta, fecha, "Banco de la Nacion Argentina - Cotizacion Divisas"

def intentar_bna():
    ultimo_error = None
    for i in range(1, REINTENTOS_BNA + 1):
        try:
            html = fetch(URL_BNA)
            return parse_bna(html)
        except Exception as e:
            ultimo_error = e
            print(f"Intento {i}/{REINTENTOS_BNA} al BNA fallo: {e}", file=sys.stderr)
            if i < REINTENTOS_BNA:
                time.sleep(ESPERA_SEG)
    raise ultimo_error

def parse_fallback():
    # dolarapi.com devuelve JSON: {"compra":..., "venta":..., "fechaActualizacion":"2026-..."}
    raw = fetch(URL_FALLBACK)
    d = json.loads(raw)
    compra = float(d["compra"])
    venta  = float(d["venta"])
    fecha = ""
    fa = d.get("fechaActualizacion", "")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", fa)
    if m:
        fecha = f"{m.group(3)}/{m.group(2)}/{m.group(1)}"
    return compra, venta, fecha, "dolarapi.com - Dolar Oficial (respaldo)"

def main():
    # 1) Intentar BNA varias veces
    try:
        compra, venta, fecha, fuente = intentar_bna()
        print("Fuente: BNA (dato preciso)")
    except Exception as e:
        print(f"BNA fallo en los {REINTENTOS_BNA} intentos ({e}). Usando respaldo dolarapi...", file=sys.stderr)
        # 2) Respaldo dolarapi solo si el BNA no respondio en ningun intento
        compra, venta, fecha, fuente = parse_fallback()
        print("Fuente: dolarapi (respaldo)")

    # validacion de cordura: el dolar tiene que estar en un rango razonable
    if not (100 < compra < 100000 and 100 < venta < 100000):
        raise ValueError(f"Valores fuera de rango: {compra}/{venta}")

    data = {
        "compra": compra,
        "venta": venta,
        "fecha": fecha,
        "fuente": fuente,
        "actualizado": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    with open("cotizacion.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("OK:", json.dumps(data, ensure_ascii=False))

if __name__ == "__main__":
    main()
