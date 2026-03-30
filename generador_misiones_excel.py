# # # generador_misiones_excel.py
# # import os, random, yaml
# # import pandas as pd
# # from datetime import timedelta

# # from openpyxl.styles import PatternFill, Font, Alignment
# # from openpyxl.utils import get_column_letter

# # def cargar_yaml(path):
# #     with open(path, "r", encoding="utf-8") as f:
# #         return yaml.safe_load(f)

# # def split_profes(s):
# #     if not s:
# #         return []
# #     return [x.strip() for x in str(s).split(",") if x.strip()]

# # def elegir_equilibrado(profes, cargas, n, rng):
# #     # minimiza cargas/horas_contrato, desempate aleatorio
# #     elegidos = []
# #     n = max(1, min(n, len(profes)))
# #     for _ in range(n):
# #         candidatos = [p for p in profes if p["codigo"] not in elegidos]
# #         ratios = []
# #         for p in candidatos:
# #             cod = p["codigo"]
# #             horas = float(p.get("horas_contrato", 1) or 1)
# #             ratios.append((cod, cargas.get(cod, 0) / max(horas, 1e-9)))
# #         min_ratio = min(r[1] for r in ratios)
# #         mejores = [cod for cod, rr in ratios if rr == min_ratio]
# #         cod = rng.choice(mejores)
# #         elegidos.append(cod)
# #         cargas[cod] = cargas.get(cod, 0) + 1
# #     return elegidos

# # def detectar_evaluaciones(df_cal):
# #     # devuelve una tabla de "hitos" evaluativos
# #     df = df_cal.copy()
# #     df["fecha"] = pd.to_datetime(df["fecha"])
# #     df["evaluación"] = df.get("evaluación", "").fillna("").astype(str)
# #     df["actividad"] = df.get("actividad", "").fillna("").astype(str)

# #     evs = []

# #     # 1) evaluaciones (prueba / tp / etc.)
# #     sub = df[df["evaluación"].str.strip() != ""].copy()
# #     for _, r in sub.iterrows():
# #         evs.append({
# #             "tipo_evento": r["evaluación"].strip(),      # "Prueba", "Trabajo práctico", ...
# #             "nombre_evento": r["evaluación"].strip(),    # puedes refinar a "Prueba 1" etc si lo codificas en observaciones
# #             "sección": r.get("sección", ""),
# #             "actividad": r.get("actividad", ""),
# #             "fecha_evento": r["fecha"].date(),
# #             "tema": r.get("tema", ""),
# #             "observaciones": r.get("observaciones", ""),
# #         })

# #     # 2) exámenes
# #     sub2 = df[df["actividad"].str.strip().str.lower() == "examen"].copy()
# #     for _, r in sub2.iterrows():
# #         evs.append({
# #             "tipo_evento": "Examen",
# #             "nombre_evento": "Examen",
# #             "sección": r.get("sección", ""),
# #             "actividad": r.get("actividad", ""),
# #             "fecha_evento": r["fecha"].date(),
# #             "tema": r.get("tema", ""),
# #             "observaciones": r.get("observaciones", ""),
# #         })

# #     return pd.DataFrame(evs)

# # # def construir_misiones(config, df_cal):
# # #     rng = random.Random(int(config.get("aleatoriedad", {}).get("semilla", 42)))

# # #     profs = config.get("profesores", []) or []
# # #     cargas = {p["codigo"]: 0 for p in profs}

# # #     protocolos = config.get("protocolos", {}) or {}
# # #     reglas = config.get("reglas_plazos", {}) or {}

# # #     df_evs = detectar_evaluaciones(df_cal)
# # #     if df_evs.empty:
# # #         # fallback: inventa 2 pruebas y 1 TP coherente si no hay fechas
# # #         f0 = pd.Timestamp(config["periodo"]["fecha_inicio"])
# # #         df_evs = pd.DataFrame([
# # #             {"tipo_evento":"Prueba", "nombre_evento":"Prueba 1", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=6)).date(), "tema":"", "observaciones":"(inventado)"},
# # #             {"tipo_evento":"TP", "nombre_evento":"TP: Linealización", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=10)).date(), "tema":"", "observaciones":"(inventado)"},
# # #             {"tipo_evento":"Prueba", "nombre_evento":"Prueba 2", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=14)).date(), "tema":"", "observaciones":"(inventado)"},
# # #             {"tipo_evento":"Examen", "nombre_evento":"Examen", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=18)).date(), "tema":"", "observaciones":"(inventado)"},
# # #         ])

# # #     filas = []
# # #     for _, ev in df_evs.iterrows():
# # #         tipo = str(ev["tipo_evento"]).strip()
# # #         nombre = str(ev.get("nombre_evento", tipo)).strip()
# # #         seccion = str(ev.get("sección", "Equipo docente")).strip()
# # #         fecha_evento = pd.Timestamp(ev["fecha_evento"])

# # #         # Mapea tipo_evento -> protocolo
# # #         if "prueba" in tipo.lower():
# # #             proto = protocolos.get("Prueba", {})
# # #         elif "trabajo" in tipo.lower() or tipo.lower() == "tp":
# # #             proto = protocolos.get("TP", {})
# # #         elif tipo.lower() == "examen":
# # #             proto = protocolos.get("Examen", {})
# # #         else:
# # #             # por defecto usa Guia/Seminario si quieres, si no, salta
# # #             proto = protocolos.get("Guia", {})

# # #         for paso_key, paso in proto.items():
# # #             offset = int(paso.get("offset_dias", 0))
# # #             deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

# # #             resp = paso.get("responsables", "Asignar")
# # #             detalle = paso.get("detalle", "")

# # #             # asignaciones automáticas
# # #             if str(resp).strip().lower() == "todos":
# # #                 responsables = "Todos"
# # #             else:
# # #                 # 1 o 2 responsables típicamente
# # #                 n_resp = 2 if ("pauta" in paso_key or "constru" in paso_key) else 1
# # #                 elegidos = elegir_equilibrado(profs, cargas, n_resp, rng)
# # #                 responsables = ", ".join(elegidos)

# # #             filas.append({
# # #                 "fecha_limite": deadline,
# # #                 "fecha_evento": fecha_evento.date(),
# # #                 "evento": nombre,
# # #                 "paso": paso_key,
# # #                 "sección": seccion,
# # #                 "responsables": responsables,
# # #                 "detalle": detalle,
# # #                 "estado": "Pendiente",
# # #             })

# # #     df_mis = pd.DataFrame(filas).sort_values(["fecha_limite","evento","sección"]).reset_index(drop=True)
# # #     return df_mis

# # def construir_misiones(config, df_cal):
# #     cfg = config["misiones"]

# #     rng = random.Random(int(cfg.get("aleatoriedad", {}).get("semilla", 42)))
# #     profs = cfg.get("profesores", []) or []
# #     cargas = {p["codigo"]: 0 for p in profs}

# #     protocolos = cfg.get("protocolos", {}) or {}

# #     df_evs = detectar_evaluaciones(df_cal)
# #     if df_evs.empty:
# #         f0 = pd.Timestamp(config["calendario"]["periodo"]["fecha_inicio"])
# #         df_evs = pd.DataFrame([
# #             {"tipo_evento":"Certamen", "nombre_evento":"Certamen 1", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=5)).date(), "tema":"", "observaciones":"(inventado)"},
# #             {"tipo_evento":"Trabajo práctico", "nombre_evento":"Trabajo práctico", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=12)).date(), "tema":"", "observaciones":"(inventado)"},
# #             {"tipo_evento":"Examen", "nombre_evento":"Examen", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=18)).date(), "tema":"", "observaciones":"(inventado)"},
# #         ])

# #     filas = []

# #     for _, ev in df_evs.iterrows():
# #         tipo = str(ev["tipo_evento"]).strip()
# #         nombre = str(ev.get("nombre_evento", tipo)).strip()
# #         seccion = str(ev.get("sección", "Equipo docente")).strip()
# #         fecha_evento = pd.Timestamp(ev["fecha_evento"])

# #         tipo_norm = tipo.lower()

# #         if "control" in tipo_norm:
# #             proto = protocolos.get("Control", {})
# #         elif "certamen" in tipo_norm or "prueba" in tipo_norm:
# #             proto = protocolos.get("Certamen", protocolos.get("Prueba", {}))
# #         elif "trabajo" in tipo_norm or tipo_norm == "tp":
# #             proto = protocolos.get("Trabajo práctico", protocolos.get("TP", {}))
# #         elif "examen" in tipo_norm:
# #             proto = protocolos.get("Examen", {})
# #         else:
# #             proto = protocolos.get("Guia", {})

# #         for paso_key, paso in proto.items():
# #             offset = int(paso.get("offset_dias", 0))
# #             deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

# #             resp = paso.get("responsables", "Asignar")
# #             # detalle = paso.get("detalle", "")
# #             detalle_base = str(paso.get("detalle", "")).strip()

# #             obs_cal = str(ev.get("observaciones", "")).strip()   # viene del calendario
# #             # opcional: si quieres también agregar el tema
# #             tema_cal = str(ev.get("tema", "")).strip()

# #             detalle_partes = []
# #             if detalle_base:
# #                 detalle_partes.append(detalle_base)
# #             if obs_cal:
# #                 detalle_partes.append(obs_cal)
# #             # si quieres sumar tema en algunas, descomenta:
# #             # if tema_cal:
# #             #     detalle_partes.append(f"Tema: {tema_cal}")

# #             detalle = " — ".join(detalle_partes)

# #             if str(resp).strip().lower() == "todos":
# #                 responsables = "Todos"
# #             else:
# #                 n_resp = 2 if ("pauta" in paso_key or "constru" in paso_key) else 1
# #                 elegidos = elegir_equilibrado(profs, cargas, n_resp, rng)
# #                 responsables = ", ".join(elegidos)

# #             filas.append({
# #                 "fecha_limite": deadline,
# #                 "fecha_evento": fecha_evento.date(),
# #                 "evento": nombre,
# #                 "paso": paso_key,
# #                 "sección": seccion,
# #                 "responsables": responsables,
# #                 "detalle": detalle,
# #                 "estado": "Pendiente",
# #             })

# #     df_mis = pd.DataFrame(filas).sort_values(["fecha_limite", "evento", "sección"]).reset_index(drop=True)
# #     return df_mis

# # # def armar_matriz(df_mis, config):
# # #     # Vista tipo imagen: filas = evento, columnas = secciones, valor = responsables de "corregir_y_notas"/"corregir_examen"/etc.
# # #     alias = config.get("alias_seccion", {}) or {}

# # #     df = df_mis.copy()
# # #     df["evento"] = df["evento"].astype(str)

# # #     # define qué pasos van a la matriz (corrección)
# # #     pasos_correccion = set(["corregir_y_notas", "corregir_examen", "revisar_tp"])
# # #     df = df[df["paso"].isin(list(pasos_correccion))].copy()
# # #     if df.empty:
# # #         return pd.DataFrame()

# # #     df["sección_col"] = df["sección"].apply(lambda s: alias.get(s, s))
# # #     mat = df.pivot_table(index="evento", columns="sección_col", values="responsables", aggfunc="first", fill_value="")

# # #     # Agrega segunda fila “Detalle / Corrección” estilo tu ejemplo si quieres hacerlo como header doble,
# # #     # en Excel lo hacemos como 2 filas arriba; acá lo dejamos plano y lo formateamos al exportar.
# # #     mat = mat.reset_index().rename(columns={"evento":"Evaluaciones"})
# # #     return mat

# # def armar_matriz(df_mis, config):
# #     alias = config.get("misiones", {}).get("alias_seccion", {}) or {}

# #     df = df_mis.copy()
# #     if df.empty:
# #         return pd.DataFrame()

# #     df["evento"] = df["evento"].astype(str)
# #     df["paso"] = df["paso"].astype(str)
# #     df["detalle"] = df["detalle"].astype(str)
# #     df["sección_col"] = df["sección"].apply(lambda s: alias.get(s, s))

# #     mat = df.pivot_table(
# #         index=["evento", "paso", "detalle"],
# #         columns="sección_col",
# #         values="responsables",
# #         aggfunc="first",
# #         fill_value=""
# #     ).reset_index()

# #     mat = mat.rename(columns={
# #         "evento": "Evaluación",
# #         "paso": "Misión",
# #         "detalle": "Detalle"
# #     })

# #     return mat

# # def exportar_excel(df_mis, df_mat, path):
# #     os.makedirs(os.path.dirname(path), exist_ok=True)

# #     with pd.ExcelWriter(path, engine="openpyxl", datetime_format="DD/MM/YYYY") as writer:
# #         df_mis.to_excel(writer, index=False, sheet_name="Misiones")
# #         if df_mat is not None and not df_mat.empty:
# #             df_mat.to_excel(writer, index=False, sheet_name="Matriz")

# #         # Un “Plan” para lectura humana: filtramos pasos clave y orden lógico
# #         # orden = ["pedir_preguntas","construir_control","pauta_prueba","revisar_prueba","escaneo","corregir_y_notas",
# #                 #  "construir_examen","pauta_examen","corregir_examen","revisar_tp","revision_guia","pauta_seminario","presentacion_grupal"]
# #         orden = ["pedir_preguntas","construir_control","pauta_prueba","revisar_prueba","escanear","corregir_y_notas",
# #          "construir_examen","pauta_examen","corregir_examen","revisar_tp","revision_guia","pauta_seminario","presentacion_grupal"]
# #         df_plan = df_mis.copy()
# #         df_plan["paso_rank"] = df_plan["paso"].apply(lambda x: orden.index(x) if x in orden else 999)
# #         df_plan = df_plan.sort_values(["evento","paso_rank","sección","fecha_limite"]).drop(columns=["paso_rank"])
# #         df_plan.to_excel(writer, index=False, sheet_name="Plan")

# #         # ------- ESTILO EXCEL (colores) -------
# #         wb = writer.book

# #         def style_sheet(ws, header_color="1F4E78"):
# #             # header
# #             fill_header = PatternFill("solid", fgColor=header_color)
# #             font_header = Font(bold=True, color="FFFFFF")
# #             for cell in ws[1]:
# #                 cell.fill = fill_header
# #                 cell.font = font_header
# #                 cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
# #             ws.freeze_panes = "A2"
# #             ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"

# #             # widths
# #             for col in range(1, ws.max_column + 1):
# #                 maxlen = 0
# #                 for r in range(1, ws.max_row + 1):
# #                     v = ws.cell(r, col).value
# #                     if v is None:
# #                         continue
# #                     maxlen = max(maxlen, len(str(v)))
# #                 ws.column_dimensions[get_column_letter(col)].width = min(max(12, maxlen + 2), 55)

# #         ws_mis = wb["Misiones"]
# #         style_sheet(ws_mis, header_color="5B2C6F")

# #         # Colorear “fecha_limite” en rojo suave y poner emoji en otra columna si quieres:
# #         headers = [c.value for c in ws_mis[1]]
# #         if "fecha_limite" in headers:
# #             c_fecha = headers.index("fecha_limite") + 1
# #             fill_deadline = PatternFill("solid", fgColor="F4CCCC")
# #             for r in range(2, ws_mis.max_row + 1):
# #                 ws_mis.cell(r, c_fecha).fill = fill_deadline
# #                 ws_mis.cell(r, c_fecha).alignment = Alignment(horizontal="center")

# #         ws_plan = wb["Plan"]
# #         style_sheet(ws_plan, header_color="2C3E50")

# #         if "Matriz" in wb.sheetnames:
# #             ws_mat = wb["Matriz"]
# #             style_sheet(ws_mat, header_color="7F7F7F")

# # # def main():
# # #     config = cargar_yaml("misiones_config.yml")
# # #     cal_path = config["fuentes"]["calendario_excel_path"]

# # #     df_cal = pd.read_excel(cal_path, sheet_name="Calendario")
# # #     df_mis = construir_misiones(config, df_cal)
# # #     df_mat = armar_matriz(df_mis, config)

# # #     out = config["salida"]["excel_path"]
# # #     exportar_excel(df_mis, df_mat, out)
# # #     print(f"OK: generado {out} con {len(df_mis)} tareas.")

# # # if __name__ == "__main__":
# # #     main()

# # # # ============================================================
# # # # MAIN MULTI-CURSO
# # # # - Lee 3 YAML distintos desde config/
# # # # - Genera los 3 misiones.xlsx
# # # # - Usa el calendario.xlsx correspondiente de cada curso
# # # # ============================================================
# # # def main():
# # #     cursos = {
# # #         "fokito": {
# # #             "config_path": os.path.join("config", "misiones_fokito.yml"),
# # #             "cal_path": os.path.join("data", "fokito", "calendario.xlsx"),
# # #             "out_path": os.path.join("data", "fokito", "misiones.xlsx"),
# # #         },
# # #         "tecnologia_medica": {
# # #             "config_path": os.path.join("config", "misiones_tecnologia_medica.yml"),
# # #             "cal_path": os.path.join("data", "tecnologia_medica", "calendario.xlsx"),
# # #             "out_path": os.path.join("data", "tecnologia_medica", "misiones.xlsx"),
# # #         },
# # #         "medicina": {
# # #             "config_path": os.path.join("config", "misiones_medicina.yml"),
# # #             "cal_path": os.path.join("data", "medicina", "calendario.xlsx"),
# # #             "out_path": os.path.join("data", "medicina", "misiones.xlsx"),
# # #         },
# # #     }

# # #     for curso, info in cursos.items():
# # #         config_path = info["config_path"]
# # #         cal_path = info["cal_path"]
# # #         out_path = info["out_path"]

# # #         if not os.path.exists(config_path):
# # #             print(f"⚠️  Saltando {curso}: no existe {config_path}")
# # #             continue

# # #         if not os.path.exists(cal_path):
# # #             print(f"⚠️  Saltando {curso}: no existe {cal_path}. Genera primero el calendario.")
# # #             continue

# # #         config = cargar_yaml(config_path)

# # #         # Sobrescribimos rutas para asegurar consistencia
# # #         if "fuentes" not in config:
# # #             config["fuentes"] = {}
# # #         if "salida" not in config:
# # #             config["salida"] = {}

# # #         config["fuentes"]["calendario_excel_path"] = cal_path
# # #         config["salida"]["excel_path"] = out_path

# # #         os.makedirs(os.path.dirname(out_path), exist_ok=True)

# # #         df_cal = pd.read_excel(cal_path, sheet_name="Calendario")
# # #         df_mis = construir_misiones(config, df_cal)
# # #         df_mat = armar_matriz(df_mis, config)

# # #         exportar_excel(df_mis, df_mat, out_path)

# # #         print(f"OK: [{curso}] generado {out_path} con {len(df_mis)} tareas.")

# # # if __name__ == "__main__":
# # #     main()




# # def main():
# #     cursos = {
# #         "fokito": {
# #             "config_path": os.path.join("config", "calendario_fokito.yml"),
# #             "cal_path": os.path.join("data", "fokito", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "fokito", "misiones.xlsx"),
# #         },
# #         "tecnologia_medica": {
# #             "config_path": os.path.join("config", "calendario_tecnologia_medica.yml"),
# #             "cal_path": os.path.join("data", "tecnologia_medica", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "tecnologia_medica", "misiones.xlsx"),
# #         },
# #         "medicina": {
# #             "config_path": os.path.join("config", "calendario_medicina.yml"),
# #             "cal_path": os.path.join("data", "medicina", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "medicina", "misiones.xlsx"),
# #         },
        
# #         "enobnu": {
# #             "config_path": os.path.join("config", "calendario_enobnu.yml"),
# #             "cal_path": os.path.join("data", "enobnu", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "enobnu", "misiones.xlsx"),
# #         },
# #     }

# #     for curso, info in cursos.items():
# #         config_path = info["config_path"]
# #         cal_path = info["cal_path"]
# #         out_path = info["out_path"]

# #         if not os.path.exists(config_path):
# #             print(f"⚠️  Saltando {curso}: no existe {config_path}")
# #             continue

# #         if not os.path.exists(cal_path):
# #             print(f"⚠️  Saltando {curso}: no existe {cal_path}. Genera primero el calendario.")
# #             continue

# #         config = cargar_yaml(config_path)

# #         os.makedirs(os.path.dirname(out_path), exist_ok=True)

# #         df_cal = pd.read_excel(cal_path, sheet_name="Calendario")
# #         df_mis = construir_misiones(config, df_cal)
# #         df_mat = armar_matriz(df_mis, config)

