"""Materiales permanentes del catálogo y aportes temporales de cada sesión."""
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit
from PIL import Image, UnidentifiedImageError
import streamlit as st

ROOT = Path(__file__).resolve().parent
MIMES = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg", ".m4a": "audio/mp4"}


def valid_link(value):
    try:
        parts = urlsplit(value)
        return parts.scheme in ("https", "http") and bool(parts.hostname) and not parts.username
    except ValueError:
        return False


def local_asset(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to((ROOT / "assets").resolve()) or not path.is_file():
        raise ValueError("El archivo debe existir dentro de assets/.")
    return path


def show_materials(obra):
    key = "materiales_" + obra["id"]
    saved = st.session_state.setdefault(key, {})
    with st.expander("＋ Probar imágenes y audio en este laboratorio", expanded=False):
        st.caption("Añade una imagen, una escucha o un enlace. Los archivos se procesan en el servidor durante esta sesión; el catálogo permanente se prepara en assets/laboratorios.json.")
        with st.form("form_" + obra["id"], clear_on_submit=True):
            image = st.file_uploader("Imagen · máximo 10 MB", type=["png", "jpg", "jpeg", "webp"], key="img_" + obra["id"])
            audio = st.file_uploader("Audio · máximo 25 MB", type=["mp3", "wav", "ogg", "m4a"], key="audio_" + obra["id"])
            link = st.text_input("Enlace a la obra, video o archivo", value=saved.get("enlace", obra.get("enlace", "")), placeholder="https://…")
            submitted = st.form_submit_button("Usar estos materiales")
        if submitted:
            try:
                update = dict(saved)
                if link.strip() and not valid_link(link.strip()):
                    raise ValueError("Escribe un enlace completo que empiece con https:// o http://.")
                update["enlace"] = link.strip()
                if image is not None:
                    if image.size > 10 * 1024 * 1024:
                        raise ValueError("La imagen supera 10 MB.")
                    raw = image.getvalue()
                    with Image.open(BytesIO(raw)) as im:
                        im.verify()
                    update["imagen"] = raw
                if audio is not None:
                    if audio.size > 25 * 1024 * 1024:
                        raise ValueError("El audio supera 25 MB.")
                    update["audio"] = audio.getvalue()
                    update["audio_mime"] = MIMES[Path(audio.name).suffix.lower()]
                st.session_state[key] = saved = update
                st.success("Materiales listos para esta sesión.")
            except (ValueError, OSError, UnidentifiedImageError, Image.DecompressionBombError):
                st.error("Revisa el enlace y los archivos: imagen válida de hasta 10 MB y audio de hasta 25 MB. El enlace debe empezar con https:// o http://.")
        if saved and st.button("Quitar mis materiales de esta obra", key="quitar_" + obra["id"]):
            st.session_state[key] = saved = {}
            st.rerun()
    for kind in ("imagen", "audio"):
        source = saved.get(kind) or obra.get(kind)
        if not source:
            continue
        try:
            if isinstance(source, str):
                path = local_asset(source)
                source = path.read_bytes()
                mime = MIMES.get(path.suffix.lower(), "audio/mpeg")
            else:
                mime = saved.get("audio_mime", "audio/mpeg")
            if kind == "imagen":
                st.image(source, caption=obra.get("credito", "Material de la obra"), width="stretch")
            else:
                st.audio(source, format=mime)
        except (ValueError, OSError):
            st.warning("No se pudo mostrar el material. Revisa el archivo de " + kind + ".")
    link = saved.get("enlace", obra.get("enlace", ""))
    if link and valid_link(link):
        st.link_button("Abrir obra o recurso ↗", link)
