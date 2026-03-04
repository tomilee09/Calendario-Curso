# generador_misiones_excel.py
import os, random, yaml
import pandas as pd
from datetime import timedelta

from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

def cargar_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def split_profes(s):
    if not s:
        return []
    return [x.strip() for x in str(s).split(",") if x.strip()]

def elegir_equilibrado(profes, cargas, n, rng):
    # minimiza cargas/horas_contrato, desempate aleatorio
    elegidos = []
    n = max(1, min(n, len(profes)))
    for _ in range(n):
        candidatos = [p for p in profes if p["codigo"] not in elegidos]
        ratios = []
        for p in candidatos:
            cod = p["codigo"]
            horas = float(p.get("horas_contrato", 1) or 1)
            ratios.append((cod, cargas.get(cod, 0) / max(horas, 1e-9)))
        min_ratio = min(r[1] for r in ratios)
        mejores = [cod for cod, rr in ratios if rr == min_ratio]
        cod = rng.choice(mejores)
        elegidos.append(cod)
        cargas[cod] = cargas.get(cod, 0) + 1
    return elegidos

def detectar_evaluaciones(df_cal):
    # devuelve una tabla de "hitos" evaluativos
    df = df_cal.copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["evaluación"] = df.get("evaluación", "").fillna("").astype(str)
    df["actividad"] = df.get("actividad", "").fillna("").astype(str)

    evs = []

    # 1) evaluaciones (prueba / tp / etc.)
    sub = df[df["evaluación"].str.strip() != ""].copy()
    for _, r in sub.iterrows():
        evs.append({
            "tipo_evento": r["evaluación"].strip(),      # "Prueba", "Trabajo práctico", ...
            "nombre_evento": r["evaluación"].strip(),    # puedes refinar a "Prueba 1" etc si lo codificas en observaciones
            "sección": r.get("sección", ""),
            "actividad": r.get("actividad", ""),
            "fecha_evento": r["fecha"].date(),
            "tema": r.get("tema", ""),
            "observaciones": r.get("observaciones", ""),
        })

    # 2) exámenes
    sub2 = df[df["actividad"].str.strip().str.lower() == "examen"].copy()
    for _, r in sub2.iterrows():
        evs.append({
            "tipo_evento": "Examen",
            "nombre_evento": "Examen",
            "sección": r.get("sección", ""),
            "actividad": r.get("actividad", ""),
            "fecha_evento": r["fecha"].date(),
            "tema": r.get("tema", ""),
            "observaciones": r.get("observaciones", ""),
        })

    return pd.DataFrame(evs)

