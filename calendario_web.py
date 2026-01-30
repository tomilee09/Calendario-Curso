# import io
# import pandas as pd
# import streamlit as st
# import plotly.express as px
# from datetime import time

# # =========================
# # Generador de calendario
# # =========================
# def crear_calendario_curso(
#     fecha_inicio="2026-03-16",  # lunes "a mitad de marzo"
#     numero_semanas=18,
# ):
#     # Horarios inventados por sección (ajústalos a tus reales)
#     # dia_semana: Monday..Sunday
#     secciones = {
#         "Sección 1": {
#             "teorica":   {"dia_semana": "Monday",    "inicio": time(12, 0),  "fin": time(13, 30)},
#             "seminario": {"dia_semana": "Wednesday", "inicio": time(15, 0), "fin": time(16, 30)},
#             "lab":       {"dia_semana": "Wednesday",    "inicio": time(16, 45),  "fin": time(18, 15)},
#         },
#         "Sección 2": {
#             "teorica":   {"dia_semana": "Monday",   "inicio": time(16, 45),   "fin": time(18, 15)},
#             "seminario": {"dia_semana": "Friday",  "inicio": time(8, 30),  "fin": time(10, 0)},
#             "lab":       {"dia_semana": "Monday",    "inicio": time(15, 0),   "fin": time(16, 30)},
#         },
#         "Sección 3": {
#             "teorica":   {"dia_semana": "Wednesday",    "inicio": time(16, 45),  "fin": time(18, 15)},
#             "seminario": {"dia_semana": "Friday", "inicio": time(10, 15), "fin": time(11, 45)},
#             "lab":       {"dia_semana": "Friday",  "inicio": time(12, 0),   "fin": time(13, 30)},
#         },
#         "Sección 4": {
#             "teorica":   {"dia_semana": "Wednesday",   "inicio": time(15, 0),  "fin": time(16, 30)},
#             "seminario": {"dia_semana": "Friday",  "inicio": time(8, 30), "fin": time(10, 0)},
#             "lab":       {"dia_semana": "Friday",  "inicio": time(10, 15),  "fin": time(11, 45)},
#         },
#     }

#     orden_dias = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
#     dias_es = {
#         "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
#         "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
#     }

#     # def fecha_de_dia_en_semana(ancla_semana, dia_semana):
#     #     # ancla_semana es Timestamp (cualquier día dentro de esa semana)
#     #     idx = orden_dias.index(dia_semana)
#     #     return ancla_semana + pd.offsets.Week(weekday=idx)
#     def fecha_de_dia_en_semana(ancla_semana, dia_semana):
#         # ancla_semana debe ser el lunes de la semana
#         idx = orden_dias.index(dia_semana)  # Monday=0, ..., Sunday=6
#         return pd.Timestamp(ancla_semana.date()) + pd.Timedelta(days=idx)

#     def rango_horario_str(inicio, fin):
#         return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

#     def inicio_datetime(fecha, inicio):
#         return pd.Timestamp(str(fecha)) + pd.Timedelta(hours=inicio.hour, minutes=inicio.minute)

#     fecha_inicio = pd.Timestamp(fecha_inicio)
#     filas = []

#     for seccion, cfg in secciones.items():
#         for semana in range(1, numero_semanas + 1):
#             ancla = fecha_inicio + pd.Timedelta(days=7*(semana-1))

#             # Teórica + Seminario todas las semanas
#             for clave, nombre in [("teorica","Clase teórica"), ("seminario","Seminario")]:
#                 dia_semana = cfg[clave]["dia_semana"]
#                 fecha_evento = fecha_de_dia_en_semana(ancla, dia_semana).date()
#                 horario = rango_horario_str(cfg[clave]["inicio"], cfg[clave]["fin"])

#                 filas.append({
#                     "semana": semana,
#                     "fecha": fecha_evento,
#                     "día": dias_es[dia_semana],
#                     "horario": horario,
#                     "sección": seccion,
#                     "actividad": nombre,
#                     "observaciones": "",
#                     "tema": "",          # <-- nuevo
#                     "evaluación": ""     # <-- nuevo (vacío por defecto)
#                 })

#             # Laboratorio cada 2 semanas (pares)
#             if semana % 2 == 0:
#                 dia_semana = cfg["lab"]["dia_semana"]
#                 fecha_evento = fecha_de_dia_en_semana(ancla, dia_semana).date()
#                 horario = rango_horario_str(cfg["lab"]["inicio"], cfg["lab"]["fin"])

#                 filas.append({
#                     "semana": semana,
#                     "fecha": fecha_evento,
#                     "día": dias_es[dia_semana],
#                     "horario": horario,
#                     "sección": seccion,
#                     "actividad": "Laboratorio",
#                     "observaciones": "Cada 2 semanas",
#                     "tema": "",          # <-- nuevo
#                     "evaluación": ""     # <-- nuevo
#                 })

#     df = pd.DataFrame(filas)

#     # columna auxiliar para ordenar por hora real
#     def extraer_inicio(h):
#         return h.split("–")[0]

#     df["_inicio_dt"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].apply(extraer_inicio))
#     df = df.sort_values(["sección", "semana", "_inicio_dt"]).drop(columns=["_inicio_dt"])

#     return df


# # =========================
# # Exportar Excel
# # =========================
# def df_a_excel_bytes(df: pd.DataFrame) -> bytes:
#     buffer = io.BytesIO()
#     with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
#         df.to_excel(writer, index=False, sheet_name="Calendario")
#     return buffer.getvalue()


# # =========================
# # (Opcional) Exportar ICS
# # =========================
# def df_a_ics_bytes(df: pd.DataFrame, tz="America/Santiago") -> bytes:
#     try:
#         from ics import Calendar, Event
#     except Exception:
#         raise RuntimeError("Falta instalar 'ics'. Ejecuta: pip install ics")

#     cal = Calendar()

#     # Parse horario
#     def parse_horario(h):
#         a, b = h.split("–")
#         hi = pd.to_datetime(a, format="%H:%M").time()
#         hf = pd.to_datetime(b, format="%H:%M").time()
#         return hi, hf

#     for _, r in df.iterrows():
#         hi, hf = parse_horario(r["horario"])
#         inicio = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
#         fin    = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hf.hour, minutes=hf.minute)

#         ev = Event()
#         ev.name = f'{r["actividad"]} ({r["sección"]})'
#         ev.begin = inicio.tz_localize(tz)
#         ev.end = fin.tz_localize(tz)
#         desc = []
#         if str(r.get("observaciones","")).strip():
#             desc.append(str(r["observaciones"]))
#         desc.append(f"Semana: {r['semana']}")
#         ev.description = "\n".join(desc)
#         cal.events.add(ev)

#     return str(cal).encode("utf-8")


# import pandas as pd
# from datetime import time

# # =========================
# # CASOS ESPECIALES (EDITA AQUÍ)
# # =========================

# CASOS_ESPECIALES = {
#     # 1) Cambios finos por sección/semana/actividad
#     "ediciones": [
#         # Ejemplo: primera semana, una sección no tiene sala de computación (lo dejo como observación)
#         # Ajusta sección/semana/actividad según tu caso real
#         {
#             "filtro": {"sección": "Sección 2", "semana": 1, "actividad": "Laboratorio"},
#             "set": {"observaciones": "No hay sala de computación esta semana (plan B)."}
#         },
#     ],

#     # 2) Semanas de "trabajo autónomo" (reemplaza clases por esta etiqueta)
#     # Puedes poner [7] o [5, 10] etc.
#     "semanas_trabajo_autonomo": [16],

#     # 3) Feriados: lista de dicts con fecha y nombre (se marca “Sin clases (Feriado)”)
#     "feriados": [
#         {"fecha": "2026-04-03", "nombre": "Feriado (ejemplo)"},
#         {"fecha": "2026-05-01", "nombre": "Día del Trabajador"},
#     ],

#     # 4) Semanas finales sin clases regulares (por ejemplo 17 y 18) y reemplazo por exámenes
#     "semanas_examenes": [17,18],

#     # Eventos de exámenes (pueden tener horarios distintos)
#     # Define explícitamente: sección + fecha + inicio/fin + nombre
#     "eventos_examenes": [
#         {"sección": "Sección 1", "fecha": "2026-07-06", "inicio": time(9, 0),  "fin": time(11, 0),
#          "actividad": "Examen", "observaciones": "Examen final"},
#         {"sección": "Sección 2", "fecha": "2026-07-07", "inicio": time(16, 0), "fin": time(18, 0),
#          "actividad": "Examen", "observaciones": "Examen final"},
#         {"sección": "Sección 3", "fecha": "2026-07-08", "inicio": time(10, 0), "fin": time(12, 0),
#          "actividad": "Examen", "observaciones": "Examen final"},
#         {"sección": "Sección 4", "fecha": "2026-07-09", "inicio": time(18, 0), "fin": time(20, 0),
#          "actividad": "Examen", "observaciones": "Examen final"},
#     ],
# }

# import holidays

# def feriados_chile_entre(fecha_min, fecha_max):
#     # fecha_min/fecha_max pueden ser date o str
#     fmin = pd.Timestamp(fecha_min).date()
#     fmax = pd.Timestamp(fecha_max).date()

#     years = list(range(fmin.year, fmax.year + 1))
#     cl = holidays.country_holidays("CL", years=years)  # Chile  [oai_citation:1‡holidays.readthedocs.io](https://holidays.readthedocs.io/en/main/examples/?utm_source=chatgpt.com)

#     lista = []
#     for d, nombre in cl.items():
#         if fmin <= d <= fmax:
#             lista.append({"fecha": pd.Timestamp(d).strftime("%Y-%m-%d"), "nombre": str(nombre)})
#     return sorted(lista, key=lambda x: x["fecha"])


# # =========================
# # APLICADOR DE CASOS ESPECIALES
# # =========================

# def _horario_str(inicio: time, fin: time) -> str:
#     return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

# def aplicar_casos_especiales(df: pd.DataFrame, reglas: dict) -> pd.DataFrame:
#     df = df.copy()

#     # A) Ediciones puntuales (muy útil para “ajustes finos”)
#     for ed in reglas.get("ediciones", []):
#         filtro = ed.get("filtro", {})
#         mask = pd.Series(True, index=df.index)
#         for k, v in filtro.items():
#             mask &= (df[k] == v)
#         for col, val in ed.get("set", {}).items():
#             df.loc[mask, col] = val

#     # B) Semanas de trabajo autónomo: reemplaza actividad (manteniendo fechas/horarios)
#     semanas_auto = set(reglas.get("semanas_trabajo_autonomo", []))
#     if semanas_auto:
#         mask_auto = df["semana"].isin(semanas_auto)
#         # Si quieres que también “cancele” laboratorios esa semana, así queda todo consistente
#         df.loc[mask_auto, "actividad"] = "Trabajo autónomo"
#         df.loc[mask_auto, "observaciones"] = "No hay clases (trabajo autónomo)."

#     # C) Feriados: marcar “Sin clases (Feriado)” solo en esas fechas
#     feriados = reglas.get("feriados", [])
#     if feriados:
#         feriados_map = {pd.Timestamp(f["fecha"]).date(): f["nombre"] for f in feriados}
#         mask_fer = df["fecha"].isin(list(feriados_map.keys()))
#         df.loc[mask_fer, "actividad"] = "Sin clases (Feriado)"
#         df.loc[mask_fer, "observaciones"] = df.loc[mask_fer, "fecha"].map(feriados_map)

#     # # D) Semanas de exámenes: eliminar clases regulares en esas semanas y luego insertar exámenes
#     # semanas_ex = set(reglas.get("semanas_examenes", []))
#     # if semanas_ex:
#     #     df = df[~df["semana"].isin(semanas_ex)].copy()

#     #     # Insertar eventos de exámenes (con horario custom)
#     #     nuevos = []
#     #     for ev in reglas.get("eventos_examenes", []):
#     #         fecha = pd.Timestamp(ev["fecha"]).date()
#     #         nuevos.append({
#     #             "semana": None,  # opcional: si quieres, puedes mapear a 17/18 manualmente
#     #             "fecha": fecha,
#     #             "día": {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}[pd.Timestamp(ev["fecha"]).weekday()],
#     #             "horario": _horario_str(ev["inicio"], ev["fin"]),
#     #             "sección": ev["sección"],
#     #             "actividad": ev["actividad"],
#     #             "observaciones": ev.get("observaciones", "")
#     #         })

#     #     if nuevos:
#     #         df = pd.concat([df, pd.DataFrame(nuevos)], ignore_index=True)
    
#         # D) Semanas de exámenes: eliminar clases regulares en esas semanas y luego insertar exámenes
#     semanas_ex = set(reglas.get("semanas_examenes", []))
#     if semanas_ex:
#         # referencia: lunes de la semana 1 (la fecha mínima del df base, que debería ser de semana 1)
#         # convertimos a Timestamp para operar
#         ref = pd.Timestamp(str(df["fecha"].min()))

#         # elimina clases regulares en semanas de exámenes
#         df = df[~df["semana"].isin(semanas_ex)].copy()

#         # Insertar eventos de exámenes (con horario custom)
#         nuevos = []
#         for ev in reglas.get("eventos_examenes", []):
#             fecha_ts = pd.Timestamp(ev["fecha"])
#             fecha = fecha_ts.date()

#             # calcula semana según la fecha respecto a ref
#             semana_ev = int((fecha_ts - ref).days // 7) + 1

#             nuevos.append({
#                 "semana": semana_ev,
#                 "fecha": fecha,
#                 "día": {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}[fecha_ts.weekday()],
#                 "horario": _horario_str(ev["inicio"], ev["fin"]),
#                 "sección": ev["sección"],
#                 "actividad": ev["actividad"],
#                 "observaciones": ev.get("observaciones", "")
#             })

#         if nuevos:
#             df = pd.concat([df, pd.DataFrame(nuevos)], ignore_index=True)

