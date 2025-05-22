import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

# ---------- Inicializar estado de sesión ---------- #
for key in [
    'folio', 'edad', 'tiempo_viuda', 'causa_fallecimiento', 'hijos_menores',
    'telefono', 'observaciones', 'edades_hijos', 'causa_muerte', 'fecha_muerte',
    'ayuda_solicita', 'rango_edad', 'prioridad_zapopan', 'perfil_cirineas',
    'atencion_psicologica', 'apoyo_economico', 'apoyo_hijos', 'archivo_cargado'
]:
    if key not in st.session_state:
        st.session_state[key] = None

# ---------- Título ---------- #
st.title("Formulario de registro - Cirineas")

# --------- Limpiar formulario si se acaba de guardar --------- #
if st.session_state.get("form_reset") is True:
    for k in [
        'folio', 'edad', 'tiempo_viuda', 'causa_fallecimiento', 'hijos_menores',
        'telefono', 'observaciones', 'edades_hijos', 'causa_muerte', 'fecha_muerte',
        'ayuda_solicita', 'rango_edad', 'prioridad_zapopan', 'perfil_cirineas',
        'atencion_psicologica', 'apoyo_economico', 'apoyo_hijos'
    ]:
        st.session_state[k] = None
    st.session_state["form_reset"] = False

# ---------- Carga el archivo ---------- #
if st.session_state['archivo_cargado'] is None:
    st.markdown("### 1. Cargar archivo existente")
    archivo_subido = st.file_uploader("📥 Sube tu archivo de capturas (Excel)", type=["xlsx"])
    if archivo_subido:
        st.session_state['archivo_cargado'] = pd.read_excel(archivo_subido)

# Obtener datos cargados o crear uno vacío
df_capturas = st.session_state['archivo_cargado'] if st.session_state['archivo_cargado'] is not None else pd.DataFrame()

# ---------- Mostrar capturas existentes ---------- #
if not df_capturas.empty:
    st.markdown("### 📄 Casos ya registrados")

    if 'FECHA_MUERTE' in df_capturas.columns:
        df_capturas['FECHA_MUERTE'] = pd.to_datetime(
            df_capturas['FECHA_MUERTE'], errors='coerce'
        ).dt.date
        df_capturas['FECHA_MUERTE'] = df_capturas['FECHA_MUERTE'].astype(str)

    st.dataframe(df_capturas)

# ---------- Cargar catálogo de colonias ---------- #
import os

catalogo_path = os.path.join("data", "auxiliares", "BD_-Cirineas_Control-v1.xlsx")
df_control = pd.read_excel(catalogo_path, sheet_name="Control")
df_control = df_control[['COLONIA', 'CP', 'MUNICIPIO']].dropna()
df_control['CP'] = df_control['CP'].astype(str)

# ---------- Formulario ---------- #
st.markdown("### 📝 Nuevo registro")

# Entradas de texto y numéricas
folio = st.text_input("Folio *", value="" if st.session_state['folio'] is None else st.session_state['folio'])
edad = st.number_input("Edad", min_value=0, max_value=120, value=st.session_state['edad'] or 0)

# Fx para calcular rango edad
def calcular_rango_edad(edad):
    if edad < 22:
        return "menos de 22"
    elif 22 <= edad <= 29:
        return "22-29"
    elif 30 <= edad <= 39:
        return "30 a 39"
    elif 40 <= edad <= 49:
        return "40 a 49"
    elif 50 <= edad <= 59:
        return "50 a 59"
    elif edad >= 60:
        return "60 y más"
    return "S/E"

rango_edad = calcular_rango_edad(edad)

cp = st.selectbox("Código Postal", sorted(df_control['CP'].unique()))
colonias = sorted(df_control[df_control['CP'] == cp]['COLONIA'].unique())
colonia = st.selectbox("Colonia", colonias)

municipio = df_control[(df_control['CP'] == cp) & (df_control['COLONIA'] == colonia)]['MUNICIPIO'].values[0]
st.text_input("Municipio", value=municipio, disabled=True)

tiempo_viuda = st.text_input("Tiempo de viudez", value="" if st.session_state['tiempo_viuda'] is None else st.session_state['tiempo_viuda'])
if tiempo_viuda and (not tiempo_viuda.isdigit() or len(tiempo_viuda) > 2):
    st.warning("⚠️ Solo se permiten números de hasta 2 dígitos.")
    
causas = [
    "ACCIDENTE", "ENFERMEDAD", "INFARTO FULMINANTE",
    "NEGLIGENCIA MEDICA", "SUICIDIO", "VIOLENCIA", "OTRA"
]
causa_fallecimiento = st.selectbox("Causa de fallecimiento", causas)

hijos_menores = st.radio("¿Tiene hijas/os menores?", ["Sí", "No"])
telefono = st.text_input("Teléfono", value=st.session_state['telefono'] or "")
if telefono and not telefono.isdigit():
    st.warning("⚠️ El teléfono solo debe contener números.")
    
