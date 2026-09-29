from pathlib import Path
from html import escape
from io import BytesIO
import base64
import json

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from materiales import show_materials, local_asset, valid_link, MIMES


ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Laboratorio de memoria",
    page_icon="◌",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# IMÁGENES: lectura validada para evitar pantallas rotas
# --------------------------------------------------
def leer_imagen(path):
    with Image.open(path) as imagen:
        imagen.load()
        salida = BytesIO()
        imagen.convert("RGB").save(salida, format="JPEG", quality=90)
        return salida.getvalue()


def mostrar_imagen(path, credito=None):
    try:
        st.image(
            leer_imagen(path),
            caption=credito,
            width="stretch",
        )
    except (OSError, ValueError, Image.DecompressionBombError):
        st.warning(
            f"No se puede abrir {path.name}. "
            "Sube nuevamente el archivo original de la imagen."
        )


# --------------------------------------------------
# GEOGRAFÍA SONORA: integrada directamente en MIRAR
# --------------------------------------------------
def geografia_sonora():
    st.subheader("Geografía de una memoria")
    st.write(
        "Activa la escucha y recorre la imagen. "
        "Cada zona abre una canción; también puedes tocarla."
    )

    imagen_path = next(
        (
            ROOT / "assets" / f"Nel_G{extension}"
            for extension in (".png", ".jpg", ".jpeg", ".webp")
            if (ROOT / "assets" / f"Nel_G{extension}").is_file()
        ),
        None,
    )

    if imagen_path is None:
        st.info("Añade la imagen Nel_G.png dentro de assets.")
        return

    try:
        imagen_bytes = leer_imagen(imagen_path)
    except (OSError, ValueError, Image.DecompressionBombError):
        st.warning(
            "Nel_G no contiene una imagen válida. "
            "Vuelve a subir la imagen original."
        )
        return

    # Rectángulos: izquierda, arriba, ancho, alto.
    # Todas las medidas son porcentajes de la imagen.
    # Ajusta estas posiciones a los elementos de tu obra.
    zonas = [
        {
            "nombre": "Dime Patria",
            "archivo": "DimePatria.mp3",
            "rect": [0, 0, 33, 85],
        },
        {
            "nombre": "Fuego en la Ruta",
            "archivo": "FuegoenlaRuta.mp3",
            "rect": [33, 0, 34, 85],
        },
        {
            "nombre": "Un Pasaporte Y Tres Valijas",
            "archivo": "UnPasaporteYTresValijas.mp3",
            "rect": [67, 0, 33, 85],
        },
        {
            "nombre": "Silencio",
            "archivo": None,
            "rect": [0, 85, 100, 15],
        },
    ]

    faltantes = []

    for zona in zonas:
        zona["audio"] = None
        zona["disponible"] = True

        if zona["archivo"] is None:
            continue

        audio_path = ROOT / "assets" / "audio" / zona["archivo"]

        if not audio_path.is_file():
            zona["disponible"] = False
            faltantes.append(zona["archivo"])
            continue

        if audio_path.stat().st_size > 10 * 1024 * 1024:
            zona["disponible"] = False
            st.warning(
                f"{zona['archivo']}: utiliza un fragmento menor de 10 MB."
            )
            continue

        zona["audio"] = base64.b64encode(
            audio_path.read_bytes()
        ).decode("ascii")

    if faltantes:
        st.info(
            "Faltan estos archivos en assets/audio/: "
            + ", ".join(faltantes)
        )

    datos = {
        "imagen": (
            "data:image/jpeg;base64,"
            + base64.b64encode(imagen_bytes).decode("ascii")
        ),
        "zonas": zonas,
    }

    html = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    background: #202c2c;
    color: #eee5d4;
    font: 15px system-ui, sans-serif;
}

.barra {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    padding: 14px;
}

button {
    padding: 11px 15px;
    border: 1px solid #ad9e84;
    border-radius: 7px;
    background: #33413b;
    color: #eee5d4;
    cursor: pointer;
    font: inherit;
}

button:disabled {
    opacity: .5;
    cursor: default;
}

button:focus-visible {
    outline: 3px solid #f0bf91;
    outline-offset: 2px;
}

button[aria-pressed="true"] {
    background: #925e49;
}