#     # Orden final por sección y fecha/hora
#     def _inicio(h): return h.split("–")[0] if isinstance(h, str) and "–" in h else "00:00"
#     df["_inicio_dt"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].apply(_inicio), errors="coerce")
#     df = df.sort_values(["sección", "fecha", "_inicio_dt"], na_position="last").drop(columns=["_inicio_dt"])

#     return df


# # =========================
# # UI Streamlit
# # =========================
# st.set_page_config(page_title="Calendario del Curso", layout="wide")

# st.title("📅 Calendario del Curso (Streamlit)")
# st.caption("Filtro por sección / semana, tabla bonita, gráficos interactivos y exportación.")

# with st.sidebar:
#     st.header("⚙️ Configuración")
#     fecha_inicio = st.date_input("Fecha de inicio (idealmente lunes)", value=pd.Timestamp("2026-03-16").date())
#     numero_semanas = st.number_input("Número de semanas", min_value=1, max_value=60, value=18, step=1)

# df = crear_calendario_curso(str(fecha_inicio), int(numero_semanas))
# CASOS_ESPECIALES["feriados"] = feriados_chile_entre(df["fecha"].min(), df["fecha"].max())
# df = aplicar_casos_especiales(df, CASOS_ESPECIALES)

# # Filtros
# colf1, colf2, colf3 = st.columns([1.2, 1.0, 1.0])
# with colf1:
#     secciones = sorted(df["sección"].unique())
#     seccion_sel = st.multiselect("Secciones", options=secciones, default=secciones)
# with colf2:
#     semanas = sorted(df["semana"].unique())
#     semana_sel = st.multiselect("Semanas", options=semanas, default=semanas)
# with colf3:
#     actividad_sel = st.multiselect(
#         "Actividad",
#         options=sorted(df["actividad"].unique()),
#         default=sorted(df["actividad"].unique())
#     )

# df_f = df[
#     df["sección"].isin(seccion_sel)
#     & df["semana"].isin(semana_sel)
#     & df["actividad"].isin(actividad_sel)
# ].copy()

# # Tabs
# tab1, tab2, tab3 = st.tabs(["Tabla", "Gráficos", "Exportar"])

# with tab1:
#     st.subheader("🧾 Tabla")
#     st.write(f"Eventos: **{len(df_f)}**")

#     # Tabla “bonita” (con DataFrame styling simple)
#     st.dataframe(
#         df_f,
#         use_container_width=True,
#         hide_index=True,
#         column_config={
#             "fecha": st.column_config.DateColumn(format="DD/MM/YYYY"),
#         }
#     )

# with tab2:
#     st.subheader("📈 Gráficos interactivos")

#     # 1) Conteo por semana y actividad
#     df_count = df_f.groupby(["semana", "actividad"], as_index=False).size()
#     fig1 = px.bar(df_count, x="semana", y="size", color="actividad", barmode="group")
#     st.plotly_chart(fig1, use_container_width=True)

#     # 2) Conteo por día de la semana
#     orden_dias_es = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
#     df_dias = df_f.groupby(["día"], as_index=False).size()
#     df_dias["día"] = pd.Categorical(df_dias["día"], categories=orden_dias_es, ordered=True)
#     df_dias = df_dias.sort_values("día")
#     fig2 = px.bar(df_dias, x="día", y="size")
#     st.plotly_chart(fig2, use_container_width=True)

#     # 3) “Timeline” simple (tipo agenda) con Plotly
#     # Creamos start/end a partir de fecha+horario
#     def parse_horario(h):
#         a, b = h.split("–")
#         hi = pd.to_datetime(a, format="%H:%M").time()
#         hf = pd.to_datetime(b, format="%H:%M").time()
#         return hi, hf

#     temp = df_f.copy()
#     hi_hf = temp["horario"].apply(parse_horario)
#     temp["inicio"] = [pd.Timestamp(str(f)) + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
#                       for f, (hi, _) in zip(temp["fecha"], hi_hf)]
#     temp["fin"] = [pd.Timestamp(str(f)) + pd.Timedelta(hours=hf.hour, minutes=hf.minute)
#                    for f, (_, hf) in zip(temp["fecha"], hi_hf)]
#     temp["label"] = temp["actividad"] + " · " + temp["sección"]

#     fig3 = px.timeline(
#         temp,
#         x_start="inicio",
#         x_end="fin",
#         y="sección",
#         color="actividad",
#         hover_data=["semana", "fecha", "día", "horario", "observaciones"],
#     )
#     fig3.update_yaxes(autorange="reversed")
#     st.plotly_chart(fig3, use_container_width=True)

# with tab3:
#     st.subheader("⬇️ Exportar")

#     excel_bytes = df_a_excel_bytes(df_f)
#     st.download_button(
#         label="Descargar Excel (.xlsx)",
#         data=excel_bytes,
#         file_name="calendario_filtrado.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

#     st.divider()
#     st.caption("Opcional: exportar a .ics (Google Calendar / Apple Calendar). Requiere `pip install ics`.")

#     colx1, colx2 = st.columns([1, 2])
#     with colx1:
#         export_ics = st.checkbox("Habilitar exportación ICS", value=False)
#     with colx2:
#         tz = st.text_input("Timezone", value="America/Santiago")

#     if export_ics:
#         try:
#             ics_bytes = df_a_ics_bytes(df_f, tz=tz)
#             st.download_button(
#                 label="Descargar calendario (.ics)",
#                 data=ics_bytes,
#                 file_name="calendario_filtrado.ics",
#                 mime="text/calendar"
#             )
#         except Exception as e:
#             st.error(str(e))

# from streamlit_calendar import calendar

# def df_a_fullcalendar_events(df: pd.DataFrame):
#     # colores por actividad (elige los que quieras)
#     colores = {
#         "Clase teórica": "#1f77b4",
#         "Seminario": "#2ca02c",
#         "Laboratorio": "#ff7f0e",
#         "Trabajo autónomo": "#9467bd",
#         "Sin clases (Feriado)": "#d62728",
#         "Examen": "#111111",
#     }

#     def parse_horario(h):
#         a, b = h.split("–")
#         hi = pd.to_datetime(a, format="%H:%M").time()
#         hf = pd.to_datetime(b, format="%H:%M").time()
#         return hi, hf

#     events = []
#     for _, r in df.iterrows():
#         # start/end ISO strings
#         if isinstance(r["horario"], str) and "–" in r["horario"]:
#             hi, hf = parse_horario(r["horario"])
#             start = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
#             end   = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hf.hour, minutes=hf.minute)
#         else:
#             # fallback (evento “all-day”)
#             start = pd.Timestamp(str(r["fecha"]))
#             end = start + pd.Timedelta(days=1)

#         title = f'{r["actividad"]} · {r["sección"]}'
#         obs = r.get("observaciones", "")
#         events.append({
#             "title": title,
#             "start": start.isoformat(),
#             "end": end.isoformat(),
#             "color": colores.get(r["actividad"], "#888888"),
#             "extendedProps": {
#                 "semana": r.get("semana", ""),
#                 "día": r.get("día", ""),
#                 "horario": r.get("horario", ""),
#                 "observaciones": obs,
#                 "sección": r.get("sección", ""),
#                 "actividad": r.get("actividad", ""),
#             }
#         })
#     return events


# # En tu tab "Calendario"
# events = df_a_fullcalendar_events(df_f)

# # calendar_options = {
# #     "initialView": "dayGridMonth",  # también: timeGridWeek, listWeek, multiMonthYear, etc.
# #     "headerToolbar": {
# #         "left": "prev,next today",
# #         "center": "title",
# #         "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
# #     },
# #     "height": "auto",
# # }

# calendar_options = {
#     "initialView": "timeGridWeek",
#     "headerToolbar": {
#         "left": "prev,next today",
#         "center": "title",
#         "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
#     },

#     # 👇 Clave para que se pueda ver y scrollear bien en semana/día
#     "height": 800,                 # más alto => más espacio y scroll interno
#     "contentHeight": "auto",

#     # 👇 Rango de horas visible (cámbialo a tu gusto)
#     "slotMinTime": "07:00:00",
#     "slotMaxTime": "22:00:00",

#     # 👇 Hora a la que “parte” el scroll al abrir
#     "scrollTime": "08:00:00",

#     # 👇 Slots cada 30 min (puedes cambiar a 15 min)
#     "slotDuration": "00:30:00",
#     "snapDuration": "00:15:00",

#     # 👇 Ahora sí habilita interacciones
#     "selectable": True,
#     "editable": False,             # True si luego quieres arrastrar eventos
#     "nowIndicator": True,

#     # 👇 Mejora UX
#     "weekNumbers": True,
#     "dayMaxEvents": True,
# }

# state = calendar(events=events, options=calendar_options)
# # state puede traer callbacks (dateClick/eventClick) si después quieres interacción





# import io
# import pandas as pd
# import streamlit as st
# import plotly.express as px
# from datetime import time

# from streamlit_calendar import calendar
# import holidays

# # =========================
# # Generador de calendario
# # =========================
# def crear_calendario_curso(
#     fecha_inicio="2026-03-16",  # lunes "a mitad de marzo"
#     numero_semanas=18,
# ):
#     # Horarios por sección (NO CAMBIAR: ya están correctos)
#     secciones = {
#         "Sección 1": {
#             "teorica":   {"dia_semana": "Monday",    "inicio": time(12, 0),  "fin": time(13, 30)},
#             "seminario": {"dia_semana": "Wednesday", "inicio": time(15, 0),  "fin": time(16, 30)},
#             "lab":       {"dia_semana": "Wednesday", "inicio": time(16, 45), "fin": time(18, 15)},
#         },
#         "Sección 2": {
#             "teorica":   {"dia_semana": "Monday", "inicio": time(16, 45), "fin": time(18, 15)},
#             "seminario": {"dia_semana": "Friday", "inicio": time(8, 30),  "fin": time(10, 0)},
#             "lab":       {"dia_semana": "Monday", "inicio": time(15, 0),  "fin": time(16, 30)},
#         },
#         "Sección 3": {
#             "teorica":   {"dia_semana": "Wednesday", "inicio": time(16, 45), "fin": time(18, 15)},
#             "seminario": {"dia_semana": "Friday",    "inicio": time(10, 15), "fin": time(11, 45)},
#             "lab":       {"dia_semana": "Friday",    "inicio": time(12, 0),  "fin": time(13, 30)},
#         },
#         "Sección 4": {
#             "teorica":   {"dia_semana": "Wednesday", "inicio": time(15, 0),  "fin": time(16, 30)},
#             "seminario": {"dia_semana": "Friday",    "inicio": time(8, 30),  "fin": time(10, 0)},
#             "lab":       {"dia_semana": "Friday",    "inicio": time(10, 15), "fin": time(11, 45)},
#         },
#     }

#     orden_dias = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
#     dias_es = {
#         "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
#         "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
#     }

#     def fecha_de_dia_en_semana(ancla_semana, dia_semana):
#         # ancla_semana debe ser el lunes de la semana
#         idx = orden_dias.index(dia_semana)  # Monday=0, ..., Sunday=6
#         return pd.Timestamp(ancla_semana.date()) + pd.Timedelta(days=idx)

#     def rango_horario_str(inicio, fin):
#         return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

#     fecha_inicio = pd.Timestamp(fecha_inicio)
#     filas = []

#     for seccion, cfg in secciones.items():
#         for semana in range(1, numero_semanas + 1):
#             ancla = fecha_inicio + pd.Timedelta(days=7*(semana-1))  # lunes de esa semana

#             # Teórica + Seminario todas las semanas
#             for clave, nombre in [("teorica","Clase teórica"), ("seminario","Seminario")]:
#                 dia_semana = cfg[clave]["dia_semana"]
#                 fecha_evento = fecha_de_dia_en_semana(ancla, dia_semana).date()
#                 horario = rango_horario_str(cfg[clave]["inicio"], cfg[clave]["fin"])

#                 filas.append({
#                     "semana": semana,
#                     "fecha": fecha_evento,
#                     "día": dias_es[dia_semana],
#                     "horario": horario,
#                     "sección": seccion,
#                     "actividad": nombre,
#                     "observaciones": "",
#                     "tema": "",          # nuevo
#                     "evaluación": ""     # nuevo
#                 })

#             # Laboratorio cada 2 semanas (pares)
#             if semana % 2 == 0:
#                 dia_semana = cfg["lab"]["dia_semana"]
#                 fecha_evento = fecha_de_dia_en_semana(ancla, dia_semana).date()
#                 horario = rango_horario_str(cfg["lab"]["inicio"], cfg["lab"]["fin"])

#                 filas.append({
#                     "semana": semana,
#                     "fecha": fecha_evento,
#                     "día": dias_es[dia_semana],
#                     "horario": horario,
#                     "sección": seccion,
#                     "actividad": "Laboratorio",
#                     "observaciones": "Cada 2 semanas",
#                     "tema": "",          # nuevo
#                     "evaluación": ""     # nuevo
#                 })

#     df = pd.DataFrame(filas)

#     # Orden por sección, semana y hora real
#     def extraer_inicio(h): return h.split("–")[0]
#     df["_inicio_dt"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].apply(extraer_inicio))
#     df = df.sort_values(["sección", "semana", "_inicio_dt"]).drop(columns=["_inicio_dt"])

#     return df


# # =========================
# # Exportar Excel
# # =========================
# def df_a_excel_bytes(df: pd.DataFrame) -> bytes:
#     buffer = io.BytesIO()
#     with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
#         df.to_excel(writer, index=False, sheet_name="Calendario")
#     return buffer.getvalue()


# # =========================
# # (Opcional) Exportar ICS
# # =========================
# def df_a_ics_bytes(df: pd.DataFrame, tz="America/Santiago") -> bytes:
#     try:
#         from ics import Calendar, Event
#     except Exception:
#         raise RuntimeError("Falta instalar 'ics'. Ejecuta: pip install ics")

