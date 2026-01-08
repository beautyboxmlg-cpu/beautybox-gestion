"""
BeautyBox Málaga - Sistema de Métricas y Gestión de Negocio
Versión Google Sheets - Para uso en la nube
v3.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gspread
from google.oauth2.service_account import Credentials

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================

st.set_page_config(
    page_title="BeautyBox Málaga - Gestión",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
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
    }
    .metric-card {
        background: linear-gradient(135deg, #f9f7f5 0%, #fff 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #d4a5a5;
    }
    .stMetric {
        background-color: #f9f7f5;
        padding: 1rem;
        border-radius: 10px;
    }
    .solicitud-pendiente {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    .solicitud-confirmada {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONEXIÓN A GOOGLE SHEETS
# ============================================

@st.cache_resource
def get_google_connection():
    """Conectar a Google Sheets usando credenciales de Streamlit Secrets"""
    try:
        # Definir los scopes necesarios
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Obtener credenciales desde Streamlit Secrets
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )
        
        # Conectar a Google Sheets
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
        st.info("Crea un Google Sheet con ese nombre y compártelo con la cuenta de servicio")
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
# FUNCIONES DE DATOS (LECTURA)
# ============================================

def get_categorias():
    """Obtener categorías desde Google Sheets"""
    spreadsheet = get_spreadsheet()
    headers = ['id', 'nombre', 'descripcion', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'categorias', headers)
    
    data = worksheet.get_all_records()
    if not data:
        # Insertar categorías por defecto
        categorias_default = [
            [1, 'Pestañas', 'Servicios de extensiones y tratamientos de pestañas', datetime.now().isoformat()],
            [2, 'Cejas', 'Servicios de diseño, laminado y micropigmentación', datetime.now().isoformat()],
            [3, 'Uñas', 'Servicios de manicura y pedicura', datetime.now().isoformat()],
            [4, 'Otros', 'Otros servicios de belleza', datetime.now().isoformat()]
        ]
        for cat in categorias_default:
            worksheet.append_row(cat)
        data = worksheet.get_all_records()
    
    return pd.DataFrame(data)

def get_servicios():
    """Obtener servicios activos desde Google Sheets"""
    spreadsheet = get_spreadsheet()
    headers = ['id', 'nombre', 'categoria_id', 'precio', 'duracion_minutos', 'costo_insumos', 'activo', 'descripcion', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'servicios', headers)
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=headers)
    
    if len(df) > 0:
        df = df[df['activo'] == 1]
        # Añadir nombre de categoría
        categorias = get_categorias()
        df = df.merge(categorias[['id', 'nombre']], left_on='categoria_id', right_on='id', 
                     how='left', suffixes=('', '_cat'))
        df = df.rename(columns={'nombre_cat': 'categoria_nombre'})
        if 'id_cat' in df.columns:
            df = df.drop(columns=['id_cat'])
    
    return df

def get_clientes():
    """Obtener clientes desde Google Sheets"""
    spreadsheet = get_spreadsheet()
    headers = ['id', 'nombre', 'telefono', 'email', 'fecha_primera_visita', 'canal_adquisicion', 'notas', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'clientes', headers)
    
    data = worksheet.get_all_records()
    return pd.DataFrame(data) if data else pd.DataFrame(columns=headers)

def get_citas(fecha_inicio=None, fecha_fin=None):
    """Obtener citas desde Google Sheets"""
    spreadsheet = get_spreadsheet()
    headers = ['id', 'fecha', 'hora', 'cliente_id', 'servicio_id', 'precio_cobrado', 'propina', 'canal_origen', 'metodo_pago', 'notas', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'citas', headers)
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=headers)
    
    if len(df) > 0:
        # Filtrar por fechas si se especifican
        if fecha_inicio and fecha_fin:
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df[(df['fecha'] >= pd.to_datetime(fecha_inicio)) & 
                   (df['fecha'] <= pd.to_datetime(fecha_fin))]
        
        # Añadir información de cliente y servicio
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
            
            # Añadir nombre de categoría
            if len(categorias) > 0:
                df = df.merge(categorias[['id', 'nombre']], left_on='categoria_id', right_on='id',
                             how='left', suffixes=('', '_cat'))
                df = df.rename(columns={'nombre': 'categoria_nombre'})
                if 'id_cat' in df.columns:
                    df = df.drop(columns=['id_cat'])
        
        df = df.sort_values('fecha', ascending=False)
    
    return df

def get_gastos_fijos():
    """Obtener gastos fijos activos desde Google Sheets"""
    spreadsheet = get_spreadsheet()
    headers = ['id', 'concepto', 'monto', 'frecuencia', 'activo', 'notas', 'created_at']
    worksheet = get_or_create_worksheet(spreadsheet, 'gastos_fijos', headers)
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=headers)
    
    if len(df) > 0:
        df = df[df['activo'] == 1]
    
    return df

def get_gastos_variables(fecha_inicio=None, fecha_fin=None):
    """Obtener gastos variables desde Google Sheets"""
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
    """Obtener solicitudes de citas desde Google Sheets"""
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
    """Obtener el siguiente ID disponible"""
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

def insertar_solicitud(nombre, telefono, email, servicio, preferencia, mensaje):
    spreadsheet = get_spreadsheet()
    headers = ['id', 'nombre', 'telefono', 'email', 'servicio_solicitado', 'preferencia_horario', 
               'mensaje', 'estado', 'fecha_solicitud', 'fecha_respuesta', 'notas_admin']
    worksheet = get_or_create_worksheet(spreadsheet, 'solicitudes', headers)
    new_id = get_next_id(worksheet)
    row = [new_id, nombre, telefono, email, servicio, preferencia, mensaje, 'pendiente', 
           datetime.now().isoformat(), '', '']
    worksheet.append_row(row)
    st.cache_resource.clear()
    return new_id

# ============================================
# FUNCIONES DE ACTUALIZACIÓN
# ============================================

def find_row_by_id(worksheet, id_value):
    """Encontrar el número de fila por ID"""
    data = worksheet.get_all_records()
    for i, row in enumerate(data):
        if row.get('id') == id_value:
            return i + 2  # +2 porque la fila 1 es el header y enumerate empieza en 0
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
        # Marcar como inactivo en lugar de eliminar
        worksheet.update(f'G{row_num}', [[0]])
    st.cache_resource.clear()
    return 0

def actualizar_cliente(cliente_id, nombre, telefono, email, canal, notas):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('clientes')
    row_num = find_row_by_id(worksheet, cliente_id)
    if row_num:
        worksheet.update(f'B{row_num}:G{row_num}', [[nombre, telefono, email, '', canal, notas]])
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

def actualizar_gasto_fijo(gasto_id, concepto, monto, frecuencia, notas):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('gastos_fijos')
    row_num = find_row_by_id(worksheet, gasto_id)
    if row_num:
        worksheet.update(f'B{row_num}:F{row_num}', [[concepto, monto, frecuencia, 1, notas]])
    st.cache_resource.clear()

def eliminar_gasto_fijo(gasto_id):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('gastos_fijos')
    row_num = find_row_by_id(worksheet, gasto_id)
    if row_num:
        worksheet.delete_rows(row_num)
    st.cache_resource.clear()

def actualizar_gasto_variable(gasto_id, fecha, concepto, monto, categoria, notas):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('gastos_variables')
    row_num = find_row_by_id(worksheet, gasto_id)
    if row_num:
        worksheet.update(f'B{row_num}:F{row_num}', [[str(fecha), concepto, monto, categoria, notas]])
    st.cache_resource.clear()

def eliminar_gasto_variable(gasto_id):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('gastos_variables')
    row_num = find_row_by_id(worksheet, gasto_id)
    if row_num:
        worksheet.delete_rows(row_num)
    st.cache_resource.clear()

def actualizar_solicitud(solicitud_id, estado, notas_admin):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet('solicitudes')
    row_num = find_row_by_id(worksheet, solicitud_id)
    if row_num:
        worksheet.update(f'H{row_num}:K{row_num}', [[estado, datetime.now().isoformat(), notas_admin]])
    st.cache_resource.clear()

# ============================================
# SIDEBAR - NAVEGACIÓN
# ============================================

st.sidebar.markdown("# 💅 BeautyBox")
st.sidebar.markdown("### Málaga")
st.sidebar.markdown("---")

# Contador de solicitudes pendientes
solicitudes = get_solicitudes()
pendientes = len(solicitudes[solicitudes['estado'] == 'pendiente']) if len(solicitudes) > 0 else 0
solicitudes_label = f"📋 Solicitudes ({pendientes})" if pendientes > 0 else "📋 Solicitudes"

pagina = st.sidebar.radio(
    "Navegación",
    ["📊 Dashboard", solicitudes_label, "📝 Registrar Cita", "💇 Servicios", "👥 Clientes", 
     "💰 Gastos", "📈 Proyecciones", "⚙️ Configuración"],
    index=0
)

# Normalizar el nombre de la página para solicitudes
if "Solicitudes" in pagina:
    pagina = "📋 Solicitudes"

st.sidebar.markdown("---")
st.sidebar.markdown("##### Filtros Globales")

# Filtro de fechas global
col1, col2 = st.sidebar.columns(2)
with col1:
    fecha_inicio = st.date_input("Desde", datetime.now().replace(day=1), key="fecha_inicio_global")
with col2:
    fecha_fin = st.date_input("Hasta", datetime.now(), key="fecha_fin_global")

# Botón para refrescar datos
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Actualizar Datos", use_container_width=True):
    st.cache_resource.clear()
    st.rerun()

# ============================================
# PÁGINA: DASHBOARD
# ============================================

if pagina == "📊 Dashboard":
    st.markdown("<h1 class='main-header'>📊 Dashboard BeautyBox</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Métricas y análisis de rendimiento</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Mostrar alerta de solicitudes pendientes
    if pendientes > 0:
        st.warning(f"📋 Tienes **{pendientes} solicitud(es) pendiente(s)** de confirmar. Ve a 'Solicitudes' para gestionarlas.")
    
    # Obtener datos
    citas = get_citas(fecha_inicio, fecha_fin)
    gastos_fijos = get_gastos_fijos()
    gastos_var = get_gastos_variables(fecha_inicio, fecha_fin)
    
    if len(citas) == 0:
        st.info("👋 ¡Bienvenida! No hay datos registrados aún. Ve a '📝 Registrar Cita' para comenzar.")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ingresos Totales", "€0")
        col2.metric("Nº Citas", "0")
        col3.metric("Ticket Promedio", "€0")
        col4.metric("Clientes Únicos", "0")
    else:
        # Calcular métricas
        ingresos_totales = citas['precio_cobrado'].sum() + citas['propina'].sum()
        propinas_total = citas['propina'].sum()
        num_citas = len(citas)
        ticket_promedio = citas['precio_cobrado'].mean()
        clientes_unicos = citas['cliente_id'].nunique()
        
        # Calcular costos
        costo_insumos_total = citas['costo_insumos'].fillna(0).sum() if 'costo_insumos' in citas.columns else 0
        gastos_fijos_mensual = gastos_fijos['monto'].sum() if len(gastos_fijos) > 0 else 0
        gastos_var_total = gastos_var['monto'].sum() if len(gastos_var) > 0 else 0
        
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        meses_periodo = dias_periodo / 30
        gastos_fijos_periodo = gastos_fijos_mensual * meses_periodo
        
        costos_totales = costo_insumos_total + gastos_fijos_periodo + gastos_var_total
        utilidad_bruta = ingresos_totales - costo_insumos_total
        utilidad_neta = ingresos_totales - costos_totales
        margen_neto = (utilidad_neta / ingresos_totales * 100) if ingresos_totales > 0 else 0
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💶 Ingresos Totales", f"€{ingresos_totales:,.2f}")
        col2.metric("📅 Nº Citas", f"{num_citas}")
        col3.metric("🎫 Ticket Promedio", f"€{ticket_promedio:,.2f}")
        col4.metric("👥 Clientes Únicos", f"{clientes_unicos}")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💵 Utilidad Bruta", f"€{utilidad_bruta:,.2f}")
        col2.metric("📊 Utilidad Neta", f"€{utilidad_neta:,.2f}")
        col3.metric("📈 Margen Neto", f"{margen_neto:.1f}%")
        col4.metric("💝 Propinas", f"€{propinas_total:,.2f}")
        
        st.markdown("---")
        
        # Gráficos
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📈 Ingresos por Día")
            citas['fecha'] = pd.to_datetime(citas['fecha'])
            ingresos_diarios = citas.groupby('fecha')['precio_cobrado'].sum().reset_index()
            
            fig = px.line(ingresos_diarios, x='fecha', y='precio_cobrado',
                         labels={'fecha': 'Fecha', 'precio_cobrado': 'Ingresos (€)'},
                         markers=True)
            fig.update_traces(line_color='#d4a5a5', marker_color='#c48b9f')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("🥧 Servicios Más Vendidos")
            if 'servicio_nombre' in citas.columns:
                servicios_count = citas.groupby('servicio_nombre').size().reset_index(name='cantidad')
                servicios_count = servicios_count.sort_values('cantidad', ascending=False).head(10)
                
                fig = px.pie(servicios_count, values='cantidad', names='servicio_nombre',
                            color_discrete_sequence=px.colors.sequential.RdPu)
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # Segunda fila
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📊 Ingresos por Categoría")
            if 'categoria_nombre' in citas.columns:
                ingresos_cat = citas.groupby('categoria_nombre')['precio_cobrado'].sum().reset_index()
                fig = px.bar(ingresos_cat, x='categoria_nombre', y='precio_cobrado',
                            color='precio_cobrado', color_continuous_scale='RdPu')
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("📱 Canal de Origen")
            canal_count = citas.groupby('canal_origen').size().reset_index(name='cantidad')
            fig = px.bar(canal_count, x='canal_origen', y='cantidad',
                        color='cantidad', color_continuous_scale='RdPu')
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# PÁGINA: SOLICITUDES
# ============================================

elif pagina == "📋 Solicitudes":
    st.markdown("<h1 class='main-header'>📋 Solicitudes de Citas</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Gestiona las solicitudes de reserva de clientes</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    solicitudes = get_solicitudes()
    
    # Tabs por estado
    tab1, tab2, tab3 = st.tabs(["⏳ Pendientes", "✅ Confirmadas", "❌ Rechazadas"])
    
    with tab1:
        pendientes_df = solicitudes[solicitudes['estado'] == 'pendiente'] if len(solicitudes) > 0 else pd.DataFrame()
        
        if len(pendientes_df) == 0:
            st.success("🎉 ¡No hay solicitudes pendientes!")
        else:
            st.warning(f"Tienes **{len(pendientes_df)}** solicitud(es) por gestionar")
            
            for _, sol in pendientes_df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class='solicitud-pendiente'>
                        <strong>👤 {sol['nombre']}</strong> - 📱 {sol['telefono']}<br>
                        <strong>Servicio:</strong> {sol['servicio_solicitado']}<br>
                        <strong>Preferencia:</strong> {sol['preferencia_horario']}<br>
                        <strong>Mensaje:</strong> {sol['mensaje'] if sol['mensaje'] else 'Sin mensaje'}<br>
                        <small>📅 Solicitado: {sol['fecha_solicitud']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        notas = st.text_input("Notas (opcional)", key=f"notas_{sol['id']}", 
                                             placeholder="Ej: Confirmada para Lunes 10:00")
                    
                    with col2:
                        if st.button("✅ Confirmar", key=f"conf_{sol['id']}", type="primary", use_container_width=True):
                            actualizar_solicitud(sol['id'], 'confirmada', notas)
                            st.success("Solicitud confirmada")
                            st.rerun()
                    
                    with col3:
                        if st.button("❌ Rechazar", key=f"rech_{sol['id']}", type="secondary", use_container_width=True):
                            actualizar_solicitud(sol['id'], 'rechazada', notas)
                            st.info("Solicitud rechazada")
                            st.rerun()
                    
                    st.markdown("---")
    
    with tab2:
        confirmadas_df = solicitudes[solicitudes['estado'] == 'confirmada'] if len(solicitudes) > 0 else pd.DataFrame()
        
        if len(confirmadas_df) == 0:
            st.info("No hay solicitudes confirmadas")
        else:
            for _, sol in confirmadas_df.iterrows():
                st.markdown(f"""
                <div class='solicitud-confirmada'>
                    <strong>👤 {sol['nombre']}</strong> - 📱 {sol['telefono']}<br>
                    <strong>Servicio:</strong> {sol['servicio_solicitado']}<br>
                    <strong>Notas:</strong> {sol['notas_admin'] if sol['notas_admin'] else 'Sin notas'}<br>
                    <small>✅ Confirmada: {sol['fecha_respuesta']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        rechazadas_df = solicitudes[solicitudes['estado'] == 'rechazada'] if len(solicitudes) > 0 else pd.DataFrame()
        
        if len(rechazadas_df) == 0:
            st.info("No hay solicitudes rechazadas")
        else:
            st.dataframe(rechazadas_df[['nombre', 'telefono', 'servicio_solicitado', 'notas_admin', 'fecha_respuesta']], 
                        use_container_width=True, hide_index=True)

# ============================================
# PÁGINA: REGISTRAR CITA
# ============================================

elif pagina == "📝 Registrar Cita":
    st.markdown("<h1 class='main-header'>📝 Registrar Cita</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Registra cada servicio realizado</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    servicios = get_servicios()
    clientes = get_clientes()
    
    if len(servicios) == 0:
        st.warning("⚠️ Primero debes crear al menos un servicio. Ve a '💇 Servicios'")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Datos de la Cita")
            
            fecha_cita = st.date_input("Fecha", datetime.now())
            hora_cita = st.time_input("Hora", datetime.now().time())
            
            servicio_opciones = servicios[['id', 'nombre', 'precio', 'categoria_nombre']].copy()
            servicio_opciones['display'] = servicio_opciones.apply(
                lambda x: f"{x['categoria_nombre']} - {x['nombre']} (€{x['precio']:.2f})", axis=1
            )
            
            servicio_sel = st.selectbox(
                "Servicio",
                options=servicio_opciones['id'].tolist(),
                format_func=lambda x: servicio_opciones[servicio_opciones['id']==x]['display'].values[0]
            )
            
            precio_servicio = servicios[servicios['id']==servicio_sel]['precio'].values[0]
            precio_cobrado = st.number_input("Precio Cobrado (€)", value=float(precio_servicio), min_value=0.0, step=1.0)
            propina = st.number_input("Propina (€)", value=0.0, min_value=0.0, step=0.5)
        
        with col2:
            st.subheader("👤 Cliente y Canal")
            
            tipo_cliente = st.radio("Tipo de cliente", ["Cliente existente", "Cliente nuevo"], horizontal=True)
            
            if tipo_cliente == "Cliente existente" and len(clientes) > 0:
                cliente_opciones = clientes[['id', 'nombre', 'telefono']].copy()
                cliente_opciones['display'] = cliente_opciones.apply(
                    lambda x: f"{x['nombre']} ({x['telefono']})" if x['telefono'] else x['nombre'], axis=1
                )
                
                cliente_sel = st.selectbox(
                    "Seleccionar cliente",
                    options=cliente_opciones['id'].tolist(),
                    format_func=lambda x: cliente_opciones[cliente_opciones['id']==x]['display'].values[0]
                )
            else:
                st.markdown("##### Nuevo Cliente")
                nuevo_nombre = st.text_input("Nombre completo")
                nuevo_tel = st.text_input("Teléfono")
                nuevo_email = st.text_input("Email (opcional)")
                cliente_sel = None
            
            canal = st.selectbox("Canal de origen", ["Booksy", "WhatsApp", "Walk-in", "Instagram", "Web", "Referido", "Otro"])
            metodo_pago = st.selectbox("Método de pago", ["Efectivo", "Tarjeta", "Bizum", "Transferencia"])
            notas = st.text_area("Notas (opcional)")
        
        st.markdown("---")
        
        if st.button("✅ Registrar Cita", type="primary", use_container_width=True):
            if tipo_cliente == "Cliente nuevo":
                if not nuevo_nombre:
                    st.error("Por favor ingresa el nombre del cliente")
                else:
                    cliente_sel = insertar_cliente(nuevo_nombre, nuevo_tel, nuevo_email, canal, "")
                    st.success(f"✅ Cliente '{nuevo_nombre}' creado")
            
            if cliente_sel:
                insertar_cita(fecha_cita, hora_cita, cliente_sel, servicio_sel, 
                            precio_cobrado, propina, canal, metodo_pago, notas)
                st.success("✅ ¡Cita registrada exitosamente!")
                st.balloons()
    
    # Últimas citas
    st.markdown("---")
    st.subheader("📋 Últimas Citas Registradas")
    
    citas_recientes = get_citas()
    if len(citas_recientes) > 0:
        cols_to_show = ['fecha', 'hora', 'cliente_nombre', 'servicio_nombre', 'precio_cobrado', 'propina', 'canal_origen']
        cols_available = [c for c in cols_to_show if c in citas_recientes.columns]
        citas_display = citas_recientes[cols_available].head(10).copy()
        st.dataframe(citas_display, use_container_width=True, hide_index=True)
    else:
        st.info("No hay citas registradas aún")

# ============================================
# PÁGINA: SERVICIOS
# ============================================

elif pagina == "💇 Servicios":
    st.markdown("<h1 class='main-header'>💇 Catálogo de Servicios</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Gestiona tu carta de servicios</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📋 Ver Servicios", "➕ Agregar Servicio", "✏️ Editar/Eliminar"])
    
    with tab1:
        servicios = get_servicios()
        if len(servicios) > 0:
            categorias_srv = servicios['categoria_nombre'].unique()
            
            for cat in categorias_srv:
                st.subheader(f"📁 {cat}")
                servicios_cat = servicios[servicios['categoria_nombre']==cat][
                    ['nombre', 'precio', 'duracion_minutos', 'costo_insumos']
                ].copy()
                servicios_cat.columns = ['Servicio', 'Precio (€)', 'Duración (min)', 'Costo Insumos (€)']
                st.dataframe(servicios_cat, use_container_width=True, hide_index=True)
        else:
            st.info("No hay servicios creados. Usa la pestaña 'Agregar Servicio'")
    
    with tab2:
        st.subheader("➕ Nuevo Servicio")
        
        categorias = get_categorias()
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_serv = st.text_input("Nombre del servicio")
            categoria_sel = st.selectbox(
                "Categoría",
                options=categorias['id'].tolist(),
                format_func=lambda x: categorias[categorias['id']==x]['nombre'].values[0]
            )
            precio_serv = st.number_input("Precio (€)", min_value=0.0, step=5.0)
        
        with col2:
            duracion_serv = st.number_input("Duración (minutos)", min_value=15, step=15, value=60)
            costo_insumos = st.number_input("Costo de insumos (€)", min_value=0.0, step=1.0)
            descripcion = st.text_area("Descripción (opcional)")
        
        if st.button("💾 Guardar Servicio", type="primary"):
            if nombre_serv and precio_serv > 0:
                insertar_servicio(nombre_serv, categoria_sel, precio_serv, duracion_serv, costo_insumos, descripcion)
                st.success(f"✅ Servicio '{nombre_serv}' creado")
                st.rerun()
            else:
                st.error("Completa nombre y precio")
    
    with tab3:
        st.subheader("✏️ Editar o Eliminar Servicio")
        
        servicios = get_servicios()
        categorias = get_categorias()
        
        if len(servicios) == 0:
            st.info("No hay servicios para editar")
        else:
            servicio_editar_id = st.selectbox(
                "Selecciona el servicio",
                options=servicios['id'].tolist(),
                format_func=lambda x: f"{servicios[servicios['id']==x]['categoria_nombre'].values[0]} - {servicios[servicios['id']==x]['nombre'].values[0]}"
            )
            
            serv_actual = servicios[servicios['id'] == servicio_editar_id].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                edit_nombre = st.text_input("Nombre", value=serv_actual['nombre'], key="edit_nombre")
                edit_categoria = st.selectbox(
                    "Categoría",
                    options=categorias['id'].tolist(),
                    format_func=lambda x: categorias[categorias['id']==x]['nombre'].values[0],
                    key="edit_categoria"
                )
                edit_precio = st.number_input("Precio (€)", value=float(serv_actual['precio']), key="edit_precio")
            
            with col2:
                edit_duracion = st.number_input("Duración (min)", value=int(serv_actual['duracion_minutos']), key="edit_duracion")
                edit_costo = st.number_input("Costo insumos (€)", value=float(serv_actual['costo_insumos'] or 0), key="edit_costo")
                edit_desc = st.text_area("Descripción", value=serv_actual['descripcion'] or "", key="edit_desc")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                    actualizar_servicio(servicio_editar_id, edit_nombre, edit_categoria, 
                                       edit_precio, edit_duracion, edit_costo, edit_desc)
                    st.success("✅ Servicio actualizado")
                    st.rerun()
            with col2:
                if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
                    eliminar_servicio(servicio_editar_id)
                    st.success("✅ Servicio eliminado")
                    st.rerun()

# ============================================
# PÁGINA: CLIENTES
# ============================================

elif pagina == "👥 Clientes":
    st.markdown("<h1 class='main-header'>👥 Base de Clientes</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    clientes = get_clientes()
    
    col1, col2 = st.columns(2)
    col1.metric("👥 Total Clientes", len(clientes))
    
    tab1, tab2 = st.tabs(["📋 Ver Clientes", "➕ Agregar Cliente"])
    
    with tab1:
        if len(clientes) > 0:
            buscar = st.text_input("🔍 Buscar cliente")
            if buscar:
                clientes = clientes[
                    clientes['nombre'].str.contains(buscar, case=False, na=False) |
                    clientes['telefono'].str.contains(buscar, case=False, na=False)
                ]
            st.dataframe(clientes[['nombre', 'telefono', 'email', 'canal_adquisicion']], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("No hay clientes registrados")
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            nombre_cl = st.text_input("Nombre completo", key="nuevo_cl_nombre")
            telefono_cl = st.text_input("Teléfono", key="nuevo_cl_tel")
        with col2:
            email_cl = st.text_input("Email", key="nuevo_cl_email")
            canal_cl = st.selectbox("¿Cómo nos conoció?", 
                                   ["Booksy", "Instagram", "WhatsApp", "Web", "Referido", "Walk-in", "Google", "Otro"])
        
        notas_cl = st.text_area("Notas", key="nuevo_cl_notas")
        
        if st.button("💾 Guardar Cliente", type="primary"):
            if nombre_cl:
                insertar_cliente(nombre_cl, telefono_cl, email_cl, canal_cl, notas_cl)
                st.success(f"✅ Cliente '{nombre_cl}' guardado")
                st.rerun()

# ============================================
# PÁGINA: GASTOS
# ============================================

elif pagina == "💰 Gastos":
    st.markdown("<h1 class='main-header'>💰 Control de Gastos</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📊 Resumen", "🏠 Gastos Fijos", "🛒 Gastos Variables"])
    
    with tab1:
        gastos_fijos = get_gastos_fijos()
        gastos_var = get_gastos_variables(fecha_inicio, fecha_fin)
        
        total_fijos = gastos_fijos['monto'].sum() if len(gastos_fijos) > 0 else 0
        total_var = gastos_var['monto'].sum() if len(gastos_var) > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🏠 Gastos Fijos Mensuales", f"€{total_fijos:,.2f}")
        col2.metric("🛒 Gastos Variables", f"€{total_var:,.2f}")
        col3.metric("💸 Total", f"€{total_fijos + total_var:,.2f}")
    
    with tab2:
        gastos_fijos = get_gastos_fijos()
        
        if len(gastos_fijos) > 0:
            st.dataframe(gastos_fijos[['concepto', 'monto', 'frecuencia']], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("➕ Agregar Gasto Fijo")
        
        col1, col2 = st.columns(2)
        with col1:
            concepto_gf = st.text_input("Concepto", placeholder="Ej: Alquiler")
            monto_gf = st.number_input("Monto (€)", min_value=0.0, step=10.0)
        with col2:
            frecuencia_gf = st.selectbox("Frecuencia", ["mensual", "trimestral", "anual"])
            notas_gf = st.text_input("Notas")
        
        if st.button("💾 Guardar Gasto Fijo", type="primary"):
            if concepto_gf and monto_gf > 0:
                insertar_gasto_fijo(concepto_gf, monto_gf, frecuencia_gf, notas_gf)
                st.success("✅ Guardado")
                st.rerun()
    
    with tab3:
        gastos_var = get_gastos_variables(fecha_inicio, fecha_fin)
        
        if len(gastos_var) > 0:
            st.dataframe(gastos_var[['fecha', 'concepto', 'monto', 'categoria']], use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("➕ Agregar Gasto Variable")
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_gv = st.date_input("Fecha", datetime.now(), key="fecha_gv")
            concepto_gv = st.text_input("Concepto", key="concepto_gv")
            monto_gv = st.number_input("Monto (€)", min_value=0.0, step=5.0, key="monto_gv")
        with col2:
            categoria_gv = st.selectbox("Categoría", ["Insumos", "Marketing", "Formación", "Mantenimiento", "Otros"])
            notas_gv = st.text_input("Notas", key="notas_gv")
        
        if st.button("💾 Guardar Gasto Variable", type="primary"):
            if concepto_gv and monto_gv > 0:
                insertar_gasto_variable(fecha_gv, concepto_gv, monto_gv, categoria_gv, notas_gv)
                st.success("✅ Guardado")
                st.rerun()

# ============================================
# PÁGINA: PROYECCIONES
# ============================================

elif pagina == "📈 Proyecciones":
    st.markdown("<h1 class='main-header'>📈 Proyecciones</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    citas = get_citas()
    gastos_fijos = get_gastos_fijos()
    
    if len(citas) < 5:
        st.warning("⚠️ Necesitas al menos 5 citas para proyecciones.")
    else:
        citas['fecha'] = pd.to_datetime(citas['fecha'])
        citas['mes'] = citas['fecha'].dt.to_period('M')
        
        ingresos_mensuales = citas.groupby('mes').agg({
            'precio_cobrado': 'sum',
            'id': 'count'
        }).reset_index()
        ingresos_mensuales.columns = ['Mes', 'Ingresos', 'Citas']
        ingresos_mensuales['Mes_str'] = ingresos_mensuales['Mes'].astype(str)
        
        promedio_mensual = ingresos_mensuales['Ingresos'].mean()
        ticket_promedio = citas['precio_cobrado'].mean()
        gastos_fijos_total = gastos_fijos['monto'].sum() if len(gastos_fijos) > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Ingreso Mensual Promedio", f"€{promedio_mensual:,.2f}")
        col2.metric("🎫 Ticket Promedio", f"€{ticket_promedio:.2f}")
        col3.metric("🏠 Gastos Fijos", f"€{gastos_fijos_total:,.2f}")
        
        st.subheader("📈 Tendencia de Ingresos")
        fig = px.bar(ingresos_mensuales, x='Mes_str', y='Ingresos', color='Ingresos',
                    color_continuous_scale='RdPu')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# PÁGINA: CONFIGURACIÓN
# ============================================

elif pagina == "⚙️ Configuración":
    st.markdown("<h1 class='main-header'>⚙️ Configuración</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("📁 Categorías de Servicios")
    categorias = get_categorias()
    st.dataframe(categorias[['nombre', 'descripcion']], use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("🔗 Link del Formulario Público")
    st.info("Una vez desplegado, tu formulario de reservas estará disponible en:")
    st.code("https://tu-app.streamlit.app/reservar")
    
    st.markdown("---")
    st.subheader("📱 Añadir a Pantalla de Inicio")
    st.markdown("""
    **En iPhone/iPad:**
    1. Abre Safari y ve a tu app
    2. Toca el icono de compartir (cuadrado con flecha)
    3. Selecciona "Añadir a pantalla de inicio"
    
    **En Android:**
    1. Abre Chrome y ve a tu app
    2. Toca los tres puntos (menú)
    3. Selecciona "Añadir a pantalla de inicio"
    """)

# ============================================
# FOOTER
# ============================================

st.sidebar.markdown("---")
st.sidebar.markdown("##### 💅 BeautyBox Málaga")
st.sidebar.markdown("Sistema de Gestión v3.0")
st.sidebar.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