def construir_misiones(config, df_cal):
    rng = random.Random(int(config.get("aleatoriedad", {}).get("semilla", 42)))

    profs = config.get("profesores", []) or []
    cargas = {p["codigo"]: 0 for p in profs}

    protocolos = config.get("protocolos", {}) or {}
    reglas = config.get("reglas_plazos", {}) or {}

    df_evs = detectar_evaluaciones(df_cal)
    if df_evs.empty:
        # fallback: inventa 2 pruebas y 1 TP coherente si no hay fechas
        f0 = pd.Timestamp(config["periodo"]["fecha_inicio"])
        df_evs = pd.DataFrame([
            {"tipo_evento":"Prueba", "nombre_evento":"Prueba 1", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=6)).date(), "tema":"", "observaciones":"(inventado)"},
            {"tipo_evento":"TP", "nombre_evento":"TP: Linealización", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=10)).date(), "tema":"", "observaciones":"(inventado)"},
            {"tipo_evento":"Prueba", "nombre_evento":"Prueba 2", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=14)).date(), "tema":"", "observaciones":"(inventado)"},
            {"tipo_evento":"Examen", "nombre_evento":"Examen", "sección":"Equipo docente", "fecha_evento":(f0+pd.Timedelta(weeks=18)).date(), "tema":"", "observaciones":"(inventado)"},
        ])

    filas = []
    for _, ev in df_evs.iterrows():
        tipo = str(ev["tipo_evento"]).strip()
        nombre = str(ev.get("nombre_evento", tipo)).strip()
        seccion = str(ev.get("sección", "Equipo docente")).strip()
        fecha_evento = pd.Timestamp(ev["fecha_evento"])

        # Mapea tipo_evento -> protocolo
        if "prueba" in tipo.lower():
            proto = protocolos.get("Prueba", {})
        elif "trabajo" in tipo.lower() or tipo.lower() == "tp":
            proto = protocolos.get("TP", {})
        elif tipo.lower() == "examen":
            proto = protocolos.get("Examen", {})
        else:
            # por defecto usa Guia/Seminario si quieres, si no, salta
            proto = protocolos.get("Guia", {})

        for paso_key, paso in proto.items():
            offset = int(paso.get("offset_dias", 0))
            deadline = (fecha_evento + pd.Timedelta(days=offset)).date()

            resp = paso.get("responsables", "Asignar")
            detalle = paso.get("detalle", "")

            # asignaciones automáticas
            if str(resp).strip().lower() == "todos":
                responsables = "Todos"
            else:
                # 1 o 2 responsables típicamente
                n_resp = 2 if ("pauta" in paso_key or "constru" in paso_key) else 1
                elegidos = elegir_equilibrado(profs, cargas, n_resp, rng)
                responsables = ", ".join(elegidos)

            filas.append({
                "fecha_limite": deadline,
                "fecha_evento": fecha_evento.date(),
                "evento": nombre,
                "paso": paso_key,
                "sección": seccion,
                "responsables": responsables,
                "detalle": detalle,
                "estado": "Pendiente",
            })

    df_mis = pd.DataFrame(filas).sort_values(["fecha_limite","evento","sección"]).reset_index(drop=True)
    return df_mis

def armar_matriz(df_mis, config):
    # Vista tipo imagen: filas = evento, columnas = secciones, valor = responsables de "corregir_y_notas"/"corregir_examen"/etc.
    alias = config.get("alias_seccion", {}) or {}

    df = df_mis.copy()
    df["evento"] = df["evento"].astype(str)

    # define qué pasos van a la matriz (corrección)
    pasos_correccion = set(["corregir_y_notas", "corregir_examen", "revisar_tp"])
    df = df[df["paso"].isin(list(pasos_correccion))].copy()
    if df.empty:
        return pd.DataFrame()

    df["sección_col"] = df["sección"].apply(lambda s: alias.get(s, s))
    mat = df.pivot_table(index="evento", columns="sección_col", values="responsables", aggfunc="first", fill_value="")

    # Agrega segunda fila “Detalle / Corrección” estilo tu ejemplo si quieres hacerlo como header doble,
    # en Excel lo hacemos como 2 filas arriba; acá lo dejamos plano y lo formateamos al exportar.
    mat = mat.reset_index().rename(columns={"evento":"Evaluaciones"})
    return mat

