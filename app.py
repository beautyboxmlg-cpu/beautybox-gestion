"""
BeautyBox Málaga - Sistema de Gestión
Versión 4.0 - Diseño Móvil Moderno con Google Sheets
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================

st.set_page_config(
    page_title="BeautyBox - Gestión",
    page_icon="💅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================
# ESTILOS CSS - DISEÑO MÓVIL iOS
# ============================================

st.markdown("""
<style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Ocultar sidebar en móvil */
    [data-testid="stSidebar"] {display: none;}
    
    /* Fondo general */
    .stApp {
        background-color: #F2F2F7;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 100px;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
        max-width: 100%;
        width: 100%;
    }
    
    @media (min-width: 576px) {
        .main .block-container {
            max-width: 540px;
            margin: 0 auto;
        }
    }
    
    /* Header estilo iOS */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 16px 0;
        margin-bottom: 16px;
    }
    
    .app-header img {
        width: 45px;
        height: 45px;
        border-radius: 12px;
        object-fit: contain;
    }
    
    .app-header-text h1 {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1C1C1E;
        margin: 0;
        line-height: 1.2;
    }
    
    .app-header-text p {
        font-size: 0.875rem;
        color: #8E8E93;
        margin: 0;
    }
    
    /* Banner de bienvenida */
    .welcome-banner {
        background: linear-gradient(135deg, #70C3E8 0%, #5BA8D0 100%);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(112, 195, 232, 0.3);
    }
    
    .welcome-banner p {
        color: white;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0;
        line-height: 1.5;
    }
    
    /* Tarjetas de métricas */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .metric-card .label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #8E8E93;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #1C1C1E;
    }
    
    /* Sección de acciones rápidas */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1C1C1E;
        margin-bottom: 12px;
        padding-left: 4px;
    }
    
    .action-card {
        background: white;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Botón principal estilo iOS */
    .btn-primary {
        background: #007AFF;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 16px 24px;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
        transition: all 0.2s ease;
    }
    
    .btn-primary:hover {
        background: #0066CC;
        transform: translateY(-1px);
    }
    
    .btn-primary:active {
        transform: translateY(0);
    }
    
    /* Botón secundario */
    .btn-secondary {
        background: #E5E5EA;
        color: #1C1C1E;
        border: none;
        border-radius: 12px;
        padding: 14px 20px;
        font-size: 0.95rem;
        font-weight: 600;
        width: 100%;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .btn-secondary:hover {
        background: #D1D1D6;
    }
    
    /* Navegación inferior fija */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid #E5E5EA;
        padding: 8px 0 20px 0;
        z-index: 1000;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .bottom-nav-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        max-width: 500px;
        margin: 0 auto;
    }
    
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 8px 12px;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .nav-item .nav-icon {
        font-size: 1.5rem;
        margin-bottom: 4px;
    }
    
    .nav-item .nav-label {
        font-size: 0.65rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .nav-item.active .nav-icon,
    .nav-item.active .nav-label {
        color: #007AFF;
    }
    
    .nav-item.inactive .nav-icon,
    .nav-item.inactive .nav-label {
        color: #8E8E93;
    }
    
    /* Lista de items estilo iOS */
    .list-card {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
    }
    
    .list-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px;
        border-bottom: 1px solid #F2F2F7;
    }
    
    .list-item:last-child {
        border-bottom: none;
    }
    
    .list-item-content {
        flex: 1;
    }
    
    .list-item-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1C1C1E;
        margin-bottom: 4px;
    }
    
    .list-item-subtitle {
        font-size: 0.85rem;
        color: #8E8E93;
    }
    
    .list-item-value {
        font-size: 1rem;
        font-weight: 600;
        color: #1C1C1E;
    }
    
    /* Tarjeta de solicitud pendiente */
    .request-card {
        background: white;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #FF9500;
    }
    
    .request-card.confirmed {
        border-left-color: #34C759;
    }
    
    .request-card .client-name {
        font-size: 1rem;
        font-weight: 700;
        color: #1C1C1E;
        margin-bottom: 8px;
    }
    
    .request-card .client-info {
        font-size: 0.85rem;
        color: #8E8E93;
        margin-bottom: 4px;
    }
    
    /* Badge de contador */
    .badge {
        background: #FF3B30;
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 10px;
        margin-left: 6px;
    }
    
    /* Formularios estilo iOS */
    .form-group {
        margin-bottom: 16px;
    }
    
    .form-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #8E8E93;
        margin-bottom: 8px;
        display: block;
    }
    
    /* Ocultar elementos default de Streamlit metric */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Ajustes para inputs de Streamlit */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        border-radius: 12px !important;
        border: 1px solid #E5E5EA !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    
    /* Selectbox - centrar texto verticalmente */
    .stSelectbox > div > div {
        border-radius: 12px !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        font-size: 14px !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        min-height: 48px !important;
        padding: 0 12px !important;
        display: flex !important;
        align-items: center !important;
    }
    
    /* Centrar el texto dentro del contenedor */
    .stSelectbox [data-baseweb="select"] > div > div {
        display: flex !important;
        align-items: center !important;
        height: 100% !important;
        line-height: normal !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div > div > div {
        display: flex !important;
        align-items: center !important;
        line-height: 1.4 !important;
    }
    
    /* Asegurar que el valor seleccionado esté centrado */
    [data-baseweb="select"] > div:first-child {
        display: flex !important;
        align-items: center !important;
    }
    
    [data-baseweb="select"] > div:first-child > div {
        display: flex !important;
        align-items: center !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Radio buttons horizontales */
    .stRadio > div {
        flex-direction: row !important;
        gap: 16px !important;
        flex-wrap: wrap !important;
    }
    
    .stRadio label {
        font-size: 14px !important;
    }
    
    .stButton > button {
        background: #007AFF !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: #0066CC !important;
    }
    
    /* Tabs estilo iOS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #E5E5EA;
        border-radius: 12px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 16px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Alerta de pendientes */
    .pending-alert {
        background: linear-gradient(135deg, #FF9500 0%, #FF7A00 100%);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .pending-alert .alert-icon {
        font-size: 1.5rem;
    }
    
    .pending-alert .alert-text {
        color: white;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Botones de navegación inferior */
    div[data-testid="stHorizontalBlock"]:last-of-type button {
        background: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 8px 4px !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        color: #8E8E93 !important;
        box-shadow: none !important;
        white-space: pre-line !important;
        line-height: 1.3 !important;
    }
    
    div[data-testid="stHorizontalBlock"]:last-of-type button:hover {
        background: #F2F2F7 !important;
        color: #007AFF !important;
    }
    
    div[data-testid="stHorizontalBlock"]:last-of-type button:active {
        color: #007AFF !important;
    }
    
    /* DataFrames mejorados */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
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
        st.error(f"Error conectando a Google Sheets: {e}")
        st.info("Asegúrate de configurar las credenciales en Streamlit Secrets")
        st.stop()

@st.cache_resource
def get_spreadsheet():
    """Obtener el spreadsheet de BeautyBox"""
    client = get_google_connection()
    try:
        spreadsheet = client.open("BeautyBox_Database")
        return spreadsheet
    except gspread.SpreadsheetNotFound:
        st.error("No se encontró el spreadsheet 'BeautyBox_Database'")
        st.stop()

def get_or_create_worksheet(spreadsheet, name, headers):
    """Obtener o crear una hoja con los headers especificados"""
    try:
        worksheet = spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=name, rows=1000, cols=20)
        worksheet.append_row(headers)
    return worksheet

# ============================================
# FUNCIONES DE DATOS
# ============================================

def get_categorias():
    spreadsheet = get_spreadsheet()
    headers = ['id', 'nombre', 'descripcion', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'categorias', headers)
    data = worksheet.get_all_records()
    if not data:
        categorias_default = [
            [1, 'Pestañas', 'Extensiones y tratamientos de pestañas', datetime.now().isoformat()],
            [2, 'Cejas', 'Diseño, laminado y micropigmentación', datetime.now().isoformat()],
            [3, 'Uñas', 'Manicura y pedicura', datetime.now().isoformat()],
            [4, 'Otros', 'Otros servicios', datetime.now().isoformat()]
        ]
        for cat in categorias_default:
            worksheet.append_row(cat)
        data = worksheet.get_all_records()
    return pd.DataFrame(data)

def get_servicios():
    spreadsheet = get_spreadsheet()
    headers = ['id', 'nombre', 'categoria_id', 'precio', 'duracion_minutos', 'costo_insumos', 'activo', 'descripcion', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'servicios', headers)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=headers)
    if len(df) > 0:
        df = df[df['activo'] == 1]
        categorias = get_categorias()
        df = df.merge(categorias[['id', 'nombre']], left_on='categoria_id', right_on='id', 
                     how='left', suffixes=('', '_cat'))
        df = df.rename(columns={'nombre_cat': 'categoria_nombre'})
        if 'id_cat' in df.columns:
            df = df.drop(columns=['id_cat'])
    return df

def get_clientes():
    spreadsheet = get_spreadsheet()
    headers = ['id', 'nombre', 'telefono', 'email', 'fecha_primera_visita', 'canal_adquisicion', 'notas', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'clientes', headers)
    data = worksheet.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(columns=headers)

def get_citas(fecha_inicio=None, fecha_fin=None):
    spreadsheet = get_spreadsheet()
    headers = ['id', 'fecha', 'hora', 'cliente_id', 'servicio_id', 'precio_cobrado', 'propina', 'canal_origen', 'metodo_pago', 'notas', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'citas', headers)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=headers)
    
    if len(df) > 0:
        if fecha_inicio and fecha_fin:
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df[(df['fecha'] >= pd.to_datetime(fecha_inicio)) & 
                   (df['fecha'] <= pd.to_datetime(fecha_fin))]
        
        clientes = get_clientes()
        servicios = get_servicios()
        categorias = get_categorias()
        
        if len(clientes) > 0:
            df = df.merge(clientes[['id', 'nombre']], left_on='cliente_id', right_on='id', 
                         how='left', suffixes=('', '_cliente'))
            df = df.rename(columns={'nombre': 'cliente_nombre'})
            if 'id_cliente' in df.columns:
                df = df.drop(columns=['id_cliente'])
        
        if len(servicios) > 0:
            servicios_info = servicios[['id', 'nombre', 'categoria_id', 'costo_insumos']].copy()
            df = df.merge(servicios_info, left_on='servicio_id', right_on='id', 
                         how='left', suffixes=('', '_servicio'))
            df = df.rename(columns={'nombre': 'servicio_nombre'})
            if 'id_servicio' in df.columns:
                df = df.drop(columns=['id_servicio'])
            
            if len(categorias) > 0:
                df = df.merge(categorias[['id', 'nombre']], left_on='categoria_id', right_on='id',
                             how='left', suffixes=('', '_cat'))
                df = df.rename(columns={'nombre': 'categoria_nombre'})
                if 'id_cat' in df.columns:
                    df = df.drop(columns=['id_cat'])
        
        df = df.sort_values('fecha', ascending=False)
    return df

def get_gastos_fijos():
    spreadsheet = get_spreadsheet()
    headers = ['id', 'concepto', 'monto', 'frecuencia', 'activo', 'notas', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'gastos_fijos', headers)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=headers)
    if len(df) > 0:
        df = df[df['activo'] == 1]
    return df