observaciones = st.text_area("Observaciones", value=st.session_state['observaciones'] or "")

edades_hijos = st.text_input("Edades de los hijos (separadas por comas)", value=st.session_state['edades_hijos'] or "")
if edades_hijos:
    try:
        edades = [int(e.strip()) for e in edades_hijos.split(",")]
    except ValueError:
        st.warning("⚠️ Ingresa solo números separados por comas. Ej: 5, 8, 12")

causa_muerte = st.text_input("Causa de muerte", value=st.session_state['causa_muerte'] or "")

# Fecha
fecha_muerte = st.date_input(
    "Fecha de fallecimiento",
    value=st.session_state['fecha_muerte'] or datetime.today(),
    min_value=datetime(1900, 1, 1),
    max_value=datetime.today()
)

ayuda_solicita = st.text_area("¿Qué ayuda solicita?", value=st.session_state['ayuda_solicita'] or "")
st.text_input("Rango de edad", value=rango_edad, disabled=True)

# Selectbox de perfil
perfil_cirineas = st.selectbox("Perfil Cirineas", ["Sí", "No"], index=0 if st.session_state['perfil_cirineas'] == "Sí" else 1)

# Checkboxes
prioridad_zapopan = st.checkbox("¿Prioridad Zapopan?", value=st.session_state['prioridad_zapopan'] or False)
atencion_psicologica = st.checkbox("Atención psicológica", value=st.session_state['atencion_psicologica'] or False)
apoyo_economico = st.checkbox("Apoyo económico", value=st.session_state['apoyo_economico'] or False)
apoyo_hijos = st.checkbox("Apoyo para hijas/os", value=st.session_state['apoyo_hijos'] or False)

st.session_state['folio'] = folio
st.session_state['edad'] = edad
st.session_state['tiempo_viuda'] = tiempo_viuda
st.session_state['causa_fallecimiento'] = causa_fallecimiento
st.session_state['hijos_menores'] = hijos_menores
st.session_state['telefono'] = telefono
st.session_state['observaciones'] = observaciones
st.session_state['edades_hijos'] = edades_hijos
st.session_state['causa_muerte'] = causa_muerte
st.session_state['fecha_muerte'] = fecha_muerte
st.session_state['ayuda_solicita'] = ayuda_solicita
st.session_state['rango_edad'] = rango_edad
st.session_state['perfil_cirineas'] = perfil_cirineas
st.session_state['prioridad_zapopan'] = prioridad_zapopan
st.session_state['atencion_psicologica'] = atencion_psicologica
st.session_state['apoyo_economico'] = apoyo_economico
st.session_state['apoyo_hijos'] = apoyo_hijos

# ---------- Guardar entrada ---------- #
if st.button("Agregar registro"):
    if folio.strip() == "":
        st.error("⚠️ El campo 'Folio' es obligatorio.")
    elif not df_capturas.empty and folio in df_capturas['FOLIO'].astype(str).values:
        st.warning("⚠️ Ya existe una entrada con ese folio.")
    else:
        nueva_fila = pd.DataFrame([{
            'FOLIO': folio.strip(),
            'EDAD': edad,
            'CP': cp,
            'COLONIA': colonia,
            'MUNICIPIO': municipio,
            'T_VIUDA': tiempo_viuda,
            'CAUS_FALL': causa_fallecimiento,
            'HIJ_MEN': hijos_menores,
            'TEL': telefono,
            'OBSERV': observaciones,
            'EDADES_HIJ': edades_hijos,
            'CAUS_MUERTE': causa_muerte,
            'FECHA_MUERTE': fecha_muerte,
            'AYUDA_SOL': ayuda_solicita,
            'RANGO_EDAD': rango_edad,
            'PRIORIDAD_ZAPOPAN': prioridad_zapopan,
            'PERFIL_CIRINEAS': perfil_cirineas,
            'ATENCION_PSICO': atencion_psicologica,
            'APOYO_ECONOMICO': apoyo_economico,
            'APOYO_HIJOS': apoyo_hijos
        }])
        df_capturas = pd.concat([df_capturas, nueva_fila], ignore_index=True)
        st.session_state['archivo_cargado'] = df_capturas
        st.success("✅ Registro agregado.")
        st.session_state["form_reset"] = True
        st.rerun()

        # Limpiar campos
        for k in ['folio', 'edad', 'tiempo_viuda', 'causa_fallecimiento', 'hijos_menores',
                  'telefono', 'observaciones', 'edades_hijos', 'causa_muerte', 'fecha_muerte',
                  'ayuda_solicita', 'rango_edad', 'prioridad_zapopan', 'perfil_cirineas',
                  'atencion_psicologica', 'apoyo_economico', 'apoyo_hijos']:
            st.session_state[k] = None

        st.rerun()

# ---------- Descargar archivo actualizado ---------- #
if not df_capturas.empty:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_capturas.to_excel(writer, index=False)
    st.download_button(
        label="📥 Descargar archivo actualizado",
        data=buffer,
        file_name=f"capturas_actualizadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )