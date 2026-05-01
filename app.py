import base64, re, io
from PIL import Image
import pytesseract
import os
import psycopg2
import re
import time
import requests
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

TIMEOUT = 10000
MSG_NO_MATRICULADO = "El vehiculo no se encuentra matriculado en la Secretaria de Movilidad"
AÑO_ACTUAL = str(datetime.now().year)

TWOCAPTCHA_API_KEY = "47a18b883a00d513b2c78b0ac2cd0f00"
EMTRASUR_SITE_KEY  = "6Leshn4sAAAAAIas9tkeW3vKPg0a4uYqw-7fG7Pn"
EMTRASUR_URL       = "https://sistematizacion.emtrasur.com.co/"
ANTIOQUIA_SITE_KEY = "0x4AAAAAACJy_BR2tRNN1cnv"
ANTIOQUIA_URL      = "https://www.vehiculosantioquia.com.co/impuestosweb/#/public"
ANTIOQUIA_API      = "https://www.vehiculosantioquia.com.co/raiz-backimpuestosweb/backimpuestosweb"

# ============================================================
#  TABLA DE TIPOS DE DOCUMENTO ANTIOQUIA
# ============================================================
ANTIOQUIA_TIPOS_DOCUMENTO = {
    "1":  {"abreviatura": "CC",    "nombre": "Cédula de Ciudadanía"},
    "8":  {"abreviatura": "CD",    "nombre": "Carnet Diplomático"},
    "5":  {"abreviatura": "CE",    "nombre": "Cédula de Extranjería"},
    "2":  {"abreviatura": "NIT",   "nombre": "NIT"},
    "4":  {"abreviatura": "PASAP", "nombre": "Pasaporte"},
    "29": {"abreviatura": "PPT",   "nombre": "Permiso por protección temporal"},
    "7":  {"abreviatura": "RC",    "nombre": "Registro Civil"},
    "6":  {"abreviatura": "TI",    "nombre": "Tarjeta de Identidad"},
}

# Mapa de abreviatura entrante → id numérico
ANTIOQUIA_TIPO_DOC_MAP = {
    "CC": "1", "NIT": "2", "PASAP": "4", "CE": "5",
    "TI": "6", "RC": "7", "CD": "8", "PPT": "29"
}

ANTIOQUIA_LIMITE_VIGENCIAS = 10


def get_db_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])


def bloquear_recursos(page):
    page.route("**/*", lambda route: route.abort()
               if route.request.resource_type in ["image", "stylesheet", "font", "media", "other"]
               else route.continue_())


def resolver_recaptcha_2captcha(site_key, page_url):
    resp = requests.post("https://2captcha.com/in.php", data={
        "key": TWOCAPTCHA_API_KEY, "method": "userrecaptcha",
        "googlekey": site_key, "pageurl": page_url, "json": 1,
    }, timeout=15)
    data = resp.json()
    if data.get("status") != 1:
        raise Exception(f"2captcha error: {data.get('request')}")
    captcha_id = data["request"]
    for _ in range(24):
        time.sleep(5)
        resultado = requests.get("https://2captcha.com/res.php", params={
            "key": TWOCAPTCHA_API_KEY, "action": "get", "id": captcha_id, "json": 1,
        }, timeout=10).json()
        if resultado.get("status") == 1:
            return resultado["request"]
        if resultado.get("request") not in ("CAPCHA_NOT_READY", "CAPTCHA_NOT_READY"):
            raise Exception(f"2captcha error: {resultado.get('request')}")
    raise Exception("2captcha tardo demasiado.")


def resolver_turnstile_2captcha(site_key, page_url):
    resp = requests.post("https://2captcha.com/in.php", data={
        "key": TWOCAPTCHA_API_KEY, "method": "turnstile",
        "sitekey": site_key, "pageurl": page_url, "json": 1,
    }, timeout=15)
    data = resp.json()
    if data.get("status") != 1:
        raise Exception(f"2captcha error: {data.get('request')}")
    captcha_id = data["request"]
    for _ in range(24):
        time.sleep(5)
        resultado = requests.get("https://2captcha.com/res.php", params={
            "key": TWOCAPTCHA_API_KEY, "action": "get", "id": captcha_id, "json": 1,
        }, timeout=10).json()
        if resultado.get("status") == 1:
            return resultado["request"]
        if resultado.get("request") not in ("CAPCHA_NOT_READY", "CAPTCHA_NOT_READY"):
            raise Exception(f"2captcha error: {resultado.get('request')}")
    raise Exception("2captcha tardo demasiado.")


# ============================================================
#  MUNICIPIOS (sin tocar)
# ============================================================
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
                registros.append({'vigencia': año.group(), 'estado': 'Pendiente de pago', 'total_vigencia': int(valor_str)})
            except ValueError:
                pass
    total = sum(r['total_vigencia'] for r in registros)
    return registros, total


