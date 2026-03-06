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
    
    "enobnu": {
    "label": "Enobnu",
    "carpeta": "enobnu",   # debe existir: data/enobnu/calendario.xlsx y data/enobnu/misiones.xlsx
    "emoji": "🍇",         # cambia el emoji si quieres
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

SECTION_COLORS = {
    "Sección 1": "rgba(59, 130, 246, 0.18)",   # azul suave
    "Sección 2": "rgba(34, 197, 94, 0.18)",    # verde suave
    "Sección 3": "rgba(249, 115, 22, 0.18)",   # naranjo suave
    "Sección 4": "rgba(168, 85, 247, 0.18)",   # violeta suave
}

BORDER_BY_ACTIVIDAD = {
    "Clase teórica": "#111827",    # gris/negro
    "Seminario": "#2563eb",        # azul
    "Laboratorio": "#f59e0b",      # ámbar
    "Trabajo autónomo": "#6b7280", # gris
    "Examen": "#111827",           # negro
    "Misión": "#991b1b",           # rojo oscuro
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



def tabla_misiones_por_profesor_y_mes(df_misiones: pd.DataFrame):
    """
    UI: tabs por profesor (p1..pN) y selector de mes.
    Muestra una tabla con misiones (fecha_limite, paso, evento, sección, detalle).
    """
    if df_misiones.empty:
        st.info("No hay misiones para mostrar.")
        return

    df2 = df_misiones.copy()

    # Asegurar datetime
    df2["fecha_limite"] = pd.to_datetime(df2.get("fecha_limite", pd.NaT), errors="coerce")
    df2 = df2.dropna(subset=["fecha_limite"]).copy()

    # Columnas seguras
    for c in ["evento", "paso", "sección", "responsables", "detalle", "estado"]:
        if c in df2.columns:
            df2[c] = df2[c].fillna("").astype(str)
        else:
            df2[c] = ""

    # Obtener lista de profes desde responsables
    profs = set()
    for s in df2["responsables"].dropna().unique():
        for p in split_profes(s):
            profs.add(p)

    # Si quieres SOLO p1..p6:
    profs = [p for p in sorted(profs) if p.startswith("p")]
    if not profs:
        st.info("No hay responsables tipo p1, p2, ... en el archivo de misiones.")
        return

    st.markdown("### 👤 Misiones por persona y por mes")
    tabs = st.tabs(profs)

    for i, prof in enumerate(profs):
        with tabs[i]:
            # Filtrar por prof
            dfp = df2[df2["responsables"].apply(lambda x: prof in split_profes(x))].copy()
            if dfp.empty:
                st.info(f"{prof}: no tiene misiones asignadas.")
                continue

            # Meses disponibles para ese prof
            dfp["mes"] = dfp["fecha_limite"].dt.to_period("M").astype(str)
            meses = sorted(dfp["mes"].unique())

            mes_sel = st.selectbox(
                "Selecciona mes:",
                options=meses,
                index=len(meses) - 1,
                key=f"mes_sel_{prof}"
            )

            dfm = dfp[dfp["mes"] == mes_sel].copy()
            dfm = dfm.sort_values(["fecha_limite", "evento", "paso", "sección"])

            # Tabla bonita
            df_show = dfm[["fecha_limite", "evento", "paso", "sección", "detalle", "estado"]].copy()

            # Formato fecha
            df_show["fecha_limite"] = df_show["fecha_limite"].dt.strftime("%d/%m/%Y")

            # Labels más humanos si tienes PASO_LABELS
            if "PASO_LABELS" in globals():
                df_show["paso"] = df_show["paso"].apply(lambda x: PASO_LABELS.get(str(x).strip(), str(x).strip()))

            st.dataframe(
                df_show,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "fecha_limite": st.column_config.TextColumn("Vence"),
                    "evento": st.column_config.TextColumn("Evaluación"),
                    "paso": st.column_config.TextColumn("Misión"),
                    "sección": st.column_config.TextColumn("Sección"),
                    "detalle": st.column_config.TextColumn("Detalle"),
                    "estado": st.column_config.TextColumn("Estado"),
                }
            )

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

        # # color = ACT_COLORS.get(actividad, "#888888")
        # # if "Feriado" in actividad or "Pausa" in actividad:
        # #     color = ACT_COLORS.get("Sin clases (Feriado)")
        # color = ACT_COLORS.get(actividad, "#888888")
        # if "Feriado" in actividad or "Pausa" in actividad:
        #     color = ACT_COLORS.get("Sin clases (Feriado)")

        # # 🔥 Resaltar evaluaciones (control/prueba/tp) con un color fuerte
        # if evaluacion:
        #     color = "#f59e0b"   # ámbar (muy visible)
        
        seccion = r.get("sección", "").strip()
        actividad = r.get("actividad", "").strip()
        evaluacion = r.get("evaluación", "").strip()

        bg = SECTION_COLORS.get(seccion, "rgba(148,163,184,0.14)")  # fallback suave
        border = BORDER_BY_ACTIVIDAD.get(actividad, "#64748b")

        # Si es evaluación, puedes reforzar un poco el borde (opcional)
        if evaluacion:
            border = "#b45309"  # ámbar oscuro

        events.append({            
            "title": title,
            "start": start_iso,
            "end": end_iso,
            "allDay": all_day,
            "backgroundColor": bg,
            "borderColor": border,
            "textColor": "#111827",
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


# def df_misiones_a_fullcalendar_events(df_mis: pd.DataFrame):
#     events = []

#     if df_mis.empty:
#         return events

#     for _, r in df_mis.iterrows():
#         fecha = r.get("fecha_limite", pd.NaT)
#         if pd.isna(fecha):
#             continue

#         evento = str(r.get("evento", "")).strip()
#         paso = str(r.get("paso", "")).strip()
#         paso_label = PASO_LABELS.get(paso, paso)
#         responsables = str(r.get("responsables", "")).strip()
#         seccion = str(r.get("sección", "")).strip()
#         detalle = str(r.get("detalle", "")).strip()
#         estado = str(r.get("estado", "Pendiente")).strip()

#         title = f"🚩 {evento} · {paso_label}"

#         events.append({
#             "title": title,
#             "start": fecha.date().isoformat(),
#             "end": (fecha + pd.Timedelta(days=1)).date().isoformat(),
#             "allDay": True,
#             "color": ACT_COLORS.get("Misión", "#8c564b"),
#             "extendedProps": {
#                 "tipo": "mision",
#                 "actividad": "Misión",
#                 "tema": evento,
#                 "horario": "",
#                 "sección": seccion,
#                 "evaluación": paso_label,
#                 "profesores": responsables,
#                 "observaciones": f"{detalle} | Estado: {estado}" if detalle else f"Estado: {estado}",
#             }
#         })

#     return events

# def df_misiones_a_fullcalendar_events(df_mis: pd.DataFrame):
#     events = []

#     if df_mis.empty:
#         return events

#     for _, r in df_mis.iterrows():
#         fecha = r.get("fecha_limite", pd.NaT)
#         if pd.isna(fecha):
#             continue

#         evento = str(r.get("evento", "")).strip()
#         paso = str(r.get("paso", "")).strip()
#         paso_label = PASO_LABELS.get(paso, paso)
#         responsables = str(r.get("responsables", "")).strip()
#         seccion = str(r.get("sección", "")).strip()
#         detalle = str(r.get("detalle", "")).strip()
#         estado = str(r.get("estado", "Pendiente")).strip()

#         fecha_evento = r.get("fecha_evento", pd.NaT)
#         if pd.notna(fecha_evento):
#             fecha_evento_str = pd.to_datetime(fecha_evento).strftime("%d/%m/%Y")
#         else:
#             fecha_evento_str = ""

#         # Título mucho más explicativo
#         titulo = f"🚩 Fin de plazo: {paso_label}"
#         if evento:
#             titulo += f" — {evento}"
#         if seccion:
#             titulo += f" — {seccion}"

#         # Observaciones completas para el modal
#         obs_partes = []
#         if detalle:
#             obs_partes.append(detalle)
#         if fecha_evento_str:
#             obs_partes.append(f"Evaluación asociada: {fecha_evento_str}")
#         if estado:
#             obs_partes.append(f"Estado: {estado}")

#         obs = " | ".join(obs_partes)

#         events.append({
#             "title": titulo,
#             "start": fecha.date().isoformat(),
#             "end": (fecha + pd.Timedelta(days=1)).date().isoformat(),
#             "allDay": True,
#             "color": "#b91c1c",  # rojo más fuerte para que destaque
#             "extendedProps": {
#                 "tipo": "mision",
#                 "actividad": "Misión",
#                 "tema": titulo,
#                 "horario": "Todo el día",
#                 "sección": seccion,
#                 "evaluación": paso_label,
#                 "profesores": responsables,
#                 "observaciones": obs,
#             }
#         })

#     return events

def df_misiones_a_fullcalendar_events(df_mis: pd.DataFrame):
    """
    Renderiza los plazos de misiones como eventos CON HORA (no allDay),
    dividiendo el día en N segmentos para que SIEMPRE se vean todos.
    """
    events = []
    if df_mis.empty:
        return events

    df2 = df_mis.copy()
    df2["fecha_limite"] = pd.to_datetime(df2.get("fecha_limite", pd.NaT), errors="coerce")
    df2 = df2.dropna(subset=["fecha_limite"]).copy()

    # Agrupamos por día para asignar slots (1/N del día por misión)
    df2["dia"] = df2["fecha_limite"].dt.date

    # Orden lógico (si no está en ORDEN_PASOS, va al final)
    def rank_paso(p):
        p = str(p).strip()
        return ORDEN_PASOS.index(p) if p in ORDEN_PASOS else 999

    df2["_rank"] = df2["paso"].apply(rank_paso)
    df2 = df2.sort_values(["dia", "_rank", "evento", "sección"]).reset_index(drop=True)

    for dia, sub in df2.groupby("dia"):
        sub = sub.reset_index(drop=True)
        n = len(sub)
        if n <= 0:
            continue

        for i in range(n):
            r = sub.loc[i]

            fecha = pd.Timestamp(dia)

            # Segmento horario del día (divide 24h en n partes)
            start_dt = fecha + pd.Timedelta(hours=(24 * i) / n)
            end_dt   = fecha + pd.Timedelta(hours=(24 * (i + 1)) / n)

            evento = str(r.get("evento", "")).strip()
            paso = str(r.get("paso", "")).strip()
            paso_label = PASO_LABELS.get(paso, paso)
            seccion = str(r.get("sección", "")).strip()
            responsables = str(r.get("responsables", "")).strip()
            detalle = str(r.get("detalle", "")).strip()
            estado = str(r.get("estado", "Pendiente")).strip()

            # Título MUY explicativo (y usa observaciones porque ya vienen metidas en detalle)
            titulo = f"🚩 Vence: {paso_label}"
            if evento:
                titulo += f" — {evento}"
            if seccion:
                titulo += f" — {seccion}"

            # Observaciones completas para modal
            obs_partes = []
            if detalle:
                obs_partes.append(detalle)
            if estado:
                obs_partes.append(f"Estado: {estado}")
            obs = " | ".join(obs_partes)

            # Color por tipo de paso (más informativo que rojo único)
            color = "#b91c1c"  # default rojo
            if paso in ["construir_control", "pauta_prueba", "construir_examen", "pauta_examen", "pedir_preguntas"]:
                color = "#2563eb"  # azul
            if paso in ["revisar_prueba", "revision_guia", "revisar_pruebas"]:
                color = "#f59e0b"  # ámbar
            if paso in ["escanear", "subir_pauta_controles"]:
                color = "#7c3aed"  # violeta
            if paso in ["corregir_y_notas", "revisar_tp", "corregir_examen", "revision_controles_y_nota"]:
                color = "#16a34a"  # verde

            events.append({
                "title": titulo,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "allDay": False,  # CLAVE: así no se colapsan
                # "color": color,
                "backgroundColor": "rgba(239, 68, 68, 0.20)",  # rojo con transparencia
                "borderColor": "#991b1b",
                "textColor": "#7f1d1d",
                "extendedProps": {
                    "tipo": "mision",
                    "actividad": "Misión",
                    "tema": titulo,
                    "horario": f"{start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')}",
                    "sección": seccion,
                    "evaluación": paso_label,
                    "profesores": responsables,
                    "observaciones": obs,
                }
            })

    return events


# def df_misiones_deadlines_background_events(df_mis: pd.DataFrame):
#     events = []

#     if df_mis.empty:
#         return events

#     fechas_agregadas = set()

#     for _, r in df_mis.iterrows():
#         fecha = r.get("fecha_limite", pd.NaT)
#         if pd.isna(fecha):
#             continue

#         fecha_str = fecha.date().isoformat()

#         # un solo fondo rojo por día
#         if fecha_str in fechas_agregadas:
#             continue

#         fechas_agregadas.add(fecha_str)

#         events.append({
#             "title": "Vencimiento de misión",
#             "start": fecha_str,
#             "end": (fecha + pd.Timedelta(days=1)).date().isoformat(),
#             "allDay": True,
#             "display": "background",
#             "color": "#fecaca",   # rojo suave visible
#         })

#     return events

def df_misiones_deadlines_background_events(df_mis: pd.DataFrame):
    """
    Crea background events por cada fecha con misiones venciendo.
    Si hay N misiones ese día, divide el día en N franjas (vertical en timeGridWeek).
    """
    events = []
    if df_mis.empty:
        return events

    df2 = df_mis.copy()
    df2["fecha_limite"] = pd.to_datetime(df2.get("fecha_limite", pd.NaT), errors="coerce")
    df2["paso"] = df2.get("paso", "").fillna("").astype(str)

    # Agrupar por día
    df2 = df2.dropna(subset=["fecha_limite"]).copy()
    df2["dia"] = df2["fecha_limite"].dt.date

    # paleta (rotativa) para distinguir visualmente
    # palette = [
    #     "#fecaca",  # rojo suave
    #     "#fde68a",  # amarillo suave
    #     "#bfdbfe",  # azul suave
    #     "#bbf7d0",  # verde suave
    #     "#e9d5ff",  # violeta suave
    #     "#fed7aa",  # naranjo suave
    # ]
    
    palette = [
    "rgba(239, 68, 68, 0.10)",   # rojo suave
    "rgba(244, 63, 94, 0.08)",   # rosado suave
    "rgba(251, 113, 133, 0.08)", # rosado más claro
    "rgba(185, 28, 28, 0.06)",   # rojo oscuro muy suave
    ]

    for dia, sub in df2.groupby("dia"):
        sub = sub.sort_values(["paso"]).copy()
        n = len(sub)
        if n <= 0:
            continue

        # división del día en n segmentos
        # (timeGridWeek: se verá como franjas verticales por día)
        for i, (_, r) in enumerate(sub.iterrows()):
            # color = palette[i % len(palette)]
            paso = str(r.get("paso", "")).strip()
            color = color_paso(paso)
            start = pd.Timestamp(dia) + pd.Timedelta(hours=(24 * i) / n)
            end = pd.Timestamp(dia) + pd.Timedelta(hours=(24 * (i + 1)) / n)

            paso = str(r.get("paso", "")).strip()
            paso_label = PASO_LABELS.get(paso, paso) if paso else "Misión"

            events.append({
                "title": f"Vence: {paso_label}",     # no siempre se ve, pero sirve para hover/tooltip
                "start": start.isoformat(),
                "end": end.isoformat(),
                "allDay": False,
                "display": "background",
                "color": color,
            })

    return events



import json

def build_events_calendario_para_html(df: pd.DataFrame):
    """
    Convierte tu df_f (calendario) en eventos FullCalendar, respetando:
    - color de fondo por sección (SECTION_COLORS)
    - borde por actividad (BORDER_BY_ACTIVIDAD)
    - títulos con evaluación visible
    """
    events = []

    for _, r in df.iterrows():
        fecha = r.get("fecha", pd.NaT)
        if pd.isna(fecha):
            continue

        horario = str(r.get("horario", "")).strip()
        tema = str(r.get("tema", "")).strip()
        evaluacion = str(r.get("evaluación", "")).strip()
        profs = str(r.get("profesores", "")).strip()
        obs = str(r.get("observaciones", "")).strip()
        actividad = str(r.get("actividad", "")).strip()
        seccion = str(r.get("sección", "")).strip()

        # Parse horario
        all_day = False
        if ("–" in horario) or ("-" in horario):
            try:
                h_clean = horario.replace("-", "–")
                a, b = h_clean.split("–")
                hi = pd.to_datetime(a.strip(), format="%H:%M").time()
                hf = pd.to_datetime(b.strip(), format="%H:%M").time()
                start_dt = fecha + pd.Timedelta(hours=hi.hour, minutes=hi.minute)
                end_dt = fecha + pd.Timedelta(hours=hf.hour, minutes=hf.minute)
                start = start_dt.isoformat()
                end = end_dt.isoformat()
            except Exception:
                all_day = True
                start = fecha.date().isoformat()
                end = (fecha + pd.Timedelta(days=1)).date().isoformat()
        else:
            all_day = True
            start = fecha.date().isoformat()
            end = (fecha + pd.Timedelta(days=1)).date().isoformat()

        # Título
        prefix = (EVAL_ICON.get(evaluacion, "") + " ") if evaluacion else ""
        if evaluacion:
            title = f"{prefix}{evaluacion} · {actividad}" + (f" · {tema}" if tema else "")
        else:
            title = f"{prefix}{actividad}" + (f" · {tema}" if tema else "")

        # Estilo
        bg = SECTION_COLORS.get(seccion, "rgba(148,163,184,0.14)")
        border = BORDER_BY_ACTIVIDAD.get(actividad, "#64748b")
        # Evaluación: borde más fuerte
        if evaluacion:
            border = "#b45309"

        # feriado/pausa: rojo suave
        if "Feriado" in actividad or "Pausa" in actividad:
            bg = "rgba(239,68,68,0.12)"
            border = "#991b1b"

        events.append({
            "title": title,
            "start": start,
            "end": end,
            "allDay": all_day,
            "backgroundColor": bg,
            "borderColor": border,
            "textColor": "#111827",
            "extendedProps": {
                "tipo": "clase",
                "actividad": actividad,
                "sección": seccion,
                "horario": horario if horario else ("Todo el día" if all_day else ""),
                "evaluación": evaluacion,
                "profesores": profs,
                "observaciones": obs,
                "tema": tema,
            }
        })

    return events


def build_events_misiones_allday_para_html(df_misiones: pd.DataFrame):
    """
    Misiones como ALL-DAY (arriba), apiladas (stack) y con texto completo.
    """
    events = []
    if df_misiones.empty:
        return events

    df2 = df_misiones.copy()
    df2["fecha_limite"] = pd.to_datetime(df2.get("fecha_limite", pd.NaT), errors="coerce")
    df2 = df2.dropna(subset=["fecha_limite"]).copy()

    # Orden por día y por paso
    def rank_paso(p):
        p = str(p).strip()
        return ORDEN_PASOS.index(p) if p in ORDEN_PASOS else 999

    df2["_rank"] = df2["paso"].apply(rank_paso)
    df2 = df2.sort_values(["fecha_limite", "_rank", "evento", "sección"]).reset_index(drop=True)

    for _, r in df2.iterrows():
        fecha = r.get("fecha_limite", pd.NaT)
        if pd.isna(fecha):
            continue

        evento = str(r.get("evento", "")).strip()
        paso = str(r.get("paso", "")).strip()
        paso_label = PASO_LABELS.get(paso, paso)
        seccion = str(r.get("sección", "")).strip()
        responsables = str(r.get("responsables", "")).strip()
        detalle = str(r.get("detalle", "")).strip()
        estado = str(r.get("estado", "Pendiente")).strip()

        # Título EXPLICATIVO y largo (all-day lo permite mejor)
        title = f"🚩 Vence: {paso_label}"
        if evento:
            title += f" — {evento}"
        if seccion:
            title += f" — {seccion}"

        # Observaciones para modal
        obs = " | ".join([x for x in [detalle, f"Estado: {estado}" if estado else ""] if x])

        # Estilo misión: rojizo TRANSPARENTE (no fuerte)
        bg = "rgba(239, 68, 68, 0.10)"
        border = "#991b1b"
        text = "#7f1d1d"

        events.append({
            "title": title,
            "start": fecha.date().isoformat(),
            "end": (fecha + pd.Timedelta(days=1)).date().isoformat(),
            "allDay": True,
            "backgroundColor": bg,
            "borderColor": border,
            "textColor": text,
            "extendedProps": {
                "tipo": "mision",
                "actividad": "Misión",
                "sección": seccion,
                "horario": "Todo el día",
                "evaluación": paso_label,
                "profesores": responsables,
                "observaciones": obs,
                "tema": title,
            }
        })

    return events


def render_fullcalendar_html_allday_stack(events, initial_date, tz="America/Santiago", height_px=780):
    """
    FullCalendar embebido con:
    - all-day expandible (misiones arriba)
    - stack vertical (una encima de otra)
    - NO solapamiento raro
    - wrap de texto + auto-fit simple
    """
    events_json = json.dumps(events, ensure_ascii=False)

    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.css" rel="stylesheet"/>
  <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js"></script>

  <style>
    html, body {{
      margin:0; padding:0;
      font-family: Arial, sans-serif;
      background: white;
    }}
    #calendar {{ padding: 0 6px; }}

    /* Bordes grilla más visibles */
    .fc .fc-scrollgrid, .fc .fc-scrollgrid td, .fc .fc-scrollgrid th {{
      border-width: 2px !important;
      border-color: rgba(0,0,0,0.22) !important;
    }}

    /* Eventos: borde más grueso */
    .fc .fc-event {{
      border-width: 3px !important;
      border-style: solid !important;
      border-radius: 10px !important;
    }}

    /* Texto WRAP real */
    .fc .fc-event-title {{
      white-space: normal !important;
      font-size: 13px !important;
      line-height: 1.15 !important;
      font-weight: 700 !important;
    }}
    .fc .fc-event-main {{
      padding: 6px 10px !important;
    }}

    /* ====== all-day: expandible y alto ====== */
    .fc .fc-timegrid-allday {{
      min-height: 180px !important;  /* base grande */
    }}

    /* En all-day, que la fila crezca en vez de cortar */
    .fc .fc-timegrid-axis-frame,
    .fc .fc-timegrid-col-frame {{
      overflow: visible !important;
    }}

    /* Evita que se escape texto a otra columna */
    .fc .fc-timegrid-col-frame {{
      overflow: hidden !important;
    }}

    /* Subir un poco el alto de slots */
    .fc .fc-timegrid-slot {{
      height: 2.0em !important;
    }}

    /* ===== Modal simple ===== */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.35);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 9999;
    }}
    .modal {{
      width: min(720px, 92vw);
      background: white;
      border-radius: 14px;
      padding: 16px;
      box-shadow: 0 12px 35px rgba(0,0,0,0.25);
    }}
    .modal h3 {{ margin: 0 0 10px 0; font-size: 18px; }}
    .row {{ margin: 6px 0; font-size: 14px; }}
    .label {{ font-weight: 800; }}
    .close {{
      float: right; cursor: pointer;
      padding: 6px 10px;
      border-radius: 10px;
      background: #f3f4f6;
      font-weight: 800;
    }}
    .close:hover {{ background: #e5e7eb; }}
  </style>
</head>

<body>
  <div id="calendar"></div>

  <div class="modal-overlay" id="modalOverlay">
    <div class="modal">
      <div class="close" id="modalClose">Cerrar ✕</div>
      <h3 id="mTitle"></h3>
      <div class="row"><span class="label">Actividad:</span> <span id="mActividad"></span></div>
      <div class="row"><span class="label">Sección:</span> <span id="mSeccion"></span></div>
      <div class="row"><span class="label">Horario:</span> <span id="mHorario"></span></div>
      <div class="row"><span class="label">Evaluación/Paso:</span> <span id="mEval"></span></div>
      <div class="row"><span class="label">Profesores:</span> <span id="mProf"></span></div>
      <div class="row"><span class="label">Observaciones:</span> <span id="mObs"></span></div>
    </div>
  </div>

  <script>
    const events = {events_json};

    const overlay = document.getElementById('modalOverlay');
    const closeBtn = document.getElementById('modalClose');

    function openModal(info) {{
      const p = info.event.extendedProps || {{}};
      document.getElementById('mTitle').textContent = info.event.title || '';
      document.getElementById('mActividad').textContent = p.actividad || '';
      document.getElementById('mSeccion').textContent = p['sección'] || p.sección || '';
      document.getElementById('mHorario').textContent = p.horario || '';
      document.getElementById('mEval').textContent = p['evaluación'] || p.evaluación || '';
      document.getElementById('mProf').textContent = p.profesores || '';
      document.getElementById('mObs').textContent = p.observaciones || '';
      overlay.style.display = 'flex';
    }}

    function closeModal() {{
      overlay.style.display = 'none';
    }}

    closeBtn.addEventListener('click', closeModal);
    overlay.addEventListener('click', (e) => {{
      if (e.target === overlay) closeModal();
    }});

    document.addEventListener('DOMContentLoaded', function() {{
      const calendarEl = document.getElementById('calendar');

      const calendar = new FullCalendar.Calendar(calendarEl, {{
        timeZone: {json.dumps(tz)},
        initialView: 'timeGridWeek',
        initialDate: {json.dumps(initial_date)},
        height: {height_px},
        nowIndicator: true,

        headerToolbar: {{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,listWeek'
        }},

        slotMinTime: '08:00:00',
        slotMaxTime: '21:00:00',
        expandRows: true,
        stickyHeaderDates: true,
        weekNumbers: true,
        allDaySlot: true,
        
        /* 👇👇 FIX eventos simultáneos */
        slotEventOverlap: false,
        eventOverlap: false,
        eventMaxStack: 50,

        dayMaxEvents: false,
        dayMaxEventRows: false,
        eventDisplay: "block",

        /* ====== clave para all-day apilado ====== */
        dayMaxEvents: false,
        dayMaxEventRows: false,

        /* IMPORTANTÍSIMO: en all-day, NO “inline”, sino “block” */
        eventDisplay: 'block',

        events: events,

        eventClick: function(info) {{
          openModal(info);
        }},

        eventDidMount: function(arg) {{
          // Solo para asegurar wrap en all-day
          const titleEl = arg.el.querySelector('.fc-event-title');
          if (titleEl) {{
            titleEl.style.whiteSpace = 'normal';
          }}
        }},
      }});

      calendar.render();
    }});
  </script>
</body>
</html>
"""



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

# st.markdown("""
# <style>
# div.stButton > button {
#     min-height: 70px;
#     font-size: 22px;
#     font-weight: 700;
#     border-radius: 14px;
# }
# </style>
# """, unsafe_allow_html=True)

# st.markdown("""
# <style>
# /* Permite que el título del evento haga wrap (no se corte con ...). */
# .fc .fc-event-title, 
# .fc .fc-event-title-container,
# .fc .fc-event-title-wrap {
#   white-space: normal !important;
# }

# /* Aumenta altura de la fila all-day para que quepan títulos */
# .fc .fc-timegrid-axis-cushion,
# .fc .fc-timegrid-slot-label-cushion {
#   white-space: nowrap;
# }
# .fc .fc-timegrid-event-harness, 
# .fc .fc-daygrid-event-harness {
#   margin-top: 2px;
# }

# /* En all-day, evita que quede ultra angosto */
# .fc .fc-timegrid-event .fc-event-main {
#   padding: 2px 6px;
# }
# </style>
# """, unsafe_allow_html=True)



# st.markdown("""
# <style>
# /* Más alto el área all-day en timeGridWeek */
# .fc .fc-timegrid-axis-frame,
# .fc .fc-timegrid-col-frame {
#   min-height: 120px;
# }

# /* Eventos: fuente un poco más chica y wrap real */
# .fc .fc-event-title {
#   font-size: 12px !important;
#   line-height: 1.15 !important;
#   white-space: normal !important;
# }

# /* All-day: que no quede ultra apretado */
# .fc .fc-timegrid-event-harness-inset .fc-event-main {
#   padding: 2px 6px !important;
# }
# </style>
# """, unsafe_allow_html=True)

st.markdown("""
<style>
/* =========================
   ENFOQUE 3: MÁS ESPACIO Y TEXTO
   ========================= */

/* Que el título NO se corte y tenga más tamaño/alto */
.fc .fc-event-title,
.fc .fc-event-title-container,
.fc .fc-event-title-wrap {
  white-space: normal !important;
  overflow: visible !important;
}

/* Más padding para que se lea mejor */
.fc .fc-event-main {
  padding: 4px 8px !important;
}

/* Aumentar altura mínima de los eventos (hace que quepa más texto) */
.fc .fc-timegrid-event,
.fc .fc-daygrid-event {
  min-height: 72px !important;
}

/* Aumentar tamaño de fuente (puedes ajustar 13/14) */
.fc .fc-event-title {
  font-size: 14px !important;
  line-height: 1.2 !important;
  font-weight: 700 !important;
}

/* Aumentar el alto de las filas horarias para que entren más eventos */
.fc .fc-timegrid-slot {
  height: 2.2em !important;   /* sube el “zoom vertical” */
}

/* Aumentar el área all-day (donde caen misiones si son allDay) */
.fc .fc-timegrid-allday {
  min-height: 140px !important;
}

/* =========================
   FIX SOLAPAMIENTO (TU IMAGEN)
   ========================= */

/* Background events SIEMPRE detrás */
.fc .fc-bg-event {
  z-index: 1 !important;
  opacity: 0.35 !important; /* fondo suave */
}

/* Eventos normales por encima del fondo */
.fc .fc-event {
  z-index: 3 !important;
  position: relative !important;
}

/* Evita que el contenido del evento se “escape” y se dibuje encima de otra columna */
.fc .fc-timegrid-event .fc-event-main,
.fc .fc-timegrid-event .fc-event-main-frame {
  overflow: hidden !important;
}

/* El contenedor de cada columna: que recorte lo que se salga */
.fc .fc-timegrid-col-frame {
  overflow: hidden !important;
}

/* =========================
   BORDES MÁS GRUESOS
   ========================= */

/* Bordes de los eventos (tarjetas) más gruesos */
.fc .fc-event {
  border-width: 3px !important;
}

/* Bordes de la grilla también más visibles */
.fc .fc-timegrid-slot,
.fc .fc-timegrid-axis,
.fc .fc-timegrid-col,
.fc .fc-scrollgrid,
.fc .fc-scrollgrid td,
.fc .fc-scrollgrid th {
  border-width: 2px !important;
  border-color: rgba(0,0,0,0.25) !important;
}

/* Línea del “ahora” (roja) más gruesa */
.fc .fc-timegrid-now-indicator-line {
  border-width: 3px !important;
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

# b1, b2, b3 = st.columns(3)

# with b1:
#     if st.button("🧮 Fokito", use_container_width=True):
#         st.session_state.curso_seleccionado = "fokito"

# with b2:
#     if st.button("🩺 Tecnología Médica", use_container_width=True):
#         st.session_state.curso_seleccionado = "tecnologia_medica"

# with b3:
#     if st.button("🏥 Medicina", use_container_width=True):
#         st.session_state.curso_seleccionado = "medicina"

b1, b2, b3, b4 = st.columns(4)

with b1:
    if st.button("🧮 Fokito", use_container_width=True):
        st.session_state.curso_seleccionado = "fokito"

with b2:
    if st.button("🩺 Tecnología Médica", use_container_width=True):
        st.session_state.curso_seleccionado = "tecnologia_medica"

with b3:
    if st.button("🏥 Medicina", use_container_width=True):
        st.session_state.curso_seleccionado = "medicina"

with b4:
    if st.button("🍇 Enobnu", use_container_width=True):
        st.session_state.curso_seleccionado = "enobnu"

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
# with tab1:
#     if "nav_semana" not in st.session_state:
#         st.session_state.nav_semana = 1

#     semana_sel = st.session_state.nav_semana
#     sec_selected = {s for s, ok in st.session_state.sel_secciones.items() if ok}
#     prof_selected = {p for p, ok in st.session_state.sel_profes.items() if ok}

#     df_f = df[df["sección"].isin(sec_selected)].copy()

#     if all_prof_codes:
#         df_f = df_f[
#             df_f["profesores"].apply(
#                 lambda x: row_has_prof(x, prof_selected) if prof_selected else True
#             )
#         ].copy()

#     fechas_semana = df[df["semana"] == semana_sel]["fecha"]
#     if not fechas_semana.empty:
#         initial_date = fechas_semana.min().strftime("%Y-%m-%d")
#     else:
#         min_global = df["fecha"].min()
#         initial_date = (min_global + pd.Timedelta(days=7 * (semana_sel - 1))).strftime("%Y-%m-%d")

#     # events_cal = df_calendario_a_fullcalendar_events(df_f)
#     # events_mis = df_misiones_a_fullcalendar_events(df_misiones)
#     # events = events_cal + events_mis
    
#     events_cal = df_calendario_a_fullcalendar_events(df_f)
#     events_mis = df_misiones_a_fullcalendar_events(df_misiones)
#     events_mis_bg = df_misiones_deadlines_background_events(df_misiones)

#     events = events_cal + events_mis_bg + events_mis

#     calendar_options = {
#         "initialView": "timeGridWeek",
#         "initialDate": initial_date,
#         "headerToolbar": {
#             "left": "prev,next today",
#             "center": "title",
#             "right": "dayGridMonth,timeGridWeek,listWeek",
#         },
#         "height": 750,
#         "eventMaxStack": 99,
#         "slotMinTime": "08:00:00",
#         "slotMaxTime": "21:00:00",
#         "allDaySlot": True,
#         "weekNumbers": True,
#         "eventDisplay": "block",
#         "dayMaxEventRows": False,
#         "expandRows": True,
#         "stickyHeaderDates": True,
#         "dayMaxEvents": False,
#         "eventTimeFormat": {
#             "hour": "2-digit",
#             "minute": "2-digit",
#             "meridiem": False
# },
#     }

#     state = calendar(events=events, options=calendar_options, key=f"cal_{curso_actual}_{semana_sel}")

#     if state.get("eventClick"):
#         ev = state["eventClick"]["event"]
#         props = ev.get("extendedProps", {})
#         mostrar_detalle_evento(props)

#     st.divider()

#     c_nav, c_filtros = st.columns([1, 2])

#     with c_nav:
#         st.subheader("Navegación")
#         max_sem = df["semana"].max()
#         if pd.isna(max_sem):
#             max_sem = 20
#         weeks = list(range(1, int(max_sem) + 1))

#         st.radio(
#             "Seleccionar Semana:",
#             options=weeks,
#             horizontal=True,
#             key="nav_semana"
#         )

#     with c_filtros:
#         st.subheader("Filtros")
#         fcol1, fcol2 = st.columns(2)

#         with fcol1:
#             st.caption("Secciones")
#             for s in all_secciones:
#                 st.checkbox(
#                     s,
#                     value=st.session_state.sel_secciones.get(s, True),
#                     key=f"sec_{curso_actual}_{s}"
#                 )
#                 st.session_state.sel_secciones[s] = st.session_state[f"sec_{curso_actual}_{s}"]

#         with fcol2:
#             st.caption("Profesores")
#             if not all_prof_codes:
#                 st.info("No hay profesores.")
#             for p in all_prof_codes:
#                 st.checkbox(
#                     p,
#                     value=st.session_state.sel_profes.get(p, True),
#                     key=f"prof_{curso_actual}_{p}"
#                 )
#                 st.session_state.sel_profes[p] = st.session_state[f"prof_{curso_actual}_{p}"]


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

    # initial_date: lunes de la semana seleccionada (según tus datos)
    fechas_semana = df[df["semana"] == semana_sel]["fecha"]
    if not fechas_semana.empty:
        initial_date = fechas_semana.min().strftime("%Y-%m-%d")
    else:
        min_global = df["fecha"].min()
        initial_date = (min_global + pd.Timedelta(days=7 * (semana_sel - 1))).strftime("%Y-%m-%d")

    # ====== eventos: clases/horarios + misiones ALL-DAY ======
    events_cal = build_events_calendario_para_html(df_f)
    events_mis = build_events_misiones_allday_para_html(df_misiones)

    # Si quieres que misiones siempre estén “arriba”, las ponemos primero
    events = events_mis + events_cal

    html_cal = render_fullcalendar_html_allday_stack(
        events=events,
        initial_date=initial_date,
        tz=TIMEZONE,
        height_px=1100
    )

    # Render del calendario
    components.html(html_cal, height=1160, scrolling=False)

    st.divider()

    # ====== (mantienes navegación + filtros igual) ======
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

    # ✅ NUEVO: misiones por persona/mes
    tabla_misiones_por_profesor_y_mes(df_misiones)

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