import re
import time
import requests
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TIMEOUT = 10000
MSG_NO_MATRICULADO = "El vehiculo no se encuentra matriculado en la Secretaria de Movilidad"
ANO_ACTUAL = str(datetime.now().year)

TWOCAPTCHA_API_KEY = "47a18b883a00d513b2c78b0ac2cd0f00"

# --- EMTRASUR (La Estrella) ---
EMTRASUR_SITE_KEY = "6Leshn4sAAAAAIas9tkeW3vKPg0a4uYqw-7fG7Pn"
EMTRASUR_URL      = "https://sistematizacion.emtrasur.com.co/"

# --- Antioquia ---
ANTIOQUIA_SITE_KEY = "0x4AAAAAACJy_BR2tRNN1cnv"
ANTIOQUIA_URL      = "https://www.vehiculosantioquia.com.co/impuestosweb/#/public"
ANTIOQUIA_API      = "https://www.vehiculosantioquia.com.co/raiz-backimpuestosweb/backimpuestosweb"


def bloquear_recursos(page):
    page.route("**/*", lambda route: route.abort()
               if route.request.resource_type in ["image", "stylesheet", "font", "media", "other"]
               else route.continue_())


# ─────────────────────────────────────────────
# CAPTCHA SOLVERS
# ─────────────────────────────────────────────

def resolver_recaptcha_2captcha(site_key, page_url):
    resp = requests.post("https://2captcha.com/in.php", data={
        "key":       TWOCAPTCHA_API_KEY,
        "method":    "userrecaptcha",
        "googlekey": site_key,
        "pageurl":   page_url,
        "json":      1,
    }, timeout=15)
    data = resp.json()
    if data.get("status") != 1:
        raise Exception(f"2captcha error al enviar: {data.get('request')}")
    captcha_id = data["request"]
    for _ in range(24):
        time.sleep(5)
        resultado = requests.get("https://2captcha.com/res.php", params={
            "key":    TWOCAPTCHA_API_KEY,
            "action": "get",
            "id":     captcha_id,
            "json":   1,
        }, timeout=10).json()
        if resultado.get("status") == 1:
            return resultado["request"]
        if resultado.get("request") not in ("CAPCHA_NOT_READY", "CAPTCHA_NOT_READY"):
            raise Exception(f"2captcha error: {resultado.get('request')}")
    raise Exception("2captcha tardo demasiado en resolver el captcha.")


def resolver_turnstile_2captcha(site_key, page_url):
    resp = requests.post("https://2captcha.com/in.php", data={
        "key":     TWOCAPTCHA_API_KEY,
        "method":  "turnstile",
        "sitekey": site_key,
        "pageurl": page_url,
        "json":    1,
    }, timeout=15)
    data = resp.json()
    if data.get("status") != 1:
        raise Exception(f"2captcha error al enviar: {data.get('request')}")
    captcha_id = data["request"]
    for _ in range(24):
        time.sleep(5)
        resultado = requests.get("https://2captcha.com/res.php", params={
            "key":    TWOCAPTCHA_API_KEY,
            "action": "get",
            "id":     captcha_id,
            "json":   1,
        }, timeout=10).json()
        if resultado.get("status") == 1:
            return resultado["request"]
        if resultado.get("request") not in ("CAPCHA_NOT_READY", "CAPTCHA_NOT_READY"):
            raise Exception(f"2captcha error: {resultado.get('request')}")
    raise Exception("2captcha tardo demasiado en resolver el captcha.")


# ─────────────────────────────────────────────
# MUNICIPIOS
# ─────────────────────────────────────────────

def consultar_envigado(page, placa, **kwargs):
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
        anno = re.search(r'\b(20\d{2})\b', texto_fila)
        montos = re.findall(r'\$\s*[\d.]+', texto_fila)
        if anno and montos:
            valor_str = montos[-1].replace('$', '').replace(' ', '').replace('.', '')
            try:
                registros.append({'vigencia': anno.group(), 'estado': 'Pendiente de pago', 'total_vigencia': int(valor_str)})
            except ValueError:
                pass
    total = sum(r['total_vigencia'] for r in registros)
    return registros, total


