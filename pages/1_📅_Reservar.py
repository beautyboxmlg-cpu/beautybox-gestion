"""
BeautyBox Málaga - Formulario Público de Reservas
Esta página es para que los clientes soliciten citas
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================

st.set_page_config(
    page_title="Reservar Cita - BeautyBox Málaga",
    page_icon="💅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Ocultar sidebar y menú
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main-header {
        font-size: 2.5rem;
        color: #d4a5a5;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    .info-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .beautybox-form {
        background: linear-gradient(135deg, #f9f7f5 0%, #fff 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONEXIÓN A GOOGLE SHEETS
# ============================================

@st.cache_resource
def get_google_connection():
    """Conectar a Google Sheets"""
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
        return None

def get_servicios_disponibles():
    """Obtener lista de servicios para el formulario"""
    try:
        client = get_google_connection()
        if not client:
            return []
        
        spreadsheet = client.open("BeautyBox_Database")
        worksheet = spreadsheet.worksheet('servicios')
        data = worksheet.get_all_records()
        
        # Filtrar solo servicios activos
        servicios = [row for row in data if row.get('activo') == 1]
        
        # Formatear para mostrar
        opciones = []
        for s in servicios:
            precio = s.get('precio', 0)
            nombre = s.get('nombre', '')
            opciones.append(f"{nombre} - €{precio}")
        
        return opciones
    except:
        # Si hay error, devolver lista predefinida
        return [
            "Extensiones de pestañas clásicas - €50",
            "Extensiones de Pestañas 2D - €65",
            "Extensiones de Pestañas Híbridas - €55",
            "Extensiones de Pestañas 3D - €80",
            "Volumen Ruso - €80",
            "Lifting de Pestañas con tinte - €50",
            "Microblading o Nanoblading - €200",
            "Micropigmentación de Cejas - €200",
            "Laminado de Cejas - €45",
            "Diseño de Cejas con Henna - €35",
            "Depilación con hilo - €10",
            "Micropigmentación de Labios - €250",
            "Micropigmentación de Ojos - €220",
            "Manicura Rusa con Nivelación - €25"
        ]

def guardar_solicitud(nombre, telefono, email, servicio, preferencia, mensaje):
    """Guardar solicitud en Google Sheets"""
    try:
        client = get_google_connection()
        if not client:
            return False
        
        spreadsheet = client.open("BeautyBox_Database")
        
        # Obtener o crear hoja de solicitudes
        try:
            worksheet = spreadsheet.worksheet('solicitudes')
        except:
            headers = ['id', 'nombre', 'telefono', 'email', 'servicio_solicitado', 
                      'preferencia_horario', 'mensaje', 'estado', 'fecha_solicitud', 
                      'fecha_respuesta', 'notas_admin']
            worksheet = spreadsheet.add_worksheet(title='solicitudes', rows=1000, cols=20)
            worksheet.append_row(headers)
        
        # Obtener siguiente ID
        data = worksheet.get_all_records()
        next_id = max([row.get('id', 0) for row in data], default=0) + 1
        
        # Guardar solicitud
        row = [
            next_id,
            nombre,
            telefono,
            email,
            servicio,
            preferencia,
            mensaje,
            'pendiente',
            datetime.now().isoformat(),
            '',
            ''
        ]
        worksheet.append_row(row)
        
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# ============================================
# INTERFAZ DEL FORMULARIO
# ============================================

# Logo y header
st.markdown("<h1 class='main-header'>💅 BeautyBox Málaga</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Solicita tu cita online</p>", unsafe_allow_html=True)

# Mensaje informativo
st.markdown("""
<div class='info-box'>
    ⚠️ <strong>Importante:</strong> Esto es una <strong>solicitud de cita</strong>, no una confirmación automática. 
    Te contactaremos por WhatsApp o teléfono para confirmar fecha y hora disponible.
</div>
""", unsafe_allow_html=True)

# Verificar si ya se envió
if 'solicitud_enviada' not in st.session_state:
    st.session_state.solicitud_enviada = False

if st.session_state.solicitud_enviada:
    st.markdown("""
    <div class='success-box'>
        <h2>✅ ¡Solicitud Recibida!</h2>
        <p>Gracias por tu interés en BeautyBox Málaga.</p>
        <p>Te contactaremos pronto por WhatsApp o teléfono para confirmar tu cita.</p>
        <p><strong>📱 +34 642 84 19 32</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📝 Hacer otra solicitud"):
        st.session_state.solicitud_enviada = False
        st.rerun()
    
    # Links de contacto
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("💬 WhatsApp Directo", 
                      "https://wa.me/34642841932?text=Hola%20BeautyBox!%20Acabo%20de%20enviar%20una%20solicitud%20de%20cita.",
                      use_container_width=True)
    with col2:
        st.link_button("🌐 Volver a la Web", 
                      "https://beautyboxcentromalaga.com",
                      use_container_width=True)

else:
    # Formulario de solicitud
    with st.form("solicitud_cita"):
        st.subheader("📋 Tus Datos")
        
        nombre = st.text_input("Nombre completo *", placeholder="María García")
        
        col1, col2 = st.columns(2)
        with col1:
            telefono = st.text_input("Teléfono/WhatsApp *", placeholder="+34 612 345 678")
        with col2:
            email = st.text_input("Email (opcional)", placeholder="tu@email.com")
        
        st.markdown("---")
        st.subheader("💅 Servicio Deseado")
        
        servicios = get_servicios_disponibles()
        servicio = st.selectbox("¿Qué servicio te interesa? *", servicios)
        
        st.markdown("---")
        st.subheader("📅 Preferencia de Horario")
        
        preferencia = st.radio(
            "¿Cuándo prefieres tu cita?",
            [
                "🌅 Mañanas (10:00 - 14:00)",
                "🌆 Tardes (16:00 - 20:00)",
                "📅 Día específico (indicar en mensaje)",
                "🤷 Flexible - cualquier horario disponible"
            ]
        )
        
        mensaje = st.text_area(
            "Mensaje adicional (opcional)",
            placeholder="Ej: Prefiero los martes, es mi primera vez con extensiones, tengo alguna alergia...",
            height=100
        )
        
        st.markdown("---")
        
        # Botón de envío
        submitted = st.form_submit_button("📤 Enviar Solicitud", type="primary", use_container_width=True)
        
        if submitted:
            # Validaciones
            if not nombre:
                st.error("Por favor ingresa tu nombre")
            elif not telefono:
                st.error("Por favor ingresa tu teléfono")
            elif len(telefono) < 9:
                st.error("Por favor ingresa un teléfono válido")
            else:
                # Guardar solicitud
                with st.spinner("Enviando solicitud..."):
                    exito = guardar_solicitud(nombre, telefono, email, servicio, preferencia, mensaje)
                
                if exito:
                    st.session_state.solicitud_enviada = True
                    st.rerun()
                else:
                    st.error("Hubo un error. Por favor contacta directamente por WhatsApp.")
                    st.link_button("💬 Contactar por WhatsApp", 
                                  "https://wa.me/34642841932",
                                  use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>📍 Av. del Arroyo de los Ángeles, 5 - Málaga</p>
    <p>📱 +34 642 84 19 32 | 📧 beautyboxmlg@gmail.com</p>
    <p>© 2025 BeautyBox Málaga</p>
</div>
""", unsafe_allow_html=True)
