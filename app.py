import re
from datetime import datetime
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

TIMEOUT = 10000
MSG_NO_MATRICULADO = "El vehiculo no se encuentra matriculado en la Secretaria de Movilidad"
AÑO_ACTUAL = str(datetime.now().year)

def bloquear_recursos(page):
    page.route("**/*", lambda route: route.abort()
               if route.request.resource_type in ["image", "stylesheet", "font", "media", "other"]
               else route.continue_())

def consultar_envigado(page, placa):
    url = "https://movilidad.envigado.gov.co/portal-servicios/#/impuesto-local"
    page.goto(url, wait_until="domcontentloaded")
    page.get_by_role("textbox", name="Placa").fill(placa)
    page.get_by_role("button", name="Buscar").click()

    page.wait_for_function("""() => {
        const tabla = document.querySelector('#tablaCollapseVigencias');
        const noMatriculado = document.body.innerText.includes('El vehiculo no se encuentra matriculado en la Secretaria de Movilidad');
        return tabla || noMatriculado;
    }""", timeout=TIMEOUT)

    if page.get_by_text(MSG_NO_MATRICULADO).is_visible():
        return [], 0

    if page.locator("#selectall").is_visible():
        page.locator("#selectall").check()

    registros = []
    filas = page.locator("#tablaCollapseVigencias tr").all()
    for fila in filas:
        texto_fila = fila.inner_text().strip()
        if not texto_fila:
            continue
        año = re.search(r'\b(20\d{2})\b', texto_fila)
        montos = re.findall(r'\$\s*[\d.]+', texto_fila)
        if año and montos:
            valor_str = montos[-1].replace('$', '').replace(' ', '').replace('.', '')
            try:
                registros.append({
                    'vigencia': año.group(),
                    'estado': 'Pendiente de pago',
                    'total_vigencia': int(valor_str)
                })
            except ValueError:
                pass

    total = sum(r['total_vigencia'] for r in registros)
    return registros, total


def consultar_sabaneta(page, placa):
    url = "https://transitosabaneta.utsetsa.com/#/impuesto-local"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    
    # Esperar que el campo de placa esté disponible
    page.locator("#placa").wait_for(state="visible", timeout=15000)
    page.locator("#placa").fill(placa)
    page.get_by_role("button", name="Buscar").click()

    # Esperar respuesta
    page.wait_for_timeout(20000)

    texto_pagina = page.inner_text("body")

    if MSG_NO_MATRICULADO in texto_pagina:
        return [], 0

    if 'Último pago realizado' in texto_pagina and 'Vigencias pendientes' not in texto_pagina:
        return [], 0

    if 'Vigencias pendientes' not in texto_pagina:
        return [], 0

    page.locator("#tablaCollapseVigencias").wait_for(state="visible", timeout=15000)
    checkbox = page.locator("#selectall")
    checkbox.wait_for(state="visible", timeout=15000)
    if checkbox.is_enabled():
        checkbox.check()

    page.wait_for_timeout(5000)

    spans_cop = page.locator("span.fs-16.ng-binding").all()
    total = 0
    for span in spans_cop[::-1]:
        texto = span.inner_text().strip()
        if "COP" in texto and texto != "COP 0":
            valor_str = texto.replace("COP", "").replace(".", "").strip()
            try:
                total = int(valor_str)
                break
            except ValueError:
                pass

    registros = []
    filas = page.locator("#tablaCollapseVigencias tr").all()
    for fila in filas:
        texto_fila = fila.inner_text().strip()
        if not texto_fila:
            continue
        año = re.search(r'\b(20\d{2})\b', texto_fila)
        montos = re.findall(r'COP\s*[\d.]+', texto_fila)
        if año and montos:
            valor_fila = montos[-1].replace('COP', '').replace(' ', '').replace('.', '')
            try:
                registros.append({
                    'vigencia': año.group(),
                    'estado': 'Pendiente de pago',
                    'total_vigencia': int(valor_fila)
                })
            except ValueError:
                pass

    return registros, total