def get_gastos_variables(fecha_inicio=None, fecha_fin=None):
    spreadsheet = get_spreadsheet()
    headers = ['id', 'fecha', 'concepto', 'monto', 'categoria', 'notas', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'gastos_variables', headers)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=headers)
    if len(df) > 0 and fecha_inicio and fecha_fin:
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df[(df['fecha'] >= pd.to_datetime(fecha_inicio)) & 
               (df['fecha'] <= pd.to_datetime(fecha_fin))]
    return df

def get_solicitudes():
    spreadsheet = get_spreadsheet()
    headers = ['id', 'nombre', 'telefono', 'email', 'servicio_solicitado', 'preferencia_horario', 
               'mensaje', 'estado', 'fecha_solicitud', 'fecha_respuesta', 'notas_admin']
    worksheet = get_or_create_worksheet(spreadsheet, 'solicitudes', headers)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=headers)
    if len(df) > 0:
        df = df.sort_values('fecha_solicitud', ascending=False)
    return df

# ============================================
# FUNCIONES DE INSERCIÓN
# ============================================

def get_next_id(worksheet):
    data = worksheet.get_all_records()
    if not data:
        return 1
    ids = [row.get('id', 0) for row in data]
    return max(ids) + 1 if ids else 1

def insertar_servicio(nombre, categoria_id, precio, duracion, costo_insumos, descripcion):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('servicios')
    new_id = get_next_id(worksheet)
    row = [new_id, nombre, categoria_id, precio, duracion, costo_insumos, 1, descripcion, datetime.now().isoformat()]
    worksheet.append_row(row)
    st.cache_resource.clear()

