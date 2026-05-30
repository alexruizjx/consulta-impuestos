import base64, re, io
from PIL import Image
import pytesseract
import os
import psycopg2
import re
import time
import uuid
import json
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

TWOCAPTCHA_API_KEY = os.environ.get("TWOCAPTCHA_API_KEY", "")
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


def job_actualizar(job_id, mensaje, estado='procesando', datos_parciales=None):
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        if datos_parciales is not None:
            cur.execute("""
                INSERT INTO consulta_jobs (job_id, estado, mensaje, resultado, actualizado_en)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (job_id) DO UPDATE SET estado=%s, mensaje=%s, resultado=%s, actualizado_en=NOW()
            """, (job_id, estado, mensaje, json.dumps({"parcial": datos_parciales}),
                  estado, mensaje, json.dumps({"parcial": datos_parciales})))
        else:
            cur.execute("""
                INSERT INTO consulta_jobs (job_id, estado, mensaje, actualizado_en)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (job_id) DO UPDATE SET estado=%s, mensaje=%s, actualizado_en=NOW()
            """, (job_id, estado, mensaje, estado, mensaje))
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f"Error job: {e}")

def job_terminar(job_id, resultado):
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            UPDATE consulta_jobs SET estado='listo', mensaje='Consulta finalizada.', resultado=%s, actualizado_en=NOW()
            WHERE job_id=%s
        """, (json.dumps(resultado), job_id))
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f"Error job terminar: {e}")

def job_error(job_id, mensaje_error):
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            UPDATE consulta_jobs SET estado='error', mensaje=%s, actualizado_en=NOW()
            WHERE job_id=%s
        """, (mensaje_error, job_id))
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f"Error job error: {e}")


# ============================================================
#  CACHE IMPUESTOS ANTIOQUIA
# ============================================================

def cache_antioquia_buscar(placa):
    """Busca PAZ_Y_SALVO en caché para el año actual."""
    try:
        anio_actual = datetime.now().year
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT estado, total_pagar, avaluo_comercial, retefuente, vigencia
            FROM cache_impuestos_antioquia
            WHERE placa = %s AND vigencia = %s AND estado = 'PAZ_Y_SALVO'
              AND (expira_en IS NULL OR expira_en >= NOW())
            ORDER BY creado_en DESC LIMIT 1
        """, (placa.upper(), str(anio_actual)))
        row = cur.fetchone()
        cur.close(); conn.close()
        if row:
            return {
                "estado":     row[0],
                "total":      row[1] or 0,
                "avaluo":     row[2] or 0,
                "retefuente": row[3] or 0,
                "vigencia":   row[4],
            }
        return None
    except Exception as e:
        print(f"Error cache buscar: {e}")
        return None


def cache_antioquia_buscar_vigencia(placa, anio):
    """Busca el valor cacheado de una vigencia específica con deuda."""
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT total_pagar, avaluo_comercial, retefuente
            FROM cache_impuestos_antioquia
            WHERE placa = %s AND vigencia = %s AND estado = 'CON_DEUDA'
              AND (expira_en IS NULL OR expira_en >= NOW())
            ORDER BY creado_en DESC LIMIT 1
        """, (placa.upper(), int(anio)))
        row = cur.fetchone()
        cur.close(); conn.close()
        if row:
            return {"total_pagar": row[0] or 0, "avaluo": row[1] or 0, "retefuente": row[2] or 0}
        return None
    except Exception as e:
        print(f"Error cache buscar vigencia: {e}")
        return None


def cache_antioquia_eliminar_vigencia(placa, anio):
    """Elimina del caché una vigencia que ya fue pagada."""
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            DELETE FROM cache_impuestos_antioquia
            WHERE placa = %s AND vigencia = %s AND estado = 'CON_DEUDA'
        """, (placa.upper(), int(anio)))
        conn.commit()
        cur.close(); conn.close()
        print(f"  → Caché eliminado para {placa} vigencia {anio} (fue pagada)")
    except Exception as e:
        print(f"Error cache eliminar vigencia: {e}")


def cache_antioquia_guardar_paz_salvo(placa, avaluo, estado_veh):
    """Guarda en caché que la placa está a paz y salvo hasta fin de año."""
    try:
        anio_actual = datetime.now().year
        expira = f"{anio_actual}-12-31"
        retefuente = round(avaluo / 100) if avaluo else 0
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO cache_impuestos_antioquia
                (placa, vigencia, total_pagar, avaluo_comercial, retefuente, estado, expira_en, creado_en)
            VALUES (%s, %s, 0, %s, %s, 'PAZ_Y_SALVO', %s, NOW())
            ON CONFLICT (placa, vigencia) DO UPDATE SET
                total_pagar=0, avaluo_comercial=EXCLUDED.avaluo_comercial,
                retefuente=EXCLUDED.retefuente, estado='PAZ_Y_SALVO',
                expira_en=EXCLUDED.expira_en, actualizado_en=NOW()
        """, (placa.upper(), str(anio_actual), avaluo or 0, retefuente, expira))
        conn.commit()
        cur.close(); conn.close()
        print(f"  → Caché guardado PAZ_Y_SALVO para {placa}")
    except Exception as e:
        print(f"Error cache guardar paz y salvo: {e}")