#     cal = Calendar()

#     def parse_horario(h):
#         a, b = h.split("–")
#         hi = pd.to_datetime(a, format="%H:%M").time()
#         hf = pd.to_datetime(b, format="%H:%M").time()
#         return hi, hf

#     for _, r in df.iterrows():
#         hi, hf = parse_horario(r["horario"])
#         inicio = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
#         fin    = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hf.hour, minutes=hf.minute)

#         ev = Event()
#         # Incluye tema y evaluación en el nombre si existen
#         tema = str(r.get("tema", "")).strip()
#         evaluacion = str(r.get("evaluación", "")).strip()
#         extra = []
#         if tema:
#             extra.append(tema)
#         if evaluacion:
#             extra.append(f"Evaluación: {evaluacion}")
#         suf = " | " + " | ".join(extra) if extra else ""

#         ev.name = f'{r["actividad"]} ({r["sección"]}){suf}'
#         ev.begin = inicio.tz_localize(tz)
#         ev.end = fin.tz_localize(tz)

#         desc = []
#         if str(r.get("observaciones","")).strip():
#             desc.append(str(r["observaciones"]))
#         desc.append(f"Semana: {r['semana']}")
#         if tema:
#             desc.append(f"Tema: {tema}")
#         if evaluacion:
#             desc.append(f"Evaluación: {evaluacion}")
#         ev.description = "\n".join(desc)

#         cal.events.add(ev)

#     return str(cal).encode("utf-8")


# # =========================
# # CASOS ESPECIALES (EDITA AQUÍ)
# # =========================
# CASOS_ESPECIALES = {
#     "ediciones": [
#         {
#             "filtro": {"sección": "Sección 2", "semana": 1, "actividad": "Laboratorio"},
#             "set": {"observaciones": "No hay sala de computación esta semana (plan B)."}
#         },

#         # Ejemplos de evaluación (solo 3 tipos por ahora)
#         # {
#         #     "filtro": {"sección": "Sección 1", "semana": 5, "actividad": "Clase teórica"},
#         #     "set": {"evaluación": "Prueba", "tema": "Tema 5", "observaciones": "Materia acumulativa"}
#         # },
#     ],

#     "semanas_trabajo_autonomo": [16],

#     # Se llenará automáticamente con feriados Chile según rango (abajo)
#     "feriados": [],

#     "semanas_examenes": [17, 18],
#     "eventos_examenes": [
#         {"sección": "Sección 1", "fecha": "2026-07-06", "inicio": time(9, 0),  "fin": time(11, 0),
#          "actividad": "Examen", "observaciones": "Examen final"},
#         {"sección": "Sección 2", "fecha": "2026-07-07", "inicio": time(16, 0), "fin": time(18, 0),
#          "actividad": "Examen", "observaciones": "Examen final"},
#         {"sección": "Sección 3", "fecha": "2026-07-08", "inicio": time(10, 0), "fin": time(12, 0),
#          "actividad": "Examen", "observaciones": "Examen final"},
#         {"sección": "Sección 4", "fecha": "2026-07-09", "inicio": time(18, 0), "fin": time(20, 0),
#          "actividad": "Examen", "observaciones": "Examen final"},
#     ],
# }


# def feriados_chile_entre(fecha_min, fecha_max):
#     fmin = pd.Timestamp(fecha_min).date()
#     fmax = pd.Timestamp(fecha_max).date()

#     years = list(range(fmin.year, fmax.year + 1))
#     cl = holidays.country_holidays("CL", years=years)

#     lista = []
#     for d, nombre in cl.items():
#         if fmin <= d <= fmax:
#             lista.append({"fecha": pd.Timestamp(d).strftime("%Y-%m-%d"), "nombre": str(nombre)})
#     return sorted(lista, key=lambda x: x["fecha"])


# # =========================
# # APLICADOR DE CASOS ESPECIALES
# # =========================
# def _horario_str(inicio: time, fin: time) -> str:
#     return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

# def aplicar_casos_especiales(df: pd.DataFrame, reglas: dict) -> pd.DataFrame:
#     df = df.copy()

#     # A) Ediciones puntuales
#     for ed in reglas.get("ediciones", []):
#         filtro = ed.get("filtro", {})
#         mask = pd.Series(True, index=df.index)
#         for k, v in filtro.items():
#             mask &= (df[k] == v)
#         for col, val in ed.get("set", {}).items():
#             df.loc[mask, col] = val

#     # B) Trabajo autónomo (reemplaza actividad)
#     semanas_auto = set(reglas.get("semanas_trabajo_autonomo", []))
#     if semanas_auto:
#         mask_auto = df["semana"].isin(semanas_auto)
#         df.loc[mask_auto, "actividad"] = "Trabajo autónomo"
#         df.loc[mask_auto, "observaciones"] = "No hay clases (trabajo autónomo)."
#         # si quieres, también podrías forzar tema vacío o dejarlo:
#         # df.loc[mask_auto, "tema"] = ""

#     # C) Feriados
#     feriados = reglas.get("feriados", [])
#     if feriados:
#         feriados_map = {pd.Timestamp(f["fecha"]).date(): f["nombre"] for f in feriados}
#         mask_fer = df["fecha"].isin(list(feriados_map.keys()))
#         df.loc[mask_fer, "actividad"] = "Sin clases (Feriado)"
#         df.loc[mask_fer, "observaciones"] = df.loc[mask_fer, "fecha"].map(feriados_map)

#     # D) Exámenes: elimina clases regulares en semanas de exámenes e inserta exámenes
#     semanas_ex = set(reglas.get("semanas_examenes", []))
#     if semanas_ex:
#         ref = pd.Timestamp(str(df["fecha"].min()))
#         df = df[~df["semana"].isin(semanas_ex)].copy()

#         nuevos = []
#         for ev in reglas.get("eventos_examenes", []):
#             fecha_ts = pd.Timestamp(ev["fecha"])
#             fecha = fecha_ts.date()
#             semana_ev = int((fecha_ts - ref).days // 7) + 1

#             nuevos.append({
#                 "semana": semana_ev,
#                 "fecha": fecha,
#                 "día": {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}[fecha_ts.weekday()],
#                 "horario": _horario_str(ev["inicio"], ev["fin"]),
#                 "sección": ev["sección"],
#                 "actividad": ev["actividad"],
#                 "observaciones": ev.get("observaciones", ""),
#                 "tema": ev.get("tema", ""),              # permite setear tema del examen
#                 "evaluación": ev.get("evaluación", ""),  # si quieres marcar examen como evaluación también
#             })

#         if nuevos:
#             df = pd.concat([df, pd.DataFrame(nuevos)], ignore_index=True)

#     # Orden final
#     def _inicio(h): return h.split("–")[0] if isinstance(h, str) and "–" in h else "00:00"
#     df["_inicio_dt"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].apply(_inicio), errors="coerce")
#     df = df.sort_values(["sección", "fecha", "_inicio_dt"], na_position="last").drop(columns=["_inicio_dt"])

#     return df


# # =========================
# # Temas automáticos integrados (sin función externa)
# # =========================
# def rellenar_temas_auto(df: pd.DataFrame) -> pd.DataFrame:
#     df = df.copy()
#     # Asigna Tema 1,2,3... por sección en orden cronológico (solo donde esté vacío)
#     for seccion in df["sección"].unique():
#         mask_sec = df["sección"] == seccion
#         idxs = df[mask_sec].index.tolist()
#         contador = 1
#         for idx in idxs:
#             if not str(df.at[idx, "tema"]).strip():
#                 df.at[idx, "tema"] = f"Tema {contador}"
#             contador += 1
#     return df


# # =========================
# # Calendario FullCalendar
# # =========================
# def df_a_fullcalendar_events(df: pd.DataFrame):
#     # colores base por actividad
#     colores = {
#         "Clase teórica": "#1f77b4",
#         "Seminario": "#2ca02c",
#         "Laboratorio": "#ff7f0e",
#         "Trabajo autónomo": "#9467bd",
#         "Sin clases (Feriado)": "#d62728",
#         "Examen": "#111111",
#     }

#     iconos_eval = {
#         "Prueba": "⭐",
#         "Experimento": "🧪",
#         "Trabajo práctico": "📝",
#     }

#     # si hay evaluación, destacamos fuerte por tipo
#     colores_eval = {
#         "Prueba": "#d62728",
#         "Experimento": "#9467bd",
#         "Trabajo práctico": "#2ca02c",
#     }

#     def parse_horario(h):
#         a, b = h.split("–")
#         hi = pd.to_datetime(a, format="%H:%M").time()
#         hf = pd.to_datetime(b, format="%H:%M").time()
#         return hi, hf

#     events = []
#     for _, r in df.iterrows():
#         hi, hf = parse_horario(r["horario"])
#         start = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
#         end   = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hf.hour, minutes=hf.minute)

#         tema = str(r.get("tema", "")).strip()
#         evaluacion = str(r.get("evaluación", "")).strip()
#         obs = str(r.get("observaciones", "")).strip()

#         icono = iconos_eval.get(evaluacion, "")
#         prefijo = f"{icono} " if icono else ""

#         # mostrar tema visible en el calendario
#         if tema:
#             title = f"{prefijo}{r['actividad']} · {tema}"
#         else:
#             title = f"{prefijo}{r['actividad']}"

#         color_evento = colores_eval.get(evaluacion, colores.get(r["actividad"], "#888888"))

#         events.append({
#             "title": title,
#             "start": start.isoformat(),
#             "end": end.isoformat(),
#             "color": color_evento,
#             "extendedProps": {
#                 "semana": r.get("semana", ""),
#                 "día": r.get("día", ""),
#                 "horario": r.get("horario", ""),
#                 "observaciones": obs,
#                 "sección": r.get("sección", ""),
#                 "actividad": r.get("actividad", ""),
#                 "tema": tema,
#                 "evaluación": evaluacion,
#             }
#         })
#     return events


# # =========================
# # UI Streamlit
# # =========================
# st.set_page_config(page_title="Calendario del Curso", layout="wide")

# st.title("📅 Calendario del Curso (Streamlit)")
# st.caption("Tabla + gráficos + calendario (FullCalendar) con tema y evaluaciones destacadas.")

# with st.sidebar:
#     st.header("⚙️ Configuración")
#     fecha_inicio = st.date_input("Fecha de inicio (idealmente lunes)", value=pd.Timestamp("2026-03-16").date())
#     numero_semanas = st.number_input("Número de semanas", min_value=1, max_value=60, value=18, step=1)

# df = crear_calendario_curso(str(fecha_inicio), int(numero_semanas))

# # Feriados Chile automáticos en el rango real del curso
# CASOS_ESPECIALES["feriados"] = feriados_chile_entre(df["fecha"].min(), df["fecha"].max())

# df = aplicar_casos_especiales(df, CASOS_ESPECIALES)

# # Relleno automático de temas (Tema 1..N) donde esté vacío
# df = rellenar_temas_auto(df)

# # Validación simple de evaluación: solo 3 permitidas
# eval_validas = {"", "Prueba", "Experimento", "Trabajo práctico"}
# mask_invalid = ~df["evaluación"].fillna("").isin(eval_validas)
# if mask_invalid.any():
#     st.warning("Hay evaluaciones con nombre no permitido (solo: Prueba, Experimento, Trabajo práctico). Revisa CASOS_ESPECIALES['ediciones'].")

# # Filtros
# colf1, colf2, colf3, colf4 = st.columns([1.2, 1.0, 1.0, 1.0])

# with colf1:
#     secciones = sorted(df["sección"].unique())
#     seccion_sel = st.multiselect("Secciones", options=secciones, default=secciones)

# with colf2:
#     semanas = sorted(df["semana"].unique())
#     semana_sel = st.multiselect("Semanas", options=semanas, default=semanas)

# with colf3:
#     actividad_sel = st.multiselect(
#         "Actividad",
#         options=sorted(df["actividad"].unique()),
#         default=sorted(df["actividad"].unique())
#     )

# with colf4:
#     eval_opts = ["(Todas)", "Prueba", "Experimento", "Trabajo práctico"]
#     eval_sel = st.selectbox("Evaluación", options=eval_opts, index=0)

# df_f = df[
#     df["sección"].isin(seccion_sel)
#     & df["semana"].isin(semana_sel)
#     & df["actividad"].isin(actividad_sel)
# ].copy()

# if eval_sel != "(Todas)":
#     df_f = df_f[df_f["evaluación"] == eval_sel].copy()

# # Tabs
# tab1, tab2, tab3, tab4 = st.tabs(["Tabla", "Gráficos", "Calendario", "Exportar"])

# with tab1:
#     st.subheader("🧾 Tabla")
#     st.write(f"Eventos: **{len(df_f)}**")

#     st.dataframe(
#         df_f,
#         use_container_width=True,
#         hide_index=True,
#         column_config={
#             "fecha": st.column_config.DateColumn(format="DD/MM/YYYY"),
#         }
#     )

# with tab2:
#     st.subheader("📈 Gráficos interactivos")

#     df_count = df_f.groupby(["semana", "actividad"], as_index=False).size()
#     fig1 = px.bar(df_count, x="semana", y="size", color="actividad", barmode="group")
#     st.plotly_chart(fig1, use_container_width=True)

#     orden_dias_es = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
#     df_dias = df_f.groupby(["día"], as_index=False).size()
#     df_dias["día"] = pd.Categorical(df_dias["día"], categories=orden_dias_es, ordered=True)
#     df_dias = df_dias.sort_values("día")
#     fig2 = px.bar(df_dias, x="día", y="size")
#     st.plotly_chart(fig2, use_container_width=True)

# with tab3:
#     st.subheader("🗓️ Calendario")

#     events = df_a_fullcalendar_events(df_f)

#     # Arranca en la primera fecha con eventos (así no te manda a "hoy")
#     if len(df_f) > 0:
#         initial_date = pd.Timestamp(df_f["fecha"].min()).strftime("%Y-%m-%d")
#     else:
#         initial_date = pd.Timestamp(str(fecha_inicio)).strftime("%Y-%m-%d")

