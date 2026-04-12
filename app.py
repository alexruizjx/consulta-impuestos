# ═══════════════════════════════════════════════════════════════
#  INSTRUCCIONES:
#  1. Agrega la función consultar_laestrella() a tu app.py
#  2. Agrega "laestrella" al diccionario MUNICIPIOS
#  3. Asegúrate de tener: import requests (al inicio del archivo)
# ═══════════════════════════════════════════════════════════════


# ── PASO 1: Agrega esta función junto a las demás (consultar_envigado, etc.) ──

def consultar_laestrella(page, placa):
    """
    Consulta impuesto vehicular en EMTRASUR - La Estrella.
    Intenta primero la API directa. Si falla por captcha,
    usa Playwright para navegar el portal normalmente.
    """
    import requests

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept":     "application/json, text/plain, */*",
        "Referer":    "https://sistematizacion.emtrasur.com.co/",
        "Origin":     "https://sistematizacion.emtrasur.com.co",
    }

    # ── Intento 1: API directa (sin captcha) ──────────────────
    try:
        url  = f"https://sistematizacion.emtrasur.com.co/api/Sistematizacion/{placa}"
        resp = requests.get(url, headers=HEADERS, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            if data.get("Success"):
                return _parsear_emtrasur(data.get("Data", []))
    except Exception:
        pass

    # ── Intento 2: Playwright (con captcha resuelto por el portal) ──
    resultado_api = []

    def capturar_respuesta(response):
        nonlocal resultado_api
        if f"/api/Sistematizacion/{placa}" in response.url and response.status == 200:
            try:
                data = response.json()
                if data.get("Success"):
                    resultado_api = data.get("Data", [])
            except Exception:
                pass

    page.on("response", capturar_respuesta)
    page.goto("https://sistematizacion.emtrasur.com.co/", wait_until="networkidle")
    page.wait_for_timeout(2000)

    # Ingresar placa
    campo = page.wait_for_selector('input[type="text"]', timeout=8000)
    campo.fill(placa)

    # Marcar checkbox captcha simple
    for sel in ['input[type="checkbox"]', '[class*="captcha" i]']:
        els = page.query_selector_all(sel)
        if els:
            els[0].click()
            page.wait_for_timeout(800)
            break

    # Clic en Consultar
    for sel in ['button:has-text("Consultar")', 'button[type="submit"]']:
        try:
            btn = page.wait_for_selector(sel, timeout=3000)
            if btn:
                btn.click()
                break
        except Exception:
            continue

    # Esperar respuesta de la API
    for _ in range(20):
        if resultado_api:
            break
        page.wait_for_timeout(500)

    return _parsear_emtrasur(resultado_api)


def _parsear_emtrasur(data: list):
    """Convierte la respuesta de EMTRASUR al formato estándar de la API."""
    registros = []
    for r in data:
        valor = r.get("ValorPorFacturar", 0)
        registros.append({
            "vigencia":       str(r.get("AnioNoFacturado", "")),
            "estado":         "Pendiente de pago",
            "total_vigencia": valor,
            # Campos extra de EMTRASUR
            "tipo_vehiculo":  r.get("TipoVehiculo", ""),
            "ultimo_pago":    r.get("AnioPagado", ""),
            "descripcion":    r.get("DescripcionNoFacturada", "").strip(),
        })
    total = sum(r["total_vigencia"] for r in registros)
    return registros, total


# ── PASO 2: Agrega "laestrella" al diccionario MUNICIPIOS ────────────────────
#
# Busca en tu app.py:
#
#   MUNICIPIOS = {
#       "envigado": consultar_envigado,
#       "sabaneta": consultar_sabaneta,
#       "itagui":   consultar_itagui,
#       "bello":    consultar_bello,
#   }
#
# Y reemplázalo por:
#
#   MUNICIPIOS = {
#       "envigado":   consultar_envigado,
#       "sabaneta":   consultar_sabaneta,
#       "itagui":     consultar_itagui,
#       "bello":      consultar_bello,
#       "laestrella": consultar_laestrella,   # ← nueva línea
#   }