def consultar_sabaneta(page, placa):
    url = "https://transitosabaneta.utsetsa.com/#/impuesto-local"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.locator("#placa").wait_for(state="visible", timeout=15000)
    page.locator("#placa").fill(placa)
    page.get_by_role("button", name="Buscar").click()
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
                registros.append({'vigencia': año.group(), 'estado': 'Pendiente de pago', 'total_vigencia': int(valor_fila)})
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
                registros.append({'vigencia': año.group(), 'estado': 'Pendiente de pago', 'total_vigencia': int(valor_fila)})
            except ValueError:
                pass
    return registros, total


def consultar_bello(page, placa):
    url = "https://serviciosdigitales.movilidadavanzadabello.com.co/portal-servicios/#/public"
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function("""() => { return document.querySelectorAll('input[type="search"]').length > 0; }""", timeout=30000)
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
        año = re.search(r'\b(20\d{2})\b', texto)
        montos = re.findall(r'COP\s*[\d.]+', texto)
        if año and montos:
            valor_fila = montos[-1].replace('COP', '').replace(' ', '').replace('.', '')
            try:
                registros.append({'vigencia': año.group(), 'estado': 'Pendiente de pago' if 'Pendiente' in texto else 'Desconocido', 'total_vigencia': int(valor_fila)})
            except ValueError:
                pass
    match_total = re.search(r'Total a pagar:\s*COP\s*([\d.]+)', texto_pagina)
    total = int(match_total.group(1).replace('.', '')) if match_total else sum(r['total_vigencia'] for r in registros)
    return registros, total


def _parsear_emtrasur(data):
    registros = []
    for r in data:
        registros.append({
            "vigencia": str(r.get("AnioNoFacturado", "")),
            "estado": "Pendiente de pago",
            "total_vigencia": r.get("ValorPorFacturar", 0),
            "tipo_vehiculo": r.get("TipoVehiculo", ""),
            "ultimo_pago": r.get("AnioPagado", ""),
            "descripcion": r.get("DescripcionNoFacturada", "").strip(),
        })
    total = sum(r["total_vigencia"] for r in registros)
    return registros, total


def consultar_laestrella(page, placa):
    token = resolver_recaptcha_2captcha(EMTRASUR_SITE_KEY, EMTRASUR_URL)
    api_url = f"https://sistematizacion.emtrasur.com.co/api/Sistematizacion/{placa}"
    resp = requests.get(api_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": EMTRASUR_URL,
        "Origin": "https://sistematizacion.emtrasur.com.co",
        "X-Captcha-Token": token,
    }, timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("Success"):
            return _parsear_emtrasur(data.get("Data", []))
    raise Exception(f"EMTRASUR respondio {resp.status_code}: {resp.text[:200]}")


# ============================================================
#  ANTIOQUIA — MÓDULO NUEVO
# ============================================================
def _calcular_digito_nit(nit):
    """Calcula el dígito de verificación de un NIT colombiano (algoritmo DIAN)."""
    factores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43]
    n = str(nit).strip().replace("-", "").replace(".", "").zfill(10)
    suma = sum(int(n[::-1][i]) * factores[i] for i in range(10))
    r = suma % 11
    return 0 if r == 0 else (1 if r == 1 else 11 - r)


