# Laboratorio de memoria · Taller de Humanidades Digitales

Tres apartados independientes en un menú lateral ☰, inicialmente cerrado:

1. **ESCUCHAR — La memoria tiene sonido** (`lab_sound`).
2. **MIRAR — Cuando una imagen comienza a sonar** (`lab_view`).
3. **RECORDAR — Laboratorio de memorias** (`lab`). Solo este apartado contiene la pizarra.

## Portadas de cada laboratorio

Guarda las imágenes de 1920 × 1080 en `assets/` con estos nombres:

- `lab_sound.png`
- `lab_view.png`
- `lab.png`

También se admiten `.jpg`, `.jpeg` y `.webp` con el mismo nombre base. Usa una sola portada por laboratorio; si hay varias, se prioriza PNG, JPG, JPEG y WebP en ese orden. Se muestran completas, adaptadas al ancho disponible y sin recorte. Los nombres distinguen mayúsculas y minúsculas al desplegar. Hasta incorporarlas se muestra una portada provisional, sin errores ni imágenes rotas.

## Catálogo de imágenes y audios

Cada apartado tiene su propia lista `materiales` en **assets/laboratorios.json**. Las listas comienzan vacías para preparar el taller con tus contenidos. Añade tantos elementos como necesites; se presentan en el orden del archivo. Cada elemento puede tener imagen, audio, texto y enlace, o solo alguno de ellos.

Ejemplo de elemento para añadir dentro de `materiales` (reemplaza las rutas por archivos reales):

```json
{
  "titulo": "Una memoria del territorio",
  "texto": "Escucha este lugar antes de continuar.",
  "imagen": "assets/escuchar/territorio.jpg",
  "audio": "assets/escuchar/paisaje.mp3",
  "credito": "Autoría y procedencia de la imagen",
  "enlace": "https://example.org/obra"
}
```

Organización sugerida para tus archivos:

```text
assets/
  lab_sound.png
  lab_view.png
  lab.png
  laboratorios.json
  escuchar/       imágenes y audios de ESCUCHAR
  mirar/          imágenes y audios de MIRAR
  recordar/       imágenes y audios de RECORDAR
```

Las portadas y carpetas de medios se añadirán cuando tengas los materiales. Las rutas siempre deben apuntar a archivos dentro de `assets/`. Utiliza PNG/JPG/WebP para imágenes y MP3/WAV/OGG/M4A para audio; su reproducción depende del navegador. El audio no comienza automáticamente. Los enlaces abren el recurso externo.

En cada laboratorio también hay un panel **Probar imágenes y audio en este laboratorio**: permite probar una imagen (hasta 10 MB), un audio (hasta 25 MB) y un enlace durante la sesión. Estos aportes se mantienen separados por laboratorio al navegar. Se procesan temporalmente en el servidor; no modifican el catálogo ni se guardan en GitHub, y pueden perderse al recargar. Para publicarlos de forma permanente, incorpora los archivos y sus rutas al catálogo.

## Pizarra de RECORDAR

Dibujo con ratón, lápiz o tacto, color, grosor, borrador, deshacer, rehacer y limpieza con confirmación. Incluye sentimiento, susurro, atmósfera sintética opcional y descargas PNG y JSON. Canvas HTML5 está integrado mediante la API de componentes de Streamlit; no requiere OpenAI, TensorFlow, gTTS ni streamlit-drawable-canvas.

El dibujo y el susurro se guardan en el navegador si permite almacenamiento local, sin envío al servidor ni galería colectiva. Descarga PNG para la imagen y JSON para trazos y textos; esta versión no importa JSON. En un dispositivo compartido otra persona puede recuperar el borrador. Los controles admiten teclado; el dibujo requiere un dispositivo apuntador. Las antiguas piezas de demostración de `assets/obras.json` se conservan como referencia, pero ya no se muestran.

## Ejecutar

Recomendado: Python 3.12. Desde la carpeta del proyecto:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Publicar más adelante

1. Completa `assets/laboratorios.json` y añade las portadas y los medios a `assets/`.
2. Sube el contenido del proyecto a GitHub, incluyendo `.streamlit/config.toml`. `app.py` y `requirements.txt` deben estar en la raíz. No subas `.test-deps/`, `.venv/` ni archivos privados.
3. En https://share.streamlit.io conecta el repositorio, selecciona la rama y `app.py`, elige Python 3.12 en opciones avanzadas y despliega.

Guía: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Archivos principales

- `app.py`: menú, portadas y recorrido de los tres laboratorios.
- `materiales.py`: pruebas de imagen, audio y enlaces por sesión.
- `assets/laboratorios.json`: catálogo permanente separado por laboratorio.
- `assets/lienzo.html`: pizarra exclusiva de RECORDAR.
- `assets/style.css` y `.streamlit/config.toml`: identidad visual.
- `requirements.txt`: dependencia de Streamlit.

## Verificación

Comprobar el menú en escritorio y móvil, las tres portadas completas y el orden de los materiales. Probar reproducción y pausa de audio, separación de aportes por laboratorio, persistencia del dibujo al cambiar de apartado y descargas. La app está preparada para ejecutar y publicar; no se ha subido a GitHub ni desplegado.
