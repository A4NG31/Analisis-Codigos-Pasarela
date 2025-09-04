# 📊 TRR Monitoreo Daily Analyzer

Una aplicación web desarrollada con Streamlit para analizar archivos CSV de monitoreo diario TRR de forma interactiva y eficiente.

## 🚀 Características

- **📁 Carga de archivos:** Interfaz intuitiva para subir archivos CSV
- **🔍 Filtrado personalizado:** Selecciona códigos específicos para análisis detallado
- **📊 Tabla dinámica:** Resumen automático con conteos y porcentajes
- **📈 Visualizaciones:** Gráficos interactivos (barras y torta) con Plotly
- **💾 Exportación Excel:** Descarga análisis completo con formato profesional
- **🎨 Formato automático:** Colores y bordes aplicados automáticamente

## 🛠️ Instalación

### Requisitos previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Instalación paso a paso

1. **Clona el repositorio:**
```bash
git clone https://github.com/tu-usuario/trr-monitoreo-analyzer.git
cd trr-monitoreo-analyzer
```

2. **Crea un entorno virtual (recomendado):**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

4. **Ejecuta la aplicación:**
```bash
streamlit run app.py
```

5. **Abre tu navegador en:** `http://localhost:8501`

## 📋 Códigos Disponibles

La aplicación soporta el filtrado y análisis de los siguientes códigos:

```
100, 102, 150, 151, 202, 203, 204, 205, 208, 210, 211, 231, 233, 244, 246, 251, 481
```

## 🎯 Uso

### 1. Carga de Archivo
- Utiliza la barra lateral para cargar tu archivo CSV
- La aplicación automáticamente detecta y procesa los datos
- Opción para saltar la primera fila si contiene metadatos

### 2. Selección de Códigos
- Selecciona uno o múltiples códigos de la lista disponible
- Cada código seleccionado generará una hoja separada en el Excel final
- Por defecto viene seleccionado el código 481

### 3. Análisis y Visualización
- **Vista previa:** Primeras 5 filas de los datos cargados
- **Métricas:** Total de registros, registros filtrados, códigos únicos
- **Tabla dinámica:** Resumen completo con conteos y porcentajes
- **Gráficos:** Visualizaciones interactivas opcionales

### 4. Descarga de Resultados
- Genera automáticamente un archivo Excel con:
  - Hoja de datos completos originales
  - Hojas separadas para cada código filtrado
  - Tabla dinámica con formato profesional (colores y bordes)

## 📁 Estructura del Proyecto

```
trr-monitoreo-analyzer/
│
├── app.py                 # Aplicación principal Streamlit
├── requirements.txt       # Dependencias del proyecto
├── README.md             # Documentación
└── .gitignore           # Archivos a ignorar por Git
```

## 🔧 Estructura del Archivo Excel Generado

### Hojas incluidas:
1. **Datos_Completos:** Todos los datos originales sin filtrar
2. **Codigo_XXX:** Una hoja por cada código seleccionado con registros filtrados
3. **Resumen_Pivot:** Tabla dinámica con formato profesional

### Formato aplicado:
- ✅ Encabezados con fondo verde oscuro (#00F214)
- ✅ Datos con fondo blanco
- ✅ Fila de totales con fondo verde oscuro
- ✅ Bordes negros en todas las celdas

## 🚀 Despliegue

### Streamlit Cloud
1. Sube tu código a GitHub
2. Conecta tu repositorio en [Streamlit Cloud](https://streamlit.io/cloud)
3. La aplicación se desplegará automáticamente

### Heroku
1. Crea un `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Despliega siguiendo la documentación de Heroku

## 🤝 Contribución

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Angel Torres**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)

## 🙏 Reconocimientos

- Streamlit por el framework de aplicaciones web
- Plotly por las visualizaciones interactivas
- Pandas por el procesamiento de datos
- OpenPyXL por la manipulación de archivos Excel

---

⭐ **Si este proyecto te fue útil, considera darle una estrella en GitHub**