def cache_antioquia_guardar_deuda(placa, vigencias_data, avaluo):
    """Guarda en caché vigencias con deuda.
    - Vigencia año actual antes del 1 agosto: expira el 31 de julio
    - Vigencia año actual desde 1 agosto, y vigencias anteriores: expira en 2 meses
    """
    try:
        ahora       = datetime.now()
        anio_actual = ahora.year
        conn = get_db_conn()
        cur  = conn.cursor()
        retefuente = round(avaluo / 100) if avaluo else 0

        for vig in vigencias_data:
            anio_vig   = int(vig.get('vigencia', 0))
            total      = vig.get('total_pagar', 0) or 0

            # Calcular expiración según reglas
            es_anio_actual    = (anio_vig == anio_actual)
            antes_de_agosto   = ahora.month < 8  # antes del 1 de agosto

            if es_anio_actual and antes_de_agosto:
                expira = f"{anio_actual}-07-31 23:59:59"
            else:
                # 2 meses desde ahora
                mes_exp  = ahora.month + 2
                anio_exp = anio_actual
                if mes_exp > 12:
                    mes_exp  -= 12
                    anio_exp += 1
                expira = f"{anio_exp}-{mes_exp:02d}-{ahora.day:02d} 23:59:59"

            expira_date = expira[:10]  # solo YYYY-MM-DD para columna date
            cur.execute("""
                INSERT INTO cache_impuestos_antioquia
                    (placa, vigencia, total_pagar, avaluo_comercial, retefuente, estado, expira_en, creado_en)
                VALUES (%s, %s, %s, %s, %s, 'CON_DEUDA', %s, NOW())
                ON CONFLICT (placa, vigencia) DO UPDATE SET
                    total_pagar=EXCLUDED.total_pagar,
                    avaluo_comercial=EXCLUDED.avaluo_comercial,
                    retefuente=EXCLUDED.retefuente,
                    estado='CON_DEUDA',
                    expira_en=EXCLUDED.expira_en,
                    actualizado_en=NOW()
            """, (placa.upper(), int(anio_vig), total, avaluo or 0, retefuente, expira_date))

        conn.commit()
        cur.close(); conn.close()
        print(f"  → Caché CON_DEUDA guardado para {placa}: {[v.get('vigencia') for v in vigencias_data]}")
    except Exception as e:
        print(f"Error cache guardar deuda: {e}")


def bloquear_recursos(page):
    page.route("**/*", lambda route: route.abort()
               if route.request.resource_type in ["image", "stylesheet", "font", "media", "other"]
               else route.continue_())


def resolver_recaptcha_2captcha(site_key, page_url, intentos=3):
    ultimo_error = None
    for intento in range(intentos):
        try:
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
        except Exception as e:
            ultimo_error = e
            if "IP_BANNED" in str(e) and intento < intentos - 1:
                time.sleep(3)
                continue
            raise
    raise ultimo_error