#     calendar_options = {
#         "initialView": "timeGridWeek",
#         "initialDate": initial_date,
#         "headerToolbar": {
#             "left": "prev,next today",
#             "center": "title",
#             "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
#         },

#         "height": 850,
#         "contentHeight": "auto",

#         "slotMinTime": "07:00:00",
#         "slotMaxTime": "22:00:00",
#         "scrollTime": "08:00:00",

#         "slotDuration": "00:30:00",
#         "snapDuration": "00:15:00",

#         "selectable": True,
#         "editable": False,
#         "nowIndicator": True,

#         "weekNumbers": True,
#         "dayMaxEvents": True,
#     }

#     state = calendar(events=events, options=calendar_options)

#     st.divider()
#     st.subheader("🔎 Detalles (clic en un evento)")

#     event_click = None
#     date_click = None
#     select_info = None

#     if isinstance(state, dict):
#         event_click = state.get("eventClick")
#         date_click = state.get("dateClick")
#         select_info = state.get("select")

#     if event_click:
#         ev = event_click.get("event", {})
#         props = ev.get("extendedProps", {})

#         st.success("Evento seleccionado")
#         st.write({
#             "Título": ev.get("title", ""),
#             "Inicio": ev.get("start", ""),
#             "Fin": ev.get("end", ""),
#             "Sección": props.get("sección", ""),
#             "Actividad": props.get("actividad", ""),
#             "Tema": props.get("tema", ""),
#             "Evaluación": props.get("evaluación", ""),
#             "Semana": props.get("semana", ""),
#             "Día": props.get("día", ""),
#             "Horario": props.get("horario", ""),
#             "Observaciones": props.get("observaciones", ""),
#         })

#     elif date_click:
#         st.info("Click en el calendario")
#         st.write({
#             "Fecha/Hora": date_click.get("date", ""),
#             "All-day": date_click.get("allDay", ""),
#         })

#     elif select_info:
#         st.info("Rango seleccionado (arrastrando)")
#         st.write({
#             "Inicio": select_info.get("start", ""),
#             "Fin": select_info.get("end", ""),
#             "All-day": select_info.get("allDay", ""),
#         })
#     else:
#         st.caption("Tip: haz clic en un evento para ver todos sus detalles (incluye tema y evaluación).")

# with tab4:
#     st.subheader("⬇️ Exportar")

#     excel_bytes = df_a_excel_bytes(df_f)
#     st.download_button(
#         label="Descargar Excel (.xlsx)",
#         data=excel_bytes,
#         file_name="calendario_filtrado.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

#     st.divider()
#     st.caption("Opcional: exportar a .ics (Google Calendar / Apple Calendar). Requiere `pip install ics`.")

#     colx1, colx2 = st.columns([1, 2])
#     with colx1:
#         export_ics = st.checkbox("Habilitar exportación ICS", value=False)
#     with colx2:
#         tz = st.text_input("Timezone", value="America/Santiago")

#     if export_ics:
#         try:
#             ics_bytes = df_a_ics_bytes(df_f, tz=tz)
#             st.download_button(
#                 label="Descargar calendario (.ics)",
#                 data=ics_bytes,
#                 file_name="calendario_filtrado.ics",
#                 mime="text/calendar"
#             )
#         except Exception as e:
#             st.error(str(e))


# import io
# import pandas as pd
# import streamlit as st
# import plotly.express as px
# from datetime import time
# from streamlit_calendar import calendar
# import holidays

# # ============================================================
# # CONFIG FIJA (sin sidebar)
# # ============================================================
# FECHA_INICIO = "2026-03-16"   # NO CAMBIAR
# NUMERO_SEMANAS = 18          # NO CAMBIAR

# PROFES_VALIDOS = {"TY", "IG", "CC", "AR", "JCS"}  # puedes agregar más siglas aquí
# EVAL_VALIDAS = {"", "Prueba", "Experimento", "Trabajo práctico"}


# # ============================================================
# # Generador de calendario (fechas/horarios tal cual los tienes)
# # ============================================================
# def crear_calendario_curso(
#     fecha_inicio=FECHA_INICIO,
#     numero_semanas=NUMERO_SEMANAS,
# ):
#     secciones = {
#         "Sección 1": {
#             "teorica":   {"dia_semana": "Monday",    "inicio": time(12, 0),  "fin": time(13, 30)},
#             "seminario": {"dia_semana": "Wednesday", "inicio": time(15, 0),  "fin": time(16, 30)},
#             "lab":       {"dia_semana": "Wednesday", "inicio": time(16, 45), "fin": time(18, 15)},
#         },
#         "Sección 2": {
#             "teorica":   {"dia_semana": "Monday", "inicio": time(16, 45), "fin": time(18, 15)},
#             "seminario": {"dia_semana": "Friday", "inicio": time(8, 30),  "fin": time(10, 0)},
#             "lab":       {"dia_semana": "Monday", "inicio": time(15, 0),  "fin": time(16, 30)},
#         },
#         "Sección 3": {
#             "teorica":   {"dia_semana": "Wednesday", "inicio": time(16, 45), "fin": time(18, 15)},
#             "seminario": {"dia_semana": "Friday",    "inicio": time(10, 15), "fin": time(11, 45)},
#             "lab":       {"dia_semana": "Friday",    "inicio": time(12, 0),  "fin": time(13, 30)},
#         },
#         "Sección 4": {
#             "teorica":   {"dia_semana": "Wednesday", "inicio": time(15, 0),  "fin": time(16, 30)},
#             "seminario": {"dia_semana": "Friday",    "inicio": time(8, 30),  "fin": time(10, 0)},
#             "lab":       {"dia_semana": "Friday",    "inicio": time(10, 15), "fin": time(11, 45)},
#         },
#     }

#     orden_dias = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
#     dias_es = {
#         "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
#         "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
#     }

#     def fecha_de_dia_en_semana(ancla_semana, dia_semana):
#         idx = orden_dias.index(dia_semana)  # Monday=0, ..., Sunday=6
#         return pd.Timestamp(ancla_semana.date()) + pd.Timedelta(days=idx)

#     def rango_horario_str(inicio, fin):
#         return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

#     fecha_inicio = pd.Timestamp(fecha_inicio)
#     filas = []

#     for seccion, cfg in secciones.items():
#         for semana in range(1, numero_semanas + 1):
#             ancla = fecha_inicio + pd.Timedelta(days=7*(semana-1))  # lunes de esa semana

#             # Teórica + Seminario todas las semanas
#             for clave, nombre in [("teorica","Clase teórica"), ("seminario","Seminario")]:
#                 dia_semana = cfg[clave]["dia_semana"]
#                 fecha_evento = fecha_de_dia_en_semana(ancla, dia_semana).date()
#                 horario = rango_horario_str(cfg[clave]["inicio"], cfg[clave]["fin"])

#                 filas.append({
#                     "semana": semana,
#                     "fecha": fecha_evento,
#                     "día": dias_es[dia_semana],
#                     "horario": horario,
#                     "sección": seccion,
#                     "actividad": nombre,
#                     "tema": "",            # se rellena manualmente via CASOS_ESPECIALES
#                     "evaluación": "",      # se rellena manualmente via CASOS_ESPECIALES
#                     "profesores": "",      # NUEVO
#                     "observaciones": ""
#                 })

#             # Laboratorio cada 2 semanas (pares)
#             if semana % 2 == 0:
#                 dia_semana = cfg["lab"]["dia_semana"]
#                 fecha_evento = fecha_de_dia_en_semana(ancla, dia_semana).date()
#                 horario = rango_horario_str(cfg["lab"]["inicio"], cfg["lab"]["fin"])

#                 filas.append({
#                     "semana": semana,
#                     "fecha": fecha_evento,
#                     "día": dias_es[dia_semana],
#                     "horario": horario,
#                     "sección": seccion,
#                     "actividad": "Laboratorio",
#                     "tema": "",
#                     "evaluación": "",
#                     "profesores": "",
#                     "observaciones": "Cada 2 semanas"
#                 })

#     df = pd.DataFrame(filas)

#     def extraer_inicio(h): return h.split("–")[0]
#     df["_inicio_dt"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].apply(extraer_inicio))
#     df = df.sort_values(["sección", "semana", "_inicio_dt"]).drop(columns=["_inicio_dt"])

#     return df


# # ============================================================
# # Exportar Excel
# # ============================================================
# def df_a_excel_bytes(df: pd.DataFrame) -> bytes:
#     buffer = io.BytesIO()
#     with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
#         df.to_excel(writer, index=False, sheet_name="Calendario")
#     return buffer.getvalue()


# # ============================================================
# # (Opcional) Exportar ICS
# # ============================================================
# def df_a_ics_bytes(df: pd.DataFrame, tz="America/Santiago") -> bytes:
#     try:
#         from ics import Calendar, Event
#     except Exception:
#         raise RuntimeError("Falta instalar 'ics'. Ejecuta: pip install ics")

#     cal = Calendar()

#     def parse_horario(h):
#         a, b = h.split("–")
#         hi = pd.to_datetime(a, format="%H:%M").time()
#         hf = pd.to_datetime(b, format="%H:%M").time()
#         return hi, hf

#     for _, r in df.iterrows():
#         hi, hf = parse_horario(r["horario"])
#         inicio = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
#         fin    = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hf.hour, minutes=hf.minute)

#         tema = str(r.get("tema", "")).strip()
#         evaluacion = str(r.get("evaluación", "")).strip()
#         profs = str(r.get("profesores", "")).strip()

#         extra = []
#         if tema:
#             extra.append(tema)
#         if evaluacion:
#             extra.append(f"Evaluación: {evaluacion}")
#         if profs:
#             extra.append(f"Prof: {profs}")
#         suf = " | " + " | ".join(extra) if extra else ""

#         ev = Event()
#         ev.name = f'{r["actividad"]} ({r["sección"]}){suf}'
#         ev.begin = inicio.tz_localize(tz)
#         ev.end = fin.tz_localize(tz)

#         desc = []
#         if str(r.get("observaciones","")).strip():
#             desc.append(str(r["observaciones"]))
#         desc.append(f"Semana: {r['semana']}")
#         if tema:
#             desc.append(f"Tema: {tema}")
#         if evaluacion:
#             desc.append(f"Evaluación: {evaluacion}")
#         if profs:
#             desc.append(f"Profesores: {profs}")
#         ev.description = "\n".join(desc)

#         cal.events.add(ev)

#     return str(cal).encode("utf-8")


# # ============================================================
# # Feriados Chile automáticos (rango del curso)
# # ============================================================
# def feriados_chile_entre(fecha_min, fecha_max):
#     fmin = pd.Timestamp(fecha_min).date()
#     fmax = pd.Timestamp(fecha_max).date()

#     years = list(range(fmin.year, fmax.year + 1))
#     cl = holidays.country_holidays("CL", years=years)

#     lista = []
#     for d, nombre in cl.items():
#         if fmin <= d <= fmax:
#             lista.append({"fecha": pd.Timestamp(d).strftime("%Y-%m-%d"), "nombre": str(nombre)})
#     return sorted(lista, key=lambda x: x["fecha"])


# # ============================================================
# # CASOS ESPECIALES (EDITA AQUÍ)
# # ============================================================
# CASOS_ESPECIALES = {
#     "ediciones": [
#         # Ejemplo: no hay sala de computación semana 1, Sección 2, Lab
#         {
#             "filtro": {"sección": "Sección 2", "semana": 1, "actividad": "Laboratorio"},
#             "set": {"observaciones": "No hay sala de computación esta semana (plan B)."}
#         },

#         # --- DEMO: temas + profes + evaluaciones para que se vea cómo queda ---
#         {
#             "filtro": {"sección": "Sección 1", "semana": 1, "actividad": "Clase teórica"},
#             "set": {"tema": "Trigonometría", "profesores": "TY", "observaciones": "Introducción"}
#         },
#         {
#             "filtro": {"sección": "Sección 1", "semana": 2, "actividad": "Clase teórica"},
#             "set": {"tema": "Trigonometría", "profesores": "TY, IG"}
#         },
#         {
#             "filtro": {"sección": "Sección 2", "semana": 3, "actividad": "Seminario"},
#             "set": {"evaluación": "Trabajo práctico", "profesores": "CC", "observaciones": "Entrega en clase"}
#         },
#         {
#             "filtro": {"sección": "Sección 3", "semana": 6, "actividad": "Laboratorio"},
#             "set": {"evaluación": "Experimento", "profesores": "AR, JCS", "observaciones": "Informe breve"}
#         },
#         {
#             "filtro": {"sección": "Sección 4", "semana": 8, "actividad": "Clase teórica"},
#             "set": {"evaluación": "Prueba", "profesores": "IG", "observaciones": "Duración: 45 min"}
#         },
#     ],

#     "semanas_trabajo_autonomo": [16],
#     "feriados": [],

#     "semanas_examenes": [17, 18],
#     "eventos_examenes": [
#         {"sección": "Sección 1", "fecha": "2026-07-06", "inicio": time(9, 0),  "fin": time(11, 0),
#          "actividad": "Examen", "observaciones": "Examen final", "profesores": "TY"},
#         {"sección": "Sección 2", "fecha": "2026-07-07", "inicio": time(16, 0), "fin": time(18, 0),
#          "actividad": "Examen", "observaciones": "Examen final", "profesores": "IG"},
#         {"sección": "Sección 3", "fecha": "2026-07-08", "inicio": time(10, 0), "fin": time(12, 0),
#          "actividad": "Examen", "observaciones": "Examen final", "profesores": "CC"},
#         {"sección": "Sección 4", "fecha": "2026-07-09", "inicio": time(18, 0), "fin": time(20, 0),
#          "actividad": "Examen", "observaciones": "Examen final", "profesores": "AR, JCS"},
#     ],
# }


