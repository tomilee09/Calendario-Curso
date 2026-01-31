# generar_excel.py
import os
import io
import yaml
import pandas as pd
from datetime import datetime, time
import holidays

from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.table import Table, TableStyleInfo


ORDEN_DIAS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DIAS_ES = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}
DIAS_ES_POR_WEEKDAY = {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",4:"Viernes",5:"Sábado",6:"Domingo"}


def cargar_config(path="calendario_config.yml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def hhmm_a_time(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def rango_horario_str(inicio: str, fin: str) -> str:
    return f"{inicio}–{fin}"


def fecha_de_dia_en_semana(lunes_semana: pd.Timestamp, dia_semana: str) -> pd.Timestamp:
    idx = ORDEN_DIAS.index(dia_semana)
    return pd.Timestamp(lunes_semana.date()) + pd.Timedelta(days=idx)


def construir_df(config: dict) -> pd.DataFrame:
    inicio = pd.Timestamp(config["periodo"]["fecha_inicio"])
    nsem = int(config["periodo"]["numero_semanas"])

    filas = []

    # ---- clases regulares ----
    for seccion, cfg in config["secciones"].items():
        for semana in range(1, nsem + 1):
            lunes = inicio + pd.Timedelta(days=7*(semana-1))

            # Teórica + Seminario
            for clave, nombre in [("teorica", "Clase teórica"), ("seminario", "Seminario")]:
                dia_semana = cfg[clave]["dia_semana"]
                fecha = fecha_de_dia_en_semana(lunes, dia_semana)

                filas.append({
                    "semana": semana,
                    "fecha": fecha.date(),
                    "día": DIAS_ES[dia_semana],
                    "horario": rango_horario_str(cfg[clave]["inicio"], cfg[clave]["fin"]),
                    "sección": seccion,
                    "actividad": nombre,
                    "tema": "",
                    "evaluación": "",
                    "profesores": "",
                    "misiones": "",
                    "observaciones": ""
                })

            # Lab semanas pares
            if config.get("laboratorios", {}).get("frecuencia") == "cada_2_semanas":
                if config.get("laboratorios", {}).get("semanas") == "pares" and (semana % 2 == 0):
                    dia_semana = cfg["lab"]["dia_semana"]
                    fecha = fecha_de_dia_en_semana(lunes, dia_semana)
                    filas.append({
                        "semana": semana,
                        "fecha": fecha.date(),
                        "día": DIAS_ES[dia_semana],
                        "horario": rango_horario_str(cfg["lab"]["inicio"], cfg["lab"]["fin"]),
                        "sección": seccion,
                        "actividad": "Laboratorio",
                        "tema": "",
                        "evaluación": "",
                        "profesores": "",
                        "misiones": "",
                        "observaciones": "Cada 2 semanas"
                    })

    df = pd.DataFrame(filas)

    # ---- tema por semana (si existe) ----
    temas = config.get("temas_por_semana", {}) or {}
    if temas:
        # temas viene como dict YAML -> keys pueden ser int o str
        temas_norm = {int(k): str(v) for k, v in temas.items()}
        df.loc[df["semana"].isin(list(temas_norm.keys())), "tema"] = df["semana"].map(temas_norm).fillna("")

    # ---- profesores base por sección+actividad ----
    for r in config.get("profesores_base", []) or []:
        secc = r.get("seccion")
        act = r.get("actividad")
        prof = r.get("profesores", "")
        mask = (df["sección"] == secc) & (df["actividad"] == act)
        df.loc[mask, "profesores"] = prof

    # ---- evaluaciones ----
    for ev in config.get("evaluaciones", []) or []:
        if ev.get("modo") == "por_filtro":
            mask = (
                (df["sección"] == ev.get("seccion")) &
                (df["semana"] == int(ev.get("semana"))) &
                (df["actividad"] == ev.get("actividad"))
            )
            df.loc[mask, "evaluación"] = ev.get("tipo", "")
            obs = str(ev.get("observaciones", "")).strip()
            if obs:
                df.loc[mask, "observaciones"] = df.loc[mask, "observaciones"].astype(str).str.strip()
                df.loc[mask, "observaciones"] = df.loc[mask, "observaciones"].apply(
                    lambda x: (x + " | " if x else "") + obs
                )

    # ---- misiones (all-day, horario vacío) ----
    ref = pd.Timestamp(config["periodo"]["fecha_inicio"])
    nuevos_m = []
    for m in config.get("misiones", []) or []:
        fecha_ts = pd.Timestamp(m["fecha"])
        semana_ev = int((fecha_ts - ref).days // 7) + 1
        nuevos_m.append({
            "semana": semana_ev,
            "fecha": fecha_ts.date(),
            "día": DIAS_ES_POR_WEEKDAY[fecha_ts.weekday()],
            "horario": "",  # all-day
            "sección": m.get("seccion", "Equipo docente"),
            "actividad": "Misión",
            "tema": "",
            "evaluación": "",
            "profesores": m.get("profesores", ""),
            "misiones": m.get("mision", ""),
            "observaciones": m.get("observaciones", "")
        })
    if nuevos_m:
        df = pd.concat([df, pd.DataFrame(nuevos_m)], ignore_index=True)

    # ---- feriados Chile automáticos + manuales ----
    fer = config.get("feriados", {}) or {}
    feriados_map = {}

    if fer.get("usar_automaticos_chile", False):
        fmin = pd.Timestamp(df["fecha"].min()).date()
        fmax = pd.Timestamp(df["fecha"].max()).date()
        years = list(range(fmin.year, fmax.year + 1))
        cl = holidays.country_holidays("CL", years=years)
        for d, nombre in cl.items():
            if fmin <= d <= fmax:
                feriados_map[pd.Timestamp(d).date()] = str(nombre)

    for fm in fer.get("manuales", []) or []:
        feriados_map[pd.Timestamp(fm["fecha"]).date()] = str(fm.get("nombre", "Feriado"))

    if feriados_map:
        mask = df["fecha"].isin(list(feriados_map.keys()))
        # Solo marcar como feriado eventos que NO sean misión (para no borrar misiones)
        mask = mask & (df["actividad"] != "Misión")
        df.loc[mask, "actividad"] = "Sin clases (Feriado)"
        df.loc[mask, "observaciones"] = df.loc[mask, "fecha"].map(feriados_map)

    # ---- pausas académicas (rangos): reemplaza clases regulares en esos días ----
    for p in config.get("pausas_academicas", []) or []:
        ini = pd.Timestamp(p["inicio"]).date()
        fin = pd.Timestamp(p["fin"]).date()
        etiqueta = str(p.get("etiqueta", "Pausa académica")).strip()

        mask = (df["fecha"] >= ini) & (df["fecha"] <= fin) & (df["actividad"] != "Misión")
        df.loc[mask, "actividad"] = "Sin clases (Pausa académica)"
        df.loc[mask, "observaciones"] = etiqueta

    # ---- semanas de trabajo autónomo por número (si quieres) ----
    semanas_auto = set(config.get("semanas_trabajo_autonomo", []) or [])
    if semanas_auto:
        mask = df["semana"].isin(list(semanas_auto)) & (df["actividad"] != "Misión")
        df.loc[mask, "actividad"] = "Trabajo autónomo"
        df.loc[mask, "observaciones"] = "No hay clases (trabajo autónomo)."

    # ---- exámenes: eliminar clases regulares en esas semanas e insertar exámenes ----
    ex = config.get("examenes", {}) or {}
    semanas_ex = set(ex.get("semanas_examenes", []) or [])
    if semanas_ex:
        df = df[~(df["semana"].isin(list(semanas_ex)) & (df["actividad"] != "Misión"))].copy()

        nuevos_ex = []
        for e in ex.get("eventos", []) or []:
            fecha_ts = pd.Timestamp(e["fecha"])
            semana_ev = int((fecha_ts - ref).days // 7) + 1
            nuevos_ex.append({
                "semana": semana_ev,
                "fecha": fecha_ts.date(),
                "día": DIAS_ES_POR_WEEKDAY[fecha_ts.weekday()],
                "horario": rango_horario_str(e["inicio"], e["fin"]),
                "sección": e["seccion"],
                "actividad": e.get("actividad", "Examen"),
                "tema": e.get("tema", ""),
                "evaluación": e.get("evaluacion", ""),
                "profesores": e.get("profesores", ""),
                "misiones": "",
                "observaciones": e.get("observaciones", "")
            })
        if nuevos_ex:
            df = pd.concat([df, pd.DataFrame(nuevos_ex)], ignore_index=True)

    # ---- bloques protegidos: marcar conflicto por solapamiento horario ----
    bloques = config.get("bloques", {}) or {}
    defin = (bloques.get("definicion", {}) or {})
    protegidos = bloques.get("protegidos", []) or []

    def parse_horario(h: str):
        a, b = h.split("–")
        ha, ma = map(int, a.split(":"))
        hb, mb = map(int, b.split(":"))
        return time(ha, ma), time(hb, mb)

    def overlap(a1, a2, b1, b2):
        # intervalos [a1,a2) y [b1,b2)
        return (a1 < b2) and (b1 < a2)

    if defin and protegidos:
        for bp in protegidos:
            fecha_bp = pd.Timestamp(bp["fecha"]).date()
            bloque_id = str(bp["bloque"])
            if bloque_id not in defin:
                continue
            b_ini = hhmm_a_time(defin[bloque_id]["inicio"])
            b_fin = hhmm_a_time(defin[bloque_id]["fin"])

            mask_fecha = (df["fecha"] == fecha_bp) & (df["actividad"] != "Misión")
            idxs = df.index[mask_fecha].tolist()
            for i in idxs:
                h = str(df.at[i, "horario"] or "").strip()
                if "–" not in h:
                    continue
                e_ini, e_fin = parse_horario(h)
                if overlap(e_ini, e_fin, b_ini, b_fin):
                    obs = str(df.at[i, "observaciones"] or "").strip()
                    tag = f"CONFLICTO: Bloque protegido {bloque_id}"
                    df.at[i, "observaciones"] = (obs + " | " if obs else "") + tag

    # ---- ordenar por sección + fecha + hora inicio ----
    def hora_inicio(h):
        if isinstance(h, str) and "–" in h:
            return h.split("–")[0]
        return "00:00"

    df["_inicio_dt"] = pd.to_datetime(
        df["fecha"].astype(str) + " " + df["horario"].fillna("").apply(hora_inicio),
        errors="coerce"
    )
    df = df.sort_values(["sección", "fecha", "_inicio_dt"], na_position="last").drop(columns=["_inicio_dt"])

    # columnas finales (orden)
    cols = ["semana", "fecha", "día", "horario", "sección", "actividad", "tema", "evaluación", "profesores", "misiones", "observaciones"]
    df = df[cols]

    return df


def exportar_excel(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with pd.ExcelWriter(path, engine="openpyxl", datetime_format="DD/MM/YYYY") as writer:
        df.to_excel(writer, index=False, sheet_name="Calendario")
        ws = writer.sheets["Calendario"]

        # congelar encabezado
        ws.freeze_panes = "A2"

        # estilo encabezados
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        headers = [c.value for c in ws[1]]
        col_fecha = headers.index("fecha") + 1 if "fecha" in headers else None
        col_horario = headers.index("horario") + 1 if "horario" in headers else None

        # forzar formato fecha y horario para evitar 70348 / ######
        if col_fecha is not None:
            for r in range(2, ws.max_row + 1):
                c = ws.cell(row=r, column=col_fecha)
                # convertir string -> date si hiciera falta
                if isinstance(c.value, str) and c.value.strip():
                    try:
                        c.value = pd.to_datetime(c.value).date()
                    except Exception:
                        pass
                c.number_format = "DD/MM/YYYY"
                c.alignment = Alignment(horizontal="center")

        if col_horario is not None:
            for r in range(2, ws.max_row + 1):
                c = ws.cell(row=r, column=col_horario)
                if c.value is None:
                    c.value = ""
                c.number_format = "@"
                c.alignment = Alignment(horizontal="center")

        # auto-anchos (evita ######)
        for col_idx in range(1, ws.max_column + 1):
            max_len = 0
            for r in range(1, ws.max_row + 1):
                v = ws.cell(row=r, column=col_idx).value
                if v is None:
                    continue
                s = str(v)
                if len(s) > max_len:
                    max_len = len(s)
            ws.column_dimensions[get_column_letter(col_idx)].width = min(max(10, max_len + 2), 45)

        # tabla estilo Excel
        try:
            tab = Table(
                displayName="TablaCalendario",
                ref=f"A1:{get_column_letter(ws.max_column)}{ws.max_row}"
            )
            style = TableStyleInfo(
                name="TableStyleMedium9",
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
                showColumnStripes=False,
            )
            tab.tableStyleInfo = style
            ws.add_table(tab)
        except Exception:
            pass


def main():
    config = cargar_config("calendario_config.yml")
    df = construir_df(config)
    out = config["salida"]["excel_path"]
    exportar_excel(df, out)
    print(f"OK: Excel generado en {out} con {len(df)} filas.")


if __name__ == "__main__":
    main()