# #         exportar_excel(df_mis, df_mat, out_path)

# #         print(f"OK: [{curso}] generado {out_path} con {len(df_mis)} tareas.")
        

# # if __name__ == "__main__":
# #     main()





# # generador_misiones_excel.py
# import os
# import yaml
# import pandas as pd
# from openpyxl.styles import PatternFill, Font, Alignment
# from openpyxl.utils import get_column_letter


# # ============================================================
# # YAML / HELPERS
# # ============================================================
# def cargar_yaml(path):
#     with open(path, "r", encoding="utf-8") as f:
#         return yaml.safe_load(f)


# # def split_profes(s):
# #     if s is None:
# #         return []

# #     if isinstance(s, list):
# #         return [str(x).strip() for x in s if str(x).strip()]

# #     return [x.strip() for x in str(s).split(",") if x.strip()]



# from collections import defaultdict
# import math

# # ============================================================
# # POOLS CÍCLICOS PERSISTENTES
# # ============================================================

# def normalizar_lista_profes(profes):
#     """
#     Acepta:
#       "JM, MB, NV"
#       ["JM", "MB", "NV"]
#     y retorna lista limpia, manteniendo repetidos si existen.
#     """
#     if profes is None:
#         return []

#     if isinstance(profes, str):
#         return [x.strip() for x in profes.split(",") if x.strip()]

#     if isinstance(profes, (list, tuple)):
#         out = []
#         for x in profes:
#             sx = str(x).strip()
#             if sx:
#                 out.append(sx)
#         return out

#     sx = str(profes).strip()
#     return [sx] if sx else []


# def construir_pool_seminario_desde_config(config_curso):
#     """
#     Construye los pools base por sección a partir de calendario.profesor_base.
#     Mantiene duplicados, por ejemplo ['SM', 'XX', 'XX'].
#     """
#     pools = {}

#     profesores_base = (
#         config_curso.get("calendario", {})
#         .get("profesores_base", [])
#     )

#     for item in profesores_base:
#         seccion = str(item.get("seccion", "")).strip()
#         actividad = str(item.get("actividad", "")).strip()
#         profesores = item.get("profesores", [])

#         if actividad == "Seminario" and seccion:
#             pools[seccion] = normalizar_lista_profes(profesores)

#     return pools


# def inicializar_estado_pools(config_curso):
#     """
#     Retorna:
#       pools_por_seccion: {'Sección 1': ['JM','MB','NV'], ...}
#       estado_pools: {'Sección 1': 0, 'Sección 2': 0, ...}
#     """
#     pools_por_seccion = construir_pool_seminario_desde_config(config_curso)
#     estado_pools = {sec: 0 for sec in pools_por_seccion.keys()}
    
#     return pools_por_seccion, estado_pools


# def responsables_desde_pool_ciclico(pool, n_responsables, cursor_inicial):
#     """
#     Selecciona n_responsables siguiendo el pool cíclico y devuelve:
#       - lista de responsables
#       - nuevo cursor
#     Mantiene duplicados del pool.
#     """
#     pool = normalizar_lista_profes(pool)

#     if not pool or n_responsables <= 0:
#         return [], cursor_inicial

#     L = len(pool)
#     cursor = cursor_inicial % L

#     seleccionados = []
#     for k in range(n_responsables):
#         idx = (cursor + k) % L
#         seleccionados.append(pool[idx])

#     nuevo_cursor = (cursor + n_responsables) % L
#     return seleccionados, nuevo_cursor


# def tomar_responsables_pool(
#     seccion,
#     n_responsables,
#     pools_por_seccion,
#     estado_pools,
#     overrides_responsables=None,
#     tipo_evento=None,
#     fecha_evento=None,
#     paso=None,
# ):
#     """
#     Función principal para asignar desde el pool.

#     Primero revisa override exacto si lo usas.
#     Si no, usa pool cíclico persistente por sección.
#     """
#     if overrides_responsables is None:
#         overrides_responsables = []

#     # --------------------------------------------------------
#     # 1) Overrides exactos
#     # --------------------------------------------------------
#     fecha_evento_str = ""
#     if fecha_evento is not None:
#         try:
#             fecha_evento_str = fecha_evento.strftime("%Y-%m-%d")
#         except Exception:
#             fecha_evento_str = str(fecha_evento)

#     for ov in overrides_responsables:
#         ov_tipo = str(ov.get("tipo_evento", "")).strip()
#         ov_seccion = str(ov.get("seccion", "")).strip()
#         ov_fecha = str(ov.get("fecha_evento", "")).strip()
#         ov_paso = str(ov.get("paso", "")).strip()

#         match_tipo = (not ov_tipo) or (ov_tipo == str(tipo_evento).strip())
#         match_seccion = (not ov_seccion) or (ov_seccion == str(seccion).strip())
#         match_fecha = (not ov_fecha) or (ov_fecha == fecha_evento_str)
#         match_paso = (not ov_paso) or (ov_paso == str(paso).strip())

#         if match_tipo and match_seccion and match_fecha and match_paso:
#             resp = normalizar_lista_profes(ov.get("responsables", []))
#             if resp:
#                 return resp

#     # --------------------------------------------------------
#     # 2) Pool cíclico persistente
#     # --------------------------------------------------------
#     pool = pools_por_seccion.get(seccion, [])
#     cursor = estado_pools.get(seccion, 0)

#     responsables, nuevo_cursor = responsables_desde_pool_ciclico(
#         pool=pool,
#         n_responsables=n_responsables,
#         cursor_inicial=cursor
#     )

#     estado_pools[seccion] = nuevo_cursor
#     return responsables


# # ============================================================
# # REGLAS DE CUÁNTOS RESPONSABLES POR PASO
# # ============================================================

# def n_responsables_para_paso(tipo_evento, paso):
#     """
#     Ajusta aquí la cantidad de personas que toma cada misión desde el pool.
#     """
#     tipo_evento = str(tipo_evento).strip()
#     paso = str(paso).strip()

#     # Controles: mejor pool cíclico también
#     if tipo_evento == "Control":
#         if paso in ["construir_control", "escanear", "corregir_y_notas"]:
#             return 1

#     # Certámenes
#     if tipo_evento == "Certamen":
#         if paso == "pedir_preguntas":
#             return 3
#         if paso in ["corregir_y_notas"]:
#             return 3

#     # Exámenes
#     if tipo_evento == "Examen":
#         if paso == "pedir_preguntas":
#             return 3
#         if paso == "corregir_examen":
#             return 3

#     # Trabajo práctico
#     if tipo_evento == "Trabajo práctico":
#         if paso == "revisar_tp":
#             return 3

#     # Talleres: normalmente los manejas aparte con AB/CD y A/B/C/D
#     return 1








# # ============================================================
# # TALLERES CON POOL CÍCLICO PERSISTENTE
# # ============================================================

# def asignar_construccion_taller_desde_pool(seccion, pools_por_seccion, estado_pools):
#     """
#     Devuelve:
#       AB -> 2 personas
#       CD -> 2 personas
#     usando el mismo cursor persistente.
#     """
#     pool = pools_por_seccion.get(seccion, [])
#     cursor = estado_pools.get(seccion, 0)

#     asignados, nuevo_cursor = responsables_desde_pool_ciclico(
#         pool=pool,
#         n_responsables=4,
#         cursor_inicial=cursor
#     )

#     estado_pools[seccion] = nuevo_cursor

#     while len(asignados) < 4:
#         asignados.append("")

#     return {
#         "construir_taller_AB": asignados[:2],
#         "construir_taller_CD": asignados[2:4],
#     }


# def asignar_correccion_taller_desde_pool(seccion, pools_por_seccion, estado_pools):
#     """
#     Devuelve responsables para A/B/C/D usando 4 tomas seguidas del pool.
#     """
#     pool = pools_por_seccion.get(seccion, [])
#     cursor = estado_pools.get(seccion, 0)

#     asignados, nuevo_cursor = responsables_desde_pool_ciclico(
#         pool=pool,
#         n_responsables=4,
#         cursor_inicial=cursor
#     )

#     estado_pools[seccion] = nuevo_cursor

#     while len(asignados) < 4:
#         asignados.append("")

#     return {
#         "corregir_taller_A": [asignados[0]],
#         "corregir_taller_B": [asignados[1]],
#         "corregir_taller_C": [asignados[2]],
#         "corregir_taller_D": [asignados[3]],
#     }



# def split_profes(valor):
#     """
#     Acepta:
#     - None
#     - "A, B, C"
#     - ["A", "B", "C"]
#     y preserva duplicados si vienen en lista/string.
#     """
#     if valor is None:
#         return []

#     # pandas NaN
#     try:
#         if pd.isna(valor):
#             return []
#     except Exception:
#         pass

#     if isinstance(valor, (list, tuple)):
#         return [str(x).strip() for x in valor if str(x).strip()]

#     texto = str(valor).strip()
#     if not texto:
#         return []

#     return [x.strip() for x in texto.split(",") if x.strip()]


# def normalizar_lista_profes(valor):
#     if valor is None:
#         return []
#     if isinstance(valor, list):
#         return [str(x).strip() for x in valor if str(x).strip()]
#     return [x.strip() for x in str(valor).split(",") if x.strip()]


# def normalizar_profes_str(valor):
#     return ", ".join(normalizar_lista_profes(valor))


# def construir_id_mision(row):
#     """
#     ID estable para preservar el estado entre regeneraciones.
#     """
#     fecha_limite = pd.to_datetime(row.get("fecha_limite"), errors="coerce")
#     fecha_evento = pd.to_datetime(row.get("fecha_evento"), errors="coerce")

#     fecha_limite_str = fecha_limite.strftime("%Y-%m-%d") if pd.notna(fecha_limite) else ""
#     fecha_evento_str = fecha_evento.strftime("%Y-%m-%d") if pd.notna(fecha_evento) else ""

#     partes = [
#         fecha_limite_str,
#         fecha_evento_str,
#         str(row.get("evento", "")).strip(),
#         str(row.get("tipo_evento", "")).strip(),
#         str(row.get("paso", "")).strip(),
#         str(row.get("sección", "")).strip(),
#         str(row.get("responsables", "")).strip(),
#     ]
#     return "||".join(partes)



# def obtener_profes_seminario_seccion(config, seccion, deduplicar=False):
#     """
#     Lee profesores_base / Seminario de una sección.
#     - deduplicar=False  -> preserva pesos (ej: XX, XX)
#     - deduplicar=True   -> deja solo únicos
#     """
#     base = config.get("calendario", {}).get("profesores_base", []) or []

#     profes = []
#     for r in base:
#         secc = str(r.get("seccion", "")).strip()
#         act = str(r.get("actividad", "")).strip()

#         if secc == seccion and act == "Seminario":
#             profes = split_profes(r.get("profesores", []))
#             break

#     return unicos(profes) if deduplicar else profes


# # def obtener_pool_participantes_seccion(config, seccion):
# #     """
# #     Para tareas colectivas de seminario:
# #     cada persona aparece una sola vez.
# #     NO excluye PEC/PCC si también hacen seminario.
# #     """
# #     return obtener_profes_seminario_seccion(config, seccion, deduplicar=True)


# def obtener_pool_ciclico_seccion(config, seccion):
#     """
#     Para controles / talleres:
#     preserva multiplicidad para ponderar el ciclo.
#     """
#     return obtener_profes_seminario_seccion(config, seccion, deduplicar=False)


# def obtener_pool_global_ciclico(config):
#     """
#     Pool global ponderado para talleres.
#     Si un profe aparece en 2 secciones, sale 2 veces.
#     Si aparece duplicado dentro de una sección, también se respeta.
#     """
#     secciones = list((config.get("calendario", {}).get("secciones", {}) or {}).keys())
#     salida = []

#     for seccion in secciones:
#         salida.extend(obtener_pool_ciclico_seccion(config, seccion))

#     return salida


# def cargar_estados_previos(path_excel):
#     """
#     Lee el Excel previo y devuelve:
#     {id_mision: estado}
#     """
#     if not os.path.exists(path_excel):
#         return {}

#     try:
#         df_prev = pd.read_excel(path_excel, sheet_name="Misiones")
#     except Exception:
#         return {}

#     if df_prev.empty:
#         return {}

#     for c in ["fecha_limite", "fecha_evento"]:
#         if c in df_prev.columns:
#             df_prev[c] = pd.to_datetime(df_prev[c], errors="coerce")

#     for c in ["evento", "tipo_evento", "paso", "sección", "responsables", "estado"]:
#         if c in df_prev.columns:
#             df_prev[c] = df_prev[c].fillna("").astype(str)
#         else:
#             df_prev[c] = ""

#     estados = {}
#     for _, row in df_prev.iterrows():
#         id_mision = construir_id_mision(row)
#         estado = str(row.get("estado", "")).strip() or "Pendiente"
#         estados[id_mision] = estado

#     return estados


# def aplicar_estados_previos(df_mis, estados_previos):
#     """
#     Si una misión ya existía, conserva su estado anterior.
#     """
#     if df_mis.empty:
#         return df_mis

#     df = df_mis.copy()
#     ids = []

#     for _, row in df.iterrows():
#         ids.append(construir_id_mision(row))

#     df["id_mision"] = ids
#     df["estado"] = df["id_mision"].apply(
#         lambda x: estados_previos.get(x, "Pendiente")
#     )

#     return df


# def obtener_profesores_base(config):
#     """
#     Devuelve dict:
#     {(seccion, actividad): [prof1, prof2, ...]}
#     """
#     salida = {}
#     for r in config.get("calendario", {}).get("profesores_base", []) or []:
#         secc = str(r.get("seccion", "")).strip()
#         act = str(r.get("actividad", "")).strip()
#         profes = normalizar_lista_profes(r.get("profesores", []))
#         salida[(secc, act)] = profes
#     return salida


# # def obtener_coordinacion(config):
# #     mis = config.get("misiones", {}) or {}
# #     coord = mis.get("coordinacion", {}) or {}
# #     pcc = str(coord.get("pcc", "")).strip()
# #     pec_por_seccion = coord.get("pec_por_seccion", {}) or {}
# #     return pcc, pec_por_seccion

# # def obtener_coordinacion(config):
# #     """
# #     Lee:
# #     misiones:
# #       coordinacion:
# #         pec_por_seccion:
# #           "Sección 1": "CC"
# #         pcc_por_seccion:
# #           "Sección 1": "TY"
# #     """
# #     mis = config.get("misiones", {}) or {}
# #     coord = mis.get("coordinacion", {}) or {}

# #     pec_por_seccion = coord.get("pec_por_seccion", {}) or {}
# #     pcc_por_seccion = coord.get("pcc_por_seccion", {}) or {}

# #     return pec_por_seccion, pcc_por_seccion


# def obtener_coordinacion(config):
#     """
#     Lee:
#     misiones:
#       coordinacion:
#         pec_por_seccion:
#           "Sección 1": "CC"
#         pcc_por_seccion:
#           "Sección 1": "TY"
#     """
#     mis = config.get("misiones", {}) or {}
#     coord = mis.get("coordinacion", {}) or {}

#     pec_por_seccion = coord.get("pec_por_seccion", {}) or {}
#     pcc_por_seccion = coord.get("pcc_por_seccion", {}) or {}

#     return pec_por_seccion, pcc_por_seccion


# # def obtener_pool_participantes_seccion(config, seccion):
# #     """
# #     Pool de profesores participantes de la sección:
# #     sale de profesores_base / Seminario
# #     excluyendo PEC y PCC.
# #     """
# #     mapa = obtener_profesores_base(config)
# #     pcc, pec_por_seccion = obtener_coordinacion(config)

# #     pool = mapa.get((seccion, "Seminario"), []).copy()
# #     pec = str(pec_por_seccion.get(seccion, "")).strip()

# #     salida = []
# #     for p in pool:
# #         if p and p != pec and p != pcc:
# #             if p not in salida:
# #                 salida.append(p)
# #     return salida

# # def obtener_pool_participantes_seccion(config, seccion):
# #     """
# #     Pool de profesores participantes de la sección:
# #     sale de profesores_base / Seminario
# #     excluyendo PEC y PCC.
# #     """
# #     mapa = obtener_profesores_base(config)
# #     pec_por_seccion, pcc_por_seccion = obtener_coordinacion(config)

# #     pool = mapa.get((seccion, "Seminario"), []).copy()
# #     pec = str(pec_por_seccion.get(seccion, "")).strip()
# #     pcc = str(pcc_por_seccion.get(seccion, "")).strip()

# #     salida = []
# #     for p in pool:
# #         if p and p != pec and p != pcc:
# #             if p not in salida:
# #                 salida.append(p)
# #     return salida


# def obtener_pool_participantes_seccion(config, seccion):
#     """
#     Pool de profesores participantes de la sección:
#     sale de profesores_base / Seminario
#     excluyendo PEC y PCC de esa sección.
#     """
#     mapa = obtener_profesores_base(config)
#     pec_por_seccion, pcc_por_seccion = obtener_coordinacion(config)

#     pool = mapa.get((seccion, "Seminario"), []).copy()
#     pec = str(pec_por_seccion.get(seccion, "")).strip()
#     pcc = str(pcc_por_seccion.get(seccion, "")).strip()

#     salida = []
#     for p in pool:
#         if p and p != pec and p != pcc:
#             if p not in salida:
#                 salida.append(p)
#     return salida


# def unicos(lista):
#     salida = []
#     for x in lista:
#         x = str(x).strip()
#         if x and x not in salida:
#             salida.append(x)
#     return salida

# def nombre_evento_desde_ev(ev):
#     """
#     Define un nombre amigable del evento sin confundirlo con observaciones
#     administrativas o feriados.
#     """
#     tipo = str(ev.get("tipo_evento", "")).strip()
#     nombre_base = str(ev.get("nombre_evento", tipo)).strip()
#     obs = str(ev.get("observaciones", "")).strip()

#     obs_low = obs.lower()

#     palabras_feriado = [
#         "san pedro", "san pablo", "feriado", "pausa académica",
#         "trabajo autónomo", "receso", "no hay clases"
#     ]

#     if obs and not any(p in obs_low for p in palabras_feriado):
#         return obs

#     return nombre_base

# def obtener_pool_laboratorio_seccion(config, seccion):
#     """
#     Pool de profesores de laboratorio de la sección.
#     """
#     mapa = obtener_profesores_base(config)
#     return mapa.get((seccion, "Laboratorio"), []).copy()


# # def obtener_pool_global_participantes(config):
# #     """
# #     Unión ordenada de todos los pools de seminario del curso, excluyendo PEC/PCC.
# #     """
# #     secciones = list((config.get("calendario", {}).get("secciones", {}) or {}).keys())
# #     salida = []
# #     for seccion in secciones:
# #         for p in obtener_pool_participantes_seccion(config, seccion):
# #             if p not in salida:
# #                 salida.append(p)
# #     return salida


# # def obtener_pool_global_participantes_ponderado(config):
# #     """
# #     Unión de pools de seminario del curso, manteniendo multiplicidad.
# #     Si un profesor aparece en más secciones/seminarios, aparece más veces.
# #     Excluye PEC/PCC porque obtener_pool_participantes_seccion ya los excluye.
# #     """
# #     secciones = list((config.get("calendario", {}).get("secciones", {}) or {}).keys())
# #     salida = []

# #     for seccion in secciones:
# #         pool_seccion = obtener_pool_participantes_seccion(config, seccion)
# #         for p in pool_seccion:
# #             if p:
# #                 salida.append(p)

# #     return salida


# def obtener_lista_seminario_seccion(config, seccion, mantener_duplicados=True):
#     """
#     Devuelve la lista de profesores de seminario de una sección.
#     - Si mantener_duplicados=True, respeta repeticiones como ["SM", "XX", "XX"].
#     - Si False, devuelve únicos preservando orden.
#     """
#     mapa = obtener_profesores_base(config)
#     lista = mapa.get((seccion, "Seminario"), []).copy()

#     if mantener_duplicados:
#         return [str(x).strip() for x in lista if str(x).strip()]

#     return unicos(lista)


# def obtener_pool_participantes_seccion(config, seccion):
#     """
#     Profesores participantes de la sección para misiones colectivas.
#     IMPORTANTE:
#     - YA NO excluye PEC ni PCC.
#     - Si alguien hace seminario, cuenta como participante aunque además sea PEC/PCC.
#     """
#     return obtener_lista_seminario_seccion(config, seccion, mantener_duplicados=False)


