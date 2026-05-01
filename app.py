<!-- Formulario Consulta Vehicular Antioquia v6 -->

<style>
  .ant-app-navbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    background: #1a2340; height: 48px;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.18);
  }
  .ant-app-navbar-titulo {
    font-family: Arial, sans-serif; font-size: 16px; font-weight: 900;
    color: #fff; letter-spacing: 1px;
  }
  .ant-app-navbar-salir {
    font-family: Arial, sans-serif; font-size: 13px; font-weight: 700;
    color: #fff; text-decoration: none; padding: 6px 14px;
    border: 1px solid rgba(255,255,255,0.3); border-radius: 6px;
    transition: background .2s;
  }
  .ant-app-navbar-salir:hover { background: rgba(255,255,255,0.12); }

  .ant-wrap { max-width: 760px; margin: 0 auto; padding: 58px 8px 24px 8px; font-family: Arial, sans-serif; }

  .ant-top { background: #fff; border: 1px solid #dde3ec; border-radius: 10px; padding: 13px 18px; margin-bottom: 10px; }

  .ant-card { background: #fff; border: 1px solid #dde3ec; border-radius: 10px; padding: 16px 18px; margin-bottom: 10px; display: none; }
  .ant-card.visible { display: block; }
  .ant-card-liq { background: #fff; border: 1px solid #dde3ec; border-radius: 10px; padding: 16px 18px; margin-bottom: 10px; }

  .ant-bloque-titulo {
    font-size: 13px; font-weight: 700; color: #fff;
    background: #1a2340; border-radius: 7px;
    padding: 9px 14px; margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
  }

  .ant-bienvenida { text-align: center; padding: 4px 20px 6px; margin-bottom: 6px; }
  .ant-bienvenida-titulo { font-size: 22px; font-weight: 900; color: #0047AB; margin-bottom: 6px; }
  .ant-bienvenida-sub { font-size: 15px; color: #555; line-height: 1.6; }

  /* Botones entrada */
  .ant-entrada-btns { display: flex; gap: 8px; margin-bottom: 14px; }
  .ant-entrada-btn {
    flex: 1; padding: 10px 6px; border: 2px solid #dde3ec; border-radius: 9px;
    background: #f8fafc; cursor: pointer; font-size: 12px; font-weight: 700;
    color: #1a2340; text-align: center; transition: all .2s;
  }
  .ant-entrada-btn:hover { border-color: #3b7de8; background: #f0f6ff; color: #1a5fa8; }
  .ant-entrada-btn.activo { border-color: #1a5fa8; background: #e8f0f8; color: #1a5fa8; }
  .ant-entrada-btn .ant-entrada-icon { font-size: 22px; display: block; margin-bottom: 4px; }

  /* Municipio */
  .ant-mun-wrap { position: relative; }
  .ant-mun-input {
    width: 100%; padding: 10px 14px; border: 1px solid #ccd3de;
    border-radius: 7px; font-size: 16px; box-sizing: border-box;
    outline: none; transition: border .2s; background: #fff;
    text-align: center;
  }
  .ant-mun-input:focus { border-color: #3b7de8; }
  .ant-mun-lista {
    border: 1px solid #ccd3de; border-top: none;
    border-radius: 0 0 7px 7px; max-height: 200px;
    overflow-y: auto; background: white;
    position: absolute; width: 100%; z-index: 1000; display: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  }
  .ant-mun-lista div { padding: 10px 14px; cursor: pointer; font-size: 16px; text-align: center; }
  .ant-mun-lista div:hover, .ant-mun-lista div.activo { background: #e8f0f8; font-weight: 600; }

  .ant-mun-confirm {
    display: none; margin-top: 14px; text-align: center;
    background: #f0f6ff; border: 1px solid #c5d8f5;
    border-radius: 10px; padding: 16px 20px;
  }
  .ant-mun-confirm-texto { font-size: 14px; color: #1a2340; margin-bottom: 12px; }
  .ant-mun-confirm-texto strong { font-size: 16px; color: #0047AB; }
  .ant-mun-confirm-btns { display: flex; gap: 10px; justify-content: center; }
  .ant-mun-confirm-btn { padding: 9px 20px; border: none; border-radius: 7px; font-size: 14px; font-weight: 700; cursor: pointer; transition: background .2s; }
  .ant-mun-confirm-si  { background: #1a6e3c; color: #fff; }
  .ant-mun-confirm-si:hover  { background: #2a9e5c; }
  .ant-mun-confirm-no  { background: #e8f0f8; color: #1a2340; border: 1px solid #c5d8f5; }
  .ant-mun-confirm-no:hover  { background: #d0e0f0; }

  /* OCR */
  .ant-ocr-zone {
    border: 2px dashed #3b7de8; border-radius: 10px; padding: 22px;
    text-align: center; background: #f0f6ff; cursor: pointer;
    margin-bottom: 14px; transition: background 0.2s; position: relative;
  }
  .ant-ocr-zone:hover, .ant-ocr-zone.dragover { background: #dceeff; border-color: #1a2340; }
  .ant-ocr-zone input[type="file"] { position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer; z-index: 2; }
  .ant-ocr-icon { font-size: 30px; margin-bottom: 4px; }
  .ant-ocr-texto { font-size: 14px; color: #3b7de8; font-weight: 600; }
  .ant-ocr-sub { font-size: 12px; color: #888; margin-top: 3px; }
  .ant-ocr-preview { max-height: 130px; border-radius: 7px; margin-top: 8px; border: 1px solid #ccd3de; position: relative; z-index: 1; display: block; margin-left: auto; margin-right: auto; }
  .ant-ocr-status { font-size: 26px; line-height: 1.4; margin-top: 8px; padding: 12px 16px; border-radius: 6px; display: none; text-align: center; font-weight: 700; }
  .ant-ocr-status.procesando { background: #fff3cd; color: #856404; }
  .ant-ocr-status.ok  { background: #f0fff6; color: #1a6e3c; }
  .ant-ocr-status.err { background: #fff0f0; color: #c0392b; }

  /* Campos */
  .ant-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 8px; }
  .ant-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 14px; }
  @media(max-width: 560px) { .ant-grid { grid-template-columns: repeat(2, 1fr); } }
  .ant-group { position: relative; }
  .ant-label { display: block; font-size: 11px; font-weight: 700; color: #555; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.4px; }
  .ant-input {
    width: 100%; padding: 9px 12px; border: 1px solid #ccd3de;
    border-radius: 7px; font-size: 14px; box-sizing: border-box;
    outline: none; transition: border .2s; background: #fff;
  }
  .ant-input:focus { border-color: #3b7de8; }
  .ant-input.upper { text-transform: uppercase; }

  /* Botones */
  .ant-btn {
    width: auto; padding: 9px 3px; border: none; border-radius: 7px;
    font-size: 14px; font-weight: 700; cursor: pointer;
    transition: background .2s; display: flex;
    align-items: center; justify-content: center; gap: 8px; margin-top: 12px;
    min-width: 140px; margin-left: auto; margin-right: auto;
  }
  .ant-btn-verde  { background: #1a6e3c; color: #fff; }
  .ant-btn-verde:hover  { background: #2a9e5c; }
  .ant-btn-azul   { background: #1a5fa8; color: #fff; }
  .ant-btn-azul:hover   { background: #2a7fd8; }
  .ant-btn-wa     { background: #25D366; color: #fff; }
  .ant-btn-wa:hover     { background: #1da851; }
  .ant-btn:disabled { background: #9aabc2; cursor: not-allowed; }

  .ant-no-depto { background: #fff3cd; border: 1px solid #ffc107; border-radius: 7px; padding: 10px 14px; color: #856404; font-size: 13px; font-weight: 600; display: none; }

  /* Tramites con autocomplete y X */
  .ant-tramite-bloque { background: #f8fafc; border: 1px solid #e0e7ef; border-radius: 8px; padding: 12px; margin-bottom: 10px; position: relative; }
  .ant-tramite-num { font-size: 11px; font-weight: 700; color: #1a5fa8; text-transform: uppercase; margin-bottom: 7px; display: flex; justify-content: space-between; align-items: center; }
  .ant-tramite-x {
    background: none; border: none; color: #c0392b; font-size: 18px; font-weight: 900;
    cursor: pointer; padding: 0 4px; line-height: 1; display: none;
  }
  .ant-tramite-x:hover { color: #e74c3c; }

  /* Autocomplete tramite */
  .ant-tram-wrap { position: relative; }
  .ant-tram-input {
    width: 100%; padding: 9px 12px; border: 1px solid #ccd3de;
    border-radius: 7px; font-size: 14px; box-sizing: border-box;
    outline: none; background: #fff; transition: border .2s;
  }
  .ant-tram-input:focus { border-color: #3b7de8; }
  .ant-tram-input:disabled { background: #f5f5f5; color: #999; cursor: not-allowed; }
  .ant-tram-lista {
    border: 1px solid #ccd3de; border-top: none;
    border-radius: 0 0 7px 7px; max-height: 180px;
    overflow-y: auto; background: white;
    position: absolute; width: 100%; z-index: 1000; display: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }
  .ant-tram-lista div { padding: 9px 14px; cursor: pointer; font-size: 13px; }
  .ant-tram-lista div:hover, .ant-tram-lista div.activo { background: #e8f0f8; font-weight: 600; }

  .ant-tarifa-precio-inline {
    display: none; margin-top: 7px; padding: 7px 12px;
    background: #e8f5e9; border: 1px solid #a5d6a7; border-radius: 6px;
    font-size: 14px; color: #1a6e3c; font-weight: 700;
  }

  /* Resultados */
  .ant-result { margin-top: 12px; }
  .ant-alert  { padding: 12px 16px; border-radius: 7px; font-size: 14px; margin-bottom: 10px; }
  .ant-alert.error   { background: #fff0f0; border: 1px solid #f5c6c6; color: #c0392b; }
  .ant-alert.success { background: #f0fff6; border: 1px solid #b2e4c8; color: #1a6e3c; }
  .ant-info { display: flex; gap: 16px; margin-bottom: 12px; flex-wrap: wrap; }
  .ant-info-item label { font-size: 11px; color: #888; display: block; margin-bottom: 2px; }
  .ant-info-item span  { font-size: 13px; font-weight: 600; color: #1a2340; }
  .ant-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .ant-table th { background: #f4f6fb; color: #555; font-weight: 600; padding: 8px 10px; text-align: left; border-bottom: 2px solid #dde3ec; }
  .ant-table td { padding: 8px 10px; border-bottom: 1px solid #eef0f5; color: #333; }
  .ant-table tr:last-child td { border-bottom: none; }
  .ant-total-bar { display: flex; justify-content: space-between; align-items: center; background: #1a2340; color: #fff; border-radius: 7px; padding: 12px 16px; margin-top: 12px; }
  .ant-total-bar span:first-child { font-size: 13px; opacity: .85; }
  .ant-total-bar span:last-child  { font-size: 20px; font-weight: 700; }
  .ant-extra { display: flex; justify-content: space-between; padding: 8px 14px; background: #f4f6fb; border-radius: 6px; margin-top: 6px; font-size: 13px; color: #444; }
  .ant-loading { display: flex; align-items: center; gap: 12px; padding: 18px 0; color: #555; font-size: 14px; }
  .ant-spinner-ring { width: 24px; height: 24px; border-radius: 50%; flex-shrink: 0; border: 3px solid #dde3ec; border-top-color: #1a2340; animation: ant-spin .8s linear infinite; }
  @keyframes ant-spin { to { transform: rotate(360deg); } }
  .ant-warning { background: #fff3cd; border: 1px solid #ffc107; border-radius: 7px; padding: 10px 14px; color: #856404; font-size: 13px; margin-top: 10px; }

  /* Liquidacion */
  .ant-liq-item { display: grid; grid-template-columns: 1fr auto; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid #eef0f5; }
  .ant-liq-item:last-child { border-bottom: none; }
  .ant-liq-nombre { font-size: 13px; color: #444; font-weight: 600; }
  .ant-liq-input { width: 140px; padding: 7px 10px; border: 1px solid #ccd3de; border-radius: 6px; font-size: 13px; text-align: right; box-sizing: border-box; outline: none; }
  .ant-liq-input:focus { border-color: #3b7de8; }
  .ant-liq-total { background: #1a2340; color: #fff; border-radius: 8px; padding: 14px 18px; margin-top: 16px; display: flex; justify-content: space-between; align-items: center; }
  .ant-liq-total span:first-child { font-size: 14px; opacity: .85; }
  .ant-liq-total span:last-child  { font-size: 24px; font-weight: 900; }
  .ant-liq-nota { font-size: 11px; color: #888; margin-top: 8px; text-align: center; }
  .ant-liq-cobro { display: grid; grid-template-columns: 1fr 140px 32px; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #eef0f5; }
  .ant-liq-cobro-nombre { font-size: 13px; color: #444; border: 1px solid #ccd3de; border-radius: 6px; padding: 6px 10px; outline: none; width: 100%; box-sizing: border-box; }
  .ant-liq-cobro-nombre:focus { border-color: #3b7de8; }
  .ant-liq-btn-add { background: #1a5fa8; color: #fff; border: none; border-radius: 6px; width: 32px; height: 32px; font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background .2s; flex-shrink: 0; }
  .ant-liq-btn-add:hover { background: #2a7fd8; }
  .ant-liq-btn-del { background: #c0392b; color: #fff; border: none; border-radius: 6px; width: 32px; height: 32px; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background .2s; flex-shrink: 0; }
  .ant-liq-btn-del:hover { background: #e74c3c; }
  .ant-wa-preview { margin-top: 12px; border-radius: 8px; overflow: hidden; border: 1px solid #dde3ec; display: none; }
  .ant-wa-preview img { width: 100%; display: block; }

  /* Retefuente */
  .ant-ret-opcion {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 14px; border: 1px solid #dde3ec; border-radius: 7px;
    margin-bottom: 8px; cursor: pointer; transition: background .2s;
    font-size: 13px;
  }
  .ant-ret-opcion:hover { background: #f0f6ff; border-color: #3b7de8; }
  .ant-ret-opcion.seleccionada { background: #e8f5e9; border-color: #1a6e3c; }
  .ant-ret-opcion-nombre { color: #1a2340; font-weight: 600; flex: 1; }
  .ant-ret-opcion-valor { color: #1a6e3c; font-weight: 700; text-align: right; min-width: 120px; }

  /* Preview con orientación */
  .ant-preview-wrap { display: none; margin-bottom: 12px; }
  .ant-preview-aviso {
    background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px;
    padding: 10px 14px; font-size: 15px; color: #856404; font-weight: 600;
    margin-bottom: 8px; text-align: center;
  }
  .ant-preview-img-wrap { position: relative; text-align: center; margin-bottom: 8px; }
  .ant-preview-img-wrap img { max-height: 180px; border-radius: 8px; border: 1px solid #ccd3de; transition: transform 0.3s; }
  .ant-btn-girar {
    display: flex; align-items: center; justify-content: center; gap: 6px;
    background: #1a5fa8; color: #fff; border: none; border-radius: 7px;
    padding: 11px 24px; font-size: 15px; font-weight: 700; cursor: pointer;
    margin: 0 auto 10px auto; transition: background .2s;
  }
  .ant-btn-girar:hover { background: #2a7fd8; }
  .ant-btn-continuar {
    display: flex; align-items: center; justify-content: center; gap: 6px;
    background: #1a6e3c; color: #fff; border: none; border-radius: 7px;
    padding: 11px 24px; font-size: 15px; font-weight: 700; cursor: pointer;
    margin: 0 auto; transition: background .2s; width: 100%;
  }
  .ant-btn-continuar:hover { background: #2a9e5c; }
</style>

<div class="ant-app-navbar">
  <span class="ant-app-navbar-titulo">🚗 TRAMY</span>
  <a href="https://juridicox.com/" class="ant-app-navbar-salir">Salir →</a>
</div>

<div class="ant-wrap">

  <!-- OCR + MUNICIPIO — SIEMPRE VISIBLES -->
  <div class="ant-top">
    <div class="ant-bienvenida" id="ant-bienvenida">
      <div style="text-align:center; margin-bottom:6px;">
        <span style="font-size:18px; font-weight:900; color:#0047AB;">Hola, </span><span style="font-size:32px; font-weight:900; color:#0047AB;">soy Tramy</span>
      </div>
      <div style="font-size:16px; color:#1a2340; text-align:center; line-height:1.6; font-family:Arial, sans-serif; font-weight:700;">Hagamos esto juntos.<br>Yo liquido, tú haces la magia.</div>
    </div>

    <!-- Botones de entrada -->
    <div class="ant-entrada-btns">
      <div class="ant-entrada-btn" id="btn-entrada-camara" onclick="antModoEntrada('camara')">
        <span class="ant-entrada-icon">📷</span>
        Tomar foto
      </div>
      <div class="ant-entrada-btn activo" id="btn-entrada-ocr" onclick="antModoEntrada('ocr')">
        <span class="ant-entrada-icon">🖼️</span>
        Subir o arrastrar
      </div>
      <div class="ant-entrada-btn" id="btn-entrada-manual" onclick="antModoEntrada('manual')">
        <span class="ant-entrada-icon">✏️</span>
        Ingresar manualmente
      </div>
    </div>

    <!-- Input cámara (oculto) -->
    <input type="file" id="ant-camara-file" accept="image/*" capture="environment" style="display:none">

    <!-- Zona OCR (subir/arrastrar) -->
    <div id="ant-zona-ocr">
      <div class="ant-ocr-zone" id="ant-ocr-zone">
        <input type="file" id="ant-ocr-file" accept="image/*">
        <div class="ant-ocr-icon">🖼️</div>
        <div class="ant-ocr-texto">Haz clic aqui o arrastra la tarjeta de propiedad</div>
        <div class="ant-ocr-sub">JPG, PNG o WEBP</div>
      </div>
      <!-- Panel de orientación -->
      <div class="ant-preview-wrap" id="ant-preview-wrap">
        <div class="ant-preview-aviso">⚠️ Mira que la foto esté bien orientada.<br>Si se te dificulta a ti leerla, a mí también.</div>
        <div class="ant-preview-img-wrap">
          <img id="ant-ocr-preview" src="">
        </div>
        <div style="display:flex; gap:8px; margin-bottom:10px;">
          <button class="ant-btn-girar" style="flex:1; margin:0;" onclick="antGirarImagen()">↻ Girar imagen</button>
          <button onclick="antEliminarImagen()" style="
            background:#c0392b; color:#fff; border:none; border-radius:7px;
            padding:11px 16px; font-size:15px; font-weight:700; cursor:pointer;
            transition:background .2s;" onmouseover="this.style.background='#e74c3c'" onmouseout="this.style.background='#c0392b'">
            🗑 Eliminar
          </button>
        </div>
        <button class="ant-btn-continuar" onclick="antContinuarOCR()">✓ La foto está bien, continuar</button>
      </div>
      <div class="ant-ocr-status" id="ant-ocr-status"></div>
    </div>

    <!-- Municipio -->
    <div id="ant-municipio-wrap" style="margin-top:14px; display:none; text-align:center;">
      <div class="ant-mun-confirm" id="ant-mun-confirm">
        <div class="ant-mun-confirm-texto">El municipio registrado es <strong id="ant-mun-confirm-nombre"></strong>. Es correcto?</div>
        <div class="ant-mun-confirm-btns">
          <button class="ant-mun-confirm-btn ant-mun-confirm-si" onclick="antConfirmarMunicipio(true)">Si, es correcto</button>
          <button class="ant-mun-confirm-btn ant-mun-confirm-no" onclick="antConfirmarMunicipio(false)">No, quiero cambiarlo</button>
        </div>
      </div>
      <label class="ant-label" for="ant-municipio-input" id="ant-mun-label" style="text-align:center; display:none;">Municipio</label>
      <div class="ant-mun-wrap" id="ant-mun-campo" style="max-width:400px; margin:0 auto; display:none;">
        <input type="text" class="ant-mun-input" id="ant-municipio-input" placeholder="Escribe o selecciona el municipio..." autocomplete="off">
        <input type="hidden" id="ant-municipio">
        <div class="ant-mun-lista" id="ant-mun-lista"></div>
      </div>
    </div>
  </div>

  <!-- BLOQUE 1 — INFORMACION -->
  <div class="ant-card" id="bloque-info">
    <!-- Cabecera con colapso -->
    <div class="ant-bloque-titulo" style="cursor:pointer; justify-content:space-between;" onclick="antToggleInfo()">
      <span>1. Informacion</span>
      <span id="ant-info-chevron" style="font-size:16px;">▲</span>
    </div>

    <!-- Vista colapsada -->
    <div id="ant-info-colapsado" style="display:none; padding:6px 0 4px 0; font-size:13px; color:#555;">
      <span id="ant-info-resumen"></span>
      <span style="color:#1a5fa8; font-weight:700; margin-left:8px; cursor:pointer;" onclick="antToggleInfo()">Ver todo ▼</span>
    </div>

    <!-- Contenido completo -->
    <div id="ant-info-contenido">
      <div style="margin-bottom:8px; text-align:center;">
        <label class="ant-label" style="text-align:center; display:none;">Placa</label>
        <div style="
          display:inline-block; position:relative; margin-top:4px;
          box-shadow: 3px 3px 10px rgba(0,0,0,0.25); border-radius:6px; overflow:hidden;
        ">
          <!-- Fondo placa colombiana -->
          <div style="
            background:#FDD835; border:3px solid #111;
            border-radius:6px; padding:8px 10px 6px 10px; width:220px;
            position:relative; box-sizing:border-box;
          ">
            <!-- Caracteres + escudo en fila -->
            <div style="display:flex; align-items:center; justify-content:center; gap:0;">

              <!-- Primeras 3 letras -->
              <div id="ant-placa-letras" style="
                font-size:28px; font-weight:900; letter-spacing:4px;
                color:#111; font-family:'Arial Black', Arial, sans-serif;
                min-width:80px; text-align:center;
              ">---</div>

              <!-- Últimos 3 caracteres -->
              <div id="ant-placa-numeros" style="
                font-size:28px; font-weight:900; letter-spacing:4px;
                color:#111; font-family:'Arial Black', Arial, sans-serif;
                min-width:80px; text-align:center;
              ">---</div>
            </div>

            <!-- Input oculto que guarda el valor real -->
            <input id="ant-placa" type="text" maxlength="7"
              style="position:absolute; opacity:0; pointer-events:none; width:1px; height:1px;">

            <!-- Municipio -->
            <div id="ant-placa-municipio" style="
              font-size:10px; font-weight:900; color:#111; text-align:center;
              letter-spacing:2px; margin-top:3px; text-transform:uppercase;
            ">MUNICIPIO</div>
          </div>


        </div>
      </div>

      <div class="ant-grid">
        <div class="ant-group">
          <label class="ant-label" for="ant-tipodoc">Tipo Documento</label>
          <select class="ant-input" id="ant-tipodoc">
            <option value="CC">C.C. - Cedula de Ciudadania</option>
            <option value="NIT">NIT</option>
            <option value="CE">C.E. - Cedula de Extranjeria</option>
            <option value="TI">T.I. - Tarjeta de Identidad</option>
            <option value="RC">R.C. - Registro Civil</option>
            <option value="PPT">P.P.T. - Permiso por Proteccion Temporal</option>
          </select>
        </div>
        <div class="ant-group">
          <label class="ant-label" for="ant-cedula">Identificacion</label>
          <input class="ant-input" id="ant-cedula" type="text" inputmode="numeric" placeholder="Ej: 1128402520">
        </div>
        <div class="ant-group">
          <label class="ant-label" for="ant-apellidos">Apellidos / Razon Social</label>
          <input class="ant-input upper" id="ant-apellidos" type="text" placeholder="Ej: LOPEZ AGUDELO">
        </div>
        <div class="ant-group">
          <label class="ant-label" for="ant-modelo">Modelo</label>
          <input class="ant-input" id="ant-modelo" type="text" inputmode="numeric" placeholder="Ej: 2015" maxlength="4">
        </div>
        <div class="ant-group" style="display:none;">
          <label class="ant-label">Municipio</label>
          <input class="ant-input upper" id="ant-municipio-info" type="text" readonly style="background:#f4f6fb; color:#1a2340; font-weight:700;">
        </div>
        <div class="ant-group">
          <label class="ant-label" for="ant-marca">Marca</label>
          <input class="ant-input upper" id="ant-marca" type="text" placeholder="Ej: CHEVROLET">
        </div>
        <div class="ant-group">
          <label class="ant-label" for="ant-linea">Linea</label>
          <input class="ant-input upper" id="ant-linea" type="text" placeholder="Ej: SPARK">
        </div>
        <div class="ant-group">
          <label class="ant-label" for="ant-cilindrada">Cilindraje (cc)</label>
          <input class="ant-input" id="ant-cilindrada" type="text" placeholder="Ej: 1200">
        </div>
        <div class="ant-group">
          <label class="ant-label" for="ant-capacidad">Capacidad</label>
          <input class="ant-input" id="ant-capacidad" type="text" placeholder="Ej: 5">
        </div>
        <div class="ant-group" style="display:none;">
          <label class="ant-label" for="ant-carroceria">Carroceria</label>
          <input class="ant-input upper" id="ant-carroceria" type="text" placeholder="Ej: SEDAN">
        </div>
        <div class="ant-group">
          <label class="ant-label" for="ant-clase">Clase de Vehiculo</label>
          <input class="ant-input upper" id="ant-clase" type="text" placeholder="Ej: AUTOMOVIL">
        </div>
        <div class="ant-group">
          <label class="ant-label" for="ant-servicio">Servicio</label>
          <input class="ant-input upper" id="ant-servicio" type="text" placeholder="Ej: PARTICULAR">
        </div>
      </div>

      <button class="ant-btn ant-btn-verde" onclick="antConfirmarInfo()" style="margin-top:8px;">
        ✓ He comparado los datos y están bien
      </button>
    </div>
  </div>

  <!-- BLOQUE 2 — IMPUESTO DEPARTAMENTAL -->
  <div class="ant-card" id="bloque-depto">
    <div class="ant-bloque-titulo" style="cursor:pointer;justify-content:space-between;" onclick="antToggleBloque('depto')">
      <span>2. Impuesto Departamental</span><span id="chevron-depto">▲</span>
    </div>
    <div id="contenido-depto">
    <div class="ant-no-depto" id="ant-no-depto" style="display:none">⚠️ Este vehiculo NO PAGA IMPUESTOS DEPARTAMENTALES</div>
    <button class="ant-btn ant-btn-verde" id="ant-btn-impuesto" style="display:none">🏛️ Consultar</button>
    <div class="ant-result" id="ant-result-depto"></div>
    </div>
  </div>

  <!-- BLOQUE 3 — IMPUESTO MUNICIPAL -->
  <div class="ant-card" id="bloque-municipal">
    <div class="ant-bloque-titulo" style="cursor:pointer;justify-content:space-between;" onclick="antToggleBloque('municipal')">
      <span>3. Impuesto Municipal</span><span id="chevron-municipal">▲</span>
    </div>
    <div id="contenido-municipal">
    <button class="ant-btn ant-btn-azul" id="ant-btn-municipal">🏘️ Consultar</button>
    <div class="ant-result" id="ant-result-municipal"></div>
    </div>
  </div>

  <!-- BLOQUE 4 — TRAMITES -->
  <div class="ant-card" id="bloque-tramites">
    <div class="ant-bloque-titulo" style="cursor:pointer;justify-content:space-between;" onclick="antToggleBloque('tramites')">
      <span>4. Tramites</span><span id="chevron-tramites">▲</span>
    </div>
    <div id="contenido-tramites">
    <div class="ant-tramite-bloque" id="ant-bloque-1">
      <div class="ant-tramite-num">
        <span>Tramite 1</span>
      </div>
      <div class="ant-tram-wrap">
        <input type="text" class="ant-tram-input" id="ant-tramite-1" placeholder="Escribe para filtrar tramites..." autocomplete="off" disabled>
        <div class="ant-tram-lista" id="ant-tram-lista-1"></div>
      </div>
      <div class="ant-tarifa-precio-inline" id="ant-precio-1"></div>
    </div>
    <div class="ant-tramite-bloque" id="ant-bloque-2" style="display:none">
      <div class="ant-tramite-num">
        <span>Tramite 2</span>
        <button class="ant-tramite-x" id="ant-x-2" onclick="antEliminarTramite(2)" title="Eliminar">✕</button>
      </div>
      <div class="ant-tram-wrap">
        <input type="text" class="ant-tram-input" id="ant-tramite-2" placeholder="Escribe para filtrar tramites..." autocomplete="off" disabled>
        <div class="ant-tram-lista" id="ant-tram-lista-2"></div>
      </div>
      <div class="ant-tarifa-precio-inline" id="ant-precio-2"></div>
    </div>
    <div class="ant-tramite-bloque" id="ant-bloque-3" style="display:none">
      <div class="ant-tramite-num">
        <span>Tramite 3</span>
        <button class="ant-tramite-x" id="ant-x-3" onclick="antEliminarTramite(3)" title="Eliminar">✕</button>
      </div>
      <div class="ant-tram-wrap">
        <input type="text" class="ant-tram-input" id="ant-tramite-3" placeholder="Escribe para filtrar tramites..." autocomplete="off" disabled>
        <div class="ant-tram-lista" id="ant-tram-lista-3"></div>
      </div>
      <div class="ant-tarifa-precio-inline" id="ant-precio-3"></div>
    </div>
    </div>
  </div>

  <!-- BLOQUE RETEFUENTE -->
  <div class="ant-card" id="bloque-retefuente" style="display:none;">
    <div class="ant-bloque-titulo" style="cursor:pointer;justify-content:space-between;" onclick="antToggleBloque('ret')">
      <span>🔍 Consultar Retefuente</span><span id="chevron-ret">▲</span>
    </div>
    <div id="contenido-ret">
      <p style="font-size:13px; color:#555; margin:0 0 12px 0;">
        Selecciona la línea que corresponde a tu vehículo para calcular el avalúo y la retefuente.
      </p>
      <div id="ant-ret-estado" style="font-size:13px; color:#888; margin-bottom:10px;"></div>
      <div id="ant-ret-opciones"></div>
      <div id="ant-ret-resultado" style="display:none; margin-top:12px;">
        <div style="background:#f0fff6; border:1px solid #b2e4c8; border-radius:7px; padding:14px 16px;">
          <div style="font-size:13px; color:#888; margin-bottom:4px;">Línea seleccionada</div>
          <div id="ant-ret-linea-sel" style="font-size:14px; font-weight:700; color:#1a2340; margin-bottom:10px;"></div>
          <div style="display:flex; gap:20px; flex-wrap:wrap;">
            <div><div style="font-size:11px; color:#888;">Avalúo Comercial</div><div id="ant-ret-avaluo" style="font-size:18px; font-weight:900; color:#1a2340;"></div></div>
            <div><div style="font-size:11px; color:#888;">Retefuente (1%)</div><div id="ant-ret-retefuente" style="font-size:18px; font-weight:900; color:#1a6e3c;"></div></div>
          </div>
          <button class="ant-btn ant-btn-verde" onclick="antUsarRetefuente()" style="margin-top:12px;">
            ✓ Usar este valor en la liquidación
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- BLOQUE 5 — LIQUIDACION -->
  <div class="ant-card-liq" id="bloque-liq" style="display:none">
    <div class="ant-bloque-titulo" style="cursor:pointer;justify-content:space-between;" onclick="antToggleBloque('liq')">
      <span>5. Liquidacion</span><span id="chevron-liq">▲</span>
    </div>
    <div id="contenido-liq">
    <div id="liq-row-tramite1" class="ant-liq-item" style="display:none"><span class="ant-liq-nombre" id="liq-label-tramite1">Tramite 1</span><input class="ant-liq-input" id="liq-tramite1" type="text" value="0" inputmode="numeric"></div>
    <div id="liq-row-tramite2" class="ant-liq-item" style="display:none"><span class="ant-liq-nombre" id="liq-label-tramite2">Tramite 2</span><input class="ant-liq-input" id="liq-tramite2" type="text" value="0" inputmode="numeric"></div>
    <div id="liq-row-tramite3" class="ant-liq-item" style="display:none"><span class="ant-liq-nombre" id="liq-label-tramite3">Tramite 3</span><input class="ant-liq-input" id="liq-tramite3" type="text" value="0" inputmode="numeric"></div>
    <div id="liq-row-retefuente" class="ant-liq-item" style="display:none"><span class="ant-liq-nombre">Retefuente (1% avaluo)</span><input class="ant-liq-input" id="liq-retefuente" type="text" value="0" inputmode="numeric"></div>
    <div id="liq-row-depto" class="ant-liq-item" style="display:none"><span class="ant-liq-nombre">Impuesto Departamental</span><input class="ant-liq-input" id="liq-depto" type="text" value="0" inputmode="numeric"></div>
    <div id="liq-row-municipal" class="ant-liq-item" style="display:none"><span class="ant-liq-nombre">Impuesto Municipal</span><input class="ant-liq-input" id="liq-municipal" type="text" value="0" inputmode="numeric"></div>
    <div id="liq-row-pazsalvo" class="ant-liq-item" style="display:none"><span class="ant-liq-nombre">Paz y Salvo</span><input class="ant-liq-input" id="liq-pazsalvo" type="text" value="6.000" inputmode="numeric"></div>
    <div id="liq-row-envios" class="ant-liq-item" style="display:none"><span class="ant-liq-nombre">Envios y/o Domicilios</span><input class="ant-liq-input" id="liq-envios" type="text" value="18.000" inputmode="numeric"></div>
    <div id="liq-row-honorarios" class="ant-liq-item" style="display:grid"><span class="ant-liq-nombre">Honorarios</span><input class="ant-liq-input" id="liq-honorarios" type="text" value="0" inputmode="numeric"></div>
    <!-- Otros Cobros dinámicos -->
    <div id="liq-cobros-wrap">
      <div class="ant-liq-cobro" id="liq-cobro-1">
        <input class="ant-liq-cobro-nombre" id="liq-cobro-nombre-1" type="text" placeholder="Concepto (ej: Certificado)">
        <input class="ant-liq-input" id="liq-cobro-valor-1" type="text" value="0" inputmode="numeric">
        <button class="ant-liq-btn-add" onclick="antAgregarCobro()" id="liq-cobro-add-btn" title="Agregar otro cobro">+</button>
      </div>
    </div>

    <div class="ant-liq-total"><span>TOTAL</span><span id="liq-total">$ 0</span></div>
    <p class="ant-liq-nota">Todos los valores son editables. El total se actualiza automaticamente.</p>
    <button class="ant-btn ant-btn-wa" id="ant-btn-wa" onclick="antEnviarWA()">📲 Generar y Enviar por WhatsApp</button>
    <div class="ant-wa-preview" id="ant-wa-preview"><img id="ant-wa-img" src="" alt="Vista previa liquidacion"></div>
    <canvas id="ant-canvas-liq" style="display:none"></canvas>
    </div>
  </div>

</div>

<script>
(function() {
  var ANT_MUNICIPIOS = [
    "ANDES","APARTADO","BARBOSA","BELLO","CALDAS","CAREPA","CHIGORODO",
    "EL CARMEN DE VIBORAL","CAUCASIA","CIUDAD BOLIVAR","COPACABANA","DEPARTAMENTAL",
    "DONMATIAS","ENVIGADO","FRONTINO","GIRARDOTA","GUARNE","ITAGUI","LA CEJA",
    "LA ESTRELLA","LA UNION","MARINILLA","MEDELLIN","PUERTO BERRIO","RIONEGRO",
    "SABANETA","SANTA FE DE ANTIOQUIA","SANTA ROSA DE OSOS","SONSON","TURBO",
    "URRAO","YARUMAL"
  ];

  var MUNICIPIOS_MUNICIPALES = {
    "ENVIGADO":"envigado","SABANETA":"sabaneta","BELLO":"bello",
    "LA ESTRELLA":"la estrella","ITAGUI":"itagui"
  };

  // Municipios que muestran mensaje de oficina en impuesto municipal
  var MUNICIPIOS_OFICINA_SIEMPRE = ["CALDAS","BARBOSA"];
  var MUNICIPIOS_OFICINA_PUBLICO = ["RIONEGRO","SANTA ROSA DE OSOS","MEDELLIN","SANTA FE DE ANTIOQUIA"];

  function debeMostrarMensajeOficina() {
    var municipio = antMunicipioActual.toUpperCase();
    var serv      = (document.getElementById('ant-servicio').value || '').trim().toUpperCase();
    if (MUNICIPIOS_OFICINA_SIEMPRE.indexOf(municipio) >= 0) return true;
    if (MUNICIPIOS_OFICINA_PUBLICO.indexOf(municipio) >= 0 && serv === 'PUBLICO') return true;
    return false;
  }

  var CLASE_A_TIPO = {
    'AUTOMOVIL':'CARRO','CAMPERO':'CARRO','CAMIONETA':'CARRO','VOLQUETA':'CARRO',
    'CAMION':'CARRO','BUS':'CARRO','BUSETA':'CARRO',
    'MOTOCICLETA':'MOTO','MOTO':'MOTO',
    'MOTOCARRO':'MOTOCARRO','TRICIMOTO':'MOTOCARRO'
  };

  var ANT_API           = 'https://consulta-impuestos-production.up.railway.app';
  var antDatosOCR       = null;
  var antIdxActivo      = -1;
  var cacheTramites     = {};
  var antAvaluo         = 0;
  var ocrLeido          = false;
  var modoEntrada       = 'ocr';
  var tramiteOpciones   = [];
  var antMunicipioActual = ''; // municipio seleccionado, guardado en variable JS

  // ── TABLA DE AUTENTICACION POR MUNICIPIO ─────────────────────────────────
  var AUTENTICACION = {
    "MEDELLIN": {
      traspaso:  { propietario: ["mandato"] },
      otro:      { propietario: ["mandato"] }
    },
    "ENVIGADO": {
      traspaso:  { propietario: ["cualquier documento"] },
      otro:      { propietario: ["cualquier documento"] }
    },
    "BELLO": {
      traspaso:  { propietario: ["cualquier documento"] },
      otro:      { propietario: ["cualquier documento"] }
    },
    "ITAGUI": {
      traspaso:  { propietario: ["contrato de compraventa"] },
      otro:      { propietario: ["formulario"] }
    },
    "LA CEJA": {
      traspaso:  { propietario: [], nota_especial: "No requiere autenticación. Revisan firma del propietario en el RUNT." },
      otro:      { propietario: [], nota_especial: "No requiere autenticación. Revisan firma del propietario en el RUNT." }
    },
    "COPACABANA": {
      traspaso:  { propietario: ["mandato", "contrato de compraventa"], comprador: ["mandato"] },
      otro:      { propietario: ["mandato", "formulario"] }
    },
    "DEPARTAMENTAL": {
      traspaso:  { propietario: ["contrato de compraventa"] },
      otro:      { propietario: ["formulario"] }
    },
    "GIRARDOTA": {
      traspaso:  { propietario: ["contrato de compraventa"] },
      otro:      { propietario: ["formulario"] }
    },
    "LA ESTRELLA": {
      traspaso:  { propietario: ["contrato de compraventa"] },
      otro:      { propietario: ["formulario"] }
    },
    "MARINILLA": {
      traspaso:  { propietario: ["mandato"] },
      otro:      { propietario: ["mandato"] }
    },
    "RIONEGRO": {
      traspaso:  { propietario: ["contrato de compraventa"] },
      otro:      { propietario: ["formulario"] }
    },
    "SABANETA": {
      traspaso:  { propietario: ["contrato de compraventa"] },
      otro:      { propietario: ["formulario"] }
    },
    "SANTA FE DE ANTIOQUIA": {
      traspaso:  { propietario: ["mandato"], nota_especial: "Si la firma es diferente a la cédula, debe autenticar todos los documentos." },
      otro:      { propietario: ["mandato"], nota_especial: "Si la firma es diferente a la cédula, debe autenticar todos los documentos." }
    }
  };

  function generarNotaAutenticacion() {
    var municipio = antMunicipioActual.toUpperCase();
    var reglas    = AUTENTICACION[municipio];
    if (!reglas) return null;

    // Detectar si hay al menos un traspaso entre los tramites seleccionados
    var hayTraspaso = [1,2,3].some(function(n) {
      var v = (document.getElementById('ant-tramite-'+n).value || '').toUpperCase();
      return v.includes('TRASPASO');
    });

    var regla = hayTraspaso ? reglas.traspaso : reglas.otro;
    if (!regla) return null;

    var lineas = [];

    // Documentos del propietario
    if (regla.propietario && regla.propietario.length > 0) {
      lineas.push('El propietario debe autenticar: ' + regla.propietario.join(' + ').toUpperCase());
    }

    // Documentos del comprador (solo Copacabana traspaso)
    if (regla.comprador && regla.comprador.length > 0) {
      lineas.push('El comprador debe autenticar: ' + regla.comprador.join(' + ').toUpperCase());
    }

    // Nota especial si existe
    if (regla.nota_especial) {
      lineas.push(regla.nota_especial);
    }

    if (lineas.length === 0) return null;
    return 'NOTA (' + antMunicipioActual + '): ' + lineas.join(' | ');
  }

  // ── MODO ENTRADA ─────────────────────────────────────────────────────────

  function actualizarColorPlaca() {
    var serv  = (document.getElementById('ant-servicio').value || '').trim().toUpperCase();
    var placa = document.getElementById('ant-placa-letras').closest('div[style*="background"]');
    if (!placa) return;
    if (serv === 'PUBLICO') {
      placa.style.background = '#FFFFFF';
    } else {
      placa.style.background = '#FDD835';
    }
  }

  window.antModoEntrada = function(modo) {
    modoEntrada = modo;
    // Marcar botón activo
    ['btn-entrada-camara','btn-entrada-ocr','btn-entrada-manual'].forEach(function(id) {
      document.getElementById(id).classList.remove('activo');
    });
    document.getElementById('btn-entrada-'+modo).classList.add('activo');

    // Mostrar u ocultar zona OCR
    document.getElementById('ant-zona-ocr').style.display = modo !== 'manual' ? 'block' : 'none';

    if (modo === 'ocr') {
      // Mostrar zona de arrastre limpia aunque haya datos previos
      document.getElementById('ant-ocr-zone').style.display = 'block';
      document.getElementById('ant-preview-wrap').style.display = 'none';
      document.getElementById('ant-ocr-status').style.display = 'none';
      // Colapsar todos los bloques
      ocultarTodo();
    } else if (modo === 'camara') {
      // Abrir cámara directamente — zona OCR sigue visible para ver preview
      document.getElementById('ant-ocr-zone').style.display = 'block';
      document.getElementById('ant-preview-wrap').style.display = 'none';
      document.getElementById('ant-camara-file').click();
      // Colapsar todos los bloques
      ocultarTodo();
    } else if (modo === 'manual') {
      limpiarCampos();
      ocrLeido = true;
      document.getElementById('ant-bienvenida').style.display = 'none';
      document.getElementById('ant-municipio-wrap').style.display = 'block';
      document.getElementById('ant-mun-confirm').style.display = 'none';
      document.getElementById('ant-mun-label').style.display = 'block';
      document.getElementById('ant-mun-campo').style.display = 'block';
      actualizarVisibilidad();
    }
  };

  // ── LIQUIDACION ──────────────────────────────────────────────────────────

  var LIQ_IDS = ['liq-tramite1','liq-tramite2','liq-tramite3','liq-retefuente',
                 'liq-depto','liq-municipal','liq-pazsalvo','liq-envios',
                 'liq-honorarios'];
  var antCobrosCount = 1; // cuántos cobros extra hay actualmente

  function parseLiq(id) {
    return parseInt((document.getElementById(id).value||'0').replace(/\D/g,''),10)||0;
  }

  function calcularTotal() {
    var total = LIQ_IDS.reduce(function(s,id){ return s+parseLiq(id); },0);
    // Sumar cobros dinámicos
    for (var i = 1; i <= antCobrosCount; i++) {
      var el = document.getElementById('liq-cobro-valor-'+i);
      if (el) total += parseInt((el.value||'0').replace(/\D/g,''),10)||0;
    }
    document.getElementById('liq-total').textContent = '$ '+total.toLocaleString('es-CO');
  }

  window.antAgregarCobro = function() {
    if (antCobrosCount >= 3) return; // máximo 3
    antCobrosCount++;
    var wrap = document.getElementById('liq-cobros-wrap');

    // Ocultar botón + del cobro anterior y agregar botón - en su lugar
    var btnAdd = document.getElementById('liq-cobro-add-btn');
    if (btnAdd) {
      btnAdd.id = 'liq-cobro-del-btn-'+(antCobrosCount-1);
      btnAdd.className = 'ant-liq-btn-del';
      btnAdd.title = 'Eliminar';
      btnAdd.textContent = '×';
      btnAdd.onclick = (function(n){ return function(){ antEliminarCobro(n); }; })(antCobrosCount-1);
    }

    var div = document.createElement('div');
    div.className = 'ant-liq-cobro';
    div.id = 'liq-cobro-'+antCobrosCount;
    div.innerHTML =
      '<input class="ant-liq-cobro-nombre" id="liq-cobro-nombre-'+antCobrosCount+'" type="text" placeholder="Concepto (ej: Certificado)">' +
      '<input class="ant-liq-input" id="liq-cobro-valor-'+antCobrosCount+'" type="text" value="0" inputmode="numeric">' +
      (antCobrosCount < 3
        ? '<button class="ant-liq-btn-add" id="liq-cobro-add-btn" onclick="antAgregarCobro()" title="Agregar otro cobro">+</button>'
        : '<button class="ant-liq-btn-del" onclick="antEliminarCobro('+antCobrosCount+')" title="Eliminar">×</button>');
    wrap.appendChild(div);

    // Listener para recalcular
    document.getElementById('liq-cobro-valor-'+antCobrosCount).addEventListener('input', calcularTotal);
  };

  window.antEliminarCobro = function(n) {
    var div = document.getElementById('liq-cobro-'+n);
    if (div) div.remove();
    antCobrosCount--;

    // Restaurar botón + en el último cobro restante
    var wrap = document.getElementById('liq-cobros-wrap');
    var cobros = wrap.querySelectorAll('.ant-liq-cobro');
    if (cobros.length > 0) {
      var ultimo = cobros[cobros.length-1];
      var delBtn = ultimo.querySelector('.ant-liq-btn-del');
      if (delBtn && antCobrosCount < 3) {
        delBtn.id = 'liq-cobro-add-btn';
        delBtn.className = 'ant-liq-btn-add';
        delBtn.title = 'Agregar otro cobro';
        delBtn.textContent = '+';
        delBtn.onclick = antAgregarCobro;
      }
    }
    calcularTotal();
  };

  function setLiq(id, valor) {
    var el = document.getElementById(id);
    if (el) el.value = Math.round(valor).toLocaleString('es-CO');
    var rowId = 'liq-row-'+id.replace('liq-','');
    var row = document.getElementById(rowId);
    if (row) row.style.display = valor > 0 ? 'grid' : 'none';
    calcularTotal();
  }

  function mostrarFilasDefecto() {
    var municipio  = document.getElementById('ant-municipio').value;
    var tieneDepto = ANT_MUNICIPIOS.indexOf(municipio) >= 0;
    var exentoLiq  = exentoDepto();
    if (tieneDepto && !exentoLiq) {
      document.getElementById('liq-row-pazsalvo').style.display = 'grid';
    }
    document.getElementById('liq-row-envios').style.display = 'grid';
    // Honorarios siempre visible
    document.getElementById('liq-row-honorarios').style.display = 'grid';
    calcularTotal();
  }

  function limpiarLiq() {
    LIQ_IDS.forEach(function(id) { document.getElementById(id).value = '0'; });
    document.getElementById('liq-pazsalvo').value  = '6.000';
    document.getElementById('liq-envios').value    = '18.000';
    document.getElementById('liq-honorarios').value = '0';
    ['tramite1','tramite2','tramite3','retefuente','depto','municipal',
     'pazsalvo','envios'].forEach(function(k) {
      var r = document.getElementById('liq-row-'+k);
      if (r) r.style.display = 'none';
    });
    // Honorarios siempre visible
    document.getElementById('liq-row-honorarios').style.display = 'grid';
    // Resetear cobros dinámicos
    var wrap = document.getElementById('liq-cobros-wrap');
    if (wrap) {
      wrap.innerHTML =
        '<div class="ant-liq-cobro" id="liq-cobro-1">' +
        '<input class="ant-liq-cobro-nombre" id="liq-cobro-nombre-1" type="text" placeholder="Concepto (ej: Certificado)">' +
        '<input class="ant-liq-input" id="liq-cobro-valor-1" type="text" value="0" inputmode="numeric">' +
        '<button class="ant-liq-btn-add" id="liq-cobro-add-btn" onclick="antAgregarCobro()" title="Agregar otro cobro">+</button>' +
        '</div>';
      antCobrosCount = 1;
      document.getElementById('liq-cobro-valor-1').addEventListener('input', calcularTotal);
    }
    calcularTotal();
  }

  LIQ_IDS.forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener('input', calcularTotal);
  });
  // Listener cobro inicial
  var cobroInicial = document.getElementById('liq-cobro-valor-1');
  if (cobroInicial) cobroInicial.addEventListener('input', calcularTotal);

  // ── EXENCION ─────────────────────────────────────────────────────────────

  function exentoDepto() {
    var serv     = (document.getElementById('ant-servicio').value||'').trim().toUpperCase();
    var cilStr   = (document.getElementById('ant-cilindrada').value||'').trim();
    var cil      = cilStr ? parseInt(cilStr, 10) : 999; // si no hay dato, asumir no exento
    var esPublico = serv === 'PUBLICO';
    var esMoto125 = cilStr && cil > 0 && cil <= 125;
    return esPublico || esMoto125;
  }

  // ── VISIBILIDAD DE BLOQUES ────────────────────────────────────────────────

  var infoConfirmada = false;

  function ocultarTodo() {
    ['bloque-tramites','bloque-depto','bloque-municipal'].forEach(function(id) {
      var bl = document.getElementById(id);
      bl.classList.remove('visible');
      bl.style.display = 'none';
    });
    document.getElementById('bloque-info').classList.remove('visible');
    var blLiq = document.getElementById('bloque-liq');
    blLiq.style.cssText = 'display:none !important';
    var blRet = document.getElementById('bloque-retefuente');
    if (blRet) { blRet.style.display = 'none'; blRet.classList.remove('visible'); }
  }

  function mostrarYExpandirBloques() {
    var municipio  = antMunicipioActual.toUpperCase();
    var tieneMun   = !!MUNICIPIOS_MUNICIPALES[municipio];
    var tieneDepto = ANT_MUNICIPIOS.indexOf(municipio) >= 0;
    var exento     = exentoDepto();
    var tipodoc    = document.getElementById('ant-tipodoc').value;

    // Departamental
    if (tieneDepto && !exento) {
      var blD = document.getElementById('bloque-depto');
      blD.classList.add('visible'); blD.style.display = 'block';
      var cD = document.getElementById('contenido-depto');
      if (cD) cD.style.display = 'block';
      var chD = document.getElementById('chevron-depto');
      if (chD) chD.textContent = '▲';
      document.getElementById('ant-btn-impuesto').style.display = 'flex';
      document.getElementById('ant-no-depto').style.display = 'none';
    }

    // Municipal
    if (tieneMun || debeMostrarMensajeOficina()) {
      var blM = document.getElementById('bloque-municipal');
      blM.classList.add('visible'); blM.style.display = 'block';
      var cM = document.getElementById('contenido-municipal');
      if (cM) cM.style.display = 'block';
      var chM = document.getElementById('chevron-municipal');
      if (chM) chM.textContent = '▲';
      if (debeMostrarMensajeOficina()) {
        document.getElementById('ant-btn-municipal').style.display = 'none';
        document.getElementById('ant-result-municipal').innerHTML =
          '<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:7px;padding:14px 16px;color:#856404;font-size:14px;font-weight:700;text-align:center;margin-top:8px;">⚠️ DEBES PREGUNTAR DIRECTAMENTE EN LA OFICINA DE MOVILIDAD</div>';
      } else {
        document.getElementById('ant-btn-municipal').style.display = 'flex';
        document.getElementById('ant-result-municipal').innerHTML = '';
      }
    }

    // Tramites
    var blT = document.getElementById('bloque-tramites');
    blT.classList.add('visible'); blT.style.display = 'block';
    var cT = document.getElementById('contenido-tramites');
    if (cT) cT.style.display = 'block';
    var chT = document.getElementById('chevron-tramites');
    if (chT) chT.textContent = '▲';

    // Liquidacion
    var blL = document.getElementById('bloque-liq');
    blL.style.cssText = 'display:block !important';
    var cL = document.getElementById('contenido-liq');
    if (cL) cL.style.display = 'block';
    var chL = document.getElementById('chevron-liq');
    if (chL) chL.textContent = '▲';

    // Retefuente (solo si no es NIT)
    if (tipodoc !== 'NIT') {
      var blR = document.getElementById('bloque-retefuente');
      blR.classList.add('visible'); blR.style.display = 'block';
      var cR = document.getElementById('contenido-ret');
      if (cR) cR.style.display = 'block';
      var chR = document.getElementById('chevron-ret');
      if (chR) chR.textContent = '▲';
      antCargarRetefuente();
    }
  }

  function actualizarVisibilidad() {
    var municipio = document.getElementById('ant-municipio').value;

    if (!ocrLeido || !municipio) {
      ocultarTodo();
      return;
    }

    // Paso 2: mostrar solo informacion expandida
    if (!infoConfirmada) {
      ocultarTodo();
      document.getElementById('bloque-info').classList.add('visible');
      document.getElementById('ant-info-contenido').style.display = 'block';
      document.getElementById('ant-info-colapsado').style.display = 'none';
      document.getElementById('ant-info-chevron').textContent = '▲';
    }
    // Si ya confirmó, no hacer nada — antConfirmarInfo maneja el siguiente paso
  }

  // ── LIMPIEZA ─────────────────────────────────────────────────────────────

  function limpiarCampos() {
    ['ant-placa','ant-placa-edit','ant-modelo','ant-cedula','ant-apellidos',
     'ant-clase','ant-servicio','ant-cilindrada','ant-carroceria','ant-municipio-info'].forEach(function(id) {
      var el = document.getElementById(id); if(el) el.value = '';
    });
    document.getElementById('ant-placa-letras').textContent  = '---';
    document.getElementById('ant-placa-numeros').textContent = '---';
    actualizarColorPlaca();
    ['ant-marca','ant-linea','ant-capacidad'].forEach(function(id) {
      document.getElementById(id).value = '';
    });
    document.getElementById('ant-tipodoc').value         = 'CC';
    document.getElementById('ant-municipio-input').value = '';
    document.getElementById('ant-municipio').value       = '';
    document.getElementById('ant-result-depto').innerHTML    = '';
    document.getElementById('ant-result-municipal').innerHTML = '';
    document.getElementById('ant-preview-wrap').style.display = 'none';
    document.getElementById('ant-ocr-zone').style.display    = 'block';
    document.getElementById('ant-ocr-status').style.display  = 'none';
    document.getElementById('ant-wa-preview').style.display  = 'none';
    ['bloque-info','bloque-tramites','bloque-depto','bloque-municipal'].forEach(function(id) {
      document.getElementById(id).classList.remove('visible');
    });
    antDatosOCR = null; antAvaluo = 0; ocrLeido = false; infoConfirmada = false; antMunicipioActual = '';
    antRetAvaluo = 0; antRetRetefuente = 0;
    document.getElementById('ant-ret-estado').textContent   = '';
    document.getElementById('ant-ret-opciones').innerHTML   = '';
    document.getElementById('ant-ret-resultado').style.display = 'none';
    var blRet = document.getElementById('bloque-retefuente');
    if (blRet) { blRet.style.display = 'none'; blRet.classList.remove('visible'); }
    document.getElementById('ant-bienvenida').style.display     = 'block';
    document.getElementById('bloque-liq').style.display         = 'none';
    document.getElementById('ant-municipio-wrap').style.display = 'none';
    document.getElementById('ant-mun-confirm').style.display    = 'none';
    document.getElementById('ant-mun-label').style.display      = 'none';
    document.getElementById('ant-mun-campo').style.display      = 'none';
    limpiarTramites();
    limpiarLiq();
  }

  // ── TRAMITES CON AUTOCOMPLETE ─────────────────────────────────────────────

  function getTipo() {
    var clase = (document.getElementById('ant-clase').value||'').trim().toUpperCase();
    return CLASE_A_TIPO[clase] || '';
  }

  function limpiarTramites() {
    [1,2,3].forEach(function(n) {
      var inp = document.getElementById('ant-tramite-'+n);
      inp.value    = '';
      inp.disabled = true;
      document.getElementById('ant-tram-lista-'+n).style.display = 'none';
      document.getElementById('ant-precio-'+n).style.display     = 'none';
      if (n > 1) document.getElementById('ant-bloque-'+n).style.display = 'none';
    });
    tramiteOpciones = [];
  }

  function cargarTramites() {
    var municipio = document.getElementById('ant-municipio').value;
    var tipo      = getTipo();
    if (!municipio || !tipo) { limpiarTramites(); return; }
    var key = municipio+'|'+tipo;
    if (cacheTramites[key]) {
      tramiteOpciones = cacheTramites[key];
      habilitarTramite(1);
      return;
    }
    fetch(ANT_API+'/tramites/filtros?campo=tramite&municipio='+encodeURIComponent(municipio)+'&clase='+encodeURIComponent(tipo))
      .then(function(r){return r.json();})
      .then(function(data){
        cacheTramites[key] = data.valores||[];
        tramiteOpciones    = cacheTramites[key];
        habilitarTramite(1);
      })
      .catch(function(){});
  }

  function habilitarTramite(n) {
    var inp = document.getElementById('ant-tramite-'+n);
    if (inp) inp.disabled = false;
  }

  function filtrarTramites(n, texto) {
    var lista = document.getElementById('ant-tram-lista-'+n);
    var filtro = texto.trim().toUpperCase();
    var items  = filtro
      ? tramiteOpciones.filter(function(t){ return t.toUpperCase().includes(filtro); })
      : tramiteOpciones;
    lista.innerHTML = '';
    if (!items.length) { lista.style.display='none'; return; }
    items.forEach(function(t) {
      var div = document.createElement('div');
      div.textContent = t;
      div.addEventListener('mousedown', function(e){
        e.preventDefault();
        seleccionarTramite(n, t);
      });
      lista.appendChild(div);
    });
    lista.style.display = 'block';
  }

  function seleccionarTramite(n, valor) {
    document.getElementById('ant-tramite-'+n).value = valor;
    document.getElementById('ant-tram-lista-'+n).style.display = 'none';
    // Mostrar X en tramites 2 y 3
    var xBtn = document.getElementById('ant-x-'+n);
    if (xBtn) xBtn.style.display = 'inline-block';
    consultarTarifaN(n);
  }

  window.antEliminarTramite = function(n) {
    document.getElementById('ant-tramite-'+n).value = '';
    document.getElementById('ant-precio-'+n).style.display = 'none';
    document.getElementById('ant-bloque-'+n).style.display = 'none';
    var xBtn = document.getElementById('ant-x-'+n);
    if (xBtn) xBtn.style.display = 'none';
    setLiq('liq-tramite'+n, 0);
    document.getElementById('liq-row-tramite'+n).style.display = 'none';
    // Si elimina el 2, también oculta el 3
    if (n === 2) {
      document.getElementById('ant-tramite-3').value = '';
      document.getElementById('ant-precio-3').style.display = 'none';
      document.getElementById('ant-bloque-3').style.display = 'none';
      setLiq('liq-tramite3', 0);
      document.getElementById('liq-row-tramite3').style.display = 'none';
    }
    actualizarLiqTramites();
    calcularTotal();
  };

  function iniciarAutocomplete(n) {
    var inp   = document.getElementById('ant-tramite-'+n);
    var lista = document.getElementById('ant-tram-lista-'+n);
    var idxAct = -1;

    inp.addEventListener('focus', function(){ filtrarTramites(n, this.value); });
    inp.addEventListener('input', function(){
      filtrarTramites(n, this.value);
      // Limpiar precio si cambia el texto
      document.getElementById('ant-precio-'+n).style.display = 'none';
      setLiq('liq-tramite'+n, 0);
      actualizarLiqTramites();
    });
    inp.addEventListener('keydown', function(e) {
      var items = lista.querySelectorAll('div');
      if (!items.length) return;
      if (e.key==='ArrowDown') { idxAct=Math.min(idxAct+1,items.length-1); items.forEach(function(el,i){el.classList.toggle('activo',i===idxAct);}); e.preventDefault(); }
      else if (e.key==='ArrowUp') { idxAct=Math.max(idxAct-1,0); items.forEach(function(el,i){el.classList.toggle('activo',i===idxAct);}); e.preventDefault(); }
      else if (e.key==='Enter'&&idxAct>=0) { seleccionarTramite(n, items[idxAct].textContent); idxAct=-1; e.preventDefault(); }
      else if (e.key==='Escape') { lista.style.display='none'; }
    });
    inp.addEventListener('blur', function(){
      setTimeout(function(){ lista.style.display='none'; }, 150);
    });
  }

  function mostrarSiguiente(n) {
    if (n < 3) {
      var tramite = document.getElementById('ant-tramite-'+n).value.trim();
      if (tramite) {
        var sig = document.getElementById('ant-bloque-'+(n+1));
        if (sig) {
          sig.style.display = 'block';
          habilitarTramite(n+1);
        }
      }
    }
  }

  function hayTraspaso() {
    return [1,2,3].some(function(n) {
      return (document.getElementById('ant-tramite-'+n).value||'').toUpperCase().includes('TRASPASO');
    });
  }

  function actualizarLiqTramites() {
    [1,2,3].forEach(function(n) {
      var tramite = document.getElementById('ant-tramite-'+n).value;
      var row     = document.getElementById('liq-row-tramite'+n);
      var label   = document.getElementById('liq-label-tramite'+n);
      if (tramite && parseLiq('liq-tramite'+n) > 0) {
        label.textContent = tramite.length > 38 ? tramite.substring(0,36)+'...' : tramite;
        row.style.display = 'grid';
      } else {
        row.style.display = 'none';
      }
    });
    // Retefuente: visible si hay traspaso Y hay avaluo
    var refRow = document.getElementById('liq-row-retefuente');
    if (hayTraspaso() && antAvaluo > 0) {
      setLiq('liq-retefuente', Math.round(antAvaluo / 100));
      refRow.style.display = 'grid';
    } else {
      refRow.style.display = 'none';
    }
    calcularTotal();
  }

  function consultarTarifaN(n) {
    var municipio = document.getElementById('ant-municipio').value;
    var tipo      = getTipo();
    var tramite   = document.getElementById('ant-tramite-'+n).value.trim();
    var precioDiv = document.getElementById('ant-precio-'+n);
    precioDiv.style.display = 'none';
    setLiq('liq-tramite'+n, 0);
    mostrarSiguiente(n);
    actualizarLiqTramites();
    if (!tramite || !municipio || !tipo) return;
    fetch(ANT_API+'/tramites/precio?municipio='+encodeURIComponent(municipio)
      +'&clase='+encodeURIComponent(tipo)
      +'&tramite='+encodeURIComponent(tramite)
      +'&departamento=ANTIOQUIA')
      .then(function(r){return r.json();})
      .then(function(data){
        if (data.precio) {
          precioDiv.textContent = '$ '+data.precio.toLocaleString('es-CO');
          precioDiv.style.display = 'block';
          setLiq('liq-tramite'+n, data.precio);
          actualizarLiqTramites();
        }
      }).catch(function(){});
  }

  // ── INIT ─────────────────────────────────────────────────────────────────

  window.addEventListener('load', function() {

    ['ant-cedula','ant-modelo'].forEach(function(id) {
      document.getElementById(id).addEventListener('input', function() {
        this.value = this.value.replace(/[^0-9]/g,'');
      });
    });

    // Sincronizar input placa con visualización
    var placaEdit = document.getElementById('ant-placa-edit');
    var placaHidden = document.getElementById('ant-placa');
    if (placaEdit) {
      placaEdit.addEventListener('input', function() {
        var val = this.value.toUpperCase().replace(/[^A-Z0-9]/g,'');
        this.value = val;
        placaHidden.value = val;
        var letras  = val.substring(0, 3) || '---';
        var numeros = val.substring(3)    || '---';
        document.getElementById('ant-placa-letras').textContent  = letras;
        document.getElementById('ant-placa-numeros').textContent = numeros;
      });
    }

    ['ant-servicio','ant-cilindrada','ant-clase'].forEach(function(id) {
      document.getElementById(id).addEventListener('input', function() {
        actualizarVisibilidad(); cargarTramites();
        actualizarColorPlaca();
      });
    });

    document.getElementById('ant-tipodoc').addEventListener('change', function() {
      actualizarReglasDocumento();
    });

    function actualizarReglasDocumento() {
      var tipodoc = document.getElementById('ant-tipodoc').value;
      var rowRet  = document.getElementById('liq-row-retefuente');
      var blRet   = document.getElementById('bloque-retefuente');
      if (tipodoc === 'NIT') {
        // NIT no paga retefuente — ocultar fila en liquidacion y modulo
        if (rowRet) rowRet.style.display = 'none';
        if (blRet) { blRet.style.display = 'none'; blRet.classList.remove('visible'); }
      } else {
        // Todos los demas si pagan retefuente
        if (blRet && infoConfirmada) {
          blRet.style.display = 'block'; blRet.classList.add('visible');
        }
      }
    }

    // Iniciar autocomplete para los 3 tramites
    [1,2,3].forEach(function(n){ iniciarAutocomplete(n); });

    LIQ_IDS.forEach(function(id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener('input', calcularTotal);
    });

    // Municipio autocomplete
    var inputMun  = document.getElementById('ant-municipio-input');
    var hiddenMun = document.getElementById('ant-municipio');
    var listaMun  = document.getElementById('ant-mun-lista');

    function mostrarOpciones(filtro) {
      var items = filtro
        ? ANT_MUNICIPIOS.filter(function(m){ return m.includes(filtro.toUpperCase()); })
        : ANT_MUNICIPIOS;
      listaMun.innerHTML = '';
      antIdxActivo = -1;
      if (!items.length) { listaMun.style.display='none'; return; }
      items.forEach(function(m) {
        var div = document.createElement('div');
        div.textContent = m;
        div.addEventListener('mousedown', function(e){ e.preventDefault(); selMunicipio(m); });
        listaMun.appendChild(div);
      });
      listaMun.style.display = 'block';
    }

    function selMunicipio(valor) {
      inputMun.value     = valor;
      hiddenMun.value    = valor;
      antMunicipioActual = valor;
      var munInfo = document.getElementById('ant-municipio-info');
      if (munInfo) munInfo.value = valor;
      var placaMun = document.getElementById('ant-placa-municipio');
      if (placaMun) placaMun.textContent = valor;
      listaMun.style.display = 'none';
      document.getElementById('ant-ocr-status').style.display = 'none';
      actualizarVisibilidad();
      cargarTramites();
      var placa = document.getElementById('ant-placa').value.trim().toUpperCase();
      if (placa && valor) {
        fetch(ANT_API+'/ocr-guardar-municipio', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({placa: placa, municipio: valor})
        }).catch(function(){});
      }
      mostrarFilasDefecto();
    }

    inputMun.addEventListener('focus', function(){ mostrarOpciones(this.value); });
    inputMun.addEventListener('input', function(){ hiddenMun.value=''; actualizarVisibilidad(); mostrarOpciones(this.value); });
    inputMun.addEventListener('keydown', function(e) {
      var items = listaMun.querySelectorAll('div');
      if (!items.length) return;
      if (e.key==='ArrowDown') { antIdxActivo=Math.min(antIdxActivo+1,items.length-1); items.forEach(function(el,i){el.classList.toggle('activo',i===antIdxActivo);}); e.preventDefault(); }
      else if (e.key==='ArrowUp') { antIdxActivo=Math.max(antIdxActivo-1,0); items.forEach(function(el,i){el.classList.toggle('activo',i===antIdxActivo);}); e.preventDefault(); }
      else if (e.key==='Enter'&&antIdxActivo>=0) { selMunicipio(items[antIdxActivo].textContent); e.preventDefault(); }
      else if (e.key==='Escape') { listaMun.style.display='none'; }
    });
    inputMun.addEventListener('blur', function() {
      setTimeout(function(){ listaMun.style.display='none'; },150);
      var val = inputMun.value.toUpperCase();
      if (ANT_MUNICIPIOS.includes(val)) { inputMun.value=val; hiddenMun.value=val; actualizarVisibilidad(); }
      else { hiddenMun.value=''; actualizarVisibilidad(); }
    });
    document.addEventListener('click', function(e){ if(e.target!==inputMun) listaMun.style.display='none'; });

    // OCR
    var zona    = document.getElementById('ant-ocr-zone');
    var fileIn  = document.getElementById('ant-ocr-file');
    var preview = document.getElementById('ant-ocr-preview');
    var status  = document.getElementById('ant-ocr-status');

    zona.addEventListener('dragover', function(e){ e.preventDefault(); zona.classList.add('dragover'); });
    zona.addEventListener('dragleave', function(){ zona.classList.remove('dragover'); });
    zona.addEventListener('drop', function(e){ e.preventDefault(); zona.classList.remove('dragover'); if(e.dataTransfer.files[0]) cargarImagen(e.dataTransfer.files[0]); });
    fileIn.addEventListener('change', function(){ if(this.files[0]) cargarImagen(this.files[0]); });

    // Listener para la cámara
    var camaraIn = document.getElementById('ant-camara-file');
    camaraIn.addEventListener('change', function(){
      if(this.files[0]) {
        document.getElementById('ant-zona-ocr').style.display = 'block';
        document.getElementById('ant-ocr-zone').style.display = 'block';
        document.getElementById('ant-preview-wrap').style.display = 'none';
        cargarImagen(this.files[0]);
        this.value = '';
      }
    });

    var imagenBase64Actual = null;
    var imagenOriginal     = null;
    var rotacionActual     = 0;

    function cargarImagen(file) {
      if (!file.type.startsWith('image/')) { mostrarStatus('err','Solo imagenes JPG, PNG, WEBP'); return; }
      limpiarCampos();
      rotacionActual = 0;
      imagenOriginal = null;
      var reader = new FileReader();
      reader.onload = function(e) {
        var img = new Image();
        img.onload = function() {
          // Auto-rotar si está vertical
          if (img.height > img.width) rotacionActual = 90;
          imagenBase64Actual = e.target.result;
          mostrarPreviewConRotacion();
        };
        img.src = e.target.result;
      };
      reader.readAsDataURL(file);
    }

    function mostrarPreviewConRotacion() {
      var img = new Image();
      img.onload = function() {
        // Guardar imagen original sin rotar para que girar siempre parta de cero
        if (!imagenOriginal) imagenOriginal = imagenBase64Actual;
        var canvas = document.createElement('canvas'), ctx = canvas.getContext('2d');
        var rad = rotacionActual * Math.PI / 180;
        if (rotacionActual === 90 || rotacionActual === 270) {
          canvas.width = img.height; canvas.height = img.width;
        } else {
          canvas.width = img.width; canvas.height = img.height;
        }
        ctx.translate(canvas.width/2, canvas.height/2);
        ctx.rotate(rad);
        ctx.drawImage(img, -img.width/2, -img.height/2);
        var imagenRotada = canvas.toDataURL('image/jpeg', 0.9);
        // Mostrar preview
        var previewEl = document.getElementById('ant-ocr-preview');
        previewEl.src = imagenRotada;
        // Guardar imagen rotada para el OCR
        imagenBase64Actual = imagenRotada;
        // Mostrar panel de orientación
        document.getElementById('ant-ocr-zone').style.display = 'none';
        document.getElementById('ant-preview-wrap').style.display = 'block';
        document.getElementById('ant-ocr-status').style.display = 'none';
      };
      img.src = imagenBase64Actual;
    }

    var imagenOriginal = null; // guarda siempre la imagen sin ninguna rotación

    window.antGirarImagen = function() {
      rotacionActual = (rotacionActual + 90) % 360;
      var img = new Image();
      img.onload = function() {
        var canvas = document.createElement('canvas'), ctx = canvas.getContext('2d');
        var rad = rotacionActual * Math.PI / 180;
        if (rotacionActual === 90 || rotacionActual === 270) {
          canvas.width = img.height; canvas.height = img.width;
        } else {
          canvas.width = img.width; canvas.height = img.height;
        }
        ctx.translate(canvas.width/2, canvas.height/2);
        ctx.rotate(rad);
        ctx.drawImage(img, -img.width/2, -img.height/2);
        var imagenRotada = canvas.toDataURL('image/jpeg', 0.9);
        document.getElementById('ant-ocr-preview').src = imagenRotada;
        imagenBase64Actual = imagenRotada;
      };
      // Siempre desde la imagen original sin rotación acumulada
      img.src = imagenOriginal;
    };

    window.antContinuarOCR = function() {
      document.getElementById('ant-preview-wrap').style.display = 'none';
      procesarImagen(imagenBase64Actual);
    };

    window.antEliminarImagen = function() {
      imagenBase64Actual = null;
      rotacionActual = 0;
      document.getElementById('ant-preview-wrap').style.display = 'none';
      document.getElementById('ant-ocr-zone').style.display = 'block';
      document.getElementById('ant-ocr-status').style.display = 'none';
      document.getElementById('ant-ocr-preview').src = '';
      document.getElementById('ant-ocr-file').value = '';
      document.getElementById('ant-camara-file').value = '';
    };

    // Mostrar solo bloque-info al terminar de confirmar la foto
    window.antMostrarSoloInfo = function() {
      document.getElementById('bloque-info').classList.add('visible');
      ['bloque-tramites','bloque-depto','bloque-municipal'].forEach(function(id) {
        document.getElementById(id).classList.remove('visible');
      });
      document.getElementById('bloque-liq').style.display = 'none';
      // Expandir info
      document.getElementById('ant-info-contenido').style.display = 'block';
      document.getElementById('ant-info-colapsado').style.display = 'none';
    };

    function procesarImagen(imagenBase64) {
      mostrarStatus('procesando','Leyendo tarjeta de propiedad...');
      fetch(ANT_API+'/ocr-tarjeta', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({imagen: imagenBase64, municipio: document.getElementById('ant-municipio').value})
      })
      .then(function(r){return r.json();})
      .then(function(data) {
        if (data.error) { mostrarStatus('err','Error: '+data.error); return; }

        var tipodocMap = (function(t) {
          if (!t) return 'CC';
          t = t.toUpperCase().replace(/[.\s]/g,'');
          if (t==='CC') return 'CC';
          if (t==='NIT') return 'NIT';
          if (t==='CE') return 'CE';
          if (t==='TI') return 'TI';
          if (t==='RC') return 'RC';
          if (t==='PPT') return 'PPT';
          return 'CC';
        })(data.tipo_documento);

        if (data.placa) {
          document.getElementById('ant-placa').value = data.placa;
          var pe = document.getElementById('ant-placa-edit');
          if (pe) pe.value = data.placa;
          document.getElementById('ant-placa-letras').textContent  = data.placa.substring(0,3) || '---';
          document.getElementById('ant-placa-numeros').textContent = data.placa.substring(3)   || '---';
        }
        if (data.marca)      document.getElementById('ant-marca').value      = data.marca;
        if (data.linea)      document.getElementById('ant-linea').value      = data.linea;
        if (data.modelo)     document.getElementById('ant-modelo').value     = data.modelo;
        if (data.clase)      document.getElementById('ant-clase').value      = data.clase;
        if (data.servicio) {
          document.getElementById('ant-servicio').value = data.servicio;
          actualizarColorPlaca();
        }
        if (data.capacidad)  document.getElementById('ant-capacidad').value  = data.capacidad;
        if (data.cilindrada) document.getElementById('ant-cilindrada').value = data.cilindrada;
        if (data.carroceria) document.getElementById('ant-carroceria').value = data.carroceria;
        if (data.cedula)     document.getElementById('ant-cedula').value     = data.cedula;
        if (data.apellidos)  document.getElementById('ant-apellidos').value  = data.apellidos;
        document.getElementById('ant-tipodoc').value = tipodocMap;
        actualizarReglasDocumento();

        if (!data.desde_cache) antDatosOCR = data;
        ocrLeido = true;

        document.getElementById('ant-bienvenida').style.display     = 'none';
        document.getElementById('ant-municipio-wrap').style.display = 'block';

        if (data.municipio && data.desde_cache) {
          document.getElementById('ant-mun-confirm-nombre').textContent  = data.municipio;
          document.getElementById('ant-mun-confirm').style.display       = 'block';
          document.getElementById('ant-mun-label').style.display         = 'none';
          document.getElementById('ant-mun-campo').style.display         = 'none';
          document.getElementById('ant-municipio-input').value = data.municipio;
          document.getElementById('ant-municipio').value       = data.municipio;
        } else {
          document.getElementById('ant-mun-confirm').style.display = 'none';
          document.getElementById('ant-mun-label').style.display   = 'block';
          document.getElementById('ant-mun-campo').style.display   = 'block';
        }

        var detectados = [data.placa,data.marca,data.modelo,data.cedula].filter(Boolean).length;
        mostrarStatus(detectados>0?'ok':'err',
          detectados>0
            ? 'He leido tu tarjeta.<br>¿De qué municipio es este vehículo?'
            : 'No se pudieron detectar datos. Completa manualmente.');
      })
      .catch(function(err){ mostrarStatus('err','Error: '+err.message); });
    }

    function mostrarStatus(tipo, msg) {
      status.className = 'ant-ocr-status '+tipo;
      status.innerHTML = msg; status.style.display='block';
    }

    // Impuesto Departamental
    document.getElementById('ant-btn-impuesto').addEventListener('click', function() {
      var placa     = document.getElementById('ant-placa').value.trim().toUpperCase();
      var cedula    = document.getElementById('ant-cedula').value.trim();
      var modelo    = document.getElementById('ant-modelo').value.trim();
      var municipio = document.getElementById('ant-municipio').value;
      var apellidos = document.getElementById('ant-apellidos').value.trim().toUpperCase();
      var tipodoc   = document.getElementById('ant-tipodoc').value;
      var resultado = document.getElementById('ant-result-depto');
      var btn       = this;

      if (!placa||!cedula||!modelo||!municipio||!apellidos) {
        resultado.innerHTML='<div class="ant-alert error">Completa todos los campos requeridos.</div>'; return;
      }

      btn.disabled=true;
      resultado.innerHTML='<div class="ant-loading"><div class="ant-spinner-ring"></div><span>Consultando la Gobernacion de Antioquia...</span></div>';

      fetch(ANT_API+'/consultar?placa='+encodeURIComponent(placa)
        +'&municipio=antioquia&identificacion='+encodeURIComponent(cedula)
        +'&modelo='+encodeURIComponent(modelo)
        +'&municipio_transito='+encodeURIComponent(municipio)
        +'&apellidos_propietario='+encodeURIComponent(apellidos)
        +'&tipo_documento='+encodeURIComponent(tipodoc))
        .then(function(r){return r.json();})
        .then(function(data){
          btn.disabled=false;
          if (data.error){resultado.innerHTML='<div class="ant-alert error">'+data.error+'</div>';return;}

          if (data.avaluo) {
            antAvaluo = data.avaluo;
            // Llenar retefuente solo si hay traspaso
            if (hayTraspaso()) {
              setLiq('liq-retefuente', Math.round(data.avaluo / 100));
              document.getElementById('liq-row-retefuente').style.display = 'grid';
            }
            // Ocultar módulo retefuente porque ya tenemos el avalúo de Antioquia
            var blRet = document.getElementById('bloque-retefuente');
            if (blRet) { blRet.style.display = 'none'; blRet.classList.remove('visible'); }
          }
          if (data.total) {
            setLiq('liq-depto', data.total);
            document.getElementById('liq-row-depto').style.display = 'grid';
          }

          var info = data.placa_info||{};
          var infoHtml = info.marca
            ?'<div class="ant-info"><div class="ant-info-item"><label>Placa</label><span>'+data.placa+'</span></div>'
             +'<div class="ant-info-item"><label>Marca</label><span>'+info.marca+' '+(info.linea||'')+'</span></div>'
             +'<div class="ant-info-item"><label>Modelo</label><span>'+(info.modelo||'')+'</span></div>'
             +'<div class="ant-info-item"><label>Propietario</label><span>'+(info.propietario||'')+'</span></div></div>':'';

          if (data.sin_deuda) {
            resultado.innerHTML=infoHtml
              +'<div class="ant-alert success">'+data.placa+' esta a paz y salvo con la Gobernacion de Antioquia.</div>'
              +(data.avaluo?'<div class="ant-extra"><span>Retefuente (1%)</span><strong>$'+Math.round(data.avaluo/100).toLocaleString('es-CO')+'</strong></div>':'');
            return;
          }

          resultado.innerHTML=infoHtml
            +'<table class="ant-table"><thead><tr><th>Vigencia</th><th>Estado</th><th style="text-align:right">Valor</th></tr></thead><tbody>'
            +(data.registros||[]).map(function(r){
              return '<tr><td>'+r.vigencia+'</td><td>'+r.estado+'</td><td style="text-align:right">'
                +(r.total_vigencia?'$'+r.total_vigencia.toLocaleString('es-CO'):'Ver con asesor')+'</td></tr>';
            }).join('')+'</tbody></table>'
            +(data.total?'<div class="ant-total-bar"><span>Total vigencias</span><span>$'+data.total.toLocaleString('es-CO')+'</span></div>':'')
            +(data.avaluo?'<div class="ant-extra"><span>Retefuente (1%)</span><strong>$'+Math.round(data.avaluo/100).toLocaleString('es-CO')+'</strong></div>':'')
            +(data.excede_limite?'<div class="ant-warning">'+data.mensaje_limite+'</div>':'');

          // Mostrar bloque municipal después de resultado exitoso
          if (antMunicipioActual && MUNICIPIOS_MUNICIPALES[antMunicipioActual]) {
            var blMun = document.getElementById('bloque-municipal');
            blMun.classList.add('visible');
            blMun.style.display = 'block';
            document.getElementById('ant-result-municipal').innerHTML = '';
            var contMun = document.getElementById('contenido-municipal');
            if (contMun) contMun.style.display = 'block';
            var chevMun = document.getElementById('chevron-municipal');
            if (chevMun) chevMun.textContent = '▲';
          }
        })
        .catch(function(){btn.disabled=false;resultado.innerHTML='<div class="ant-alert error">Error de conexion.</div>';});
    });

    // Impuesto Municipal
    document.getElementById('ant-btn-municipal').addEventListener('click', function() {
      var placa     = document.getElementById('ant-placa').value.trim().toUpperCase();
      var municipio = document.getElementById('ant-municipio').value;
      var resultado = document.getElementById('ant-result-municipal');
      var btn       = this;

      if (!placa||!municipio) {
        resultado.innerHTML='<div class="ant-alert error">Ingresa la placa y selecciona el municipio.</div>'; return;
      }

      var municipioApi = MUNICIPIOS_MUNICIPALES[municipio];
      btn.disabled=true;
      resultado.innerHTML='<div class="ant-loading"><div class="ant-spinner-ring"></div><span>Consultando impuesto municipal...</span></div>';

      fetch(ANT_API+'/consultar?placa='+encodeURIComponent(placa)+'&municipio='+encodeURIComponent(municipioApi))
        .then(function(r){return r.json();})
        .then(function(data){
          btn.disabled=false;
          if (data.error){resultado.innerHTML='<div class="ant-alert error">'+data.error+'</div>';return;}

          if (data.total) {
            setLiq('liq-municipal', data.total);
            document.getElementById('liq-row-municipal').style.display='grid';
          }

          if (data.sin_deuda) {
            resultado.innerHTML='<div class="ant-alert success">'+data.placa+' esta al dia en '+municipio+'.</div>';
            return;
          }

          resultado.innerHTML='<div class="ant-info">'
            +'<div class="ant-info-item"><label>Placa</label><span>'+data.placa+'</span></div>'
            +'<div class="ant-info-item"><label>Municipio</label><span>'+municipio+'</span></div>'
            +(data.registros&&data.registros[0]&&data.registros[0].tipo_vehiculo?'<div class="ant-info-item"><label>Tipo</label><span>'+data.registros[0].tipo_vehiculo+'</span></div>':'')
            +'</div>'
            +'<table class="ant-table"><thead><tr><th>Anio</th><th>Descripcion</th><th style="text-align:right">Valor</th></tr></thead><tbody>'
            +(data.registros||[]).map(function(r){
              return '<tr><td>'+r.vigencia+'</td><td>'+(r.descripcion||'Sistematizacion')+'</td><td style="text-align:right">$'+r.total_vigencia.toLocaleString('es-CO')+'</td></tr>';
            }).join('')+'</tbody></table>'
            +'<div class="ant-total-bar"><span>Total adeudado</span><span>$'+data.total.toLocaleString('es-CO')+'</span></div>';
        })
        .catch(function(){btn.disabled=false;resultado.innerHTML='<div class="ant-alert error">Error de conexion.</div>';});
    });

  }); // end load

  // ── FUNCIONES GLOBALES ────────────────────────────────────────────────────

  // ── RETEFUENTE ───────────────────────────────────────────────────────────
  var antRetAvaluo     = 0;
  var antRetRetefuente = 0;

  function antCargarRetefuente() {
    var marca      = (document.getElementById('ant-marca').value || '').trim().toUpperCase();
    var linea      = (document.getElementById('ant-linea').value || '').trim().toUpperCase();
    var clase      = (document.getElementById('ant-clase').value || '').trim().toUpperCase();
    var carroceria = (document.getElementById('ant-carroceria').value || '').trim().toUpperCase();
    var modelo     = (document.getElementById('ant-modelo').value || '').trim();

    if (!marca || !clase || !modelo) return;

    var estado = document.getElementById('ant-ret-estado');
    var opcDiv = document.getElementById('ant-ret-opciones');
    estado.textContent = 'Buscando...';
    opcDiv.innerHTML   = '';
    document.getElementById('ant-ret-resultado').style.display = 'none';

    var cilindrada = (document.getElementById('ant-cilindrada').value || '').trim();
    fetch(ANT_API + '/retefuente/buscar?marca=' + encodeURIComponent(marca)
      + '&linea=' + encodeURIComponent(linea)
      + '&clase=' + encodeURIComponent(clase)
      + '&carroceria=' + encodeURIComponent(carroceria)
      + '&modelo=' + encodeURIComponent(modelo)
      + '&cilindraje=' + encodeURIComponent(cilindrada))
      .then(function(r){ return r.json(); })
      .then(function(data) {
        if (data.error) { estado.textContent = 'Error: ' + data.error; return; }
        if (!data.opciones || data.opciones.length === 0) {
          estado.textContent = 'No se encontraron resultados para esta marca y clase.';
          return;
        }
        estado.textContent = 'Se encontraron ' + data.opciones.length + ' opciones. Selecciona la que corresponde:';
        opcDiv.innerHTML = '';
        data.opciones.forEach(function(op) {
          var div = document.createElement('div');
          div.className = 'ant-ret-opcion';
          div.innerHTML =
            '<div class="ant-ret-opcion-nombre">' + op.linea + (op.cilindraje ? ' — ' + op.cilindraje + 'cc' : '') + '</div>' +
            '<div class="ant-ret-opcion-valor">Avalúo: $' + op.avaluo.toLocaleString('es-CO') + '</div>';
          div.addEventListener('click', function() {
            document.querySelectorAll('.ant-ret-opcion').forEach(function(el){ el.classList.remove('seleccionada'); });
            div.classList.add('seleccionada');
            antRetAvaluo     = op.avaluo;
            antRetRetefuente = op.retefuente;
            document.getElementById('ant-ret-linea-sel').textContent = op.linea;
            document.getElementById('ant-ret-avaluo').textContent    = '$' + op.avaluo.toLocaleString('es-CO');
            document.getElementById('ant-ret-retefuente').textContent = '$' + op.retefuente.toLocaleString('es-CO');
            document.getElementById('ant-ret-resultado').style.display = 'block';
          });
          opcDiv.appendChild(div);
        });
      })
      .catch(function(e){ estado.textContent = 'Error de conexión.'; });
  }

  window.antUsarRetefuente = function() {
    if (!antRetRetefuente) return;
    setLiq('liq-retefuente', antRetRetefuente);
    document.getElementById('liq-row-retefuente').style.display = 'grid';
    antAvaluo = antRetAvaluo;
    calcularTotal();
    // Cerrar bloque retefuente
    document.getElementById('contenido-ret').style.display = 'none';
    document.getElementById('chevron-ret').textContent = '▼';
  };

  window.antToggleBloque = function(id) {
    var contenido = document.getElementById('contenido-'+id);
    var chevron   = document.getElementById('chevron-'+id);
    if (!contenido) return;
    var visible = contenido.style.display !== 'none';
    contenido.style.display = visible ? 'none' : 'block';
    if (chevron) chevron.textContent = visible ? '▼' : '▲';
  };

  window.antToggleInfo = function() {
    var contenido = document.getElementById('ant-info-contenido');
    var chevron   = document.getElementById('ant-info-chevron');
    var visible   = contenido.style.display !== 'none';
    contenido.style.display = visible ? 'none' : 'block';
    // El resumen colapsado siempre oculto — solo el botón del título
    document.getElementById('ant-info-colapsado').style.display = 'none';
    chevron.textContent = visible ? '▼' : '▲';
  };

  window.antConfirmarInfo = function() {
    var placa     = document.getElementById('ant-placa').value.trim().toUpperCase();
    var municipio = document.getElementById('ant-municipio').value;

    infoConfirmada = true;

    // 1. Guardar en cache
    if (placa && municipio) {
      fetch(ANT_API+'/ocr-guardar-municipio', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({placa: placa, municipio: municipio})
      }).catch(function(){});
    }

    // 2. Colapsar informacion completamente
    document.getElementById('ant-info-contenido').style.display = 'none';
    document.getElementById('ant-info-colapsado').style.display = 'none';
    document.getElementById('ant-info-chevron').textContent = '▼';

    // 3. Ocultar mensaje OCR y selector de municipio
    document.getElementById('ant-ocr-status').style.display = 'none';
    document.getElementById('ant-municipio-wrap').style.display = 'none';

    // 4. Mostrar todos los bloques expandidos
    mostrarYExpandirBloques();
    cargarTramites();
    mostrarFilasDefecto();


  };

  window.antConfirmarMunicipio = function(confirmado) {
    if (confirmado) {
      antMunicipioActual = document.getElementById('ant-municipio').value;
      var munInfo = document.getElementById('ant-municipio-info');
      if (munInfo) munInfo.value = antMunicipioActual;
      var placaMun = document.getElementById('ant-placa-municipio');
      if (placaMun) placaMun.textContent = antMunicipioActual;
      document.getElementById('ant-mun-confirm').style.display = 'none';
      document.getElementById('ant-ocr-status').style.display = 'none';
      actualizarVisibilidad();
      cargarTramites();
      mostrarFilasDefecto();
    } else {
      document.getElementById('ant-mun-confirm').style.display = 'none';
      document.getElementById('ant-mun-label').style.display   = 'block';
      document.getElementById('ant-mun-campo').style.display   = 'block';
      document.getElementById('ant-municipio-input').value = '';
      document.getElementById('ant-municipio').value       = '';
      document.getElementById('ant-municipio-input').focus();
      ['bloque-info','bloque-tramites','bloque-depto','bloque-municipal'].forEach(function(id) {
        document.getElementById(id).classList.remove('visible');
      });
      document.getElementById('bloque-liq').style.display = 'none';
    }
  };

  window.antEnviarWA = function() {
    var canvas = document.getElementById('ant-canvas-liq');
    var ctx    = canvas.getContext('2d');
    var W      = 800;
    var filas  = [];

    [1,2,3].forEach(function(n) {
      var row = document.getElementById('liq-row-tramite'+n);
      if (row && row.style.display !== 'none') {
        var label = document.getElementById('liq-label-tramite'+n);
        var val   = parseLiq('liq-tramite'+n);
        if (val > 0) filas.push({label: label ? label.textContent : 'Tramite '+n, valor: val});
      }
    });

    var rowRef = document.getElementById('liq-row-retefuente');
    if (rowRef && rowRef.style.display !== 'none') {
      var vRef = parseLiq('liq-retefuente');
      if (vRef > 0) filas.push({label:'Retefuente (1% avaluo)', valor: vRef});
    }

    [{id:'liq-depto',label:'Impuesto Departamental'},{id:'liq-municipal',label:'Impuesto Municipal'},
     {id:'liq-pazsalvo',label:'Paz y Salvo'},{id:'liq-envios',label:'Envios y/o Domicilios'},
     {id:'liq-honorarios',label:'Honorarios'}
    ].forEach(function(c) {
      var v = parseLiq(c.id);
      if (v > 0) filas.push({label: c.label, valor: v});
    });
    // Cobros dinámicos — solo si tienen valor
    for (var ci = 1; ci <= antCobrosCount; ci++) {
      var cobroValEl    = document.getElementById('liq-cobro-valor-'+ci);
      var cobroNombreEl = document.getElementById('liq-cobro-nombre-'+ci);
      if (cobroValEl) {
        var cobroVal = parseInt((cobroValEl.value||'0').replace(/\D/g,''),10)||0;
        if (cobroVal > 0) {
          var cobroNombre = (cobroNombreEl && cobroNombreEl.value.trim()) ? cobroNombreEl.value.trim() : 'Otros Cobros';
          filas.push({label: cobroNombre, valor: cobroVal});
        }
      }
    }

    if (filas.length === 0) { alert('No hay items en la liquidacion.'); return; }

    var total    = filas.reduce(function(s,f){return s+f.valor;},0);
    var placa    = (document.getElementById('ant-placa').value||'').toUpperCase()||'SIN PLACA';
    var municipio = antMunicipioActual || '';
    var fecha    = new Date().toLocaleDateString('es-CO',{day:'2-digit',month:'long',year:'numeric'});

    // Obtener nombres de tramites seleccionados
    var tramitesNombres = [];
    [1,2,3].forEach(function(n) {
      var inp = document.getElementById('ant-tramite-'+n);
      if (inp && inp.value.trim()) tramitesNombres.push(inp.value.trim());
    });
    var tituloTramites = tramitesNombres.length > 0 ? tramitesNombres.join(' + ') : 'Liquidacion';
    var tituloCompleto = 'Tramy ' + tituloTramites + (municipio ? ' - ' + municipio : '');

    var PAD=40, ROW_H=44, HDR_H=100, TTL_H=64, FTR_H=70;
    var H = HDR_H+20+(filas.length*ROW_H)+16+TTL_H+FTR_H+PAD;
    canvas.width=W; canvas.height=H;

    ctx.fillStyle='#ffffff'; ctx.fillRect(0,0,W,H);

    // Header
    ctx.fillStyle='#0047AB'; ctx.fillRect(0,0,W,HDR_H);
    ctx.font='bold 36px Arial'; ctx.fillStyle='#ffffff'; ctx.textAlign='left';
    ctx.fillText('TRAMY',PAD,52);
    ctx.textAlign='right';
    ctx.font='bold 17px Arial'; ctx.fillStyle='#ffffff';
    ctx.fillText('Placa: '+placa, W-PAD, 44);
    if (municipio) {
      ctx.font='13px Arial'; ctx.fillStyle='rgba(255,255,255,0.85)';
      ctx.fillText(municipio, W-PAD, 64);
    }
    ctx.font='13px Arial'; ctx.fillStyle='rgba(255,255,255,0.7)';
    ctx.fillText(fecha, W-PAD, 84);
    ctx.textAlign='left';

    // Filas
    var y=HDR_H+28;
    filas.forEach(function(fila,i) {
      if (i%2===0) { ctx.fillStyle='#f4f8ff'; ctx.fillRect(PAD-10,y-26,W-(PAD-10)*2,ROW_H); }
      ctx.font='14px Arial'; ctx.fillStyle='#333333'; ctx.fillText(fila.label,PAD,y);
      ctx.font='bold 14px Arial'; ctx.fillStyle='#1a2340'; ctx.textAlign='right';
      ctx.fillText('$ '+fila.valor.toLocaleString('es-CO'),W-PAD,y);
      ctx.textAlign='left'; y+=ROW_H;
    });

    // Nota de autenticacion si aplica
    var notaAuth = generarNotaAutenticacion();
    if (notaAuth) {
      // Fondo de la nota
      var notaLineas = [];
      var maxAncho = W - (PAD*2) - 20;
      ctx.font = '11px Arial';
      // Dividir texto en líneas que quepan
      var palabras = notaAuth.split(' ');
      var lineaActual = '';
      palabras.forEach(function(palabra) {
        var prueba = lineaActual ? lineaActual + ' ' + palabra : palabra;
        if (ctx.measureText(prueba).width > maxAncho) {
          notaLineas.push(lineaActual);
          lineaActual = palabra;
        } else {
          lineaActual = prueba;
        }
      });
      if (lineaActual) notaLineas.push(lineaActual);

      var notaH = 16 + (notaLineas.length * 16) + 10;
      ctx.fillStyle = '#fff8e1';
      ctx.fillRect(PAD-10, y+4, W-(PAD-10)*2, notaH);
      ctx.strokeStyle = '#ffc107'; ctx.lineWidth = 1;
      ctx.strokeRect(PAD-10, y+4, W-(PAD-10)*2, notaH);
      ctx.font = 'bold 11px Arial'; ctx.fillStyle = '#856404'; ctx.textAlign = 'left';
      var ny = y + 18;
      notaLineas.forEach(function(linea, i) {
        if (i === 0) {
          ctx.font = 'bold 11px Arial';
        } else {
          ctx.font = '11px Arial';
        }
        ctx.fillText(linea, PAD, ny);
        ny += 16;
      });
      ctx.textAlign = 'left';
      y += notaH + 12;
    }

    // Total
    y+=8; ctx.strokeStyle='#0047AB'; ctx.lineWidth=2;
    ctx.beginPath(); ctx.moveTo(PAD,y); ctx.lineTo(W-PAD,y); ctx.stroke(); y+=14;
    ctx.fillStyle='#0047AB'; ctx.fillRect(PAD-10,y-26,W-(PAD-10)*2,TTL_H);
    ctx.font='bold 15px Arial'; ctx.fillStyle='rgba(255,255,255,0.85)'; ctx.fillText('TOTAL',PAD,y+4);
    ctx.font='bold 26px Arial'; ctx.fillStyle='#ffffff'; ctx.textAlign='right';
    ctx.fillText('$ '+total.toLocaleString('es-CO'),W-PAD,y+4);
    ctx.textAlign='left'; y+=TTL_H+12;

    // Pie de página
    ctx.fillStyle='#f0f4ff'; ctx.fillRect(0,H-FTR_H,W,FTR_H);
    ctx.font='bold 13px Arial'; ctx.fillStyle='#0047AB'; ctx.textAlign='center';
    ctx.fillText('Tramy - Liquidador de tramites de transito',W/2,H-FTR_H+22);
    ctx.font='11px Arial'; ctx.fillStyle='#888888';
    ctx.fillText('Documento informativo. Los valores pueden cambiar por concepto de intereses u otros',W/2,H-FTR_H+42);
    ctx.fillText('conceptos relacionados con las entidades de movilidad.',W/2,H-FTR_H+58);

    // Marca de agua
    ctx.save(); ctx.translate(W/2,H/2); ctx.rotate(-Math.PI/6);
    ctx.font='bold 80px Arial'; ctx.fillStyle='rgba(0,71,171,0.04)'; ctx.textAlign='center';
    ctx.fillText('TRAMY',0,0); ctx.restore();

    var dataUrl = canvas.toDataURL('image/png');
    document.getElementById('ant-wa-img').src = dataUrl;
    document.getElementById('ant-wa-preview').style.display = 'block';

    var textoWA = tituloCompleto + ' - Placa: ' + placa + ' - Total: $' + total.toLocaleString('es-CO') + ' - Generado por Tramy';

    if (navigator.share && navigator.canShare) {
      canvas.toBlob(function(blob) {
        var file = new File([blob],'liquidacion_'+placa+'.png',{type:'image/png'});
        if (navigator.canShare({files:[file]})) {
          navigator.share({title: tituloCompleto, text: textoWA, files:[file]})
            .catch(function(){ window.open('https://wa.me/?text='+encodeURIComponent(textoWA),'_blank'); });
        } else { window.open('https://wa.me/?text='+encodeURIComponent(textoWA),'_blank'); }
      });
    } else {
      var link = document.createElement('a');
      link.download = 'liquidacion_'+placa+'.png';
      link.href = dataUrl; link.click();
      setTimeout(function(){ window.open('https://web.whatsapp.com/','_blank'); },500);
    }
  };

})();
</script>