def consultar_itagui(page, placa):
    url = "https://movilidad.transitoitagui.gov.co/portal-servicios/#/impuesto-local"
    page.goto(url, wait_until="domcontentloaded")
    page.get_by_role("textbox", name="Placa").fill(placa)
    page.get_by_role("button", name="Buscar").click()

    page.wait_for_function("""() => {
        const texto = document.body.innerText;
        const noMatriculado = texto.includes('El vehiculo no se encuentra matriculado en la Secretaria de Movilidad');
        const conDeuda = texto.includes('Vigencias pendientes');
        const pazYSalvo = texto.includes('Último pago realizado') && !texto.includes('Vigencias pendientes');
        return noMatriculado || conDeuda || pazYSalvo;
    }""", timeout=20000)

    texto_pagina = page.inner_text("body")

    if MSG_NO_MATRICULADO in texto_pagina:
        return [], 0

    if 'Vigencias pendientes' not in texto_pagina and AÑO_ACTUAL in texto_pagina:
        return [], 0

    page.locator("#tablaCollapseVigencias").wait_for(state="visible", timeout=15000)
    checkbox = page.locator("#selectall")
    checkbox.wait_for(state="visible", timeout=15000)
    if checkbox.is_enabled():
        checkbox.check()

    page.wait_for_timeout(3000)

    spans_cop = page.locator("span.fs-16.ng-binding").all()
    total = 0
    for span in spans_cop[::-1]:
        texto = span.inner_text().strip()
        if "COP" in texto and texto != "COP 0":
            valor_str = texto.replace("COP", "").replace(".", "").strip()
            try:
                total = int(valor_str)
                break
            except ValueError:
                pass

    registros = []
    filas = page.locator("#tablaCollapseVigencias tr").all()
    for fila in filas:
        texto_fila = fila.inner_text().strip()
        if not texto_fila:
            continue
        año = re.search(r'\b(20\d{2})\b', texto_fila)
        montos = re.findall(r'COP\s*[\d.]+', texto_fila)
        if año and montos:
            valor_fila = montos[-1].replace('COP', '').replace(' ', '').replace('.', '')
            try:
                registros.append({
                    'vigencia': año.group(),
                    'estado': 'Pendiente de pago',
                    'total_vigencia': int(valor_fila)
                })
            except ValueError:
                pass

    return registros, total


def consultar_bello(page, placa):
    url = "https://serviciosdigitales.movilidadavanzadabello.com.co/portal-servicios/#/public"
    page.goto(url, wait_until="networkidle", timeout=30000)

    try:
        page.get_by_role("button", name="Close").click(timeout=5000)
    except:
        pass

    page.get_by_role("searchbox", name="Placa").nth(3).fill(placa)
    page.get_by_role("button").nth(5).click()

    try:
        page.wait_for_url("**/impuesto-local", timeout=15000)
    except:
        return [], 0

    page.wait_for_function("""() => {
        const texto = document.body.innerText;
        return texto.includes('Total a pagar') ||
               texto.includes('paz y salvo') ||
               texto.includes('No se encontraron registros');
    }""", timeout=30000)

    texto_pagina = page.inner_text("body")

    if 'paz y salvo' in texto_pagina or 'No se encontraron registros' in texto_pagina:
        return [], 0

    match_total = re.search(r'Total a pagar:\s*COP\s*([\d.]+)', texto_pagina)
    total = int(match_total.group(1).replace('.', '')) if match_total else 0

    registros = []
    tbodies = page.locator("tbody").all()
    for tbody in tbodies[::2]:
        texto = tbody.inner_text().strip()
        if not texto:
            continue
        año = re.search(r'\b(20\d{2})\b', texto)
        montos = re.findall(r'COP\s*[\d.]+', texto)
        if año and montos:
            valor_fila = montos[-1].replace('COP', '').replace(' ', '').replace('.', '')
            try:
                registros.append({
                    'vigencia': año.group(),
                    'estado': 'Pendiente de pago' if 'Pendiente' in texto else 'Desconocido',
                    'total_vigencia': int(valor_fila)
                })
            except ValueError:
                pass

    return registros, total


MUNICIPIOS = {
    "envigado": consultar_envigado,
    "sabaneta": consultar_sabaneta,
    "itagui":   consultar_itagui,
    "bello":    consultar_bello,
}

@app.route("/consultar", methods=["GET"])
def consultar():
    placa     = request.args.get("placa", "").upper().strip()
    municipio = request.args.get("municipio", "").lower().strip()

    if not placa or not municipio:
        return jsonify({"error": "Debes proporcionar placa y municipio."}), 400

    if municipio not in MUNICIPIOS:
        return jsonify({
            "error": f"Municipio '{municipio}' no reconocido.",
            "opciones": list(MUNICIPIOS.keys())
        }), 400

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--single-process",
                    "--no-zygote",
                    "--disable-setuid-sandbox"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            bloquear_recursos(page)

            funcion = MUNICIPIOS[municipio]
            registros, total = funcion(page, placa)

            context.close()
            browser.close()

        return jsonify({
            "placa":     placa,
            "municipio": municipio,
            "registros": registros,
            "total":     total,
            "sin_deuda": total == 0
        })

    except Exception as e:
        error = str(e).lower()
        if any(x in error for x in [
            "net::err_internet_disconnected",
            "net::err_name_not_resolved",
            "net::err_connection_refused",
            "net::err_connection_timed_out",
            "net::err_connection_reset",
            "net::err_aborted",
            "timeout",
            "page.goto"
        ]):
            return jsonify({
                "error": f"No se pudo conectar al portal de {municipio}. Intenta más tarde."
            }), 503
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