def _sesion_antioquia(placa, identificacion, tipo_documento_id,
                      modelo, organismo_transito, apellidos_propietario):
    """
    Abre sesión completa en Antioquia y retorna (session, token_cuestionario, data3).
    Costo: 2 Turnstiles.
    """
    try:
        token_captcha = resolver_turnstile_2captcha(ANTIOQUIA_SITE_KEY, ANTIOQUIA_URL)
    except Exception as e:
        raise Exception(f"Error resolviendo captcha inicial: {e}")

    session = requests.Session()
    session.headers.update({
        "Accept": "*/*",
        "Content-Type": "application/json",
        "captcha": token_captcha,
        "Referer": "https://www.vehiculosantioquia.com.co/impuestosweb/",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
    })

    r1 = session.post(
        f"{ANTIOQUIA_API}/ConsultarEstadoCuentaImpAntioquia/obtenerCuestionarioEstadoCuenta",
        json={"placa": placa, "idTipoIdentificacion": tipo_documento_id, "identificacion": identificacion},
        timeout=60
    )
    data1 = r1.json()
    referencia = data1.get("referencia")

    opciones_nombre = data1.get("preguntaNombrePropietario", {}).get("opcionesPregunta", [])
    nombre_encontrado = next(
        (n for n in opciones_nombre if apellidos_propietario.upper() in n.upper()), None
    )
    if not nombre_encontrado:
        raise Exception(f"No se encontró propietario con apellidos '{apellidos_propietario}'. Opciones: {opciones_nombre}")

    r2 = session.post(
        f"{ANTIOQUIA_API}/ConsultarEstadoCuentaImpAntioquia/validarCuestionarioEstadoCuenta",
        json={
            "placa": placa, "tipoDocumento": tipo_documento_id, "numeroDocumento": identificacion,
            "idEstadoCuenta": referencia,
            "respuestas": {
                "respuestaModelo": modelo,
                "respuestaOrganismoTransito": organismo_transito,
                "respuestaNombrePropietario": nombre_encontrado
            }
        },
        timeout=60
    )
    validacion = r2.json()
    if validacion.get("codigo") != 1:
        raise Exception(f"Cuestionario inválido: {validacion.get('descripcion')}")

    try:
        token_captcha2 = resolver_turnstile_2captcha(ANTIOQUIA_SITE_KEY, ANTIOQUIA_URL)
    except Exception as e:
        raise Exception(f"Error resolviendo segundo captcha: {e}")
    session.headers.update({"captcha": token_captcha2})

    token_cuestionario = session.cookies.get("token_cuestionario")
    if not token_cuestionario:
        raise Exception("No se pudo obtener el token de sesión.")

    r3 = session.post(
        f"{ANTIOQUIA_API}/ConsultarEstadoCuentaImpAntioquia/consultarEstadoCuentaVehiculoHomePublico",
        json={"placa": placa, "informacionDeclarante": {
            "idsolicitante": identificacion, "idTipoIdentificacion": tipo_documento_id
        }},
        headers={"Cookie": f"token_cuestionario={token_cuestionario}"},
        timeout=60
    )
    return session, token_cuestionario, r3.json()


def _consultar_vigencia_antioquia(vigencia, session, token_cuestionario,
                                   placa, identificacion, tipo_documento_id,
                                   doc_abreviatura, doc_nombre,
                                   celular, email, direccion, municipio, municipio_cod, departamento_cod):
    """
    Consulta el costo de una vigencia específica.
    Costo: 2 Turnstiles adicionales.
    """
    try:
        token_prop = resolver_turnstile_2captcha(ANTIOQUIA_SITE_KEY, ANTIOQUIA_URL)
    except Exception as e:
        raise Exception(f"Error resolviendo captcha vigencia {vigencia}: {e}")
    session.headers.update({"captcha": token_prop})

    r4 = session.post(
        f"{ANTIOQUIA_API}/UsuariosPortalAntioquia/consultarPropietarioVehiculo",
        json={"tipoDoc": doc_abreviatura, "nroDoc": identificacion, "placa": placa, "vigencia": vigencia},
        headers={"Cookie": f"token_cuestionario={token_cuestionario}"},
        timeout=60
    )
    propietario = r4.json().get("propietario", {})

    session.post(f"{ANTIOQUIA_API}/TablasTipo/obtenerTablasPropietario", json={},
                 headers={"Cookie": f"token_cuestionario={token_cuestionario}"}, timeout=60)
    session.get(f"{ANTIOQUIA_API}/UtilImpuestos/obtenerDescripcionPPST",
                headers={"Cookie": f"token_cuestionario={token_cuestionario}"}, timeout=60)
    session.post(f"{ANTIOQUIA_API}/Pagos/parametrosPago", json={},
                 headers={"Cookie": f"token_cuestionario={token_cuestionario}"}, timeout=60)
    session.get(f"{ANTIOQUIA_API}/UtilImpuestos/obtenerVigenciaMinimaAutodeclarar",
                headers={"Cookie": f"token_cuestionario={token_cuestionario}"}, timeout=60)

    try:
        token_decl = resolver_turnstile_2captcha(ANTIOQUIA_SITE_KEY, ANTIOQUIA_URL)
    except Exception as e:
        raise Exception(f"Error resolviendo captcha declaración vigencia {vigencia}: {e}")
    session.headers.update({"captcha": token_decl})
    session.cookies.clear()

    es_nit = (str(tipo_documento_id) == "2")
    if es_nit:
        declarante = {
            "idsolicitante": identificacion,
            "idtipodocumento": doc_abreviatura,
            "desctipodocument": doc_nombre,
            "nombres": propietario.get("nameOrg1", ""),
            "apellidos": "",
            "celular": celular,
            "telefono": propietario.get("celphone", celular),
            "email": email,
            "direccion": direccion, "municipio": municipio,
            "departamento": "ANTIOQUIA", "nivreclamacion": 0, "procedimiento": ""
        }
    else:
        declarante = {
            "idsolicitante": identificacion,
            "idtipodocumento": doc_abreviatura,
            "desctipodocument": doc_nombre,
            "nombres": propietario.get("nameFirst", ""),
            "apellidos": propietario.get("nameLast", ""),
            "celular": celular, "telefono": celular, "email": email,
            "direccion": direccion, "municipio": municipio,
            "departamento": "ANTIOQUIA", "nivreclamacion": 0, "procedimiento": ""
        }

    r5 = session.post(
        f"{ANTIOQUIA_API}/LiquidacionAntioquia/crearDeclaracionImpuestoAnt",
        json={
            "formularioLiquidacion": "",
            "declarante": declarante,
            "iIdliqIm": 0,
            "informacionComplementaria": {
                "idTipoDocumento": int(tipo_documento_id),
                "distribucionDepartamento": departamento_cod,
                "distribucionMunicipio": municipio_cod,
                "direccionCompleta": direccion,
                "nombreDistribucionDepartamento": "ANTIOQUIA",
                "nombreDistribucionMunicipio": municipio,
                "tipoCanalLiquidacion": 2, "tipoOpcionLiquidacion": 1
            },
            "placa": placa,
            "vigencia": [{"persl": vigencia}]
        },
        timeout=60
    )
    return r5.json()