# # ============================================================
# # APLICADOR DE CASOS ESPECIALES
# # ============================================================
# def _horario_str(inicio: time, fin: time) -> str:
#     return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

# def aplicar_casos_especiales(df: pd.DataFrame, reglas: dict) -> pd.DataFrame:
#     df = df.copy()

#     # A) Ediciones puntuales
#     for ed in reglas.get("ediciones", []):
#         filtro = ed.get("filtro", {})
#         mask = pd.Series(True, index=df.index)
#         for k, v in filtro.items():
#             mask &= (df[k] == v)
#         for col, val in ed.get("set", {}).items():
#             df.loc[mask, col] = val

#     # B) Trabajo autónomo
#     semanas_auto = set(reglas.get("semanas_trabajo_autonomo", []))
#     if semanas_auto:
#         mask_auto = df["semana"].isin(semanas_auto)
#         df.loc[mask_auto, "actividad"] = "Trabajo autónomo"
#         df.loc[mask_auto, "observaciones"] = "No hay clases (trabajo autónomo)."

#     # C) Feriados
#     feriados = reglas.get("feriados", [])
#     if feriados:
#         feriados_map = {pd.Timestamp(f["fecha"]).date(): f["nombre"] for f in feriados}
#         mask_fer = df["fecha"].isin(list(feriados_map.keys()))
#         df.loc[mask_fer, "actividad"] = "Sin clases (Feriado)"
#         df.loc[mask_fer, "observaciones"] = df.loc[mask_fer, "fecha"].map(feriados_map)

#     # D) Exámenes
#     semanas_ex = set(reglas.get("semanas_examenes", []))
#     if semanas_ex:
#         ref = pd.Timestamp(str(df["fecha"].min()))
#         df = df[~df["semana"].isin(semanas_ex)].copy()

#         nuevos = []
#         for ev in reglas.get("eventos_examenes", []):
#             fecha_ts = pd.Timestamp(ev["fecha"])
#             fecha = fecha_ts.date()
#             semana_ev = int((fecha_ts - ref).days // 7) + 1

#             nuevos.append({
#                 "semana": semana_ev,
#                 "fecha": fecha,
#                 "día": {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}[fecha_ts.weekday()],
#                 "horario": _horario_str(ev["inicio"], ev["fin"]),
#                 "sección": ev["sección"],
#                 "actividad": ev["actividad"],
#                 "tema": ev.get("tema", ""),
#                 "evaluación": ev.get("evaluación", ""),
#                 "profesores": ev.get("profesores", ""),
#                 "observaciones": ev.get("observaciones", "")
#             })

#         if nuevos:
#             df = pd.concat([df, pd.DataFrame(nuevos)], ignore_index=True)

#     # Orden final
#     def _inicio(h): return h.split("–")[0] if isinstance(h, str) and "–" in h else "00:00"
#     df["_inicio_dt"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].apply(_inicio), errors="coerce")
#     df = df.sort_values(["sección", "fecha", "_inicio_dt"], na_position="last").drop(columns=["_inicio_dt"])

#     return df


# # ============================================================
# # FullCalendar events (tema visible + evaluación destacada)
# # ============================================================
# def df_a_fullcalendar_events(df: pd.DataFrame):
#     colores = {
#         "Clase teórica": "#1f77b4",
#         "Seminario": "#2ca02c",
#         "Laboratorio": "#ff7f0e",
#         "Trabajo autónomo": "#9467bd",
#         "Sin clases (Feriado)": "#d62728",
#         "Examen": "#111111",
#     }

#     iconos_eval = {
#         "Prueba": "⭐",
#         "Experimento": "🧪",
#         "Trabajo práctico": "📝",
#     }

#     colores_eval = {
#         "Prueba": "#d62728",
#         "Experimento": "#9467bd",
#         "Trabajo práctico": "#2ca02c",
#     }

#     def parse_horario(h):
#         a, b = h.split("–")
#         hi = pd.to_datetime(a, format="%H:%M").time()
#         hf = pd.to_datetime(b, format="%H:%M").time()
#         return hi, hf

#     events = []
#     for _, r in df.iterrows():
#         hi, hf = parse_horario(r["horario"])
#         start = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
#         end   = pd.Timestamp(str(r["fecha"])) + pd.Timedelta(hours=hf.hour, minutes=hf.minute)

#         tema = str(r.get("tema", "")).strip()
#         evaluacion = str(r.get("evaluación", "")).strip()
#         profs = str(r.get("profesores", "")).strip()
#         obs = str(r.get("observaciones", "")).strip()

#         icono = iconos_eval.get(evaluacion, "")
#         pref = f"{icono} " if icono else ""

#         # título: actividad + tema (si existe)
#         if tema:
#             title = f"{pref}{r['actividad']} · {tema}"
#         else:
#             title = f"{pref}{r['actividad']}"

#         color_evento = colores_eval.get(evaluacion, colores.get(r["actividad"], "#888888"))

#         events.append({
#             "title": title,
#             "start": start.isoformat(),
#             "end": end.isoformat(),
#             "color": color_evento,
#             "extendedProps": {
#                 "semana": r.get("semana", ""),
#                 "día": r.get("día", ""),
#                 "horario": r.get("horario", ""),
#                 "sección": r.get("sección", ""),
#                 "actividad": r.get("actividad", ""),
#                 "tema": tema,
#                 "evaluación": evaluacion,
#                 "profesores": profs,
#                 "observaciones": obs,
#             }
#         })
#     return events


# # ============================================================
# # UI Streamlit (sin sidebar)
# # ============================================================
# st.set_page_config(page_title="Calendario del Curso", layout="wide")

# st.title("📅 Calendario del Curso")
# st.caption("Calendario + tabla + exportación. Evaluaciones destacadas con íconos.")

# df = crear_calendario_curso(FECHA_INICIO, NUMERO_SEMANAS)
# CASOS_ESPECIALES["feriados"] = feriados_chile_entre(df["fecha"].min(), df["fecha"].max())
# df = aplicar_casos_especiales(df, CASOS_ESPECIALES)

# # Validaciones suaves
# if not df["evaluación"].fillna("").isin(EVAL_VALIDAS).all():
#     st.warning("Hay evaluaciones fuera de las permitidas (Prueba, Experimento, Trabajo práctico).")

# def profes_ok(s):
#     s = str(s).strip()
#     if not s:
#         return True
#     tokens = [t.strip() for t in s.split(",")]
#     return all(t in PROFES_VALIDOS for t in tokens if t)

# if not df["profesores"].apply(profes_ok).all():
#     st.warning("Hay profesores fuera de la lista permitida. Ajusta PROFES_VALIDOS o corrige CASOS_ESPECIALES.")

# # Filtros (arriba, visibles para todos)
# colf1, colf2, colf3, colf4 = st.columns([1.2, 1.0, 1.0, 1.0])

# with colf1:
#     secciones = sorted(df["sección"].unique())
#     seccion_sel = st.multiselect("Secciones", options=secciones, default=secciones)

# with colf2:
#     semanas = sorted(df["semana"].unique())
#     semana_sel = st.multiselect("Semanas", options=semanas, default=semanas)

# with colf3:
#     actividad_sel = st.multiselect(
#         "Actividad",
#         options=sorted(df["actividad"].unique()),
#         default=sorted(df["actividad"].unique())
#     )

# with colf4:
#     eval_opts = ["(Todas)", "Prueba", "Experimento", "Trabajo práctico"]
#     eval_sel = st.selectbox("Evaluación", options=eval_opts, index=0)

# df_f = df[
#     df["sección"].isin(seccion_sel)
#     & df["semana"].isin(semana_sel)
#     & df["actividad"].isin(actividad_sel)
# ].copy()

# if eval_sel != "(Todas)":
#     df_f = df_f[df_f["evaluación"] == eval_sel].copy()

# # Tabs
# tab1, tab2, tab3, tab4 = st.tabs(["Calendario", "Tabla", "Gráficos", "Exportar"])

# with tab1:
#     st.subheader("🗓️ Vista calendario")

#     events = df_a_fullcalendar_events(df_f)

#     initial_date = pd.Timestamp(df_f["fecha"].min()).strftime("%Y-%m-%d") if len(df_f) else FECHA_INICIO

#     calendar_options = {
#         "initialView": "timeGridWeek",
#         "initialDate": initial_date,
#         "headerToolbar": {
#             "left": "prev,next today",
#             "center": "title",
#             "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
#         },
#         "height": 850,
#         "contentHeight": "auto",
#         "slotMinTime": "07:00:00",
#         "slotMaxTime": "22:00:00",
#         "scrollTime": "08:00:00",
#         "slotDuration": "00:30:00",
#         "snapDuration": "00:15:00",
#         "selectable": True,
#         "editable": False,
#         "nowIndicator": True,
#         "weekNumbers": True,
#         "dayMaxEvents": True,
#     }

#     state = calendar(events=events, options=calendar_options)

#     st.divider()
#     st.subheader("🔎 Detalles (clic en un evento)")

#     event_click = state.get("eventClick") if isinstance(state, dict) else None
#     if event_click:
#         ev = event_click.get("event", {})
#         props = ev.get("extendedProps", {})
#         st.success("Evento seleccionado")
#         st.write({
#             "Título": ev.get("title", ""),
#             "Inicio": ev.get("start", ""),
#             "Fin": ev.get("end", ""),
#             "Sección": props.get("sección", ""),
#             "Actividad": props.get("actividad", ""),
#             "Tema": props.get("tema", ""),
#             "Evaluación": props.get("evaluación", ""),
#             "Profesores": props.get("profesores", ""),
#             "Semana": props.get("semana", ""),
#             "Día": props.get("día", ""),
#             "Horario": props.get("horario", ""),
#             "Observaciones": props.get("observaciones", ""),
#         })
#     else:
#         st.caption("Tip: haz clic en un evento para ver tema, evaluación y profesores.")

# with tab2:
#     st.subheader("🧾 Tabla")
#     st.write(f"Eventos: **{len(df_f)}**")
#     st.dataframe(
#         df_f,
#         use_container_width=True,
#         hide_index=True,
#         column_config={
#             "fecha": st.column_config.DateColumn(format="DD/MM/YYYY"),
#         }
#     )

# with tab3:
#     st.subheader("📈 Gráficos")

#     df_count = df_f.groupby(["semana", "actividad"], as_index=False).size()
#     fig1 = px.bar(df_count, x="semana", y="size", color="actividad", barmode="group")
#     st.plotly_chart(fig1, use_container_width=True)

#     orden_dias_es = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
#     df_dias = df_f.groupby(["día"], as_index=False).size()
#     df_dias["día"] = pd.Categorical(df_dias["día"], categories=orden_dias_es, ordered=True)
#     df_dias = df_dias.sort_values("día")
#     fig2 = px.bar(df_dias, x="día", y="size")
#     st.plotly_chart(fig2, use_container_width=True)

# with tab4:
#     st.subheader("⬇️ Exportar")

#     excel_bytes = df_a_excel_bytes(df_f)
#     st.download_button(
#         label="Descargar Excel (.xlsx)",
#         data=excel_bytes,
#         file_name="calendario_filtrado.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

#     st.divider()
#     st.caption("Opcional: exportar a .ics (Google Calendar / Apple Calendar). Requiere `pip install ics`.")

#     export_ics = st.checkbox("Habilitar exportación ICS", value=False)
#     tz = st.text_input("Timezone", value="America/Santiago")

#     if export_ics:
#         try:
#             ics_bytes = df_a_ics_bytes(df_f, tz=tz)
#             st.download_button(
#                 label="Descargar calendario (.ics)",
#                 data=ics_bytes,
#                 file_name="calendario_filtrado.ics",
#                 mime="text/calendar"
#             )
#         except Exception as e:
#             st.error(str(e))




# import io
# import pandas as pd
# import streamlit as st
# import plotly.express as px
# from datetime import time
# from streamlit_calendar import calendar
# import holidays

# # ============================================================
# # CONFIG FIJA
# # ============================================================
# FECHA_INICIO = "2026-03-16"
# NUMERO_SEMANAS = 20

# # ============================================================
# # Generador de calendario (CLASES) - NO cambies horarios/fechas
# # ============================================================
# def crear_calendario_curso(
#     fecha_inicio=FECHA_INICIO,
#     numero_semanas=NUMERO_SEMANAS,
# ):
#     secciones = {
#         "Sección 1": {
#             "teorica":   {"dia_semana": "Monday",    "inicio": time(12, 0),  "fin": time(13, 30)},
#             "seminario": {"dia_semana": "Wednesday", "inicio": time(15, 0),  "fin": time(16, 30)},
#             "lab":       {"dia_semana": "Wednesday", "inicio": time(16, 45), "fin": time(18, 15)},
#         },
#         "Sección 2": {
#             "teorica":   {"dia_semana": "Monday", "inicio": time(16, 45), "fin": time(18, 15)},
#             "seminario": {"dia_semana": "Friday", "inicio": time(8, 30),  "fin": time(10, 0)},
#             "lab":       {"dia_semana": "Monday", "inicio": time(15, 0),  "fin": time(16, 30)},
#         },
#         "Sección 3": {
#             "teorica":   {"dia_semana": "Wednesday", "inicio": time(16, 45), "fin": time(18, 15)},
#             "seminario": {"dia_semana": "Friday",    "inicio": time(10, 15), "fin": time(11, 45)},
#             "lab":       {"dia_semana": "Friday",    "inicio": time(12, 0),  "fin": time(13, 30)},
#         },
#         "Sección 4": {
#             "teorica":   {"dia_semana": "Wednesday", "inicio": time(15, 0),  "fin": time(16, 30)},
#             "seminario": {"dia_semana": "Friday",    "inicio": time(8, 30),  "fin": time(10, 0)},
#             "lab":       {"dia_semana": "Friday",    "inicio": time(10, 15), "fin": time(11, 45)},
#         },
#     }

#     orden_dias = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
#     dias_es = {
#         "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
#         "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
#     }

#     def fecha_de_dia_en_semana(ancla_semana, dia_semana):
#         idx = orden_dias.index(dia_semana)  # Monday=0 ... Sunday=6
#         return pd.Timestamp(ancla_semana.date()) + pd.Timedelta(days=idx)

#     def rango_horario_str(inicio, fin):
#         return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

#     fecha_inicio = pd.Timestamp(fecha_inicio)
#     filas = []

#     for seccion, cfg in secciones.items():
#         for semana in range(1, numero_semanas + 1):
#             ancla = fecha_inicio + pd.Timedelta(days=7*(semana-1))  # lunes

#             # Teórica + Seminario
#             for clave, nombre in [("teorica","Clase teórica"), ("seminario","Seminario")]:
#                 dia_semana = cfg[clave]["dia_semana"]
#                 fecha_evento = fecha_de_dia_en_semana(ancla, dia_semana).date()
#                 horario = rango_horario_str(cfg[clave]["inicio"], cfg[clave]["fin"])

#                 filas.append({
#                     "semana": semana,
#                     "fecha": fecha_evento,
#                     "día": dias_es[dia_semana],
#                     "horario": horario,
#                     "sección": seccion,
#                     "actividad": nombre,
#                     "tema": "",
#                     "evaluación": "",
#                     "profesores": "",
#                     "misiones": "",          # NUEVO
#                     "observaciones": ""
#                 })

#             # Laboratorio semanas pares
#             if semana % 2 == 0:
#                 dia_semana = cfg["lab"]["dia_semana"]
#                 fecha_evento = fecha_de_dia_en_semana(ancla, dia_semana).date()
#                 horario = rango_horario_str(cfg["lab"]["inicio"], cfg["lab"]["fin"])

#                 filas.append({
#                     "semana": semana,
#                     "fecha": fecha_evento,
#                     "día": dias_es[dia_semana],
#                     "horario": horario,
#                     "sección": seccion,
#                     "actividad": "Laboratorio",
#                     "tema": "",
#                     "evaluación": "",
#                     "profesores": "",
#                     "misiones": "",
#                     "observaciones": "Cada 2 semanas"
#                 })

#     df = pd.DataFrame(filas)

#     def extraer_inicio(h): return h.split("–")[0]
#     df["_inicio_dt"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].apply(extraer_inicio))
#     df = df.sort_values(["sección", "semana", "_inicio_dt"]).drop(columns=["_inicio_dt"])

#     return df


# # ============================================================
# # Exportar Excel
# # ============================================================
# def df_a_excel_bytes(df: pd.DataFrame) -> bytes:
#     buffer = io.BytesIO()
#     with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
#         df.to_excel(writer, index=False, sheet_name="Calendario")
#     return buffer.getvalue()


# # ============================================================
# # Feriados Chile automáticos (rango del curso)
# # ============================================================
# def feriados_chile_entre(fecha_min, fecha_max):
#     fmin = pd.Timestamp(fecha_min).date()
#     fmax = pd.Timestamp(fecha_max).date()
#     years = list(range(fmin.year, fmax.year + 1))
#     cl = holidays.country_holidays("CL", years=years)
#     lista = []
#     for d, nombre in cl.items():
#         if fmin <= d <= fmax:
#             lista.append({"fecha": pd.Timestamp(d).strftime("%Y-%m-%d"), "nombre": str(nombre)})
#     return sorted(lista, key=lambda x: x["fecha"])


# # ============================================================
# # CASOS ESPECIALES (EDITA AQUÍ)
# # ============================================================
# CASOS_ESPECIALES = {
#     "ediciones": [
#         # ejemplo
#         {
#             "filtro": {"sección": "Sección 2", "semana": 1, "actividad": "Laboratorio"},
#             "set": {"observaciones": "No hay sala de computación esta semana (plan B)."}
#         },
#         # demo para ver "tema", "evaluación", "profesores"
#         {
#             "filtro": {"sección": "Sección 1", "semana": 1, "actividad": "Clase teórica"},
#             "set": {"tema": "Trigonometría", "profesores": "TY", "observaciones": "Introducción"}
#         },
#         {
#             "filtro": {"sección": "Sección 4", "semana": 8, "actividad": "Clase teórica"},
#             "set": {"evaluación": "Prueba", "profesores": "IG", "observaciones": "Duración: 45 min"}
#         },
#     ],

#     "semanas_trabajo_autonomo": [16],
#     "feriados": [],

#     "semanas_examenes": [17, 18],
#     "eventos_examenes": [
#         {"sección": "Sección 1", "fecha": "2026-07-06", "inicio": time(9, 0),  "fin": time(11, 0),
#          "actividad": "Examen", "observaciones": "Examen final", "profesores": "TY"},
#         {"sección": "Sección 2", "fecha": "2026-07-07", "inicio": time(16, 0), "fin": time(18, 0),
#          "actividad": "Examen", "observaciones": "Examen final", "profesores": "IG"},
#         {"sección": "Sección 3", "fecha": "2026-07-08", "inicio": time(10, 0), "fin": time(12, 0),
#          "actividad": "Examen", "observaciones": "Examen final", "profesores": "CC"},
#         {"sección": "Sección 4", "fecha": "2026-07-09", "inicio": time(18, 0), "fin": time(20, 0),
#          "actividad": "Examen", "observaciones": "Examen final", "profesores": "AR, JCS"},
#     ],

#     # 👇 NUEVO: misiones (sin horario, se verán como all-day)
#     # misiones permitidas: propuesta de preguntas, revisión taller, revisión prueba
#     "eventos_misiones": [
#         {
#             "fecha": "2026-04-10",
#             "sección": "Equipo docente",      # o una sección específica
#             "misiones": "Propuesta de preguntas",
#             "profesores": "TY, IG",
#             "observaciones": "Subir documento a carpeta compartida"
#         },
#         {
#             "fecha": "2026-05-08",
#             "sección": "Equipo docente",
#             "misiones": "Revisión prueba",
#             "profesores": "IG",
#             "observaciones": "Enviar versión final"
#         },
#         {
#             "fecha": "2026-06-05",
#             "sección": "Equipo docente",
#             "misiones": "Revisión taller",
#             "profesores": "CC, AR",
#             "observaciones": "Revisar guía y pauta"
#         },
#     ],
# }


# # ============================================================
# # APLICADOR DE CASOS ESPECIALES
# # ============================================================
# def _horario_str(inicio: time, fin: time) -> str:
#     return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

# def aplicar_casos_especiales(df: pd.DataFrame, reglas: dict) -> pd.DataFrame:
#     df = df.copy()

#     # A) Ediciones puntuales
#     for ed in reglas.get("ediciones", []):
#         filtro = ed.get("filtro", {})
#         mask = pd.Series(True, index=df.index)
#         for k, v in filtro.items():
#             mask &= (df[k] == v)
#         for col, val in ed.get("set", {}).items():
#             df.loc[mask, col] = val

#     # B) Trabajo autónomo
#     semanas_auto = set(reglas.get("semanas_trabajo_autonomo", []))
#     if semanas_auto:
#         mask_auto = df["semana"].isin(semanas_auto)
#         df.loc[mask_auto, "actividad"] = "Trabajo autónomo"
#         df.loc[mask_auto, "observaciones"] = "No hay clases (trabajo autónomo)."

#     # C) Feriados
#     feriados = reglas.get("feriados", [])
#     if feriados:
#         feriados_map = {pd.Timestamp(f["fecha"]).date(): f["nombre"] for f in feriados}
#         mask_fer = df["fecha"].isin(list(feriados_map.keys()))
#         df.loc[mask_fer, "actividad"] = "Sin clases (Feriado)"
#         df.loc[mask_fer, "observaciones"] = df.loc[mask_fer, "fecha"].map(feriados_map)

#     # D) Exámenes: borra clases regulares en esas semanas + inserta exámenes
#     semanas_ex = set(reglas.get("semanas_examenes", []))
#     if semanas_ex:
#         ref = pd.Timestamp(str(df["fecha"].min()))
#         df = df[~df["semana"].isin(semanas_ex)].copy()

#         nuevos = []
#         for ev in reglas.get("eventos_examenes", []):
#             fecha_ts = pd.Timestamp(ev["fecha"])
#             semana_ev = int((fecha_ts - ref).days // 7) + 1
#             nuevos.append({
#                 "semana": semana_ev,
#                 "fecha": fecha_ts.date(),
#                 "día": {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}[fecha_ts.weekday()],
#                 "horario": _horario_str(ev["inicio"], ev["fin"]),
#                 "sección": ev["sección"],
#                 "actividad": ev["actividad"],
#                 "tema": ev.get("tema", ""),
#                 "evaluación": ev.get("evaluación", ""),
#                 "profesores": ev.get("profesores", ""),
#                 "misiones": "",
#                 "observaciones": ev.get("observaciones", "")
#             })
#         if nuevos:
#             df = pd.concat([df, pd.DataFrame(nuevos)], ignore_index=True)

#     # E) Misiones: insertar filas sin horario (quedan como all-day en el calendario)
#     misiones = reglas.get("eventos_misiones", [])
#     if misiones:
#         ref = pd.Timestamp(str(df["fecha"].min()))
#         nuevos = []
#         for m in misiones:
#             fecha_ts = pd.Timestamp(m["fecha"])
#             semana_ev = int((fecha_ts - ref).days // 7) + 1
#             nuevos.append({
#                 "semana": semana_ev,
#                 "fecha": fecha_ts.date(),
#                 "día": {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}[fecha_ts.weekday()],
#                 "horario": "",  # clave: vacío => lo tratamos como all-day
#                 "sección": m.get("sección", "Equipo docente"),
#                 "actividad": "Misión",
#                 "tema": "",
#                 "evaluación": "",
#                 "profesores": m.get("profesores", ""),
#                 "misiones": m.get("misiones", ""),
#                 "observaciones": m.get("observaciones", "")
#             })
#         df = pd.concat([df, pd.DataFrame(nuevos)], ignore_index=True)

#     # Orden final
#     def _inicio(h): return h.split("–")[0] if isinstance(h, str) and "–" in h else "00:00"
#     df["_inicio_dt"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].fillna("").apply(_inicio), errors="coerce")
#     df = df.sort_values(["sección", "fecha", "_inicio_dt"], na_position="last").drop(columns=["_inicio_dt"])

#     return df


# # ============================================================
# # FullCalendar: clases con horario, misiones como all-day
# # ============================================================
# def df_a_fullcalendar_events(df: pd.DataFrame):
#     colores_actividad = {
#         "Clase teórica": "#1f77b4",
#         "Seminario": "#2ca02c",
#         "Laboratorio": "#ff7f0e",
#         "Trabajo autónomo": "#9467bd",
#         "Sin clases (Feriado)": "#d62728",
#         "Examen": "#111111",
#         "Misión": "#8c564b",
#     }

#     iconos_eval = {"Prueba": "⭐", "Experimento": "🧪", "Trabajo práctico": "📝"}
#     colores_eval = {"Prueba": "#d62728", "Experimento": "#9467bd", "Trabajo práctico": "#2ca02c"}

#     iconos_mision = {"Propuesta de preguntas": "💡", "Revisión taller": "🧰", "Revisión prueba": "🔎"}

#     def parse_horario(h):
#         a, b = h.split("–")
#         hi = pd.to_datetime(a, format="%H:%M").time()
#         hf = pd.to_datetime(b, format="%H:%M").time()
#         return hi, hf

#     events = []
#     for _, r in df.iterrows():
#         fecha = pd.Timestamp(str(r["fecha"]))
#         horario = str(r.get("horario", "") or "").strip()

#         tema = str(r.get("tema", "")).strip()
#         evaluacion = str(r.get("evaluación", "")).strip()
#         profs = str(r.get("profesores", "")).strip()
#         obs = str(r.get("observaciones", "")).strip()
#         mision_txt = str(r.get("misiones", "")).strip()
#         actividad = str(r.get("actividad", "")).strip()

#         # --- MISIÓN (all-day, no bloquea horas) ---
#         if actividad == "Misión":
#             ic = iconos_mision.get(mision_txt, "📌")
#             title = f"{ic} {mision_txt}" if mision_txt else f"{ic} Misión"
#             # start/end como all-day: end exclusivo => +1 día
#             start = fecha.date().isoformat()
#             end = (fecha + pd.Timedelta(days=1)).date().isoformat()
#             events.append({
#                 "title": title,
#                 "start": start,
#                 "end": end,
#                 "allDay": True,
#                 "color": colores_actividad["Misión"],
#                 "extendedProps": {
#                     "tipo": "mision",
#                     "semana": r.get("semana", ""),
#                     "sección": r.get("sección", ""),
#                     "misiones": mision_txt,
#                     "profesores": profs,
#                     "observaciones": obs,
#                 }
#             })
#             continue

#         # --- Eventos con horario normal ---
#         if "–" in horario:
#             hi, hf = parse_horario(horario)
#             start_dt = fecha + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
#             end_dt   = fecha + pd.Timedelta(hours=hf.hour, minutes=hf.minute)
#             start = start_dt.isoformat()
#             end = end_dt.isoformat()
#             all_day = False
#         else:
#             # fallback all-day (no debería pasar en clases)
#             start = fecha.date().isoformat()
#             end = (fecha + pd.Timedelta(days=1)).date().isoformat()
#             all_day = True

#         icono = iconos_eval.get(evaluacion, "")
#         pref = f"{icono} " if icono else ""

#         if tema:
#             title = f"{pref}{actividad} · {tema}"
#         else:
#             title = f"{pref}{actividad}"

#         color_evento = colores_eval.get(evaluacion, colores_actividad.get(actividad, "#888888"))