label {
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

input { accent-color: #d9a17b; }

#escena {
    position: relative;
    line-height: 0;
}

#imagen {
    display: block;
    width: 100%;
    height: auto;
}

.zona {
    position: absolute;
    border: 0;
    border-radius: 0;
    background: transparent;
    padding: 0;
}

.zona:hover {
    background: #efd9b51c;
}

.guias .zona {
    border: 1px dashed #fff9;
}

#estado {
    min-height: 48px;
    padding: 14px;
    line-height: 1.5;
}

.nota {
    margin: 0;
    padding: 0 14px 16px;
    color: #c3c2b0;
    font-size: 13px;
    line-height: 1.5;
}
</style>
</head>

<body>
<div class="barra">
    <button id="activar">Activar escucha</button>

    <label>
        Volumen
        <input id="volumen" type="range"
               min="0" max="100" value="35">
    </label>

    <label>
        <input id="guias" type="checkbox">
        Mostrar zonas
    </label>
</div>

<div id="escena">
    <img id="imagen" alt="Nel_G: imagen para explorar mediante sonidos.">
</div>

<div id="estado" role="status" aria-live="polite">
    Activa la escucha para comenzar.
</div>

<div class="barra" id="botones"
     aria-label="Elegir una zona sonora"></div>

<p class="nota">
    Recorre con el cursor o toca una zona.
    También puedes usar Tab y Enter en los botones.
    Pulsa Escape para detener la escucha.
</p>

<script>
const datos = __DATOS__;
const $ = id => document.getElementById(id);

$("imagen").src = datos.imagen;

let contexto = null;
let volumenGeneral = null;
let activo = false;
let preparando = false;
let zonaActual = -1;
let generacion = 0;

const buffers = [];
const errores = new Set();
const voces = new Set();
const botones = [];

function apagarVoces(inmediato = false) {
    if (!contexto) return;

    const ahora = contexto.currentTime;

    for (const voz of [...voces]) {
        if (voz.saliendo && !inmediato) continue;

        voz.saliendo = true;
        voz.ganancia.gain.cancelScheduledValues(ahora);

        try {
            if (inmediato) {
                voz.ganancia.gain.setValueAtTime(0, ahora);
                voz.fuente.stop();
            } else {
                voz.ganancia.gain.setTargetAtTime(0, ahora, 0.08);
                voz.fuente.stop(ahora + 0.4);
            }
        } catch (error) {
            // La fuente ya terminó.
        }
    }
}

function seleccionarZona(indice) {
    if (!activo || indice === zonaActual) return;

    zonaActual = indice;
    apagarVoces();

    botones.forEach((boton, posicion) => {
        boton.setAttribute(
            "aria-pressed",
            String(posicion === indice)
        );
    });

    if (indice < 0) {
        $("estado").textContent = "Silencio.";
        return;
    }

    const zona = datos.zonas[indice];

    if (!zona.disponible) {
        $("estado").textContent =
            zona.nombre + ": archivo todavía no disponible.";
        return;
    }

    if (errores.has(indice)) {
        $("estado").textContent =
            zona.nombre + ": no se pudo leer el audio.";
        return;
    }

    $("estado").textContent = zona.nombre;

    // La zona de silencio no tiene audio.
    if (!buffers[indice]) return;

    const fuente = contexto.createBufferSource();
    fuente.buffer = buffers[indice];
    fuente.loop = true;

    const ganancia = contexto.createGain();
    ganancia.gain.value = 0;

    fuente.connect(ganancia);
    ganancia.connect(volumenGeneral);

    const voz = {
        fuente,
        ganancia,
        saliendo: false
    };

    voces.add(voz);

    fuente.onended = () => {
        fuente.disconnect();
        ganancia.disconnect();
        voces.delete(voz);
    };

    fuente.start();

    ganancia.gain.linearRampToValueAtTime(
        1,
        contexto.currentTime + 0.35
    );
}

function detener() {
    generacion += 1;
    activo = false;
    zonaActual = -1;

    apagarVoces(true);

    botones.forEach(boton => {
        boton.setAttribute("aria-pressed", "false");
    });

    $("activar").textContent = "Activar escucha";
    $("estado").textContent = "Escucha detenida.";
}