def consultar_antioquia(page, placa, identificacion, tipo_documento_abrev,
                        modelo, municipio_transito, apellidos_propietario,
                        celular="3000000000", email="consulta@consulta.com",
                        direccion="CRA", municipio="MEDELLIN",
                        municipio_cod=5001000, departamento_cod=5):
    """
    Proceso completo para Antioquia.
    Retorna (registros, total, avaluo, estado_vehiculo, excede_limite).
    """
    LIMITE = ANTIOQUIA_LIMITE_VIGENCIAS

    # Resolver tipo de documento
    tipo_documento_id = ANTIOQUIA_TIPO_DOC_MAP.get(tipo_documento_abrev.upper(), "1")
    tipo_doc_info     = ANTIOQUIA_TIPOS_DOCUMENTO.get(tipo_documento_id, ANTIOQUIA_TIPOS_DOCUMENTO["1"])
    doc_abreviatura   = tipo_doc_info["abreviatura"]
    doc_nombre        = tipo_doc_info["nombre"]

    # Si es NIT, calcular y agregar dígito de verificación
    if tipo_documento_id == "2":
        identificacion = str(identificacion) + str(_calcular_digito_nit(identificacion))

    print(f"\n  → Consultando primer bloque de datos ({placa})...")
    session0, token0, data3 = _sesion_antioquia(
        placa, identificacion, tipo_documento_id,
        modelo, municipio_transito, apellidos_propietario
    )

    estado_veh          = data3.get("estadoCuenta", {})
    vigencias_adeudadas = data3.get("listaVigenciasAdeudas", [])
    avaluo              = estado_veh.get("avaluoComercial", 0) or 0
    print(f"  → Vigencias adeudadas encontradas: {len(vigencias_adeudadas)}")

    # Paz y salvo
    if not vigencias_adeudadas:
        return [], 0, avaluo, estado_veh, False

    total_vigencias       = len(vigencias_adeudadas)
    vigencias_a_consultar = sorted(vigencias_adeudadas, key=lambda x: x["vigencia"], reverse=True)
    excede_limite         = total_vigencias > LIMITE
    if excede_limite:
        vigencias_a_consultar = vigencias_a_consultar[:LIMITE]

    registros         = []
    total_suma        = 0
    avaluo_actual     = 0
    retefuente_actual = 0
    MAX_INTENTOS      = 2

    for v in vigencias_a_consultar:
        anio = v.get("vigencia")
        print(f"\n  → Consultando vigencia {anio}...")

        total_pagar  = None
        avaluo_vig   = 0

        for intento in range(1, MAX_INTENTOS + 1):
            if intento > 1:
                print(f"  ↺ Reintentando vigencia {anio}...")
            try:
                session_v, token_v, _ = _sesion_antioquia(
                    placa, identificacion, tipo_documento_id,
                    modelo, municipio_transito, apellidos_propietario
                )
                data_vig = _consultar_vigencia_antioquia(
                    anio, session_v, token_v,
                    placa, identificacion, tipo_documento_id,
                    doc_abreviatura, doc_nombre,
                    celular, email, direccion, municipio, municipio_cod, departamento_cod
                )
                # Mostrar error del servidor si lo hay
                _msg    = data_vig.get("mensaje") or data_vig.get("descripcion")
                _codigo = data_vig.get("codigo")
                if _codigo and _codigo != 1 and _msg:
                    print(f"  ✖ Error servidor vigencia {anio}: {_msg}")

                total_pagar = data_vig.get("totalPagar")
                avaluo_vig  = data_vig.get("avaluoComercial", 0) or 0
                if total_pagar is not None:
                    print(f"  ✔ Vigencia {anio}: ${total_pagar:,}")
                    break
            except Exception as e:
                print(f"  ✖ Error vigencia {anio} intento {intento}: {e}")

        if not avaluo_actual and avaluo_vig:
            avaluo_actual     = avaluo_vig
            retefuente_actual = round(avaluo_vig / 100)

        if total_pagar is not None:
            total_suma += total_pagar

        registros.append({
            "vigencia":       str(anio),
            "estado":         "Pendiente de pago",
            "total_vigencia": total_pagar,
        })

    print(f"\n  ✔ ¡Consulta Antioquia finalizada!")
    return registros, total_suma, avaluo_actual or avaluo, estado_veh, excede_limite


