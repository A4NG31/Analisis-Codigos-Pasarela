import streamlit as st
import pandas as pd
import io

# Configuración de la página
st.set_page_config(
    page_title="TRR Monitoreo Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Códigos disponibles
CODIGOS_DISPONIBLES = [100, 102, 150, 151, 202, 203, 204, 205, 208, 210, 211, 231, 233, 244, 246, 251, 481]

def procesar_archivo(df_completo, codigos_seleccionados):
    """
    Procesa DataFrame normalizando OverallReasonCode (quita .0 y espacios)
    y crea hojas filtradas + pivot consistente.
    """
    resultados = {}
    datos_copy = df_completo.copy()
    resultados['datos_completos'] = datos_copy.copy()

    if 'OverallReasonCode' not in datos_copy.columns:
        st.error("❌ No se encontró la columna 'OverallReasonCode' en el archivo")
        return None

    # Normalizar: "481.0" -> "481", remove spaces
    df_proc = datos_copy.copy()
    df_proc['_orc_norm'] = df_proc['OverallReasonCode'].astype(str).str.strip().replace(r'\.0+$', '', regex=True)

    # Hojas filtradas (sin la columna auxiliar)
    for codigo in codigos_seleccionados:
        mask = df_proc['_orc_norm'] == str(codigo)
        resultados[f'codigo_{codigo}'] = df_proc[mask].drop(columns=['_orc_norm']).copy()

    # Pivot usando la columna normalizada
    if 'RequestID' in df_proc.columns:
        pivot_data = df_proc.groupby('_orc_norm')['RequestID'].count().reset_index()
        pivot_data.columns = ['OverallReasonCode', 'Count']
    else:
        pivot_data = df_proc.groupby('_orc_norm').size().reset_index()
        pivot_data.columns = ['OverallReasonCode', 'Count']

    pivot_data['Count'] = pivot_data['Count'].astype(int)
    pivot_data['Percentage'] = (pivot_data['Count'] / pivot_data['Count'].sum()) * 100
    pivot_data['Percentage'] = pivot_data['Percentage'].round(2)

    total_row = pd.DataFrame({
        'OverallReasonCode': ['Total'],
        'Count': [pivot_data['Count'].sum()],
        'Percentage': [100.00]
    })
    pivot_data = pd.concat([pivot_data, total_row], ignore_index=True)

    resultados['pivot_table'] = pivot_data
    return resultados


def crear_excel_descarga(resultados, codigos_seleccionados):
    """
    Crea un archivo Excel en memoria para descargar usando xlsxwriter
    (corrige la doble escritura de la hoja Resumen_Pivot).
    """
    output = io.BytesIO()

    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # 1) Hojas de datos
            resultados['datos_completos'].to_excel(
                writer, sheet_name='Datos_Completos', index=False
            )
            for codigo in codigos_seleccionados:
                key = f'codigo_{codigo}'
                if key in resultados:
                    resultados[key].to_excel(
                        writer, sheet_name=f'Codigo_{codigo}', index=False
                    )

            # 2) Hoja de Resumen (escritura manual, sin to_excel)
            pivot_df = resultados['pivot_table'].copy()
            workbook = writer.book
            sheet_name = 'Resumen_Pivot'
            worksheet = workbook.add_worksheet(sheet_name)
            writer.sheets[sheet_name] = worksheet

            # --- Formatos ---
            header_format = workbook.add_format({
                'bold': True, 'text_wrap': True, 'valign': 'top',
                'fg_color': '#00F214', 'border': 1, 'border_color': '#000000'
            })
            data_text = workbook.add_format({'border': 1, 'border_color': '#000000'})
            data_int  = workbook.add_format({'border': 1, 'border_color': '#000000',
                                             'num_format': '#,##0'})
            data_num2 = workbook.add_format({'border': 1, 'border_color': '#000000',
                                             'num_format': '0.00'})
            total_format = workbook.add_format({
                'bold': True, 'fg_color': '#00F214',
                'border': 1, 'border_color': '#000000'
            })

            # --- Encabezados ---
            for col_num, col_name in enumerate(pivot_df.columns):
                worksheet.write(0, col_num, col_name, header_format)

            # --- Datos ---
            # Espera columnas: ['OverallReasonCode', 'Count', 'Percentage']
            for r, (_, row) in enumerate(pivot_df.iterrows(), start=1):
                if row['OverallReasonCode'] == 'Total':
                    worksheet.write(r, 0, row['OverallReasonCode'], total_format)
                    worksheet.write_number(r, 1, float(row['Count']), total_format)
                    worksheet.write_number(r, 2, float(row['Percentage']), total_format)
                else:
                    worksheet.write(r, 0, row['OverallReasonCode'], data_text)
                    # asegura numéricos
                    cnt = int(row['Count']) if pd.notna(row['Count']) else 0
                    pct = float(row['Percentage']) if pd.notna(row['Percentage']) else 0.0
                    worksheet.write_number(r, 1, cnt, data_int)
                    # Percentage en 0–100 (dos decimales)
                    worksheet.write_number(r, 2, pct, data_num2)

            # Ancho de columnas, filtro y panes
            worksheet.set_column('A:A', 20)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 15)
            worksheet.autofilter(0, 0, len(pivot_df), len(pivot_df.columns) - 1)
            worksheet.freeze_panes(1, 0)

        output.seek(0)
        return output.getvalue()

    except Exception as e:
        st.error(f"Error al crear archivo Excel: {str(e)}")
        return None