#         events.append({
#             "title": title,
#             "start": start,
#             "end": end,
#             "allDay": all_day,
#             "color": color_evento,
#             "extendedProps": {
#                 "tipo": "clase",
#                 "semana": r.get("semana", ""),
#                 "día": r.get("día", ""),
#                 "horario": horario,
#                 "sección": r.get("sección", ""),
#                 "actividad": actividad,
#                 "tema": tema,
#                 "evaluación": evaluacion,
#                 "profesores": profs,
#                 "observaciones": obs,
#             }
#         })

#     return events


# # ============================================================
# # UI Streamlit
# # ============================================================
# st.set_page_config(page_title="Calendario del Curso", layout="wide")
# st.title("📅 Calendario del Curso + Misiones")
# st.caption("Misiones se muestran como all-day (arriba) para NO bloquear la grilla horaria.")

# df = crear_calendario_curso(FECHA_INICIO, NUMERO_SEMANAS)
# CASOS_ESPECIALES["feriados"] = feriados_chile_entre(df["fecha"].min(), df["fecha"].max())
# df = aplicar_casos_especiales(df, CASOS_ESPECIALES)

# # Filtros (visibles)
# colf1, colf2, colf3 = st.columns([1.2, 1.0, 1.0])
# with colf1:
#     secciones = sorted(df["sección"].unique())
#     seccion_sel = st.multiselect("Secciones", options=secciones, default=secciones)
# with colf2:
#     semanas = sorted(df["semana"].unique())
#     semana_sel = st.multiselect("Semanas", options=semanas, default=semanas)
# with colf3:
#     actividad_sel = st.multiselect(
#         "Actividad",
#         options=sorted(df["actividad"].unique()),
#         default=sorted(df["actividad"].unique())
#     )

# df_f = df[
#     df["sección"].isin(seccion_sel)
#     & df["semana"].isin(semana_sel)
#     & df["actividad"].isin(actividad_sel)
# ].copy()

# tab1, tab2, tab3 = st.tabs(["Calendario", "Tabla", "Exportar"])

# with tab1:
#     events = df_a_fullcalendar_events(df_f)
#     initial_date = pd.Timestamp(df_f["fecha"].min()).strftime("%Y-%m-%d") if len(df_f) else FECHA_INICIO

#     calendar_options = {
#         "initialView": "timeGridWeek",
#         "initialDate": initial_date,
#         "headerToolbar": {
#             "left": "prev,next today",
#             "center": "title",
#             "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
#         },
#         "height": 850,
#         "contentHeight": "auto",
#         "slotMinTime": "07:00:00",
#         "slotMaxTime": "22:00:00",
#         "scrollTime": "08:00:00",
#         "slotDuration": "00:30:00",
#         "snapDuration": "00:15:00",
#         "selectable": True,
#         "editable": False,
#         "nowIndicator": True,
#         "weekNumbers": True,
#         "dayMaxEvents": True,
#     }

#     state = calendar(events=events, options=calendar_options)

#     st.divider()
#     st.subheader("🔎 Detalles (clic en un evento)")
#     event_click = state.get("eventClick") if isinstance(state, dict) else None
#     if event_click:
#         ev = event_click.get("event", {})
#         props = ev.get("extendedProps", {})
#         st.write({
#             "Título": ev.get("title", ""),
#             "Inicio": ev.get("start", ""),
#             "Fin": ev.get("end", ""),
#             "Tipo": props.get("tipo", ""),
#             "Sección": props.get("sección", ""),
#             "Actividad": props.get("actividad", ""),
#             "Misión": props.get("misiones", ""),
#             "Tema": props.get("tema", ""),
#             "Evaluación": props.get("evaluación", ""),
#             "Profesores": props.get("profesores", ""),
#             "Observaciones": props.get("observaciones", ""),
#             "Semana": props.get("semana", ""),
#         })
#     else:
#         st.caption("Clickea una clase o misión para ver detalles.")

# with tab2:
#     st.subheader("🧾 Tabla")
#     st.dataframe(df_f, use_container_width=True, hide_index=True,
#                  column_config={"fecha": st.column_config.DateColumn(format="DD/MM/YYYY")})

# with tab3:
#     st.subheader("⬇️ Exportar")
#     excel_bytes = df_a_excel_bytes(df_f)
#     st.download_button(
#         label="Descargar Excel (.xlsx)",
#         data=excel_bytes,
#         file_name="calendario_filtrado.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )




import io
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import time
from streamlit_calendar import calendar
import holidays

# ============================================================
# CONFIG FIJA
# ============================================================
FECHA_INICIO = "2026-03-16"
NUMERO_SEMANAS = 19

# ============================================================
# Generador de calendario (CLASES) - NO cambies horarios/fechas
# ============================================================
def crear_calendario_curso(
    fecha_inicio=FECHA_INICIO,
    numero_semanas=NUMERO_SEMANAS,
):
    secciones = {
        "Sección 1": {
            "teorica":   {"dia_semana": "Monday",    "inicio": time(12, 0),  "fin": time(13, 30)},
            "seminario": {"dia_semana": "Wednesday", "inicio": time(15, 0),  "fin": time(16, 30)},
            "lab":       {"dia_semana": "Wednesday", "inicio": time(16, 45), "fin": time(18, 15)},
        },
        "Sección 2": {
            "teorica":   {"dia_semana": "Monday", "inicio": time(16, 45), "fin": time(18, 15)},
            "seminario": {"dia_semana": "Friday", "inicio": time(8, 30),  "fin": time(10, 0)},
            "lab":       {"dia_semana": "Monday", "inicio": time(15, 0),  "fin": time(16, 30)},
        },
        "Sección 3": {
            "teorica":   {"dia_semana": "Wednesday", "inicio": time(16, 45), "fin": time(18, 15)},
            "seminario": {"dia_semana": "Friday",    "inicio": time(10, 15), "fin": time(11, 45)},
            "lab":       {"dia_semana": "Friday",    "inicio": time(12, 0),  "fin": time(13, 30)},
        },
        "Sección 4": {
            "teorica":   {"dia_semana": "Wednesday", "inicio": time(15, 0),  "fin": time(16, 30)},
            "seminario": {"dia_semana": "Friday",    "inicio": time(8, 30),  "fin": time(10, 0)},
            "lab":       {"dia_semana": "Friday",    "inicio": time(10, 15), "fin": time(11, 45)},
        },
    }

    orden_dias = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dias_es = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }

    def fecha_de_dia_en_semana(ancla_semana, dia_semana):
        idx = orden_dias.index(dia_semana)  # Monday=0 ... Sunday=6
        return pd.Timestamp(ancla_semana.date()) + pd.Timedelta(days=idx)

    def rango_horario_str(inicio, fin):
        return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

    fecha_inicio = pd.Timestamp(fecha_inicio)
    filas = []

    for seccion, cfg in secciones.items():
        for semana in range(1, numero_semanas + 1):
            ancla = fecha_inicio + pd.Timedelta(days=7*(semana-1))  # lunes

            # Teórica + Seminario
            for clave, nombre in [("teorica","Clase teórica"), ("seminario","Seminario")]:
                dia_semana = cfg[clave]["dia_semana"]
                fecha_evento = fecha_de_dia_en_semana(ancla, dia_semana).date()
                horario = rango_horario_str(cfg[clave]["inicio"], cfg[clave]["fin"])

                filas.append({
                    "semana": semana,
                    "fecha": fecha_evento,
                    "día": dias_es[dia_semana],
                    "horario": horario,
                    "sección": seccion,
                    "actividad": nombre,
                    "tema": "",
                    "evaluación": "",
                    "profesores": "",
                    "misiones": "",
                    "observaciones": ""
                })

            # Laboratorio semanas pares
            if semana % 2 == 0:
                dia_semana = cfg["lab"]["dia_semana"]
                fecha_evento = fecha_de_dia_en_semana(ancla, dia_semana).date()
                horario = rango_horario_str(cfg["lab"]["inicio"], cfg["lab"]["fin"])

                filas.append({
                    "semana": semana,
                    "fecha": fecha_evento,
                    "día": dias_es[dia_semana],
                    "horario": horario,
                    "sección": seccion,
                    "actividad": "Laboratorio",
                    "tema": "",
                    "evaluación": "",
                    "profesores": "",
                    "misiones": "",
                    "observaciones": "Cada 2 semanas"
                })

    df = pd.DataFrame(filas)

    def extraer_inicio(h): return h.split("–")[0]
    df["_inicio_dt"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].apply(extraer_inicio))
    df = df.sort_values(["sección", "semana", "_inicio_dt"]).drop(columns=["_inicio_dt"])

    return df


# ============================================================
# Exportar Excel
# ============================================================
def df_a_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Calendario")
    return buffer.getvalue()


# ============================================================
# Feriados Chile automáticos (rango del curso)
# ============================================================
def feriados_chile_entre(fecha_min, fecha_max):
    fmin = pd.Timestamp(fecha_min).date()
    fmax = pd.Timestamp(fecha_max).date()
    years = list(range(fmin.year, fmax.year + 1))
    cl = holidays.country_holidays("CL", years=years)
    lista = []
    for d, nombre in cl.items():
        if fmin <= d <= fmax:
            lista.append({"fecha": pd.Timestamp(d).strftime("%Y-%m-%d"), "nombre": str(nombre)})
    return sorted(lista, key=lambda x: x["fecha"])


# ============================================================
# CASOS ESPECIALES (EDITA AQUÍ)
# ============================================================

# Horarios por bloque protegido (AJUSTA a lo real de tu facultad)
# Si no coincide, el “cruce” no se detectará correctamente.
HORARIOS_BLOQUES = {
    "Bloque 3": {"inicio": time(12, 0), "fin": time(13, 30)},
    "Bloque 4": {"inicio": time(15, 0), "fin": time(16, 30)},
}

CASOS_ESPECIALES = {
    "ediciones": [
        # ejemplo
        {
            "filtro": {"sección": "Sección 2", "semana": 1, "actividad": "Laboratorio"},
            "set": {"observaciones": "No hay sala de computación esta semana (plan B)."}
        },
        # demo
        {
            "filtro": {"sección": "Sección 1", "semana": 1, "actividad": "Clase teórica"},
            "set": {"tema": "Trigonometría", "profesores": "TY", "observaciones": "Introducción"}
        },
        {
            "filtro": {"sección": "Sección 4", "semana": 8, "actividad": "Clase teórica"},
            "set": {"evaluación": "Prueba", "profesores": "IG", "observaciones": "Duración: 45 min"}
        },
    ],

    # Semana trabajo autónomo (tu regla)
    "semanas_trabajo_autonomo": [17],

    # Feriados (se llenan automáticamente abajo)
    "feriados": [],

    # Exámenes (tu regla)
    "semanas_examenes": [18, 19],
    "eventos_examenes": [
        {"sección": "Sección 1", "fecha": "2026-07-13", "inicio": time(12, 0),  "fin": time(13, 30),
         "actividad": "Examen", "observaciones": "Examen de Primera Oportunidad", "profesores": "TY"},
        {"sección": "Sección 2", "fecha": "2026-07-13", "inicio": time(12, 0),  "fin": time(13, 30),
         "actividad": "Examen", "observaciones": "Examen de Primera Oportunidad", "profesores": "TY"},
        {"sección": "Sección 3", "fecha": "2026-07-13", "inicio": time(12, 0),  "fin": time(13, 30),
         "actividad": "Examen", "observaciones": "Examen de Primera Oportunidad", "profesores": "TY"},
        {"sección": "Sección 4", "fecha": "2026-07-13", "inicio": time(12, 0),  "fin": time(13, 30),
         "actividad": "Examen", "observaciones": "Examen de Primera Oportunidad", "profesores": "TY"},
        {"sección": "Sección 1", "fecha": "2026-07-20", "inicio": time(12, 0),  "fin": time(13, 30),
         "actividad": "Examen", "observaciones": "Examen de Segunda Oportunidad", "profesores": "TY"},
        {"sección": "Sección 2", "fecha": "2026-07-20", "inicio": time(12, 0),  "fin": time(13, 30),
         "actividad": "Examen", "observaciones": "Examen de Segunda Oportunidad", "profesores": "TY"},
        {"sección": "Sección 3", "fecha": "2026-07-20", "inicio": time(12, 0),  "fin": time(13, 30),
         "actividad": "Examen", "observaciones": "Examen de Segunda Oportunidad", "profesores": "TY"},
        {"sección": "Sección 4", "fecha": "2026-07-20", "inicio": time(12, 0),  "fin": time(13, 30),
         "actividad": "Examen", "observaciones": "Examen de Segunda Oportunidad", "profesores": "TY"},
    ],

    # Misiones (se muestran como all-day y NO bloquean la grilla horaria)
    "eventos_misiones": [
        {
            "fecha": "2026-04-10",
            "sección": "Equipo docente",
            "misiones": "Propuesta de preguntas",
            "profesores": "TY, IG",
            "observaciones": "Subir documento a carpeta compartida"
        },
        {
            "fecha": "2026-05-08",
            "sección": "Equipo docente",
            "misiones": "Revisión prueba",
            "profesores": "IG",
            "observaciones": "Enviar versión final"
        },
        {
            "fecha": "2026-06-05",
            "sección": "Equipo docente",
            "misiones": "Revisión taller",
            "profesores": "CC, AR",
            "observaciones": "Revisar guía y pauta"
        },
    ],

    # 👇 NUEVO: rangos sin clases por calendario académico (primer semestre)
    # Semana de pausa: 18 al 24 mayo 2026
    # Vacaciones de invierno: 06 al 12 julio 2026 (por si cae dentro de tu curso)
    "rangos_sin_clases": [
        {"inicio": "2026-05-18", "fin": "2026-05-24", "motivo": "Pausa académica"},
        {"inicio": "2026-07-06", "fin": "2026-07-12", "motivo": "Trabajo Autónomo"},
    ],

    # 👇 NUEVO: Bloques protegidos (fechas exactas + bloque)
    "bloques_protegidos": [
        {"fecha": "2026-04-01", "bloque": "Bloque 3"},
        {"fecha": "2026-05-04", "bloque": "Bloque 4"},
        {"fecha": "2026-06-11", "bloque": "Bloque 3"},
        {"fecha": "2026-06-23", "bloque": "Bloque 4"},
    ],
}