# ============================================================
#  MAPA DE MUNICIPIOS
# ============================================================
MUNICIPIOS = {
    "envigado":    consultar_envigado,
    "sabaneta":    consultar_sabaneta,
    "itagui":      consultar_itagui,
    "bello":       consultar_bello,
    "laestrella":  consultar_laestrella,
    "la estrella": consultar_laestrella,
}


@app.route("/consultar", methods=["GET"])
def consultar():
    import traceback
    placa     = request.args.get("placa", "").upper().strip()
    municipio = request.args.get("municipio", "").lower().strip()
    if not placa or not municipio:
        return jsonify({"error": "Debes proporcionar placa y municipio."}), 400
    if municipio not in MUNICIPIOS and municipio != "antioquia":
        return jsonify({"error": f"Municipio '{municipio}' no reconocido.", "opciones": list(MUNICIPIOS.keys()) + ["antioquia"]}), 400

    identificacion     = request.args.get("identificacion", "").strip()
    tipo_documento     = request.args.get("tipo_documento", "CC").strip().upper() or "CC"
    modelo             = request.args.get("modelo", "").strip()
    municipio_transito = request.args.get("municipio_transito", "").upper().strip()
    apellidos          = request.args.get("apellidos_propietario", "").upper().strip()
    celular            = request.args.get("celular", "3000000000").strip()
    email              = request.args.get("email", "consulta@consulta.com").strip()
    direccion          = request.args.get("direccion", "CRA").strip()
    mun_declarante     = request.args.get("municipio_declarante", "MEDELLIN").strip().upper()
    municipio_cod      = int(request.args.get("municipio_cod", 5001000))
    departamento_cod   = int(request.args.get("departamento_cod", 5))

    if municipio == "antioquia":
        if not identificacion or not modelo or not municipio_transito or not apellidos:
            return jsonify({"error": "Para Antioquia debes proporcionar: identificacion, modelo, municipio_transito, apellidos_propietario."}), 400

    resultado       = {}
    error_container = {}

    def ejecutar():
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True, args=[
                    "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                    "--single-process", "--no-zygote", "--disable-setuid-sandbox"
                ])
                context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                page = context.new_page()

                if municipio == "antioquia":
                    registros, total, avaluo, estado_veh, excede = consultar_antioquia(
                        page, placa, identificacion, tipo_documento,
                        modelo, municipio_transito, apellidos,
                        celular, email, direccion, mun_declarante,
                        municipio_cod, departamento_cod
                    )
                    resultado['registros']  = registros
                    resultado['total']      = total
                    resultado['avaluo']     = avaluo
                    resultado['excede']     = excede
                    resultado['retefuente'] = round(avaluo / 100) if avaluo else 0
                    resultado['placa_info'] = {
                        "marca":       estado_veh.get("marca", ""),
                        "linea":       estado_veh.get("linea", ""),
                        "modelo":      estado_veh.get("modelo", ""),
                        "propietario": estado_veh.get("nombrePropietario", ""),
                    }
                else:
                    if municipio not in ["bello", "sabaneta", "laestrella"]:
                        bloquear_recursos(page)
                    funcion = MUNICIPIOS[municipio]
                    registros, total = funcion(page, placa)
                    resultado['registros'] = registros
                    resultado['total']     = total

                context.close()
                browser.close()
        except Exception as e:
            error_container['error'] = str(e)
            print(traceback.format_exc(), flush=True)

    hilo = threading.Thread(target=ejecutar)
    hilo.start()
    hilo.join(timeout=620)

    if hilo.is_alive():
        return jsonify({"error": "La consulta tardo demasiado. Intenta de nuevo."}), 504

    if error_container:
        error = error_container['error'].lower()
        if any(x in error for x in ["net::err_internet_disconnected", "net::err_name_not_resolved",
                                     "net::err_connection_refused", "net::err_connection_timed_out",
                                     "net::err_connection_reset", "net::err_aborted"]):
            return jsonify({"error": f"No se pudo conectar al portal de {municipio}. Intenta mas tarde."}), 503
        return jsonify({"error": error_container['error']}), 500

    if municipio != "antioquia":
        return jsonify({
            "placa":     placa,
            "municipio": municipio,
            "registros": resultado.get('registros', []),
            "total":     resultado.get('total', 0),
            "sin_deuda": resultado.get('total', 0) == 0
        })

    excede    = resultado.get('excede', False)
    registros = resultado.get('registros', [])
    total     = resultado.get('total', 0)
    respuesta = {
        "placa":      placa,
        "municipio":  "antioquia",
        "placa_info": resultado.get('placa_info', {}),
        "registros":  registros,
        "total":      total,
        "avaluo":     resultado.get('avaluo', 0),
        "retefuente": resultado.get('retefuente', 0),
        "sin_deuda":  len(registros) == 0,
    }
    if excede:
        respuesta["excede_limite"]  = True
        respuesta["mensaje_limite"] = f"El límite de consulta es de {ANTIOQUIA_LIMITE_VIGENCIAS} vigencias. Comunícate con un asesor de la Gobernación de Antioquia al 6044444666."
    return jsonify(respuesta)