def consultar_sabaneta(page, placa, **kwargs):
    url = "https://transitosabaneta.utsetsa.com/#/impuesto-local"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.locator("#placa").wait_for(state="visible", timeout=15000)
    page.locator("#placa").fill(placa)
    page.get_by_role("button", name="Buscar").click()
    page.wait_for_timeout(20000)
    texto_pagina = page.inner_text("body")
    if MSG_NO_MATRICULADO in texto_pagina:
        return [], 0
    if 'Ultimo pago realizado' in texto_pagina and 'Vigencias pendientes' not in texto_pagina:
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
        anno = re.search(r'\b(20\d{2})\b', texto_fila)
        montos = re.findall(r'COP\s*[\d.]+', texto_fila)
        if anno and montos:
            valor_fila = montos[-1].replace('COP', '').replace(' ', '').replace('.', '')
            try:
                registros.append({'vigencia': anno.group(), 'estado': 'Pendiente de pago', 'total_vigencia': int(valor_fila)})
            except ValueError:
                pass
    return registros, total


def consultar_itagui(page, placa, **kwargs):
    url = "https://movilidad.transitoitagui.gov.co/portal-servicios/#/impuesto-local"
    page.goto(url, wait_until="domcontentloaded")
    page.get_by_role("textbox", name="Placa").fill(placa)
    page.get_by_role("button", name="Buscar").click()
    page.wait_for_function("""() => {
        const texto = document.body.innerText;
        const noMatriculado = texto.includes('El vehiculo no se encuentra matriculado en la Secretaria de Movilidad');
        const conDeuda = texto.includes('Vigencias pendientes');
        const pazYSalvo = texto.includes('Ultimo pago realizado') && !texto.includes('Vigencias pendientes');
        return noMatriculado || conDeuda || pazYSalvo;
    }""", timeout=20000)
    texto_pagina = page.inner_text("body")
    if MSG_NO_MATRICULADO in texto_pagina:
        return [], 0
    if 'Vigencias pendientes' not in texto_pagina and ANO_ACTUAL in texto_pagina:
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
        anno = re.search(r'\b(20\d{2})\b', texto_fila)
        montos = re.findall(r'COP\s*[\d.]+', texto_fila)
        if anno and montos:
            valor_fila = montos[-1].replace('COP', '').replace(' ', '').replace('.', '')
            try:
                registros.append({'vigencia': anno.group(), 'estado': 'Pendiente de pago', 'total_vigencia': int(valor_fila)})
            except ValueError:
                pass
    return registros, total


def consultar_bello(page, placa, **kwargs):
    url = "https://serviciosdigitales.movilidadavanzadabello.com.co/portal-servicios/#/public"
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function("""() => {
        return document.querySelectorAll('input[type="search"]').length > 0;
    }""", timeout=30000)
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
    page.wait_for_timeout(10000)
    texto_pagina = page.inner_text("body")
    if 'paz y salvo' in texto_pagina or 'No se encontraron registros' in texto_pagina:
        return [], 0
    if 'Vigencias pendientes' not in texto_pagina:
        return [], 0
    registros = []
    tbodies = page.locator("tbody").all()
    for tbody in tbodies[::2]:
        texto = tbody.inner_text().strip()
        if not texto:
            continue
        anno = re.search(r'\b(20\d{2})\b', texto)
        montos = re.findall(r'COP\s*[\d.]+', texto)
        if anno and montos:
            valor_fila = montos[-1].replace('COP', '').replace(' ', '').replace('.', '')
            try:
                registros.append({
                    'vigencia': anno.group(),
                    'estado': 'Pendiente de pago' if 'Pendiente' in texto else 'Desconocido',
                    'total_vigencia': int(valor_fila)
                })
            except ValueError:
                pass
    match_total = re.search(r'Total a pagar:\s*COP\s*([\d.]+)', texto_pagina)
    if match_total:
        total = int(match_total.group(1).replace('.', ''))
    else:
        total = sum(r['total_vigencia'] for r in registros)
    return registros, total