# ============================================================
# APLICADOR DE CASOS ESPECIALES
# ============================================================
def _horario_str(inicio: time, fin: time) -> str:
    return f"{inicio.strftime('%H:%M')}–{fin.strftime('%H:%M')}"

def _parse_horario_str(h: str):
    # retorna (time_inicio, time_fin) o (None, None)
    if not isinstance(h, str) or "–" not in h:
        return None, None
    a, b = h.split("–")
    hi = pd.to_datetime(a, format="%H:%M").time()
    hf = pd.to_datetime(b, format="%H:%M").time()
    return hi, hf

def _overlap(hi1, hf1, hi2, hf2) -> bool:
    # hi/hf son datetime.time
    if hi1 is None or hf1 is None or hi2 is None or hf2 is None:
        return False
    # [hi1, hf1) intersect [hi2, hf2)
    return (hi1 < hf2) and (hi2 < hf1)

def aplicar_casos_especiales(df: pd.DataFrame, reglas: dict) -> pd.DataFrame:
    df = df.copy()

    # A) Ediciones puntuales
    for ed in reglas.get("ediciones", []):
        filtro = ed.get("filtro", {})
        mask = pd.Series(True, index=df.index)
        for k, v in filtro.items():
            mask &= (df[k] == v)
        for col, val in ed.get("set", {}).items():
            df.loc[mask, col] = val

    # B) Trabajo autónomo (por semana)
    semanas_auto = set(reglas.get("semanas_trabajo_autonomo", []))
    if semanas_auto:
        mask_auto = df["semana"].isin(semanas_auto)
        # no tocar misiones (si existieran con semana); aquí solo hay clases
        df.loc[mask_auto, "actividad"] = "Trabajo autónomo"
        df.loc[mask_auto, "observaciones"] = "No hay clases (trabajo autónomo)."

    # C) Feriados
    feriados = reglas.get("feriados", [])
    if feriados:
        feriados_map = {pd.Timestamp(f["fecha"]).date(): f["nombre"] for f in feriados}
        mask_fer = df["fecha"].isin(list(feriados_map.keys()))
        df.loc[mask_fer, "actividad"] = "Sin clases (Feriado)"
        df.loc[mask_fer, "observaciones"] = df.loc[mask_fer, "fecha"].map(feriados_map)
        df.loc[mask_fer, "evaluación"] = ""  # por seguridad

    # D) Rangos sin clases (pausa académica / vacaciones, etc.)
    for r in reglas.get("rangos_sin_clases", []):
        ini = pd.Timestamp(r["inicio"]).date()
        fin = pd.Timestamp(r["fin"]).date()
        motivo = str(r.get("motivo", "Sin clases")).strip()
        mask_r = (df["fecha"] >= ini) & (df["fecha"] <= fin)
        df.loc[mask_r, "actividad"] = f"Sin clases ({motivo})"
        df.loc[mask_r, "observaciones"] = f"{motivo} (según calendario académico)"
        df.loc[mask_r, "evaluación"] = ""

    # E) Bloques protegidos (solo marca las clases que CAEN dentro del bloque protegido)
    # - se aplica por FECHA exacta
    # - y solo si el horario de la clase se cruza con el horario del bloque
    for bp in reglas.get("bloques_protegidos", []):
        fecha_bp = pd.Timestamp(bp["fecha"]).date()
        bloque = str(bp["bloque"]).strip()

        bh = HORARIOS_BLOQUES.get(bloque)
        if not bh:
            continue

        hi_b = bh["inicio"]
        hf_b = bh["fin"]

        mask_fecha = (df["fecha"] == fecha_bp)
        if not mask_fecha.any():
            continue

        # para cada fila ese día, ver si hay overlap con el bloque
        for idx in df[mask_fecha].index:
            hi_c, hf_c = _parse_horario_str(df.at[idx, "horario"])
            if _overlap(hi_c, hf_c, hi_b, hf_b):
                df.at[idx, "actividad"] = "Sin clases (Bloque protegido)"
                df.at[idx, "observaciones"] = f"{bloque} protegido (Facultad)."
                df.at[idx, "evaluación"] = ""

    # F) Exámenes: borra clases regulares en semanas de exámenes + inserta exámenes
    semanas_ex = set(reglas.get("semanas_examenes", []))
    if semanas_ex:
        ref = pd.Timestamp(str(df["fecha"].min()))
        df = df[~df["semana"].isin(semanas_ex)].copy()

        nuevos = []
        for ev in reglas.get("eventos_examenes", []):
            fecha_ts = pd.Timestamp(ev["fecha"])
            semana_ev = int((fecha_ts - ref).days // 7) + 1
            nuevos.append({
                "semana": semana_ev,
                "fecha": fecha_ts.date(),
                "día": {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}[fecha_ts.weekday()],
                "horario": _horario_str(ev["inicio"], ev["fin"]),
                "sección": ev["sección"],
                "actividad": ev["actividad"],
                "tema": ev.get("tema", ""),
                "evaluación": ev.get("evaluación", ""),
                "profesores": ev.get("profesores", ""),
                "misiones": "",
                "observaciones": ev.get("observaciones", "")
            })
        if nuevos:
            df = pd.concat([df, pd.DataFrame(nuevos)], ignore_index=True)

    # G) Misiones: insertar filas all-day
    misiones = reglas.get("eventos_misiones", [])
    if misiones:
        ref = pd.Timestamp(str(df["fecha"].min()))
        nuevos = []
        for m in misiones:
            fecha_ts = pd.Timestamp(m["fecha"])
            semana_ev = int((fecha_ts - ref).days // 7) + 1
            nuevos.append({
                "semana": semana_ev,
                "fecha": fecha_ts.date(),
                "día": {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}[fecha_ts.weekday()],
                "horario": "",
                "sección": m.get("sección", "Equipo docente"),
                "actividad": "Misión",
                "tema": "",
                "evaluación": "",
                "profesores": m.get("profesores", ""),
                "misiones": m.get("misiones", ""),
                "observaciones": m.get("observaciones", "")
            })
        df = pd.concat([df, pd.DataFrame(nuevos)], ignore_index=True)

    # Orden final
    def _inicio(h): return h.split("–")[0] if isinstance(h, str) and "–" in h else "00:00"
    df["_inicio_dt"] = pd.to_datetime(df["fecha"].astype(str) + " " + df["horario"].fillna("").apply(_inicio), errors="coerce")
    df = df.sort_values(["sección", "fecha", "_inicio_dt"], na_position="last").drop(columns=["_inicio_dt"])

    return df


# ============================================================
# FullCalendar: clases con horario, misiones como all-day
# ============================================================
def df_a_fullcalendar_events(df: pd.DataFrame):
    colores_actividad = {
        "Clase teórica": "#1f77b4",
        "Seminario": "#2ca02c",
        "Laboratorio": "#ff7f0e",
        "Trabajo autónomo": "#9467bd",
        "Sin clases (Feriado)": "#d62728",
        "Sin clases (Pausa académica)": "#d62728",
        "Sin clases (Vacaciones de invierno)": "#d62728",
        "Sin clases (Bloque protegido)": "#bcbd22",
        "Examen": "#111111",
        "Misión": "#8c564b",
    }

    iconos_eval = {"Prueba": "⭐", "Experimento": "🧪", "Trabajo práctico": "📝"}
    colores_eval = {"Prueba": "#d62728", "Experimento": "#9467bd", "Trabajo práctico": "#2ca02c"}

    iconos_mision = {"Propuesta de preguntas": "💡", "Revisión taller": "🧰", "Revisión prueba": "🔎"}

    def parse_horario(h):
        a, b = h.split("–")
        hi = pd.to_datetime(a, format="%H:%M").time()
        hf = pd.to_datetime(b, format="%H:%M").time()
        return hi, hf

    events = []
    for _, r in df.iterrows():
        fecha = pd.Timestamp(str(r["fecha"]))
        horario = str(r.get("horario", "") or "").strip()

        tema = str(r.get("tema", "")).strip()
        evaluacion = str(r.get("evaluación", "")).strip()
        profs = str(r.get("profesores", "")).strip()
        obs = str(r.get("observaciones", "")).strip()
        mision_txt = str(r.get("misiones", "")).strip()
        actividad = str(r.get("actividad", "")).strip()

        # MISIÓN all-day
        if actividad == "Misión":
            ic = iconos_mision.get(mision_txt, "📌")
            title = f"{ic} {mision_txt}" if mision_txt else f"{ic} Misión"
            start = fecha.date().isoformat()
            end = (fecha + pd.Timedelta(days=1)).date().isoformat()
            events.append({
                "title": title,
                "start": start,
                "end": end,
                "allDay": True,
                "color": colores_actividad.get("Misión", "#8c564b"),
                "extendedProps": {
                    "tipo": "mision",
                    "semana": r.get("semana", ""),
                    "sección": r.get("sección", ""),
                    "misiones": mision_txt,
                    "profesores": profs,
                    "observaciones": obs,
                }
            })
            continue

        # Eventos con horario
        if "–" in horario:
            hi, hf = parse_horario(horario)
            start_dt = fecha + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
            end_dt   = fecha + pd.Timedelta(hours=hf.hour, minutes=hf.minute)
            start = start_dt.isoformat()
            end = end_dt.isoformat()
            all_day = False
        else:
            start = fecha.date().isoformat()
            end = (fecha + pd.Timedelta(days=1)).date().isoformat()
            all_day = True

        icono = iconos_eval.get(evaluacion, "")
        pref = f"{icono} " if icono else ""

        if tema:
            title = f"{pref}{actividad} · {tema}"
        else:
            title = f"{pref}{actividad}"

        # prioridad color: evaluación > actividad
        color_evento = colores_eval.get(evaluacion, colores_actividad.get(actividad, "#888888"))

        events.append({
            "title": title,
            "start": start,
            "end": end,
            "allDay": all_day,
            "color": color_evento,
            "extendedProps": {
                "tipo": "clase",
                "semana": r.get("semana", ""),
                "día": r.get("día", ""),
                "horario": horario,
                "sección": r.get("sección", ""),
                "actividad": actividad,
                "tema": tema,
                "evaluación": evaluacion,
                "profesores": profs,
                "observaciones": obs,
            }
        })

    return events


# ============================================================
# UI Streamlit
# ============================================================
st.set_page_config(page_title="Calendario del Curso + Pausas/Bloques", layout="wide")
st.title("📅 Calendario del Curso (con Pausa Académica + Bloques Protegidos)")
st.caption("Pausa académica y bloques protegidos se marcan como 'Sin clases' sobre los eventos afectados.")

df = crear_calendario_curso(FECHA_INICIO, NUMERO_SEMANAS)
CASOS_ESPECIALES["feriados"] = feriados_chile_entre(df["fecha"].min(), df["fecha"].max())
df = aplicar_casos_especiales(df, CASOS_ESPECIALES)

# Filtros
colf1, colf2, colf3 = st.columns([1.2, 1.0, 1.0])
with colf1:
    secciones = sorted(df["sección"].unique())
    seccion_sel = st.multiselect("Secciones", options=secciones, default=secciones)
with colf2:
    semanas = sorted(df["semana"].unique())
    semana_sel = st.multiselect("Semanas", options=semanas, default=semanas)
with colf3:
    actividad_sel = st.multiselect(
        "Actividad",
        options=sorted(df["actividad"].unique()),
        default=sorted(df["actividad"].unique())
    )

df_f = df[
    df["sección"].isin(seccion_sel)
    & df["semana"].isin(semana_sel)
    & df["actividad"].isin(actividad_sel)
].copy()

tab1, tab2, tab3 = st.tabs(["Calendario", "Tabla", "Exportar"])

with tab1:
    events = df_a_fullcalendar_events(df_f)
    initial_date = pd.Timestamp(df_f["fecha"].min()).strftime("%Y-%m-%d") if len(df_f) else FECHA_INICIO

    calendar_options = {
        "initialView": "timeGridWeek",
        "initialDate": initial_date,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
        },
        "height": 850,
        "contentHeight": "auto",
        "slotMinTime": "07:00:00",
        "slotMaxTime": "22:00:00",
        "scrollTime": "08:00:00",
        "slotDuration": "00:30:00",
        "snapDuration": "00:15:00",
        "selectable": True,
        "editable": False,
        "nowIndicator": True,
        "weekNumbers": True,
        "dayMaxEvents": True,
    }

    state = calendar(events=events, options=calendar_options)

    st.divider()
    st.subheader("🔎 Detalles (clic en un evento)")
    event_click = state.get("eventClick") if isinstance(state, dict) else None
    if event_click:
        ev = event_click.get("event", {})
        props = ev.get("extendedProps", {})
        st.write({
            "Título": ev.get("title", ""),
            "Inicio": ev.get("start", ""),
            "Fin": ev.get("end", ""),
            "Tipo": props.get("tipo", ""),
            "Sección": props.get("sección", ""),
            "Actividad": props.get("actividad", ""),
            "Misión": props.get("misiones", ""),
            "Tema": props.get("tema", ""),
            "Evaluación": props.get("evaluación", ""),
            "Profesores": props.get("profesores", ""),
            "Observaciones": props.get("observaciones", ""),
            "Semana": props.get("semana", ""),
        })
    else:
        st.caption("Clickea una clase o misión para ver detalles.")

with tab2:
    st.subheader("🧾 Tabla")
    st.dataframe(df_f, use_container_width=True, hide_index=True,
                 column_config={"fecha": st.column_config.DateColumn(format="DD/MM/YYYY")})

with tab3:
    st.subheader("⬇️ Exportar")
    excel_bytes = df_a_excel_bytes(df_f)
    st.download_button(
        label="Descargar Excel (.xlsx)",
        data=excel_bytes,
        file_name="calendario_filtrado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