def resolver_turnstile_2captcha(site_key, page_url, intentos=3):
    ultimo_error = None
    for intento in range(intentos):
        try:
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
        except Exception as e:
            ultimo_error = e
            if "IP_BANNED" in str(e) and intento < intentos - 1:
                time.sleep(3)
                continue
            raise
    raise ultimo_error


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
    try:
        data1 = r1.json()
    except Exception:
        data1 = None

    if not data1 or not isinstance(data1, dict):
        raise Exception("La placa ingresada no coincide con la identificacion del propietario. Verifica los datos e intenta de nuevo.")

    if data1.get("codigo") == 0 or (not data1.get("referencia") and data1.get("mensaje")):
        mensaje = data1.get("mensaje") or data1.get("descripcion") or "La placa ingresada no coincide con la identificacion del propietario."
        raise Exception(mensaje)

    referencia = data1.get("referencia")
    if not referencia:
        raise Exception("La placa ingresada no coincide con la identificacion del propietario. Verifica los datos e intenta de nuevo.")

    opciones_nombre = (data1.get("preguntaNombrePropietario") or {}).get("opcionesPregunta", [])
    primer_apellido = apellidos_propietario.upper().split()[0] if apellidos_propietario.strip() else ""
    nombre_encontrado = next(
        (n for n in opciones_nombre if primer_apellido in n.upper()), None
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
                        municipio_cod=5001000, departamento_cod=5, job_id=None):
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

    if job_id:
        job_actualizar(job_id, "Estoy ingresando a la página de la Gobernación de Antioquia...")
    print(f"\n  → Consultando primer bloque de datos ({placa})...")
    session0, token0, data3 = _sesion_antioquia(
        placa, identificacion, tipo_documento_id,
        modelo, municipio_transito, apellidos_propietario
    )

    estado_veh          = data3.get("estadoCuenta", {})
    vigencias_adeudadas = data3.get("listaVigenciasAdeudas", [])
    avaluo              = estado_veh.get("avaluoComercial", 0) or 0
    print(f"  → Vigencias adeudadas encontradas: {len(vigencias_adeudadas)}")
    if job_id:
        if not vigencias_adeudadas:
            job_actualizar(job_id, "Este vehículo está a paz y salvo con la Gobernación de Antioquia.")
        else:
            job_actualizar(job_id, f"Encontré {len(vigencias_adeudadas)} año(s) con impuesto pendiente. Consultando valores...")

    # Paz y salvo — solo retornar si el avaluo es confiable (> 0)
    if not vigencias_adeudadas:
        if not avaluo or avaluo == 0:
            raise Exception("No se pudo obtener información completa del vehículo. Por favor intente de nuevo.")
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

    # Vigencias actualmente adeudadas según el portal
    anios_adeudados = set(str(v.get("vigencia")) for v in vigencias_a_consultar)

    # Limpiar del caché las vigencias que ya fueron pagadas
    try:
        conn_c = get_db_conn()
        cur_c  = conn_c.cursor()
        cur_c.execute("""
            SELECT vigencia FROM cache_impuestos_antioquia
            WHERE placa = %s AND estado = 'CON_DEUDA'
              AND (expira_en IS NULL OR expira_en >= NOW())
        """, (placa.upper(),))
        anios_en_cache = set(str(r[0]) for r in cur_c.fetchall())
        cur_c.close(); conn_c.close()
        for anio_pagado in (anios_en_cache - anios_adeudados):
            cache_antioquia_eliminar_vigencia(placa, anio_pagado)
    except Exception as e:
        print(f"  → Error limpiando caché: {e}")

    for v in vigencias_a_consultar:
        anio = v.get("vigencia")
        if job_id:
            job_actualizar(job_id, f"Estoy consultando el impuesto del año {anio}...")
        print(f"\n  → Consultando vigencia {anio}...")

        total_pagar  = None
        avaluo_vig   = 0

        # Intentar desde caché primero
        cache_vig = cache_antioquia_buscar_vigencia(placa, anio)
        if cache_vig:
            total_pagar = cache_vig['total_pagar']
            avaluo_vig  = cache_vig['avaluo']
            print(f"  ✔ Vigencia {anio} desde caché: ${total_pagar:,}")
        else:
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
                    _msg    = data_vig.get("mensaje") or data_vig.get("descripcion")
                    _codigo = data_vig.get("codigo")
                    if _codigo and _codigo != 1 and _msg:
                        print(f"  ✖ Error servidor vigencia {anio}: {_msg}")

                    total_pagar = data_vig.get("totalPagar")
                    avaluo_vig  = data_vig.get("avaluoComercial", 0) or 0
                    if total_pagar is not None:
                        print(f"  ✔ Vigencia {anio}: ${total_pagar:,}")
                        # Guardar en caché
                        try:
                            cache_antioquia_guardar_deuda(placa, [{
                                'vigencia': anio,
                                'total_pagar': total_pagar,
                            }], avaluo_vig or avaluo)
                            print(f"  → Caché guardado exitosamente para {placa} vigencia {anio}")
                        except Exception as ce:
                            print(f"  ✖ Error guardando caché vigencia {anio}: {ce}")
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

        if job_id and total_pagar is not None:
            job_actualizar(job_id,
                f"Año {anio}: impuesto es ${total_pagar:,}. Continuando...",
                datos_parciales=list(registros))

    print(f"\n  ✔ ¡Consulta Antioquia finalizada!")
    return registros, total_suma, avaluo_actual or avaluo, estado_veh, excede_limite