def _parsear_emtrasur(data):
    registros = []
    for r in data:
        valor = r.get("ValorPorFacturar", 0)
        registros.append({
            "vigencia":       str(r.get("AnioNoFacturado", "")),
            "estado":         "Pendiente de pago",
            "total_vigencia": valor,
            "tipo_vehiculo":  r.get("TipoVehiculo", ""),
            "ultimo_pago":    r.get("AnioPagado", ""),
            "descripcion":    r.get("DescripcionNoFacturada", "").strip(),
        })
    total = sum(r["total_vigencia"] for r in registros)
    return registros, total


def consultar_laestrella(page, placa, **kwargs):
    token = resolver_recaptcha_2captcha(EMTRASUR_SITE_KEY, EMTRASUR_URL)
    api_url = f"https://sistematizacion.emtrasur.com.co/api/Sistematizacion/{placa}"
    resp = requests.get(api_url, headers={
        "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept":          "application/json, text/plain, */*",
        "Referer":         EMTRASUR_URL,
        "Origin":          "https://sistematizacion.emtrasur.com.co",
        "X-Captcha-Token": token,
    }, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("Success"):
            return _parsear_emtrasur(data.get("Data", []))
    raise Exception(f"EMTRASUR respondio {resp.status_code}: {resp.text[:200]}")


def consultar_antioquia(page, placa, identificacion="", tipo_documento="1",
                        modelo="", municipio_transito="", nombre_propietario="", **kwargs):
    """
    Retorna (registros, total, avaluo) para un vehiculo en el portal de Antioquia.

    Parametros requeridos ademas de placa:
        identificacion      : Numero de cedula del propietario
        tipo_documento      : "1" = Cedula (default)
        modelo              : Anio del modelo (ej: "2010")
        municipio_transito  : Municipio de matricula (ej: "ENVIGADO")
        nombre_propietario  : Nombre completo (ej: "GERMAN ALEXIS RUIZ ARROYAVE")
    """

    # Paso 1: resolver Turnstile
    token_captcha = resolver_turnstile_2captcha(ANTIOQUIA_SITE_KEY, ANTIOQUIA_URL)

    session = requests.Session()
    session.headers.update({
        "Accept":           "*/*",
        "Content-Type":     "application/json",
        "captcha":          token_captcha,
        "Referer":          "https://www.vehiculosantioquia.com.co/impuestosweb/",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent":       "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
    })

    # Paso 2: obtener cuestionario
    r1 = session.post(
        f"{ANTIOQUIA_API}/ConsultarEstadoCuentaImpAntioquia/obtenerCuestionarioEstadoCuenta",
        json={
            "placa":                placa,
            "idTipoIdentificacion": tipo_documento,
            "identificacion":       identificacion,
        },
        timeout=30
    )
    if r1.status_code != 200:
        raise Exception(f"Error obteniendo cuestionario: {r1.status_code} - {r1.text[:200]}")

    data1 = r1.json()
    if data1.get("estadoService", {}).get("codigoEstado") != 1:
        raise Exception(f"Vehiculo no encontrado o error en consulta.")

    id_estado_cuenta = data1.get("referencia")

    # Paso 3: validar cuestionario con datos del usuario
    r2 = session.post(
        f"{ANTIOQUIA_API}/ConsultarEstadoCuentaImpAntioquia/validarCuestionarioEstadoCuenta",
        json={
            "placa":           placa,
            "tipoDocumento":   tipo_documento,
            "numeroDocumento": identificacion,
            "idEstadoCuenta":  id_estado_cuenta,
            "respuestas": {
                "respuestaModelo":            modelo,
                "respuestaOrganismoTransito": municipio_transito,
                "respuestaNombrePropietario": nombre_propietario,
            }
        },
        timeout=30
    )
    if r2.status_code != 200:
        raise Exception(f"Error validando cuestionario: {r2.status_code} - {r2.text[:200]}")

    data2 = r2.json()
    if data2.get("codigo") != 1:
        raise Exception("Cuestionario incorrecto. Verifica modelo, municipio y nombre del propietario.")

    # Paso 4: obtener estado de cuenta (cookie token ya esta en la sesion)
    r3 = session.get(
        f"{ANTIOQUIA_API}/ConsultarEstadoCuentaImpAntioquia/consultarEstadoCuentaVehiculoHomePublico",
        timeout=30
    )
    if r3.status_code != 200:
        raise Exception(f"Error consultando estado de cuenta: {r3.status_code} - {r3.text[:200]}")

    data3 = r3.json()
    estado_cuenta = data3.get("estadoCuenta", {})
    lista_pagos   = estado_cuenta.get("listaDetallePagos", [])
    lista_vigencias = estado_cuenta.get("listVigenciasAdeudadas", [])

    # Avaluo del pago mas reciente
    avaluo = 0
    if lista_pagos:
        ultimo = sorted(lista_pagos, key=lambda x: x.get("vigencia", 0), reverse=True)[0]
        try:
            avaluo = int(str(ultimo.get("avaluo", 0)).replace(".", "").replace(",", "").replace("$", "").strip())
        except ValueError:
            pass

    # Vigencias adeudadas
    registros = []
    for v in lista_vigencias:
        registros.append({
            "vigencia":       str(v.get("vigencia", "")),
            "estado":         "Pendiente de pago",
            "total_vigencia": v.get("totalVigencia", 0),
        })

    total = sum(r["total_vigencia"] for r in registros)
    return registros, total, avaluo


# ─────────────────────────────────────────────
# ROUTING
# ─────────────────────────────────────────────

MUNICIPIOS = {
    "envigado":    consultar_envigado,
    "sabaneta":    consultar_sabaneta,
    "itagui":      consultar_itagui,
    "bello":       consultar_bello,
    "laestrella":  consultar_laestrella,
    "la estrella": consultar_laestrella,
    "antioquia":   consultar_antioquia,
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

    kwargs = {}
    if municipio == "antioquia":
        identificacion     = request.args.get("identificacion", "").strip()
        tipo_documento     = request.args.get("tipo_documento", "1").strip()
        modelo             = request.args.get("modelo", "").strip()
        municipio_transito = request.args.get("municipio_transito", "").upper().strip()
        nombre_propietario = request.args.get("nombre_propietario", "").upper().strip()

        if not identificacion or not modelo or not municipio_transito or not nombre_propietario:
            return jsonify({
                "error": "Para Antioquia debes proporcionar: identificacion, modelo, municipio_transito, nombre_propietario."
            }), 400

        kwargs = {
            "identificacion":     identificacion,
            "tipo_documento":     tipo_documento,
            "modelo":             modelo,
            "municipio_transito": municipio_transito,
            "nombre_propietario": nombre_propietario,
        }

    resultado = {}
    error_container = {}

    def ejecutar():
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

                if municipio not in ["bello", "sabaneta", "laestrella", "antioquia"]:
                    bloquear_recursos(page)

                funcion = MUNICIPIOS[municipio]
                retorno = funcion(page, placa, **kwargs)

                context.close()
                browser.close()

                if municipio == "antioquia":
                    resultado['registros'] = retorno[0]
                    resultado['total']     = retorno[1]
                    resultado['avaluo']    = retorno[2]
                else:
                    resultado['registros'] = retorno[0]
                    resultado['total']     = retorno[1]

        except Exception as e:
            error_container['error'] = str(e)

    hilo = threading.Thread(target=ejecutar)
    hilo.start()
    hilo.join(timeout=180)

    if hilo.is_alive():
        return jsonify({"error": "La consulta tardo demasiado. Intenta de nuevo."}), 504

    if error_container:
        error = error_container['error'].lower()
        if any(x in error for x in [
            "net::err_internet_disconnected",
            "net::err_name_not_resolved",
            "net::err_connection_refused",
            "net::err_connection_timed_out",
            "net::err_connection_reset",
            "net::err_aborted",
        ]):
            return jsonify({"error": f"No se pudo conectar al portal de {municipio}. Intenta mas tarde."}), 503
        return jsonify({"error": error_container['error']}), 500

    response = {
        "placa":     placa,
        "municipio": municipio,
        "registros": resultado.get('registros', []),
        "total":     resultado.get('total', 0),
        "sin_deuda": resultado.get('total', 0) == 0,
    }
    if municipio == "antioquia":
        response["avaluo"] = resultado.get('avaluo', 0)

    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
