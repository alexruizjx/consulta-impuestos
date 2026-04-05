import re
from datetime import datetime
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

TIMEOUT = 30000
MSG_NO_MATRICULADO = "El vehiculo no se encuentra matriculado en la Secretaria de Movilidad"
AÑO_ACTUAL = str(datetime.now().year)

def bloquear_recursos(page):
    page.route("**/*", lambda route: route.abort()
               if route.request.resource_type in ["image", "font", "media"]
               else route.continue_())

# =========================
# ENVIGADO
# =========================
def consultar_envigado(page, placa):
    page.goto("https://movilidad.envigado.gov.co/portal-servicios/#/impuesto-local",
              wait_until="domcontentloaded")

    page.get_by_role("textbox", name="Placa").fill(placa)
    page.get_by_role("button", name="Buscar").click()

    page.wait_for_function("""() => {
        return document.querySelector('#tablaCollapseVigencias') ||
               document.body.innerText.includes('no se encuentra matriculado');
    }""", timeout=TIMEOUT)

    if MSG_NO_MATRICULADO in page.inner_text("body"):
        return [], 0

    registros = []
    filas = page.locator("#tablaCollapseVigencias tr").all()

    for fila in filas:
        texto = fila.inner_text()
        año = re.search(r'\b(20\d{2})\b', texto)
        montos = re.findall(r'\$\s*[\d.]+', texto)

        if año and montos:
            valor = int(montos[-1].replace("$", "").replace(".", "").strip())
            registros.append({
                "vigencia": año.group(),
                "estado": "Pendiente",
                "total_vigencia": valor
            })

    total = sum(r["total_vigencia"] for r in registros)
    return registros, total


# =========================
# SABANETA (CORREGIDO)
# =========================
def consultar_sabaneta(page, placa):
    page.goto("https://transitosabaneta.utsetsa.com/#/impuesto-local",
              wait_until="domcontentloaded")

    page.locator("#placa").fill(placa)
    page.get_by_role("button", name="Buscar").click()

    page.wait_for_function("""() => {
        const t = document.body.innerText;
        return t.includes('Vigencias pendientes') ||
               t.includes('Último pago realizado') ||
               t.includes('no se encuentra matriculado');
    }""", timeout=TIMEOUT)

    texto = page.inner_text("body")

    if MSG_NO_MATRICULADO in texto:
        return [], 0

    if "Vigencias pendientes" not in texto:
        return [], 0

    registros = []
    filas = page.locator("#tablaCollapseVigencias tr").all()

    for fila in filas:
        texto_fila = fila.inner_text()
        año = re.search(r'\b(20\d{2})\b', texto_fila)
        montos = re.findall(r'COP\s*[\d.]+', texto_fila)

        if año and montos:
            valor = int(montos[-1].replace("COP", "").replace(".", "").strip())
            registros.append({
                "vigencia": año.group(),
                "estado": "Pendiente",
                "total_vigencia": valor
            })

    total = sum(r["total_vigencia"] for r in registros)
    return registros, total


# =========================
# ITAGUI
# =========================
def consultar_itagui(page, placa):
    page.goto("https://movilidad.transitoitagui.gov.co/portal-servicios/#/impuesto-local",
              wait_until="domcontentloaded")

    page.get_by_role("textbox", name="Placa").fill(placa)
    page.get_by_role("button", name="Buscar").click()

    page.wait_for_function("""() => {
        const t = document.body.innerText;
        return t.includes('Vigencias pendientes') ||
               t.includes('Último pago realizado') ||
               t.includes('no se encuentra matriculado');
    }""", timeout=TIMEOUT)

    texto = page.inner_text("body")

    if MSG_NO_MATRICULADO in texto:
        return [], 0

    if "Vigencias pendientes" not in texto:
        return [], 0

    registros = []
    filas = page.locator("#tablaCollapseVigencias tr").all()

    for fila in filas:
        texto_fila = fila.inner_text()
        año = re.search(r'\b(20\d{2})\b', texto_fila)
        montos = re.findall(r'COP\s*[\d.]+', texto_fila)

        if año and montos:
            valor = int(montos[-1].replace("COP", "").replace(".", "").strip())
            registros.append({
                "vigencia": año.group(),
                "estado": "Pendiente",
                "total_vigencia": valor
            })

    total = sum(r["total_vigencia"] for r in registros)
    return registros, total


# =========================
# BELLO (CORREGIDO)
# =========================
def consultar_bello(page, placa):
    page.goto("https://serviciosdigitales.movilidadavanzadabello.com.co/portal-servicios/#/public",
              wait_until="domcontentloaded")

    try:
        page.get_by_role("button", name="Close").click(timeout=3000)
    except:
        pass

    page.locator("input[placeholder*='Placa']").first.fill(placa)
    page.locator("button:has-text('Buscar')").click()

    page.wait_for_function("""() => {
        const t = document.body.innerText;
        return t.includes('Total a pagar') ||
               t.includes('paz y salvo') ||
               t.includes('No se encontraron registros');
    }""", timeout=TIMEOUT)

    texto = page.inner_text("body")

    if "paz y salvo" in texto or "No se encontraron registros" in texto:
        return [], 0

    match = re.search(r'COP\s*([\d.]+)', texto)
    total = int(match.group(1).replace(".", "")) if match else 0

    registros = []
    tbodies = page.locator("tbody").all()

    for tbody in tbodies:
        texto_fila = tbody.inner_text()
        año = re.search(r'\b(20\d{2})\b', texto_fila)
        montos = re.findall(r'COP\s*[\d.]+', texto_fila)

        if año and montos:
            valor = int(montos[-1].replace("COP", "").replace(".", "").strip())
            registros.append({
                "vigencia": año.group(),
                "estado": "Pendiente",
                "total_vigencia": valor
            })

    return registros, total


MUNICIPIOS = {
    "envigado": consultar_envigado,
    "sabaneta": consultar_sabaneta,
    "itagui": consultar_itagui,
    "bello": consultar_bello,
}


@app.route("/consultar", methods=["GET"])
def consultar():
    placa = request.args.get("placa", "").upper().strip()
    municipio = request.args.get("municipio", "").lower().strip()

    if municipio not in MUNICIPIOS:
        return jsonify({"error": "Municipio no válido"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )

            context = browser.new_context()
            page = context.new_page()

            page.set_default_timeout(TIMEOUT)
            bloquear_recursos(page)

            registros, total = MUNICIPIOS[municipio](page, placa)

            browser.close()

        return jsonify({
            "placa": placa,
            "municipio": municipio,
            "registros": registros,
            "total": total,
            "sin_deuda": total == 0
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run()