def exportar_excel(df_mis, df_mat, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with pd.ExcelWriter(path, engine="openpyxl", datetime_format="DD/MM/YYYY") as writer:
        df_mis.to_excel(writer, index=False, sheet_name="Misiones")
        if df_mat is not None and not df_mat.empty:
            df_mat.to_excel(writer, index=False, sheet_name="Matriz")

        # Un “Plan” para lectura humana: filtramos pasos clave y orden lógico
        orden = ["pedir_preguntas","construir_control","pauta_prueba","revisar_prueba","escaneo","corregir_y_notas",
                 "construir_examen","pauta_examen","corregir_examen","revisar_tp","revision_guia","pauta_seminario","presentacion_grupal"]
        df_plan = df_mis.copy()
        df_plan["paso_rank"] = df_plan["paso"].apply(lambda x: orden.index(x) if x in orden else 999)
        df_plan = df_plan.sort_values(["evento","paso_rank","sección","fecha_limite"]).drop(columns=["paso_rank"])
        df_plan.to_excel(writer, index=False, sheet_name="Plan")

        # ------- ESTILO EXCEL (colores) -------
        wb = writer.book

        def style_sheet(ws, header_color="1F4E78"):
            # header
            fill_header = PatternFill("solid", fgColor=header_color)
            font_header = Font(bold=True, color="FFFFFF")
            for cell in ws[1]:
                cell.fill = fill_header
                cell.font = font_header
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"

            # widths
            for col in range(1, ws.max_column + 1):
                maxlen = 0
                for r in range(1, ws.max_row + 1):
                    v = ws.cell(r, col).value
                    if v is None:
                        continue
                    maxlen = max(maxlen, len(str(v)))
                ws.column_dimensions[get_column_letter(col)].width = min(max(12, maxlen + 2), 55)

        ws_mis = wb["Misiones"]
        style_sheet(ws_mis, header_color="5B2C6F")

        # Colorear “fecha_limite” en rojo suave y poner emoji en otra columna si quieres:
        headers = [c.value for c in ws_mis[1]]
        if "fecha_limite" in headers:
            c_fecha = headers.index("fecha_limite") + 1
            fill_deadline = PatternFill("solid", fgColor="F4CCCC")
            for r in range(2, ws_mis.max_row + 1):
                ws_mis.cell(r, c_fecha).fill = fill_deadline
                ws_mis.cell(r, c_fecha).alignment = Alignment(horizontal="center")

        ws_plan = wb["Plan"]
        style_sheet(ws_plan, header_color="2C3E50")

        if "Matriz" in wb.sheetnames:
            ws_mat = wb["Matriz"]
            style_sheet(ws_mat, header_color="7F7F7F")

# def main():
#     config = cargar_yaml("misiones_config.yml")
#     cal_path = config["fuentes"]["calendario_excel_path"]

#     df_cal = pd.read_excel(cal_path, sheet_name="Calendario")
#     df_mis = construir_misiones(config, df_cal)
#     df_mat = armar_matriz(df_mis, config)

#     out = config["salida"]["excel_path"]
#     exportar_excel(df_mis, df_mat, out)
#     print(f"OK: generado {out} con {len(df_mis)} tareas.")

# if __name__ == "__main__":
#     main()

# ============================================================
# MAIN MULTI-CURSO
# - Lee 3 YAML distintos desde config/
# - Genera los 3 misiones.xlsx
# - Usa el calendario.xlsx correspondiente de cada curso
# ============================================================
def main():
    cursos = {
        "fokito": {
            "config_path": os.path.join("config", "misiones_fokito.yml"),
            "cal_path": os.path.join("data", "fokito", "calendario.xlsx"),
            "out_path": os.path.join("data", "fokito", "misiones.xlsx"),
        },
        "tecnologia_medica": {
            "config_path": os.path.join("config", "misiones_tecnologia_medica.yml"),
            "cal_path": os.path.join("data", "tecnologia_medica", "calendario.xlsx"),
            "out_path": os.path.join("data", "tecnologia_medica", "misiones.xlsx"),
        },
        "medicina": {
            "config_path": os.path.join("config", "misiones_medicina.yml"),
            "cal_path": os.path.join("data", "medicina", "calendario.xlsx"),
            "out_path": os.path.join("data", "medicina", "misiones.xlsx"),
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

        # Sobrescribimos rutas para asegurar consistencia
        if "fuentes" not in config:
            config["fuentes"] = {}
        if "salida" not in config:
            config["salida"] = {}

        config["fuentes"]["calendario_excel_path"] = cal_path
        config["salida"]["excel_path"] = out_path

        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        df_cal = pd.read_excel(cal_path, sheet_name="Calendario")
        df_mis = construir_misiones(config, df_cal)
        df_mat = armar_matriz(df_mis, config)

        exportar_excel(df_mis, df_mat, out_path)

        print(f"OK: [{curso}] generado {out_path} con {len(df_mis)} tareas.")

if __name__ == "__main__":
    main()