"""
BeautyBox Málaga - Formulario de Reserva Público
Página para clientes que quieren solicitar una cita
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================

st.set_page_config(
    page_title="Reservar Cita - BeautyBox Málaga",
    page_icon="💅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================
# ESTILOS CSS
# ============================================

st.markdown("""
<style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stSidebar"] {display: none;}
    
    /* Fondo y contenedor */
    .stApp {
        background: linear-gradient(135deg, #FDF8F7 0%, #FFFFFF 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 480px;
    }
    
    /* Header del formulario */
    .booking-header {
        text-align: center;
        padding: 20px 0;
        margin-bottom: 20px;
    }
    
    .booking-header .logo {
        width: 80px;
        height: 80px;
        border: 2px solid #d4a5a5;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 16px;
        font-size: 0.8rem;
        color: #c48b9f;
        background: white;
    }
    
    .booking-header h1 {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2D2D2D;
        margin: 0 0 4px 0;
    }
    
    .booking-header p {
        font-size: 0.9rem;
        color: #8E8E93;
        margin: 0;
    }
    
    /* Tarjeta del formulario */
    .form-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }
    
    .form-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2D2D2D;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Campos del formulario */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        border-radius: 12px !important;
        border: 1.5px solid #E5E5EA !important;
        padding: 14px !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #d4a5a5 !important;
        box-shadow: 0 0 0 3px rgba(212, 165, 165, 0.1) !important;
    }
    
    /* Botón de envío */
    .stButton > button {
        background: linear-gradient(135deg, #d4a5a5 0%, #c48b9f 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 16px 32px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(196, 139, 159, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(196, 139, 159, 0.5) !important;
    }
    
    /* Mensaje de éxito */
    .success-message {
        background: linear-gradient(135deg, #D4EDDA 0%, #C3E6CB 100%);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin: 20px 0;
    }
    
    .success-message .icon {
        font-size: 3rem;
        margin-bottom: 12px;
    }
    
    .success-message h2 {
        color: #155724;
        font-size: 1.3rem;
        margin: 0 0 8px 0;
    }
    
    .success-message p {
        color: #155724;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* Info de contacto */
    .contact-info {
        background: #F8F9FA;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-top: 24px;
    }
    
    .contact-info h3 {
        font-size: 0.9rem;
        font-weight: 600;
        color: #6C757D;
        margin: 0 0 12px 0;
    }
    
    .contact-info a {
        color: #d4a5a5;
        text-decoration: none;
        font-weight: 500;
    }
    
    .contact-info a:hover {
        text-decoration: underline;
    }
    
    /* Footer */
    .booking-footer {
        text-align: center;
        padding: 20px 0;
        color: #ADB5BD;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONEXIÓN A GOOGLE SHEETS
# ============================================

@st.cache_resource
def get_google_connection():
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

@st.cache_resource
def get_spreadsheet():
    client = get_google_connection()
    try:
        return client.open("BeautyBox_Database")
    except:
        st.error("Error conectando a la base de datos")
        st.stop()

def get_servicios():
    spreadsheet = get_spreadsheet()
    try:
        worksheet = spreadsheet.worksheet('servicios')
        data = worksheet.get_all_records()
        df = pd.DataFrame(data) if data else pd.DataFrame()
        if len(df) > 0:
            df = df[df['activo'] == 1]
        return df
    except:
        return pd.DataFrame()

def insertar_solicitud(nombre, telefono, email, servicio, preferencia, mensaje):
    spreadsheet = get_spreadsheet()
    headers = ['id', 'nombre', 'telefono', 'email', 'servicio_solicitado', 'preferencia_horario', 
               'mensaje', 'estado', 'fecha_solicitud', 'fecha_respuesta', 'notas_admin']
    
    try:
        worksheet = spreadsheet.worksheet('solicitudes')
    except:
        worksheet = spreadsheet.add_worksheet(title='solicitudes', rows=1000, cols=20)
        worksheet.append_row(headers)
    
    data = worksheet.get_all_records()
    new_id = max([row.get('id', 0) for row in data], default=0) + 1
    
    row = [new_id, nombre, telefono, email, servicio, preferencia, mensaje, 'pendiente',
           datetime.now().isoformat(), '', '']
    worksheet.append_row(row)
    return new_id

def enviar_notificacion_email(nombre, telefono, email, servicio, preferencia, mensaje):
    """Enviar notificación por email cuando se recibe una nueva solicitud"""
    try:
        # Configuración del email desde secrets
        try:
            email_sender = st.secrets["email"]["sender"]
            email_password = st.secrets["email"]["app_password"]
            email_recipient = st.secrets["email"]["recipient"]
        except KeyError as e:
            st.error(f"❌ DEBUG: Falta configuración de email: {e}")
            return False

        if not email_password:
            st.error("❌ DEBUG: app_password está vacío")
            return False

        # DEBUG: Mostrar que los secrets se leyeron bien
        st.info(f"📧 DEBUG: Intentando enviar a {email_recipient}...")

        # Crear el mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Nueva Solicitud de Cita - {nombre}'
        msg['From'] = email_sender
        msg['To'] = email_recipient

        # Contenido del email en texto plano
        text_content = f"""
Nueva Solicitud de Cita - BeautyBox Málaga

👤 Cliente: {nombre}
📱 Teléfono: {telefono}
📧 Email: {email if email else 'No proporcionado'}
💅 Servicio: {servicio}
🕐 Preferencia: {preferencia}
💬 Mensaje: {mensaje if mensaje else 'Sin mensaje'}

📅 Fecha de solicitud: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Abre la app para confirmar o rechazar esta solicitud.
        """

        # Contenido del email en HTML
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #FDF8F7; padding: 20px;">
            <div style="max-width: 480px; margin: 0 auto; background: white; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h1 style="color: #c48b9f; margin: 0;">🔔 Nueva Solicitud</h1>
                    <p style="color: #8E8E93; margin: 5px 0;">BeautyBox Málaga</p>
                </div>

                <div style="background: #F8F9FA; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
                    <p style="margin: 8px 0;"><strong>👤 Cliente:</strong> {nombre}</p>
                    <p style="margin: 8px 0;"><strong>📱 Teléfono:</strong> <a href="tel:{telefono}">{telefono}</a></p>
                    <p style="margin: 8px 0;"><strong>📧 Email:</strong> {email if email else 'No proporcionado'}</p>
                </div>

                <div style="background: #F8F9FA; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
                    <p style="margin: 8px 0;"><strong>💅 Servicio:</strong> {servicio}</p>
                    <p style="margin: 8px 0;"><strong>🕐 Preferencia:</strong> {preferencia}</p>
                    <p style="margin: 8px 0;"><strong>💬 Mensaje:</strong> {mensaje if mensaje else 'Sin mensaje'}</p>
                </div>

                <div style="text-align: center; padding: 16px; background: linear-gradient(135deg, #d4a5a5 0%, #c48b9f 100%); border-radius: 12px;">
                    <p style="color: white; margin: 0; font-weight: 600;">📲 Abre la app para confirmar o rechazar</p>
                </div>

                <p style="text-align: center; color: #8E8E93; font-size: 12px; margin-top: 16px;">
                    Solicitud recibida: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        # Enviar el email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_recipient, msg.as_string())

        st.success("✅ DEBUG: Email enviado correctamente!")
        return True
    except Exception as e:
        # Mostrar el error para debugging
        st.error(f"❌ DEBUG Error enviando email: {e}")
        return False

# ============================================
# FORMULARIO
# ============================================

# Header
st.markdown("""
<div class="booking-header">
    <div class="logo">Beauty<br>Box</div>
    <h1>Reservar Cita</h1>
    <p>Centro de Estética • Málaga</p>
</div>
""", unsafe_allow_html=True)

# Estado del formulario
if 'solicitud_enviada' not in st.session_state:
    st.session_state.solicitud_enviada = False

if st.session_state.solicitud_enviada:
    # Mensaje de éxito
    st.markdown("""
    <div class="success-message">
        <div class="icon">✅</div>
        <h2>¡Solicitud Enviada!</h2>
        <p>Te contactaremos pronto para confirmar tu cita.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📝 Nueva Solicitud"):
        st.session_state.solicitud_enviada = False
        st.rerun()
else:
    # Formulario
    servicios = get_servicios()
    
    with st.form("reserva_form"):
        st.markdown('<div class="form-title">📋 Tus Datos</div>', unsafe_allow_html=True)
        
        nombre = st.text_input("Nombre completo *", placeholder="María García")
        telefono = st.text_input("Teléfono *", placeholder="600 123 456")
        email = st.text_input("Email", placeholder="tu@email.com")
        
        st.markdown('<div class="form-title" style="margin-top: 20px;">💅 Servicio</div>', unsafe_allow_html=True)
        
        if len(servicios) > 0:
            servicio_nombres = servicios['nombre'].tolist()
            servicio = st.selectbox("¿Qué servicio te interesa? *", options=servicio_nombres)
        else:
            servicio = st.selectbox("¿Qué servicio te interesa? *", 
                options=["Extensiones de Pestañas", "Lifting de Pestañas", "Laminado de Cejas", 
                        "Micropigmentación", "Manicura", "Pedicura", "Otro"])
        
        preferencia = st.selectbox("Preferencia de horario *",
            options=["Mañana (9:00 - 13:00)", "Tarde (16:00 - 20:00)", "Flexible"])
        
        mensaje = st.text_area("Mensaje (opcional)", 
            placeholder="¿Alguna preferencia o comentario?",
            height=100)
        
        submitted = st.form_submit_button("📩 Enviar Solicitud")
        
        if submitted:
            if not nombre or not telefono:
                st.error("Por favor completa los campos obligatorios (*)")
            else:
                insertar_solicitud(nombre, telefono, email, servicio, preferencia, mensaje)
                # Enviar notificación por email
                enviar_notificacion_email(nombre, telefono, email, servicio, preferencia, mensaje)
                st.session_state.solicitud_enviada = True
                st.rerun()

# Info de contacto
st.markdown("""
<div class="contact-info">
    <h3>¿Prefieres contactarnos directamente?</h3>
    <p>📱 WhatsApp: <a href="https://wa.me/34XXXXXXXXX">+34 XXX XXX XXX</a></p>
    <p>📍 Málaga Centro</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="booking-footer">
    <p>© BeautyBox Málaga</p>
    <p>Lashes & Brows</p>
</div>
""", unsafe_allow_html=True)
