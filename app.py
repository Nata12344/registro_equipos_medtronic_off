import streamlit as st
from PIL import Image
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

# Configuración de página
st.set_page_config(page_title="Registro Medtronic", layout="centered", page_icon="🩺")

# Estilo visual
st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }
    .title {
        text-align: center;
        font-size: 22px;
        color: #000000;
        font-family: 'Arial', sans-serif;
        margin-top: 20px;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 200px;
        height: 40px;
        background-color: #002d5d;
        color: white;
        border: none;
        border-radius: 8px;
        margin: auto;
        display: block;
    }
    .stButton>button:hover {
        background-color: #0053a6;
    }
    </style>
""", unsafe_allow_html=True)

# Datos iniciales
correos_ingenieros = {
    "Nicolle Riaño": "nicolle.n.riano@medtronic.com"
}

# Estados iniciales
if "tipo_operacion" not in st.session_state:
    st.session_state.tipo_operacion = "Ingreso"
if "equipos" not in st.session_state:
    st.session_state.equipos = []
if "cliente" not in st.session_state:
    st.session_state.cliente = ""
if "movimiento" not in st.session_state:
    st.session_state.movimiento = ""

# SIDEBAR: logo + ingreso/salida
with st.sidebar:
    try:
        logo = Image.open("logo_medtronic.png")
        st.image(logo, width=150)
    except:
        st.warning("No se pudo cargar el logo.")

    st.markdown("**Información confidencial - uso exclusivo de Medtronic**", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ¿Qué deseas registrar?")
    st.session_state.tipo_operacion = st.radio("Tipo de operación:", ["Ingreso", "Salida"])

# TÍTULO CENTRAL
# ENCABEZADO AZUL CON LOGO Y TÍTULO
st.markdown("""
    <div style="background-color: #003087; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 20px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Medtronic_logo.svg/320px-Medtronic_logo.svg.png" width="80">
            <div>
                <p style="color: white; margin: 0; font-weight: 300; font-size: 16px;">
                    {tipo_operacion} – Registro de Equipos
                </p>
                <p style="color: white; font-size: 12px; margin: 0; font-weight: 300;">
                    Información confidencial – uso exclusivo de Medtronic
                </p>
            </div>
        </div>
    </div>