# def obtener_pool_controles_seccion(config, seccion):
#     """
#     Pool ponderado para controles.
#     Aquí SÍ se respetan duplicados del YAML, por ejemplo:
#     ["SM", "XX", "XX"]  -> XX tiene doble peso.
#     """
#     return obtener_lista_seminario_seccion(config, seccion, mantener_duplicados=True)


# def obtener_pool_global_participantes(config):
#     """
#     Pool global ponderado para talleres.
#     Junta todas las listas de seminario de todas las secciones,
#     respetando duplicados dentro de cada sección.
#     """
#     secciones = list((config.get("calendario", {}).get("secciones", {}) or {}).keys())
#     salida = []
#     for seccion in secciones:
#         salida.extend(obtener_lista_seminario_seccion(config, seccion, mantener_duplicados=True))
#     return [str(x).strip() for x in salida if str(x).strip()]


# def elegir_varios_ciclico_sin_repetir(pool, inicio, cantidad):
#     """
#     Elige 'cantidad' profesores recorriendo un pool ponderado en forma cíclica,
#     pero evitando repetir a la misma persona dentro de la misma asignación.
#     """
#     if not pool or cantidad <= 0:
#         return []

#     n = len(pool)
#     elegidos = []
#     vistos = set()
#     intentos = 0
#     idx = inicio

#     while len(elegidos) < cantidad and intentos < 10 * n:
#         prof = str(pool[idx % n]).strip()
#         if prof and prof not in vistos:
#             elegidos.append(prof)
#             vistos.add(prof)
#         idx += 1
#         intentos += 1

#     return elegidos


# def buscar_override(config, tipo_evento, seccion, fecha_evento):
#     """
#     Busca override por tipo, sección y fecha_evento.
#     """
#     mis = config.get("misiones", {}) or {}
#     overrides = mis.get("overrides_responsables", []) or []

#     fecha_evento_str = pd.Timestamp(fecha_evento).strftime("%Y-%m-%d")

#     for ov in overrides:
#         tipo_ov = str(ov.get("tipo_evento", "")).strip().lower()
#         seccion_ov = str(ov.get("seccion", "")).strip()
#         fecha_ov = str(ov.get("fecha_evento", "")).strip()

#         if tipo_ov == str(tipo_evento).strip().lower() and seccion_ov == seccion and fecha_ov == fecha_evento_str:
#             return ov

#     return None


# def slot_a_indice(slot):
#     slot = str(slot).strip().upper()
#     mapa = {
#         "A": 0, "B": 1, "C": 2, "D": 3,
#         "E": 4, "F": 5, "G": 6, "H": 7
#     }
#     return mapa.get(slot, None)


# def elegir_ciclico(pool, indice):
#     if not pool:
#         return []
#     return [pool[indice % len(pool)]]


# def elegir_varios_ciclico(pool, inicio, cantidad):
#     if not pool:
#         return []
#     salida = []
#     for k in range(cantidad):
#         salida.append(pool[(inicio + k) % len(pool)])
#     return salida


# def normalizar_responsables(valor):
#     if valor is None:
#         return ""
#     if isinstance(valor, list):
#         return ", ".join([str(x).strip() for x in valor if str(x).strip()])
#     return str(valor).strip()


# def a_fecha(x):
#     ts = pd.to_datetime(x, errors="coerce")
#     if pd.isna(ts):
#         return None
#     return ts.date()


# # ============================================================
# # EVALUACIONES DESDE CALENDARIO
# # ============================================================
# def detectar_evaluaciones(df_cal):
#     df = df_cal.copy()

#     if "fecha" in df.columns:
#         df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

#     for c in ["evaluación", "actividad", "sección", "tema", "observaciones"]:
#         if c in df.columns:
#             df[c] = df[c].fillna("").astype(str)

#     evs = []

#     sub = df[df["evaluación"].str.strip() != ""].copy()

#     for _, r in sub.iterrows():
#         evs.append({
#             "tipo_evento": str(r["evaluación"]).strip(),
#             "nombre_evento": str(r["evaluación"]).strip(),
#             "sección": str(r.get("sección", "")).strip(),
#             "actividad": str(r.get("actividad", "")).strip(),
#             "fecha_evento": pd.Timestamp(r["fecha"]).date(),
#             "tema": str(r.get("tema", "")).strip(),
#             "observaciones": str(r.get("observaciones", "")).strip(),
#         })

#     df_evs = pd.DataFrame(evs)

#     if df_evs.empty:
#         return df_evs

#     df_evs = df_evs.sort_values(["fecha_evento", "sección", "tipo_evento", "actividad"]).reset_index(drop=True)
#     return df_evs


# # ============================================================
# # PROFES PARTICIPANTES POR SECCIÓN
# # Usa profesores_base / Seminario como equipo participante
# # ============================================================
# # def obtener_profes_participantes_por_seccion(config):
# #     cfg_cal = config.get("calendario", {}) or {}
# #     base = cfg_cal.get("profesores_base", []) or {}

# #     participantes = {}

# #     for r in base:
# #         seccion = str(r.get("seccion", "")).strip()
# #         actividad = str(r.get("actividad", "")).strip()
# #         profes = split_profes(r.get("profesores", ""))

# #         if not seccion:
# #             continue

# #         # Profes participantes = profes de Seminario
# #         if actividad == "Seminario":
# #             participantes[seccion] = profes

# #     return participantes


# def obtener_profes_participantes_por_seccion(config):
#     """
#     Los profesores participantes de una sección se toman desde
#     calendario.profesores_base en la actividad 'Seminario'.
#     """
#     cfg_cal = config.get("calendario", {}) or {}
#     base = cfg_cal.get("profesores_base", []) or []

#     participantes = {}

#     for r in base:
#         seccion = str(r.get("seccion", "")).strip()
#         actividad = str(r.get("actividad", "")).strip()
#         profes = split_profes(r.get("profesores", ""))

#         if not seccion:
#             continue

#         if actividad == "Seminario":
#             participantes[seccion] = profes

#     return participantes


# # ============================================================
# # COORDINACIÓN
# # ============================================================
# # def obtener_coordinacion(cfg_mis):
# #     coord = cfg_mis.get("coordinacion", {}) or {}
# #     pcc = str(coord.get("pcc", "")).strip()
# #     pec_por_seccion = coord.get("pec_por_seccion", {}) or {}
# #     return pcc, pec_por_seccion

# # def obtener_coordinacion(cfg_mis):
# #     coord = cfg_mis.get("coordinacion", {}) or {}
# #     pec_por_seccion = coord.get("pec_por_seccion", {}) or {}
# #     pcc_por_seccion = coord.get("pcc_por_seccion", {}) or {}
# #     return pec_por_seccion, pcc_por_seccion


# # ============================================================
# # POOLS CÍCLICOS POR SECCIÓN
# # ============================================================
# # def construir_pools_por_seccion(cfg_mis, participantes_por_seccion):
# #     """
# #     Si existe pools_por_seccion en YAML, lo usa.
# #     Si no existe, arma uno automático con el orden de participantes.
# #     """
# #     pools_cfg = cfg_mis.get("pools_por_seccion", {}) or {}
# #     pools_final = {}

# #     for seccion, participantes in participantes_por_seccion.items():
# #         if seccion in pools_cfg:
# #             lista = []
# #             for x in pools_cfg[seccion]:
# #                 slot = str(x.get("slot", "")).strip()
# #                 profesor = str(x.get("profesor", "")).strip()
# #                 if slot and profesor:
# #                     lista.append({
# #                         "slot": slot,
# #                         "profesor": profesor,
# #                     })
# #             pools_final[seccion] = lista
# #         else:
# #             auto = []
# #             letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
# #             for i, prof in enumerate(participantes):
# #                 if i < len(letras):
# #                     auto.append({
# #                         "slot": letras[i],
# #                         "profesor": prof
# #                     })
# #             pools_final[seccion] = auto

# #     return pools_final


# # def construir_pools_por_seccion(config):
# #     """
# #     El pool cíclico se construye automáticamente desde
# #     calendario.profesores_base, usando la actividad 'Seminario'.

# #     Orden:
# #     - si profesores viene como lista, respeta ese orden
# #     - si viene como string "A, B, C", respeta ese orden
# #     """
# #     cfg_cal = config.get("calendario", {}) or {}
# #     base = cfg_cal.get("profesores_base", []) or []

# #     pools = {}
# #     letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# #     for r in base:
# #         seccion = str(r.get("seccion", "")).strip()
# #         actividad = str(r.get("actividad", "")).strip()
# #         profesores = split_profes(r.get("profesores", ""))

# #         if not seccion or actividad != "Seminario":
# #             continue

# #         pool = []
# #         for i, prof in enumerate(profesores):
# #             if i >= len(letras):
# #                 break
# #             pool.append({
# #                 "slot": letras[i],
# #                 "profesor": prof
# #             })

# #         pools[seccion] = pool

# #     return pools




# def construir_pools_por_seccion(config):
#     """
#     Pool cíclico automático desde profesores_base / Seminario.
#     Respeta duplicados para ponderar carga.
#     Ejemplo:
#       ["SM", "XX", "XX"] -> slots A=SM, B=XX, C=XX
#     """
#     cfg_cal = config.get("calendario", {}) or {}
#     base = cfg_cal.get("profesores_base", []) or []

#     pools = {}
#     letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#     for r in base:
#         seccion = str(r.get("seccion", "")).strip()
#         actividad = str(r.get("actividad", "")).strip()
#         profesores = split_profes(r.get("profesores", ""))  # mantiene duplicados

#         if not seccion or actividad != "Seminario":
#             continue

#         pool = []
#         for i, prof in enumerate(profesores):
#             if i >= len(letras):
#                 break
#             pool.append({
#                 "slot": letras[i],
#                 "profesor": prof
#             })

#         pools[seccion] = pool

#     return pools


# # ============================================================
# # OVERRIDES MANUALES
# # ============================================================
# def construir_overrides(cfg_mis):
#     """
#     Índice por:
#     (tipo_evento, seccion, fecha_evento)
#     """
#     overrides = {}
#     for r in cfg_mis.get("overrides_responsables", []) or []:
#         tipo = str(r.get("tipo_evento", "")).strip()
#         seccion = str(r.get("seccion", "")).strip()
#         fecha = a_fecha(r.get("fecha_evento"))
#         if not tipo or not seccion or not fecha:
#             continue

#         overrides[(tipo, seccion, fecha)] = r

#     return overrides


# # ============================================================
# # ASIGNACIÓN CÍCLICA DE CONTROLES
# # ============================================================
# def construir_mapa_asignacion_controles(df_evs, pools_por_seccion, overrides):
#     """
#     Para cada control por sección, asigna 1 responsable según ciclo.
#     El ciclo depende del orden cronológico de los controles de esa sección.
#     """
#     mapa = {}

#     df_ctrl = df_evs[df_evs["tipo_evento"].str.lower() == "control"].copy()
#     if df_ctrl.empty:
#         return mapa

#     df_ctrl = df_ctrl.sort_values(["sección", "fecha_evento", "observaciones"]).reset_index(drop=True)

#     for seccion, sub in df_ctrl.groupby("sección"):
#         pool = pools_por_seccion.get(seccion, [])
#         if not pool:
#             continue

#         n = len(pool)
#         sub = sub.sort_values(["fecha_evento", "observaciones"]).reset_index(drop=True)

#         for i, (_, ev) in enumerate(sub.iterrows()):
#             key = ("Control", seccion, ev["fecha_evento"])

#             # base del ciclo
#             elegido = pool[i % n]
#             responsables = [elegido["profesor"]]
#             slot_usado = elegido["slot"]

#             # override manual
#             ov = overrides.get(key)
#             if ov:
#                 if "slot" in ov:
#                     slot_override = str(ov.get("slot", "")).strip()
#                     for item in pool:
#                         if item["slot"] == slot_override:
#                             responsables = [item["profesor"]]
#                             slot_usado = item["slot"]
#                             break
#                 elif "responsables" in ov:
#                     responsables = split_profes(ov.get("responsables", []))
#                     slot_usado = "MANUAL"

#             mapa[(seccion, ev["fecha_evento"], ev["observaciones"])] = {
#                 "responsables": responsables,
#                 "slot": slot_usado
#             }

#     return mapa


# # ============================================================
# # LÓGICA DE RESPONSABLES SEGÚN TIPO DE EVENTO Y PASO
# # ============================================================
# # def resolver_responsables(
# #     tipo_evento,
# #     paso_key,
# #     seccion,
# #     fecha_evento,
# #     observaciones,
# #     participantes_por_seccion,
# #     pec_por_seccion,
# #     pcc,
# #     mapa_controles
# # ):

# def resolver_responsables(
#     tipo_evento,
#     paso_key,
#     seccion,
#     fecha_evento,
#     observaciones,
#     participantes_por_seccion,
#     pec_por_seccion,
#     pcc_por_seccion,
#     mapa_controles
# ):

#     participantes = participantes_por_seccion.get(seccion, [])
#     # pec = str(pec_por_seccion.get(seccion, "")).strip()
#     # pcc = str(pcc_por_seccion.get(seccion, "")).strip()
#     pec = str(pec_por_seccion.get(seccion, "")).strip()
#     pcc = str(pcc_por_seccion.get(seccion, "")).strip()

#     tipo_norm = str(tipo_evento).strip().lower()

#     # -------------------------
#     # CONTROL
#     # -------------------------
#     if tipo_norm == "control":
#         info_ctrl = mapa_controles.get((seccion, fecha_evento, observaciones), None)

#         if paso_key in ["construir_control", "escanear", "corregir_y_notas"]:
#             if info_ctrl:
#                 return info_ctrl["responsables"], f"Pool cíclico ({info_ctrl['slot']})"
#             return [], "Sin pool"

#         return [], "Paso no usado"

#     # -------------------------
#     # CERTAMEN
#     # -------------------------
#     if tipo_norm == "certamen":
#         if paso_key == "pedir_preguntas":
#             return participantes, "Todos los profesores participantes"
#         if paso_key in ["construir_control", "pauta_prueba", "revisar_prueba"]:
#             resp = []
#             if pec:
#                 resp.append(pec)
#             if pcc and pcc not in resp:
#                 resp.append(pcc)
#             return resp, "PEC + PCC"
#         if paso_key == "escanear":
#             return [pec] if pec else [], "PEC"
#         if paso_key == "corregir_y_notas":
#             return participantes, "Todos los profesores participantes"
#         return [], "Paso no usado"

#     # -------------------------
#     # TRABAJO PRÁCTICO
#     # -------------------------
#     if "trabajo" in tipo_norm:
#         if paso_key == "revisar_tp":
#             return participantes, "Cada profesor participante revisa su sección"
#         return [], "Paso no usado"

#     # -------------------------
#     # EXAMEN
#     # -------------------------
#     if tipo_norm == "examen":
#         if paso_key == "pedir_preguntas":
#             return participantes, "Todos los profesores participantes"
#         if paso_key in ["construir_examen", "pauta_examen"]:
#             resp = []
#             if pec:
#                 resp.append(pec)
#             if pcc and pcc not in resp:
#                 resp.append(pcc)
#             return resp, "PEC + PCC"
#         if paso_key == "corregir_examen":
#             return participantes, "Todos los profesores participantes"
#         return [], "Paso no usado"

#     return [], "Tipo de evento no reconocido"


# # ============================================================
# # CONSTRUCCIÓN DE MISIONES
# # ============================================================
# # def construir_misiones(config, df_cal):
# #     cfg_mis = config.get("misiones", {}) or {}
# #     protocolos = cfg_mis.get("protocolos", {}) or {}

# #     df_evs = detectar_evaluaciones(df_cal)

# #     if df_evs.empty:
# #         return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# #     # participantes_por_seccion = obtener_profes_participantes_por_seccion(config)
# #     # pcc, pec_por_seccion = obtener_coordinacion(cfg_mis)
# #     # pools_por_seccion = construir_pools_por_seccion(cfg_mis, participantes_por_seccion)
    
# #     participantes_por_seccion = obtener_profes_participantes_por_seccion(config)
# #     pec_por_seccion, pcc_por_seccion = obtener_coordinacion(cfg_mis)
# #     pools_por_seccion = construir_pools_por_seccion(config)

# #     overrides = construir_overrides(cfg_mis)

# #     mapa_controles = construir_mapa_asignacion_controles(df_evs, pools_por_seccion, overrides)

# #     filas = []

# #     for _, ev in df_evs.iterrows():
# #         tipo_evento = str(ev["tipo_evento"]).strip()
# #         evento = str(ev["nombre_evento"]).strip()
# #         seccion = str(ev["sección"]).strip()
# #         fecha_evento = pd.Timestamp(ev["fecha_evento"])
# #         observaciones = str(ev.get("observaciones", "")).strip()
# #         tema = str(ev.get("tema", "")).strip()

# #         tipo_norm = tipo_evento.lower()

# #         if tipo_norm == "control":
# #             proto = protocolos.get("Control", {})
# #         elif tipo_norm == "certamen":
# #             proto = protocolos.get("Certamen", {})
# #         elif "trabajo" in tipo_norm:
# #             proto = protocolos.get("Trabajo práctico", {})
# #         elif tipo_norm == "examen":
# #             proto = protocolos.get("Examen", {})
# #         else:
# #             proto = {}

# #         for paso_key, paso in proto.items():
# #             offset = int(paso.get("offset_dias", 0))
# #             fecha_limite = (fecha_evento + pd.Timedelta(days=offset)).date()

# #             # responsables_lista, criterio = resolver_responsables(
# #             #     tipo_evento=tipo_evento,
# #             #     paso_key=paso_key,
# #             #     seccion=seccion,
# #             #     fecha_evento=fecha_evento.date(),
# #             #     observaciones=observaciones,
# #             #     participantes_por_seccion=participantes_por_seccion,
# #             #     pec_por_seccion=pec_por_seccion,
# #             #     pcc=pcc,
# #             #     mapa_controles=mapa_controles
# #             # )
            
# #             responsables_lista, criterio = resolver_responsables(
# #                 tipo_evento=tipo_evento,
# #                 paso_key=paso_key,
# #                 seccion=seccion,
# #                 fecha_evento=fecha_evento.date(),
# #                 observaciones=observaciones,
# #                 participantes_por_seccion=participantes_por_seccion,
# #                 pec_por_seccion=pec_por_seccion,
# #                 pcc_por_seccion=pcc_por_seccion,
# #                 mapa_controles=mapa_controles
# #             )

# #             detalle_base = str(paso.get("detalle", "")).strip()
# #             detalle_partes = []

# #             if detalle_base:
# #                 detalle_partes.append(detalle_base)
# #             if observaciones:
# #                 detalle_partes.append(observaciones)
# #             if tema:
# #                 detalle_partes.append(f"Tema: {tema}")

# #             detalle = " — ".join(detalle_partes)

# #             filas.append({
# #                 "fecha_limite": fecha_limite,
# #                 "fecha_evento": fecha_evento.date(),
# #                 "evento": evento,
# #                 "tipo_evento": tipo_evento,
# #                 "paso": paso_key,
# #                 "sección": seccion,
# #                 "responsables": normalizar_responsables(responsables_lista),
# #                 "detalle": detalle,
# #                 "criterio_asignacion": criterio,
# #                 "estado": "Pendiente",
# #             })

# #     df_mis = pd.DataFrame(filas)
# #     if df_mis.empty:
# #         return df_mis, pd.DataFrame(), pd.DataFrame()

# #     df_mis = df_mis.sort_values(
# #         ["fecha_limite", "fecha_evento", "sección", "tipo_evento", "paso"]
# #     ).reset_index(drop=True)

# #     # Hoja chequeo: cómo quedó el ciclo de controles
# #     filas_chk = []
# #     df_ctrl = df_evs[df_evs["tipo_evento"].str.lower() == "control"].copy()
# #     df_ctrl = df_ctrl.sort_values(["sección", "fecha_evento", "observaciones"])

# #     for _, ev in df_ctrl.iterrows():
# #         seccion = str(ev["sección"]).strip()
# #         fecha_evento = ev["fecha_evento"]
# #         observaciones = str(ev.get("observaciones", "")).strip()

