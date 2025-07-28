import streamlit as st
from PIL import Image
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
import os

# Datos iniciales
correos_ingenieros = {
    "Nicolle Riaño": "nicolle.n.riano@medtronic.com"
}

st.set_page_config(page_title="Registro de Equipos", layout="wide")

st.markdown("""
    <style>
        .encabezado {
            background-color: #003A70;
            color: white;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }
        .encabezado h1 {
            margin: 0;
            font-size: 26px;
        }
        .encabezado p {
            margin: 0;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="encabezado"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Medtronic_logo.svg/2560px-Medtronic_logo.svg.png" width="200"/><h1>Registro de Equipos</h1><p>Información confidencial - Uso exclusivo de Medtronic</p></div>', unsafe_allow_html=True)

st.sidebar.title("Menú")
st.sidebar.write("Selecciona la opción deseada")

# Inicializar variables de sesión
if "equipos" not in st.session_state:
    st.session_state.equipos = []

# Información general
st.subheader("Información General")
st.session_state.tipo_operacion = st.selectbox("Tipo de operación:", ["Ingreso", "Salida"], key="tipo_operacion")
cliente = st.text_input("Cliente:")
ingeniero = st.selectbox("Ingeniero responsable:", list(correos_ingenieros.keys()))
correo_destino = correos_ingenieros[ingeniero]

# Registro de equipos
st.subheader("Equipos")

if st.button("➕ Agregar equipo"):
    st.session_state.equipos.append({
        "tipo": "",
        "serial": "",
        "accesorios": "",
        "observaciones": [],
        "formas": [],
        "fotos": []
    })

# Lista de índices a eliminar
equipos_a_eliminar = []

# Mostrar cada equipo
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

# Eliminar equipos después de recorrer
for idx in sorted(equipos_a_eliminar, reverse=True):
    del st.session_state.equipos[idx]

# Envío del correo (ejemplo)
if st.button("📤 Enviar información"):
    st.success("Correo enviado exitosamente (simulado).")









































