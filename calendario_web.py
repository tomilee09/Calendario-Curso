import os
import html
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from streamlit_calendar import calendar

# ============================================================
# CONFIG FIJA
# ============================================================
TIMEZONE = "America/Santiago"
LOGO_PATH = "assets/logo.png"
DATA_DIR = "data"

CURSOS = {
    "fokito": {
        "label": "Fokito",
        "carpeta": "fokito",
        "emoji": "🧮",
    },
    "tecnologia_medica": {
        "label": "Tecnología Médica",
        "carpeta": "tecnologia_medica",
        "emoji": "🩺",
    },
    "medicina": {
        "label": "Medicina",
        "carpeta": "medicina",
        "emoji": "🏥",
    },
}

# ============================================================
# UTILIDADES Y ESTILOS
# ============================================================
PROF_PALETTE = {
    "TY": "#1f77b4", "IG": "#2ca02c", "CC": "#ff7f0e",
    "AR": "#9467bd", "JCS": "#8c564b",
    "p1": "#1f77b4", "p2": "#2ca02c", "p3": "#ff7f0e",
    "p4": "#9467bd", "p5": "#8c564b", "p6": "#e377c2",
    "Todos": "#374151"
}

EVAL_ICON = {
    "Trabajo práctico": "📝",
    "Control": "⭐",          # o "🧾" si prefieres
    "Certamen": "🧠",         # opcional
    "Examen": "🎓",           # opcional
}

ACT_COLORS = {
    "Clase teórica": "#1f77b4",
    "Seminario": "#2ca02c",
    "Laboratorio": "#ff7f0e",
    "Trabajo autónomo": "#9467bd",
    "Sin clases (Feriado)": "#d62728",
    "Sin clases (Pausa académica)": "#d62728",
    "Examen": "#111111",
    "Misión": "#8c564b",
}

PASO_LABELS = {
    "pedir_preguntas": "Proponer preguntas",
    "construir_control": "Construcción evaluación",
    "pauta_prueba": "Construcción pauta",
    "revisar_prueba": "Revisar evaluación",
    "escanear": "Escanear evaluación",
    "corregir_y_notas": "Corregir y poner notas",
    "revisar_tp": "Revisar TP y poner nota",
    "revision_guia": "Revisión de guía",
    "subir_pauta_controles": "Subir pauta controles",
    "pauta_seminario": "Pauta seminario",
    "presentacion_grupal": "Presentación grupal seminario",
    "construir_examen": "Construcción examen",
    "pauta_examen": "Pauta examen",
    "corregir_examen": "Corregir examen",
    "revision_actividad_autonoma": "Revisión actividad autónoma",
    "revision_controles_y_nota": "Revisión controles y poner nota",
    "revisar_pruebas": "Revisar pruebas",
}

ORDEN_PASOS = [
    "pedir_preguntas",
    "construir_control",
    "pauta_prueba",
    "revisar_prueba",
    "revision_guia",
    "subir_pauta_controles",
    "pauta_seminario",
    "presentacion_grupal",
    "escanear",
    "corregir_y_notas",
    "revisar_tp",
    "construir_examen",
    "pauta_examen",
    "corregir_examen",
    "revision_actividad_autonoma",
    "revision_controles_y_nota",
    "revisar_pruebas",
]


def obtener_paths_curso(curso_key: str):
    carpeta = CURSOS[curso_key]["carpeta"]
    base_dir = os.path.join(DATA_DIR, carpeta)

    return {
        "base_dir": base_dir,
        "excel_calendario": os.path.join(base_dir, "calendario.xlsx"),
        "excel_misiones": os.path.join(base_dir, "misiones.xlsx"),
    }


def split_profes(s: str):
    if not s or pd.isna(s):
        return []
    return [x.strip() for x in str(s).split(",") if x.strip()]


def row_has_prof(row_prof: str, selected_set: set) -> bool:
    profs = set(split_profes(row_prof))
    if not profs:
        return False
    return len(profs.intersection(selected_set)) > 0


def escape_texto(x):
    if x is None or pd.isna(x):
        return ""
    return html.escape(str(x))