# #         info = mapa_controles.get((seccion, fecha_evento, observaciones), {})
# #         filas_chk.append({
# #             "sección": seccion,
# #             "fecha_evento": fecha_evento,
# #             "evento": str(ev["nombre_evento"]).strip(),
# #             "observaciones": observaciones,
# #             "slot_pool": info.get("slot", ""),
# #             "responsable_control": normalizar_responsables(info.get("responsables", [])),
# #         })

# #     df_chequeo = pd.DataFrame(filas_chk)

# #     # Hoja pools
# #     filas_pool = []
# #     for seccion, pool in pools_por_seccion.items():
# #         for item in pool:
# #             filas_pool.append({
# #                 "sección": seccion,
# #                 "slot": item["slot"],
# #                 "profesor": item["profesor"],
# #             })

# #     df_pools = pd.DataFrame(filas_pool)

# #     return df_mis, df_chequeo, df_pools


# # def construir_misiones(config, df_cal):
# #     cfg_mis = config.get("misiones", {}) or {}
# #     protocolos = cfg_mis.get("protocolos", {}) or {}

# #     df_evs = detectar_evaluaciones(df_cal)
# #     if df_evs.empty:
# #         return pd.DataFrame(columns=[
# #             "fecha_limite", "fecha_evento", "evento", "paso",
# #             "sección", "responsables", "detalle", "estado"
# #         ])

# #     df_evs["fecha_evento"] = pd.to_datetime(df_evs["fecha_evento"], errors="coerce")
# #     df_evs = df_evs.sort_values(["fecha_evento", "sección", "tipo_evento", "nombre_evento"]).reset_index(drop=True)

# #     filas = []

# #     contador_control_por_seccion = {}
# #     contador_lab_video_por_seccion = {}
# #     contador_taller_global = 0

# #     pcc, pec_por_seccion = obtener_coordinacion(config)

# #     for _, ev in df_evs.iterrows():
# #         tipo = str(ev.get("tipo_evento", "")).strip()
# #         nombre = str(ev.get("nombre_evento", tipo)).strip()
# #         seccion = str(ev.get("sección", "")).strip()
# #         fecha_evento = pd.Timestamp(ev["fecha_evento"])
# #         tema = str(ev.get("tema", "")).strip()
# #         obs_cal = str(ev.get("observaciones", "")).strip()

# #         tipo_norm = tipo.lower()

# #         if "control" in tipo_norm:
# #             proto_nombre = "Control"
# #         elif "taller" in tipo_norm:
# #             proto_nombre = "Taller"
# #         elif "certamen" in tipo_norm or "prueba" in tipo_norm:
# #             proto_nombre = "Certamen"
# #         elif "trabajo práctico" in tipo_norm or tipo_norm == "tp":
# #             proto_nombre = "Trabajo práctico"
# #         elif "examen" in tipo_norm:
# #             proto_nombre = "Examen"
# #         elif "laboratorio" in tipo_norm or "informe laboratorio" in tipo_norm:
# #             proto_nombre = "Laboratorio"
# #         else:
# #             continue

# #         proto = protocolos.get(proto_nombre, {})
# #         if not proto:
# #             continue

# #         participantes = obtener_pool_participantes_seccion(config, seccion)
# #         pool_lab = obtener_pool_laboratorio_seccion(config, seccion)
# #         pec = str(pec_por_seccion.get(seccion, "")).strip()

# #         override = buscar_override(config, proto_nombre, seccion, fecha_evento.date())

# #         detalle_base_evento = []
# #         if obs_cal:
# #             detalle_base_evento.append(obs_cal)
# #         if tema:
# #             detalle_base_evento.append(f"Tema: {tema}")
# #         detalle_base_evento = " — ".join(detalle_base_evento)

# #         # ========================================================
# #         # CONTROL
# #         # Un responsable cíclico por sección para TODO el control
# #         # ========================================================
# #         if proto_nombre == "Control":
# #             idx = contador_control_por_seccion.get(seccion, 0)

# #             if override and "responsables" in override:
# #                 responsable_control = normalizar_lista_profes(override.get("responsables", []))
# #             elif override and "slot" in override:
# #                 slot_idx = slot_a_indice(override.get("slot"))
# #                 if slot_idx is not None and participantes:
# #                     responsable_control = [participantes[slot_idx % len(participantes)]]
# #                 else:
# #                     responsable_control = elegir_ciclico(participantes, idx)
# #             else:
# #                 responsable_control = elegir_ciclico(participantes, idx)

# #             contador_control_por_seccion[seccion] = idx + 1

# #             for paso_key, paso in proto.items():
# #                 offset = int(paso.get("offset_dias", 0))
# #                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

# #                 detalle = str(paso.get("detalle", "")).strip()
# #                 if detalle_base_evento:
# #                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

# #                 filas.append({
# #                     "fecha_limite": deadline,
# #                     "fecha_evento": fecha_evento.date(),
# #                     "evento": nombre,
# #                     "paso": paso_key,
# #                     "sección": seccion,
# #                     "responsables": normalizar_profes_str(responsable_control),
# #                     "detalle": detalle,
# #                     "estado": "Pendiente",
# #                 })
# #             continue

# #         # ========================================================
# #         # TALLER
# #         # 4 profesores globales, 2 para A/B y 2 para C/D.
# #         # Luego cada uno corrige su propia versión.
# #         # ========================================================
# #         if proto_nombre == "Taller":
# #             pool_global = obtener_pool_global_participantes(config)

# #             if len(pool_global) == 0:
# #                 continue

# #             elegidos = elegir_varios_ciclico(pool_global, contador_taller_global, 4)
# #             contador_taller_global += 4

# #             while len(elegidos) < 4:
# #                 elegidos += elegir_varios_ciclico(pool_global, 0, 4 - len(elegidos))

# #             p1, p2, p3, p4 = elegidos[:4]

# #             for paso_key, paso in proto.items():
# #                 offset = int(paso.get("offset_dias", 0))
# #                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
# #                 detalle = str(paso.get("detalle", "")).strip()
# #                 if detalle_base_evento:
# #                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

# #                 if paso_key == "construir_taller":
# #                     filas.append({
# #                         "fecha_limite": deadline,
# #                         "fecha_evento": fecha_evento.date(),
# #                         "evento": nombre,
# #                         "paso": "construir_taller_AB",
# #                         "sección": seccion,
# #                         "responsables": normalizar_profes_str([p1, p2]),
# #                         "detalle": f"{detalle} — Versiones A y B.",
# #                         "estado": "Pendiente",
# #                     })
# #                     filas.append({
# #                         "fecha_limite": deadline,
# #                         "fecha_evento": fecha_evento.date(),
# #                         "evento": nombre,
# #                         "paso": "construir_taller_CD",
# #                         "sección": seccion,
# #                         "responsables": normalizar_profes_str([p3, p4]),
# #                         "detalle": f"{detalle} — Versiones C y D.",
# #                         "estado": "Pendiente",
# #                     })

# #                 elif paso_key == "corregir_taller":
# #                     for prof, version in [(p1, "A"), (p2, "B"), (p3, "C"), (p4, "D")]:
# #                         filas.append({
# #                             "fecha_limite": deadline,
# #                             "fecha_evento": fecha_evento.date(),
# #                             "evento": nombre,
# #                             "paso": f"corregir_taller_{version}",
# #                             "sección": seccion,
# #                             "responsables": normalizar_profes_str([prof]),
# #                             "detalle": f"{detalle} — Corregir versión {version}.",
# #                             "estado": "Pendiente",
# #                         })
# #                 else:
# #                     filas.append({
# #                         "fecha_limite": deadline,
# #                         "fecha_evento": fecha_evento.date(),
# #                         "evento": nombre,
# #                         "paso": paso_key,
# #                         "sección": seccion,
# #                         "responsables": normalizar_profes_str(elegidos),
# #                         "detalle": detalle,
# #                         "estado": "Pendiente",
# #                     })
# #             continue

# #         # ========================================================
# #         # CERTAMEN
# #         # pedir preguntas: todos los participantes
# #         # construir/pauta: PEC + PCC
# #         # corregir y notas: todos los participantes
# #         # ========================================================
# #         if proto_nombre == "Certamen":
# #             for paso_key, paso in proto.items():
# #                 offset = int(paso.get("offset_dias", 0))
# #                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
# #                 detalle = str(paso.get("detalle", "")).strip()
# #                 if detalle_base_evento:
# #                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

# #                 if paso_key == "pedir_preguntas":
# #                     responsables = participantes
# #                 elif paso_key in ["construir_control", "pauta_prueba", "revisar_prueba"]:
# #                     responsables = [x for x in [pec, pcc] if x]
# #                 elif paso_key == "corregir_y_notas":
# #                     responsables = participantes
# #                 else:
# #                     responsables = participantes

# #                 filas.append({
# #                     "fecha_limite": deadline,
# #                     "fecha_evento": fecha_evento.date(),
# #                     "evento": nombre,
# #                     "paso": paso_key,
# #                     "sección": seccion,
# #                     "responsables": normalizar_profes_str(responsables),
# #                     "detalle": detalle,
# #                     "estado": "Pendiente",
# #                 })
# #             continue

# #         # ========================================================
# #         # EXAMEN
# #         # igual que certamen
# #         # ========================================================
# #         if proto_nombre == "Examen":
# #             for paso_key, paso in proto.items():
# #                 offset = int(paso.get("offset_dias", 0))
# #                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
# #                 detalle = str(paso.get("detalle", "")).strip()
# #                 if detalle_base_evento:
# #                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

# #                 if paso_key == "pedir_preguntas":
# #                     responsables = participantes
# #                 elif paso_key in ["construir_examen", "pauta_examen"]:
# #                     responsables = [x for x in [pec, pcc] if x]
# #                 elif paso_key == "corregir_examen":
# #                     responsables = participantes
# #                 else:
# #                     responsables = participantes

# #                 filas.append({
# #                     "fecha_limite": deadline,
# #                     "fecha_evento": fecha_evento.date(),
# #                     "evento": nombre,
# #                     "paso": paso_key,
# #                     "sección": seccion,
# #                     "responsables": normalizar_profes_str(responsables),
# #                     "detalle": detalle,
# #                     "estado": "Pendiente",
# #                 })
# #             continue

# #         # ========================================================
# #         # TRABAJO PRÁCTICO
# #         # corrigen los profesores participantes de la sección
# #         # ========================================================
# #         if proto_nombre == "Trabajo práctico":
# #             for paso_key, paso in proto.items():
# #                 offset = int(paso.get("offset_dias", 0))
# #                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
# #                 detalle = str(paso.get("detalle", "")).strip()
# #                 if detalle_base_evento:
# #                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

# #                 filas.append({
# #                     "fecha_limite": deadline,
# #                     "fecha_evento": fecha_evento.date(),
# #                     "evento": nombre,
# #                     "paso": paso_key,
# #                     "sección": seccion,
# #                     "responsables": normalizar_profes_str(participantes),
# #                     "detalle": detalle,
# #                     "estado": "Pendiente",
# #                 })
# #             continue

# #         # ========================================================
# #         # LABORATORIO
# #         # preparar material previo -> PEC
# #         # grabar video -> 1 lab teacher cíclico
# #         # corregir informe -> todos los lab teachers de la sección
# #         # ========================================================
# #         if proto_nombre == "Laboratorio":
# #             idx_lab = contador_lab_video_por_seccion.get(seccion, 0)
# #             video_lab = elegir_ciclico(pool_lab, idx_lab)
# #             contador_lab_video_por_seccion[seccion] = idx_lab + 1

# #             for paso_key, paso in proto.items():
# #                 offset = int(paso.get("offset_dias", 0))
# #                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
# #                 detalle = str(paso.get("detalle", "")).strip()
# #                 if detalle_base_evento:
# #                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

# #                 if paso_key == "preparar_material_previo":
# #                     responsables = [pec] if pec else []
# #                 elif paso_key == "grabar_video_solucion":
# #                     responsables = video_lab
# #                 elif paso_key == "corregir_informe_laboratorio":
# #                     responsables = pool_lab
# #                 else:
# #                     responsables = pool_lab

# #                 filas.append({
# #                     "fecha_limite": deadline,
# #                     "fecha_evento": fecha_evento.date(),
# #                     "evento": nombre,
# #                     "paso": paso_key,
# #                     "sección": seccion,
# #                     "responsables": normalizar_profes_str(responsables),
# #                     "detalle": detalle,
# #                     "estado": "Pendiente",
# #                 })
# #             continue

# #     df_mis = pd.DataFrame(filas)
# #     if df_mis.empty:
# #         return pd.DataFrame(columns=[
# #             "fecha_limite", "fecha_evento", "evento", "paso",
# #             "sección", "responsables", "detalle", "estado"
# #         ])

# #     df_mis = df_mis.sort_values(["fecha_limite", "evento", "sección", "paso"]).reset_index(drop=True)
# #     return df_mis



# def construir_misiones(config, df_cal):
#     cfg_mis = config.get("misiones", {}) or {}
#     protocolos = cfg_mis.get("protocolos", {}) or {}

#     df_evs = detectar_evaluaciones(df_cal)

#     if df_evs.empty:
#         columnas = [
#             "fecha_limite", "fecha_evento", "evento", "tipo_evento", "paso",
#             "sección", "responsables", "detalle", "estado"
#         ]
#         return (
#             pd.DataFrame(columns=columnas),
#             pd.DataFrame(),
#             pd.DataFrame()
#         )

#     df_evs["fecha_evento"] = pd.to_datetime(df_evs["fecha_evento"], errors="coerce")
#     df_evs = df_evs.sort_values(
#         ["fecha_evento", "sección", "tipo_evento", "nombre_evento"]
#     ).reset_index(drop=True)

#     filas = []

#     contador_control_por_seccion = {}
#     contador_lab_video_por_seccion = {}
#     contador_taller_global = 0

#     pec_por_seccion, pcc_por_seccion = obtener_coordinacion(config)

#     # pools automáticos desde profesores_base / Seminario
#     pools_por_seccion = construir_pools_por_seccion(config)
#     overrides = construir_overrides(cfg_mis)

#     filas_chequeo = []
#     filas_pools = []

#     for seccion, pool in pools_por_seccion.items():
#         for item in pool:
#             filas_pools.append({
#                 "sección": seccion,
#                 "slot": item["slot"],
#                 "profesor": item["profesor"],
#             })

#     for _, ev in df_evs.iterrows():
#         tipo = str(ev.get("tipo_evento", "")).strip()
#         # nombre = str(ev.get("nombre_evento", tipo)).strip()
#         # nombre_base = str(ev.get("nombre_evento", tipo)).strip()
#         # obs_corta = str(ev.get("observaciones", "")).strip()
#         # nombre = obs_corta if obs_corta else nombre_base
#         nombre = nombre_evento_desde_ev(ev)
#         seccion = str(ev.get("sección", "")).strip()
#         fecha_evento = pd.Timestamp(ev["fecha_evento"])
#         tema = str(ev.get("tema", "")).strip()
#         obs_cal = str(ev.get("observaciones", "")).strip()

#         tipo_norm = tipo.lower()

#         if "control" in tipo_norm:
#             proto_nombre = "Control"
#         elif "taller" in tipo_norm:
#             proto_nombre = "Taller"
#         elif "certamen" in tipo_norm or "prueba" in tipo_norm:
#             proto_nombre = "Certamen"
#         elif "trabajo práctico" in tipo_norm or tipo_norm == "tp":
#             proto_nombre = "Trabajo práctico"
#         elif "examen" in tipo_norm:
#             proto_nombre = "Examen"
#         elif "laboratorio" in tipo_norm or "informe laboratorio" in tipo_norm:
#             proto_nombre = "Laboratorio"
#         else:
#             continue

#         proto = protocolos.get(proto_nombre, {})
#         if not proto:
#             continue

#         participantes = obtener_pool_participantes_seccion(config, seccion)
#         pool_lab = obtener_pool_laboratorio_seccion(config, seccion)
#         pec = str(pec_por_seccion.get(seccion, "")).strip()
#         pcc = str(pcc_por_seccion.get(seccion, "")).strip()

#         override = buscar_override(config, proto_nombre, seccion, fecha_evento.date())

#         detalle_base_evento = []
#         if obs_cal:
#             detalle_base_evento.append(obs_cal)
#         if tema:
#             detalle_base_evento.append(f"Tema: {tema}")
#         detalle_base_evento = " — ".join(detalle_base_evento)

#         # ========================================================
#         # CONTROL
#         # ========================================================
#         # if proto_nombre == "Control":
#         #     idx = contador_control_por_seccion.get(seccion, 0)

#         #     if override and "responsables" in override:
#         #         responsable_control = normalizar_lista_profes(override.get("responsables", []))
#         #         slot_usado = "MANUAL"
#         #     elif override and "slot" in override:
#         #         slot_idx = slot_a_indice(override.get("slot"))
#         #         if slot_idx is not None and participantes:
#         #             responsable_control = [participantes[slot_idx % len(participantes)]]
#         #             slot_usado = str(override.get("slot", "")).strip().upper()
#         #         else:
#         #             responsable_control = elegir_ciclico(participantes, idx)
#         #             slot_usado = pools_por_seccion.get(seccion, [])[idx % len(pools_por_seccion.get(seccion, []))]["slot"] if pools_por_seccion.get(seccion, []) else ""
#         #     else:
#         #         responsable_control = elegir_ciclico(participantes, idx)
#         #         slot_usado = pools_por_seccion.get(seccion, [])[idx % len(pools_por_seccion.get(seccion, []))]["slot"] if pools_por_seccion.get(seccion, []) else ""

#         #     contador_control_por_seccion[seccion] = idx + 1

#         #     filas_chequeo.append({
#         #         "sección": seccion,
#         #         "fecha_evento": fecha_evento.date(),
#         #         "evento": nombre,
#         #         "observaciones": obs_cal,
#         #         "slot_pool": slot_usado,
#         #         "responsable_control": normalizar_profes_str(responsable_control),
#         #     })

#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         filas.append({
#         #             "fecha_limite": deadline,
#         #             "fecha_evento": fecha_evento.date(),
#         #             "evento": nombre,
#         #             "tipo_evento": proto_nombre,
#         #             "paso": paso_key,
#         #             "sección": seccion,
#         #             "responsables": normalizar_profes_str(responsable_control),
#         #             "detalle": detalle,
#         #             "estado": "Pendiente",
#         #         })
#         #     continue

#         # if proto_nombre == "Control":
#         #     idx = contador_control_por_seccion.get(seccion, 0)
#         #     pool_ciclico = obtener_pool_ciclico_seccion(config, seccion)

#         #     if override and "responsables" in override:
#         #         responsable_control = normalizar_lista_profes(override.get("responsables", []))
#         #         slot_usado = "MANUAL"
#         #     elif override and "slot" in override:
#         #         slot_idx = slot_a_indice(override.get("slot"))
#         #         if slot_idx is not None and pool_ciclico:
#         #             responsable_control = [pool_ciclico[slot_idx % len(pool_ciclico)]]
#         #             slot_usado = str(override.get("slot", "")).strip().upper()
#         #         else:
#         #             responsable_control = elegir_ciclico(pool_ciclico, idx)
#         #             slot_usado = pools_por_seccion.get(seccion, [])[idx % len(pools_por_seccion.get(seccion, []))]["slot"] if pools_por_seccion.get(seccion, []) else ""
#         #     else:
#         #         responsable_control = elegir_ciclico(pool_ciclico, idx)
#         #         slot_usado = pools_por_seccion.get(seccion, [])[idx % len(pools_por_seccion.get(seccion, []))]["slot"] if pools_por_seccion.get(seccion, []) else ""

#         #     contador_control_por_seccion[seccion] = idx + 1

#         #     filas_chequeo.append({
#         #         "sección": seccion,
#         #         "fecha_evento": fecha_evento.date(),
#         #         "evento": nombre,
#         #         "observaciones": obs_cal,
#         #         "slot_pool": slot_usado,
#         #         "responsable_control": normalizar_profes_str(responsable_control),
#         #     })

#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         filas.append({
#         #             "fecha_limite": deadline,
#         #             "fecha_evento": fecha_evento.date(),
#         #             "evento": nombre,
#         #             "tipo_evento": proto_nombre,
#         #             "paso": paso_key,
#         #             "sección": seccion,
#         #             "responsables": normalizar_profes_str(responsable_control),
#         #             "detalle": detalle,
#         #             "estado": "Pendiente",
#         #         })
#         #     continue
        
        
#         if proto_nombre == "Control":
#             idx = contador_control_por_seccion.get(seccion, 0)