def insertar_cliente(nombre, telefono, email, canal, notas):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('clientes')
    new_id = get_next_id(worksheet)
    row = [new_id, nombre, telefono, email, datetime.now().strftime('%Y-%m-%d'), canal, notas, datetime.now().isoformat()]
    worksheet.append_row(row)
    st.cache_resource.clear()
    return new_id

def insertar_cita(fecha, hora, cliente_id, servicio_id, precio, propina, canal, metodo_pago, notas):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('citas')
    new_id = get_next_id(worksheet)
    row = [new_id, str(fecha), str(hora), cliente_id, servicio_id, precio, propina, canal, metodo_pago, notas, datetime.now().isoformat()]
    worksheet.append_row(row)
    st.cache_resource.clear()

def insertar_gasto_fijo(concepto, monto, frecuencia, notas):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('gastos_fijos')
    new_id = get_next_id(worksheet)
    row = [new_id, concepto, monto, frecuencia, 1, notas, datetime.now().isoformat()]
    worksheet.append_row(row)
    st.cache_resource.clear()

def insertar_gasto_variable(fecha, concepto, monto, categoria, notas):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('gastos_variables')
    new_id = get_next_id(worksheet)
    row = [new_id, str(fecha), concepto, monto, categoria, notas, datetime.now().isoformat()]
    worksheet.append_row(row)
    st.cache_resource.clear()