# ============================================================
#  RETEFUENTE
# ============================================================

# Mapeo clase OCR → tabla retefuente
def _tabla_retefuente(clase, carroceria=''):
    clase      = (clase or '').strip().upper()
    carroceria = (carroceria or '').strip().upper()
    if clase in ('AUTOMOVIL', 'AUTOMÓVIL'):             return 'T1'
    if clase == 'CAMIONETA':
        return 'T3' if carroceria == 'DOBLE CABINA' else 'T2'
    if clase in ('CAMPERO',):                            return 'T2'
    if clase in ('MOTOCICLETA', 'MOTOCARRO'):            return 'T5'
    if clase in ('BUS', 'BUSETA', 'MICROBUS', 'MICROBÚS'): return 'T6'
    if clase in ('CAMION', 'CAMIÓN', 'VOLQUETA'):        return 'T7'
    if clase == 'AMBULANCIA':                            return 'T8'
    return None

def _col_anio(modelo):
    """Devuelve el nombre de columna según el modelo del vehículo."""
    try:
        anio = int(str(modelo).strip())
    except:
        return 'anio_2001_ant'
    if anio <= 2001:
        return 'anio_2001_ant'
    if anio > 2025:
        return 'anio_2025'
    return f'anio_{anio}'


@app.route("/retefuente/buscar", methods=["GET"])
def retefuente_buscar():
    """
    Busca opciones de retefuente según marca, clase, carroceria y modelo.
    Devuelve lista de opciones para que el usuario elija.
    """
    marca      = request.args.get("marca", "").strip().upper()
    linea      = request.args.get("linea", "").strip().upper()
    clase      = request.args.get("clase", "").strip().upper()
    carroceria = request.args.get("carroceria", "").strip().upper()
    modelo     = request.args.get("modelo", "").strip()

    if not marca or not clase or not modelo:
        return jsonify({"error": "Debes enviar marca, clase y modelo."}), 400

    tabla = _tabla_retefuente(clase, carroceria)
    if not tabla:
        return jsonify({"error": f"Clase '{clase}' no tiene tabla de retefuente."}), 400

    col_anio = _col_anio(modelo)

    try:
        conn = get_db_conn()
        cur  = conn.cursor()

        # 1. Buscar coincidencias exactas de marca + línea contiene palabras clave
        palabras = [p for p in linea.split() if len(p) > 2]
        if palabras and linea:
            like_conditions = " AND ".join([f"linea ILIKE %s" for _ in palabras[:3]])
            params = [tabla, marca] + [f'%{p}%' for p in palabras[:3]]
            cur.execute(f"""
                SELECT id, marca, linea, cilindraje, {col_anio} as avaluo
                FROM retefuente_2026
                WHERE tabla = %s AND marca = %s AND {like_conditions}
                  AND {col_anio} > 0
                ORDER BY linea
                LIMIT 20
            """, params)
            rows = cur.fetchall()
        else:
            rows = []

        # 2. Si no hay resultados buscar línea base estándar de esa marca
        if not rows:
            cur.execute(f"""
                SELECT id, marca, linea, cilindraje, {col_anio} as avaluo
                FROM retefuente_2026
                WHERE tabla = %s AND marca = %s
                  AND (linea ILIKE %s OR linea ILIKE %s)
                  AND {col_anio} > 0
                ORDER BY linea
                LIMIT 5
            """, (tabla, marca, '%LINEA BASE%', '%BASE ESTANDAR%'))
            rows = cur.fetchall()

        # 3. Si sigue sin resultados, devolver todas las líneas de esa marca
        if not rows:
            cur.execute(f"""
                SELECT id, marca, linea, cilindraje, {col_anio} as avaluo
                FROM retefuente_2026
                WHERE tabla = %s AND marca = %s AND {col_anio} > 0
                ORDER BY linea
                LIMIT 30
            """, (tabla, marca))
            rows = cur.fetchall()

        cur.close()
        conn.close()

        opciones = [{
            "id":         r[0],
            "marca":      r[1],
            "linea":      r[2],
            "cilindraje": r[3],
            "avaluo":     r[4],
            "retefuente": round(r[4] / 100) if r[4] else 0
        } for r in rows]

        return jsonify({
            "tabla":   tabla,
            "col_anio": col_anio,
            "opciones": opciones,
            "total":   len(opciones)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/retefuente/marcas", methods=["GET"])
def retefuente_marcas():
    """Devuelve lista de marcas disponibles para una tabla."""
    clase      = request.args.get("clase", "").strip().upper()
    carroceria = request.args.get("carroceria", "").strip().upper()
    tabla = _tabla_retefuente(clase, carroceria)
    if not tabla:
        return jsonify({"error": "Clase no reconocida"}), 400
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("SELECT DISTINCT marca FROM retefuente_2026 WHERE tabla=%s ORDER BY marca", (tabla,))
        marcas = [r[0] for r in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"marcas": marcas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/tramites/filtros", methods=["GET"])
def tramites_filtros():
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        campo        = request.args.get("campo", "")
        departamento = request.args.get("departamento", "").strip().upper()
        municipio    = request.args.get("municipio", "").strip().upper()
        clase        = request.args.get("clase", "").strip().upper()
        if campo == "departamento":
            cur.execute("SELECT DISTINCT departamento FROM tramites_transito ORDER BY departamento")
        elif campo == "municipio" and departamento:
            cur.execute("SELECT DISTINCT municipio FROM tramites_transito WHERE departamento=%s ORDER BY municipio", (departamento,))
        elif campo == "clase" and municipio:
            cur.execute("SELECT DISTINCT clase FROM tramites_transito WHERE municipio=%s ORDER BY clase", (municipio,))
        elif campo == "tramite" and municipio and clase:
            cur.execute("SELECT DISTINCT tramite FROM tramites_transito WHERE municipio=%s AND clase=%s ORDER BY tramite", (municipio, clase))
        else:
            cur.close(); conn.close()
            return jsonify({"error": "Parametros insuficientes"}), 400
        valores = [row[0] for row in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"valores": valores})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/tramites/precio", methods=["GET"])
def tramites_precio():
    departamento = request.args.get("departamento", "").strip().upper()
    municipio    = request.args.get("municipio", "").strip().upper()
    clase        = request.args.get("clase", "").strip().upper()
    tramite      = request.args.get("tramite", "").strip().upper()
    if not all([departamento, municipio, clase, tramite]):
        return jsonify({"error": "Debes enviar departamento, municipio, clase y tramite"}), 400
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT precio FROM tramites_transito WHERE departamento=%s AND municipio=%s AND clase=%s AND tramite=%s LIMIT 1", (departamento, municipio, clase, tramite))
        row = cur.fetchone()
        cur.close(); conn.close()
        if row:
            return jsonify({"departamento": departamento, "municipio": municipio, "clase": clase, "tramite": tramite, "precio": row[0]})
        return jsonify({"error": "No se encontro el tramite"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/debug-env", methods=["GET"])
def debug_env():
    return jsonify({"DATABASE_URL": os.environ.get("DATABASE_URL", "NO EXISTE"), "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", "NO EXISTE")})


@app.route("/ocr-tarjeta", methods=["POST"])
def ocr_tarjeta():
    try:
        data = request.get_json()
        if not data or "imagen" not in data:
            return jsonify({"error": "No se recibio imagen"}), 400
        img_data   = data["imagen"]
        media_type = "image/jpeg"
        if "data:image/png" in img_data:
            media_type = "image/png"
        elif "data:image/webp" in img_data:
            media_type = "image/webp"
        if "," in img_data:
            img_data = img_data.split(",")[1]
        import hashlib
        hash_imagen = hashlib.sha256(img_data.encode()).hexdigest()
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT placa, marca, linea, modelo, clase, servicio, capacidad, cilindrada, carroceria, tipo_documento, cedula, apellidos, municipio FROM cache_tarjetas WHERE hash_imagen = %s", (hash_imagen,))
        row = cur.fetchone()
        if row:
            cur.close(); conn.close()
            return jsonify({"placa": row[0] or "", "marca": row[1] or "", "linea": row[2] or "", "modelo": row[3] or "", "clase": row[4] or "", "servicio": row[5] or "", "capacidad": row[6] or "", "cilindrada": row[7] or "", "carroceria": row[8] or "", "tipo_documento": row[9] or "", "cedula": row[10] or "", "apellidos": row[11] or "", "municipio": row[12] or "", "desde_cache": True})
        cur.close(); conn.close()
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_key:
            return jsonify({"error": "API Key de Anthropic no configurada"}), 500
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": anthropic_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-opus-4-5", "max_tokens": 600, "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": img_data}},
                {"type": "text", "text": "Eres un experto en leer tarjetas de propiedad de vehiculos colombianos. La imagen puede estar en cualquier orientacion. Analiza TODOS los caracteres con mucho cuidado especialmente los numeros. Extrae: 1. PLACA (exactamente 3 letras + 3 numeros, verifica cada caracter) 2. MARCA del vehiculo 3. LINEA del vehiculo 4. MODELO (anno 4 digitos) 5. CLASE (automovil, motocicleta, campero, camioneta, etc) 6. SERVICIO (particular, publico, oficial) 7. CAPACIDAD (numero de pasajeros o carga) 8. CILINDRADA (numero en cc) 9. TIPO_DOCUMENTO (uno de: C.C, NIT, P.P.T, T.I, R.C - aparece debajo de IDENTIFICACION al lado izquierdo del numero) 10. CEDULA (numero de identificacion, verifica TODOS los digitos uno por uno, no omitas ninguno) 11. APELLIDOS del propietario. Responde SOLO en JSON sin explicaciones: {\"placa\": \"\", \"marca\": \"\", \"linea\": \"\", \"modelo\": \"\", \"clase\": \"\", \"servicio\": \"\", \"capacidad\": \"\", \"cilindrada\": \"\", \"carroceria\": \"\", \"tipo_documento\": \"\", \"cedula\": \"\", \"apellidos\": \"\"}"}
            ]}]},
            timeout=120
        )
        if response.status_code != 200:
            return jsonify({"error": f"Error Claude API: {response.status_code}"}), 500
        resp_data = response.json()
        texto = resp_data["content"][0]["text"].strip()
        import json as json_lib, re as re_module
        texto_clean = texto.replace("```json", "").replace("```", "").strip()
        json_match = re_module.search(r'\{[^{}]*\}', texto_clean, re_module.DOTALL)
        if not json_match:
            return jsonify({"error": "No se pudo parsear respuesta de Claude"}), 500
        resultado = json_lib.loads(json_match.group())
        placa          = resultado.get("placa", "").upper().replace(" ", "").replace("-", "")
        marca          = resultado.get("marca", "").upper().strip()
        linea          = resultado.get("linea", "").upper().strip()
        modelo         = resultado.get("modelo", "").strip()
        clase          = resultado.get("clase", "").upper().strip()
        servicio       = resultado.get("servicio", "").upper().strip()
        capacidad      = resultado.get("capacidad", "").strip()
        cilindrada     = resultado.get("cilindrada", "").strip()
        carroceria     = resultado.get("carroceria", "").upper().strip()
        tipo_documento = resultado.get("tipo_documento", "").upper().strip()
        cedula         = resultado.get("cedula", "").strip()
        apellidos      = resultado.get("apellidos", "").upper().strip()
        try:
            conn2 = get_db_conn()
            cur2  = conn2.cursor()
            if placa:
                cur2.execute("DELETE FROM cache_tarjetas WHERE placa = %s AND hash_imagen != %s", (placa, hash_imagen))
            cur2.execute("""
                INSERT INTO cache_tarjetas (hash_imagen, placa, marca, linea, modelo, clase, servicio, capacidad, cilindrada, tipo_documento, cedula, apellidos, municipio)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (hash_imagen) DO UPDATE SET placa=EXCLUDED.placa, marca=EXCLUDED.marca, linea=EXCLUDED.linea, modelo=EXCLUDED.modelo, clase=EXCLUDED.clase, servicio=EXCLUDED.servicio, capacidad=EXCLUDED.capacidad, cilindrada=EXCLUDED.cilindrada, tipo_documento=EXCLUDED.tipo_documento, cedula=EXCLUDED.cedula, apellidos=EXCLUDED.apellidos, actualizado_en=NOW()
            """, (hash_imagen, placa, marca, linea, modelo, clase, servicio, capacidad, cilindrada, tipo_documento, cedula, apellidos, ""))
            conn2.commit()
            cur2.close()
            conn2.close()
        except Exception as e_cache:
            print(f"Error cache tarjeta: {e_cache}")
        return jsonify({"placa": placa, "marca": marca, "linea": linea, "modelo": modelo, "clase": clase, "servicio": servicio, "capacidad": capacidad, "cilindrada": cilindrada, "carroceria": carroceria, "tipo_documento": tipo_documento, "cedula": cedula, "apellidos": apellidos, "municipio": "", "desde_cache": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ocr-guardar-municipio", methods=["POST"])
def ocr_guardar_municipio():
    try:
        data      = request.get_json()
        placa     = data.get("placa", "").upper().strip()
        municipio = data.get("municipio", "").upper().strip()
        if not placa or not municipio:
            return jsonify({"ok": False}), 400
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("UPDATE cache_tarjetas SET municipio=%s, actualizado_en=NOW() WHERE placa=%s", (municipio, placa))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