#             pool_control = obtener_pool_controles_seccion(config, seccion)
#             pool_slots = pools_por_seccion.get(seccion, [])

#             responsable_control = []
#             slot_usado = ""

#             if override and "responsables" in override:
#                 responsable_control = normalizar_lista_profes(override.get("responsables", []))
#                 slot_usado = "MANUAL"

#             elif override and "slot" in override:
#                 slot_override = str(override.get("slot", "")).strip().upper()
#                 encontrado = False
#                 for item in pool_slots:
#                     if str(item.get("slot", "")).strip().upper() == slot_override:
#                         responsable_control = [str(item.get("profesor", "")).strip()]
#                         slot_usado = slot_override
#                         encontrado = True
#                         break

#                 if not encontrado and pool_control:
#                     responsable_control = [str(pool_control[idx % len(pool_control)]).strip()]
#                     slot_usado = f"AUTO-{(idx % len(pool_control)) + 1}"

#             else:
#                 if pool_control:
#                     responsable_control = [str(pool_control[idx % len(pool_control)]).strip()]
#                     if pool_slots:
#                         slot_usado = str(pool_slots[idx % len(pool_slots)].get("slot", "")).strip()
#                     else:
#                         slot_usado = f"AUTO-{(idx % len(pool_control)) + 1}"

#             contador_control_por_seccion[seccion] = idx + 1

#             filas_chequeo.append({
#                 "sección": seccion,
#                 "fecha_evento": fecha_evento.date(),
#                 "evento": nombre,
#                 "observaciones": obs_cal,
#                 "slot_pool": slot_usado,
#                 "responsable_control": normalizar_profes_str(responsable_control),
#             })

#             for paso_key, paso in proto.items():
#                 offset = int(paso.get("offset_dias", 0))
#                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

#                 detalle = str(paso.get("detalle", "")).strip()
#                 if detalle_base_evento:
#                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#                 filas.append({
#                     "fecha_limite": deadline,
#                     "fecha_evento": fecha_evento.date(),
#                     "evento": nombre,
#                     "tipo_evento": proto_nombre,
#                     "paso": paso_key,
#                     "sección": seccion,
#                     "responsables": normalizar_profes_str(responsable_control),
#                     "detalle": detalle,
#                     "estado": "Pendiente",
#                 })
#             continue
        

#         # ========================================================
#         # TALLER
#         # ========================================================
#         # if proto_nombre == "Taller":
#         #     # pool_global = obtener_pool_global_participantes_ponderado(config)
#         #     pool_global = obtener_pool_global_ciclico(config)

#         #     if len(pool_global) == 0:
#         #         continue

#         #     elegidos = elegir_varios_ciclico(pool_global, contador_taller_global, 4)
#         #     contador_taller_global += 4

#         #     while len(elegidos) < 4:
#         #         elegidos += elegir_varios_ciclico(pool_global, 0, 4 - len(elegidos))

#         #     p1, p2, p3, p4 = elegidos[:4]

#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         if paso_key == "construir_taller":
#         #             filas.append({
#         #                 "fecha_limite": deadline,
#         #                 "fecha_evento": fecha_evento.date(),
#         #                 "evento": nombre,
#         #                 "tipo_evento": proto_nombre,
#         #                 "paso": "construir_taller_AB",
#         #                 "sección": seccion,
#         #                 "responsables": normalizar_profes_str([p1, p2]),
#         #                 "detalle": f"{detalle} — Versiones A y B.",
#         #                 "estado": "Pendiente",
#         #             })
#         #             filas.append({
#         #                 "fecha_limite": deadline,
#         #                 "fecha_evento": fecha_evento.date(),
#         #                 "evento": nombre,
#         #                 "tipo_evento": proto_nombre,
#         #                 "paso": "construir_taller_CD",
#         #                 "sección": seccion,
#         #                 "responsables": normalizar_profes_str([p3, p4]),
#         #                 "detalle": f"{detalle} — Versiones C y D.",
#         #                 "estado": "Pendiente",
#         #             })

#         #         elif paso_key == "corregir_taller":
#         #             for prof, version in [(p1, "A"), (p2, "B"), (p3, "C"), (p4, "D")]:
#         #                 filas.append({
#         #                     "fecha_limite": deadline,
#         #                     "fecha_evento": fecha_evento.date(),
#         #                     "evento": nombre,
#         #                     "tipo_evento": proto_nombre,
#         #                     "paso": f"corregir_taller_{version}",
#         #                     "sección": seccion,
#         #                     "responsables": normalizar_profes_str([prof]),
#         #                     "detalle": f"{detalle} — Corregir versión {version}.",
#         #                     "estado": "Pendiente",
#         #                 })
#         #         else:
#         #             filas.append({
#         #                 "fecha_limite": deadline,
#         #                 "fecha_evento": fecha_evento.date(),
#         #                 "evento": nombre,
#         #                 "tipo_evento": proto_nombre,
#         #                 "paso": paso_key,
#         #                 "sección": seccion,
#         #                 "responsables": normalizar_profes_str(elegidos),
#         #                 "detalle": detalle,
#         #                 "estado": "Pendiente",
#         #             })
#         #     continue
        
        
#         if proto_nombre == "Taller":
#             pool_global = obtener_pool_global_participantes(config)

#             if len(pool_global) == 0:
#                 continue

#             elegidos = elegir_varios_ciclico_sin_repetir(pool_global, contador_taller_global, 4)

#             if len(elegidos) < 4:
#                 faltan = 4 - len(elegidos)
#                 extra = elegir_varios_ciclico_sin_repetir(pool_global, contador_taller_global + 4, 4 + faltan)
#                 for p in extra:
#                     if p not in elegidos:
#                         elegidos.append(p)
#                     if len(elegidos) == 4:
#                         break

#             if len(elegidos) < 4:
#                 continue

#             contador_taller_global += 4

#             p1, p2, p3, p4 = elegidos[:4]

#             for paso_key, paso in proto.items():
#                 offset = int(paso.get("offset_dias", 0))
#                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#                 detalle = str(paso.get("detalle", "")).strip()
#                 if detalle_base_evento:
#                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#                 if paso_key == "construir_taller":
#                     filas.append({
#                         "fecha_limite": deadline,
#                         "fecha_evento": fecha_evento.date(),
#                         "evento": nombre,
#                         "tipo_evento": proto_nombre,
#                         "paso": "construir_taller_AB",
#                         "sección": seccion,
#                         "responsables": normalizar_profes_str([p1, p2]),
#                         "detalle": f"{detalle} — Versiones A y B.",
#                         "estado": "Pendiente",
#                     })
#                     filas.append({
#                         "fecha_limite": deadline,
#                         "fecha_evento": fecha_evento.date(),
#                         "evento": nombre,
#                         "tipo_evento": proto_nombre,
#                         "paso": "construir_taller_CD",
#                         "sección": seccion,
#                         "responsables": normalizar_profes_str([p3, p4]),
#                         "detalle": f"{detalle} — Versiones C y D.",
#                         "estado": "Pendiente",
#                     })

#                 elif paso_key == "corregir_taller":
#                     for prof, version in [(p1, "A"), (p2, "B"), (p3, "C"), (p4, "D")]:
#                         filas.append({
#                             "fecha_limite": deadline,
#                             "fecha_evento": fecha_evento.date(),
#                             "evento": nombre,
#                             "tipo_evento": proto_nombre,
#                             "paso": f"corregir_taller_{version}",
#                             "sección": seccion,
#                             "responsables": normalizar_profes_str([prof]),
#                             "detalle": f"{detalle} — Corregir versión {version}.",
#                             "estado": "Pendiente",
#                         })
#                 else:
#                     filas.append({
#                         "fecha_limite": deadline,
#                         "fecha_evento": fecha_evento.date(),
#                         "evento": nombre,
#                         "tipo_evento": proto_nombre,
#                         "paso": paso_key,
#                         "sección": seccion,
#                         "responsables": normalizar_profes_str(elegidos),
#                         "detalle": detalle,
#                         "estado": "Pendiente",
#                     })
#             continue

#         # ========================================================
#         # CERTAMEN
#         # ========================================================
#         # if proto_nombre == "Certamen":
#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         if paso_key == "pedir_preguntas":
#         #             responsables = participantes
#         #         elif paso_key in ["construir_control", "pauta_prueba", "revisar_prueba"]:
#         #             responsables = unicos([pec, pcc])
#         #         elif paso_key == "corregir_y_notas":
#         #             responsables = participantes
#         #         else:
#         #             responsables = participantes

#         #         filas.append({
#         #             "fecha_limite": deadline,
#         #             "fecha_evento": fecha_evento.date(),
#         #             "evento": nombre,
#         #             "tipo_evento": proto_nombre,
#         #             "paso": paso_key,
#         #             "sección": seccion,
#         #             "responsables": normalizar_profes_str(responsables),
#         #             "detalle": detalle,
#         #             "estado": "Pendiente",
#         #         })
#         #     continue


#         # if proto_nombre == "Certamen":
#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         if paso_key == "pedir_preguntas":
#         #             responsables = participantes
#         #         elif paso_key in ["construir_control", "pauta_prueba", "revisar_prueba"]:
#         #             responsables = [pec] if pec else []
#         #         elif paso_key == "corregir_y_notas":
#         #             responsables = participantes
#         #         else:
#         #             responsables = participantes
                    
#         #         filas.append({
#         #             "fecha_limite": deadline,
#         #             "fecha_evento": fecha_evento.date(),
#         #             "evento": nombre,
#         #             "tipo_evento": proto_nombre,
#         #             "paso": paso_key,
#         #             "sección": seccion,
#         #             "responsables": normalizar_profes_str(responsables),
#         #             "detalle": detalle,
#         #             "estado": "Pendiente",
#         #         })

#         # if proto_nombre == "Certamen":
#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         if paso_key == "pedir_preguntas":
#         #             responsables = participantes
#         #         elif paso_key in ["construir_control", "pauta_prueba", "revisar_prueba"]:
#         #             responsables = unicos([pec])
#         #         elif paso_key == "corregir_y_notas":
#         #             responsables = participantes
#         #         else:
#         #             responsables = participantes

#         #         filas.append({
#         #             "fecha_limite": deadline,
#         #             "fecha_evento": fecha_evento.date(),
#         #             "evento": nombre,
#         #             "tipo_evento": proto_nombre,
#         #             "paso": paso_key,
#         #             "sección": seccion,
#         #             "responsables": normalizar_profes_str(responsables),
#         #             "detalle": detalle,
#         #             "estado": "Pendiente",
#         #         })
#         #     continue
        
        
#         if proto_nombre == "Certamen":
#             for paso_key, paso in proto.items():
#                 offset = int(paso.get("offset_dias", 0))
#                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#                 detalle = str(paso.get("detalle", "")).strip()
#                 if detalle_base_evento:
#                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#                 if paso_key == "pedir_preguntas":
#                     responsables = participantes
#                 elif paso_key in ["construir_control", "pauta_prueba"]:
#                     responsables = [pec] if pec else []
#                 elif paso_key == "corregir_y_notas":
#                     responsables = participantes
#                 else:
#                     responsables = participantes

#                 filas.append({
#                     "fecha_limite": deadline,
#                     "fecha_evento": fecha_evento.date(),
#                     "evento": nombre,
#                     "tipo_evento": proto_nombre,
#                     "paso": paso_key,
#                     "sección": seccion,
#                     "responsables": normalizar_profes_str(responsables),
#                     "detalle": detalle,
#                     "estado": "Pendiente",
#                 })
#             continue
        

#         # ========================================================
#         # EXAMEN
#         # ========================================================
#         # if proto_nombre == "Examen":
#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         if paso_key == "pedir_preguntas":
#         #             responsables = participantes
#         #         elif paso_key in ["construir_examen", "pauta_examen"]:
#         #             responsables = unicos([pec, pcc])
#         #         elif paso_key == "corregir_examen":
#         #             responsables = participantes
#         #         else:
#         #             responsables = participantes

#         #         filas.append({
#         #             "fecha_limite": deadline,
#         #             "fecha_evento": fecha_evento.date(),
#         #             "evento": nombre,
#         #             "tipo_evento": proto_nombre,
#         #             "paso": paso_key,
#         #             "sección": seccion,
#         #             "responsables": normalizar_profes_str(responsables),
#         #             "detalle": detalle,
#         #             "estado": "Pendiente",
#         #         })
#         #     continue
        
#         # if proto_nombre == "Examen":
#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         if paso_key == "pedir_preguntas":
#         #             responsables = participantes
#         #         elif paso_key in ["construir_examen", "pauta_examen"]:
#         #             responsables = [pec] if pec else []
#         #         elif paso_key == "corregir_examen":
#         #             responsables = participantes
#         #         else:
#         #             responsables = participantes
                
#         #         filas.append({
#         #             "fecha_limite": deadline,
#         #             "fecha_evento": fecha_evento.date(),
#         #             "evento": nombre,
#         #             "tipo_evento": proto_nombre,
#         #             "paso": paso_key,
#         #             "sección": seccion,
#         #             "responsables": normalizar_profes_str(responsables),
#         #             "detalle": detalle,
#         #             "estado": "Pendiente",
#         #         })
        
#         # if proto_nombre == "Examen":
#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         if paso_key == "pedir_preguntas":
#         #             responsables = participantes
#         #         elif paso_key in ["construir_examen", "pauta_examen"]:
#         #             responsables = unicos([pec])
#         #         elif paso_key == "corregir_examen":
#         #             responsables = participantes
#         #         else:
#         #             responsables = participantes

#         #         filas.append({
#         #             "fecha_limite": deadline,
#         #             "fecha_evento": fecha_evento.date(),
#         #             "evento": nombre,
#         #             "tipo_evento": proto_nombre,
#         #             "paso": paso_key,
#         #             "sección": seccion,
#         #             "responsables": normalizar_profes_str(responsables),
#         #             "detalle": detalle,
#         #             "estado": "Pendiente",
#         #         })
#         #     continue

#         if proto_nombre == "Examen":
#             for paso_key, paso in proto.items():
#                 offset = int(paso.get("offset_dias", 0))
#                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#                 detalle = str(paso.get("detalle", "")).strip()
#                 if detalle_base_evento:
#                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#                 if paso_key == "pedir_preguntas":
#                     responsables = participantes
#                 elif paso_key in ["construir_examen", "pauta_examen"]:
#                     responsables = [pec] if pec else []
#                 elif paso_key == "corregir_examen":
#                     responsables = participantes
#                 else:
#                     responsables = participantes

#                 filas.append({
#                     "fecha_limite": deadline,
#                     "fecha_evento": fecha_evento.date(),
#                     "evento": nombre,
#                     "tipo_evento": proto_nombre,
#                     "paso": paso_key,
#                     "sección": seccion,
#                     "responsables": normalizar_profes_str(responsables),
#                     "detalle": detalle,
#                     "estado": "Pendiente",
#                 })
#             continue

#         # ========================================================
#         # TRABAJO PRÁCTICO
#         # ========================================================
#         # if proto_nombre == "Trabajo práctico":
#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         filas.append({
#         #             "fecha_limite": deadline,
#         #             "fecha_evento": fecha_evento.date(),
#         #             "evento": nombre,
#         #             "tipo_evento": proto_nombre,
#         #             "paso": paso_key,
#         #             "sección": seccion,
#         #             "responsables": normalizar_profes_str(participantes),
#         #             "detalle": detalle,
#         #             "estado": "Pendiente",
#         #         })
#         #     continue


#         if proto_nombre == "Trabajo práctico":
#             for paso_key, paso in proto.items():
#                 offset = int(paso.get("offset_dias", 0))
#                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#                 detalle = str(paso.get("detalle", "")).strip()
#                 if detalle_base_evento:
#                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#                 filas.append({
#                     "fecha_limite": deadline,
#                     "fecha_evento": fecha_evento.date(),
#                     "evento": nombre,
#                     "tipo_evento": proto_nombre,
#                     "paso": paso_key,
#                     "sección": seccion,
#                     "responsables": normalizar_profes_str(participantes),
#                     "detalle": detalle,
#                     "estado": "Pendiente",
#                 })
#             continue


#         # ========================================================
#         # LABORATORIO
#         # ========================================================
#         # if proto_nombre == "Laboratorio":
#         #     idx_lab = contador_lab_video_por_seccion.get(seccion, 0)
#         #     video_lab = elegir_ciclico(pool_lab, idx_lab)
#         #     contador_lab_video_por_seccion[seccion] = idx_lab + 1

#         #     for paso_key, paso in proto.items():
#         #         offset = int(paso.get("offset_dias", 0))
#         #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#         #         detalle = str(paso.get("detalle", "")).strip()
#         #         if detalle_base_evento:
#         #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#         #         if paso_key == "preparar_material_previo":
#         #             responsables = [pec] if pec else []
#         #         elif paso_key == "grabar_video_solucion":
#         #             responsables = video_lab
#         #         elif paso_key == "corregir_informe_laboratorio":
#         #             responsables = pool_lab
#         #         else:
#         #             responsables = pool_lab

#         #         filas.append({
#         #             "fecha_limite": deadline,
#         #             "fecha_evento": fecha_evento.date(),
#         #             "evento": nombre,
#         #             "tipo_evento": proto_nombre,
#         #             "paso": paso_key,
#         #             "sección": seccion,
#         #             "responsables": normalizar_profes_str(responsables),
#         #             "detalle": detalle,
#         #             "estado": "Pendiente",
#         #         })
#         #     continue
        
#         if proto_nombre == "Laboratorio":
#             idx_lab = contador_lab_video_por_seccion.get(seccion, 0)
#             video_lab = elegir_ciclico(pool_lab, idx_lab)
#             contador_lab_video_por_seccion[seccion] = idx_lab + 1

#             for paso_key, paso in proto.items():
#                 offset = int(paso.get("offset_dias", 0))
#                 deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
#                 detalle = str(paso.get("detalle", "")).strip()
#                 if detalle_base_evento:
#                     detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

#                 if paso_key == "preparar_material_previo":
#                     responsables = [pec] if pec else []
#                 elif paso_key == "grabar_video_solucion":
#                     responsables = video_lab
#                 elif paso_key == "corregir_informe_laboratorio":
#                     responsables = pool_lab
#                 else:
#                     responsables = pool_lab

#                 filas.append({
#                     "fecha_limite": deadline,
#                     "fecha_evento": fecha_evento.date(),
#                     "evento": nombre,
#                     "tipo_evento": proto_nombre,
#                     "paso": paso_key,
#                     "sección": seccion,
#                     "responsables": normalizar_profes_str(responsables),
#                     "detalle": detalle,
#                     "estado": "Pendiente",
#                 })
#             continue

#     df_mis = pd.DataFrame(filas)
#     if df_mis.empty:
#         columnas = [
#             "fecha_limite", "fecha_evento", "evento", "tipo_evento", "paso",
#             "sección", "responsables", "detalle", "estado"
#         ]
#         return (
#             pd.DataFrame(columns=columnas),
#             pd.DataFrame(filas_chequeo),
#             pd.DataFrame(filas_pools)
#         )

#     df_mis = df_mis.sort_values(
#         ["fecha_limite", "fecha_evento", "sección", "tipo_evento", "paso"]
#     ).reset_index(drop=True)

#     df_chequeo = pd.DataFrame(filas_chequeo)
#     df_pools = pd.DataFrame(filas_pools)

#     return df_mis, df_chequeo, df_pools


# # ============================================================
# # MATRIZ
# # ============================================================
# # def armar_matriz(df_mis, config):
# #     alias = config.get("misiones", {}).get("alias_seccion", {}) or {}

# #     if df_mis.empty:
# #         return pd.DataFrame()

# #     df = df_mis.copy()
# #     df["sección_col"] = df["sección"].apply(lambda s: alias.get(s, s))

# #     mat = df.pivot_table(
# #         index=["evento", "tipo_evento", "paso", "detalle"],
# #         columns="sección_col",
# #         values="responsables",
# #         aggfunc="first",
# #         fill_value=""
# #     ).reset_index()

# #     mat = mat.rename(columns={
# #         "evento": "Evaluación",
# #         "tipo_evento": "Tipo",
# #         "paso": "Misión",
# #         "detalle": "Detalle",
# #     })

