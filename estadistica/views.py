from django.shortcuts import render
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io, base64
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from scipy.stats import skew, kurtosis

# 📌 Función para generar gráficos

def generar_grafico(numeros, tipo):
    if tipo == "tendencia":
        plt.figure(figsize=(14, 7))  # Tamaño más grande para el gráfico de tendencia
    elif tipo == "histograma":
        plt.figure(figsize=(12, 6))  # Tamaño más grande para el histograma
    elif tipo == "caja_bigote":
        plt.figure(figsize=(10, 6))   # Tamaño más grande para el gráfico de caja y bigote

    if tipo == "histograma":
        sns.histplot(numeros, kde=True, bins=10)
        plt.title("Histograma")
    elif tipo == "caja_bigote":
        sns.boxplot(y=numeros)
        plt.title("Gráfico de Caja y Bigote")
    elif tipo == "tendencia":
        plt.plot(numeros, marker='o', linestyle='-')
        plt.title("Gráfico de Tendencia")
        plt.xlabel("Índice")
        plt.ylabel("Valor")

    plt.tight_layout()

    # Guardar la imagen en base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    return imagen_base64

# 📌 API para calcular estadísticas de una lista de números
@api_view(['POST'])
def calcular_estadisticas(request):
    datos = request.data.get("numeros", [])

    if not datos:
        return Response({"error": "No se proporcionaron datos"}, status=400)

    try:
        numeros = np.array(datos, dtype=np.float64)
        media = np.mean(numeros)
        mediana = np.median(numeros)
        moda = pd.Series(numeros).mode().tolist()
        varianza = np.var(numeros, ddof=1)
        desviacion = np.std(numeros, ddof=1)
        sesgo = skew(numeros)
        curtosis = kurtosis(numeros)
        cuartiles = {
            "Q1": np.percentile(numeros, 25),
            "Q2": np.percentile(numeros, 50),
            "Q3": np.percentile(numeros, 75),
        }

        # Generar gráficos
        histograma = generar_grafico(numeros, "histograma")
        caja_bigote = generar_grafico(numeros, "caja_bigote")
        tendencia = generar_grafico(numeros, "tendencia")

        return Response({
            "media": media,
            "mediana": mediana,
            "moda": moda,
            "varianza": varianza,
            "desviacion_estandar": desviacion,
            "sesgo": sesgo,
            "curtosis": curtosis,
            "cuartiles": cuartiles,
            "graficos": {
                "histograma": histograma,
                "caja_bigote": caja_bigote,
                "tendencia": tendencia
            }
        })
    except Exception as e:
        print("Error en el servidor:", e) 
        return Response({"error": str(e)}, status=400)

# 📌 Rutas para las páginas web
def index(request):
    return render(request, 'estadistica/index.html')

def pagina_calculadora(request):
    return render(request, 'estadistica/calculadora.html')

def pagina_radiacion(request):
    return render(request, 'estadistica/radiacion.html')

def pagina_ayuda(request):
    return render(request, 'estadistica/ayuda.html')
# 📌 API para calcular radiación desde un archivo Excel

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def calcular_radiacion(request):
    print("📥 Archivos recibidos:", request.FILES)

    if 'archivoExcel' not in request.FILES:
        print("❌ No se ha recibido un archivo válido")
        return Response({"error": "No se ha proporcionado un archivo"}, status=400)

    archivo = request.FILES['archivoExcel']
    print("📂 Nombre del archivo:", archivo.name)

    if not archivo.name.endswith('.xlsx'):
        print("❌ Formato de archivo inválido")
        return Response({"error": "Solo se permiten archivos en formato .xlsx"}, status=400)

    try:
        # 1️⃣ Verificar si el archivo tiene hojas de cálculo
        archivo.seek(0)
        with pd.ExcelFile(archivo, engine="openpyxl") as xls:
            if len(xls.sheet_names) == 0:
                print("❌ El archivo no tiene hojas de cálculo válidas.")
                return Response({"error": "El archivo no tiene hojas de cálculo válidas."}, status=400)

            # 2️⃣ Leer la primera hoja con el encabezado correcto
            df = pd.read_excel(xls, sheet_name=0, header=9)

        # 3️⃣ Verificar si el DataFrame está vacío
        if df.empty:
            print("❌ El archivo está vacío o mal formateado.")
            return Response({"error": "El archivo está vacío o tiene un formato incorrecto."}, status=400)

        # 4️⃣ Buscar la columna que contenga "Radiación"
        columna_radiacion = next((col for col in df.columns if "radiación" in col.lower()), None)

        if not columna_radiacion:
            print("❌ No se encontró la columna de Radiación")
            return Response({"error": "No se encontró una columna con 'Radiación' en el archivo."}, status=400)

        # 5️⃣ Convertir la columna a valores numéricos, reemplazar NaN e infinitos con 0
        df[columna_radiacion] = pd.to_numeric(df[columna_radiacion], errors='coerce').fillna(0).replace([np.inf, -np.inf], 0)
        radiacion = df[columna_radiacion].to_numpy()

        # 6️⃣ Calcular estadísticas
        media = np.mean(radiacion)
        mediana = np.median(radiacion)
        moda = pd.Series(radiacion).mode().tolist()
        varianza = np.var(radiacion, ddof=1)
        desviacion = np.std(radiacion, ddof=1)
        sesgo = skew(radiacion) if len(radiacion) > 2 else 0
        curtosis = kurtosis(radiacion) if len(radiacion) > 3 else 0
        cuartiles = {
            "Q1": np.percentile(radiacion, 25),
            "Q2": np.percentile(radiacion, 50),
            "Q3": np.percentile(radiacion, 75),
        }

        # 7️⃣ Generar gráficos
        histograma = generar_grafico(radiacion, "histograma")
        caja_bigote = generar_grafico(radiacion, "caja_bigote")
        tendencia = generar_grafico(radiacion, "tendencia")

        # 8️⃣ Preparar la respuesta
        response_data = {
            "radiacion_total": np.sum(radiacion),
            "radiacion_promedio": media,
            "media": media,
            "mediana": mediana,
            "moda": moda,
            "varianza": varianza,
            "desviacion_estandar": desviacion,
            "sesgo": sesgo,
            "curtosis": curtosis,
            "cuartiles": cuartiles,
            "datos_muestra": df.head().to_dict(orient="records"),
            "graficos": {
                "histograma": histograma,
                "caja_bigote": caja_bigote,
                "tendencia": tendencia
            }
        }

        # 9️⃣ Convertir datos a formatos estándar de Python
        def convertir_numpy_a_python(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj) if not np.isnan(obj) and not np.isinf(obj) else 0
            elif isinstance(obj, dict):
                return {k: convertir_numpy_a_python(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convertir_numpy_a_python(v) for v in obj]
            return obj

        response_data["datos_muestra"] = [
            {k: (None if pd.isna(v) else v) for k, v in fila.items()}
            for fila in response_data["datos_muestra"]
        ]

        response_data_python = convertir_numpy_a_python(response_data)

        print("📊 Respuesta final convertida:", response_data_python)
        return Response(response_data_python)

    except pd.errors.EmptyDataError:
        return Response({"error": "El archivo está vacío o no tiene datos válidos."}, status=400)
    except pd.errors.ParserError:
        return Response({"error": "El archivo tiene un formato no válido o está corrupto."}, status=400)
    except Exception as e:
        print("❌ Error procesando el archivo:", str(e))
        return Response({"error": f"No se pudo procesar el archivo. Verifica que el formato sea correcto ({str(e)})"}, status=400)