def crear_visualizaciones(pivot_data):
    """
    Crea visualizaciones usando componentes nativos de Streamlit
    """
    # Filtrar datos sin el total
    data_sin_total = pivot_data[pivot_data['OverallReasonCode'] != 'Total'].copy()
    
    if len(data_sin_total) > 0:
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.subheader("📊 Distribución por Código")
            chart_data = data_sin_total.set_index('OverallReasonCode')['Count']
            st.bar_chart(chart_data, height=400)
        
        with col2:
            st.subheader("📈 Detalles por Código")
            
            # --- CSS para métricas más compactas ---
            st.markdown("""
            <style>
            div[data-testid="stMetric"] {
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 10px;
                background-color: #f9f9f9;
                margin: 4px;
            }
            div[data-testid="stMetric"] > label {
                font-size: 0.85rem !important;
            }
            div[data-testid="stMetric"] > div {
                font-size: 1rem !important;
                font-weight: 600 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Mostrar métricas en un grid de 3 columnas
            cols = st.columns(3)
            for i, (_, row) in enumerate(data_sin_total.iterrows()):
                with cols[i % 3]:
                    st.metric(
                        label=f"Código {row['OverallReasonCode']}",
                        value=f"{row['Count']}",
                        delta=f"{row['Percentage']:.1f}%"
                    )
    else:
        st.warning("No hay datos para mostrar en gráficos")

def main():
    # Título principal
    st.title("📊 TRR Monitoreo Daily Analyzer")
    st.markdown("---")
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Carga de archivo
        st.subheader("📁 Cargar Archivo")
        uploaded_file = st.file_uploader(
            "Selecciona tu archivo CSV",
            type=['csv'],
            help="Sube el archivo TRR_Monitoreo_Daily.csv"
        )
        
        # Selección de códigos
        st.subheader("🔍 Códigos a Filtrar")
        codigos_seleccionados = st.multiselect(
            "Selecciona los códigos a analizar:",
            options=CODIGOS_DISPONIBLES,
            default=[481],
            help="Puedes seleccionar múltiples códigos para crear hojas separadas"
        )
        
        # Opciones adicionales
        st.subheader("📋 Opciones")
        saltar_primera_fila = st.checkbox("Saltar primera fila", value=True)
        mostrar_visualizaciones = st.checkbox("Mostrar visualizaciones", value=True)
    
    # Contenido principal
    if uploaded_file is not None:
        try:
            # Mostrar información del archivo
            st.success(f"✅ Archivo cargado: {uploaded_file.name}")
            
            # Cargar datos
            with st.spinner("📥 Cargando datos..."):
                skip_rows = 1 if saltar_primera_fila else 0
                df_completo = pd.read_csv(uploaded_file, sep=',', skiprows=skip_rows)
            
            st.info(f"📈 Datos cargados: {df_completo.shape[0]} filas, {df_completo.shape[1]} columnas")
            
            # Mostrar preview de los datos
            with st.expander("👀 Vista previa de los datos (primeras 5 filas)"):
                st.dataframe(df_completo.head())
            
            # Verificar que existe la columna necesaria
            if 'OverallReasonCode' not in df_completo.columns:
                st.error("❌ Error: No se encontró la columna 'OverallReasonCode' en el archivo")
                st.info("Columnas disponibles: " + ", ".join(df_completo.columns.tolist()))
                return
            
            # Procesar datos si hay códigos seleccionados
            if codigos_seleccionados:
                with st.spinner("⚙️ Procesando datos..."):
                    resultados = procesar_archivo(df_completo, codigos_seleccionados)
                
                if resultados:
                    # Mostrar resumen
                    st.subheader("📋 Resumen del Análisis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total de Registros", len(resultados['datos_completos']))
                    
                    with col2:
                        total_filtrados = sum([len(resultados[f'codigo_{codigo}']) for codigo in codigos_seleccionados if f'codigo_{codigo}' in resultados])
                        st.metric("Registros Filtrados", total_filtrados)
                    
                    with col3:
                        st.metric("Códigos Únicos", len(resultados['pivot_table']) - 1)  # -1 por el total
                    
                    # Mostrar detalles por código
                    st.subheader("🔍 Detalles por Código Seleccionado")
                    for codigo in codigos_seleccionados:
                        if f'codigo_{codigo}' in resultados:
                            cantidad = len(resultados[f'codigo_{codigo}'])
                            porcentaje = (cantidad / len(resultados['datos_completos'])) * 100
                            st.write(f"**Código {codigo}:** {cantidad} registros ({porcentaje:.2f}%)")
                    
                    # Tabla dinámica
                    st.subheader("📊 Tabla Dinámica - Resumen General")
                    st.dataframe(
                        resultados['pivot_table'], 
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Visualizaciones
                    if mostrar_visualizaciones:
                        st.subheader("📈 Visualizaciones")
                        crear_visualizaciones(resultados['pivot_table'])
                    
                    # Botón de descarga
                    st.subheader("💾 Descargar Análisis")
                    
                    with st.spinner("📦 Preparando archivo Excel..."):
                        excel_data = crear_excel_descarga(resultados, codigos_seleccionados)
                    
                    if excel_data is not None:
                        st.download_button(
                            label="📥 Descargar Análisis Completo (Excel)",
                            data=excel_data,
                            file_name=f"TRR_Monitoreo_Analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            help="Descarga el archivo Excel con todas las hojas: datos completos, códigos filtrados y tabla dinámica"
                        )
                        
                        # Información adicional
                        with st.expander("ℹ️ Información del Archivo Excel"):
                            st.write("**El archivo Excel contiene las siguientes hojas:**")
                            st.write("- 📋 **Datos_Completos:** Todos los datos originales")
                            for codigo in codigos_seleccionados:
                                cantidad = len(resultados[f'codigo_{codigo}']) if f'codigo_{codigo}' in resultados else 0
                                st.write(f"- 🔍 **Codigo_{codigo}:** {cantidad} registros filtrados")
                            st.write("- 📊 **Resumen_Pivot:** Tabla dinámica con formato y colores")
                    else:
                        st.error("❌ No se pudo generar el archivo Excel para descarga")
            else:
                st.warning("⚠️ Selecciona al menos un código para procesar")
                
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")
            st.exception(e)
    
    else:
        # Página de bienvenida
        st.markdown("""
        ## 👋 Bienvenido al Analizador de Monitoreo TRR
        
        Esta aplicación te permite analizar archivos CSV de monitoreo diario TRR con las siguientes funcionalidades:
        
        ### 🚀 Características principales:
        - 📁 **Carga de archivos:** Sube tu archivo CSV directamente
        - 🔍 **Filtrado personalizado:** Selecciona los códigos específicos que deseas analizar
        - 📊 **Tabla dinámica:** Visualiza un resumen completo con conteos y porcentajes
        - 📈 **Visualizaciones:** Gráficos de barras y métricas individuales
        - 💾 **Descarga Excel:** Obtén un archivo completo con formato profesional
        
        ### 📋 Códigos disponibles:
        `100, 102, 150, 151, 202, 203, 204, 205, 208, 210, 211, 231, 233, 244, 246, 251, 481`
        
        ### 🛠️ Para comenzar:
        1. Carga tu archivo CSV en la barra lateral
        2. Selecciona los códigos que deseas analizar
        3. Revisa los resultados y visualizaciones
        4. Descarga el análisis completo en Excel
        
        ---
        💡 **Tip:** Puedes seleccionar múltiples códigos para crear hojas separadas de cada uno en el archivo Excel final.
        """)

if __name__ == "__main__":
    main()