""".format(tipo_operacion=st.session_state.tipo_operacion), unsafe_allow_html=True)

# Información general
st.markdown("#### Información general")
cliente = st.text_input("Cliente:", value=st.session_state.cliente)
ingeniero = st.selectbox("Ingeniero:", list(correos_ingenieros.keys()), index=0)
movimiento = st.text_input("Movimiento / Delivery:", value=st.session_state.movimiento)

st.session_state.cliente = cliente
st.session_state.movimiento = movimiento

# Equipos
st.divider()
st.markdown("### Equipos registrados")

if st.button("Agregar equipo"):
    st.session_state.equipos.append({})

equipos_a_eliminar = []

for idx, equipo in enumerate(st.session_state.equipos):
    with st.expander(f"Equipo {idx + 1}", expanded=True):
        tipo = st.selectbox(f"Tipo de equipo {idx + 1}:", ["WEM", "ForceTriad", "FX", "PB840", "PB980", "BIS VISTA", "CONSOLA DE CAMARA"], key=f"tipo_{idx}")
        serial = st.text_input("Serial:", key=f"serial_{idx}")
        accesorios = st.text_input("Accesorios:", key=f"accesorios_{idx}")

        st.markdown("**Observaciones físicas:**")
        observaciones = []
        opciones = ["Carcasa rayada", "Golpes visibles", "Pantalla rayada", "Pieza rotos", "Cable dañado"]
        for obs in opciones:
            if st.checkbox(obs, key=f"{obs}_{idx}"):
                observaciones.append(obs)
        if st.checkbox("Otro:", key=f"otro_check_{idx}"):
            otro_texto = st.text_input("¿Cuál?", key=f"otro_text_{idx}")
            if otro_texto:
                observaciones.append(otro_texto)

        llegada_label = "¿Cómo llegó el equipo?" if st.session_state.tipo_operacion == "Ingreso" else "¿Cómo sale el equipo?"
        st.markdown(f"**{llegada_label}**")
        llegada_formas = ["Caja original", "Caja cartón", "Huacal", "Maletín", "Contenedor"]
        formas = [f for f in llegada_formas if st.checkbox(f, key=f"{f}_{idx}")]

        st.markdown("**Fotos del equipo (mínimo 4):**")
        fotos = st.file_uploader("Seleccionar fotos", accept_multiple_files=True, key=f"fotos_{idx}", type=["png", "jpg", "jpeg"])

        equipo.update({
            "tipo": tipo,
            "serial": serial,
            "accesorios": accesorios,
            "observaciones": observaciones,
            "formas": formas,
            "fotos": fotos
        })

        st.markdown("---")
        if st.button(f"❌ Eliminar equipo {idx + 1}", key=f"eliminar_{idx}"):
            equipos_a_eliminar.append(idx)

# Eliminar equipos marcados
if equipos_a_eliminar:
    for i in sorted(equipos_a_eliminar, reverse=True):
        del st.session_state.equipos[i]
    st.rerun()

# Enviar correo
st.divider()
if st.button("Enviar"):
    if not cliente or not ingeniero or not movimiento:
        st.error("Por favor completa todos los campos generales.")
    else:
        for idx, eq in enumerate(st.session_state.equipos):
            if not eq.get("fotos") or len(eq["fotos"]) < 4:
                st.error(f"El equipo {idx + 1} debe tener al menos 4 fotos.")
                st.stop()

        try:
            from_email = "rianonicolle1101@gmail.com"
            password = "pmfb qjwu rnyc bojy"
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            correo_destino = correos_ingenieros.get(ingeniero)
            correo_fijo = "mejiah5@medtronic.com"

            msg = MIMEMultipart('related')
            msg["From"] = from_email
            msg["To"] = f"{correo_destino}, {correo_fijo}"
            msg["Subject"] = f"{st.session_state.tipo_operacion} ST - Movimiento/Delivery: {movimiento}"

            html = f"""<html><body>
            <p><b>{'Ingreso a Servicio Técnico' if st.session_state.tipo_operacion == 'Ingreso' else 'Salida de Servicio Técnico'}</b></p>
            <p><b>Cliente:</b> {cliente}<br>
            <b>Ingeniero:</b> {ingeniero}<br>
            <b>Movimiento / Delivery:</b> {movimiento}</p>
            <p><b>Equipos registrados:</b></p>
            """

            img_cids = []
            img_index = 0

            for idx, eq in enumerate(st.session_state.equipos):
                obs = ", ".join(eq.get("observaciones", [])) or "Ninguna"
                formas = ", ".join(eq.get("formas", [])) or "No especificada"
                fotos = eq.get("fotos", [])

                html += f"""<p><b>Equipo {idx + 1}:</b><br>
                <b>- Tipo:</b> {eq['tipo']}<br>
                <b>- Serial:</b> {eq['serial']}<br>
                <b>- Accesorios:</b> {eq['accesorios']}<br>
                <b>- Observaciones físicas:</b> {obs}<br>
                <b>- Forma de {'llegada' if st.session_state.tipo_operacion == 'Ingreso' else 'salida'}:</b> {formas}<br>
                <b>- Número de fotos:</b> {len(fotos)}</p>"""

                for foto in fotos:
                    cid = f"image{img_index}"
                    img_index += 1
                    img_cids.append((foto, cid))
                    html += f'<img src="cid:{cid}" style="max-width:400px;"><br>'

            html += """<p style="font-style: italic; color: #555; font-size: 12px; margin-top: 30px; border-top: 1px solid #ccc; padding-top: 10px;">
            Este mensaje ha sido generado automáticamente por el Departamento de Servicio Técnico de <b>Medtronic</b>.</p></body></html>"""

            msg.attach(MIMEText(html, "html"))

            for foto, cid in img_cids:
                img = MIMEImage(foto.read())
                img.add_header("Content-ID", f"<{cid}>")
                img.add_header("Content-Disposition", "inline", filename=foto.name)
                msg.attach(img)

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()

            st.success("Correo enviado correctamente.")
            st.session_state.equipos = []
            st.session_state.cliente = ""
            st.session_state.movimiento = ""

        except Exception as e:
            st.error(f"No se pudo enviar el correo: {e}")










































