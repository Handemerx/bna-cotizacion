# Cotización Banco Nación automática — Guía paso a paso

Este sistema lee la **Cotización Divisas del Banco Nación** sola, varias veces al día,
y la muestra en la web de Handel. Una vez configurado, NO tenés que tocar nada nunca más.

## Qué hace
1. Un "robot" (GitHub Actions) entra al BNA 4 veces por día (lun a vie) y lee el dólar divisa.
2. Guarda el valor en un archivo `cotizacion.json`.
3. La web de Handel lee ese archivo y muestra Compra/Venta del BNA exacto.

Mientras tanto, si el robot fallara algún día, la web muestra automáticamente el dólar
oficial de referencia (dolarapi) para no quedar nunca en blanco.

---

## PASO A PASO (una sola vez, ~10 minutos)

### 1. Crear cuenta en GitHub (si no tenés)
- Entrá a https://github.com → "Sign up". Es gratis. Anotá usuario y contraseña.

### 2. Crear un repositorio nuevo
- Arriba a la derecha, botón "+" → "New repository".
- Nombre: `bna-cotizacion`
- Marcá **Public** (tiene que ser público para que la web lo lea gratis).
- Click "Create repository".

### 3. Subir los archivos
- En el repo nuevo, click en "uploading an existing file" (o Add file → Upload files).
- Arrastrá estos 2 archivos que están en este paquete:
  - `scrape_bna.py`
  - `cotizacion.json`
- Y la carpeta `.github` completa (que adentro tiene `workflows/cotizacion.yml`).
  - Si no te deja arrastrar la carpeta, creala a mano: Add file → Create new file →
    escribí en el nombre: `.github/workflows/cotizacion.yml` y pegá el contenido del archivo.
- Abajo, click "Commit changes".

### 4. Activar los permisos del robot
- En el repo: Settings → Actions → General.
- Bajá hasta "Workflow permissions".
- Marcá **"Read and write permissions"** → Save.

### 5. Probar que funciona
- Pestaña "Actions" del repo → click en "Actualizar cotizacion BNA" → "Run workflow" → "Run workflow".
- Esperá ~1 minuto. Si sale tilde verde ✓, funcionó.
- Abrí el archivo `cotizacion.json` en el repo: tiene que mostrar el valor del BNA del día.

### 6. Copiar la URL del JSON
- Click en `cotizacion.json` → botón "Raw".
- Copiá la URL de la barra del navegador. Va a ser algo así:
  `https://raw.githubusercontent.com/TU-USUARIO/bna-cotizacion/main/cotizacion.json`
- **Pasame esa URL** y yo la pego en la web (o seguí el paso 7 vos misma).

### 7. (Opcional, lo puede hacer Claude) Pegar la URL en la web
- En `index.html`, buscá el texto `REEMPLAZAR_URL_BNA`.
- Reemplazalo por la URL del paso 6 (dejá las comillas).
- Subí el index a DonWeb como siempre.

---

## Listo
A partir de ahí el robot corre solo de lunes a viernes, 4 veces al día, y la web
siempre muestra el dólar divisa del Banco Nación actualizado. Cero mantenimiento.

Si algún día el BNA cambia el diseño de su página y el robot deja de leer bien,
la web sigue mostrando el dólar oficial de referencia hasta que se ajuste el robot.
