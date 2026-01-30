import pandas as pd
from datetime import time

def crear_calendario_curso(
    fecha_inicio="2026-03-16",  # lunes a mitad de marzo (puedes cambiarlo)
    numero_semanas=18,
    exportar_a="calendario_curso.xlsx"
):
    # Configuración fija por sección (día de la semana + horario)
    # día_semana: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
    secciones = {
        "Sección 1": {
            "teorica":   {"dia_semana": "Monday",    "horario_inicio": time(8, 30),  "horario_fin": time(10, 0)},
            "seminario": {"dia_semana": "Wednesday", "horario_inicio": time(10, 15), "horario_fin": time(11, 45)},
            "lab":       {"dia_semana": "Friday",    "horario_inicio": time(14, 0),  "horario_fin": time(16, 0)},
        },
        "Sección 2": {
            "teorica":   {"dia_semana": "Tuesday",   "horario_inicio": time(9, 0),   "horario_fin": time(10, 30)},
            "seminario": {"dia_semana": "Thursday",  "horario_inicio": time(11, 0),  "horario_fin": time(12, 30)},
            "lab":       {"dia_semana": "Friday",    "horario_inicio": time(8, 0),   "horario_fin": time(10, 0)},
        },
        "Sección 3": {
            "teorica":   {"dia_semana": "Monday",    "horario_inicio": time(14, 0),  "horario_fin": time(15, 30)},
            "seminario": {"dia_semana": "Wednesday", "horario_inicio": time(15, 45), "horario_fin": time(17, 15)},
            "lab":       {"dia_semana": "Saturday",  "horario_inicio": time(9, 0),   "horario_fin": time(11, 0)},
        },
        "Sección 4": {
            "teorica":   {"dia_semana": "Tuesday",   "horario_inicio": time(16, 0),  "horario_fin": time(17, 30)},
            "seminario": {"dia_semana": "Thursday",  "horario_inicio": time(17, 45), "horario_fin": time(19, 15)},
            "lab":       {"dia_semana": "Saturday",  "horario_inicio": time(12, 0),  "horario_fin": time(14, 0)},
        },
    }

    # Helpers
    dias_es = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }

    def combinar_fecha_hora(fecha_base, hora_inicio, hora_fin):
        # fecha_base es Timestamp (solo fecha)
        inicio = pd.Timestamp(fecha_base.date()) + pd.Timedelta(hours=hora_inicio.hour, minutes=hora_inicio.minute)
        fin    = pd.Timestamp(fecha_base.date()) + pd.Timedelta(hours=hora_fin.hour, minutes=hora_fin.minute)
        return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

    fecha_inicio = pd.Timestamp(fecha_inicio)
    semanas = range(1, numero_semanas + 1)

    filas = []
    for seccion, cfg in secciones.items():
        for semana in semanas:
            # Definimos el "ancla" de la semana: fecha_inicio + (semana-1)*7 días
            ancla_semana = fecha_inicio + pd.Timedelta(days=7 * (semana - 1))

            # 2 clases por semana: teórica + seminario
            for tipo_actividad, nombre_actividad in [
                ("teorica", "Clase teórica"),
                ("seminario", "Seminario")
            ]:
                dia_semana = cfg[tipo_actividad]["dia_semana"]
                fecha_evento = ancla_semana + pd.offsets.Week(weekday=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].index(dia_semana))

                horario = combinar_fecha_hora(
                    fecha_evento,
                    cfg[tipo_actividad]["horario_inicio"],
                    cfg[tipo_actividad]["horario_fin"]
                )

                filas.append({
                    "semana": semana,
                    "fecha": fecha_evento.date(),
                    "día": dias_es[dia_semana],
                    "horario": horario,
                    "sección": seccion,
                    "actividad": nombre_actividad,
                    "observaciones": ""
                })

            # Laboratorio cada 2 semanas (semanas pares: 2,4,6,...,18)
            if semana % 2 == 0:
                dia_semana = cfg["lab"]["dia_semana"]
                fecha_evento = ancla_semana + pd.offsets.Week(weekday=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].index(dia_semana))

                horario = combinar_fecha_hora(
                    fecha_evento,
                    cfg["lab"]["horario_inicio"],
                    cfg["lab"]["horario_fin"]
                )

                filas.append({
                    "semana": semana,
                    "fecha": fecha_evento.date(),
                    "día": dias_es[dia_semana],
                    "horario": horario,
                    "sección": seccion,
                    "actividad": "Laboratorio",
                    "observaciones": "Cada 2 semanas"
                })

    df = pd.DataFrame(filas)

    # Orden útil: por sección, semana y fecha/hora
    # Creamos una columna auxiliar de orden con Timestamp inicio (para ordenar bien)
    def extraer_hora_inicio(horario_str):
        # "HH:MM–HH:MM"
        return horario_str.split("–")[0]

    df["_fecha_hora_inicio"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].apply(extraer_hora_inicio))
    df = df.sort_values(by=["sección", "semana", "_fecha_hora_inicio"]).drop(columns=["_fecha_hora_inicio"])

    # Exportar a Excel
    with pd.ExcelWriter(exportar_a, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Calendario")

    return df



df_calendario = crear_calendario_curso(
    fecha_inicio="2026-03-16",          # cambia esto si quieres otro lunes de inicio
    numero_semanas=18,
    exportar_a="calendario_curso.xlsx"
)
print("Listo: calendario_curso.xlsx generado.")
print(df_calendario.head(10))