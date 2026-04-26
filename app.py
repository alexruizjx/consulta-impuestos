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

# ── Captcha ──
TWOCAPTCHA_API_KEY = "47a18b883a00d513b2c78b0ac2cd0f00"
EMTRASUR_SITE_KEY  = "6Leshn4sAAAAAIas9tkeW3vKPg0a4uYqw-7fG7Pn"
EMTRASUR_URL       = "https://sistematizacion.emtrasur.com.co/"
ANTIOQUIA_SITE_KEY = "0x4AAAAAACJy_BR2tRNN1cnv"
ANTIOQUIA_URL      = "https://www.vehiculosantioquia.com.co/impuestosweb/#/public"
ANTIOQUIA_API      = "https://www.vehiculosantioquia.com.co/raiz-backimpuestosweb/backimpuestosweb"


def bloquear_recursos(page):
    page.route("**/*", lambda route: route.abort()
               if route.request.resource_type in ["image", "stylesheet", "font", "media", "other"]
               else route.continue_())


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
    raise Exception("2captcha tardó demasiado en resolver el captcha.")


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
    raise Exception("2captcha tardó demasiado en resolver el captcha.")


# ── Municipios ──

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

    match_total = re.search(r'Total a pagar:\s*COP\s*([\d.]+)', texto_pagina)
    total = int(match_total.group(1).replace('.', '')) if match_total else sum(r['total_vigencia'] for r in registros)
    return registros, total


def _parsear_emtrasur(data):
    registros = []
    for r in data:
        registros.append({
            "vigencia":       str(r.get("AnioNoFacturado", "")),
            "estado":         "Pendiente de pago",
            "total_vigencia": r.get("ValorPorFacturar", 0),
            "tipo_vehiculo":  r.get("TipoVehiculo", ""),
            "ultimo_pago":    r.get("AnioPagado", ""),
            "descripcion":    r.get("DescripcionNoFacturada", "").strip(),
        })
    total = sum(r["total_vigencia"] for r in registros)
    return registros, total


def consultar_laestrella(page, placa):
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
    raise Exception(f"EMTRASUR respondió {resp.status_code}: {resp.text[:200]}")

# ── AGREGAR ESTA FUNCIÓN EN app.py ───────────────────────────────────────────
# Llamar a guardar_cache_impuesto_antioquia() después de procesar cada vigencia
# en el endpoint /consultar cuando municipio=antioquia

