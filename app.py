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
    font-size: 15px; font-weight: 900; color: #fff;
    background: #1a2340; border-radius: 7px;
    padding: 11px 16px; margin-bottom: 16px;
    display: flex; align-items: center; justify-content: space-between;
    text-transform: uppercase; letter-spacing: 0.5px;
  }
  .ant-bloque-titulo-texto { flex: 1; text-align: center; }
  .ant-bloque-titulo-chevron { font-size: 14px; min-width: 20px; text-align: right; }
  .ant-bloque-titulo-left { min-width: 20px; }

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
  .ant-total-bar { display: flex; justify-content: space-between; align-items: center; background: #2a7fd8; color: #fff; border-radius: 7px; padding: 12px 16px; margin-top: 12px; }
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
  .ant-liq-total { background: #2a7fd8; color: #fff; border-radius: 8px; padding: 14px 18px; margin-top: 16px; display: flex; justify-content: space-between; align-items: center; }
  .ant-liq-total span:first-child { font-size: 14px; opacity: .85; }
  .ant-liq-total span:last-child  { font-size: 24px; font-weight: 900; }
  .ant-liq-nota { font-size: 11px; color: #888; margin-top: 8px; text-align: center; }
  .ant-liq-cobro { display: grid; grid-template-columns: 1fr 140px 32px; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #eef0f5; }
  .ant-liq-cobro-nombre { font-size: 13px; color: #444; border: 1px solid #ccd3de; border-radius: 6px; padding: 6px 10px; outline: none; width: 100%; box-sizing: border-box; background: #fff; }
  .ant-liq-cobro-nombre:focus { border-color: #3b7de8; }
  .ant-liq-btn-add { background: #1a5fa8; color: #fff; border: none; border-radius: 6px; width: 32px; height: 32px; font-size: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background .2s; flex-shrink: 0; }
  .ant-liq-btn-add:hover { background: #2a7fd8; }
  .ant-liq-btn-del { background: #c0392b; color: #fff; border: none; border-radius: 6px; width: 32px; height: 32px; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background .2s; flex-shrink: 0; }
  .ant-liq-btn-del:hover { background: #e74c3c; }
  .ant-wa-preview { margin-top: 12px; border-radius: 8px; overflow: hidden; border: 1px solid #dde3ec; display: none; }
  .ant-wa-preview img { width: 100%; display: block; }

  /* Tooltip ayuda */
  .ant-ayuda-btn { background: none; border: 1.5px solid #fff; color: #fff; border-radius: 50%; width: 18px; height: 18px; font-size: 11px; font-weight: 900; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; margin-left: 6px; flex-shrink: 0; opacity: 0.85; transition: opacity .2s; }
  .ant-ayuda-btn:hover { opacity: 1; }
  .ant-ayuda-panel { display: none; background: #f0f6ff; border: 1px solid #b3d0f5; border-radius: 8px; padding: 12px 14px; margin-top: 10px; font-size: 13px; color: #1a2340; line-height: 1.6; }
  .ant-ayuda-panel ol { margin: 6px 0 0 16px; padding: 0; }
  .ant-ayuda-panel li { margin-bottom: 4px; }

  .ant-progreso-wrap { padding: 14px; background: #f8fafc; border-radius: 8px; border: 1px solid #dde3ec; }
  .ant-progreso-msg { font-size: 14px; color: #1a2340; font-weight: 600; margin-bottom: 10px; line-height: 1.4; }
  .ant-progreso-barra-bg { background: #e0e7ef; border-radius: 10px; height: 10px; overflow: hidden; }
  .ant-progreso-barra { background: linear-gradient(90deg, #1a5fa8, #25a06e); height: 10px; border-radius: 10px; width: 5%; transition: width 0.8s ease; }

  /* Botón nueva liquidación */
  .ant-fab-nuevo {
    position: fixed; bottom: 20px; right: 20px; z-index: 9998;
    width: 56px; height: 56px; border-radius: 50%;
    background: #0047AB; color: #fff; border: none;
    font-size: 32px; font-weight: 300; cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,71,171,0.4);
    display: flex; align-items: center; justify-content: center;
    transition: background .2s, transform .2s;
    line-height: 1;
  }
  .ant-fab-nuevo:hover { background: #1a5fa8; transform: scale(1.08); }

  /* Botón reporte */
  .ant-reporte-btn {
    position: fixed; bottom: 20px; left: 20px; z-index: 9998;
    background: #1a2340; color: #fff; border: none; border-radius: 50px;
    padding: 10px 16px; font-size: 12px; font-weight: 700; cursor: pointer;
    box-shadow: 0 3px 10px rgba(0,0,0,0.2); transition: background .2s;
    display: flex; align-items: center; gap: 6px; font-family: Arial, sans-serif;
  }
  .ant-reporte-btn:hover { background: #2a3a60; }
  .ant-reporte-panel {
    position: fixed; bottom: 70px; left: 20px; z-index: 9997;
    background: #fff; border: 1px solid #dde3ec; border-radius: 12px;
    padding: 18px; width: 280px; box-shadow: 0 6px 24px rgba(0,0,0,0.15);
    display: none; font-family: Arial, sans-serif;
  }
  .ant-reporte-titulo { font-size: 14px; font-weight: 700; color: #1a2340; margin-bottom: 12px; }
  .ant-reporte-opciones { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
  .ant-reporte-opcion {
    padding: 6px 12px; border: 1px solid #dde3ec; border-radius: 20px;
    font-size: 12px; cursor: pointer; transition: all .2s; color: #444;
    background: #f8fafc;
  }
  .ant-reporte-opcion:hover, .ant-reporte-opcion.sel { background: #1a2340; color: #fff; border-color: #1a2340; }
  .ant-reporte-textarea {
    width: 100%; border: 1px solid #ccd3de; border-radius: 7px;
    padding: 8px 10px; font-size: 12px; resize: none; outline: none;
    box-sizing: border-box; margin-bottom: 10px; font-family: Arial, sans-serif;
  }
  .ant-reporte-textarea:focus { border-color: #3b7de8; }
  .ant-reporte-enviar {
    width: 100%; padding: 9px; background: #1a6e3c; color: #fff;
    border: none; border-radius: 7px; font-size: 13px; font-weight: 700;
    cursor: pointer; transition: background .2s;
  }
  .ant-reporte-enviar:hover { background: #2a9e5c; }
  .ant-reporte-ok { font-size: 13px; color: #1a6e3c; font-weight: 700; text-align: center; display: none; margin-top: 8px; }

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

  <!-- SALUDO -->
  <div class="ant-top" id="ant-saludo">
    <div class="ant-bienvenida" id="ant-bienvenida">
      <div style="text-align:center; margin-bottom:6px;">
        <span style="font-size:18px; font-weight:900; color:#0047AB;">Hola, </span><span style="font-size:32px; font-weight:900; color:#0047AB;">soy Tramy</span>
      </div>
      <div style="font-size:16px; color:#1a2340; text-align:center; line-height:1.6; font-family:Arial, sans-serif; font-weight:700;">Hagamos esto juntos.<br>Yo liquido, tú haces la magia.</div>
    </div>
  </div>

  <!-- OCR + Municipio -->
  <div class="ant-top" id="bloque-info-top" style="display:block;">
    <div id="contenido-info-top">

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
    </div><!-- fin contenido-info-top -->
  </div><!-- fin bloque-info-top -->

  <!-- Placa mini — visible después de confirmar info -->
  <div id="ant-placa-mini" style="display:none; text-align:center; margin-bottom:8px;">
    <div style="display:inline-block; background:#FDD835; border:2px solid #111; border-radius:5px; padding:4px 12px; box-shadow:1px 1px 5px rgba(0,0,0,0.18); cursor:pointer;" onclick="antToggleInfo()">
      <div style="display:flex; align-items:center; justify-content:center; gap:3px;">
        <span id="ant-placa-col-letras" style="font-size:15px; font-weight:900; letter-spacing:3px; color:#111; font-family:'Arial Black',Arial,sans-serif;"></span>
        <span id="ant-placa-col-numeros" style="font-size:15px; font-weight:900; letter-spacing:3px; color:#111; font-family:'Arial Black',Arial,sans-serif;"></span>
      </div>
      <div id="ant-placa-col-municipio" style="font-size:8px; font-weight:900; color:#111; text-align:center; letter-spacing:1px; text-transform:uppercase;"></div>
    </div>
    <span style="display:block; font-size:11px; color:#1a5fa8; font-weight:700; margin-top:3px; cursor:pointer;" onclick="antToggleInfo()">✏️ Editar información</span>
  </div>

  <!-- BLOQUE 1 — INFORMACION -->
  <div class="ant-card" id="bloque-info">
    <!-- Cabecera con colapso -->
    <div class="ant-bloque-titulo" style="cursor:pointer;" onclick="antToggleInfo()">
      <span class="ant-bloque-titulo-left" style="opacity:0;">▼</span>
      <span class="ant-bloque-titulo-texto" id="titulo-info">PASO 1 — INFORMACION</span>
      <span class="ant-bloque-titulo-chevron" id="ant-info-chevron">▲</span>
    </div>

    <!-- Contenido completo -->
    <div id="ant-info-colapsado" style="display:none;"></div>
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

            <!-- Input editable visible -->
            <input id="ant-placa-editar" type="text" maxlength="7" placeholder="Editar placa"
              class="ant-input upper"
              style="margin-top:6px; text-align:center; font-size:14px; font-weight:700; letter-spacing:3px; width:100%; box-sizing:border-box;">

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
    <div class="ant-bloque-titulo" style="cursor:pointer;" onclick="antToggleBloque('depto')">
      <span class="ant-bloque-titulo-left" style="opacity:0;">▼</span>
      <span class="ant-bloque-titulo-texto" id="titulo-depto">PASO 2 — IMPUESTO DEPARTAMENTAL</span>
      <span style="display:flex;align-items:center;gap:6px;">
        <button class="ant-ayuda-btn" onclick="event.stopPropagation();antToggleAyuda('ayuda-depto')" title="Ayuda">?</button>
        <span class="ant-bloque-titulo-chevron" id="chevron-depto">▲</span>
      </span>
    </div>
    <div id="ayuda-depto" class="ant-ayuda-panel">
      Este módulo funciona igual que si consultaras directamente en la página de impuestos departamentales de Antioquia. Si te sale error puede ser por los mismos motivos que si lo hicieras tú mismo en la página oficial:
      <ol>
        <li>A veces la consulta entrega error y basta con intentarlo de nuevo. Esto también ocurre a veces al intentar consultar por la página de impuesto vehicular Antioquia.</li>
        <li>El dato "apellidos del propietario" no está bien. Sucede porque el sistema no diferencia entre nombres y apellidos cuando el propietario tiene un solo apellido. En este caso debes borrar los nombres y dejar solo el apellido.</li>
        <li>El propietario en la tarjeta que leíste ya no es el propietario actual.</li>
        <li>El propietario no está actualizado en la Gobernación de Antioquia, generalmente porque el último traspaso fue realizado hace muy poco tiempo (menos de 2 meses).</li>
        <li>La Gobernación de Antioquia tiene algún dato desactualizado.</li>
      </ol>
    </div>
    <div id="contenido-depto">
    <div class="ant-no-depto" id="ant-no-depto" style="display:none">⚠️ Este vehiculo NO PAGA IMPUESTOS DEPARTAMENTALES</div>
    <button class="ant-btn ant-btn-verde" id="ant-btn-impuesto" style="display:none">🏛️ Consultar</button>
    <div class="ant-result" id="ant-result-depto"></div>
    </div>
  </div>

  <!-- BLOQUE 3 — IMPUESTO MUNICIPAL -->
  <div class="ant-card" id="bloque-municipal">
    <div class="ant-bloque-titulo" style="cursor:pointer;" onclick="antToggleBloque('municipal')">
      <span class="ant-bloque-titulo-left" style="opacity:0;">▼</span>
      <span class="ant-bloque-titulo-texto" id="titulo-municipal">PASO 3 — IMPUESTO MUNICIPAL</span>
      <span style="display:flex;align-items:center;gap:6px;">
        <button class="ant-ayuda-btn" onclick="event.stopPropagation();antToggleAyuda('ayuda-municipal')" title="Ayuda">?</button>
        <span class="ant-bloque-titulo-chevron" id="chevron-municipal">▲</span>
      </span>
    </div>
    <div id="ayuda-municipal" class="ant-ayuda-panel">
      Si el resultado que arroja este módulo es <strong>"paz y salvo"</strong>, inténtalo de nuevo. Es posible que el vehículo no esté a paz y salvo — debes confirmar con un segundo intento. Si vuelve a mostrar "paz y salvo", continúa con los siguientes pasos.
    </div>
    <div id="contenido-municipal">
    <button class="ant-btn ant-btn-azul" id="ant-btn-municipal">🏘️ Consultar</button>
    <div class="ant-result" id="ant-result-municipal"></div>
    </div>
  </div>

  <!-- BLOQUE 4 — TRAMITES -->
  <div class="ant-card" id="bloque-tramites">
    <div class="ant-bloque-titulo" style="cursor:pointer;" onclick="antToggleBloque('tramites')">
      <span class="ant-bloque-titulo-left" style="opacity:0;">▼</span>
      <span class="ant-bloque-titulo-texto" id="titulo-tramites">PASO 4 — TRAMITES</span>
      <span class="ant-bloque-titulo-chevron" id="chevron-tramites">▲</span>
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
    <div class="ant-bloque-titulo" style="cursor:pointer;" onclick="antToggleBloque('ret')">
      <span class="ant-bloque-titulo-left" style="opacity:0;">▼</span>
      <span class="ant-bloque-titulo-texto" id="titulo-ret">PASO 5 — RETEFUENTE</span>
      <span class="ant-bloque-titulo-chevron" id="chevron-ret">▲</span>
    </div>
    <div id="contenido-ret">
      <div id="ant-ret-datos-veh" style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:12px;">
        <span id="ret-dato-clase" style="background:#e8f0f8; border-radius:20px; padding:4px 12px; font-size:13px; font-weight:700; color:#1a2340;"></span>
        <span id="ret-dato-marca" style="background:#e8f0f8; border-radius:20px; padding:4px 12px; font-size:13px; font-weight:700; color:#1a2340;"></span>
        <span id="ret-dato-linea" style="background:#e8f0f8; border-radius:20px; padding:4px 12px; font-size:13px; font-weight:700; color:#1a2340;"></span>
        <span id="ret-dato-modelo" style="background:#e8f0f8; border-radius:20px; padding:4px 12px; font-size:13px; font-weight:700; color:#1a2340;"></span>
        <span id="ret-dato-cil" style="background:#e8f0f8; border-radius:20px; padding:4px 12px; font-size:13px; font-weight:700; color:#1a2340;"></span>
        <span id="ret-dato-cap" style="background:#e8f0f8; border-radius:20px; padding:4px 12px; font-size:13px; font-weight:700; color:#1a2340;"></span>
      </div>
      <p style="font-size:13px; color:#555; margin:0 0 12px 0;">Elige la opción más acertada con tu vehículo.</p>
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
      <p style="font-size:11px; color:#999; margin-top:14px; text-align:center; line-height:1.5;">
        Los datos aquí enlistados provienen del <a href="https://web.mintransporte.gov.co/sibga/" target="_blank" style="color:#1a5fa8;">SIBGA</a>, de las <a href="https://mintransporte.gov.co/publicaciones/12234/base-gravable-2026/" target="_blank" style="color:#1a5fa8;">tablas de avalúos</a> publicadas por el Ministerio de Transporte.
      </p>
    </div>
  </div>

  <!-- BLOQUE 5 — LIQUIDACION -->
  <div class="ant-card-liq" id="bloque-liq" style="display:none">
    <div class="ant-bloque-titulo" style="cursor:pointer;" onclick="antToggleBloque('liq')">
      <span class="ant-bloque-titulo-left" style="opacity:0;">▼</span>
      <span class="ant-bloque-titulo-texto" id="titulo-liq">PASO 6 — LIQUIDACION</span>
      <span class="ant-bloque-titulo-chevron" id="chevron-liq">▲</span>
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

<datalist id="ant-cobro-opciones"><option value="Retefuente">Retefuente</option><option value="Impuesto Departamental">Impuesto Departamental</option><option value="Impuesto Municipal">Impuesto Municipal</option><option value="Envio">Envio</option><option value="Domicilio">Domicilio</option><option value="4 X 1.000">4 X 1.000</option><option value="Camara Comercio">Camara Comercio</option><option value="Copias">Copias</option><option value="Liquidacion de Impuesto">Liquidacion de Impuesto</option><option value="Cupl">Cupl</option><option value="Parqueadero">Parqueadero</option></datalist>

<!-- Botón flotante nueva liquidación -->
<button class="ant-fab-nuevo" onclick="antNuevaLiquidacion()" title="Nueva liquidación">+</button>



<!-- Botón flotante de reporte -->
<button class="ant-reporte-btn" onclick="antToggleReporte()" style="left:20px;right:auto;">⚠️ Reportar daños</button>
<div class="ant-reporte-panel" id="ant-reporte-panel" style="left:20px;right:auto;">
  <div class="ant-reporte-titulo">¿Qué está pasando?</div>
  <div class="ant-reporte-opciones">
    <div class="ant-reporte-opcion" onclick="antSelOpcion(this,'Dato incorrecto')">Dato incorrecto</div>
    <div class="ant-reporte-opcion" onclick="antSelOpcion(this,'Precio errado')">Precio errado</div>
    <div class="ant-reporte-opcion" onclick="antSelOpcion(this,'No cargó')">No cargó</div>
    <div class="ant-reporte-opcion" onclick="antSelOpcion(this,'Error en consulta')">Error en consulta</div>
    <div class="ant-reporte-opcion" onclick="antSelOpcion(this,'Otro')">Otro</div>
  </div>
  <textarea class="ant-reporte-textarea" id="ant-reporte-texto" rows="3" placeholder="Cuéntanos más (opcional)..."></textarea>
  <button class="ant-reporte-enviar" onclick="antEnviarReporte()">Enviar reporte</button>
  <div class="ant-reporte-ok" id="ant-reporte-ok">✓ Gracias, lo revisaremos pronto.</div>
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
      '<input class="ant-liq-cobro-nombre" id="liq-cobro-nombre-'+antCobrosCount+'" type="text" placeholder="Concepto" list="ant-cobro-opciones">' +
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
        '<input class="ant-liq-cobro-nombre" id="liq-cobro-nombre-1" type="text" placeholder="Concepto" list="ant-cobro-opciones">' +
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
    var cil      = cilStr ? parseInt(cilStr.replace(/\./g, '').replace(/,/g, ''), 10) : 999; // limpiar puntos y comas antes de parsear
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

    // Departamental — visible pero colapsado
    if (tieneDepto && !exento) {
      var blD = document.getElementById('bloque-depto');
      blD.classList.add('visible'); blD.style.display = 'block';
      var cD = document.getElementById('contenido-depto');
      if (cD) cD.style.display = 'none';
      var chD = document.getElementById('chevron-depto');
      if (chD) chD.textContent = '▼';
      document.getElementById('ant-btn-impuesto').style.display = 'flex';
      document.getElementById('ant-no-depto').style.display = 'none';
    }

    // Municipal — visible pero colapsado
    if (tieneMun || debeMostrarMensajeOficina()) {
      var blM = document.getElementById('bloque-municipal');
      blM.classList.add('visible'); blM.style.display = 'block';
      var cM = document.getElementById('contenido-municipal');
      if (cM) cM.style.display = 'none';
      var chM = document.getElementById('chevron-municipal');
      if (chM) chM.textContent = '▼';
      if (debeMostrarMensajeOficina()) {
        document.getElementById('ant-btn-municipal').style.display = 'none';
        document.getElementById('ant-result-municipal').innerHTML =
          '<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:7px;padding:14px 16px;color:#856404;font-size:14px;font-weight:700;text-align:center;margin-top:8px;">⚠️ DEBES PREGUNTAR DIRECTAMENTE EN LA OFICINA DE MOVILIDAD</div>';
      } else {
        document.getElementById('ant-btn-municipal').style.display = 'flex';
        document.getElementById('ant-result-municipal').innerHTML = '';
      }
    }

    // Tramites — visible pero colapsado
    var blT = document.getElementById('bloque-tramites');
    blT.classList.add('visible'); blT.style.display = 'block';
    var cT = document.getElementById('contenido-tramites');
    if (cT) cT.style.display = 'none';
    var chT = document.getElementById('chevron-tramites');
    if (chT) chT.textContent = '▼';

    // Liquidacion — visible pero colapsada
    var blL = document.getElementById('bloque-liq');
    blL.style.cssText = 'display:block !important';
    var cL = document.getElementById('contenido-liq');
    if (cL) cL.style.display = 'none';
    var chL = document.getElementById('chevron-liq');
    if (chL) chL.textContent = '▼';

    // WhatsApp — visible pero colapsado
    var blWA = document.getElementById('bloque-wa');
    if (blWA) { blWA.classList.add('visible'); blWA.style.display = 'block'; }
    var cWA = document.getElementById('contenido-wa');
    if (cWA) cWA.style.display = 'none';
    var chWA = document.getElementById('chevron-wa');
    if (chWA) chWA.textContent = '▼';

    // Retefuente — visible pero colapsado (solo si no es NIT)
    if (tipodoc !== 'NIT') {
      var blR = document.getElementById('bloque-retefuente');
      blR.classList.add('visible'); blR.style.display = 'block';
      var cR = document.getElementById('contenido-ret');
      if (cR) cR.style.display = 'none';
      var chR = document.getElementById('chevron-ret');
      if (chR) chR.textContent = '▼';
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
    var pe3 = document.getElementById('ant-placa-editar');
    if (pe3) pe3.value = '';
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

    // Sincronizar input placa con visualización (ant-placa-edit legacy)
    var placaEdit = document.getElementById('ant-placa-edit');
    var placaHidden = document.getElementById('ant-placa');
    if (placaEdit) {
      placaEdit.addEventListener('input', function() {
        var val = this.value.toUpperCase().replace(/[^A-Z0-9]/g,'');
        this.value = val;
        placaHidden.value = val;
        document.getElementById('ant-placa-letras').textContent  = val.substring(0,3) || '---';
        document.getElementById('ant-placa-numeros').textContent = val.substring(3)   || '---';
      });
    }

    // Input editable de placa (nuevo)
    var placaEditarEl = document.getElementById('ant-placa-editar');
    if (placaEditarEl) {
      placaEditarEl.addEventListener('input', function() {
        var val = this.value.toUpperCase().replace(/[^A-Z0-9]/g,'');
        this.value = val;
        document.getElementById('ant-placa').value = val;
        document.getElementById('ant-placa-letras').textContent  = val.substring(0,3) || '---';
        document.getElementById('ant-placa-numeros').textContent = val.substring(3)   || '---';
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
          var pe2 = document.getElementById('ant-placa-editar');
          if (pe2) pe2.value = data.placa;
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
      var municipio = antMunicipioActual.toUpperCase();
      var apellidos = document.getElementById('ant-apellidos').value.trim().toUpperCase();
      var tipodoc   = document.getElementById('ant-tipodoc').value.trim().toUpperCase();
      var btn       = document.getElementById('ant-btn-impuesto');
      var resultado = document.getElementById('ant-result-depto');

      if (!placa||!cedula||!modelo||!municipio||!apellidos) {
        resultado.innerHTML='<div class="ant-alert error">Por favor completa todos los datos del vehiculo.</div>';
        return;
      }

      // ── PASO 1: Consultar vigencias (rapido) ──────────────────────────────
      btn.disabled = true;
      resultado.innerHTML = '<div class="ant-loading"><div class="ant-spinner-ring"></div><span>Consultando vigencias en la Gobernación de Antioquia...</span></div>';

      fetch(ANT_API+'/consultar/antioquia/vigencias?placa='+encodeURIComponent(placa)
        +'&identificacion='+encodeURIComponent(cedula)
        +'&modelo='+encodeURIComponent(modelo)
        +'&municipio_transito='+encodeURIComponent(municipio)
        +'&apellidos_propietario='+encodeURIComponent(apellidos)
        +'&tipo_documento='+encodeURIComponent(tipodoc))
        .then(function(r){ return r.json(); })
        .then(function(data) {
          btn.disabled = false;
          if (data.error) {
            resultado.innerHTML = '<div class="ant-alert error">'+data.error+'</div>';
            return;
          }

          var info = data.placa_info || {};
          var infoHtml = info.marca
            ? '<div class="ant-info"><div class="ant-info-item"><label>Placa</label><span>'+data.placa+'</span></div>'
              +'<div class="ant-info-item"><label>Marca</label><span>'+info.marca+' '+(info.linea||'')+'</span></div>'
              +'<div class="ant-info-item"><label>Modelo</label><span>'+(info.modelo||'')+'</span></div>'
              +'<div class="ant-info-item"><label>Propietario</label><span>'+(info.propietario||info.nombrePropietario||'')+'</span></div></div>' : '';

          // Paz y salvo
          if (data.sin_deuda) {
            if (data.avaluo) {
              antAvaluo = data.avaluo;
              if (hayTraspaso()) {
                setLiq('liq-retefuente', Math.round(data.avaluo/100));
                document.getElementById('liq-row-retefuente').style.display = 'grid';
              }
              var blRet = document.getElementById('bloque-retefuente');
              if (blRet) { blRet.style.display='none'; blRet.classList.remove('visible'); }
            }
            resultado.innerHTML = infoHtml
              + '<div class="ant-alert success">'+data.placa+' esta a paz y salvo con la Gobernacion de Antioquia.</div>'
              + (data.avaluo ? '<div class="ant-extra"><span>Retefuente (1%)</span><strong>$'+Math.round(data.avaluo/100).toLocaleString('es-CO')+'</strong></div>' : '');
            return;
          }

          // Hay vigencias — mostrar tabla con botón para consultar valores
          var vigencias = data.vigencias || [];
          var filasHtml = vigencias.map(function(v) {
            return '<tr><td>'+v.vigencia+'</td><td>Pendiente de pago</td><td style="text-align:right;color:#888;">Pendiente...</td></tr>';
          }).join('');

          resultado.innerHTML = infoHtml
            + '<table class="ant-table"><thead><tr><th>Vigencia</th><th>Estado</th><th style="text-align:right">Valor</th></tr></thead>'
            + '<tbody id="ant-tbody-vigencias">'+filasHtml+'</tbody></table>'
            + '<button id="ant-btn-valores" class="ant-btn ant-btn-primary" style="margin-top:12px;width:100%;">Consultar valores de cada vigencia</button>'
            + '<div id="ant-prog-wrap" style="display:none;margin-top:12px;">'
            + '<div class="ant-progreso-wrap"><div class="ant-progreso-msg" id="ant-prog-msg">Iniciando...</div>'
            + '<div class="ant-progreso-barra-bg"><div class="ant-progreso-barra" id="ant-prog-barra" style="width:5%"></div></div></div>'
            + '</div>';

          // ── PASO 2: Consultar valores (asincrono) ─────────────────────────
          document.getElementById('ant-btn-valores').addEventListener('click', function() {
            var btnVal = this;
            btnVal.disabled = true;
            document.getElementById('ant-prog-wrap').style.display = 'block';
            var antProgresoPorc = 5;

            fetch(ANT_API+'/consultar?placa='+encodeURIComponent(placa)
              +'&municipio=antioquia&identificacion='+encodeURIComponent(cedula)
              +'&modelo='+encodeURIComponent(modelo)
              +'&municipio_transito='+encodeURIComponent(municipio)
              +'&apellidos_propietario='+encodeURIComponent(apellidos)
              +'&tipo_documento='+encodeURIComponent(tipodoc))
              .then(function(r){ return r.json(); })
              .then(function(resp) {
                if (resp.error) {
                  btnVal.disabled = false;
                  document.getElementById('ant-prog-msg').textContent = 'Error: '+resp.error;
                  return;
                }

                // Respuesta desde caché — sin polling
                if (resp.estado === 'cache' && resp.resultado) {
                  btnVal.disabled = false;
                  document.getElementById('ant-prog-wrap').style.display = 'none';
                  var d = resp.resultado;
                  if (d.avaluo) {
                    antAvaluo = d.avaluo;
                    if (hayTraspaso()) {
                      setLiq('liq-retefuente', Math.round(d.avaluo/100));
                      document.getElementById('liq-row-retefuente').style.display = 'grid';
                    }
                    var blRet = document.getElementById('bloque-retefuente');
                    if (blRet) { blRet.style.display='none'; blRet.classList.remove('visible'); }
                  }
                  if (d.total) {
                    setLiq('liq-depto', d.total);
                    document.getElementById('liq-row-depto').style.display = 'grid';
                    var nVig = (d.registros || []).filter(function(r){ return r.total_vigencia > 0; }).length;
                    if (nVig > 0) {
                      var lblD = document.querySelector('#liq-row-depto .ant-liq-nombre');
                      if (lblD) lblD.textContent = 'Impuesto Departamental (' + nVig + ' vigencia' + (nVig > 1 ? 's' : '') + ')';
                    }
                  }
                  var tbody = document.getElementById('ant-tbody-vigencias');
                  if (tbody && d.registros) {
                    tbody.innerHTML = d.registros.map(function(r) {
                      return '<tr><td>'+r.vigencia+'</td><td>'+r.estado+'</td><td style="text-align:right">'
                        +(r.total_vigencia ? '$'+r.total_vigencia.toLocaleString('es-CO') : 'Ver con asesor')+'</td></tr>';
                    }).join('');
                  }
                  var totalHtml = (d.total ? '<div class="ant-total-bar"><span>Total vigencias</span><span>$'+d.total.toLocaleString('es-CO')+'</span></div>' : '')
                    + (d.avaluo ? '<div class="ant-extra"><span>Retefuente (1%)</span><strong>$'+Math.round(d.avaluo/100).toLocaleString('es-CO')+'</strong></div>' : '');
                  var btnValEl = document.getElementById('ant-btn-valores');
                  if (btnValEl) btnValEl.remove();
                  resultado.innerHTML += totalHtml;
                  return;
                }

                var jobId = resp.job_id;
                var timer = setInterval(function() {
                  fetch(ANT_API+'/consultar/estado?job_id='+jobId)
                    .then(function(r){ return r.json(); })
                    .then(function(estado) {
                      // Actualizar barra y mensaje
                      if (estado.mensaje) {
                        antProgresoPorc = Math.min(antProgresoPorc + 10, 90);
                        var msgEl = document.getElementById('ant-prog-msg');
                        var barEl = document.getElementById('ant-prog-barra');
                        if (msgEl) msgEl.textContent = estado.mensaje;
                        if (barEl) barEl.style.width = antProgresoPorc + '%';
                      }

                      if (estado.estado === 'listo') {
                        clearInterval(timer);
                        btnVal.disabled = false;
                        document.getElementById('ant-prog-wrap').style.display = 'none';
                        var d = estado.resultado;
                        if (!d) return;

                        // Rellenar valores en la tabla
                        if (d.avaluo) {
                          antAvaluo = d.avaluo;
                          if (hayTraspaso()) {
                            setLiq('liq-retefuente', Math.round(d.avaluo/100));
                            document.getElementById('liq-row-retefuente').style.display = 'grid';
                          }
                          var blRet = document.getElementById('bloque-retefuente');
                          if (blRet) { blRet.style.display='none'; blRet.classList.remove('visible'); }
                        }
                        if (d.total) {
                          setLiq('liq-depto', d.total);
                          document.getElementById('liq-row-depto').style.display = 'grid';
                          var nVig = (d.registros || []).filter(function(r){ return r.total_vigencia > 0; }).length;
                          if (nVig > 0) {
                            var lblD = document.querySelector('#liq-row-depto .ant-liq-nombre');
                            if (lblD) lblD.textContent = 'Impuesto Departamental (' + nVig + ' vigencia' + (nVig > 1 ? 's' : '') + ')';
                          }
                        }

                        // Actualizar filas de la tabla con los valores reales
                        var tbody = document.getElementById('ant-tbody-vigencias');
                        if (tbody && d.registros) {
                          tbody.innerHTML = d.registros.map(function(r) {
                            return '<tr><td>'+r.vigencia+'</td><td>'+r.estado+'</td><td style="text-align:right">'
                              +(r.total_vigencia ? '$'+r.total_vigencia.toLocaleString('es-CO') : 'Ver con asesor')+'</td></tr>';
                          }).join('');
                        }

                        // Agregar total y retefuente debajo de la tabla
                        var totalHtml = (d.total ? '<div class="ant-total-bar"><span>Total vigencias</span><span>$'+d.total.toLocaleString('es-CO')+'</span></div>' : '')
                          + (d.avaluo ? '<div class="ant-extra"><span>Retefuente (1%)</span><strong>$'+Math.round(d.avaluo/100).toLocaleString('es-CO')+'</strong></div>' : '')
                          + (d.excede_limite ? '<div class="ant-warning">'+d.mensaje_limite+'</div>' : '');

                        var btnValEl = document.getElementById('ant-btn-valores');
                        if (btnValEl) btnValEl.remove();
                        resultado.innerHTML += totalHtml;

                        // Mostrar bloque municipal si aplica
                        if (antMunicipioActual && MUNICIPIOS_MUNICIPALES[antMunicipioActual.toUpperCase()]) {
                          var blMun = document.getElementById('bloque-municipal');
                          blMun.classList.add('visible'); blMun.style.display = 'block';
                          document.getElementById('ant-result-municipal').innerHTML = '';
                          var contMun = document.getElementById('contenido-municipal');
                          if (contMun) contMun.style.display = 'block';
                          var chevMun = document.getElementById('chevron-municipal');
                          if (chevMun) chevMun.textContent = '▲';
                        }

                      } else if (estado.estado === 'error') {
                        clearInterval(timer);
                        btnVal.disabled = false;
                        document.getElementById('ant-prog-msg').textContent = 'Error: '+(estado.error||estado.mensaje);
                      }
                    })
                    .catch(function(){});
                }, 3000);
              })
              .catch(function(){
                btnVal.disabled = false;
                document.getElementById('ant-prog-msg').textContent = 'Error de conexion.';
              });
          });
        })
        .catch(function(){
          btn.disabled = false;
          resultado.innerHTML = '<div class="ant-alert error">Error de conexion.</div>';
        });
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
            var nVigM = (data.registros || []).length;
            if (nVigM > 0) {
              var lblM = document.querySelector('#liq-row-municipal .ant-liq-nombre');
              if (lblM) lblM.textContent = 'Impuesto Municipal (' + nVigM + ' vigencia' + (nVigM > 1 ? 's' : '') + ')';
            }
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
    var cil        = (document.getElementById('ant-cilindrada').value || '').trim();
    var cap        = (document.getElementById('ant-capacidad').value || '').trim();

    // Llenar datos del vehículo en el módulo retefuente
    var setDato = function(id, val) {
      var el = document.getElementById(id);
      if (el) { el.textContent = val; el.style.display = val ? '' : 'none'; }
    };
    setDato('ret-dato-clase',  clase);
    setDato('ret-dato-marca',  marca);
    setDato('ret-dato-linea',  linea);
    setDato('ret-dato-modelo', modelo);
    setDato('ret-dato-cil',    cil ? cil + 'cc' : '');
    setDato('ret-dato-cap',    cap ? cap + ' pax' : '');

    if (!marca || !clase || !modelo) return;

    var estado = document.getElementById('ant-ret-estado');
    var opcDiv = document.getElementById('ant-ret-opciones');
    estado.textContent = 'Buscando...';
    opcDiv.innerHTML   = '';
    document.getElementById('ant-ret-resultado').style.display = 'none';

    var cilindrada = (document.getElementById('ant-cilindrada').value || '').trim();
    fetch(ANT_API + '/retefuente/opciones?marca=' + encodeURIComponent(marca)
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
          var extraInfo = '';
          if (op.tonelaje && op.tonelaje > 0) extraInfo = ' · ' + op.tonelaje + ' toneladas';
          else if (op.pasajeros && op.pasajeros > 0) extraInfo = ' · ' + op.pasajeros + ' pasajeros';
          div.innerHTML =
            '<div class="ant-ret-opcion-nombre">' + op.linea + (op.cilindraje ? ' — ' + op.cilindraje + 'cc' : '') + extraInfo + '</div>' +
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

  // Recalcular numeración de pasos según bloques visibles
  window.antToggleAyuda = function(id) {
    var panel = document.getElementById(id);
    if (!panel) return;
    panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
  };

  function recalcularPasos() {
    var orden = [
      {id:'bloque-info',       titulo:'titulo-info',       nombre:'INFORMACION'},
      {id:'bloque-depto',      titulo:'titulo-depto',      nombre:'IMPUESTO DEPARTAMENTAL'},
      {id:'bloque-municipal',  titulo:'titulo-municipal',  nombre:'IMPUESTO MUNICIPAL'},
      {id:'bloque-tramites',   titulo:'titulo-tramites',   nombre:'TRAMITES'},
      {id:'bloque-retefuente', titulo:'titulo-ret',        nombre:'RETEFUENTE'},
      {id:'bloque-liq',        titulo:'titulo-liq',        nombre:'LIQUIDACION'},
      {id:'bloque-wa',         titulo:'titulo-wa',         nombre:'ENVIAR LIQUIDACION POR WHATSAPP'},
    ];
    var paso = 1;
    orden.forEach(function(b) {
      var bl  = document.getElementById(b.id);
      var tit = document.getElementById(b.titulo);
      if (!bl || !tit) return;
      var visible = bl.style.display !== 'none' && bl.style.cssText.indexOf('display: none') < 0;
      if (visible) {
        tit.textContent = 'PASO ' + paso + ' — ' + b.nombre;
        paso++;
      }
    });
  }

  window.antToggleInfoTop = function() {
    var contenido = document.getElementById('contenido-info-top');
    var chevron   = document.getElementById('chevron-info-top');
    if (!contenido) return;
    var visible = contenido.style.display !== 'none';
    contenido.style.display = visible ? 'none' : 'block';
    if (chevron) chevron.textContent = visible ? '▼' : '▲';
  };

  window.antToggleBloque = function(id) {
    var contenido = document.getElementById('contenido-'+id);
    var chevron   = document.getElementById('chevron-'+id);
    if (!contenido) return;
    var visible = contenido.style.display !== 'none';

    // Si va a expandirse, colapsar todos los demas bloques primero
    if (visible) {
      // Solo colapsar — no hace falta expandir otros
    } else {
      var todos = ['info','depto','municipal','tramites','ret','liq'];
      todos.forEach(function(bid) {
        if (bid === id) return;
        var c = document.getElementById('contenido-'+bid);
        var ch = document.getElementById('chevron-'+bid);
        if (c && c.style.display !== 'none') {
          c.style.display = 'none';
          if (ch) ch.textContent = '▼';
        }
      });
    }

    contenido.style.display = visible ? 'none' : 'block';
    if (chevron) chevron.textContent = visible ? '▼' : '▲';
  };

  window.antToggleInfo = function() {
    var contenido = document.getElementById('ant-info-contenido');
    var chevron   = document.getElementById('ant-info-chevron');
    var visible   = contenido.style.display !== 'none';
    contenido.style.display = visible ? 'none' : 'block';
    document.getElementById('ant-info-colapsado').style.display = 'none';
    chevron.textContent = visible ? '▼' : '▲';
    // Mostrar/ocultar placa mini y zona OCR
    var placaMini = document.getElementById('ant-placa-mini');
    if (infoConfirmada) {
      if (placaMini) placaMini.style.display = visible ? 'block' : 'none';
      var zonaOcr = document.getElementById('ant-zona-ocr');
      if (!visible && zonaOcr) zonaOcr.style.display = 'none';
    }
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

    // 2. Colapsar informacion y ocultar zona OCR/bienvenida
    document.getElementById('ant-info-contenido').style.display = 'none';
    document.getElementById('ant-info-chevron').textContent = '▼';
    // Ocultar zona OCR, botones de entrada, bienvenida, saludo y bloque-info-top
    ['ant-zona-ocr', 'ant-bienvenida', 'ant-info-expandido'].forEach(function(id) {
      var el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });
    var elSaludo = document.getElementById('ant-saludo');
    if (elSaludo) elSaludo.style.display = 'none';
    var elInfoTop = document.getElementById('bloque-info-top');
    if (elInfoTop) elInfoTop.style.display = 'none';
    // Ocultar botones de entrada (tomar foto, subir, manual)
    var entradaBtns = document.querySelector('.ant-entrada-btns');
    if (entradaBtns) entradaBtns.style.display = 'none';
    var camaraFile = document.getElementById('ant-camara-file');
    if (camaraFile) camaraFile.style.display = 'none';

    // Mostrar placa mini encima del wrap
    var placaMini = document.getElementById('ant-placa-mini');
    if (placaMini) placaMini.style.display = 'block';
    var plcLetras  = document.getElementById('ant-placa-letras');
    var plcNumeros = document.getElementById('ant-placa-numeros');
    var plcMun     = document.getElementById('ant-placa-municipio');
    var colLetras  = document.getElementById('ant-placa-col-letras');
    var colNumeros = document.getElementById('ant-placa-col-numeros');
    var colMun     = document.getElementById('ant-placa-col-municipio');
    if (colLetras && plcLetras)   colLetras.textContent  = plcLetras.textContent;
    if (colNumeros && plcNumeros) colNumeros.textContent = plcNumeros.textContent;
    if (colMun && plcMun)         colMun.textContent     = plcMun.textContent;

    // 3. Ocultar mensaje OCR y selector de municipio
    document.getElementById('ant-ocr-status').style.display = 'none';
    document.getElementById('ant-municipio-wrap').style.display = 'none';

    // 4. Mostrar todos los bloques expandidos
    mostrarYExpandirBloques();
    cargarTramites();
    mostrarFilasDefecto();
    recalcularPasos();
  };

  window.antConfirmarMunicipio = function(confirmado) {
    if (confirmado) {
      antMunicipioActual = document.getElementById('ant-municipio').value;
      var elSaludo2 = document.getElementById('ant-saludo');
      if (elSaludo2) elSaludo2.style.display = 'none';
      var elInfoTop2 = document.getElementById('bloque-info-top');
      if (elInfoTop2) elInfoTop2.style.display = 'none';
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

    // Generar texto y enviar por WhatsApp
    var cedula  = document.getElementById('ant-cedula').value.trim();
    var tipodoc = document.getElementById('ant-tipodoc').value;
    var tituloTramitesTexto = tramitesNombres.length > 0 ? tramitesNombres.join(' + ') : 'LIQUIDACION';
    var tituloLiq = '*TRAMITE ' + tituloTramitesTexto + (municipio ? ' ' + municipio : '') + ' ' + placa + ' ' + tipodoc + ' ' + cedula + '*';
    var lineasLiq = filas.map(function(f){ return '- ' + f.label + ': $' + f.valor.toLocaleString('es-CO'); }).join('\n');

    var tieneCompraventa = [1,2,3].some(function(n) {
      return (document.getElementById('ant-tramite-'+n).value || '').toUpperCase().includes('COMPRA');
    }) || hayTraspaso();

    var requisitosEspeciales = '';
    if (tieneCompraventa) {
      requisitosEspeciales = '\n- Contrato de Compra venta\n- Copia cedula del comprador\n- Improntas';
    }

    var autenticacionTexto = '';
    var munAuth = antMunicipioActual.toUpperCase();
    var reglasAuth = AUTENTICACION[munAuth];
    if (reglasAuth) {
      var reglaAuth = hayTraspaso() ? reglasAuth.traspaso : reglasAuth.otro;
      if (reglaAuth) {
        var docsAuth = reglaAuth.propietario || [];
        var docsCompradorAuth = reglaAuth.comprador || [];
        var notaAuth = reglaAuth.nota_especial || '';
        var lineasAuth = [];
        if (docsAuth.length > 0) lineasAuth.push('- Propietario debe autenticar: ' + docsAuth.join(' + ').toUpperCase());
        if (docsCompradorAuth.length > 0) lineasAuth.push('- Comprador debe autenticar: ' + docsCompradorAuth.join(' + ').toUpperCase());
        if (notaAuth) lineasAuth.push('- ' + notaAuth);
        if (lineasAuth.length > 0) autenticacionTexto = '\n\n*AUTENTICACION:*\n' + lineasAuth.join('\n');
      }
    }

    var textoWA = 'Liquidacion realizada por Tramy App\nhttps://juridicox.com/tramy/\n\n'
      + tituloLiq + '\n\n'
      + '*LIQUIDACION*\n'
      + lineasLiq + '\n'
      + 'TOTAL: $' + total.toLocaleString('es-CO') + '\n\n'
      + '*REQUISITOS:*\n'
      + '- Formulario\n'
      + '- Contrato de Mandato\n'
      + '- Copia cedula del propietario\n'
      + '- Copia de la tarjeta de propiedad'
      + requisitosEspeciales
      + autenticacionTexto + '\n\n'
      + '*NOTAS:*\n'
      + '- NO olvide firmas y huellas en todos los documentos.\n'
      + '- No ponga precio en la compra venta. En caso de tener que ponerlo puede usar el precio del avaluo.\n\n'
      + 'Liquidacion realizada por Tramy App\nhttps://juridicox.com/tramy/';

    var esMovil = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    if (esMovil && navigator.share) {
      navigator.share({title: tituloCompleto, text: textoWA})
        .catch(function(){ window.open('https://wa.me/?text='+encodeURIComponent(textoWA),'_blank'); });
    } else {
      var btnWA = document.getElementById('ant-btn-wa');
      function confirmarCopiado() {
        if (btnWA) {
          var orig = btnWA.innerHTML;
          btnWA.innerHTML = 'Texto copiado! Pega en WhatsApp';
          setTimeout(function(){ btnWA.innerHTML = orig; }, 3000);
        }
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textoWA).then(confirmarCopiado).catch(function() {
          var ta = document.createElement('textarea');
          ta.value = textoWA;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          confirmarCopiado();
        });
      } else {
        var ta = document.createElement('textarea');
        ta.value = textoWA;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        confirmarCopiado();
      }
    }
  };

  // ── NUEVA LIQUIDACION ────────────────────────────────────────────────────
  window.antNuevaLiquidacion = function() {
    window.location.reload();
    return;
    // Limpiar todo y volver al estado inicial
    limpiarCampos();
    antMunicipioActual = '';
    ocrLeido = false;
    infoConfirmada = false;
    antAvaluo = 0;
    antRetAvaluo = 0;
    antRetRetefuente = 0;

    // Ocultar todos los bloques excepto info
    ['bloque-depto','bloque-municipal','bloque-tramites','bloque-retefuente'].forEach(function(id) {
      var bl = document.getElementById(id);
      if (bl) { bl.style.display='none'; bl.classList.remove('visible'); }
    });
    var blLiq = document.getElementById('bloque-liq');
    if (blLiq) blLiq.style.cssText = 'display:none !important';
    var blRet = document.getElementById('bloque-retefuente');
    if (blRet) { blRet.style.display='none'; blRet.classList.remove('visible'); }

    // Mostrar y expandir bloque info
    var blInfo = document.getElementById('bloque-info');
    if (blInfo) { blInfo.style.display='block'; blInfo.classList.add('visible'); }
    var contInfo = document.getElementById('contenido-info');
    if (contInfo) contInfo.style.display='block';
    var chevInfo = document.getElementById('ant-info-chevron');
    if (chevInfo) chevInfo.textContent = '▲';

    // Mostrar bienvenida y ocultar municipio
    document.getElementById('ant-bienvenida').style.display = 'block';
    document.getElementById('ant-municipio-wrap').style.display = 'none';
    document.getElementById('ant-info-expandido').style.display = 'block';
    document.getElementById('ant-info-colapsado').style.display = 'none';

    // Mostrar zona OCR y botones de entrada
    document.getElementById('ant-zona-ocr').style.display = 'block';
    document.getElementById('ant-ocr-zone').style.display = 'block';
    document.getElementById('ant-preview-wrap').style.display = 'none';
    document.getElementById('ant-ocr-status').style.display = 'none';
    var entradaBtns = document.querySelector('.ant-entrada-btns');
    if (entradaBtns) entradaBtns.style.display = 'flex';

    // Limpiar liquidacion
    limpiarLiq();

    // Ocultar placa mini
    var placaMini = document.getElementById('ant-placa-mini');
    if (placaMini) placaMini.style.display = 'none';

    // Scroll al inicio
    window.scrollTo({top: 0, behavior: 'smooth'});
  };

  // ── REPORTE ──────────────────────────────────────────────────────────────
  var antReporteTipo = '';

  window.antToggleReporte = function() {
    var panel = document.getElementById('ant-reporte-panel');
    panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
    document.getElementById('ant-reporte-ok').style.display = 'none';
    document.getElementById('ant-reporte-texto').value = '';
    document.querySelectorAll('.ant-reporte-opcion').forEach(function(el){ el.classList.remove('sel'); });
    antReporteTipo = '';
  };

  window.antSelOpcion = function(el, tipo) {
    document.querySelectorAll('.ant-reporte-opcion').forEach(function(e){ e.classList.remove('sel'); });
    el.classList.add('sel');
    antReporteTipo = tipo;
  };

  window.antEnviarReporte = function() {
    if (!antReporteTipo) { alert('Selecciona qué está pasando.'); return; }
    var comentario  = document.getElementById('ant-reporte-texto').value.trim();
    var placaEl     = document.getElementById('ant-placa');
    var placa       = placaEl ? placaEl.value.trim() : '';
    var tipoGuardar = antReporteTipo; // guardar antes de resetear

    // Enviar primero
    fetch(ANT_API + '/reportar', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        tipo:       tipoGuardar,
        comentario: comentario,
        placa:      placa,
        municipio:  antMunicipioActual || '',
        pagina:     window.location.href
      })
    }).catch(function(){});

    // Mostrar confirmación inmediatamente
    antReporteTipo = '';
    document.getElementById('ant-reporte-ok').style.display = 'block';
    setTimeout(function(){
      document.getElementById('ant-reporte-panel').style.display = 'none';
      document.getElementById('ant-reporte-ok').style.display = 'none';
    }, 1500);
  };

})();
</script>