$("activar").onclick = async () => {
    if (preparando) return;

    if (activo) {
        detener();
        return;
    }

    preparando = true;
    $("activar").disabled = true;
    const intento = ++generacion;

    try {
        if (!contexto) {
            const AudioAPI =
                window.AudioContext || window.webkitAudioContext;

            if (!AudioAPI) {
                throw new Error("Audio no compatible");
            }

            contexto = new AudioAPI();
            volumenGeneral = contexto.createGain();
            volumenGeneral.gain.value =
                Number($("volumen").value) / 100;

            volumenGeneral.connect(contexto.destination);
        }

        // Se ejecuta desde el clic que autoriza la escucha.
        await contexto.resume();

        $("estado").textContent = "Preparando las canciones…";

        await Promise.all(
            datos.zonas.map(async (zona, indice) => {
                if (!zona.audio || buffers[indice]) return;

                try {
                    const bytes = Uint8Array.from(
                        atob(zona.audio),
                        caracter => caracter.charCodeAt(0)
                    );

                    buffers[indice] =
                        await contexto.decodeAudioData(bytes.buffer);

                    errores.delete(indice);
                } catch (error) {
                    errores.add(indice);
                }
            })
        );

        if (intento !== generacion || document.hidden) return;

        if (!buffers.some(Boolean)) {
            $("estado").textContent =
                "No hay canciones disponibles. " +
                "Comprueba los archivos de audio.";
            return;
        }

        activo = true;
        zonaActual = -1;
        $("activar").textContent = "Detener escucha";

        $("estado").textContent = errores.size
            ? "Puedes explorar. Algunos audios no pudieron abrirse."
            : "Recorre la imagen o elige una canción.";
    } catch (error) {
        detener();
        $("estado").textContent =
            "No se pudo activar el sonido. " +
            "Comprueba los archivos y vuelve a intentarlo.";
    } finally {
        preparando = false;
        $("activar").disabled = false;
    }
};

datos.zonas.forEach((zona, indice) => {
    const [izquierda, arriba, ancho, alto] = zona.rect;

    const area = document.createElement("button");
    area.className = "zona";
    area.tabIndex = -1;
    area.setAttribute("aria-label", zona.nombre);

    Object.assign(area.style, {
        left: izquierda + "%",
        top: arriba + "%",
        width: ancho + "%",
        height: alto + "%"
    });

    area.onpointerenter = evento => {
        if (evento.pointerType === "mouse") {
            seleccionarZona(indice);
        }
    };

    area.onclick = () => seleccionarZona(indice);
    $("escena").appendChild(area);

    const boton = document.createElement("button");
    boton.textContent = zona.nombre;
    boton.setAttribute("aria-pressed", "false");
    boton.onclick = () => seleccionarZona(indice);

    $("botones").appendChild(boton);
    botones.push(boton);
});

$("escena").onpointerleave = evento => {
    if (evento.pointerType === "mouse") {
        seleccionarZona(-1);
    }
};

$("escena").onpointermove = evento => {
    if (
        evento.pointerType === "mouse"
        && evento.target === $("imagen")
    ) {
        seleccionarZona(-1);
    }
};

$("volumen").oninput = () => {
    if (!volumenGeneral) return;

    volumenGeneral.gain.setTargetAtTime(
        Number($("volumen").value) / 100,
        contexto.currentTime,
        0.03
    );
};

$("guias").onchange = () => {
    $("escena").classList.toggle(
        "guias",
        $("guias").checked
    );
};

document.addEventListener("visibilitychange", () => {
    if (document.hidden) detener();
});

window.addEventListener("pagehide", () => {
    detener();
    if (contexto) contexto.close();
});