def guardar_cache_impuesto_antioquia(placa, vigencia, declaracion, sin_deuda=False):
    """
    Guarda o actualiza los datos de impuesto de Antioquia en caché.
    declaracion: dict con los campos del JSON de crearDeclaracionImpuestoAnt
    """
    try:
        conn = get_db_conn()
        cur  = conn.cursor()

        avaluo      = int(declaracion.get("avaluoComercial", 0) or 0)
        retefuente  = round(avaluo / 100) if avaluo else 0
        estado      = "PAZ_Y_SALVO" if sin_deuda else "PENDIENTE"
        
        # Fecha de expiracion
        from datetime import date, timedelta
        hoy_d       = date.today()
        anio_actual = hoy_d.year
        if sin_deuda:
            expira_en = date(anio_actual, 12, 31)
        elif vigencia < anio_actual:
            expira_en = hoy_d + timedelta(days=30)
        elif hoy_d >= date(anio_actual, 8, 1):
            expira_en = hoy_d + timedelta(days=30)
        else:
            expira_en = None

        cur.execute("""
            INSERT INTO cache_impuestos_antioquia (
                placa, vigencia, formulario_liquidacion,
                avaluo_comercial, impuesto, impuesto_con_desc,
                sancion, sancion_con_desc, descuento_sancion, otras_sanciones,
                intereses_mora, intereses_con_desc, descuento_intereses,
                descuento_pronto_pago, pagos_anteriores, otros_pagos,
                total_cargo, saldo_pagar, total_pagar, saldo_favor,
                retefuente, aplica_beneficio, estado, actualizado_en, expira_en
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, NOW(), %s
            )
            ON CONFLICT (placa, vigencia) DO UPDATE SET
                formulario_liquidacion = EXCLUDED.formulario_liquidacion,
                avaluo_comercial       = EXCLUDED.avaluo_comercial,
                impuesto               = EXCLUDED.impuesto,
                impuesto_con_desc      = EXCLUDED.impuesto_con_desc,
                sancion                = EXCLUDED.sancion,
                sancion_con_desc       = EXCLUDED.sancion_con_desc,
                descuento_sancion      = EXCLUDED.descuento_sancion,
                otras_sanciones        = EXCLUDED.otras_sanciones,
                intereses_mora         = EXCLUDED.intereses_mora,
                intereses_con_desc     = EXCLUDED.intereses_con_desc,
                descuento_intereses    = EXCLUDED.descuento_intereses,
                descuento_pronto_pago  = EXCLUDED.descuento_pronto_pago,
                pagos_anteriores       = EXCLUDED.pagos_anteriores,
                otros_pagos            = EXCLUDED.otros_pagos,
                total_cargo            = EXCLUDED.total_cargo,
                saldo_pagar            = EXCLUDED.saldo_pagar,
                total_pagar            = EXCLUDED.total_pagar,
                saldo_favor            = EXCLUDED.saldo_favor,
                retefuente             = EXCLUDED.retefuente,
                aplica_beneficio       = EXCLUDED.aplica_beneficio,
                estado                 = EXCLUDED.estado,
                expira_en              = EXCLUDED.expira_en,
                actualizado_en         = NOW()
        """, (
            placa.upper(), vigencia,
            str(declaracion.get("formularioLiquidacion", "") or ""),
            avaluo,
            int(declaracion.get("impuesto",         0) or 0),
            int(declaracion.get("impuestoConDesc",   0) or 0),
            int(declaracion.get("sancion",           0) or 0),
            int(declaracion.get("sancionConDesc",    0) or 0),
            int(declaracion.get("descuentoSancion",  0) or 0),
            int(declaracion.get("otrasSanciones",    0) or 0),
            int(declaracion.get("interesesMora",     0) or 0),
            int(declaracion.get("interesesConDesc",  0) or 0),
            int(declaracion.get("descuentoInteresesMora", 0) or 0),
            int(declaracion.get("descuentoProntoPago", 0) or 0),
            int(declaracion.get("pagosAnteriores",   0) or 0),
            int(declaracion.get("otrosPagos",        0) or 0),
            int(declaracion.get("totalCargo",        0) or 0),
            int(declaracion.get("saldoPagar",        0) or 0),
            int(declaracion.get("totalPagar",        0) or 0),
            int(declaracion.get("saldoFavor",        0) or 0),
            retefuente,
            str(declaracion.get("aplicaBeneficioTributario", "") or ""),
            estado,
            expira_en
        ))

        conn.commit()
        cur.close()
        conn.close()
        print(f"Cache impuesto Antioquia guardado: {placa} vigencia {vigencia} estado {estado}")

    except Exception as e:
        print(f"Error guardando cache impuesto Antioquia: {e}")


# ── ENDPOINT PARA CONSULTAR EL CACHE ─────────────────────────────────────────

@app.route("/impuesto-antioquia/cache", methods=["GET"])
def impuesto_antioquia_cache():
    """Consulta el cache de impuestos de Antioquia para una placa."""
    placa = request.args.get("placa", "").upper().strip()
    if not placa:
        return jsonify({"error": "Falta la placa"}), 400
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT vigencia, impuesto_con_desc, sancion_con_desc, intereses_con_desc,
                   otros_pagos, total_pagar, avaluo_comercial, retefuente,
                   estado, aplica_beneficio, actualizado_en
            FROM cache_impuestos_antioquia
            WHERE placa = %s
            ORDER BY vigencia DESC
        """, (placa,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            return jsonify({"encontrado": False})
        return jsonify({
            "encontrado": True,
            "placa":      placa,
            "registros":  [{
                "vigencia":          r[0],
                "impuesto":          r[1],
                "sanciones":         r[2],
                "intereses":         r[3],
                "otros_pagos":       r[4],
                "total_pagar":       r[5],
                "avaluo_comercial":  r[6],
                "retefuente":        r[7],
                "estado":            r[8],
                "aplica_beneficio":  r[9],
                "actualizado_en":    str(r[10])
            } for r in rows]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def consultar_antioquia(page, placa, identificacion, tipo_documento,
                        modelo, municipio_transito, apellidos_propietario):
                            
    # Verificar cache primero — si hay datos guardados devolver inmediatamente
    try:
        conn_c = get_db_conn()
        cur_c  = conn_c.cursor()
        cur_c.execute("""
            SELECT vigencia, total_pagar, avaluo_comercial, estado
            FROM cache_impuestos_antioquia
            WHERE placa = %s
            AND (expira_en IS NULL OR expira_en >= CURRENT_DATE)
            ORDER BY vigencia DESC
        """, (placa,))
        rows_c = cur_c.fetchall()
        cur_c.close()
        conn_c.close()

        if rows_c:
            # Cache inicial SOLO aplica para paz y salvo total
            todas_paz = all(r[3] == 'PAZ_Y_SALVO' for r in rows_c)
            if todas_paz:
                avaluo_cache = rows_c[0][2] or 0
                return [], 0, avaluo_cache, {}, False
            # Si tiene deuda, NO devolver desde cache
            # Continuar con consulta completa a Antioquia

    except Exception as e_cache_init:
        print(f"Error consultando cache inicial: {e_cache_init}", flush=True, file=sys.stderr)

    # Paso 1 — Resolver Turnstile
    token = resolver_turnstile_2captcha(ANTIOQUIA_SITE_KEY, ANTIOQUIA_URL)

    session = requests.Session()
    session.headers.update({
        "Accept":           "*/*",
        "Content-Type":     "application/json",
        "captcha":          token,
        "Referer":          "https://www.vehiculosantioquia.com.co/impuestosweb/",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent":       "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
    })

    # Paso 2 — Obtener cuestionario
    r1 = session.post(
        f"{ANTIOQUIA_API}/ConsultarEstadoCuentaImpAntioquia/obtenerCuestionarioEstadoCuenta",
        json={
            "placa":                placa,
            "idTipoIdentificacion": tipo_documento,
            "identificacion":       identificacion,
        },
        timeout=120
    )
    data1 = r1.json()
    referencia = data1.get("referencia")

    opciones_nombre = data1.get("preguntaNombrePropietario", {}).get("opcionesPregunta", [])
    nombre_encontrado = next(
        (n for n in opciones_nombre if apellidos_propietario.upper() in n.upper()), None
    )
    if not nombre_encontrado:
        raise Exception(f"No se encontró propietario con apellidos '{apellidos_propietario}'.")

    # Paso 3 — Validar cuestionario
    r2 = session.post(
        f"{ANTIOQUIA_API}/ConsultarEstadoCuentaImpAntioquia/validarCuestionarioEstadoCuenta",
        json={
            "placa":           placa,
            "tipoDocumento":   tipo_documento,
            "numeroDocumento": identificacion,
            "idEstadoCuenta":  referencia,
            "respuestas": {
                "respuestaModelo":            modelo,
                "respuestaOrganismoTransito": municipio_transito,
                "respuestaNombrePropietario": nombre_encontrado,
            }
        },
        timeout=120
    )
    if r2.json().get("codigo") != 1:
        raise Exception("Cuestionario incorrecto. Verifica modelo, municipio y apellidos.")

    # Paso 4 — Segundo Turnstile y estado de cuenta
    token2 = resolver_turnstile_2captcha(ANTIOQUIA_SITE_KEY, ANTIOQUIA_URL)
    session.headers.update({"captcha": token2})

    token_cuestionario = session.cookies.get("token_cuestionario")
    if not token_cuestionario:
        raise Exception("No se obtuvo token_cuestionario.")

    r3 = session.post(
        f"{ANTIOQUIA_API}/ConsultarEstadoCuentaImpAntioquia/consultarEstadoCuentaVehiculoHomePublico",
        json={"placa": placa, "informacionDeclarante": {
            "idsolicitante":        identificacion,
            "idTipoIdentificacion": tipo_documento
        }},
        headers={"Cookie": f"token_cuestionario={token_cuestionario}"},
        timeout=120
    )
    data3 = r3.json()
    data3 = r3.json()
    print("VIGENCIAS ADEUDADAS:", data3.get("listaVigenciasAdeudas", []))                        

    estado              = data3.get("estadoCuenta", {})
    vigencias_adeudadas = data3.get("listaVigenciasAdeudas", [])
    procesos_fiscales   = data3.get("listaProcesoFiscal", [])
    avaluo              = estado.get("avaluoComercial", 0) or 0

    from datetime import date
    import sys
    hoy         = date.today()
    anio_actual = hoy.year
    solo_actual = (len(vigencias_adeudadas) == 1 and
                   vigencias_adeudadas[0]["vigencia"] == anio_actual)
    periodo_calc = date(anio_actual, 1, 1) <= hoy <= date(anio_actual, 7, 31)

    if solo_actual and periodo_calc:
        try:
            conn_c = get_db_conn()
            cur_c  = conn_c.cursor()
            cur_c.execute("""
                SELECT impuesto_con_desc, otros_pagos
                FROM cache_impuestos_antioquia
                WHERE placa = %s AND vigencia = %s
            """, (placa, anio_actual))
            row_c = cur_c.fetchone()
            cur_c.close()
            conn_c.close()

            if row_c:
                impuesto_base  = row_c[0] or 0
                valor_servicio = row_c[1] or 0

                if hoy <= date(anio_actual, 4, 30):
                    total_calculado = round(impuesto_base * 0.90) + valor_servicio
                else:
                    total_calculado = impuesto_base + valor_servicio

                print(f"CALCULO LOCAL: placa={placa} total={total_calculado}", flush=True, file=sys.stderr)

                registros = [{
                    "vigencia":       str(anio_actual),
                    "estado":         "Pendiente de pago",
                    "total_vigencia": total_calculado,
                }]
                return registros, total_calculado, avaluo, estado, False

        except Exception as e_calc:
            print(f"Error calculo local: {e_calc}", flush=True, file=sys.stderr)

    if not vigencias_adeudadas:
        try:
            anio_actual = datetime.now().year
            guardar_cache_impuesto_antioquia(placa, anio_actual, estado, sin_deuda=True)
        except Exception as e_cache:
            print(f"Error cache paz y salvo: {e_cache}")
        return [], 0, avaluo, estado, False

    total_vigencias = len(vigencias_adeudadas)
    LIMITE = 5

    def liquidar_vigencia(anio):
        """Liquida una vigencia y retorna (total, avaluo)."""
        token3 = resolver_turnstile_2captcha(ANTIOQUIA_SITE_KEY, ANTIOQUIA_URL)
        session.headers.update({"captcha": token3})

        r4 = session.post(
            f"{ANTIOQUIA_API}/UsuariosPortalAntioquia/consultarPropietarioVehiculo",
            json={"tipoDoc": "CC", "nroDoc": identificacion, "placa": placa, "vigencia": anio},
            headers={"Cookie": f"token_cuestionario={token_cuestionario}"},
            timeout=120
        )
        propietario = r4.json().get("propietario", {})

        session.post(f"{ANTIOQUIA_API}/TablasTipo/obtenerTablasPropietario", json={},
                     headers={"Cookie": f"token_cuestionario={token_cuestionario}"}, timeout=120)
        session.get(f"{ANTIOQUIA_API}/UtilImpuestos/obtenerDescripcionPPST",
                    headers={"Cookie": f"token_cuestionario={token_cuestionario}"}, timeout=120)
        session.post(f"{ANTIOQUIA_API}/Pagos/parametrosPago", json={},
                     headers={"Cookie": f"token_cuestionario={token_cuestionario}"}, timeout=120)
        session.get(f"{ANTIOQUIA_API}/UtilImpuestos/obtenerVigenciaMinimaAutodeclarar",
                    headers={"Cookie": f"token_cuestionario={token_cuestionario}"}, timeout=120)

        token4 = resolver_turnstile_2captcha(ANTIOQUIA_SITE_KEY, ANTIOQUIA_URL)
        session.headers.update({"captcha": token4})
        session.cookies.clear()

        r5 = session.post(
            f"{ANTIOQUIA_API}/LiquidacionAntioquia/crearDeclaracionImpuestoAnt",
            json={
                "formularioLiquidacion": "",
                "declarante": {
                    "idsolicitante":    identificacion,
                    "idtipodocumento":  "CC",
                    "desctipodocument": "Cédula de Ciudadanía",
                    "nombres":          propietario.get("nameFirst", ""),
                    "apellidos":        propietario.get("nameLast", ""),
                    "celular":          "3000000000",
                    "telefono":         "3000000000",
                    "email":            "consulta@consulta.com",
                    "direccion":        "CRA",
                    "municipio":        "MEDELLIN",
                    "departamento":     "ANTIOQUIA",
                    "nivreclamacion":   0,
                    "procedimiento":    ""
                },
                "iIdliqIm": 0,
                "informacionComplementaria": {
                    "idTipoDocumento":               1,
                    "distribucionDepartamento":      5,
                    "distribucionMunicipio":         5001000,
                    "direccionCompleta":             "CRA",
                    "nombreDistribucionDepartamento": "ANTIOQUIA",
                    "nombreDistribucionMunicipio":   "MEDELLIN",
                    "tipoCanalLiquidacion":          2,
                    "tipoOpcionLiquidacion":         1
                },
                "placa":    placa,
                "vigencia": [{"persl": anio}]
            },
            timeout=120
        )
        data5 = r5.json()

        # Guardar en cache
        try:
            guardar_cache_impuesto_antioquia(placa, anio, data5, sin_deuda=False)
        except Exception as e_cache:
            print(f"Error cache impuesto: {e_cache}")

        return data5.get("totalPagar", 0), data5.get("avaluoComercial", avaluo)

    LIMITE = 1  # Cambiar este número para liquidar más vigencias

    # Ordenar vigencias de más reciente a más antigua
    vigencias_ordenadas = sorted(vigencias_adeudadas, key=lambda x: x["vigencia"], reverse=True)

    registros = []
    total_reciente   = 0
    avaluo_reciente  = avaluo
    vigencias_liquidadas = 0

    for v in vigencias_ordenadas:
        anio = v.get("vigencia")
        procesos = [p for p in procesos_fiscales if p.get("vigencia") == anio]
        estado_vigencia = procesos[0].get("descripcionProcesoFiscal") if procesos else "Pendiente de pago"

        # Verificar si ya está en caché
        total_cache = None
        try:
            conn_c = get_db_conn()
            cur_c  = conn_c.cursor()
            cur_c.execute(
                "SELECT total_pagar, avaluo_comercial FROM cache_impuestos_antioquia WHERE placa=%s AND vigencia=%s",
                (placa, anio)
            )
            row_c = cur_c.fetchone()
            cur_c.close()
            conn_c.close()
            if row_c:
                total_cache     = row_c[0]
                avaluo_reciente = row_c[1] or avaluo
        except Exception:
            pass

        if total_cache is not None:
            # Viene del caché — sin costo
            total = total_cache
            if vigencias_liquidadas == 0:
                total_reciente = total
        elif vigencias_liquidadas < LIMITE:
            # Liquidar con Turnstile
            total, avaluo_reciente = liquidar_vigencia(anio)
            if vigencias_liquidadas == 0:
                total_reciente = total
            vigencias_liquidadas += 1
        else:
            # Límite alcanzado y no está en caché
            total = None

        registros.append({
            "vigencia":       str(anio),
            "estado":         estado_vigencia,
            "total_vigencia": total,
        })

    excede = total_vigencias > LIMITE
    return registros, total_reciente, avaluo_reciente, estado, excede


# ── Router ──

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
    placa     = request.args.get("placa", "").upper().strip()
    municipio = request.args.get("municipio", "").lower().strip()

    if not placa or not municipio:
        return jsonify({"error": "Debes proporcionar placa y municipio."}), 400

    if municipio not in MUNICIPIOS and municipio != "antioquia":
        return jsonify({
            "error": f"Municipio '{municipio}' no reconocido.",
            "opciones": list(MUNICIPIOS.keys()) + ["antioquia"]
        }), 400

    # ── Extraer parámetros ANTES del hilo ──
    identificacion     = request.args.get("identificacion", "").strip()
    tipo_documento     = request.args.get("tipo_documento", "1").strip()
    modelo             = request.args.get("modelo", "").strip()
    municipio_transito = request.args.get("municipio_transito", "").upper().strip()
    apellidos          = request.args.get("apellidos_propietario", "").upper().strip()

    if municipio == "antioquia":
        if not identificacion or not modelo or not municipio_transito or not apellidos:
            return jsonify({
                "error": "Para Antioquia debes proporcionar: identificacion, modelo, municipio_transito, apellidos_propietario."
            }), 400

    resultado       = {}
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

                if municipio == "antioquia":
                    retorno = consultar_antioquia(
                        page, placa, identificacion, tipo_documento,
                        modelo, municipio_transito, apellidos
                    )
                    registros, total, avaluo, estado_veh, excede = retorno
                    resultado['registros']  = registros
                    resultado['total']      = total
                    resultado['avaluo']     = avaluo
                    resultado['excede']     = excede
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

    hilo = threading.Thread(target=ejecutar)
    hilo.start()
    hilo.join(timeout=180)

    if hilo.is_alive():
        return jsonify({"error": "La consulta tardó demasiado. Intenta de nuevo."}), 504

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
            return jsonify({
                "error": f"No se pudo conectar al portal de {municipio}. Intenta más tarde."
            }), 503
        return jsonify({"error": error_container['error']}), 500

    # ── Respuesta municipios ──
    if municipio != "antioquia":
        return jsonify({
            "placa":     placa,
            "municipio": municipio,
            "registros": resultado.get('registros', []),
            "total":     resultado.get('total', 0),
            "sin_deuda": resultado.get('total', 0) == 0
        })

    # ── Respuesta Antioquia ──
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
        "sin_deuda":  total == 0 if total is not None else False,
    }

    if excede:
        respuesta["excede_limite"]  = True
        respuesta["mensaje_limite"] = "El límite de consulta es de 5 vigencias. Para saber lo adeudado en las demás vigencias comunícate con un asesor de la Gobernación de Antioquia al 6044444666."

    return jsonify(respuesta)




def get_db_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])


@app.route("/tramites/filtros", methods=["GET"])
def tramites_filtros():
    """Devuelve los valores únicos para poblar los dropdowns."""
    try:
        conn = get_db_conn()
        cur = conn.cursor()

        campo = request.args.get("campo", "")
        departamento = request.args.get("departamento", "").strip().upper()
        municipio = request.args.get("municipio", "").strip().upper()
        clase = request.args.get("clase", "").strip().upper()

        if campo == "departamento":
            cur.execute("SELECT DISTINCT departamento FROM tramites_transito ORDER BY departamento")

        elif campo == "municipio" and departamento:
            cur.execute(
                "SELECT DISTINCT municipio FROM tramites_transito WHERE departamento=%s ORDER BY municipio",
                (departamento,)
            )

        elif campo == "clase" and municipio:
            cur.execute(
                "SELECT DISTINCT clase FROM tramites_transito WHERE municipio=%s ORDER BY clase",
                (municipio,)
            )

        elif campo == "tramite" and municipio and clase:
            cur.execute(
                "SELECT DISTINCT tramite FROM tramites_transito WHERE municipio=%s AND clase=%s ORDER BY tramite",
                (municipio, clase)
            )

        else:
            cur.close()
            conn.close()
            return jsonify({"error": "Parámetros insuficientes"}), 400

        valores = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify({"valores": valores})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/tramites/precio", methods=["GET"])
def tramites_precio():
    """Devuelve el precio para una combinación exacta."""
    departamento = request.args.get("departamento", "").strip().upper()
    municipio    = request.args.get("municipio", "").strip().upper()
    clase        = request.args.get("clase", "").strip().upper()
    tramite      = request.args.get("tramite", "").strip().upper()

    if not all([departamento, municipio, clase, tramite]):
        return jsonify({"error": "Debes enviar departamento, municipio, clase y tramite"}), 400

    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT precio FROM tramites_transito
            WHERE departamento=%s AND municipio=%s AND clase=%s AND tramite=%s
            LIMIT 1
        """, (departamento, municipio, clase, tramite))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return jsonify({
                "departamento": departamento,
                "municipio":    municipio,
                "clase":        clase,
                "tramite":      tramite,
                "precio":       row[0]
            })
        else:
            return jsonify({"error": "No se encontró el trámite"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/debug-env", methods=["GET"])
def debug_env():
    return jsonify({
        "DATABASE_URL": os.environ.get("DATABASE_URL", "NO EXISTE"),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", "NO EXISTE")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

# ── AGREGAR AL INICIO DE app.py ──────────────────────────────────────────────
# import base64, re
# from PIL import Image
# import pytesseract
# import io

# ── AGREGAR AL FINAL DE app.py ────────────────────────────────────────────────

# ── REEMPLAZAR el endpoint /ocr-tarjeta en app.py ────────────────────────────

@app.route("/ocr-tarjeta", methods=["POST"])
def ocr_tarjeta():
    """Recibe imagen base64 de tarjeta de propiedad y extrae los datos con Claude AI."""
    try:
        data = request.get_json()
        if not data or "imagen" not in data:
            return jsonify({"error": "No se recibió imagen"}), 400

        img_data = data["imagen"]
        media_type = "image/jpeg"

        if "data:image/png" in img_data:
            media_type = "image/png"
        elif "data:image/webp" in img_data:
            media_type = "image/webp"

        if "," in img_data:
            img_data = img_data.split(",")[1]

        # Generar hash de la imagen
        import hashlib
        hash_imagen = hashlib.sha256(img_data.encode()).hexdigest()

        # Buscar en caché por hash exacto
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT placa, marca, linea, modelo, clase, servicio, capacidad, cilindrada, tipo_documento, cedula, apellidos, municipio FROM cache_tarjetas WHERE hash_imagen = %s", (hash_imagen,))
        row = cur.fetchone()

        if row:
            cur.close()
            conn.close()
            return jsonify({
                "placa":          row[0] or "",
                "marca":          row[1] or "",
                "linea":          row[2] or "",
                "modelo":         row[3] or "",
                "clase":          row[4] or "",
                "servicio":       row[5] or "",
                "capacidad":      row[6] or "",
                "cilindrada":     row[7] or "",
                "tipo_documento": row[8] or "",
                "cedula":         row[9] or "",
                "apellidos":      row[10] or "",
                "municipio":      row[11] or "",
                "desde_cache":    True
            })

        cur.close()
        conn.close()

        # No está en caché — llamar a Claude
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_key:
            return jsonify({"error": "API Key de Anthropic no configurada"}), 500

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         anthropic_key,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-opus-4-5",
                "max_tokens": 600,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type":       "base64",
                                "media_type": media_type,
                                "data":       img_data,
                            }
                        },
                        {
                            "type": "text",
                            "text": "Eres un experto en leer tarjetas de propiedad de vehiculos colombianos. La imagen puede estar en cualquier orientacion. Analiza TODOS los caracteres con mucho cuidado especialmente los numeros. Extrae: 1. PLACA (exactamente 3 letras + 3 numeros, verifica cada caracter) 2. MARCA del vehiculo 3. LINEA del vehiculo 4. MODELO (año 4 digitos) 5. CLASE (automovil, motocicleta, campero, camioneta, etc) 6. SERVICIO (particular, publico, oficial) 7. CAPACIDAD (numero de pasajeros o carga) 8. CILINDRADA (numero en cc) 9. TIPO_DOCUMENTO (uno de: C.C, NIT, P.P.T, T.I, R.C - aparece debajo de IDENTIFICACION al lado izquierdo del numero) 10. CEDULA (numero de identificacion, verifica TODOS los digitos uno por uno, no omitas ninguno) 11. APELLIDOS del propietario 12. MUNICIPIO de transito. Responde SOLO en JSON sin explicaciones: {\"placa\": \"\", \"marca\": \"\", \"linea\": \"\", \"modelo\": \"\", \"clase\": \"\", \"servicio\": \"\", \"capacidad\": \"\", \"cilindrada\": \"\", \"tipo_documento\": \"\", \"cedula\": \"\", \"apellidos\": \"\", \"municipio\": \"\"}. Municipios validos: ANDES, APARTADO, BARBOSA, BELLO, CALDAS, CAREPA, EL CARMEN DE VIBORAL, CAUCASIA, CIUDAD BOLIVAR, COPACABANA, DEPARTAMENTAL, ENVIGADO, FRONTINO, GIRARDOTA, ITAGUI, LA CEJA, LA ESTRELLA, LA UNION, MARINILLA, MEDELLIN, PUERTO BERRIO, RIONEGRO, SABANETA, SANTA FE DE ANTIOQUIA, SANTA ROSA DE OSOS, SONSON, TURBO, URRAO, YARUMAL"
                        }
                    ]
                }]
            },
            timeout=120
        )

        if response.status_code != 200:
            return jsonify({"error": f"Error Claude API: {response.status_code} - {response.text}"}), 500

        resp_data = response.json()
        texto = resp_data["content"][0]["text"].strip()

        import json as json_lib
        import re as re_module
        texto_clean = texto.replace("```json", "").replace("```", "").strip()
        json_match = re_module.search(r'\{[^{}]*\}', texto_clean, re_module.DOTALL)
        if not json_match:
            return jsonify({"error": "No se pudo parsear respuesta de Claude", "raw": texto}), 500

        resultado = json_lib.loads(json_match.group())

        # Normalizar
        placa          = resultado.get("placa", "").upper().replace(" ", "").replace("-", "")
        marca          = resultado.get("marca", "").upper().strip()
        linea          = resultado.get("linea", "").upper().strip()
        modelo         = resultado.get("modelo", "").strip()
        clase          = resultado.get("clase", "").upper().strip()
        servicio       = resultado.get("servicio", "").upper().strip()
        capacidad      = resultado.get("capacidad", "").strip()
        cilindrada     = resultado.get("cilindrada", "").strip()
        tipo_documento = resultado.get("tipo_documento", "").upper().strip()
        cedula         = resultado.get("cedula", "").strip()
        apellidos      = resultado.get("apellidos", "").upper().strip()
        municipio      = resultado.get("municipio", "").upper().strip()

        # Guardar en caché — si la placa ya existe, sobrescribir
        try:
            conn2 = get_db_conn()
            cur2  = conn2.cursor()

            # Borrar registro anterior con misma placa (diferente hash)
            if placa:
                cur2.execute("DELETE FROM cache_tarjetas WHERE placa = %s AND hash_imagen != %s", (placa, hash_imagen))

            # Insertar nuevo registro
            cur2.execute("""
                INSERT INTO cache_tarjetas
                    (hash_imagen, placa, marca, linea, modelo, clase, servicio, capacidad, cilindrada, tipo_documento, cedula, apellidos, municipio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (hash_imagen) DO UPDATE SET
                    placa=EXCLUDED.placa, marca=EXCLUDED.marca, linea=EXCLUDED.linea,
                    modelo=EXCLUDED.modelo, clase=EXCLUDED.clase, servicio=EXCLUDED.servicio,
                    capacidad=EXCLUDED.capacidad, cilindrada=EXCLUDED.cilindrada,
                    tipo_documento=EXCLUDED.tipo_documento, cedula=EXCLUDED.cedula,
                    apellidos=EXCLUDED.apellidos, municipio=EXCLUDED.municipio,
                    actualizado_en=NOW()
            """, (hash_imagen, placa, marca, linea, modelo, clase, servicio, capacidad, cilindrada, tipo_documento, cedula, apellidos, municipio))

            conn2.commit()
            cur2.close()
            conn2.close()
        except Exception as e_cache:
            print(f"Error guardando caché: {e_cache}")

        return jsonify({
            "placa":          placa,
            "marca":          marca,
            "linea":          linea,
            "modelo":         modelo,
            "clase":          clase,
            "servicio":       servicio,
            "capacidad":      capacidad,
            "cilindrada":     cilindrada,
            "tipo_documento": tipo_documento,
            "cedula":         cedula,
            "apellidos":      apellidos,
            "municipio":      municipio,
            "desde_cache":    False
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ocr-guardar-municipio", methods=["POST"])
def ocr_guardar_municipio():
    try:
        data = request.get_json()
        placa = data.get("placa", "").upper().strip()
        municipio = data.get("municipio", "").upper().strip()
        if not placa or not municipio:
            return jsonify({"ok": False}), 400
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("UPDATE cache_tarjetas SET municipio=%s, actualizado_en=NOW() WHERE placa=%s", (municipio, placa))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
