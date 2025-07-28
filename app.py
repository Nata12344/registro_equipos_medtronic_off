# streamlit_app.py
import streamlit as st
from PIL import Image
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
import io

st.set_page_config(page_title="Registro de equipos - Medtronic", layout="centered")
st.title("Registro de equipos - Medtronic")

st.sidebar.title("Configuración")
tipo_operacion = st.sidebar.radio("Tipo de operación", ["Ingreso", "Salida"])

cliente = st.text_input("Cliente")
ingeniero = st.selectbox("Ingeniero", ["Nicolle Riaño"])
movimiento = st.text_input("Movimiento / Delivery")

num_equipos = st.number_input("Cantidad de equipos", min_value=1, max_value=10, value=1, step=1)

# Entrada de datos por equipo
info_equipos = []
st.subheader("Equipos")
for i in range(num_equipos):
    st.markdown(f"### Equipo {i+1}")
    tipo = st.selectbox(f"Tipo de equipo {i+1}", ["WEM", "ForceTriad", "FX", "PB840", "PB980", "BIS VISTA", "CONSOLA DE CAMARA"], key=f"tipo_{i}")
    serial = st.text_input(f"Serial {i+1}", key=f"serial_{i}")
    accesorios = st.text_input(f"Accesorios {i+1}", key=f"accesorios_{i}")
    obs = st.multiselect(f"Observaciones físicas {i+1}", ["Carcasa rayada", "Golpes visibles", "Pantalla rayada", "Pieza rotos", "Cable dañado", "otro"], key=f"obs_{i}")
    obs_otro = ""
    if "otro" in obs:
        obs_otro = st.text_input(f"Observación adicional {i+1}", key=f"otro_{i}")
    llegada = st.multiselect(f"{'Llegada' if tipo_operacion == 'Ingreso' else 'Salida'} del equipo {i+1}", ["Caja original", "Caja cartón", "Huacal", "Maletín", "Contenedor"], key=f"llegada_{i}")
    fotos = st.file_uploader(f"Fotos del equipo {i+1} (mínimo 4)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key=f"fotos_{i}")

    info_equipos.append({
        "tipo": tipo,
        "serial": serial,
        "accesorios": accesorios,
        "observaciones": obs,
        "otro": obs_otro,
        "llegada": llegada,
        "fotos": fotos
    })

if st.button("Enviar informe"):
    try:
        for i, eq in enumerate(info_equipos):
            if len(eq["fotos"]) < 4:
                st.error(f"El equipo {i+1} debe tener al menos 4 fotos.")
                st.stop()

        from_email = "rianonicolle1101@gmail.com"
        password = "pmfb qjwu rnyc bojy"
        to_email = "nicolle.n.riano@medtronic.com, mejiah5@medtronic.com"

        msg = MIMEMultipart('related')
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = f"{tipo_operacion} ST - Movimiento/Delivery: {movimiento}"

        html = f"""
        <html><body>
        <p><b>{'Ingreso a Servicio Técnico' if tipo_operacion == 'Ingreso' else 'Salida de Servicio Técnico'}</b></p>
        <p><b>Cliente:</b> {cliente}<br>
        <b>Ingeniero:</b> {ingeniero}<br>
        <b>Movimiento / Delivery:</b> {movimiento}</p>
        <p><b>Equipos registrados:</b></p>
        """

        imagenes = []
        cid_counter = 0
        for i, eq in enumerate(info_equipos):
            obs_text = ", ".join(eq["observaciones"])
            if eq["otro"]:
                obs_text += f", {eq['otro']}"

            llegada_text = ", ".join(eq["llegada"])

            html += f"""
            <p><b>Equipo {i+1}:</b><br>
            <b>- Tipo:</b> {eq['tipo']}<br>
            <b>- Serial:</b> {eq['serial']}<br>
            <b>- Accesorios:</b> {eq['accesorios']}<br>
            <b>- Observaciones físicas:</b> {obs_text}<br>
            <b>- Forma de {'llegada' if tipo_operacion == 'Ingreso' else 'salida'}:</b> {llegada_text}<br>
            <b>- Número de fotos:</b> {len(eq['fotos'])}</p>
            """
            for foto in eq['fotos']:
                cid = f"image{cid_counter}"
                cid_counter += 1
                html += f'<img src="cid:{cid}" style="max-width:400px;"><br>'

                img_bytes = foto.read()
                img = MIMEImage(img_bytes)
                img.add_header('Content-ID', f'<{cid}>')
                img.add_header('Content-Disposition', 'inline', filename=foto.name)
                imagenes.append(img)

            html += "<br>"

        html += """
         <p style="font-style: italic; color: #555; font-size: 12px; margin-top: 30px; border-top: 1px solid #ccc; padding-top: 10px;">
         Este mensaje ha sido generado automáticamente por el Departamento de Servicio Técnico de <b>Medtronic</b>.
         </p></body></html>
        """

        msg.attach(MIMEText(html, 'html'))
        for img in imagenes:
            msg.attach(img)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()

        st.success("Correo enviado correctamente.")
    except Exception as e:
        st.error(f"No se pudo enviar el correo: {e}")