# #     return mat


# def armar_matriz(df_mis, config):
#     alias = config.get("misiones", {}).get("alias_seccion", {}) or {}

#     if df_mis.empty:
#         return pd.DataFrame()

#     df = df_mis.copy()

#     for c in ["evento", "tipo_evento", "paso", "detalle", "sección", "responsables"]:
#         if c not in df.columns:
#             df[c] = ""
#         df[c] = df[c].fillna("").astype(str)

#     df["sección_col"] = df["sección"].apply(lambda s: alias.get(s, s))

#     mat = df.pivot_table(
#         index=["evento", "tipo_evento", "paso", "detalle"],
#         columns="sección_col",
#         values="responsables",
#         aggfunc="first",
#         fill_value=""
#     ).reset_index()

#     mat = mat.rename(columns={
#         "evento": "Evaluación",
#         "tipo_evento": "Tipo",
#         "paso": "Misión",
#         "detalle": "Detalle",
#     })

#     return mat


# # ============================================================
# # EXPORTAR
# # ============================================================
# def style_sheet(ws, header_color="1F4E78"):
#     fill_header = PatternFill("solid", fgColor=header_color)
#     font_header = Font(bold=True, color="FFFFFF")

#     for cell in ws[1]:
#         cell.fill = fill_header
#         cell.font = font_header
#         cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

#     ws.freeze_panes = "A2"
#     ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"

#     for col in range(1, ws.max_column + 1):
#         maxlen = 0
#         for r in range(1, ws.max_row + 1):
#             v = ws.cell(r, col).value
#             if v is None:
#                 continue
#             maxlen = max(maxlen, len(str(v)))
#         ws.column_dimensions[get_column_letter(col)].width = min(max(12, maxlen + 2), 60)


# def exportar_excel(df_mis, df_mat, df_chequeo, df_pools, path):
#     os.makedirs(os.path.dirname(path), exist_ok=True)

#     with pd.ExcelWriter(path, engine="openpyxl", datetime_format="DD/MM/YYYY") as writer:
#         df_mis.to_excel(writer, index=False, sheet_name="Misiones")
#         if not df_mat.empty:
#             df_mat.to_excel(writer, index=False, sheet_name="Matriz")
#         if not df_chequeo.empty:
#             df_chequeo.to_excel(writer, index=False, sheet_name="Chequeo")
#         if not df_pools.empty:
#             df_pools.to_excel(writer, index=False, sheet_name="Pools")

#         # Plan ordenado
#         orden = [
#             "pedir_preguntas",
#             "construir_control",
#             "pauta_prueba",
#             "revisar_prueba",
#             "escanear",
#             "corregir_y_notas",
#             "revisar_tp",
#             "construir_examen",
#             "pauta_examen",
#             "corregir_examen",
#         ]

#         df_plan = df_mis.copy()
#         df_plan["paso_rank"] = df_plan["paso"].apply(lambda x: orden.index(x) if x in orden else 999)
#         df_plan = df_plan.sort_values(["fecha_evento", "sección", "tipo_evento", "paso_rank"]).drop(columns=["paso_rank"])
#         df_plan.to_excel(writer, index=False, sheet_name="Plan")

#         wb = writer.book

#         style_sheet(wb["Misiones"], "5B2C6F")
#         style_sheet(wb["Plan"], "2C3E50")

#         if "Matriz" in wb.sheetnames:
#             style_sheet(wb["Matriz"], "7F7F7F")
#         if "Chequeo" in wb.sheetnames:
#             style_sheet(wb["Chequeo"], "0F766E")
#         if "Pools" in wb.sheetnames:
#             style_sheet(wb["Pools"], "92400E")

#         ws_mis = wb["Misiones"]
#         headers = [c.value for c in ws_mis[1]]

#         if "fecha_limite" in headers:
#             idx = headers.index("fecha_limite") + 1
#             fill_deadline = PatternFill("solid", fgColor="F4CCCC")
#             for r in range(2, ws_mis.max_row + 1):
#                 ws_mis.cell(r, idx).fill = fill_deadline
#                 ws_mis.cell(r, idx).alignment = Alignment(horizontal="center")


# # ============================================================
# # MAIN
# # ============================================================
# # def main():
# #     cursos = {
# #         "fokito": {
# #             "config_path": os.path.join("config", "calendario_fokito.yml"),
# #             "cal_path": os.path.join("data", "fokito", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "fokito", "misiones.xlsx"),
# #         },
# #         "tecnologia_medica": {
# #             "config_path": os.path.join("config", "calendario_tecnologia_medica.yml"),
# #             "cal_path": os.path.join("data", "tecnologia_medica", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "tecnologia_medica", "misiones.xlsx"),
# #         },
# #         "medicina": {
# #             "config_path": os.path.join("config", "calendario_medicina.yml"),
# #             "cal_path": os.path.join("data", "medicina", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "medicina", "misiones.xlsx"),
# #         },
# #         "enobnu": {
# #             "config_path": os.path.join("config", "calendario_enobnu.yml"),
# #             "cal_path": os.path.join("data", "enobnu", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "enobnu", "misiones.xlsx"),
# #         },
# #     }

# #     for curso, info in cursos.items():
# #         config_path = info["config_path"]
# #         cal_path = info["cal_path"]
# #         out_path = info["out_path"]

# #         if not os.path.exists(config_path):
# #             print(f"⚠️  Saltando {curso}: no existe {config_path}")
# #             continue

# #         if not os.path.exists(cal_path):
# #             print(f"⚠️  Saltando {curso}: no existe {cal_path}. Genera primero el calendario.")
# #             continue

# #         config = cargar_yaml(config_path)
# #         df_cal = pd.read_excel(cal_path, sheet_name="Calendario")

# #         df_mis, df_chequeo, df_pools = construir_misiones(config, df_cal)
# #         df_mat = armar_matriz(df_mis, config)

# #         exportar_excel(df_mis, df_mat, df_chequeo, df_pools, out_path)

# #         print(f"OK: [{curso}] generado {out_path} con {len(df_mis)} tareas.")

# #         if not df_chequeo.empty:
# #             print("  Controles asignados:")
# #             print(df_chequeo[["sección", "fecha_evento", "slot_pool", "responsable_control"]].to_string(index=False))

# # def main():
# #     cursos = {
# #         "fokito": {
# #             "config_path": os.path.join("config", "calendario_fokito.yml"),
# #             "cal_path": os.path.join("data", "fokito", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "fokito", "misiones.xlsx"),
# #         },
# #         "tecnologia_medica": {
# #             "config_path": os.path.join("config", "calendario_tecnologia_medica.yml"),
# #             "cal_path": os.path.join("data", "tecnologia_medica", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "tecnologia_medica", "misiones.xlsx"),
# #         },
# #         "medicina": {
# #             "config_path": os.path.join("config", "calendario_medicina.yml"),
# #             "cal_path": os.path.join("data", "medicina", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "medicina", "misiones.xlsx"),
# #         },
# #         "enobnu": {
# #             "config_path": os.path.join("config", "calendario_enobnu.yml"),
# #             "cal_path": os.path.join("data", "enobnu", "calendario.xlsx"),
# #             "out_path": os.path.join("data", "enobnu", "misiones.xlsx"),
# #         },
# #     }

# #     for curso, info in cursos.items():
# #         config_path = info["config_path"]
# #         cal_path = info["cal_path"]
# #         out_path = info["out_path"]

# #         if not os.path.exists(config_path):
# #             print(f"⚠️  Saltando {curso}: no existe {config_path}")
# #             continue

# #         if not os.path.exists(cal_path):
# #             print(f"⚠️  Saltando {curso}: no existe {cal_path}. Genera primero el calendario.")
# #             continue

# #         config = cargar_yaml(config_path)
# #         df_cal = pd.read_excel(cal_path, sheet_name="Calendario")

# #         estados_previos = cargar_estados_previos(out_path)

# #         df_mis = construir_misiones(config, df_cal)
# #         df_mis = aplicar_estados_previos(df_mis, estados_previos)

# #         df_mat = armar_matriz(df_mis, config)

# #         # hojas auxiliares vacías por ahora
# #         df_chequeo = pd.DataFrame()
# #         df_pools = pd.DataFrame()

# #         exportar_excel(df_mis, df_mat, df_chequeo, df_pools, out_path)

# #         print(f"OK: [{curso}] generado {out_path} con {len(df_mis)} tareas.")


# def main():
#     cursos = {
#         "fokito": {
#             "config_path": os.path.join("config", "calendario_fokito.yml"),
#             "cal_path": os.path.join("data", "fokito", "calendario.xlsx"),
#             "out_path": os.path.join("data", "fokito", "misiones.xlsx"),
#         },
#         "tecnologia_medica": {
#             "config_path": os.path.join("config", "calendario_tecnologia_medica.yml"),
#             "cal_path": os.path.join("data", "tecnologia_medica", "calendario.xlsx"),
#             "out_path": os.path.join("data", "tecnologia_medica", "misiones.xlsx"),
#         },
#         "medicina": {
#             "config_path": os.path.join("config", "calendario_medicina.yml"),
#             "cal_path": os.path.join("data", "medicina", "calendario.xlsx"),
#             "out_path": os.path.join("data", "medicina", "misiones.xlsx"),
#         },
#         "enobnu": {
#             "config_path": os.path.join("config", "calendario_enobnu.yml"),
#             "cal_path": os.path.join("data", "enobnu", "calendario.xlsx"),
#             "out_path": os.path.join("data", "enobnu", "misiones.xlsx"),
#         },
#     }

#     for curso, info in cursos.items():
#         config_path = info["config_path"]
#         cal_path = info["cal_path"]
#         out_path = info["out_path"]

#         if not os.path.exists(config_path):
#             print(f"⚠️  Saltando {curso}: no existe {config_path}")
#             continue

#         if not os.path.exists(cal_path):
#             print(f"⚠️  Saltando {curso}: no existe {cal_path}. Genera primero el calendario.")
#             continue

#         config = cargar_yaml(config_path)
#         df_cal = pd.read_excel(cal_path, sheet_name="Calendario")

#         estados_previos = cargar_estados_previos(out_path)

#         # OJO: construir_misiones devuelve 3 cosas
#         df_mis, df_chequeo, df_pools = construir_misiones(config, df_cal)

#         df_mis = aplicar_estados_previos(df_mis, estados_previos)
#         df_mat = armar_matriz(df_mis, config)

#         exportar_excel(df_mis, df_mat, df_chequeo, df_pools, out_path)

#         print(f"OK: [{curso}] generado {out_path} con {len(df_mis)} tareas.")

#         if not df_chequeo.empty:
#             print("  Controles asignados:")
#             print(
#                 df_chequeo[
#                     ["sección", "fecha_evento", "slot_pool", "responsable_control"]
#                 ].to_string(index=False)
#             )


# if __name__ == "__main__":
#     main()














import os
import yaml
import pandas as pd

from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter


# ============================================================
# YAML / HELPERS
# ============================================================
def cargar_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def split_profes(valor):
    """
    Acepta:
    - None
    - "A, B, C"
    - ["A", "B", "C"]
    y preserva duplicados si vienen en lista/string.
    """
    if valor is None:
        return []

    try:
        if pd.isna(valor):
            return []
    except Exception:
        pass

    if isinstance(valor, (list, tuple)):
        return [str(x).strip() for x in valor if str(x).strip()]

    texto = str(valor).strip()
    if not texto:
        return []

    return [x.strip() for x in texto.split(",") if x.strip()]


def normalizar_lista_profes(valor):
    return split_profes(valor)


def normalizar_profes_str(valor):
    return ", ".join(split_profes(valor))


def unicos(lista):
    salida = []
    for x in lista:
        sx = str(x).strip()
        if sx and sx not in salida:
            salida.append(sx)
    return salida


def a_fecha(x):
    ts = pd.to_datetime(x, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.date()


def construir_horas_seminario_map(df_cal):
    df_horas = horas_seminario_por_profesor(df_cal)
    if df_horas.empty:
        return {}
    return dict(zip(df_horas["profesor"], df_horas["horas_seminario"]))


def score_balance(profesor, carga_actual, horas_map):
    horas = float(horas_map.get(profesor, 0.0))
    carga = float(carga_actual.get(profesor, 0.0))

    if horas <= 0:
        return -10**9

    return horas / (carga + 1.0)


def elegir_balanceado(pool, carga_actual, horas_map, cantidad=1, excluir=None):
    if excluir is None:
        excluir = set()
    else:
        excluir = set(excluir)

    candidatos = [p for p in unicos(pool) if p not in excluir]

    if not candidatos:
        return []

    candidatos = sorted(
        candidatos,
        key=lambda p: (
            score_balance(p, carga_actual, horas_map),
            float(horas_map.get(p, 0.0)),
            -float(carga_actual.get(p, 0.0)),
            p
        ),
        reverse=True
    )

    return candidatos[:cantidad]


def sumar_carga(carga_actual, responsables, peso=1.0):
    for p in split_profes(responsables):
        carga_actual[p] = float(carga_actual.get(p, 0.0)) + float(peso)


def construir_id_mision(row):
    """
    ID estable para preservar estado entre regeneraciones.
    """
    fecha_limite = pd.to_datetime(row.get("fecha_limite"), errors="coerce")
    fecha_evento = pd.to_datetime(row.get("fecha_evento"), errors="coerce")

    fecha_limite_str = fecha_limite.strftime("%Y-%m-%d") if pd.notna(fecha_limite) else ""
    fecha_evento_str = fecha_evento.strftime("%Y-%m-%d") if pd.notna(fecha_evento) else ""

    partes = [
        fecha_limite_str,
        fecha_evento_str,
        str(row.get("evento", "")).strip(),
        str(row.get("tipo_evento", "")).strip(),
        str(row.get("paso", "")).strip(),
        str(row.get("sección", "")).strip(),
        str(row.get("responsables", "")).strip(),
    ]
    return "||".join(partes)


def cargar_estados_previos(path_excel):
    """
    Lee el Excel previo y devuelve {id_mision: estado}
    """
    if not os.path.exists(path_excel):
        return {}

    try:
        df_prev = pd.read_excel(path_excel, sheet_name="Misiones")
    except Exception:
        return {}

    if df_prev.empty:
        return {}

    for c in ["fecha_limite", "fecha_evento"]:
        if c in df_prev.columns:
            df_prev[c] = pd.to_datetime(df_prev[c], errors="coerce")

    for c in ["evento", "tipo_evento", "paso", "sección", "responsables", "estado"]:
        if c in df_prev.columns:
            df_prev[c] = df_prev[c].fillna("").astype(str)
        else:
            df_prev[c] = ""

    estados = {}
    for _, row in df_prev.iterrows():
        id_mision = construir_id_mision(row)
        estado = str(row.get("estado", "")).strip() or "Pendiente"
        estados[id_mision] = estado

    return estados


def aplicar_estados_previos(df_mis, estados_previos):
    if df_mis.empty:
        return df_mis

    df = df_mis.copy()
    df["id_mision"] = df.apply(construir_id_mision, axis=1)
    df["estado"] = df["id_mision"].apply(lambda x: estados_previos.get(x, "Pendiente"))
    return df


# ============================================================
# LECTURA DE CONFIG DEL CURSO
# ============================================================
def obtener_profesores_base(config):
    """
    Devuelve dict:
    {(seccion, actividad): [prof1, prof2, ...]}
    """
    salida = {}
    for r in config.get("calendario", {}).get("profesores_base", []) or []:
        secc = str(r.get("seccion", "")).strip()
        act = str(r.get("actividad", "")).strip()
        profes = split_profes(r.get("profesores", []))
        salida[(secc, act)] = profes
    return salida


def obtener_coordinacion(config):
    """
    Lee:
    misiones:
      coordinacion:
        pec_por_seccion:
          "Sección 1": "CC"
        pcc_por_seccion:
          "Sección 1": "TY"
    """
    mis = config.get("misiones", {}) or {}
    coord = mis.get("coordinacion", {}) or {}

    pec_por_seccion = coord.get("pec_por_seccion", {}) or {}
    pcc_por_seccion = coord.get("pcc_por_seccion", {}) or {}

    return pec_por_seccion, pcc_por_seccion


def obtener_lista_seminario_seccion(config, seccion, mantener_duplicados=True):
    """
    Devuelve la lista de profesores de seminario de una sección.
    - Si mantener_duplicados=True, respeta repeticiones como ["SM", "XX", "XX"].
    - Si False, devuelve únicos preservando orden.
    """
    mapa = obtener_profesores_base(config)
    lista = mapa.get((seccion, "Seminario"), []).copy()

    if mantener_duplicados:
        return [str(x).strip() for x in lista if str(x).strip()]

    return unicos(lista)


# def obtener_pool_participantes_seccion(config, seccion):
#     """
#     Profesores participantes de la sección para misiones colectivas.
#     IMPORTANTE:
#     - NO excluye PEC ni PCC.
#     - Si alguien hace seminario, cuenta como participante aunque además sea PEC/PCC.
#     """
#     return obtener_lista_seminario_seccion(config, seccion, mantener_duplicados=False)


def obtener_pool_participantes_seccion(config, seccion):
    """
    Pool de profesores participantes de la sección para misiones colectivas.
    IMPORTANTE:
    - mantiene duplicados
    - si un profesor aparece dos veces en seminario, también aparece dos veces aquí
    """
    return obtener_lista_seminario_seccion(config, seccion, mantener_duplicados=True)


def obtener_pool_controles_seccion(config, seccion):
    """
    Pool ponderado para controles.
    Aquí sí se respetan duplicados del YAML, por ejemplo:
    ["SM", "XX", "XX"] -> XX tiene doble peso.
    """
    return obtener_lista_seminario_seccion(config, seccion, mantener_duplicados=True)




def obtener_pool_global_participantes(config):
    """
    Pool global ponderado para talleres.
    Junta todas las listas de seminario de todas las secciones,
    respetando duplicados dentro de cada sección.
    """
    secciones = list((config.get("calendario", {}).get("secciones", {}) or {}).keys())
    salida = []

    for seccion in secciones:
        salida.extend(obtener_lista_seminario_seccion(config, seccion, mantener_duplicados=True))

    return [str(x).strip() for x in salida if str(x).strip()]


def obtener_pool_laboratorio_seccion(config, seccion):
    mapa = obtener_profesores_base(config)
    return mapa.get((seccion, "Laboratorio"), []).copy()


# ============================================================
# POOLS / OVERRIDES
# ============================================================
def construir_pools_por_seccion(config):
    """
    Pool cíclico automático desde profesores_base / Seminario.
    Respeta duplicados para ponderar carga.
    Ejemplo:
      ["SM", "XX", "XX"] -> slots A=SM, B=XX, C=XX
    """
    cfg_cal = config.get("calendario", {}) or {}
    base = cfg_cal.get("profesores_base", []) or []

    pools = {}
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    for r in base:
        seccion = str(r.get("seccion", "")).strip()
        actividad = str(r.get("actividad", "")).strip()
        profesores = split_profes(r.get("profesores", ""))

        if not seccion or actividad != "Seminario":
            continue

        pool = []
        for i, prof in enumerate(profesores):
            if i >= len(letras):
                break
            pool.append({
                "slot": letras[i],
                "profesor": prof
            })

        pools[seccion] = pool

    return pools


def construir_overrides(cfg_mis):
    """
    Índice por:
    (tipo_evento, seccion, fecha_evento)
    """
    overrides = {}
    for r in cfg_mis.get("overrides_responsables", []) or []:
        tipo = str(r.get("tipo_evento", "")).strip()
        seccion = str(r.get("seccion", "")).strip()
        fecha = a_fecha(r.get("fecha_evento"))
        if not tipo or not seccion or not fecha:
            continue

        overrides[(tipo, seccion, fecha)] = r

    return overrides


# def buscar_override(config, tipo_evento, seccion, fecha_evento):
#     mis = config.get("misiones", {}) or {}
#     overrides = mis.get("overrides_responsables", []) or []

#     fecha_evento_str = pd.Timestamp(fecha_evento).strftime("%Y-%m-%d")

#     for ov in overrides:
#         tipo_ov = str(ov.get("tipo_evento", "")).strip().lower()
#         seccion_ov = str(ov.get("seccion", "")).strip()
#         fecha_ov = str(ov.get("fecha_evento", "")).strip()

#         if tipo_ov == str(tipo_evento).strip().lower() and seccion_ov == seccion and fecha_ov == fecha_evento_str:
#             return ov

#     return None



def buscar_override(config, tipo_evento, seccion, fecha_evento, paso=None):
    mis = config.get("misiones", {}) or {}
    overrides = mis.get("overrides_responsables", []) or []

    fecha_evento_str = pd.Timestamp(fecha_evento).strftime("%Y-%m-%d")

    for ov in overrides:
        tipo_ov = str(ov.get("tipo_evento", "")).strip().lower()
        seccion_ov = str(ov.get("seccion", "")).strip()
        fecha_ov = str(ov.get("fecha_evento", "")).strip()
        paso_ov = str(ov.get("paso", "")).strip()

        if tipo_ov != str(tipo_evento).strip().lower():
            continue
        if seccion_ov != seccion:
            continue
        if fecha_ov != fecha_evento_str:
            continue

        if paso is not None and paso_ov:
            if paso_ov != paso:
                continue

        return ov

    return None





def slot_a_indice(slot):
    slot = str(slot).strip().upper()
    mapa = {
        "A": 0, "B": 1, "C": 2, "D": 3,
        "E": 4, "F": 5, "G": 6, "H": 7
    }
    return mapa.get(slot, None)


def elegir_ciclico(pool, indice):
    if not pool:
        return []
    return [pool[indice % len(pool)]]


# def elegir_varios_ciclico_sin_repetir(pool, inicio, cantidad):
#     """
#     Elige 'cantidad' profesores recorriendo un pool ponderado en forma cíclica,
#     pero evitando repetir a la misma persona dentro de la misma asignación.
#     """
#     if not pool or cantidad <= 0:
#         return []

#     n = len(pool)
#     elegidos = []
#     vistos = set()
#     intentos = 0
#     idx = inicio

#     while len(elegidos) < cantidad and intentos < 10 * n:
#         prof = str(pool[idx % n]).strip()
#         if prof and prof not in vistos:
#             elegidos.append(prof)
#             vistos.add(prof)
#         idx += 1
#         intentos += 1

#     return elegidos


def elegir_varios_ciclico_sin_repetir(pool, inicio, cantidad):
    """
    Elige 'cantidad' profesores recorriendo un pool ponderado en forma cíclica,
    evitando repetir a la misma persona dentro de la misma asignación.

    IMPORTANTE:
    devuelve también el nuevo cursor REAL, según cuántas posiciones
    se recorrieron efectivamente en el pool.
    """
    if not pool or cantidad <= 0:
        return [], inicio

    n = len(pool)
    elegidos = []
    vistos = set()
    intentos = 0
    idx = inicio

    while len(elegidos) < cantidad and intentos < 10 * n:
        prof = str(pool[idx % n]).strip()
        if prof and prof not in vistos:
            elegidos.append(prof)
            vistos.add(prof)
        idx += 1
        intentos += 1

    return elegidos, idx

# ============================================================
# DETECCIÓN DE EVALUACIONES
# ============================================================
def nombre_evento_desde_ev(ev):
    """
    Define un nombre amigable del evento sin confundirlo con observaciones
    administrativas o feriados.
    """
    tipo = str(ev.get("tipo_evento", "")).strip()
    nombre_base = str(ev.get("nombre_evento", tipo)).strip()
    obs = str(ev.get("observaciones", "")).strip()

    obs_low = obs.lower()

    palabras_feriado = [
        "san pedro", "san pablo", "feriado", "pausa académica",
        "trabajo autónomo", "receso", "no hay clases"
    ]

    if obs and not any(p in obs_low for p in palabras_feriado):
        return obs

    return nombre_base


def detectar_evaluaciones(df_cal):
    df = df_cal.copy()

    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    for c in ["evaluación", "actividad", "sección", "tema", "observaciones"]:
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str)

    evs = []

    sub = df[df["evaluación"].str.strip() != ""].copy()

    for _, r in sub.iterrows():
        evs.append({
            "tipo_evento": str(r["evaluación"]).strip(),
            "nombre_evento": str(r["evaluación"]).strip(),
            "sección": str(r.get("sección", "")).strip(),
            "actividad": str(r.get("actividad", "")).strip(),
            "fecha_evento": pd.Timestamp(r["fecha"]).date(),
            "tema": str(r.get("tema", "")).strip(),
            "observaciones": str(r.get("observaciones", "")).strip(),
        })

    df_evs = pd.DataFrame(evs)

    if df_evs.empty:
        return df_evs

    df_evs = df_evs.sort_values(
        ["fecha_evento", "sección", "tipo_evento", "actividad", "nombre_evento"]
    ).reset_index(drop=True)

    return df_evs







