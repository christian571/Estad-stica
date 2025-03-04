import pandas as pd

ruta_archivo = r"C:\Users\cristian\Downloads\loreto.xlsx"

try:
    df = pd.read_excel(ruta_archivo, engine="openpyxl", header=None)  # Leer sin encabezado
    print("✅ Vista previa del archivo:\n")
    print(df.head(20))  # Mostrar las primeras 20 filas para encontrar la fila correcta
except Exception as e:
    print("❌ Error al leer el archivo:", str(e))
