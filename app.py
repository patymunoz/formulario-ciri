import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

# ---------- Inicializar estado de sesión ---------- #
for key in [
    'folio','nombre', 'primer_apellido', 'segundo_apellido', 
    'edad', 'rango_edad', 'causa_fallecimiento', 'dia_fallecimiento', 
    'mes_fallecimiento', 'anio_fallecimiento', 'hijos_menores', 'numero_hijos_menores', 
    'telefono', 'circulo_restaurativo', 'primera_derivacion', 'curp', 'cp', 'colonia', 'municipio', 'archivo_cargado',
    'apoyo_legal', 'apoyo_economico', 'apoyo_hijos',
    'apoyo_gastos_funerarios', 'apoyo_salud'
]:
    if key not in st.session_state:
        st.session_state[key] = None

# ---------- Título ---------- #
st.title("Formulario de registro - Cirineas")

# --------- Limpiar formulario si se acaba de guardar --------- #
if st.session_state.get("form_reset") is True:
    for k in ['folio','nombre', 'primer_apellido', 'segundo_apellido', 
              'edad', 'rango_edad', 'causa_fallecimiento', 'dia_fallecimiento', 
              'mes_fallecimiento', 'anio_fallecimiento', 'hijos_menores', 'numero_hijos_menores', 
              'telefono', 'circulo_restaurativo', 'primera_derivacion', 'curp', 'cp', 'colonia', 'municipio'
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

# FOLIO
folio = st.text_input("Folio *", value="" if st.session_state['folio'] is None else st.session_state['folio'])
if folio.strip() == "":
    st.error("⚠️ El campo 'Folio' es obligatorio.")

nombre = st.text_input("Nombre(s)", value=st.session_state.get("nombre", ""))
primer_apellido = st.text_input("Primer apellido", value=st.session_state.get("primer_apellido", ""))
segundo_apellido = st.text_input("Segundo apellido", value=st.session_state.get("segundo_apellido", ""))

# EDAD
edad = st.number_input("Edad", min_value=0, max_value=120, value=st.session_state.get("edad") or 0)

# Fx para calcular rango edad
def calcular_rango_edad(edad):
    if edad < 19:
        return "menos de 19"
    elif 20 <= edad <= 29:
        return "22-29"
    elif 30 <= edad <= 39:
        return "30 a 39"
    elif 40 <= edad <= 49:
        return "40 a 49"
    elif 50 <= edad <= 59:
        return "50 a 59"
    elif 60 <= edad <= 64:
        return "60 a 64"
    elif edad >= 65:
        return "65 y más"
    return "Sin dato"

rango_edad = calcular_rango_edad(edad)
st.text_input("Rango de edad", value=rango_edad, disabled=True)

# CAUSA_FALL
causas = [
    "ACCIDENTE", "ENFERMEDAD", "INFARTO FULMINANTE",
    "NEGLIGENCIA MEDICA", "SUICIDIO", "VIOLENCIA", "DESCONOCIDA"
]
causa_fallecimiento = st.selectbox("Causa de fallecimiento", causas)

# DIA | MES | AÑO DE FALLECIMIENTO (DIA_FALL, MES_FALL, ANIO_FALL)
dia_fallecimiento = st.text_input("Día de fallecimiento (DD)", value=st.session_state.get("dia_fallecimiento", ""))
if dia_fallecimiento and (not dia_fallecimiento.isdigit() or len(dia_fallecimiento) != 2 or not (1 <= int(dia_fallecimiento) <= 31)):
    st.warning("⚠️ Ingresa un día válido en formato de dos dígitos (01-31)")

mes_fallecimiento = st.text_input("Mes de fallecimiento (MM)", value=st.session_state.get("mes_fallecimiento", ""))
if mes_fallecimiento and (not mes_fallecimiento.isdigit() or len(mes_fallecimiento) != 2 or not (1 <= int(mes_fallecimiento) <= 12)):
    st.warning("⚠️ Ingresa un mes válido en formato de dos dígitos (01-12)")

anio_fallecimiento = st.text_input("Año de fallecimiento (AAAA)", value=st.session_state.get("anio_fallecimiento", ""))
año_actual = datetime.today().year
if anio_fallecimiento and (not anio_fallecimiento.isdigit() or len(anio_fallecimiento) != 4 or not (1900 <= int(anio_fallecimiento) <= año_actual)):
    st.warning(f"⚠️ Ingresa un año válido entre 1900 y {año_actual}")

# NUM_HMD
hijos_menores = st.radio("¿Tiene hijas/os menores de edad?", ["Sí", "No"])
cuantos_hijos = st.number_input(
    "¿Cuántos?", 
    min_value=0, 
    max_value=10, 
    value=st.session_state.get("numero_hijos_menores") or 0
)

# TEL
telefono = st.text_input("Teléfono", value=st.session_state.get("telefono", ""))
if telefono and not telefono.isdigit():
    st.warning("⚠️ El teléfono solo debe contener números.")

# CIR_REST
circulo_restaurativo = st.selectbox("Círculo restaurativo", ["Sí", "No"], index=0 if st.session_state.get("circulo_restaurativo") == "Sí" else 1)

# PRI_DERIV
opciones_derivacion = ["Zapopan", "Guadalajara", "Tonalá", "San Pedro Tlaquepaque", "El Salto", "Tlajomulco de Zúñiga", "Cirineas", "Centro de Justicia para las Mujeres"]
indice_derivacion = opciones_derivacion.index(st.session_state.get("primera_derivacion", "Zapopan")) if st.session_state.get("primera_derivacion") in opciones_derivacion else 0
primera_derivacion = st.selectbox("Primera derivación", opciones_derivacion, index=indice_derivacion)

# CP | COLONIA | MUNICIPIO
cp = st.selectbox("Código Postal", sorted(df_control['CP'].unique()))
colonias = sorted(df_control[df_control['CP'] == cp]['COLONIA'].unique())
colonia = st.selectbox("Colonia", colonias)
municipio = df_control[(df_control['CP'] == cp) & (df_control['COLONIA'] == colonia)]['MUNICIPIO'].values[0]
st.text_input("Municipio", value=municipio, disabled=True)

# curp
curp = st.text_input("CURP", value=st.session_state.get("curp", ""))

# apoyos

st.markdown("### Apoyos requeridos")

apoyo_legal = st.checkbox("Requiere apoyo legal", value=st.session_state['apoyo_legal'])
apoyo_economico = st.checkbox("Requiere apoyo económico", value=st.session_state['apoyo_economico'])
apoyo_hijos = st.checkbox("Requiere apoyo para sus hijos", value=st.session_state['apoyo_hijos'])
apoyo_gastos_funerarios = st.checkbox("Requiere apoyo para Gastos Funerarios", value=st.session_state['apoyo_gastos_funerarios'])
apoyo_salud = st.checkbox("Requiere apoyo para temas de Salud", value=st.session_state['apoyo_salud'])

# Curps hijxs menores

curps_hijxs = []

if hijos_menores == "Sí" and cuantos_hijos > 0:
    st.markdown("#### CURP de hijas/os menores")
    for i in range(1, cuantos_hijos + 1):
        curp = st.text_input(f"CURP de la hija/o #{i}", key=f"curp_hijo_{i}")
        curps_hijxs.append(curp)


# Fecha
#fecha_muerte = st.date_input(
#    "Fecha de fallecimiento",
#    value=st.session_state['fecha_muerte'] or datetime.today(),
#    min_value=datetime(1900, 1, 1),
#    max_value=datetime.today()
#)

st.session_state['folio'] = folio
st.session_state['nombre'] = nombre
st.session_state['primer_apellido'] = primer_apellido
st.session_state['segundo_apellido'] = segundo_apellido
st.session_state['edad'] = edad
st.session_state['rango_edad'] = rango_edad
st.session_state['causa_fallecimiento'] = causa_fallecimiento
st.session_state['dia_fallecimiento'] = dia_fallecimiento
st.session_state['mes_fallecimiento'] = mes_fallecimiento
st.session_state['anio_fallecimiento'] = anio_fallecimiento
st.session_state['hijos_menores'] = hijos_menores
st.session_state['numero_hijos_menores'] = cuantos_hijos
st.session_state['telefono'] = telefono
st.session_state['circulo_restaurativo'] = circulo_restaurativo
st.session_state['primera_derivacion'] = primera_derivacion
st.session_state['curp'] = curp
st.session_state['apoyo_legal'] = apoyo_legal
st.session_state['apoyo_economico'] = apoyo_economico
st.session_state['apoyo_hijos'] = apoyo_hijos
st.session_state['apoyo_gastos_funerarios'] = apoyo_gastos_funerarios
st.session_state['apoyo_salud'] = apoyo_salud
st.session_state['curps_hijos'] = curps_hijxs

# ---------- Guardar entrada ---------- #
if st.button("Agregar registro"):
    if folio.strip() == "":
        st.error("⚠️ El campo 'Folio' es obligatorio.")
    elif not df_capturas.empty and folio in df_capturas['FOLIO'].astype(str).values:
        st.warning("⚠️ Ya existe una entrada con ese folio.")
    else:
        # Crear el diccionario de CURPs (hasta 10 si deseas)
        curps_dict = {
            f"CURP_HIJO_{i+1}": curps_hijxs[i] if i < len(curps_hijxs) else ""
            for i in range(6)
        }

        nueva_fila = pd.DataFrame([{
            'FOLIO': folio.strip(),
            'NOMBRE': nombre,
            'APELLIDO1': primer_apellido,
            'APELLIDO2': segundo_apellido,
            'EDAD': edad,
            'RANGO_EDAD': rango_edad,
            'CAUSA_FALL': causa_fallecimiento,
            'DIA_FALL': dia_fallecimiento,
            'MES_FALL': mes_fallecimiento,
            'ANIO_FALL': anio_fallecimiento,
            'NUM_HMD': cuantos_hijos,
            'TEL': telefono,
            'CIRC_REST': circulo_restaurativo,
            'PRI_DERIV': primera_derivacion,
            'CP': cp,
            'COLONIA': colonia,
            'NOM_MUN': municipio,
            'CURP': curp,
            'APOYO_LEGAL': apoyo_legal,
            'APOYO_ECONOMICO': apoyo_economico,
            'APOYO_HIJOS': apoyo_hijos,
            'APOYO_FUNERARIOS': apoyo_gastos_funerarios,
            'APOYO_SALUD': apoyo_salud,
            **curps_dict  
        }])

        df_capturas = pd.concat([df_capturas, nueva_fila], ignore_index=True)
        st.session_state['archivo_cargado'] = df_capturas
        st.success("✅ Registro agregado.")

        st.session_state["form_reset"] = True
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