import matplotlib.pyplot as plt


def horas_seminario_por_profesor(df_cal):
    df = df_cal.copy()

    for c in ["actividad", "profesores", "horario"]:
        if c not in df.columns:
            df[c] = ""

    df = df[df["actividad"].astype(str).str.strip() == "Seminario"].copy()

    filas = []
    for _, row in df.iterrows():
        horario = str(row.get("horario", "")).strip()
        profes = split_profes(row.get("profesores", ""))

        duracion = 0.0
        m = pd.Series([horario]).astype(str).str.replace("–", "-", regex=False).iloc[0]
        mm = __import__("re").match(r"^\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*$", m)
        if mm:
            t1 = pd.to_datetime(mm.group(1), format="%H:%M", errors="coerce")
            t2 = pd.to_datetime(mm.group(2), format="%H:%M", errors="coerce")
            if pd.notna(t1) and pd.notna(t2):
                duracion = (t2 - t1).total_seconds() / 3600.0

        for p in profes:
            filas.append({"profesor": p, "horas": duracion})

    if not filas:
        return pd.DataFrame(columns=["profesor", "horas_seminario"])

    out = pd.DataFrame(filas).groupby("profesor", as_index=False)["horas"].sum()
    out = out.rename(columns={"horas": "horas_seminario"})
    return out


# def misiones_seminario_por_profesor(df_mis):
#     if df_mis.empty:
#         return pd.DataFrame(columns=["profesor", "misiones_seminario"])

#     df = df_mis.copy()

#     # excluimos laboratorio
#     df = df[df["tipo_evento"].astype(str).str.strip() != "Laboratorio"].copy()

#     filas = []
#     for _, row in df.iterrows():
#         for p in split_profes(row.get("responsables", "")):
#             filas.append({"profesor": p, "misiones_seminario": 1})

#     if not filas:
#         return pd.DataFrame(columns=["profesor", "misiones_seminario"])

#     out = pd.DataFrame(filas).groupby("profesor", as_index=False)["misiones_seminario"].sum()
#     return out


def misiones_seminario_por_profesor(df_mis):
    if df_mis.empty:
        return pd.DataFrame(columns=["profesor", "misiones_seminario"])

    df = df_mis.copy()

    # solo misiones realmente repartibles respecto a horas de seminario
    pasos_validos = {
        "construir_control",
        "escanear",
        "corregir_y_notas",
        "revisar_tp",
        "construir_taller",
        "corregir_taller",
        "revisar_portafolio",
    }

    df = df[df["paso"].astype(str).str.strip().isin(pasos_validos)].copy()

    filas = []
    for _, row in df.iterrows():
        for p in split_profes(row.get("responsables", "")):
            filas.append({"profesor": p, "misiones_seminario": 1})

    if not filas:
        return pd.DataFrame(columns=["profesor", "misiones_seminario"])

    out = pd.DataFrame(filas).groupby("profesor", as_index=False)["misiones_seminario"].sum()
    return out