def consultar_medellin(page, placa, identificacion, modelo, apellidos_propietario,
                       celular="3208578787", email="consulta@juridicox.com",
                       direccion="CRA 20 20 20"):
    """Consulta impuesto municipal de Medellín (servicio público) con valores reales incluyendo intereses."""
    import re as _re

    url = "https://www.medellin.gov.co/irj/portal/medellin/pago-impuesto-circulacion-transito"
    page.goto(url, wait_until="domcontentloaded", timeout=60000)

    # Esperar popup de validación
    page.wait_for_selector("#popupValidacion", timeout=30000)

    # Cerrar popup de imagen si aparece
    try:
        cerrar = page.locator(".divCerrarPopup")
        if cerrar.is_visible(timeout=3000):
            cerrar.click()
            page.wait_for_timeout(500)
    except Exception:
        pass

    # Paso 0 — popup validación: servicio público + Medellín
    page.locator("input[name='tipoVehiculo'][value='publico']").check()
    page.wait_for_timeout(500)
    page.wait_for_selector("#matriculaLugar", timeout=5000)
    page.locator("input[name='lugarMatricula'][value='medellin']").check()
    page.wait_for_timeout(500)
    page.wait_for_function("() => !document.getElementById('btnContinuar').disabled", timeout=5000)
    page.locator("#btnContinuar").click()

    # Paso 1 — llenar placa y documento
    page.wait_for_selector("#placa", timeout=15000)
    page.locator("#placa").fill(placa.upper())
    page.locator("#id").fill(identificacion)
    page.locator("button.boton_consulta").click()

    # Esperar tabla de vigencias
    page.wait_for_selector("#cont_paso1 table tbody tr", timeout=30000)

    body_text = page.inner_text("body").lower()
    if "no se encuentra matriculado" in body_text or "no está matriculado" in body_text:
        raise Exception("Este vehículo no está matriculado en la Secretaría de Movilidad de Medellín.")
    if "no presenta deuda" in body_text or "no adeuda" in body_text or "paz y salvo" in body_text:
        return [], 0

    # Seleccionar todos los checkboxes de vigencias
    try:
        page.locator(".sel_todo").click(timeout=3000)
    except Exception:
        pass
    page.wait_for_timeout(500)
    # Si no quedaron todos marcados, marcarlos uno a uno
    checkboxes = page.locator("#cont_paso1 input[type='checkbox']").all()
    for cb in checkboxes:
        try:
            if not cb.is_checked():
                cb.check()
        except Exception:
            pass
    page.wait_for_timeout(500)
    # Verificar que hay checkboxes marcados antes de continuar
    marcados = page.locator("#cont_paso1 input[type='checkbox']:checked").count()
    print(f"[MED] Checkboxes marcados: {marcados}")
    btn = page.locator("button.boton_continuar").first
    disabled = btn.get_attribute("disabled")
    print(f"[MED] boton_continuar disabled={disabled}")
    # Forzar click aunque esté deshabilitado
    btn.evaluate("el => el.click()")
    page.wait_for_timeout(1000)
    print(f"[MED] Tras click: cont_paso2_visible={page.locator('#cont_paso2').is_visible()}, modelo_veh_existe={page.locator('#modelo_veh').count()}")

    # Paso 2a — modelo y propietario
    page.wait_for_selector("#modelo_veh", timeout=15000)
    modelo_str = str(modelo).strip()[:4].zfill(4)
    print(f"[MED] Modelo a llenar: '{modelo_str}'")
    page.locator("#modelo_veh").fill(modelo_str)

    # Seleccionar propietario — primera opción disponible si no hay match por apellido
    try:
        opciones = page.locator("#nombres_props option.valorSel").all()
        print(f"[MED] Opciones propietario: {[op.inner_text() for op in opciones]}")
        valor_sel = opciones[0].get_attribute("value") if opciones else None
        for op in opciones:
            texto = (op.inner_text() or "").upper()
            if apellidos_propietario and apellidos_propietario.split()[0].upper() in texto:
                valor_sel = op.get_attribute("value")
                break
        if valor_sel:
            page.locator("#nombres_props").select_option(valor_sel)
            print(f"[MED] Propietario seleccionado: {valor_sel}")
    except Exception as e:
        print(f"[MED] Error seleccionando propietario: {e}")

    # Forzar click en boton_validar ignorando validación HTML5
    page.locator("button.boton_validar").evaluate("el => el.click()")
    page.wait_for_timeout(1500)
    print(f"[MED] Tras boton_validar: correo_existe={page.locator('#correo').count()}, cont_paso2_visible={page.locator('#cont_paso2').is_visible()}")

    # Paso 2b — datos de contacto del propietario
    page.wait_for_selector("#correo", timeout=15000)
    page.locator("#correo").fill(email)
    page.locator("#celular").fill(celular)
    try:
        page.locator("#telefono").fill("6042379933")
    except Exception:
        pass

    # Dirección — abrir popup y llenar
    try:
        page.locator("#direccion").click()
        page.wait_for_selector("#tipo_via", state="visible", timeout=5000)
        page.locator("#tipo_via").select_option("CARRERA")
        page.locator("#numero1").fill("20")
        page.locator("#numero2").fill("20")
        page.locator("#numero3").fill("20")
        # Guardar dirección con evaluate para bypass validación
        page.locator("button.boton_dir").evaluate("el => el.click()")
        page.wait_for_timeout(1000)
        # Verificar que la dirección quedó guardada
        dir_val = page.locator("#direccion").input_value()
        print(f"[MED] Dirección guardada: '{dir_val}'")
    except Exception as e:
        print(f"[MED] Error dirección: {e}")
        # Si falla el popup, inyectar la dirección directamente
        try:
            page.evaluate("document.getElementById('direccion').removeAttribute('readonly')")
            page.locator("#direccion").fill("CARRERA 20 20 20")
        except Exception:
            pass

    # Departamento y municipio
    try:
        page.locator("#departamento").select_option("05")
        page.wait_for_timeout(500)
        page.locator("#municipio").select_option("000000005001")
        page.wait_for_timeout(500)
    except Exception as e:
        print(f"[MED] Error depto/municipio: {e}")

    # Guardar datos del propietario — bypass validación HTML5
    print(f"[MED] Antes guardar: dir='{page.locator('#direccion').input_value()}', depto='{page.locator('#departamento').input_value()}', mun='{page.locator('#municipio').input_value()}'")
    # Listar todos los botones disponibles para debug
    botones = page.locator("button").all()
    info_btns = [(b.get_attribute("class") or "", b.get_attribute("form") or "", b.inner_text()[:30] if b.is_visible() else "[hidden]") for b in botones]
    print(f"[MED] Todos los botones: {info_btns}")
    # Intentar el botón de guardar del form info_propietario
    try:
        page.locator("button[form='info_propietario']").first.evaluate("el => el.click()")
    except Exception:
        # Si no existe, buscar boton_continuar o cualquier submit visible
        try:
            page.locator(".divContBotones button:not(.boton_cancelar)").first.evaluate("el => el.click()")
        except Exception as e2:
            print(f"[MED] Error click guardar: {e2}")
    page.wait_for_timeout(1500)
    print(f"[MED] Tras guardar: cont_paso3_visible={page.locator('#cont_paso3').is_visible()}, tabla_filas={page.locator('#cont_paso3 table tbody tr').count()}")

    # Esperar tabla del paso 3 con valores reales
    page.wait_for_selector("#cont_paso3 table tbody tr", timeout=30000)

    # Extraer total general del tfoot
    total = 0
    try:
        tfoot_text = page.locator("#cont_paso3 table tfoot").inner_text()
        total_match = _re.search(r'\$([\d\.]+)', tfoot_text)
        if total_match:
            total = int(total_match.group(1).replace('.', ''))
    except Exception:
        pass

    # Extraer vigencias con valores reales (impuesto + intereses + total por vigencia)
    registros = []
    filas = page.locator("#cont_paso3 table tbody tr").all()
    for fila in filas:
        texto = fila.inner_text().strip()
        if not texto:
            continue
        anio = _re.search(r'\b(20\d{2}|19\d{2})\b', texto)
        # Buscar "Total a pagar" que es la última columna
        valores = _re.findall(r'\$([\d\.]+)', texto)
        if anio and valores:
            try:
                # El último valor es "Total a pagar" por vigencia
                total_vigencia = int(valores[-1].replace('.', ''))
                impuesto = int(valores[-3].replace('.', '')) if len(valores) >= 3 else 0
                interes = int(valores[-2].replace('.', '')) if len(valores) >= 2 else 0
                if total_vigencia > 0:
                    registros.append({
                        'vigencia': anio.group(),
                        'estado': 'Pendiente de pago',
                        'impuesto_base': impuesto,
                        'interes_mora': interes,
                        'total_vigencia': total_vigencia
                    })
            except ValueError:
                pass

    if not total and registros:
        total = sum(r['total_vigencia'] for r in registros)

    return registros, total

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
    "medellin":    consultar_medellin,
    "medellín":    consultar_medellin,
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

    # Municipios síncronos
    if municipio != "antioquia":
        resultado       = {}
        error_container = {}

        def ejecutar_mun():
            try:
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(headless=True, args=[
                        "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                        "--single-process", "--no-zygote", "--disable-setuid-sandbox"
                    ])
                    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                    page = context.new_page()
                    if municipio not in ["bello", "sabaneta", "laestrella"]:
                        bloquear_recursos(page)
                    funcion = MUNICIPIOS[municipio]
                    if municipio == "medellin":
                        registros, total = funcion(page, placa,
                            identificacion=identificacion,
                            modelo=modelo,
                            apellidos_propietario=apellidos,
                            celular=celular,
                            email=email)
                    else:
                        registros, total = funcion(page, placa)
                    resultado['registros'] = registros
                    resultado['total']     = total
                    context.close(); browser.close()
            except Exception as e:
                error_container['error'] = str(e)
                print(traceback.format_exc(), flush=True)

        hilo = threading.Thread(target=ejecutar_mun)
        hilo.start()
        hilo.join(timeout=620)

        if hilo.is_alive():
            return jsonify({"error": "La consulta tardo demasiado. Intenta de nuevo."}), 504
        if error_container:
            return jsonify({"error": error_container['error']}), 500
        return jsonify({
            "placa":     placa,
            "municipio": municipio,
            "registros": resultado.get('registros', []),
            "total":     resultado.get('total', 0),
            "sin_deuda": resultado.get('total', 0) == 0
        })

    # Antioquia — verificar caché de vigencias antes de lanzar Playwright
    # El snippet pasa las vigencias adeudadas que ya conoce del paso 1
    vigencias_param = request.args.get("vigencias", "").strip()
    if vigencias_param:
        anios_solicitados = [a.strip() for a in vigencias_param.split(",") if a.strip()]
        registros_cache = []
        avaluo_cache    = 0
        total_cache     = 0
        todos_cacheados = True

        for anio in anios_solicitados:
            cv = cache_antioquia_buscar_vigencia(placa, anio)
            if cv:
                registros_cache.append({
                    "vigencia":       str(anio),
                    "estado":         "Pendiente de pago",
                    "total_vigencia": cv['total_pagar'],
                })
                total_cache  += cv['total_pagar']
                if not avaluo_cache:
                    avaluo_cache = cv['avaluo']
            else:
                todos_cacheados = False
                break

        if todos_cacheados and registros_cache:
            print(f"  → Cache hit completo para {placa} — respondiendo sin Playwright")
            return jsonify({
                "placa":      placa,
                "municipio":  "antioquia",
                "placa_info": {},
                "registros":  registros_cache,
                "total":      total_cache,
                "avaluo":     avaluo_cache,
                "retefuente": round(avaluo_cache / 100) if avaluo_cache else 0,
                "sin_deuda":  False,
                "desde_cache": True,
            })

    # Antioquia — sistema asíncrono
    job_id = str(uuid.uuid4())[:12]
    job_actualizar(job_id, "Iniciando consulta...", "procesando")

    def ejecutar_antioquia():
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True, args=[
                    "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                    "--single-process", "--no-zygote", "--disable-setuid-sandbox"
                ])
                context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                page = context.new_page()
                registros, total, avaluo, estado_veh, excede = consultar_antioquia(
                    page, placa, identificacion, tipo_documento,
                    modelo, municipio_transito, apellidos,
                    celular, email, direccion, mun_declarante,
                    municipio_cod, departamento_cod, job_id=job_id
                )
                context.close(); browser.close()

            respuesta = {
                "placa":      placa,
                "municipio":  "antioquia",
                "placa_info": {
                    "marca":       estado_veh.get("marca", ""),
                    "linea":       estado_veh.get("linea", ""),
                    "modelo":      estado_veh.get("modelo", ""),
                    "propietario": estado_veh.get("nombrePropietario", ""),
                },
                "registros":  registros,
                "total":      total,
                "avaluo":     avaluo,
                "retefuente": round(avaluo / 100) if avaluo else 0,
                "sin_deuda":  len(registros) == 0,
            }
            if excede:
                respuesta["excede_limite"]  = True
                respuesta["mensaje_limite"] = f"El límite de consulta es de {ANTIOQUIA_LIMITE_VIGENCIAS} vigencias. Comunícate con un asesor de la Gobernación de Antioquia al 6044444666."
            job_terminar(job_id, respuesta)
        except Exception as e:
            print(traceback.format_exc(), flush=True)
            msg = str(e)
            if any(x in msg.lower() for x in ["net::err", "connection"]):
                msg = "No se pudo conectar al portal de Antioquia. Intenta más tarde."
            job_error(job_id, msg)

    threading.Thread(target=ejecutar_antioquia, daemon=True).start()
    return jsonify({"job_id": job_id, "estado": "procesando"})


