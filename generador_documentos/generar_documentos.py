import pandas as pd
from docxtpl import DocxTemplate
import os

# --- CONFIGURACIÓN DE ARCHIVOS ---
ARCHIVO_EXCEL = 'datos_profes.xlsx'
PLANTILLA_1 = 'Plantilla_Ejecucion.docx'
PLANTILLA_2 = 'Plantilla_Labor.docx'
CARPETA_SALIDA = 'Informes_Generados'

# Crear carpeta de salida si no existe
if not os.path.exists(CARPETA_SALIDA):
    os.makedirs(CARPETA_SALIDA)

# Leer el archivo Excel
print(f"Leyendo datos desde {ARCHIVO_EXCEL}...")
df = pd.read_excel(ARCHIVO_EXCEL)

# Asegurar que los datos como RUT o Convenio se traten como texto
df = df.astype(str)

for index, row in df.iterrows():
    nombre_profe = row['Nombre']
    print(f"Generando informes para: {nombre_profe}")

    # Convertir la fila del Excel en un diccionario para la plantilla
    # Las llaves de este diccionario deben coincidir EXACTAMENTE con lo que pusiste entre {{ }} en el Word
    contexto = {
        'Nombre': row['Nombre'],
        'RUT': row['RUT'],
        'N_Convenio': row['N_Convenio'],
        'Ano_Convenio': row['Ano_Convenio'],
        'N_Solicitud': row['N_Solicitud'],
        'Fecha_Inicio': row['Fecha_Inicio'],
        'Fecha_Termino': row['Fecha_Termino'],
        'Monto_Numeros': row['Monto_Numeros'],
        'Monto_Palabras': row['Monto_Palabras'],
        'Horas_Totales': row['Horas_Totales'],
        'Horas_Lectivas': row['Horas_Lectivas'],
        'Horas_No_Lectivas': row['Horas_No_Lectivas'],
        'Fecha_Emision': row['Fecha_Emision'],
        'Labor_1': row['Labor_1'],
        'Labor_2': row['Labor_2']
    }

    # --- GENERAR INFORME 1 ---
    doc_1 = DocxTemplate(PLANTILLA_1)
    doc_1.render(contexto)
    nombre_archivo_1 = f"1_Ejecucion_{nombre_profe.replace(' ', '_')}.docx"
    doc_1.save(os.path.join(CARPETA_SALIDA, nombre_archivo_1))

    # --- GENERAR INFORME 2 ---
    doc_2 = DocxTemplate(PLANTILLA_2)
    doc_2.render(contexto)
    nombre_archivo_2 = f"2_Labor_{nombre_profe.replace(' ', '_')}.docx"
    doc_2.save(os.path.join(CARPETA_SALIDA, nombre_archivo_2))

print(f"\n¡Proceso terminado exitosamente! Los archivos con el formato institucional están en la carpeta '{CARPETA_SALIDA}'.")