def color_paso(paso: str) -> str:
    paso = str(paso).strip()
    if paso in ["pedir_preguntas", "construir_control", "pauta_prueba", "construir_examen", "pauta_examen"]:
        return "#dbeafe"
    if paso in ["revisar_prueba", "revision_guia", "revisar_pruebas"]:
        return "#fef3c7"
    if paso in ["escanear", "subir_pauta_controles"]:
        return "#ede9fe"
    if paso in ["corregir_y_notas", "revisar_tp", "corregir_examen", "revision_controles_y_nota"]:
        return "#dcfce7"
    if paso in ["pauta_seminario", "presentacion_grupal"]:
        return "#ffe4e6"
    return "#f3f4f6"


# ============================================================
# CARGA DE DATOS
# ============================================================
def cargar_datos_calendario_excel(excel_calendario_path):
    if not os.path.exists(excel_calendario_path):
        st.error(f"⚠️ No se encontró el archivo: {excel_calendario_path}")
        st.warning("Genera primero el Excel correspondiente al curso seleccionado.")
        st.stop()

    df = pd.read_excel(excel_calendario_path, sheet_name="Calendario")
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    cols_str = [
        "horario", "sección", "actividad", "tema",
        "evaluación", "profesores", "observaciones"
    ]
    for c in cols_str:
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str)

    return df


def cargar_sheet_excel(path, sheet):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_excel(path, sheet_name=sheet)
    except Exception:
        return pd.DataFrame()


def cargar_datos_misiones_base(excel_misiones_path):
    df = cargar_sheet_excel(excel_misiones_path, "Misiones")
    if df.empty:
        return df

    for c in ["fecha_limite", "fecha_evento", "fecha"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    for c in ["evento", "paso", "sección", "responsables", "detalle", "estado"]:
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str)

    return df


# ============================================================
# TAB 2: COLORES WEB PARA CALENDARIO
# ============================================================
def color_fila_calendario(row):
    actividad = str(row.get("actividad", "")).strip()
    evaluacion = str(row.get("evaluación", "")).strip()

    mapa = {
        "Clase teórica": "#dbeafe",
        "Seminario": "#dcfce7",
        "Laboratorio": "#ffedd5",
        "Trabajo autónomo": "#ede9fe",
        "Sin clases (Feriado)": "#fee2e2",
        "Sin clases (Pausa académica)": "#fecaca",
        "Examen": "#e5e7eb",
    }

    color = mapa.get(actividad, "#ffffff")
    estilos = [f"background-color: {color};" for _ in row.index]

    if evaluacion:
        for i, col in enumerate(row.index):
            if col == "evaluación":
                estilos[i] = "background-color: #fde68a; font-weight: bold;"
            elif col == "observaciones":
                estilos[i] = estilos[i] + " font-style: italic;"

    return estilos


def estilo_tabla_calendario(df_tabla: pd.DataFrame):
    df2 = df_tabla.copy()

    if "fecha" in df2.columns:
        df2["fecha"] = pd.to_datetime(df2["fecha"], errors="coerce")

    styler = (
        df2.style
        .apply(color_fila_calendario, axis=1)
        .format({"fecha": lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else ""})
        .set_properties(**{
            "text-align": "left",
            "font-size": "13px",
            "border-color": "#d1d5db"
        })
        .set_properties(subset=[c for c in ["fecha", "semana", "horario"] if c in df2.columns], **{
            "text-align": "center"
        })
        .set_properties(subset=[c for c in ["evaluación"] if c in df2.columns], **{
            "text-align": "center"
        })
    )

    return styler


def tabla_resumen_colores():
    html_leyenda = """
    <div style="display:flex; flex-wrap:wrap; gap:10px; margin:8px 0 14px 0; font-size:13px;">
        <span style="background:#dbeafe; padding:6px 10px; border-radius:8px;">Clase teórica</span>
        <span style="background:#dcfce7; padding:6px 10px; border-radius:8px;">Seminario</span>
        <span style="background:#ffedd5; padding:6px 10px; border-radius:8px;">Laboratorio</span>
        <span style="background:#ede9fe; padding:6px 10px; border-radius:8px;">Trabajo autónomo</span>
        <span style="background:#fee2e2; padding:6px 10px; border-radius:8px;">Feriado</span>
        <span style="background:#fecaca; padding:6px 10px; border-radius:8px;">Pausa académica</span>
        <span style="background:#e5e7eb; padding:6px 10px; border-radius:8px;">Examen</span>
        <span style="background:#fde68a; padding:6px 10px; border-radius:8px; font-weight:700;">Evaluación</span>
    </div>
    """
    st.markdown(html_leyenda, unsafe_allow_html=True)