@app.route("/consultar/antioquia/vigencias", methods=["GET"])
def consultar_antioquia_vigencias():
    """PASO 1 — Rápido (2 captchas). Devuelve lista de vigencias sin valores."""
    import traceback
    placa              = request.args.get("placa", "").upper().strip()
    identificacion     = request.args.get("identificacion", "").strip()
    tipo_documento     = request.args.get("tipo_documento", "CC").strip().upper()
    modelo             = request.args.get("modelo", "").strip()
    municipio_transito = request.args.get("municipio_transito", "").upper().strip()
    apellidos          = request.args.get("apellidos_propietario", "").upper().strip()

    if not all([placa, identificacion, modelo, municipio_transito, apellidos]):
        return jsonify({"error": "Faltan datos requeridos"}), 400

    # Verificar caché primero
    cache = cache_antioquia_buscar(placa)
    if cache and cache['estado'] == 'PAZ_Y_SALVO':
        print(f"  → Cache hit PAZ_Y_SALVO para {placa}")
        return jsonify({
            "placa":       placa,
            "sin_deuda":   True,
            "avaluo":      cache.get('avaluo', 0),
            "retefuente":  cache.get('retefuente', 0),
            "vigencias":   [],
            "placa_info":  {},
            "desde_cache": True,
        })


    resultado       = {}
    error_container = {}

    def ejecutar():
        try:
            tipo_documento_id = ANTIOQUIA_TIPO_DOC_MAP.get(tipo_documento, "1")
            if tipo_documento_id == "2":
                ident = str(identificacion) + str(_calcular_digito_nit(identificacion))
            else:
                ident = identificacion
            session0, token0, data3 = _sesion_antioquia(
                placa, ident, tipo_documento_id,
                modelo, municipio_transito, apellidos
            )
            estado_veh          = data3.get("estadoCuenta", {})
            vigencias_adeudadas = data3.get("listaVigenciasAdeudas", [])
            avaluo              = estado_veh.get("avaluoComercial", 0) or 0
            resultado['vigencias']  = vigencias_adeudadas
            resultado['avaluo']     = avaluo
            resultado['estado_veh'] = estado_veh
            resultado['sin_deuda']  = len(vigencias_adeudadas) == 0
            # Guardar en caché si está a paz y salvo
            if not vigencias_adeudadas and avaluo and avaluo > 0:
                cache_antioquia_guardar_paz_salvo(placa, avaluo, estado_veh)
        except Exception as e:
            error_container['error'] = str(e)
            print(traceback.format_exc(), flush=True)

    hilo = threading.Thread(target=ejecutar)
    hilo.start()
    hilo.join(timeout=120)

    if hilo.is_alive():
        return jsonify({"error": "La consulta tardó demasiado. Intenta de nuevo."}), 504
    if error_container:
        return jsonify({"error": error_container['error']}), 500

    estado_veh = resultado.get('estado_veh', {})
    avaluo     = resultado.get('avaluo', 0)
    vigencias  = resultado.get('vigencias', [])

    return jsonify({
        "placa":      placa,
        "sin_deuda":  resultado.get('sin_deuda', True),
        "avaluo":     avaluo,
        "retefuente": round(avaluo / 100) if avaluo else 0,
        "vigencias":  vigencias,
        "placa_info": {
            "marca":       estado_veh.get("marca", ""),
            "linea":       estado_veh.get("linea", ""),
            "modelo":      estado_veh.get("modelo", ""),
            "propietario": estado_veh.get("nombrePropietario", ""),
        }
    })