def graficar_equilibrio_curso(nombre_curso, df_cal, df_mis, carpeta_salida):
    df_horas = horas_seminario_por_profesor(df_cal)
    df_misiones_prof = misiones_seminario_por_profesor(df_mis)

    df_plot = pd.merge(df_horas, df_misiones_prof, on="profesor", how="outer").fillna(0)

    if df_plot.empty:
        print(f"⚠️ No hay datos para graficar equilibrio en {nombre_curso}")
        return

    df_plot["ratio_horas_por_mision"] = df_plot.apply(
        lambda r: (r["horas_seminario"] / r["misiones_seminario"]) if r["misiones_seminario"] > 0 else 0,
        axis=1
    )

    df_plot = df_plot.sort_values("ratio_horas_por_mision", ascending=False).reset_index(drop=True)

    plt.figure(figsize=(10, 5))
    plt.bar(df_plot["profesor"], df_plot["ratio_horas_por_mision"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Horas de seminario / misiones")
    plt.title(f"Equilibrio de carga — {nombre_curso}")
    plt.tight_layout()

    os.makedirs(carpeta_salida, exist_ok=True)
    path_png = os.path.join(carpeta_salida, "equilibrio_carga.png")
    plt.savefig(path_png, dpi=200)
    plt.close()

    print(f"✅ Gráfico de equilibrio guardado en: {path_png}")
    print(df_plot.to_string(index=False))






# ============================================================
# CONSTRUCCIÓN DE MISIONES
# ============================================================
def construir_misiones(config, df_cal):
    cfg_mis = config.get("misiones", {}) or {}
    protocolos = cfg_mis.get("protocolos", {}) or {}

    df_evs = detectar_evaluaciones(df_cal)

    if df_evs.empty:
        columnas = [
            "fecha_limite", "fecha_evento", "evento", "tipo_evento", "paso",
            "sección", "responsables", "detalle", "estado"
        ]
        return (
            pd.DataFrame(columns=columnas),
            pd.DataFrame(),
            pd.DataFrame()
        )

    df_evs["fecha_evento"] = pd.to_datetime(df_evs["fecha_evento"], errors="coerce")
    df_evs = df_evs.sort_values(
        ["fecha_evento", "sección", "tipo_evento", "nombre_evento"]
    ).reset_index(drop=True)

    filas = []
    filas_chequeo = []
    filas_pools = []

    contador_control_por_seccion = {}
    contador_lab_video_por_seccion = {}
    contador_taller_global = 0
    horas_map = construir_horas_seminario_map(df_cal)
    carga_actual = {}

    pec_por_seccion, pcc_por_seccion = obtener_coordinacion(config)
    pools_por_seccion = construir_pools_por_seccion(config)

    for seccion, pool in pools_por_seccion.items():
        for item in pool:
            filas_pools.append({
                "sección": seccion,
                "slot": item["slot"],
                "profesor": item["profesor"],
            })

    for _, ev in df_evs.iterrows():
        tipo = str(ev.get("tipo_evento", "")).strip()
        nombre = nombre_evento_desde_ev(ev)
        seccion = str(ev.get("sección", "")).strip()
        fecha_evento = pd.Timestamp(ev["fecha_evento"])
        tema = str(ev.get("tema", "")).strip()
        obs_cal = str(ev.get("observaciones", "")).strip()

        tipo_norm = tipo.lower()

        if "control" in tipo_norm:
            proto_nombre = "Control"
        elif "taller" in tipo_norm:
            proto_nombre = "Taller"
        elif "certamen" in tipo_norm or "prueba" in tipo_norm:
            proto_nombre = "Certamen"
        elif "portafolio" in tipo_norm:
            proto_nombre = "Portafolio"
        elif "trabajo práctico" in tipo_norm or tipo_norm == "tp":
            proto_nombre = "Trabajo práctico"
        elif "examen" in tipo_norm:
            proto_nombre = "Examen"
        elif "laboratorio" in tipo_norm or "informe laboratorio" in tipo_norm:
            proto_nombre = "Laboratorio"
        else:
            continue

        proto = protocolos.get(proto_nombre, {})
        if not proto:
            continue

        participantes = obtener_pool_participantes_seccion(config, seccion)
        pool_lab = obtener_pool_laboratorio_seccion(config, seccion)
        pec = str(pec_por_seccion.get(seccion, "")).strip()
        pcc = str(pcc_por_seccion.get(seccion, "")).strip()

        override = buscar_override(config, proto_nombre, seccion, fecha_evento.date())

        detalle_base_evento = []
        if obs_cal:
            detalle_base_evento.append(obs_cal)
        if tema:
            detalle_base_evento.append(f"Tema: {tema}")
        detalle_base_evento = " — ".join(detalle_base_evento)

        # ========================================================
        # CONTROL
        # pool cíclico ponderado por sección
        # ========================================================
        # if proto_nombre == "Control":
        #     idx = contador_control_por_seccion.get(seccion, 0)

        #     pool_control = obtener_pool_controles_seccion(config, seccion)
        #     pool_slots = pools_por_seccion.get(seccion, [])

        #     responsable_control = []
        #     slot_usado = ""

        #     if override and "responsables" in override:
        #         responsable_control = normalizar_lista_profes(override.get("responsables", []))
        #         slot_usado = "MANUAL"

        #     elif override and "slot" in override:
        #         slot_override = str(override.get("slot", "")).strip().upper()
        #         encontrado = False

        #         for item in pool_slots:
        #             if str(item.get("slot", "")).strip().upper() == slot_override:
        #                 responsable_control = [str(item.get("profesor", "")).strip()]
        #                 slot_usado = slot_override
        #                 encontrado = True
        #                 break

        #         if not encontrado and pool_control:
        #             responsable_control = [str(pool_control[idx % len(pool_control)]).strip()]
        #             slot_usado = f"AUTO-{(idx % len(pool_control)) + 1}"

        #     else:
        #         if pool_control:
        #             responsable_control = [str(pool_control[idx % len(pool_control)]).strip()]
        #             if pool_slots:
        #                 slot_usado = str(pool_slots[idx % len(pool_slots)].get("slot", "")).strip()
        #             else:
        #                 slot_usado = f"AUTO-{(idx % len(pool_control)) + 1}"

        #     contador_control_por_seccion[seccion] = idx + 1

        #     filas_chequeo.append({
        #         "sección": seccion,
        #         "fecha_evento": fecha_evento.date(),
        #         "evento": nombre,
        #         "observaciones": obs_cal,
        #         "slot_pool": slot_usado,
        #         "responsable_control": normalizar_profes_str(responsable_control),
        #     })

        #     for paso_key, paso in proto.items():
        #         offset = int(paso.get("offset_dias", 0))
        #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

        #         detalle = str(paso.get("detalle", "")).strip()
        #         if detalle_base_evento:
        #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

        #         filas.append({
        #             "fecha_limite": deadline,
        #             "fecha_evento": fecha_evento.date(),
        #             "evento": nombre,
        #             "tipo_evento": proto_nombre,
        #             "paso": paso_key,
        #             "sección": seccion,
        #             "responsables": normalizar_profes_str(responsable_control),
        #             "detalle": detalle,
        #             "estado": "Pendiente",
        #         })
        #     continue
        
        if proto_nombre == "Control":
            pool_control = obtener_pool_controles_seccion(config, seccion)
            pool_slots = pools_por_seccion.get(seccion, [])

            responsable_control = []
            slot_usado = ""

            if override and "responsables" in override:
                responsable_control = normalizar_lista_profes(override.get("responsables", []))
                slot_usado = "MANUAL"

            elif override and "slot" in override:
                slot_override = str(override.get("slot", "")).strip().upper()
                encontrado = False

                for item in pool_slots:
                    if str(item.get("slot", "")).strip().upper() == slot_override:
                        responsable_control = [str(item.get("profesor", "")).strip()]
                        slot_usado = slot_override
                        encontrado = True
                        break

                if not encontrado:
                    elegido = elegir_balanceado(pool_control, carga_actual, horas_map, cantidad=1)
                    if elegido:
                        responsable_control = elegido
                        slot_usado = "BALANCEADO"

            else:
                elegido = elegir_balanceado(pool_control, carga_actual, horas_map, cantidad=1)
                if elegido:
                    responsable_control = elegido
                    slot_usado = "BALANCEADO"

            filas_chequeo.append({
                "sección": seccion,
                "fecha_evento": fecha_evento.date(),
                "evento": nombre,
                "observaciones": obs_cal,
                "slot_pool": slot_usado,
                "responsable_control": normalizar_profes_str(responsable_control),
            })

            for paso_key, paso in proto.items():
                offset = int(paso.get("offset_dias", 0))
                deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

                detalle = str(paso.get("detalle", "")).strip()
                if detalle_base_evento:
                    detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

                filas.append({
                    "fecha_limite": deadline,
                    "fecha_evento": fecha_evento.date(),
                    "evento": nombre,
                    "tipo_evento": proto_nombre,
                    "paso": paso_key,
                    "sección": seccion,
                    "responsables": normalizar_profes_str(responsable_control),
                    "detalle": detalle,
                    "estado": "Pendiente",
                })

                # contar esta carga como repartible de seminario
                if paso_key in ["construir_control", "escanear", "corregir_y_notas"]:
                    sumar_carga(carga_actual, responsable_control, peso=1.0)

            continue


        if proto_nombre == "Portafolio":
            for paso_key, paso in proto.items():
                offset = int(paso.get("offset_dias", 0))
                deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

                detalle = str(paso.get("detalle", "")).strip()
                if detalle_base_evento:
                    detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

                filas.append({
                    "fecha_limite": deadline,
                    "fecha_evento": fecha_evento.date(),
                    "evento": nombre,
                    "tipo_evento": proto_nombre,
                    "paso": paso_key,
                    "sección": seccion,
                    "responsables": normalizar_profes_str(participantes),
                    "detalle": detalle,
                    "estado": "Pendiente",
                })
            continue


        # ========================================================
        # TALLER
        # pool global ponderado, pero sin repetir persona dentro del mismo taller
        # ========================================================
        # if proto_nombre == "Taller":
        #     pool_global = obtener_pool_global_participantes(config)

        #     if len(pool_global) == 0:
        #         continue

        #     elegidos = elegir_varios_ciclico_sin_repetir(pool_global, contador_taller_global, 4)

        #     if len(elegidos) < 4:
        #         faltan = 4 - len(elegidos)
        #         extra = elegir_varios_ciclico_sin_repetir(pool_global, contador_taller_global + 4, 4 + faltan)
        #         for p in extra:
        #             if p not in elegidos:
        #                 elegidos.append(p)
        #             if len(elegidos) == 4:
        #                 break

        #     if len(elegidos) < 4:
        #         continue

        #     contador_taller_global += 4

        #     p1, p2, p3, p4 = elegidos[:4]

        #     for paso_key, paso in proto.items():
        #         offset = int(paso.get("offset_dias", 0))
        #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
        #         detalle = str(paso.get("detalle", "")).strip()
        #         if detalle_base_evento:
        #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

        #         if paso_key == "construir_taller":
        #             filas.append({
        #                 "fecha_limite": deadline,
        #                 "fecha_evento": fecha_evento.date(),
        #                 "evento": nombre,
        #                 "tipo_evento": proto_nombre,
        #                 "paso": "construir_taller_AB",
        #                 "sección": seccion,
        #                 "responsables": normalizar_profes_str([p1, p2]),
        #                 "detalle": f"{detalle} — Versiones A y B.",
        #                 "estado": "Pendiente",
        #             })
        #             filas.append({
        #                 "fecha_limite": deadline,
        #                 "fecha_evento": fecha_evento.date(),
        #                 "evento": nombre,
        #                 "tipo_evento": proto_nombre,
        #                 "paso": "construir_taller_CD",
        #                 "sección": seccion,
        #                 "responsables": normalizar_profes_str([p3, p4]),
        #                 "detalle": f"{detalle} — Versiones C y D.",
        #                 "estado": "Pendiente",
        #             })

        #         elif paso_key == "corregir_taller":
        #             for prof, version in [(p1, "A"), (p2, "B"), (p3, "C"), (p4, "D")]:
        #                 filas.append({
        #                     "fecha_limite": deadline,
        #                     "fecha_evento": fecha_evento.date(),
        #                     "evento": nombre,
        #                     "tipo_evento": proto_nombre,
        #                     "paso": f"corregir_taller_{version}",
        #                     "sección": seccion,
        #                     "responsables": normalizar_profes_str([prof]),
        #                     "detalle": f"{detalle} — Corregir versión {version}.",
        #                     "estado": "Pendiente",
        #                 })

        #         else:
        #             filas.append({
        #                 "fecha_limite": deadline,
        #                 "fecha_evento": fecha_evento.date(),
        #                 "evento": nombre,
        #                 "tipo_evento": proto_nombre,
        #                 "paso": paso_key,
        #                 "sección": seccion,
        #                 "responsables": normalizar_profes_str(elegidos),
        #                 "detalle": detalle,
        #                 "estado": "Pendiente",
        #             })
        #     continue


        # if proto_nombre == "Taller":
        #     pool_global = obtener_pool_global_participantes(config)

        #     if len(pool_global) == 0:
        #         continue

        #     elegidos, nuevo_cursor = elegir_varios_ciclico_sin_repetir(
        #         pool_global,
        #         contador_taller_global,
        #         4
        #     )

        #     if len(elegidos) < 4:
        #         elegidos_extra, cursor_extra = elegir_varios_ciclico_sin_repetir(
        #             pool_global,
        #             nuevo_cursor,
        #             4
        #         )
        #         for p in elegidos_extra:
        #             if p not in elegidos:
        #                 elegidos.append(p)
        #             if len(elegidos) == 4:
        #                 break
        #         nuevo_cursor = cursor_extra

        #     if len(elegidos) < 4:
        #         continue

        #     contador_taller_global = nuevo_cursor

        #     p1, p2, p3, p4 = elegidos[:4]
        
        
        
        
        
        
        
        # if proto_nombre == "Taller":
        #     pool_global = obtener_pool_global_participantes(config)

        #     if len(pool_global) == 0:
        #         continue

        #     elegidos, nuevo_cursor = elegir_varios_ciclico_sin_repetir(
        #         pool_global,
        #         contador_taller_global,
        #         4
        #     )

        #     if len(elegidos) < 4:
        #         elegidos_extra, cursor_extra = elegir_varios_ciclico_sin_repetir(
        #             pool_global,
        #             nuevo_cursor,
        #             4
        #         )
        #         for p in elegidos_extra:
        #             if p not in elegidos:
        #                 elegidos.append(p)
        #             if len(elegidos) == 4:
        #                 break
        #         nuevo_cursor = cursor_extra

        #     if len(elegidos) < 4:
        #         continue

        #     contador_taller_global = nuevo_cursor

        #     p1, p2, p3, p4 = elegidos[:4]

        #     for paso_key, paso in proto.items():
        #         offset = int(paso.get("offset_dias", 0))
        #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

        #         detalle = str(paso.get("detalle", "")).strip()
        #         if detalle_base_evento:
        #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

        #         if paso_key == "construir_taller":
        #             filas.append({
        #                 "fecha_limite": deadline,
        #                 "fecha_evento": fecha_evento.date(),
        #                 "evento": nombre,
        #                 "tipo_evento": proto_nombre,
        #                 "paso": "construir_taller_AB",
        #                 "sección": seccion,
        #                 "responsables": normalizar_profes_str([p1, p2]),
        #                 "detalle": f"{detalle} — Versiones A y B.",
        #                 "estado": "Pendiente",
        #             })

        #             filas.append({
        #                 "fecha_limite": deadline,
        #                 "fecha_evento": fecha_evento.date(),
        #                 "evento": nombre,
        #                 "tipo_evento": proto_nombre,
        #                 "paso": "construir_taller_CD",
        #                 "sección": seccion,
        #                 "responsables": normalizar_profes_str([p3, p4]),
        #                 "detalle": f"{detalle} — Versiones C y D.",
        #                 "estado": "Pendiente",
        #             })

        #         elif paso_key == "corregir_taller":
        #             for prof, version in [(p1, "A"), (p2, "B"), (p3, "C"), (p4, "D")]:
        #                 filas.append({
        #                     "fecha_limite": deadline,
        #                     "fecha_evento": fecha_evento.date(),
        #                     "evento": nombre,
        #                     "tipo_evento": proto_nombre,
        #                     "paso": f"corregir_taller_{version}",
        #                     "sección": seccion,
        #                     "responsables": normalizar_profes_str([prof]),
        #                     "detalle": f"{detalle} — Corregir versión {version}.",
        #                     "estado": "Pendiente",
        #                 })

        #         else:
        #             filas.append({
        #                 "fecha_limite": deadline,
        #                 "fecha_evento": fecha_evento.date(),
        #                 "evento": nombre,
        #                 "tipo_evento": proto_nombre,
        #                 "paso": paso_key,
        #                 "sección": seccion,
        #                 "responsables": normalizar_profes_str(elegidos),
        #                 "detalle": detalle,
        #                 "estado": "Pendiente",
        #             })

        #     continue
        
        
        
        # if proto_nombre == "Taller":
        #     pool_global = obtener_pool_global_participantes(config)

        #     if len(pool_global) == 0:
        #         continue

        #     # una persona para construir
        #     elegido_construccion, cursor_1 = elegir_varios_ciclico_sin_repetir(
        #         pool_global,
        #         contador_taller_global,
        #         1
        #     )

        #     if len(elegido_construccion) < 1:
        #         continue

        #     # una persona para corregir (idealmente distinta)
        #     elegido_correccion, cursor_2 = elegir_varios_ciclico_sin_repetir(
        #         pool_global,
        #         cursor_1,
        #         1
        #     )

        #     if len(elegido_correccion) < 1:
        #         elegido_correccion = elegido_construccion[:]
        #         cursor_2 = cursor_1

        #     profe_construccion = elegido_construccion[0]
        #     profe_correccion = elegido_correccion[0]

        #     # overrides manuales
        #     override_construccion = buscar_override(
        #         config,
        #         proto_nombre,
        #         seccion,
        #         fecha_evento.date(),
        #         paso="construir_taller"
        #     )
        #     if override_construccion and "responsables" in override_construccion:
        #         manual = normalizar_lista_profes(override_construccion.get("responsables", []))
        #         if manual:
        #             profe_construccion = manual[0]

        #     override_correccion = buscar_override(
        #         config,
        #         proto_nombre,
        #         seccion,
        #         fecha_evento.date(),
        #         paso="corregir_taller"
        #     )
        #     if override_correccion and "responsables" in override_correccion:
        #         manual = normalizar_lista_profes(override_correccion.get("responsables", []))
        #         if manual:
        #             profe_correccion = manual[0]

        #     contador_taller_global = cursor_2

        #     for paso_key, paso in proto.items():
        #         offset = int(paso.get("offset_dias", 0))
        #         deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

        #         detalle = str(paso.get("detalle", "")).strip()
        #         if detalle_base_evento:
        #             detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

        #         if paso_key == "construir_taller":
        #             responsables = [profe_construccion]
        #             detalle_final = detalle

        #         elif paso_key == "corregir_taller":
        #             responsables = [profe_correccion]
        #             detalle_final = detalle

        #         else:
        #             responsables = [profe_construccion]
        #             detalle_final = detalle

        #         filas.append({
        #             "fecha_limite": deadline,
        #             "fecha_evento": fecha_evento.date(),
        #             "evento": nombre,
        #             "tipo_evento": proto_nombre,
        #             "paso": paso_key,
        #             "sección": seccion,
        #             "responsables": normalizar_profes_str(responsables),
        #             "detalle": detalle_final,
        #             "estado": "Pendiente",
        #         })

        #     continue



        if proto_nombre == "Taller":
            pool_global = obtener_pool_global_participantes(config)

            if len(pool_global) == 0:
                continue

            elegido_construccion = elegir_balanceado(
                pool_global,
                carga_actual,
                horas_map,
                cantidad=1
            )

            if len(elegido_construccion) < 1:
                continue

            elegido_correccion = elegir_balanceado(
                pool_global,
                carga_actual,
                horas_map,
                cantidad=1,
                excluir=set(elegido_construccion)
            )

            if len(elegido_correccion) < 1:
                elegido_correccion = elegido_construccion[:]

            profe_construccion = elegido_construccion[0]
            profe_correccion = elegido_correccion[0]

            override_construccion = buscar_override(
                config,
                proto_nombre,
                seccion,
                fecha_evento.date(),
                paso="construir_taller"
            )
            if override_construccion and "responsables" in override_construccion:
                manual = normalizar_lista_profes(override_construccion.get("responsables", []))
                if manual:
                    profe_construccion = manual[0]

            override_correccion = buscar_override(
                config,
                proto_nombre,
                seccion,
                fecha_evento.date(),
                paso="corregir_taller"
            )
            if override_correccion and "responsables" in override_correccion:
                manual = normalizar_lista_profes(override_correccion.get("responsables", []))
                if manual:
                    profe_correccion = manual[0]

            for paso_key, paso in proto.items():
                offset = int(paso.get("offset_dias", 0))
                deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

                detalle = str(paso.get("detalle", "")).strip()
                if detalle_base_evento:
                    detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

                if paso_key == "construir_taller":
                    responsables = [profe_construccion]
                elif paso_key == "corregir_taller":
                    responsables = [profe_correccion]
                else:
                    responsables = [profe_construccion]

                filas.append({
                    "fecha_limite": deadline,
                    "fecha_evento": fecha_evento.date(),
                    "evento": nombre,
                    "tipo_evento": proto_nombre,
                    "paso": paso_key,
                    "sección": seccion,
                    "responsables": normalizar_profes_str(responsables),
                    "detalle": detalle,
                    "estado": "Pendiente",
                })

                if paso_key in ["construir_taller", "corregir_taller"]:
                    sumar_carga(carga_actual, responsables, peso=1.0)

            continue



        # ========================================================
        # CERTAMEN
        # pedir_preguntas: participantes
        # construir/pauta: PEC
        # corregir_y_notas: participantes
        # ========================================================
        if proto_nombre == "Certamen":
            for paso_key, paso in proto.items():
                offset = int(paso.get("offset_dias", 0))
                deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
                detalle = str(paso.get("detalle", "")).strip()
                if detalle_base_evento:
                    detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

                if paso_key == "pedir_preguntas":
                    responsables = participantes
                elif paso_key in ["construir_control", "pauta_prueba"]:
                    responsables = [pec] if pec else []
                elif paso_key == "corregir_y_notas":
                    responsables = participantes
                else:
                    responsables = participantes

                filas.append({
                    "fecha_limite": deadline,
                    "fecha_evento": fecha_evento.date(),
                    "evento": nombre,
                    "tipo_evento": proto_nombre,
                    "paso": paso_key,
                    "sección": seccion,
                    "responsables": normalizar_profes_str(responsables),
                    "detalle": detalle,
                    "estado": "Pendiente",
                })
            continue

        # ========================================================
        # EXAMEN
        # pedir_preguntas: participantes
        # construir/pauta: PEC
        # corregir_examen: participantes
        # ========================================================
        if proto_nombre == "Examen":
            for paso_key, paso in proto.items():
                offset = int(paso.get("offset_dias", 0))
                deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
                detalle = str(paso.get("detalle", "")).strip()
                if detalle_base_evento:
                    detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

                if paso_key == "pedir_preguntas":
                    responsables = participantes
                elif paso_key in ["construir_examen", "pauta_examen"]:
                    responsables = [pec] if pec else []
                elif paso_key == "corregir_examen":
                    responsables = participantes
                else:
                    responsables = participantes

                filas.append({
                    "fecha_limite": deadline,
                    "fecha_evento": fecha_evento.date(),
                    "evento": nombre,
                    "tipo_evento": proto_nombre,
                    "paso": paso_key,
                    "sección": seccion,
                    "responsables": normalizar_profes_str(responsables),
                    "detalle": detalle,
                    "estado": "Pendiente",
                })
            continue

        # ========================================================
        # TRABAJO PRÁCTICO
        # ========================================================
        if proto_nombre == "Trabajo práctico":
            for paso_key, paso in proto.items():
                offset = int(paso.get("offset_dias", 0))
                deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
                detalle = str(paso.get("detalle", "")).strip()
                if detalle_base_evento:
                    detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

                filas.append({
                    "fecha_limite": deadline,
                    "fecha_evento": fecha_evento.date(),
                    "evento": nombre,
                    "tipo_evento": proto_nombre,
                    "paso": paso_key,
                    "sección": seccion,
                    "responsables": normalizar_profes_str(participantes),
                    "detalle": detalle,
                    "estado": "Pendiente",
                })
            continue

        # ========================================================
        # LABORATORIO
        # ========================================================
        if proto_nombre == "Laboratorio":
            idx_lab = contador_lab_video_por_seccion.get(seccion, 0)
            video_lab = elegir_ciclico(pool_lab, idx_lab)
            contador_lab_video_por_seccion[seccion] = idx_lab + 1

            for paso_key, paso in proto.items():
                offset = int(paso.get("offset_dias", 0))
                deadline = (fecha_evento + pd.Timedelta(days=offset)).date()
                detalle = str(paso.get("detalle", "")).strip()
                if detalle_base_evento:
                    detalle = f"{detalle} — {detalle_base_evento}" if detalle else detalle_base_evento

                if paso_key == "preparar_material_previo":
                    responsables = [pec] if pec else []
                elif paso_key == "grabar_video_solucion":
                    responsables = video_lab
                elif paso_key == "corregir_informe_laboratorio":
                    responsables = pool_lab
                else:
                    responsables = pool_lab

                filas.append({
                    "fecha_limite": deadline,
                    "fecha_evento": fecha_evento.date(),
                    "evento": nombre,
                    "tipo_evento": proto_nombre,
                    "paso": paso_key,
                    "sección": seccion,
                    "responsables": normalizar_profes_str(responsables),
                    "detalle": detalle,
                    "estado": "Pendiente",
                })
            continue

    df_mis = pd.DataFrame(filas)

    if df_mis.empty:
        columnas = [
            "fecha_limite", "fecha_evento", "evento", "tipo_evento", "paso",
            "sección", "responsables", "detalle", "estado"
        ]
        return (
            pd.DataFrame(columns=columnas),
            pd.DataFrame(filas_chequeo),
            pd.DataFrame(filas_pools)
        )

    df_mis = df_mis.sort_values(
        ["fecha_limite", "fecha_evento", "sección", "tipo_evento", "paso"]
    ).reset_index(drop=True)

    df_chequeo = pd.DataFrame(filas_chequeo)
    df_pools = pd.DataFrame(filas_pools)

    return df_mis, df_chequeo, df_pools


# ============================================================
# MATRIZ
# ============================================================
def armar_matriz(df_mis, config):
    alias = config.get("misiones", {}).get("alias_seccion", {}) or {}

    if df_mis.empty:
        return pd.DataFrame()

    df = df_mis.copy()

    for c in ["evento", "tipo_evento", "paso", "detalle", "sección", "responsables"]:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)

    df["sección_col"] = df["sección"].apply(lambda s: alias.get(s, s))

    mat = df.pivot_table(
        index=["evento", "tipo_evento", "paso", "detalle"],
        columns="sección_col",
        values="responsables",
        aggfunc="first",
        fill_value=""
    ).reset_index()

    mat = mat.rename(columns={
        "evento": "Evaluación",
        "tipo_evento": "Tipo",
        "paso": "Misión",
        "detalle": "Detalle",
    })

    return mat


# ============================================================
# EXPORTAR
# ============================================================
def style_sheet(ws, header_color="1F4E78"):
    fill_header = PatternFill("solid", fgColor=header_color)
    font_header = Font(bold=True, color="FFFFFF")

    for cell in ws[1]:
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"

    for col in range(1, ws.max_column + 1):
        maxlen = 0
        for r in range(1, ws.max_row + 1):
            v = ws.cell(r, col).value
            if v is None:
                continue
            maxlen = max(maxlen, len(str(v)))
        ws.column_dimensions[get_column_letter(col)].width = min(max(12, maxlen + 2), 60)


def exportar_excel(df_mis, df_mat, df_chequeo, df_pools, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with pd.ExcelWriter(path, engine="openpyxl", datetime_format="DD/MM/YYYY") as writer:
        df_mis.to_excel(writer, index=False, sheet_name="Misiones")

        if not df_mat.empty:
            df_mat.to_excel(writer, index=False, sheet_name="Matriz")

        if not df_chequeo.empty:
            df_chequeo.to_excel(writer, index=False, sheet_name="Chequeo")

        if not df_pools.empty:
            df_pools.to_excel(writer, index=False, sheet_name="Pools")

        orden = [
            "pedir_preguntas",
            "construir_control",
            "pauta_prueba",
            "revisar_prueba",
            "escanear",
            "corregir_y_notas",
            "revisar_tp",
            # "construir_taller_AB",
            # "construir_taller_CD",
            # "corregir_taller_A",
            # "corregir_taller_B",
            # "corregir_taller_C",
            # "corregir_taller_D",
            "construir_taller",
            "corregir_taller",
            "construir_examen",
            "pauta_examen",
            "corregir_examen",
            "preparar_material_previo",
            "grabar_video_solucion",
            "corregir_informe_laboratorio",
            "revisar_portafolio",
        ]

        df_plan = df_mis.copy()
        df_plan["paso_rank"] = df_plan["paso"].apply(lambda x: orden.index(x) if x in orden else 999)
        df_plan = df_plan.sort_values(
            ["fecha_evento", "sección", "tipo_evento", "paso_rank", "fecha_limite"]
        ).drop(columns=["paso_rank"])
        df_plan.to_excel(writer, index=False, sheet_name="Plan")

        wb = writer.book

        style_sheet(wb["Misiones"], "5B2C6F")
        style_sheet(wb["Plan"], "2C3E50")

        if "Matriz" in wb.sheetnames:
            style_sheet(wb["Matriz"], "7F7F7F")

        if "Chequeo" in wb.sheetnames:
            style_sheet(wb["Chequeo"], "0F766E")

        if "Pools" in wb.sheetnames:
            style_sheet(wb["Pools"], "92400E")

        ws_mis = wb["Misiones"]
        headers = [c.value for c in ws_mis[1]]

        if "fecha_limite" in headers:
            idx = headers.index("fecha_limite") + 1
            fill_deadline = PatternFill("solid", fgColor="F4CCCC")
            for r in range(2, ws_mis.max_row + 1):
                ws_mis.cell(r, idx).fill = fill_deadline
                ws_mis.cell(r, idx).alignment = Alignment(horizontal="center")


# ============================================================
# MAIN
# ============================================================
def main():
    cursos = {
        "fokito": {
            "config_path": os.path.join("config", "calendario_fokito.yml"),
            "cal_path": os.path.join("data", "fokito", "calendario.xlsx"),
            "out_path": os.path.join("data", "fokito", "misiones.xlsx"),
        },
        "tecnologia_medica": {
            "config_path": os.path.join("config", "calendario_tecnologia_medica.yml"),
            "cal_path": os.path.join("data", "tecnologia_medica", "calendario.xlsx"),
            "out_path": os.path.join("data", "tecnologia_medica", "misiones.xlsx"),
        },
        "medicina": {
            "config_path": os.path.join("config", "calendario_medicina.yml"),
            "cal_path": os.path.join("data", "medicina", "calendario.xlsx"),
            "out_path": os.path.join("data", "medicina", "misiones.xlsx"),
        },
        "enobnu": {
            "config_path": os.path.join("config", "calendario_enobnu.yml"),
            "cal_path": os.path.join("data", "enobnu", "calendario.xlsx"),
            "out_path": os.path.join("data", "enobnu", "misiones.xlsx"),
        },
    }

    for curso, info in cursos.items():
        config_path = info["config_path"]
        cal_path = info["cal_path"]
        out_path = info["out_path"]

        if not os.path.exists(config_path):
            print(f"⚠️  Saltando {curso}: no existe {config_path}")
            continue

        if not os.path.exists(cal_path):
            print(f"⚠️  Saltando {curso}: no existe {cal_path}. Genera primero el calendario.")
            continue

        config = cargar_yaml(config_path)
        df_cal = pd.read_excel(cal_path, sheet_name="Calendario")

        estados_previos = cargar_estados_previos(out_path)

        df_mis, df_chequeo, df_pools = construir_misiones(config, df_cal)
        df_mis = aplicar_estados_previos(df_mis, estados_previos)
        df_mat = armar_matriz(df_mis, config)


        graficar_equilibrio_curso(
            nombre_curso=curso,
            df_cal=df_cal,
            df_mis=df_mis,
            carpeta_salida=os.path.dirname(out_path)
        )


        exportar_excel(df_mis, df_mat, df_chequeo, df_pools, out_path)

        print(f"OK: [{curso}] generado {out_path} con {len(df_mis)} tareas.")

        if not df_chequeo.empty:
            print("  Controles asignados:")
            print(
                df_chequeo[
                    ["sección", "fecha_evento", "slot_pool", "responsable_control"]
                ].to_string(index=False)
            )


if __name__ == "__main__":
    main()