# ============================================================
# RENDER HTML MISIONES
# ============================================================
def render_badges_profes(responsables: str) -> str:
    lista = split_profes(responsables)
    if not lista:
        return "<span style='color:#999;'>—</span>"

    badges = []
    for p in lista:
        color = PROF_PALETTE.get(p, "#6b7280")
        badges.append(
            f"<span style='display:inline-block; margin:2px 4px 2px 0; "
            f"padding:4px 9px; border-radius:999px; background:{color}; color:white; "
            f"font-size:12px; font-weight:600;'>{escape_texto(p)}</span>"
        )
    return "".join(badges)


def render_matriz_misiones_html(df_mis: pd.DataFrame) -> str:
    if df_mis.empty:
        return "<p>No hay misiones disponibles.</p>"

    df2 = df_mis.copy()

    for c in ["evento", "paso", "sección", "responsables", "detalle"]:
        if c in df2.columns:
            df2[c] = df2[c].fillna("").astype(str)

    df2["_orden_paso"] = df2["paso"].apply(
        lambda x: ORDEN_PASOS.index(x) if x in ORDEN_PASOS else 999
    )

    secciones_fijas = ["Sección 1", "Sección 2", "Sección 3", "Sección 4"]
    secciones_presentes = [s for s in secciones_fijas if s in df2["sección"].unique()]
    if not secciones_presentes:
        secciones_presentes = sorted(df2["sección"].unique())

    df_pivot = df2.pivot_table(
        index=["evento", "paso", "detalle", "_orden_paso"],
        columns="sección",
        values="responsables",
        aggfunc=lambda x: " | ".join(sorted(set([str(v).strip() for v in x if str(v).strip()]))),
        fill_value=""
    ).reset_index()

    df_pivot = df_pivot.sort_values(["evento", "_orden_paso", "detalle"]).reset_index(drop=True)

    rows_html = ""
    ultimo_evento = None

    for _, row in df_pivot.iterrows():
        evento = str(row.get("evento", "")).strip()
        paso = str(row.get("paso", "")).strip()
        detalle = str(row.get("detalle", "")).strip()

        paso_label = PASO_LABELS.get(paso, paso if paso else "—")
        color_fila = color_paso(paso)

        if evento == ultimo_evento:
            evento_html = "<span style='color:#bbb;'>↳</span>"
        else:
            evento_html = f"<div style='font-weight:800;'>{escape_texto(evento)}</div>"
            ultimo_evento = evento

        detalle_html = f"""
        <div style="font-weight:700; color:#111827;">{escape_texto(paso_label)}</div>
        <div style="font-size:12px; color:#6b7280; margin-top:3px;">{escape_texto(detalle) if detalle else "—"}</div>
        """

        celdas_secciones = ""
        for sec in secciones_presentes:
            val = str(row.get(sec, "")).strip()
            if val:
                contenido = render_badges_profes(val)
            else:
                contenido = "<span style='color:#bbb;'>—</span>"

            celdas_secciones += f"""
            <td style="padding:10px; border:1px solid #d1d5db; vertical-align:top; background:white;">
                {contenido}
            </td>
            """

        rows_html += f"""
        <tr>
            <td style="padding:10px; border:1px solid #d1d5db; vertical-align:top; background:#f9fafb; min-width:180px;">
                {evento_html}
            </td>
            <td style="padding:10px; border:1px solid #d1d5db; vertical-align:top; background:{color_fila}; min-width:320px;">
                {detalle_html}
            </td>
            {celdas_secciones}
        </tr>
        """

    headers_sec = "".join([
        f'<th style="padding:10px; border:1px solid #9ca3af; background:#9ca3af; color:black; text-align:center; font-weight:800;">{escape_texto(sec)}</th>'
        for sec in secciones_presentes
    ])

    return f"""
    <style>
        .tabla-matriz-wrap {{ width:100%; overflow-x:auto; }}
        .tabla-matriz {{
            width:100%;
            min-width:1400px;
            border-collapse:collapse;
            font-family:Arial, sans-serif;
            font-size:14px;
        }}
        .tabla-matriz tr:hover td {{ filter:brightness(0.99); }}
    </style>
    <div class="tabla-matriz-wrap">
        <table class="tabla-matriz">
            <thead>
                <tr>
                    <th style="padding:10px; border:1px solid #9ca3af; background:#9ca3af; color:black; text-align:center; font-weight:800;">Evaluación</th>
                    <th style="padding:10px; border:1px solid #9ca3af; background:#9ca3af; color:black; text-align:center; font-weight:800;">Misión / Detalle</th>
                    {headers_sec}
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """


def render_plan_html(df_plan: pd.DataFrame) -> str:
    if df_plan.empty:
        return "<p>No hay plan disponible.</p>"

    df2 = df_plan.copy()

    if "fecha_limite" in df2.columns:
        df2["fecha_limite"] = pd.to_datetime(df2["fecha_limite"], errors="coerce")
    if "fecha_evento" in df2.columns:
        df2["fecha_evento"] = pd.to_datetime(df2["fecha_evento"], errors="coerce")

    if "paso" in df2.columns:
        df2["_orden"] = df2["paso"].apply(lambda x: ORDEN_PASOS.index(x) if x in ORDEN_PASOS else 999)
    else:
        df2["_orden"] = 999

    ordenar_cols = [c for c in ["evento", "_orden", "sección", "fecha_limite"] if c in df2.columns]
    if ordenar_cols:
        df2 = df2.sort_values(ordenar_cols)

    rows_html = ""
    for _, row in df2.iterrows():
        evento = escape_texto(row.get("evento", ""))
        paso = str(row.get("paso", "")).strip()
        paso_label = PASO_LABELS.get(paso, paso if paso else "—")
        seccion = escape_texto(row.get("sección", ""))
        fecha_limite = row.get("fecha_limite", pd.NaT)
        fecha_evento = row.get("fecha_evento", pd.NaT)
        detalle = escape_texto(row.get("detalle", ""))
        responsables = str(row.get("responsables", "")).strip()
        estado = str(row.get("estado", "Pendiente")).strip()

        fecha_limite_str = fecha_limite.strftime("%d/%m/%Y") if pd.notna(fecha_limite) else "—"
        fecha_evento_str = fecha_evento.strftime("%d/%m/%Y") if pd.notna(fecha_evento) else "—"

        color_fila = color_paso(paso)
        color_estado = "#dcfce7" if estado.lower() in ["listo", "ok", "done", "completado", "completada"] else "#fee2e2"

        rows_html += f"""
        <tr>
            <td style="padding:10px; border:1px solid #d1d5db; background:{color_fila}; font-weight:700;">{evento}</td>
            <td style="padding:10px; border:1px solid #d1d5db; background:{color_fila};">{escape_texto(paso_label)}</td>
            <td style="padding:10px; border:1px solid #d1d5db;">{seccion}</td>
            <td style="padding:10px; border:1px solid #d1d5db; background:#fecaca; font-weight:700; text-align:center;">{fecha_limite_str}</td>
            <td style="padding:10px; border:1px solid #d1d5db; text-align:center;">{fecha_evento_str}</td>
            <td style="padding:10px; border:1px solid #d1d5db;">{render_badges_profes(responsables)}</td>
            <td style="padding:10px; border:1px solid #d1d5db;">{detalle if detalle else "—"}</td>
            <td style="padding:10px; border:1px solid #d1d5db; background:{color_estado}; font-weight:700; text-align:center;">{escape_texto(estado)}</td>
        </tr>
        """

    return f"""
    <style>
        .tabla-plan-wrap {{ width:100%; overflow-x:auto; }}
        .tabla-plan {{
            width:100%;
            min-width:1400px;
            border-collapse:collapse;
            font-family:Arial, sans-serif;
            font-size:14px;
        }}
        .tabla-plan tr:hover td {{ filter:brightness(0.99); }}
    </style>
    <div class="tabla-plan-wrap">
        <table class="tabla-plan">
            <thead>
                <tr>
                    <th style="padding:10px; border:1px solid #9ca3af; background:#374151; color:white;">Evaluación</th>
                    <th style="padding:10px; border:1px solid #9ca3af; background:#374151; color:white;">Paso</th>
                    <th style="padding:10px; border:1px solid #9ca3af; background:#374151; color:white;">Sección</th>
                    <th style="padding:10px; border:1px solid #9ca3af; background:#374151; color:white;">Fecha límite</th>
                    <th style="padding:10px; border:1px solid #9ca3af; background:#374151; color:white;">Fecha evaluación</th>
                    <th style="padding:10px; border:1px solid #9ca3af; background:#374151; color:white;">Responsables</th>
                    <th style="padding:10px; border:1px solid #9ca3af; background:#374151; color:white;">Detalle</th>
                    <th style="padding:10px; border:1px solid #9ca3af; background:#374151; color:white;">Estado</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """


# ============================================================
# CALENDARIO
# ============================================================
def df_calendario_a_fullcalendar_events(df: pd.DataFrame):
    events = []

    for _, r in df.iterrows():
        fecha = r["fecha"]
        horario = r.get("horario", "").strip()
        tema = r.get("tema", "").strip()
        evaluacion = r.get("evaluación", "").strip()
        profs = r.get("profesores", "").strip()
        obs = r.get("observaciones", "").strip()
        actividad = r.get("actividad", "").strip()

        eval_ic = EVAL_ICON.get(evaluacion, "")
        prefix = (eval_ic + " ") if eval_ic else ""

        all_day = False
        start_iso, end_iso = "", ""

        if "–" in horario or "-" in horario:
            try:
                h_clean = horario.replace("-", "–")
                a, b = h_clean.split("–")
                hi = pd.to_datetime(a.strip(), format="%H:%M").time()
                hf = pd.to_datetime(b.strip(), format="%H:%M").time()

                start_dt = fecha + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
                end_dt = fecha + pd.Timedelta(hours=hf.hour, minutes=hf.minute)

                start_iso = start_dt.isoformat()
                end_iso = end_dt.isoformat()
            except Exception:
                all_day = True
                start_iso = fecha.date().isoformat()
                end_iso = (fecha + pd.Timedelta(days=1)).date().isoformat()
        else:
            all_day = True
            start_iso = fecha.date().isoformat()
            end_iso = (fecha + pd.Timedelta(days=1)).date().isoformat()

        # title = f"{prefix}{actividad} · {tema}" if tema else f"{prefix}{actividad}"
        
        title = f"{prefix}{actividad} · {tema}" if tema else f"{prefix}{actividad}"
        if evaluacion:
            title = f"{prefix}{evaluacion} · {actividad}" + (f" · {tema}" if tema else "")

        # color = ACT_COLORS.get(actividad, "#888888")
        # if "Feriado" in actividad or "Pausa" in actividad:
        #     color = ACT_COLORS.get("Sin clases (Feriado)")
        color = ACT_COLORS.get(actividad, "#888888")
        if "Feriado" in actividad or "Pausa" in actividad:
            color = ACT_COLORS.get("Sin clases (Feriado)")

        # 🔥 Resaltar evaluaciones (control/prueba/tp) con un color fuerte
        if evaluacion:
            color = "#f59e0b"   # ámbar (muy visible)

        events.append({
            "title": title,
            "start": start_iso,
            "end": end_iso,
            "allDay": all_day,
            "color": color,
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


def df_misiones_a_fullcalendar_events(df_mis: pd.DataFrame):
    events = []

    if df_mis.empty:
        return events

    for _, r in df_mis.iterrows():
        fecha = r.get("fecha_limite", pd.NaT)
        if pd.isna(fecha):
            continue

        evento = str(r.get("evento", "")).strip()
        paso = str(r.get("paso", "")).strip()
        paso_label = PASO_LABELS.get(paso, paso)
        responsables = str(r.get("responsables", "")).strip()
        seccion = str(r.get("sección", "")).strip()
        detalle = str(r.get("detalle", "")).strip()
        estado = str(r.get("estado", "Pendiente")).strip()

        title = f"🚩 {evento} · {paso_label}"

        events.append({
            "title": title,
            "start": fecha.date().isoformat(),
            "end": (fecha + pd.Timedelta(days=1)).date().isoformat(),
            "allDay": True,
            "color": ACT_COLORS.get("Misión", "#8c564b"),
            "extendedProps": {
                "tipo": "mision",
                "actividad": "Misión",
                "tema": evento,
                "horario": "",
                "sección": seccion,
                "evaluación": paso_label,
                "profesores": responsables,
                "observaciones": f"{detalle} | Estado: {estado}" if detalle else f"Estado: {estado}",
            }
        })

    return events


# ============================================================
# MODAL
# ============================================================
@st.dialog("Detalles del Evento")
def mostrar_detalle_evento(props):
    actividad = props.get("actividad", "Evento")
    tema = props.get("tema", "")
    color = ACT_COLORS.get(actividad, "#333333")

    st.markdown(f"""
    <div style="background-color:{color}; padding:10px; border-radius:8px; color:white; margin-bottom:10px;">
        <h3 style="margin:0;">{actividad}</h3>
        <p style="margin:0; font-size:0.9em; opacity:0.9;">{tema}</p>
    </div>
    """, unsafe_allow_html=True)

    data = {
        "Horario": props.get("horario", "Todo el día"),
        "Sección": props.get("sección", "-"),
        "Profesores": props.get("profesores", "-"),
        "Evaluación / Paso": props.get("evaluación", "-"),
        "Observaciones": props.get("observaciones", "-")
    }

    for k, v in data.items():
        if v and str(v).strip() and str(v) != "nan":
            st.markdown(f"**{k}:** {v}")


# ============================================================
# UI PRINCIPAL
# ============================================================
st.set_page_config(page_title="Calendario del Curso", layout="wide")

st.markdown("""
<style>
div.stButton > button {
    min-height: 70px;
    font-size: 22px;
    font-weight: 700;
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

if "curso_seleccionado" not in st.session_state:
    st.session_state.curso_seleccionado = "fokito"

c1, c2 = st.columns([5, 1])
with c1:
    st.title("📅 Calendarios de Cursos")
    st.caption("Selecciona un curso para cargar su calendario y sus misiones.")
with c2:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)

st.markdown("### Selección de curso")

b1, b2, b3 = st.columns(3)

with b1:
    if st.button("🧮 Fokito", use_container_width=True):
        st.session_state.curso_seleccionado = "fokito"

with b2:
    if st.button("🩺 Tecnología Médica", use_container_width=True):
        st.session_state.curso_seleccionado = "tecnologia_medica"

with b3:
    if st.button("🏥 Medicina", use_container_width=True):
        st.session_state.curso_seleccionado = "medicina"

curso_actual = st.session_state.curso_seleccionado
curso_info = CURSOS[curso_actual]
paths = obtener_paths_curso(curso_actual)

EXCEL_CALENDARIO_PATH = paths["excel_calendario"]
EXCEL_MISIONES_PATH = paths["excel_misiones"]

st.info(f"Curso actual: **{curso_info['label']}**")

df = cargar_datos_calendario_excel(EXCEL_CALENDARIO_PATH)
df_misiones = cargar_datos_misiones_base(EXCEL_MISIONES_PATH)
df_mat = cargar_sheet_excel(EXCEL_MISIONES_PATH, "Matriz")
df_plan = cargar_sheet_excel(EXCEL_MISIONES_PATH, "Plan")

all_secciones = sorted(df["sección"].dropna().unique())

all_prof_codes = set()
for s in df["profesores"].dropna().unique():
    for p in split_profes(s):
        all_prof_codes.add(p)

if not df_misiones.empty and "responsables" in df_misiones.columns:
    for s in df_misiones["responsables"].dropna().unique():
        for p in split_profes(s):
            all_prof_codes.add(p)

all_prof_codes = sorted(all_prof_codes)

if "curso_anterior" not in st.session_state:
    st.session_state.curso_anterior = curso_actual

if st.session_state.curso_anterior != curso_actual:
    st.session_state.sel_secciones = {s: True for s in all_secciones}
    st.session_state.sel_profes = {p: True for p in all_prof_codes}
    st.session_state.nav_semana = 1
    st.session_state.curso_anterior = curso_actual

if "sel_secciones" not in st.session_state:
    st.session_state.sel_secciones = {s: True for s in all_secciones}
else:
    st.session_state.sel_secciones = {
        s: st.session_state.sel_secciones.get(s, True) for s in all_secciones
    }

if "sel_profes" not in st.session_state:
    st.session_state.sel_profes = {p: True for p in all_prof_codes}
else:
    st.session_state.sel_profes = {
        p: st.session_state.sel_profes.get(p, True) for p in all_prof_codes
    }

tab1, tab2, tab3, tab4 = st.tabs([
    "📆 Calendario",
    "📄 Excel Horarios",
    "🧭 Misiones",
    "📊 Estadísticas"
])

# ============================================================
# TAB 1: CALENDARIO
# ============================================================
with tab1:
    if "nav_semana" not in st.session_state:
        st.session_state.nav_semana = 1

    semana_sel = st.session_state.nav_semana
    sec_selected = {s for s, ok in st.session_state.sel_secciones.items() if ok}
    prof_selected = {p for p, ok in st.session_state.sel_profes.items() if ok}

    df_f = df[df["sección"].isin(sec_selected)].copy()

    if all_prof_codes:
        df_f = df_f[
            df_f["profesores"].apply(
                lambda x: row_has_prof(x, prof_selected) if prof_selected else True
            )
        ].copy()

    fechas_semana = df[df["semana"] == semana_sel]["fecha"]
    if not fechas_semana.empty:
        initial_date = fechas_semana.min().strftime("%Y-%m-%d")
    else:
        min_global = df["fecha"].min()
        initial_date = (min_global + pd.Timedelta(days=7 * (semana_sel - 1))).strftime("%Y-%m-%d")

    events_cal = df_calendario_a_fullcalendar_events(df_f)
    events_mis = df_misiones_a_fullcalendar_events(df_misiones)
    events = events_cal + events_mis

    calendar_options = {
        "initialView": "timeGridWeek",
        "initialDate": initial_date,
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,listWeek",
        },
        "height": 750,
        "slotMinTime": "08:00:00",
        "slotMaxTime": "21:00:00",
        "allDaySlot": True,
        "weekNumbers": True,
    }

    state = calendar(events=events, options=calendar_options, key=f"cal_{curso_actual}_{semana_sel}")

    if state.get("eventClick"):
        ev = state["eventClick"]["event"]
        props = ev.get("extendedProps", {})
        mostrar_detalle_evento(props)

    st.divider()

    c_nav, c_filtros = st.columns([1, 2])

    with c_nav:
        st.subheader("Navegación")
        max_sem = df["semana"].max()
        if pd.isna(max_sem):
            max_sem = 20
        weeks = list(range(1, int(max_sem) + 1))

        st.radio(
            "Seleccionar Semana:",
            options=weeks,
            horizontal=True,
            key="nav_semana"
        )

    with c_filtros:
        st.subheader("Filtros")
        fcol1, fcol2 = st.columns(2)

        with fcol1:
            st.caption("Secciones")
            for s in all_secciones:
                st.checkbox(
                    s,
                    value=st.session_state.sel_secciones.get(s, True),
                    key=f"sec_{curso_actual}_{s}"
                )
                st.session_state.sel_secciones[s] = st.session_state[f"sec_{curso_actual}_{s}"]

        with fcol2:
            st.caption("Profesores")
            if not all_prof_codes:
                st.info("No hay profesores.")
            for p in all_prof_codes:
                st.checkbox(
                    p,
                    value=st.session_state.sel_profes.get(p, True),
                    key=f"prof_{curso_actual}_{p}"
                )
                st.session_state.sel_profes[p] = st.session_state[f"prof_{curso_actual}_{p}"]

# ============================================================
# TAB 2: HORARIOS
# ============================================================
with tab2:
    st.subheader(f"📄 Horarios cargados de: {EXCEL_CALENDARIO_PATH}")
    st.caption("Vista coloreada en la web para facilitar la lectura.")

    tabla_resumen_colores()

    df_tab2 = df.sort_values(["semana", "sección", "fecha"]).copy()

    st.dataframe(
        estilo_tabla_calendario(df_tab2),
        use_container_width=True,
        hide_index=True
    )

    if os.path.exists(EXCEL_CALENDARIO_PATH):
        with open(EXCEL_CALENDARIO_PATH, "rb") as f:
            st.download_button(
                "⬇️ Descargar Excel de Horarios",
                f,
                file_name=f"calendario_{curso_actual}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ============================================================
# TAB 3: MISIONES
# ============================================================
with tab3:
    st.subheader(f"🧭 Misiones y protocolo docente — {curso_info['label']}")
    st.caption("Vista ordenada para profesores: matriz rápida con todas las misiones y plan detallado.")

    if df_plan.empty and df_misiones.empty:
        st.info("No se encontró 'misiones.xlsx' o no tiene las hojas esperadas.")
    else:
        if not df_misiones.empty:
            st.markdown("### 📌 Matriz rápida por sección")
            html_mat = render_matriz_misiones_html(df_misiones)
            components.html(html_mat, height=650, scrolling=True)

        if not df_plan.empty:
            st.markdown("### ✅ Plan completo por evaluación")
            html_plan = render_plan_html(df_plan)
            components.html(html_plan, height=650, scrolling=True)

        if os.path.exists(EXCEL_MISIONES_PATH):
            with open(EXCEL_MISIONES_PATH, "rb") as f:
                st.download_button(
                    "⬇️ Descargar Excel de Misiones",
                    f,
                    file_name=f"misiones_{curso_actual}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# ============================================================
# TAB 4: ESTADÍSTICAS
# ============================================================
with tab4:
    st.subheader("📊 Plots útiles para profesores")

    df_plot = df.copy()
    df_plot["semana"] = pd.to_numeric(df_plot["semana"], errors="coerce")
    df_plot = df_plot.dropna(subset=["semana"])

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Eventos por semana")
        week_counts = df_plot.groupby("semana").size().rename("eventos")
        st.bar_chart(week_counts)

    with c2:
        st.markdown("### Eventos por actividad")
        act_counts = df_plot.groupby("actividad").size().rename("eventos").sort_values(ascending=False)
        st.bar_chart(act_counts)

    st.divider()

    st.markdown("### Carga por profesor (horarios)")
    rows = []
    for _, r in df_plot.iterrows():
        for p in split_profes(r.get("profesores", "")):
            rows.append({
                "profesor": p,
                "actividad": r.get("actividad", ""),
                "semana": r.get("semana", None)
            })

    if rows:
        prof_df = pd.DataFrame(rows)
        prof_counts = prof_df.groupby("profesor").size().rename("eventos").sort_values(ascending=False)
        st.bar_chart(prof_counts)
    else:
        st.info("No hay profesores asignados en el calendario.")

    st.divider()

    if not df_misiones.empty:
        st.markdown("### Misiones por profesor")
        filas_misiones = []
        for _, r in df_misiones.iterrows():
            for p in split_profes(r.get("responsables", "")):
                filas_misiones.append({
                    "profesor": p,
                    "evento": r.get("evento", ""),
                    "paso": PASO_LABELS.get(str(r.get("paso", "")).strip(), str(r.get("paso", "")).strip())
                })

        if filas_misiones:
            df_mp = pd.DataFrame(filas_misiones)
            conteo_misiones = df_mp.groupby("profesor").size().rename("misiones").sort_values(ascending=False)
            st.bar_chart(conteo_misiones)

            st.markdown("### Distribución por tipo de paso")
            conteo_pasos = df_mp.groupby("paso").size().rename("cantidad").sort_values(ascending=False)
            st.bar_chart(conteo_pasos)