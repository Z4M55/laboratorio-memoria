"""Tres laboratorios para explorar la memoria."""
from pathlib import Path
from html import escape
import json
import streamlit as st
import streamlit.components.v1 as components
from materiales import show_materials, local_asset, valid_link, MIMES

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Laboratorio de memoria", page_icon="◌", layout="wide", initial_sidebar_state="collapsed")
st.markdown((ROOT / "assets/style.css").read_text(encoding="utf-8"), unsafe_allow_html=True)
catalogo = json.loads((ROOT / "assets/laboratorios.json").read_text(encoding="utf-8"))
with st.sidebar:
    st.markdown("### ◌ Laboratorio de memoria")
    lab_id = st.radio("Explora los laboratorios", list(catalogo), format_func=lambda k: catalogo[k]["nombre"], key="laboratorio")
    st.caption("Escuchar · Mirar · Recordar")
lab = dict(catalogo[lab_id], id=lab_id)
st.markdown('<div class="brand">◌ &nbsp; LABORATORIO DE MEMORIA <span>HUMANIDADES DIGITALES</span></div>', unsafe_allow_html=True)
st.caption("☰ Abre el menú lateral para cambiar de laboratorio")
st.title(lab["nombre"])
st.markdown("### " + lab["subtitulo"])
# El nombre base permite incorporar PNG, JPG, JPEG o WebP sin cambiar código.
portada = next((ROOT / "assets" / (lab_id + ext) for ext in (".png", ".jpg", ".jpeg", ".webp") if (ROOT / "assets" / (lab_id + ext)).is_file()), None)
if portada:
    st.image(str(portada), width="stretch")
else:
    st.markdown('<div class="lab-cover ' + lab_id + '"><span>◌</span><p>' + escape(lab["subtitulo"]) + '</p></div>', unsafe_allow_html=True)
st.write(lab["invitacion"])

for i, pieza in enumerate(lab["materiales"]):
    with st.container(border=True):
        if pieza.get("titulo"):
            st.subheader(pieza["titulo"])
        if pieza.get("texto"):
            st.write(pieza["texto"])
        for tipo in ("imagen", "audio"):
            if not pieza.get(tipo):
                continue
            try:
                path = local_asset(pieza[tipo])
                if tipo == "imagen":
                    st.image(str(path), caption=pieza.get("credito"), width="stretch")
                else:
                    st.audio(path.read_bytes(), format=MIMES.get(path.suffix.lower(), "audio/mpeg"))
            except (ValueError, OSError):
                st.warning("Este material todavía no está disponible: " + tipo + ".")
        if pieza.get("enlace") and valid_link(pieza["enlace"]):
            st.link_button("Abrir recurso ↗", pieza["enlace"])
if not lab["materiales"]:
    st.markdown('<div class="empty-catalog">IMÁGENES Y ESCUCHAS<br><small>Un espacio para los materiales de esta experiencia.</small></div>', unsafe_allow_html=True)
show_materials(lab)

if lab_id == "lab":
    st.divider()
    st.caption(lab["pregunta"])
    obra = {"id": "lab", "titulo": lab["subtitulo"]}
    html = (ROOT / "assets/lienzo.html").read_text(encoding="utf-8")
    payload = json.dumps(obra, ensure_ascii=True).replace("<", "\\u003c")
    components.html(html.replace("__OBRA__", payload), height=830, scrolling=True)
    st.caption("Tu dibujo y tu susurro se conservan en este navegador. Descárgalos para guardarlos fuera de él.")