window.addEventListener("keydown", evento => {
    if (evento.key === "Escape") detener();
});
</script>
</body>
</html>
"""

    datos_seguros = json.dumps(
        datos, ensure_ascii=True
    ).replace("<", "\\u003c")

    components.html(
        html.replace("__DATOS__", datos_seguros),
        height=850,
        scrolling=True,
    )

    st.caption(
        "Las zonas iniciales son tres franjas de escucha "
        "y una franja inferior de silencio. "
        "Se pueden ajustar a los elementos de Nel_G."
    )

    st.markdown(
        "**¿Qué parte de la imagen siguió sonando en ti?** "
        "Entra en RECORDAR y dibuja esa huella."
    )


# --------------------------------------------------
# ESTILO Y CATÁLOGO EXISTENTES
# --------------------------------------------------
estilos = ROOT / "assets" / "style.css"

if estilos.is_file():
    st.markdown(
        estilos.read_text(encoding="utf-8"),
        unsafe_allow_html=True,
    )

try:
    catalogo = json.loads(
        (ROOT / "assets" / "laboratorios.json").read_text(
            encoding="utf-8"
        )
    )
except (OSError, ValueError):
    st.error("No se pudo leer assets/laboratorios.json.")
    st.stop()


# --------------------------------------------------
# MENÚ: mantiene los tres apartados existentes
# --------------------------------------------------
with st.sidebar:
    st.markdown("### ◌ Laboratorio de memoria")

    lab_id = st.radio(
        "Explora los laboratorios",
        list(catalogo),
        format_func=lambda clave: catalogo[clave]["nombre"],
        key="laboratorio",
    )

    st.caption("Escuchar · Mirar · Recordar")

lab = dict(catalogo[lab_id], id=lab_id)

st.markdown(
    '<div class="brand">'
    '◌ &nbsp; LABORATORIO DE MEMORIA'
    '<span>HUMANIDADES DIGITALES</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.caption("☰ Abre el menú lateral para cambiar de laboratorio")
st.title(lab["nombre"])
st.markdown("### " + lab["subtitulo"])


# --------------------------------------------------
# PORTADA DE CADA LABORATORIO
# --------------------------------------------------
portada = next(
    (
        ROOT / "assets" / f"{lab_id}{extension}"
        for extension in (".png", ".jpg", ".jpeg", ".webp")
        if (ROOT / "assets" / f"{lab_id}{extension}").is_file()
    ),
    None,
)

if portada:
    mostrar_imagen(portada)
else:
    st.markdown(
        '<div class="lab-cover '
        + escape(lab_id, quote=True)
        + '"><span>◌</span><p>'
        + escape(lab["subtitulo"])
        + "</p></div>",
        unsafe_allow_html=True,
    )

st.write(lab["invitacion"])


# --------------------------------------------------
# MATERIALES DEL CATÁLOGO EXISTENTE
# --------------------------------------------------
for pieza in lab.get("materiales", []):
    with st.container(border=True):
        if pieza.get("titulo"):
            st.subheader(pieza["titulo"])

        if pieza.get("texto"):
            st.write(pieza["texto"])

        if pieza.get("imagen"):
            try:
                mostrar_imagen(
                    local_asset(pieza["imagen"]),
                    pieza.get("credito"),
                )
            except (ValueError, OSError):
                st.warning("No se encontró la imagen de esta pieza.")

        if pieza.get("audio"):
            try:
                audio_path = local_asset(pieza["audio"])
                st.audio(
                    audio_path.read_bytes(),
                    format=MIMES.get(
                        audio_path.suffix.lower(),
                        "audio/mpeg",
                    ),
                )
            except (ValueError, OSError):
                st.warning("No se encontró el audio de esta pieza.")

        if pieza.get("enlace") and valid_link(pieza["enlace"]):
            st.link_button("Abrir recurso ↗", pieza["enlace"])

show_materials(lab)


# --------------------------------------------------
# MIRAR: imagen + canciones
# --------------------------------------------------
if lab_id == "lab_view":
    st.divider()
    geografia_sonora()


# --------------------------------------------------
# RECORDAR: conserva la pizarra anterior
# --------------------------------------------------
if lab_id == "lab":
    st.divider()

    st.caption(
        lab.get(
            "pregunta",
            "¿Cómo dibujarías la memoria que despertó la experiencia?",
        )
    )

    lienzo_path = ROOT / "assets" / "lienzo.html"

    if lienzo_path.is_file():
        obra = {
            "id": "lab",
            "titulo": lab["subtitulo"],
        }

        datos = json.dumps(
            obra, ensure_ascii=True
        ).replace("<", "\\u003c")

        lienzo = lienzo_path.read_text(encoding="utf-8")

        components.html(
            lienzo.replace("__OBRA__", datos),
            height=830,
            scrolling=True,
        )

        st.caption(
            "Tu dibujo y tu susurro se conservan en este navegador. "
            "Descárgalos para guardarlos fuera de él."
        )
    else:
        st.warning("Falta assets/lienzo.html para mostrar la pizarra.")