# ============================================
# FUNCIONES DE ACTUALIZACIÓN
# ============================================

def find_row_by_id(worksheet, id_value):
    data = worksheet.get_all_records()
    for i, row in enumerate(data):
        if row.get('id') == id_value:
            return i + 2
    return None

def actualizar_servicio(servicio_id, nombre, categoria_id, precio, duracion, costo_insumos, descripcion):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('servicios')
    row_num = find_row_by_id(worksheet, servicio_id)
    if row_num:
        worksheet.update(f'B{row_num}:H{row_num}', [[nombre, categoria_id, precio, duracion, costo_insumos, 1, descripcion]])
    st.cache_resource.clear()

def eliminar_servicio(servicio_id):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('servicios')
    row_num = find_row_by_id(worksheet, servicio_id)
    if row_num:
        worksheet.update(f'G{row_num}', [[0]])
    st.cache_resource.clear()

def actualizar_solicitud(solicitud_id, estado, notas_admin):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('solicitudes')
    row_num = find_row_by_id(worksheet, solicitud_id)
    if row_num:
        worksheet.update(f'H{row_num}:K{row_num}', [[estado, datetime.now().isoformat(), notas_admin]])
    st.cache_resource.clear()

def eliminar_cliente(cliente_id):
    citas = get_citas()
    if len(citas) > 0 and cliente_id in citas['cliente_id'].values:
        return False, len(citas[citas['cliente_id'] == cliente_id])
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('clientes')
    row_num = find_row_by_id(worksheet, cliente_id)
    if row_num:
        worksheet.delete_rows(row_num)
    st.cache_resource.clear()
    return True, 0

def eliminar_cita(cita_id):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('citas')
    row_num = find_row_by_id(worksheet, cita_id)
    if row_num:
        worksheet.delete_rows(row_num)
    st.cache_resource.clear()

# ============================================
# ESTADO DE NAVEGACIÓN
# ============================================

if 'pagina' not in st.session_state:
    st.session_state.pagina = 'dashboard'

# ============================================
# OBTENER DATOS GLOBALES
# ============================================

# Filtros de fecha (usando el mes actual)
fecha_inicio = datetime.now().replace(day=1).date()
fecha_fin = datetime.now().date()

# Contar solicitudes pendientes
solicitudes = get_solicitudes()
pendientes = len(solicitudes[solicitudes['estado'] == 'pendiente']) if len(solicitudes) > 0 else 0

# ============================================
# NAVEGACIÓN INFERIOR (FUNCIONAL)
# ============================================

# CSS adicional para los botones de navegación
st.markdown("""
<style>
    /* Contenedor de navegación inferior */
    .nav-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid #E5E5EA;
        padding: 8px 0 20px 0;
        z-index: 1000;
    }
    
    /* Estilo para botones de navegación */
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div > div > div > div > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 8px 4px !important;
        min-height: 60px !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div > div > div > div > button:hover {
        background: #F2F2F7 !important;
    }
    
    /* Ocultar el borde del botón */
    .nav-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
    }
    
    .nav-btn .icon {
        font-size: 1.4rem;
    }
    
    .nav-btn .label {
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .nav-btn.active .label {
        color: #007AFF;
    }
    
    .nav-btn.inactive .label {
        color: #8E8E93;
    }
</style>
""", unsafe_allow_html=True)

def cambiar_pagina(nueva_pagina):
    st.session_state.pagina = nueva_pagina

# ============================================
# HEADER
# ============================================

pagina_actual = st.session_state.pagina