@app.route("/consultar/estado", methods=["GET"])
def consultar_estado():
    job_id = request.args.get("job_id", "").strip()
    if not job_id:
        return jsonify({"error": "Falta job_id"}), 400
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("SELECT estado, mensaje, resultado FROM consulta_jobs WHERE job_id=%s", (job_id,))
        row = cur.fetchone()
        cur.close(); conn.close()
        if not row:
            return jsonify({"estado": "no_encontrado"})
        estado, mensaje, resultado = row
        resp = {"estado": estado, "mensaje": mensaje}
        if resultado:
            # Siempre devolver resultado si existe (parcial o final)
            resp["resultado"] = resultado
        if estado == "error":
            resp["error"] = mensaje
        return jsonify(resp)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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



@app.route("/retefuente/marcas-all", methods=["GET"])
def retefuente_marcas_all():
    """Devuelve todas las marcas para una clase (tabla o clase_bd)."""
    clase      = request.args.get("clase", "").strip().upper()
    clase_bd   = request.args.get("clase_bd", "").strip().upper()
    carroceria = request.args.get("carroceria", "").strip().upper()
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        if clase_bd:
            cur.execute("SELECT DISTINCT marca FROM retefuente_2026 WHERE clase=%s ORDER BY marca", (clase_bd,))
        elif clase:
            tabla = _tabla_retefuente(clase, carroceria)
            if tabla:
                cur.execute("SELECT DISTINCT marca FROM retefuente_2026 WHERE tabla=%s ORDER BY marca", (tabla,))
            else:
                cur.execute("SELECT DISTINCT marca FROM retefuente_2026 ORDER BY marca")
        else:
            cur.execute("SELECT DISTINCT marca FROM retefuente_2026 ORDER BY marca")
        marcas = [r[0] for r in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"marcas": marcas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/retefuente/lineas", methods=["GET"])
def retefuente_lineas():
    """Devuelve las lineas para una marca (y opcionalmente clase o clase_bd)."""
    marca      = request.args.get("marca", "").strip().upper()
    clase      = request.args.get("clase", "").strip().upper()
    clase_bd   = request.args.get("clase_bd", "").strip().upper()
    carroceria = request.args.get("carroceria", "").strip().upper()
    if not marca:
        return jsonify({"error": "Debes enviar marca."}), 400
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        if clase_bd:
            cur.execute("SELECT DISTINCT linea FROM retefuente_2026 WHERE marca=%s AND clase=%s ORDER BY linea", (marca, clase_bd))
        elif clase:
            tabla = _tabla_retefuente(clase, carroceria)
            if tabla:
                cur.execute("SELECT DISTINCT linea FROM retefuente_2026 WHERE marca=%s AND tabla=%s ORDER BY linea", (marca, tabla))
            else:
                cur.execute("SELECT DISTINCT linea FROM retefuente_2026 WHERE marca=%s ORDER BY linea", (marca,))
        else:
            cur.execute("SELECT DISTINCT linea FROM retefuente_2026 WHERE marca=%s ORDER BY linea", (marca,))
        lineas = [r[0] for r in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"lineas": lineas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/retefuente/modelos", methods=["GET"])
def retefuente_modelos():
    """Devuelve los modelos (anos) disponibles."""
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'retefuente_2026'
              AND column_name LIKE 'anio_%'
            ORDER BY column_name DESC
        """)
        modelos = [r[0].replace('anio_', '').replace('_ant', ' y anteriores') for r in cur.fetchall()]
        cur.close(); conn.close()
        return jsonify({"modelos": modelos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/retefuente/opciones", methods=["GET"])
def retefuente_opciones():
    """
    Devuelve todas las opciones para marca+linea+modelo+cilindraje.
    Cilindraje >= al ingresado. Incluye clase, tonelaje, pasajeros.
    """
    marca      = request.args.get("marca", "").strip().upper()
    linea      = request.args.get("linea", "").strip().upper()
    clase      = request.args.get("clase", "").strip().upper()
    carroceria = request.args.get("carroceria", "").strip().upper()
    modelo     = request.args.get("modelo", "").strip()
    cilindraje = request.args.get("cilindraje", "0").strip()

    if not marca or not modelo:
        return jsonify({"error": "Debes enviar marca y modelo."}), 400

    # Normalizar modelo — acepta año libre, "2001 y anteriores", etc.
    modelo_norm = modelo.replace(" y anteriores", "").replace("_ant", "").strip()
    try:
        anio_int = int(modelo_norm)
    except:
        return jsonify({"error": "Modelo invalido."}), 400
    col_anio = _col_anio(str(anio_int))

    try:
        cil = int(cilindraje) if cilindraje else 0
    except:
        cil = 0

    try:
        conn = get_db_conn()
        cur  = conn.cursor()

        where  = ["marca = %s", f"{col_anio} > 0"]
        params = [marca]

        if linea:
            palabras = [p for p in linea.split() if len(p) > 2][:3]
            for p in palabras:
                where.append("linea ILIKE %s")
                params.append(f'%{p}%')

        clase_bd   = request.args.get("clase_bd", "").strip().upper()
        if clase_bd:
            where.append("clase = %s")
            params.append(clase_bd)
        elif clase:
            tabla = _tabla_retefuente(clase, carroceria)
            if tabla:
                where.append("tabla = %s")
                params.append(tabla)

        if cil > 0:
            where.append("cilindraje >= %s")
            params.append(cil)

        sql = f"""
            SELECT marca, linea, cilindraje, tabla, {col_anio} as avaluo,
                   clase, tonelaje, pasajeros
            FROM retefuente_2026
            WHERE {' AND '.join(where)}
            ORDER BY cilindraje ASC
            LIMIT 20
        """
        cur.execute(sql, params)
        rows = cur.fetchall()

        # Si no hay resultados con filtro de linea, buscar sin él
        if not rows and linea:
            where2  = ["marca = %s", f"{col_anio} > 0"]
            params2 = [marca]
            if clase_bd:
                where2.append("clase = %s")
                params2.append(clase_bd)
            elif clase:
                tabla = _tabla_retefuente(clase, carroceria)
                if tabla:
                    where2.append("tabla = %s")
                    params2.append(tabla)
            if cil > 0:
                where2.append("cilindraje >= %s")
                params2.append(cil)
            sql2 = f"""
                SELECT marca, linea, cilindraje, tabla, {col_anio} as avaluo,
                       clase, tonelaje, pasajeros
                FROM retefuente_2026
                WHERE {' AND '.join(where2)}
                ORDER BY cilindraje ASC
                LIMIT 20
            """
            cur.execute(sql2, params2)
            rows = cur.fetchall()

        cur.close(); conn.close()

        TABLA_CLASE = {
            'T1':'Automóvil','T2':'Campero/Camioneta','T3':'Camioneta D.C.',
            'T4':'Eléctrico','T5':'Motocicleta','T6':'Bus/Buseta',
            'T7':'Camión/Volqueta','T8':'Ambulancia','T9':'Híbrido'
        }

        opciones = []
        for r in rows:
            op = {
                "marca":      r[0],
                "linea":      r[1],
                "cilindraje": r[2],
                "tabla":      r[3],
                "avaluo":     r[4],
                "retefuente": round(r[4] / 100) if r[4] else 0,
                "clase_veh":  r[5] or TABLA_CLASE.get(r[3], r[3]),
                "tonelaje":   float(r[6]) if r[6] else None,
                "pasajeros":  r[7] if r[7] else None,
            }
            opciones.append(op)

        return jsonify({"opciones": opciones})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

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
    cilindraje = request.args.get("cilindraje", "0").strip()

    if not marca or not clase or not modelo:
        return jsonify({"error": "Debes enviar marca, clase y modelo."}), 400

    tabla = _tabla_retefuente(clase, carroceria)
    if not tabla:
        return jsonify({"error": f"Clase '{clase}' no tiene tabla de retefuente."}), 400

    col_anio = _col_anio(modelo)

    try:
        conn = get_db_conn()
        cur  = conn.cursor()

        # Cilindraje del vehículo para filtrar — mostrar desde (cilindraje - 100) hacia arriba
        try:
            cil_vehiculo = int(cilindraje) if cilindraje else 0
        except:
            cil_vehiculo = 0
        cil_min = max(0, cil_vehiculo - 50) if cil_vehiculo > 0 else 0

        # Función auxiliar para construir query con filtro cilindraje
        def query_retefuente(where_extra, params_extra, cil_desde, limite=8):
            cil_cond = f"AND cilindraje >= {cil_desde}" if cil_desde > 0 else ""
            order = f"CASE WHEN cilindraje >= {cil_vehiculo} THEN cilindraje ELSE cilindraje + 999999 END, linea"
            sql = f"""
                SELECT id, marca, linea, cilindraje, {col_anio} as avaluo
                FROM retefuente_2026
                WHERE tabla = %s AND marca = %s {where_extra} {cil_cond} AND {col_anio} > 0
                ORDER BY {order}
                LIMIT {limite}
            """
            cur.execute(sql, [tabla, marca] + params_extra)
            return cur.fetchall()

        # Buscar solo cilindraje >= vehiculo (exacto o superior)
        rows = []
        palabras = [p for p in linea.split() if len(p) > 2][:3]

        # 1. Con palabras de la línea + cilindraje >= vehiculo
        if palabras and linea:
            like_conds = " AND ".join(["linea ILIKE %s" for _ in palabras])
            rows = query_retefuente(f"AND {like_conds}", [f'%{p}%' for p in palabras], cil_vehiculo)

        # 2. Línea base estándar + cilindraje >= vehiculo
        if not rows:
            rows = query_retefuente(
                "AND (linea ILIKE %s OR linea ILIKE %s)",
                ['%LINEA BASE%', '%BASE ESTANDAR%'], cil_vehiculo
            )

        # 3. Todas las líneas de esa marca + cilindraje >= vehiculo
        if not rows:
            rows = query_retefuente("", [], cil_vehiculo)

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
        if campo == "departamento" and municipio:
            cur.execute("SELECT DISTINCT departamento FROM tramites_transito WHERE municipio=%s ORDER BY departamento LIMIT 1", (municipio,))
        elif campo == "departamento":
            cur.execute("SELECT DISTINCT departamento FROM tramites_transito ORDER BY departamento")
        elif campo == "municipio" and departamento:
            cur.execute("SELECT DISTINCT municipio FROM tramites_transito WHERE departamento=%s ORDER BY municipio", (departamento,))
        elif campo == "municipio" and not departamento:
            cur.execute("SELECT DISTINCT municipio FROM tramites_transito ORDER BY municipio")
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


@app.route("/reportar", methods=["POST"])
def reportar():
    try:
        data      = request.get_json()
        tipo      = data.get("tipo", "").strip()
        comentario = data.get("comentario", "").strip()
        placa     = data.get("placa", "").strip().upper()
        municipio = data.get("municipio", "").strip().upper()
        pagina    = data.get("pagina", "").strip()
        if not tipo:
            return jsonify({"ok": False, "error": "Tipo requerido"}), 400
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO reportes_usuarios (tipo, comentario, placa, municipio, pagina)
            VALUES (%s, %s, %s, %s, %s)
        """, (tipo, comentario, placa, municipio, pagina))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/reportar/lista", methods=["GET"])
def reportar_lista():
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT id, tipo, comentario, placa, municipio, pagina, creado_en
            FROM reportes_usuarios
            ORDER BY creado_en DESC
            LIMIT 100
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"reportes": [{
            "id": r[0], "tipo": r[1], "comentario": r[2],
            "placa": r[3], "municipio": r[4], "pagina": r[5],
            "fecha": str(r[6])
        } for r in rows]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reportar/eliminar/<int:reporte_id>", methods=["DELETE"])
def reportar_eliminar(reporte_id):
    try:
        conn = get_db_conn()
        cur  = conn.cursor()
        cur.execute("DELETE FROM reportes_usuarios WHERE id = %s", (reporte_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500





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