# Títulos por página
titulos = {
    'dashboard': 'Dashboard',
    'solicitudes': 'Solicitudes',
    'clientes': 'Clientes', 
    'servicios': 'Servicios',
    'registrar': 'Registrar Cita',
    'gastos': 'Gastos',
    'config': 'Configuración'
}

st.markdown(f"""
<div class="app-header">
    <div style="width: 45px; height: 45px; border: 2px solid #d4a5a5; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; color: #c48b9f; text-align: center; line-height: 1.1;">
        Beauty<br>Box
    </div>
    <div class="app-header-text">
        <h1>{titulos.get(pagina_actual, 'Dashboard')}</h1>
        <p>BeautyBox</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# CONTENIDO PRINCIPAL
# ============================================

pagina = st.session_state.pagina

# ---------- DASHBOARD ----------
if pagina == 'dashboard':
    # Alerta de solicitudes pendientes
    if pendientes > 0:
        st.markdown(f"""
        <div class="pending-alert">
            <span class="alert-icon">📋</span>
            <span class="alert-text"><strong>{pendientes}</strong> solicitud(es) pendiente(s)</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Obtener datos
    citas = get_citas(fecha_inicio, fecha_fin)
    
    if len(citas) == 0:
        # Banner de bienvenida
        st.markdown("""
        <div class="welcome-banner">
            <p>¡Bienvenida! No hay datos registrados aún.<br>Ve a 'Registrar Cita' para comenzar.</p>
        </div>
        """, unsafe_allow_html=True)
        
        ingresos = 0
        num_citas = 0
        ticket_prom = 0
        clientes_unicos = 0
    else:
        ingresos = citas['precio_cobrado'].sum() + citas['propina'].sum()
        num_citas = len(citas)
        ticket_prom = citas['precio_cobrado'].mean()
        clientes_unicos = citas['cliente_id'].nunique()
    
    # Grid de métricas
    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <span class="label">Ingresos Totales</span>
            <span class="value">€{ingresos:,.0f}</span>
        </div>
        <div class="metric-card">
            <span class="label">Citas</span>
            <span class="value">{num_citas}</span>
        </div>
        <div class="metric-card">
            <span class="label">Ticket Promedio</span>
            <span class="value">€{ticket_prom:,.0f}</span>
        </div>
        <div class="metric-card">
            <span class="label">Clientes Únicos</span>
            <span class="value">{clientes_unicos}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Acciones rápidas
    st.markdown('<h2 class="section-title">Acciones Rápidas</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Registrar Cita", use_container_width=True, type="primary", key="btn_registrar_cita"):
            st.session_state.pagina = 'registrar'
            st.rerun()
    with col2:
        if st.button("💰 Agregar Gasto", use_container_width=True, key="btn_agregar_gasto"):
            st.session_state.pagina = 'gastos'
            st.rerun()
    
    # Gráfico si hay datos
    if len(citas) > 0:
        st.markdown("---")
        st.markdown('<h2 class="section-title">Ingresos del Mes</h2>', unsafe_allow_html=True)
        
        citas['fecha'] = pd.to_datetime(citas['fecha'])
        ingresos_diarios = citas.groupby('fecha')['precio_cobrado'].sum().reset_index()
        
        fig = px.area(ingresos_diarios, x='fecha', y='precio_cobrado',
                     labels={'fecha': '', 'precio_cobrado': '€'})
        fig.update_traces(fill='tozeroy', line_color='#007AFF', fillcolor='rgba(0, 122, 255, 0.1)')
        fig.update_layout(
            height=200,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#F2F2F7'),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------- REGISTRAR CITA ----------
elif pagina == 'registrar':
    # Botón volver
    if st.button("← Volver al Dashboard", key="volver_registrar"):
        st.session_state.pagina = 'dashboard'
        st.rerun()
    
    st.markdown('<h2 class="section-title">📝 Registrar Cita</h2>', unsafe_allow_html=True)
    
    servicios = get_servicios()
    clientes = get_clientes()
    
    if len(servicios) == 0:
        st.warning("⚠️ Primero crea al menos un servicio")
    else:
        with st.form("form_cita"):
            fecha_cita = st.date_input("📅 Fecha", datetime.now())
            hora_cita = st.time_input("🕐 Hora", datetime.now().time())
            
            # Servicio
            servicio_opciones = servicios[['id', 'nombre', 'precio', 'categoria_nombre']].copy()
            servicio_opciones['display'] = servicio_opciones.apply(
                lambda x: f"{x['nombre']} - €{x['precio']}", axis=1
            )
            servicio_sel = st.selectbox("💅 Servicio", options=servicio_opciones['id'].tolist(),
                format_func=lambda x: servicio_opciones[servicio_opciones['id']==x]['display'].values[0])
            
            precio_servicio = servicios[servicios['id']==servicio_sel]['precio'].values[0]
            precio_cobrado = st.number_input("💶 Precio (€)", value=float(precio_servicio), min_value=0.0)
            
            # Cliente
            tipo_cliente = st.radio("👤 Cliente", ["Existente", "Nuevo"], horizontal=True)
            
            if tipo_cliente == "Existente" and len(clientes) > 0:
                cliente_sel = st.selectbox("Seleccionar", options=clientes['id'].tolist(),
                    format_func=lambda x: clientes[clientes['id']==x]['nombre'].values[0])
                nuevo_nombre = nuevo_tel = nuevo_email = None
            else:
                cliente_sel = None
                nuevo_nombre = st.text_input("Nombre")
                nuevo_tel = st.text_input("Teléfono")
                nuevo_email = st.text_input("Email")
            
            canal = st.selectbox("📱 Canal", ["Booksy", "WhatsApp", "Walk-in", "Instagram", "Web", "Referido"])
            metodo_pago = st.selectbox("💳 Pago", ["Efectivo", "Tarjeta", "Bizum"])
            propina = st.number_input("💝 Propina (€)", value=0.0, min_value=0.0)
            notas = st.text_area("📝 Notas")
            
            submitted = st.form_submit_button("✅ Registrar Cita", use_container_width=True, type="primary")
            
            if submitted:
                if tipo_cliente == "Nuevo":
                    if not nuevo_nombre:
                        st.error("Ingresa el nombre del cliente")
                    else:
                        cliente_sel = insertar_cliente(nuevo_nombre, nuevo_tel, nuevo_email, canal, "")
                        st.success(f"✅ Cliente '{nuevo_nombre}' creado")
                
                if cliente_sel:
                    insertar_cita(fecha_cita, hora_cita, cliente_sel, servicio_sel, 
                                precio_cobrado, propina, canal, metodo_pago, notas)
                    st.success("✅ ¡Cita registrada!")
                    st.balloons()

# ---------- SOLICITUDES ----------
elif pagina == 'solicitudes':
    st.markdown('<h2 class="section-title">📋 Solicitudes</h2>', unsafe_allow_html=True)
    
    solicitudes = get_solicitudes()
    
    tab1, tab2 = st.tabs(["⏳ Pendientes", "✅ Confirmadas"])
    
    with tab1:
        pendientes_df = solicitudes[solicitudes['estado'] == 'pendiente'] if len(solicitudes) > 0 else pd.DataFrame()
        
        if len(pendientes_df) == 0:
            st.success("🎉 ¡No hay solicitudes pendientes!")
        else:
            for _, sol in pendientes_df.iterrows():
                st.markdown(f"""
                <div class="request-card">
                    <div class="client-name">👤 {sol['nombre']}</div>
                    <div class="client-info">📱 {sol['telefono']}</div>
                    <div class="client-info">💅 {sol['servicio_solicitado']}</div>
                    <div class="client-info">🕐 {sol['preferencia_horario']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar", key=f"conf_{sol['id']}", use_container_width=True):
                        actualizar_solicitud(sol['id'], 'confirmada', '')
                        st.rerun()
                with col2:
                    if st.button("❌ Rechazar", key=f"rech_{sol['id']}", use_container_width=True):
                        actualizar_solicitud(sol['id'], 'rechazada', '')
                        st.rerun()
                st.markdown("---")
    
    with tab2:
        confirmadas_df = solicitudes[solicitudes['estado'] == 'confirmada'] if len(solicitudes) > 0 else pd.DataFrame()
        if len(confirmadas_df) > 0:
            for _, sol in confirmadas_df.iterrows():
                st.markdown(f"""
                <div class="request-card confirmed">
                    <div class="client-name">👤 {sol['nombre']}</div>
                    <div class="client-info">💅 {sol['servicio_solicitado']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay solicitudes confirmadas")

# ---------- CLIENTES ----------
elif pagina == 'clientes':
    st.markdown('<h2 class="section-title">👥 Clientes</h2>', unsafe_allow_html=True)
    
    clientes = get_clientes()
    
    # Búsqueda
    buscar = st.text_input("🔍 Buscar cliente", placeholder="Nombre o teléfono")
    
    if len(clientes) > 0:
        if buscar:
            clientes = clientes[
                clientes['nombre'].str.contains(buscar, case=False, na=False) |
                clientes['telefono'].astype(str).str.contains(buscar, case=False, na=False)
            ]
        
        st.markdown(f'<p style="color: #8E8E93; font-size: 0.85rem; margin-bottom: 12px;">{len(clientes)} clientes</p>', unsafe_allow_html=True)
        
        for _, cl in clientes.iterrows():
            st.markdown(f"""
            <div class="list-card">
                <div class="list-item">
                    <div class="list-item-content">
                        <div class="list-item-title">{cl['nombre']}</div>
                        <div class="list-item-subtitle">📱 {cl['telefono'] or 'Sin teléfono'}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay clientes registrados")
    
    # Agregar cliente
    with st.expander("➕ Agregar Cliente"):
        with st.form("form_cliente"):
            nombre_cl = st.text_input("Nombre")
            telefono_cl = st.text_input("Teléfono")
            email_cl = st.text_input("Email")
            canal_cl = st.selectbox("Canal", ["Booksy", "Instagram", "WhatsApp", "Web", "Referido", "Walk-in"])
            
            if st.form_submit_button("💾 Guardar", use_container_width=True):
                if nombre_cl:
                    insertar_cliente(nombre_cl, telefono_cl, email_cl, canal_cl, "")
                    st.success(f"✅ Cliente '{nombre_cl}' guardado")
                    st.rerun()

# ---------- SERVICIOS ----------
elif pagina == 'servicios':
    st.markdown('<h2 class="section-title">💅 Servicios</h2>', unsafe_allow_html=True)
    
    servicios = get_servicios()
    categorias = get_categorias()
    
    if len(servicios) > 0:
        for cat in servicios['categoria_nombre'].unique():
            st.markdown(f'<p style="color: #8E8E93; font-size: 0.85rem; font-weight: 600; margin: 16px 0 8px 4px; text-transform: uppercase;">{cat}</p>', unsafe_allow_html=True)
            
            servicios_cat = servicios[servicios['categoria_nombre'] == cat]
            
            for _, srv in servicios_cat.iterrows():
                st.markdown(f"""
                <div class="list-card">
                    <div class="list-item">
                        <div class="list-item-content">
                            <div class="list-item-title">{srv['nombre']}</div>
                            <div class="list-item-subtitle">{srv['duracion_minutos']} min</div>
                        </div>
                        <div class="list-item-value">€{srv['precio']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay servicios creados")
    
    # Agregar servicio
    with st.expander("➕ Agregar Servicio"):
        with st.form("form_servicio"):
            nombre_srv = st.text_input("Nombre del servicio")
            categoria_sel = st.selectbox("Categoría", options=categorias['id'].tolist(),
                format_func=lambda x: categorias[categorias['id']==x]['nombre'].values[0])
            precio_srv = st.number_input("Precio (€)", min_value=0.0, step=5.0)
            duracion_srv = st.number_input("Duración (min)", min_value=15, step=15, value=60)
            costo_ins = st.number_input("Costo insumos (€)", min_value=0.0, step=1.0)
            
            if st.form_submit_button("💾 Guardar", use_container_width=True):
                if nombre_srv and precio_srv > 0:
                    insertar_servicio(nombre_srv, categoria_sel, precio_srv, duracion_srv, costo_ins, "")
                    st.success(f"✅ Servicio '{nombre_srv}' creado")
                    st.rerun()

# ---------- GASTOS ----------
elif pagina == 'gastos':
    # Botón volver
    if st.button("← Volver al Dashboard", key="volver_gastos"):
        st.session_state.pagina = 'dashboard'
        st.rerun()
    
    st.markdown('<h2 class="section-title">💰 Gastos</h2>', unsafe_allow_html=True)
    
    gastos_fijos = get_gastos_fijos()
    gastos_var = get_gastos_variables(fecha_inicio, fecha_fin)
    
    total_fijos = gastos_fijos['monto'].sum() if len(gastos_fijos) > 0 else 0
    total_var = gastos_var['monto'].sum() if len(gastos_var) > 0 else 0
    
    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <span class="label">Gastos Fijos</span>
            <span class="value">€{total_fijos:,.0f}</span>
        </div>
        <div class="metric-card">
            <span class="label">Gastos Variables</span>
            <span class="value">€{total_var:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🏠 Fijos", "🛒 Variables"])
    
    with tab1:
        if len(gastos_fijos) > 0:
            for _, gf in gastos_fijos.iterrows():
                st.markdown(f"""
                <div class="list-card">
                    <div class="list-item">
                        <div class="list-item-content">
                            <div class="list-item-title">{gf['concepto']}</div>
                            <div class="list-item-subtitle">{gf['frecuencia']}</div>
                        </div>
                        <div class="list-item-value">€{gf['monto']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with st.form("form_gasto_fijo"):
            st.markdown("**➕ Agregar Gasto Fijo**")
            concepto_gf = st.text_input("Concepto")
            monto_gf = st.number_input("Monto (€)", min_value=0.0, step=10.0)
            frecuencia = st.selectbox("Frecuencia", ["mensual", "trimestral", "anual"])
            
            if st.form_submit_button("💾 Guardar"):
                if concepto_gf and monto_gf > 0:
                    insertar_gasto_fijo(concepto_gf, monto_gf, frecuencia, "")
                    st.success("✅ Guardado")
                    st.rerun()
    
    with tab2:
        if len(gastos_var) > 0:
            for _, gv in gastos_var.iterrows():
                st.markdown(f"""
                <div class="list-card">
                    <div class="list-item">
                        <div class="list-item-content">
                            <div class="list-item-title">{gv['concepto']}</div>
                            <div class="list-item-subtitle">{gv['fecha']} • {gv['categoria']}</div>
                        </div>
                        <div class="list-item-value">€{gv['monto']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with st.form("form_gasto_var"):
            st.markdown("**➕ Agregar Gasto Variable**")
            fecha_gv = st.date_input("Fecha", datetime.now())
            concepto_gv = st.text_input("Concepto", key="concepto_gv_form")
            monto_gv = st.number_input("Monto (€)", min_value=0.0, step=5.0, key="monto_gv_form")
            categoria_gv = st.selectbox("Categoría", ["Insumos", "Marketing", "Formación", "Mantenimiento", "Otros"])
            
            if st.form_submit_button("💾 Guardar"):
                if concepto_gv and monto_gv > 0:
                    insertar_gasto_variable(fecha_gv, concepto_gv, monto_gv, categoria_gv, "")
                    st.success("✅ Guardado")
                    st.rerun()

# ---------- CONFIGURACIÓN ----------
elif pagina == 'config':
    st.markdown('<h2 class="section-title">⚙️ Configuración</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="list-card">
        <div class="list-item">
            <div class="list-item-content">
                <div class="list-item-title">📅 Período Actual</div>
                <div class="list-item-subtitle">Mes en curso</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Categorías
    st.markdown('<h3 class="section-title" style="margin-top: 24px;">📁 Categorías</h3>', unsafe_allow_html=True)
    categorias = get_categorias()
    
    for _, cat in categorias.iterrows():
        st.markdown(f"""
        <div class="list-card">
            <div class="list-item">
                <div class="list-item-content">
                    <div class="list-item-title">{cat['nombre']}</div>
                    <div class="list-item-subtitle">{cat['descripcion'] or 'Sin descripción'}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Botón refrescar
    st.markdown("---")
    if st.button("🔄 Actualizar Datos", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()
    
    # Info
    st.markdown("""
    <div style="text-align: center; margin-top: 32px; color: #8E8E93; font-size: 0.8rem;">
        <p>BeautyBox Málaga v4.0</p>
        <p>Sistema de Gestión</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# NAVEGACIÓN INFERIOR CON BOTONES
# ============================================

# Solo mostrar navegación en páginas principales (no en registrar/gastos que tienen formularios)
if pagina not in ['registrar', 'gastos']:
    st.markdown("---")
    
    # Crear columnas para los botones de navegación
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📊\nDashboard", key="nav_dashboard", use_container_width=True):
            st.session_state.pagina = 'dashboard'
            st.rerun()
    
    with col2:
        badge = f" ({pendientes})" if pendientes > 0 else ""
        if st.button(f"📋\nSolicitudes{badge}", key="nav_solicitudes", use_container_width=True):
            st.session_state.pagina = 'solicitudes'
            st.rerun()
    
    with col3:
        if st.button("👥\nClientes", key="nav_clientes", use_container_width=True):
            st.session_state.pagina = 'clientes'
            st.rerun()
    
    with col4:
        if st.button("💅\nServicios", key="nav_servicios", use_container_width=True):
            st.session_state.pagina = 'servicios'
            st.rerun()
    
    with col5:
        if st.button("⚙️\nConfig", key="nav_config", use_container_width=True):
            st.session_state.pagina = 'config'
            st.rerun()
