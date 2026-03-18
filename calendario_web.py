import os
import html
import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import yaml


# ============================================================
# GOOGLE SHEET: URGENTES
# ============================================================
# https://docs.google.com/spreadsheets/d/1F_-cTrLiNtYM736nWm_UquKuRWm7MNf5BDcU_I7IF4A/edit?usp=sharing
GSHEET_ID_URGENTES = "1F_-cTrLiNtYM736nWm_UquKuRWm7MNf5BDcU_I7IF4A"
GSHEET_GID_URGENTES = "0"


@st.cache_data(ttl=60)
def cargar_urgentes_google_sheet():
    url = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID_URGENTES}/export?format=csv&gid={GSHEET_GID_URGENTES}"
    df = pd.read_csv(url)

    df.columns = [str(c).strip().lower() for c in df.columns]

    for c in ["titulo", "descripcion", "responsable", "estado", "urgente", "fecha_limite"]:
        if c not in df.columns:
            df[c] = ""

    df["titulo"] = df["titulo"].fillna("").astype(str).str.strip()
    df["descripcion"] = df["descripcion"].fillna("").astype(str).str.strip()
    df["responsable"] = df["responsable"].fillna("").astype(str).str.strip()
    df["estado"] = df["estado"].fillna("").astype(str).str.strip()
    df["urgente"] = df["urgente"].fillna("").astype(str).str.strip().str.upper()
    df["fecha_limite"] = pd.to_datetime(df["fecha_limite"], errors="coerce")

    return df


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
        "carpeta": "enobnu",
        "emoji": "🍇",
    },
}


# ============================================================
# PALETA / ESTILOS
# ============================================================
PROF_PALETTE = {
    "TY": "#1f77b4",
    "IG": "#2ca02c",
    "CC": "#ff7f0e",
    "AR": "#9467bd",
    "JCS": "#8c564b",
    "MB": "#e377c2",
    "GM": "#17becf",
    "VB": "#bcbd22",
    "NV": "#d62728",
    "JM": "#7f7f7f",
    "EG": "#8c564b",
    "RL": "#6b7280",
    "DH": "#14b8a6",
    "SM": "#ef4444",
    "RM": "#f59e0b",
    "XX": "#64748b",
    "Todos": "#374151",
}

PALETA_FALLBACK = [
    "#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b",
    "#e377c2", "#17becf", "#bcbd22", "#d62728", "#14b8a6",
    "#f59e0b", "#6366f1", "#ec4899", "#22c55e", "#0ea5e9",
]

EVAL_ICON = {
    "Trabajo práctico": "📝",
    "Control": "⭐",
    "Certamen": "🧠",
    "Examen": "🎓",
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
    "Sección 1": "rgba(59, 130, 246, 0.18)",
    "Sección 2": "rgba(34, 197, 94, 0.18)",
    "Sección 3": "rgba(249, 115, 22, 0.18)",
    "Sección 4": "rgba(168, 85, 247, 0.18)",
}

BORDER_BY_ACTIVIDAD = {
    "Clase teórica": "#111827",
    "Seminario": "#2563eb",
    "Laboratorio": "#f59e0b",
    "Trabajo autónomo": "#6b7280",
    "Examen": "#111827",
    "Misión": "#991b1b",
}

PESOS_MISION_DEFAULT = {
    "pedir_preguntas": 1.0,
    "construir_control": 1.0,
    "pauta_prueba": 1.0,
    "revisar_prueba": 1.0,
    "escanear": 1.0,
    "corregir_y_notas": 1.0,
    "revisar_tp": 1.0,
    "construir_examen": 1.0,
    "pauta_examen": 1.0,
    "corregir_examen": 1.0,
    "construir_taller_AB": 1.0,
    "construir_taller_CD": 1.0,
    "corregir_taller_A": 1.0,
    "corregir_taller_B": 1.0,
    "corregir_taller_C": 1.0,
    "corregir_taller_D": 1.0,
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
    "construir_taller": "Construcción de taller",
    "construir_taller_AB": "Construcción taller versiones A y B",
    "construir_taller_CD": "Construcción taller versiones C y D",
    "corregir_taller": "Corrección de taller",
    "corregir_taller_A": "Corregir taller versión A",
    "corregir_taller_B": "Corregir taller versión B",
    "corregir_taller_C": "Corregir taller versión C",
    "corregir_taller_D": "Corregir taller versión D",
    "preparar_material_previo": "Preparar material previo",
    "grabar_video_solucion": "Grabar video solución",
    "corregir_informe_laboratorio": "Corregir informe de laboratorio",
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
    "construir_taller_AB",
    "construir_taller_CD",
    "corregir_taller_A",
    "corregir_taller_B",
    "corregir_taller_C",
    "corregir_taller_D",
    "preparar_material_previo",
    "grabar_video_solucion",
    "corregir_informe_laboratorio",
]


# ============================================================
# HELPERS GENERALES
# ============================================================
def cargar_yaml(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def cargar_urgentes(path="config/urgente.yml", curso_actual=None):
    cfg = cargar_yaml(path)
    items = cfg.get("urgentes", []) or []

    filas = []
    for x in items:
        curso = str(x.get("curso", "")).strip()
        if curso_actual and curso != curso_actual:
            continue

        filas.append({
            "id": str(x.get("id", "")).strip(),
            "curso": curso,
            "titulo": str(x.get("titulo", "")).strip(),
            "descripcion": str(x.get("descripcion", "")).strip(),
            "estado": str(x.get("estado", "pendiente")).strip().lower(),
            "prioridad": str(x.get("prioridad", "media")).strip().lower(),
        })

    return pd.DataFrame(filas)


def color_prioridad(prioridad: str) -> str:
    prioridad = str(prioridad).strip().lower()
    if prioridad == "alta":
        return "#dc2626"
    if prioridad == "media":
        return "#f59e0b"
    return "#2563eb"


def color_estado_urgente(estado: str) -> str:
    estado = str(estado).strip().lower()
    if estado == "completado":
        return "#dcfce7"
    if estado == "en_progreso":
        return "#fef3c7"
    return "#fee2e2"


def hay_urgentes_pendientes(df_urg):
    if df_urg is None or df_urg.empty:
        return False
    return (df_urg["estado"].isin(["pendiente", "en_progreso"])).any()


def render_sidebar_urgentes(df_urg: pd.DataFrame):
    if df_urg is None or df_urg.empty:
        st.sidebar.markdown("## 🚨 Misiones urgentes")
        st.sidebar.info("No hay misiones urgentes para este curso.")
        return

    pendientes = df_urg[df_urg["estado"].isin(["pendiente", "en_progreso"])].copy()
    completadas = df_urg[df_urg["estado"] == "completado"].copy()

    alerta = hay_urgentes_pendientes(df_urg)

    st.sidebar.markdown(
        """
        <style>
        @keyframes pulsoUrgente {
          0%   { box-shadow: 0 0 0 0 rgba(220,38,38,0.75); opacity: 1; }
          50%  { box-shadow: 0 0 0 10px rgba(220,38,38,0.15); opacity: 0.88; }
          100% { box-shadow: 0 0 0 0 rgba(220,38,38,0.00); opacity: 1; }
        }
        .urgente-alerta {
          animation: pulsoUrgente 1.2s infinite;
          border: 2px solid #dc2626;
          background: #fef2f2;
          border-radius: 14px;
          padding: 12px;
          margin-bottom: 14px;
        }
        .urgente-normal {
          border: 1px solid #d1d5db;
          background: #f9fafb;
          border-radius: 14px;
          padding: 12px;
          margin-bottom: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    clase = "urgente-alerta" if alerta else "urgente-normal"
    titulo = "🚨 Misiones urgentes" if alerta else "📌 Misiones urgentes"

    st.sidebar.markdown(f'<div class="{clase}"><b>{titulo}</b></div>', unsafe_allow_html=True)

    st.sidebar.caption("Se edita desde `config/urgente.yml`")

    if not pendientes.empty:
        st.sidebar.markdown("### Pendientes")
        for _, r in pendientes.iterrows():
            borde = color_prioridad(r["prioridad"])
            color_estado = color_estado_urgente(r["estado"])
            estado_txt = r["estado"].replace("_", " ").capitalize()

            st.sidebar.markdown(f"""
            <div style="
                border:1px solid #d1d5db;
                border-left:6px solid {borde};
                border-radius:12px;
                padding:10px;
                margin-bottom:10px;
                background:white;
            ">
                <div style="font-weight:800; font-size:14px; margin-bottom:4px;">
                    {escape_texto(r["titulo"])}
                </div>
                <div style="font-size:12px; color:#4b5563; margin-bottom:8px;">
                    {escape_texto(r["descripcion"])}
                </div>
                <div style="
                    display:inline-block;
                    padding:4px 8px;
                    border-radius:999px;
                    background:{color_estado};
                    font-size:11px;
                    font-weight:700;
                ">
                    {escape_texto(estado_txt)}
                </div>
            </div>
            """, unsafe_allow_html=True)

    if not completadas.empty:
        with st.sidebar.expander("Completadas", expanded=False):
            for _, r in completadas.iterrows():
                st.markdown(f"""
                <div style="
                    border:1px solid #d1d5db;
                    border-left:6px solid #16a34a;
                    border-radius:12px;
                    padding:10px;
                    margin-bottom:10px;
                    background:white;
                ">
                    <div style="font-weight:800; font-size:14px; margin-bottom:4px;">
                        {escape_texto(r["titulo"])}
                    </div>
                    <div style="font-size:12px; color:#4b5563;">
                        {escape_texto(r["descripcion"])}
                    </div>
                </div>
                """, unsafe_allow_html=True)



def color_profesor(codigo: str) -> str:
    codigo = str(codigo).strip()
    if not codigo:
        return "#6b7280"
    if codigo in PROF_PALETTE:
        return PROF_PALETTE[codigo]
    idx = sum(ord(ch) for ch in codigo) % len(PALETA_FALLBACK)
    return PALETA_FALLBACK[idx]


def split_profes(valor):
    if valor is None:
        return []
    try:
        if pd.isna(valor):
            return []
    except Exception:
        pass
    if isinstance(valor, (list, tuple)):
        return [str(x).strip() for x in valor if str(x).strip()]
    return [x.strip() for x in str(valor).split(",") if x.strip()]


def row_has_prof(row_prof, selected_set: set) -> bool:
    profs = set(split_profes(row_prof))
    if not profs:
        return False
    return len(profs.intersection(selected_set)) > 0



def render_badge_responsable(responsable: str) -> str:
    if not responsable:
        return "<span style='color:#999;'>—</span>"
    color = color_profesor(responsable)
    return f"""
    <span style="
        display:inline-block;
        padding:4px 9px;
        border-radius:999px;
        background:{color};
        color:white;
        font-size:12px;
        font-weight:700;
    ">
        {escape_texto(responsable)}
    </span>
    """


def mostrar_urgentes_sidebar():
    if not GSHEET_ID_URGENTES or GSHEET_ID_URGENTES == "F_-_-cTrLiNtYM736nWm_UquKuRWm7MNf5BDcU_I7IF4A":
        st.sidebar.info("Configura GSHEET_ID_URGENTES para ver urgentes.")
        return

    try:
        df_u = cargar_urgentes_google_sheet(GSHEET_ID_URGENTES, GSHEET_GID_URGENTES)
    except Exception as e:
        st.sidebar.error(f"No pude leer la Google Sheet: {e}")
        return

    pendientes = df_u[
        (df_u["urgente"] == "SI") &
        (~df_u["estado"].str.lower().isin(["completado", "completada", "ok", "done"]))
    ].copy()

    if pendientes.empty:
        st.sidebar.success("No hay urgentes pendientes.")
        return

    st.sidebar.markdown("## 🚨 Misiones urgentes")

    st.sidebar.markdown("""
    <style>
    @keyframes alertaUrgente {
      0% { box-shadow: 0 0 0 0 rgba(220,38,38,0.55); }
      70% { box-shadow: 0 0 0 10px rgba(220,38,38,0); }
      100% { box-shadow: 0 0 0 0 rgba(220,38,38,0); }
    }
    .bloque-urgente {
      border: 2px solid #dc2626;
      border-left: 8px solid #991b1b;
      border-radius: 12px;
      padding: 10px 12px;
      margin-bottom: 10px;
      background: #fef2f2;
      animation: alertaUrgente 1.5s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

    for _, r in pendientes.sort_values("fecha_limite").iterrows():
        fecha_txt = r["fecha_limite"].strftime("%d/%m/%Y") if pd.notna(r["fecha_limite"]) else "—"

        st.sidebar.markdown(f"""
        <div class="bloque-urgente">
            <div style="font-weight:800; margin-bottom:6px;">{escape_texto(r["titulo"])}</div>
            <div style="font-size:13px; margin-bottom:6px;">{escape_texto(r["descripcion"])}</div>
            <div style="font-size:12px; margin-bottom:6px;"><b>Fecha límite:</b> {fecha_txt}</div>
            <div style="font-size:12px; margin-bottom:6px;"><b>Estado:</b> {escape_texto(r["estado"] or "Pendiente")}</div>
            <div>{render_badge_responsable(r["responsable"])}</div>
        </div>
        """, unsafe_allow_html=True)


def escape_texto(x):
    if x is None:
        return ""
    try:
        if pd.isna(x):
            return ""
    except Exception:
        pass
    return html.escape(str(x))


def obtener_paths_curso(curso_key: str):
    carpeta = CURSOS[curso_key]["carpeta"]
    base_dir = os.path.join(DATA_DIR, carpeta)
    return {
        "base_dir": base_dir,
        "excel_calendario": os.path.join(base_dir, "calendario.xlsx"),
        "excel_misiones": os.path.join(base_dir, "misiones.xlsx"),
    }


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df2 = df.copy()
    rename_map = {}

    for col in df2.columns:
        base = str(col).strip()

        if base.lower() == "seccion":
            rename_map[col] = "sección"
        elif base.lower() == "evaluacion":
            rename_map[col] = "evaluación"
        elif base.lower() == "dia":
            rename_map[col] = "día"
        else:
            rename_map[col] = base

    df2 = df2.rename(columns=rename_map)
    return df2


def asegurar_columnas(df: pd.DataFrame, cols, fill=""):
    df2 = df.copy()
    for c in cols:
        if c not in df2.columns:
            df2[c] = fill
    return df2


def semana_actual_desde_df(df):
    if df.empty or "fecha" not in df.columns or "semana" not in df.columns:
        return 1

    df2 = df.copy()
    df2["fecha"] = pd.to_datetime(df2["fecha"], errors="coerce")
    df2["semana"] = pd.to_numeric(df2["semana"], errors="coerce")
    df2 = df2.dropna(subset=["fecha", "semana"]).copy()

    if df2.empty:
        return 1

    hoy = pd.Timestamp.now(tz=TIMEZONE).tz_localize(None).normalize()

    resumen = (
        df2.groupby("semana", as_index=False)
        .agg(fecha_min=("fecha", "min"), fecha_max=("fecha", "max"))
        .sort_values("semana")
        .reset_index(drop=True)
    )

    mask = (
        (resumen["fecha_min"].dt.normalize() <= hoy) &
        (resumen["fecha_max"].dt.normalize() >= hoy)
    )
    if mask.any():
        return int(resumen.loc[mask, "semana"].iloc[0])

    if hoy < resumen["fecha_min"].min().normalize():
        return int(resumen["semana"].min())

    if hoy > resumen["fecha_max"].max().normalize():
        return int(resumen["semana"].max())

    futuras = resumen[resumen["fecha_min"].dt.normalize() > hoy]
    if not futuras.empty:
        return int(futuras["semana"].iloc[0])

    return int(resumen["semana"].max())


# ============================================================
# CARGA DE DATOS
# ============================================================
def cargar_datos_calendario_excel(excel_calendario_path):
    if not os.path.exists(excel_calendario_path):
        st.error(f"⚠️ No se encontró el archivo: {excel_calendario_path}")
        st.stop()

    df = pd.read_excel(excel_calendario_path, sheet_name="Calendario")
    df = normalizar_columnas(df)
    df = asegurar_columnas(
        df,
        ["fecha", "semana", "horario", "sección", "actividad", "tema", "evaluación", "profesores", "observaciones"]
    )

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["semana"] = pd.to_numeric(df["semana"], errors="coerce")

    cols_str = ["horario", "sección", "actividad", "tema", "evaluación", "profesores", "observaciones"]
    for c in cols_str:
        df[c] = df[c].fillna("").astype(str).str.strip()

    return df


def cargar_sheet_excel(path, sheet):
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        df = pd.read_excel(path, sheet_name=sheet)
        return normalizar_columnas(df)
    except Exception:
        return pd.DataFrame()


def cargar_datos_misiones_base(excel_misiones_path):
    df = cargar_sheet_excel(excel_misiones_path, "Misiones")
    if df.empty:
        return df

    df = asegurar_columnas(
        df,
        ["fecha_limite", "fecha_evento", "evento", "tipo_evento", "paso", "sección", "responsables", "detalle", "estado"]
    )

    for c in ["fecha_limite", "fecha_evento"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")

    for c in ["evento", "tipo_evento", "paso", "sección", "responsables", "detalle", "estado"]:
        df[c] = df[c].fillna("").astype(str).str.strip()

    return df



# ============================================================
# FILTROS
# ============================================================
def inicializar_widgets_filtros(curso_actual, all_secciones, all_prof_codes):
    if "sel_secciones" not in st.session_state:
        st.session_state.sel_secciones = {s: True for s in all_secciones}
    if "sel_profes" not in st.session_state:
        st.session_state.sel_profes = {p: True for p in all_prof_codes}

    for s in all_secciones:
        key = f"sec_{curso_actual}_{s}"
        if key not in st.session_state:
            st.session_state[key] = st.session_state.sel_secciones.get(s, True)

    for p in all_prof_codes:
        key = f"prof_{curso_actual}_{p}"
        if key not in st.session_state:
            st.session_state[key] = st.session_state.sel_profes.get(p, True)


def sincronizar_filtros_desde_widgets(curso_actual, all_secciones, all_prof_codes):
    st.session_state.sel_secciones = {
        s: bool(st.session_state.get(f"sec_{curso_actual}_{s}", True))
        for s in all_secciones
    }
    st.session_state.sel_profes = {
        p: bool(st.session_state.get(f"prof_{curso_actual}_{p}", True))
        for p in all_prof_codes
    }


# ============================================================
# MISIONES / ESTADÍSTICAS
# ============================================================
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


def es_mision_laboratorio(row) -> bool:
    tipo_evento = str(row.get("tipo_evento", "")).strip().lower()
    evento = str(row.get("evento", "")).strip().lower()
    paso = str(row.get("paso", "")).strip().lower()
    detalle = str(row.get("detalle", "")).strip().lower()

    return (
        "laboratorio" in tipo_evento
        or "informe laboratorio" in tipo_evento
        or "laboratorio" in evento
        or "informe laboratorio" in evento
        or paso == "corregir_informe_laboratorio"
        or "laboratorio" in detalle
    )


def construir_tabla_carga_seminario(df_cal, df_misiones, pesos=None):
    if pesos is None:
        pesos = {}

    df_sem1 = df_cal.copy()
    df_sem1["semana"] = pd.to_numeric(df_sem1["semana"], errors="coerce")
    df_sem1 = df_sem1[
        (df_sem1["actividad"].astype(str).str.strip() == "Seminario") &
        (df_sem1["semana"] == 1)
    ].copy()

    conteo_cupos = {}
    for _, r in df_sem1.iterrows():
        for p in split_profes(r.get("profesores", "")):
            conteo_cupos[p] = conteo_cupos.get(p, 0) + 1

    clases_estimadas = {p: n * 17 for p, n in conteo_cupos.items()}
    profes_seminario = set(conteo_cupos.keys())

    df_mis = df_misiones.copy()
    if df_mis.empty:
        return pd.DataFrame(columns=[
            "profesor", "cupos_semana_1", "clases_estimadas", "misiones_ponderadas", "ratio"
        ])

    df_mis = asegurar_columnas(df_mis, ["tipo_evento", "evento", "paso", "responsables", "detalle"])
    for c in ["tipo_evento", "evento", "paso", "responsables", "detalle"]:
        df_mis[c] = df_mis[c].fillna("").astype(str)

    df_mis = df_mis[~df_mis.apply(es_mision_laboratorio, axis=1)].copy()

    carga = {}
    for _, r in df_mis.iterrows():
        paso = str(r.get("paso", "")).strip()
        peso = float(pesos.get(paso, 1.0))
        for p in split_profes(r.get("responsables", "")):
            if p not in profes_seminario:
                continue
            carga[p] = carga.get(p, 0.0) + peso

    filas = []
    for p in sorted(profes_seminario):
        cupos = conteo_cupos.get(p, 0)
        clases = clases_estimadas.get(p, 0)
        mis = carga.get(p, 0.0)
        ratio = (mis / clases) if clases > 0 else 0.0
        filas.append({
            "profesor": p,
            "cupos_semana_1": cupos,
            "clases_estimadas": clases,
            "misiones_ponderadas": mis,
            "ratio": ratio,
        })

    return pd.DataFrame(filas).sort_values(
        ["ratio", "misiones_ponderadas", "profesor"],
        ascending=[False, False, True]
    ).reset_index(drop=True)


def render_navegacion_semanal(df, curso_actual):
    st.caption("Navegación semanal")

    max_sem = df["semana"].max()
    if pd.isna(max_sem):
        max_sem = 20
    max_sem = int(max_sem)

    nav1, nav2 = st.columns(2)

    with nav1:
        if st.button("⬅️ Semana anterior", use_container_width=True, key=f"prev_week_{curso_actual}_{st.session_state.get('nav_render_pos', 'x')}"):
            if st.session_state.nav_semana > 1:
                st.session_state.nav_semana -= 1
            st.rerun()

    with nav2:
        if st.button("Semana siguiente ➡️", use_container_width=True, key=f"next_week_{curso_actual}_{st.session_state.get('nav_render_pos', 'x')}"):
            if st.session_state.nav_semana < max_sem:
                st.session_state.nav_semana += 1
            st.rerun()

    semana_nueva = st.radio(
        "Semana",
        options=list(range(1, max_sem + 1)),
        horizontal=True,
        index=max(0, min(st.session_state.nav_semana - 1, max_sem - 1)),
        key=f"radio_semana_{curso_actual}_{st.session_state.get('nav_render_pos', 'x')}"
    )

    if semana_nueva != st.session_state.nav_semana:
        st.session_state.nav_semana = semana_nueva
        st.rerun()

# ============================================================
# TABLA MISIONES POR PERSONA
# ============================================================
def tabla_misiones_por_profesor_y_mes(df_misiones: pd.DataFrame):
    if df_misiones.empty:
        st.info("No hay misiones para mostrar.")
        return

    df2 = df_misiones.copy()
    df2["fecha_limite"] = pd.to_datetime(df2.get("fecha_limite", pd.NaT), errors="coerce")
    df2 = df2.dropna(subset=["fecha_limite"]).copy()

    for c in ["evento", "paso", "sección", "responsables", "detalle", "estado"]:
        if c not in df2.columns:
            df2[c] = ""
        df2[c] = df2[c].fillna("").astype(str)

    profs = set()
    for s in df2["responsables"].dropna().unique():
        for p in split_profes(s):
            profs.add(p.strip())

    profs = sorted([p for p in profs if p])

    if not profs:
        st.info("No hay responsables en el archivo de misiones.")
        return

    st.markdown("### 👤 Misiones por persona")
    tabs = st.tabs(profs)

    for i, prof in enumerate(profs):
        with tabs[i]:
            dfp = df2[df2["responsables"].apply(lambda x: prof in split_profes(x))].copy()

            if dfp.empty:
                st.info(f"{prof}: no tiene misiones asignadas.")
                continue

            dfp = dfp.sort_values(["fecha_limite", "evento", "paso", "sección"]).copy()

            primer_mes = dfp["fecha_limite"].min().to_period("M").to_timestamp()
            ultimo_mes = dfp["fecha_limite"].max().to_period("M").to_timestamp()

            clave_offset = f"offset_mes_{prof}"
            if clave_offset not in st.session_state:
                st.session_state[clave_offset] = 0

            mes_actual = pd.Timestamp.today().to_period("M").to_timestamp()
            mes_base = max(primer_mes, mes_actual)
            mes_sel = (mes_base + pd.DateOffset(months=st.session_state[clave_offset])).to_period("M").to_timestamp()

            if mes_sel < primer_mes:
                mes_sel = primer_mes
            if mes_sel > ultimo_mes:
                mes_sel = ultimo_mes

            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                if st.button("⬅️", key=f"prev_mes_{prof}", use_container_width=True):
                    st.session_state[clave_offset] -= 1
                    st.rerun()

            with c2:
                st.markdown(
                    f"<div style='text-align:center; font-weight:700; font-size:18px; margin-top:6px;'>"
                    f"{mes_sel.strftime('%B %Y').capitalize()}</div>",
                    unsafe_allow_html=True
                )

            with c3:
                if st.button("➡️", key=f"next_mes_{prof}", use_container_width=True):
                    st.session_state[clave_offset] += 1
                    st.rerun()

            inicio_mes = mes_sel
            fin_mes = mes_sel + pd.DateOffset(months=1)

            dfm = dfp[(dfp["fecha_limite"] >= inicio_mes) & (dfp["fecha_limite"] < fin_mes)].copy()

            if dfm.empty:
                st.info("No hay misiones para este mes.")
                continue

            st.markdown("---")

            for _, r in dfm.iterrows():
                fecha_limite = r["fecha_limite"].strftime("%d/%m/%Y") if pd.notna(r["fecha_limite"]) else "—"
                evento = str(r.get("evento", "")).strip()
                paso = PASO_LABELS.get(str(r.get("paso", "")).strip(), str(r.get("paso", "")).strip())
                seccion = str(r.get("sección", "")).strip()
                detalle = str(r.get("detalle", "")).strip()
                estado = str(r.get("estado", "")).strip()

                color_estado = "#dcfce7" if estado.lower() in ["completado", "completada", "listo", "ok", "done"] else "#fee2e2"

                st.markdown(f"""
                <div style="
                    border:1px solid #d1d5db;
                    border-left:6px solid #2563eb;
                    border-radius:10px;
                    padding:12px 14px;
                    margin-bottom:10px;
                    background:white;
                ">
                    <div style="font-weight:800; font-size:15px;">{paso}</div>
                    <div style="margin-top:4px; color:#374151;"><b>Vence:</b> {fecha_limite}</div>
                    <div style="color:#374151;"><b>Evaluación:</b> {evento or '—'}</div>
                    <div style="color:#374151;"><b>Sección:</b> {seccion or '—'}</div>
                    <div style="color:#374151;"><b>Detalle:</b> {detalle or '—'}</div>
                    <div style="
                        display:inline-block;
                        margin-top:8px;
                        padding:4px 10px;
                        border-radius:999px;
                        background:{color_estado};
                        font-weight:700;
                        font-size:12px;
                    ">
                        {estado or 'Pendiente'}
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# TAB 2: TABLA HORARIOS
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
                estilos[i] += " font-style: italic;"

    return estilos


def estilo_tabla_calendario(df_tabla: pd.DataFrame):
    df2 = df_tabla.copy()
    if "fecha" in df2.columns:
        df2["fecha"] = pd.to_datetime(df2["fecha"], errors="coerce")

    styler = (
        df2.style
        .apply(color_fila_calendario, axis=1)
        .format({"fecha": lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else ""})
        .set_properties(**{"text-align": "left", "font-size": "13px", "border-color": "#d1d5db"})
        .set_properties(subset=[c for c in ["fecha", "semana", "horario"] if c in df2.columns], **{"text-align": "center"})
        .set_properties(subset=[c for c in ["evaluación"] if c in df2.columns], **{"text-align": "center"})
    )
    return styler


def tabla_resumen_colores():
    st.markdown("""
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
    """, unsafe_allow_html=True)


# ============================================================
# RENDER HTML MISIONES
# ============================================================
def render_badges_profes(responsables: str) -> str:
    lista = split_profes(responsables)
    if not lista:
        return "<span style='color:#999;'>—</span>"

    badges = []
    for p in lista:
        color = color_profesor(p)
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
    df2 = asegurar_columnas(df2, ["evento", "paso", "sección", "responsables", "detalle"])

    for c in ["evento", "paso", "sección", "responsables", "detalle"]:
        df2[c] = df2[c].fillna("").astype(str)

    df2["_orden_paso"] = df2["paso"].apply(lambda x: ORDEN_PASOS.index(x) if x in ORDEN_PASOS else 999)

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

        celdas = ""
        for sec in secciones_presentes:
            val = str(row.get(sec, "")).strip()
            contenido = render_badges_profes(val) if val else "<span style='color:#bbb;'>—</span>"
            celdas += f"""
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
            {celdas}
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
    df2 = asegurar_columnas(df2, ["evento", "paso", "sección", "detalle", "responsables", "estado", "fecha_limite", "fecha_evento"])

    df2["fecha_limite"] = pd.to_datetime(df2["fecha_limite"], errors="coerce")
    df2["fecha_evento"] = pd.to_datetime(df2["fecha_evento"], errors="coerce")
    df2["_orden"] = df2["paso"].apply(lambda x: ORDEN_PASOS.index(x) if x in ORDEN_PASOS else 999)

    df2 = df2.sort_values(["evento", "_orden", "sección", "fecha_limite"]).copy()

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
# EVENTOS CALENDARIO
# ============================================================
def build_events_calendario_para_html(df: pd.DataFrame):
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

        prefix = (EVAL_ICON.get(evaluacion, "") + " ") if evaluacion else ""

        partes_titulo = []
        if evaluacion:
            partes_titulo.append(f"{prefix}{evaluacion}")
            if actividad:
                partes_titulo.append(actividad)
        else:
            if actividad:
                partes_titulo.append(f"{prefix}{actividad}".strip())

        if tema:
            partes_titulo.append(tema)
        if seccion:
            partes_titulo.append(seccion)
        if profs:
            partes_titulo.append(profs)

        title = " · ".join([x for x in partes_titulo if x])

        bg = SECTION_COLORS.get(seccion, "rgba(148,163,184,0.14)")
        border = BORDER_BY_ACTIVIDAD.get(actividad, "#64748b")

        if evaluacion:
            border = "#b45309"

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
    events = []
    if df_misiones.empty:
        return events

    df2 = df_misiones.copy()
    df2 = asegurar_columnas(
        df2,
        ["fecha_limite", "evento", "paso", "sección", "responsables", "detalle", "estado"]
    )

    df2["fecha_limite"] = pd.to_datetime(df2["fecha_limite"], errors="coerce")
    df2 = df2.dropna(subset=["fecha_limite"]).copy()

    if df2.empty:
        return events

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

        title = f"🚩 {paso_label}"
        if evento:
            title += f" — {evento}"
        if seccion:
            title += f" — {seccion}"

        obs = " | ".join([
            x for x in [
                detalle,
                f"Responsables: {responsables}" if responsables else "",
                f"Estado: {estado}" if estado else ""
            ] if x
        ])

        events.append({
            "title": title,
            "start": fecha.date().isoformat(),
            "end": (fecha + pd.Timedelta(days=1)).date().isoformat(),
            "allDay": True,
            "backgroundColor": "#fee2e2",
            "borderColor": "#dc2626",
            "textColor": "#7f1d1d",
            "classNames": ["evento-mision"],
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


def render_misiones_semana_html(df_mis_sem: pd.DataFrame, fechas_semana_ordenadas):
    """
    Render robusto de misiones por semana, en columnas por día.
    Agrega un cuadrado rojo visual en cada misión.
    """
    if df_mis_sem.empty:
        return """
        <div style="padding:12px; border:1px solid #e5e7eb; border-radius:12px; background:#fafafa;">
            No hay misiones para esta semana con los filtros seleccionados.
        </div>
        """

    df2 = df_mis_sem.copy()
    df2 = asegurar_columnas(
        df2,
        ["fecha_limite", "evento", "paso", "sección", "responsables", "detalle", "estado"]
    )

    df2["fecha_limite"] = pd.to_datetime(df2["fecha_limite"], errors="coerce")
    df2 = df2.dropna(subset=["fecha_limite"]).copy()

    if df2.empty:
        return """
        <div style="padding:12px; border:1px solid #e5e7eb; border-radius:12px; background:#fafafa;">
            No hay misiones válidas para esta semana.
        </div>
        """

    def rank_paso(p):
        p = str(p).strip()
        return ORDEN_PASOS.index(p) if p in ORDEN_PASOS else 999

    df2["_rank"] = df2["paso"].apply(rank_paso)
    df2["fecha_dia"] = df2["fecha_limite"].dt.date

    dias_es = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo",
    }

    columnas_html = []

    for fecha in fechas_semana_ordenadas:
        fecha_ts = pd.Timestamp(fecha)
        fecha_date = fecha_ts.date()

        sub = df2[df2["fecha_dia"] == fecha_date].copy()
        sub = sub.sort_values(["_rank", "evento", "sección"]).reset_index(drop=True)

        tarjetas = ""
        if sub.empty:
            tarjetas = """
            <div style="
                border:1px dashed #d1d5db;
                border-radius:10px;
                padding:10px;
                color:#9ca3af;
                background:#fcfcfc;
                font-size:13px;
            ">
                Sin misiones
            </div>
            """
        else:
            for _, r in sub.iterrows():
                paso = str(r.get("paso", "")).strip()
                paso_label = PASO_LABELS.get(paso, paso if paso else "—")
                evento = escape_texto(r.get("evento", ""))
                seccion = escape_texto(r.get("sección", ""))
                detalle = escape_texto(r.get("detalle", ""))
                estado = escape_texto(r.get("estado", "Pendiente"))
                responsables = str(r.get("responsables", "")).strip()

                color_fondo = color_paso(paso)
                color_estado = "#dcfce7" if str(estado).lower() in ["listo", "ok", "done", "completado", "completada"] else "#fee2e2"

                tarjetas += f"""
                <div style="
                    border:1px solid #d1d5db;
                    border-left:6px solid #991b1b;
                    border-radius:12px;
                    padding:10px;
                    margin-bottom:10px;
                    background:{color_fondo};
                ">
                    <div style="
                        display:flex;
                        align-items:center;
                        gap:8px;
                        margin-bottom:6px;
                    ">
                        <div style="
                            width:14px;
                            height:14px;
                            min-width:14px;
                            border-radius:3px;
                            background:#dc2626;
                            border:2px solid #991b1b;
                        "></div>

                        <div style="font-weight:800; font-size:13px; color:#111827;">
                            {escape_texto(paso_label)}
                        </div>
                    </div>

                    <div style="font-size:12px; color:#374151; margin-bottom:3px;">
                        <b>Evaluación:</b> {evento if evento else "—"}
                    </div>
                    <div style="font-size:12px; color:#374151; margin-bottom:3px;">
                        <b>Sección:</b> {seccion if seccion else "—"}
                    </div>
                    <div style="font-size:12px; color:#374151; margin-bottom:6px;">
                        <b>Responsables:</b> {render_badges_profes(responsables)}
                    </div>
                    <div style="font-size:12px; color:#6b7280; margin-bottom:8px;">
                        {detalle if detalle else "—"}
                    </div>
                    <div style="
                        display:inline-block;
                        padding:4px 8px;
                        border-radius:999px;
                        background:{color_estado};
                        font-size:11px;
                        font-weight:700;
                        color:#111827;
                    ">
                        {estado if estado else "Pendiente"}
                    </div>
                </div>
                """

        encabezado = f"{dias_es.get(fecha_ts.weekday(), '')} {fecha_ts.strftime('%d/%m')}"
        columnas_html.append(f"""
        <div style="min-width:260px; flex:1;">
            <div style="
                text-align:center;
                font-weight:800;
                background:#374151;
                color:white;
                padding:10px 8px;
                border-radius:10px;
                margin-bottom:10px;
                font-size:13px;
            ">
                {encabezado}
            </div>
            {tarjetas}
        </div>
        """)

    return f"""
    <div style="
        width:100%;
        overflow-x:auto;
        padding-bottom:4px;
    ">
        <div style="
            display:flex;
            gap:12px;
            align-items:flex-start;
            min-width:1200px;
        ">
            {''.join(columnas_html)}
        </div>
    </div>
    """
    
    


# def altura_misiones_allday(df_mis_sem):
#     if df_mis_sem.empty or "fecha_limite" not in df_mis_sem.columns:
#         return 220

#     df2 = df_mis_sem.copy()
#     df2["fecha_limite"] = pd.to_datetime(df2["fecha_limite"], errors="coerce")
#     df2 = df2.dropna(subset=["fecha_limite"]).copy()

#     if df2.empty:
#         return 220

#     max_por_dia = df2.groupby(df2["fecha_limite"].dt.date).size().max()
#     max_por_dia = int(max_por_dia) if pd.notna(max_por_dia) else 1

#     return max(220, min(520, 130 + 34 * max_por_dia))


def altura_misiones_allday(df_mis_sem):
    if df_mis_sem.empty or "fecha_limite" not in df_mis_sem.columns:
        return 260

    df2 = df_mis_sem.copy()
    df2["fecha_limite"] = pd.to_datetime(df2["fecha_limite"], errors="coerce")
    df2 = df2.dropna(subset=["fecha_limite"]).copy()

    if df2.empty:
        return 260

    max_por_dia = df2.groupby(df2["fecha_limite"].dt.date).size().max()
    max_por_dia = int(max_por_dia) if pd.notna(max_por_dia) else 1

    # sin tope chico: Fokito y Enobnu necesitan más alto
    return max(260, 180 + 48 * max_por_dia)


def render_fullcalendar_html_con_misiones_abajo(events_cal, events_mis, initial_date, tz="America/Santiago", height_px=900, height_misiones_px=260):
    events_cal_json = json.dumps(events_cal, ensure_ascii=False)
    events_mis_json = json.dumps(events_mis, ensure_ascii=False)

    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.css" rel="stylesheet"/>
  <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/locales-all.global.min.js"></script>

  <style>
    html, body {{
      margin: 0;
      padding: 0;
      font-family: Arial, sans-serif;
      background: white;
    }}

    #calendar-main {{
      padding: 0 6px;
      margin-bottom: 12px;
    }}

    .titulo-misiones {{
      padding: 0 10px;
      margin: 8px 0 6px 0;
      font-size: 15px;
      font-weight: 800;
      color: #374151;
    }}

    #calendar-misiones-wrap {{
      margin-left: 54px;
      width: calc(100% - 54px);
    }}

    #calendar-misiones {{
      padding: 0 6px;
      margin-top: 4px;
    }}

    .fc .fc-scrollgrid, .fc .fc-scrollgrid td, .fc .fc-scrollgrid th {{
      border-width: 2px !important;
      border-color: rgba(0,0,0,0.22) !important;
    }}

    .fc .fc-event {{
      border-width: 3px !important;
      border-style: solid !important;
      border-radius: 10px !important;
    }}

    .fc .fc-event-title {{
      white-space: normal !important;
      font-size: 13px !important;
      line-height: 1.15 !important;
      font-weight: 700 !important;
    }}

    .fc .fc-event-main {{
      padding: 6px 10px !important;
    }}

    .fc .fc-timegrid-slot {{
      height: 2.0em !important;
    }}

    .fc .fc-day-today {{
      background: rgba(250, 204, 21, 0.10) !important;
    }}

    .fc .fc-daygrid-day.fc-day-today,
    .fc .fc-timegrid-col.fc-day-today {{
      box-shadow: inset 0 0 0 2px rgba(245, 158, 11, 0.45);
    }}

    .fc-theme-standard td, .fc-theme-standard th {{
      border-color: rgba(0,0,0,0.22) !important;
    }}

    .evento-mision {{
      background: #fee2e2 !important;
      border-color: #dc2626 !important;
      color: #7f1d1d !important;
    }}

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

    .modal h3 {{
      margin: 0 0 10px 0;
      font-size: 18px;
    }}

    .row {{
      margin: 6px 0;
      font-size: 14px;
    }}

    .label {{
      font-weight: 800;
    }}

    .close {{
      float: right;
      cursor: pointer;
      padding: 6px 10px;
      border-radius: 10px;
      background: #f3f4f6;
      font-weight: 800;
    }}

    .close:hover {{
      background: #e5e7eb;
    }}
  </style>
</head>

<body>
  <div id="calendar-main"></div>

  <div class="titulo-misiones">🚩 Misiones de la semana</div>
  <div id="calendar-misiones-wrap">
    <div id="calendar-misiones"></div>
  </div>

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
    const eventsCal = {events_cal_json};
    const eventsMis = {events_mis_json};

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
      const calendarMainEl = document.getElementById('calendar-main');
      const calendarMisEl = document.getElementById('calendar-misiones');

      const calMain = new FullCalendar.Calendar(calendarMainEl, {{
        locale: 'es',
        timeZone: {json.dumps(tz)},
        firstDay: 1,
        initialView: 'timeGridWeek',
        initialDate: {json.dumps(initial_date)},
        height: {height_px},
        nowIndicator: true,
        allDaySlot: false,
        slotMinTime: '08:00:00',
        slotMaxTime: '21:00:00',
        expandRows: true,
        stickyHeaderDates: true,
        weekNumbers: true,
        fixedWeekCount: false,
        showNonCurrentDates: false,
        dayHeaderFormat: {{ weekday: 'short', day: '2-digit', month: '2-digit' }},
        titleFormat: {{ year: 'numeric', month: 'long' }},
        headerToolbar: {{
          left: '',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,listWeek'
        }},
        events: eventsCal,
        eventClick: function(info) {{
          openModal(info);
        }},
      }});

      const calMis = new FullCalendar.Calendar(calendarMisEl, {{
        locale: 'es',
        timeZone: {json.dumps(tz)},
        firstDay: 1,
        initialView: 'dayGridWeek',
        initialDate: {json.dumps(initial_date)},
        height: {height_misiones_px},
        headerToolbar: false,
        weekNumbers: false,
        fixedWeekCount: false,
        showNonCurrentDates: false,
        contentHeight: "auto",
        dayMaxEvents: false,
        dayMaxEventRows: false,
        displayEventTime: false,
        dayHeaderFormat: {{ weekday: 'short', day: '2-digit', month: '2-digit' }},
        events: eventsMis,
        eventClick: function(info) {{
          openModal(info);
        }},
        eventDidMount: function(arg) {{
          arg.el.classList.add("evento-mision");
        }}
      }});

      calMain.render();
      calMis.render();
    }});
  </script>
</body>
</html>
"""


# ============================================================
# MODAL STREAMLIT (por si lo quieres reutilizar)
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
# CONFIG STREAMLIT
# ============================================================
st.set_page_config(page_title="Calendario del Curso", layout="wide")

# st.markdown("""
# <style>
# .fc .fc-event-title,
# .fc .fc-event-title-container,
# .fc .fc-event-title-wrap {
#   white-space: normal !important;
#   overflow: visible !important;
# }

# .fc .fc-event-main {
#   padding: 4px 8px !important;
# }

# .fc .fc-timegrid-event,
# .fc .fc-daygrid-event {
#   min-height: 72px !important;
# }

# .fc .fc-event-title {
#   font-size: 14px !important;
#   line-height: 1.2 !important;
#   font-weight: 700 !important;
# }

# .fc .fc-timegrid-slot {
#   height: 2.2em !important;
# }

# .fc .fc-timegrid-allday {
#   min-height: 140px !important;
# }

# .fc .fc-bg-event {
#   z-index: 1 !important;
#   opacity: 0.35 !important;
# }

# .fc .fc-event {
#   z-index: 3 !important;
#   position: relative !important;
#   border-width: 3px !important;
# }

# .fc .fc-timegrid-event .fc-event-main,
# .fc .fc-timegrid-event .fc-event-main-frame,
# .fc .fc-timegrid-col-frame {
#   overflow: hidden !important;
# }

# .fc .fc-timegrid-slot,
# .fc .fc-timegrid-axis,
# .fc .fc-timegrid-col,
# .fc .fc-scrollgrid,
# .fc .fc-scrollgrid td,
# .fc .fc-scrollgrid th {
#   border-width: 2px !important;
#   border-color: rgba(0,0,0,0.25) !important;
# }

# .fc .fc-timegrid-now-indicator-line {
#   border-width: 3px !important;
# }
# </style>
# """, unsafe_allow_html=True)

st.markdown("""
<style>
.fc .fc-event-title,
.fc .fc-event-title-container,
.fc .fc-event-title-wrap {
  white-space: normal !important;
  overflow: hidden !important;
  word-break: break-word !important;
}

.fc .fc-event-main {
  padding: 4px 8px !important;
  overflow: hidden !important;
}

.fc .fc-timegrid-event,
.fc .fc-daygrid-event {
  min-height: 72px !important;
  max-width: 100% !important;
}

.fc .fc-event-title {
  font-size: 14px !important;
  line-height: 1.2 !important;
  font-weight: 700 !important;
}

.fc .fc-timegrid-slot {
  height: 2.2em !important;
}

.fc .fc-timegrid-allday {
  min-height: 140px !important;
}

.fc .fc-bg-event {
  z-index: 1 !important;
  opacity: 0.35 !important;
}

.fc .fc-event {
  z-index: 3 !important;
  position: relative !important;
  border-width: 3px !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
}

.fc .fc-timegrid-event .fc-event-main,
.fc .fc-timegrid-event .fc-event-main-frame,
.fc .fc-timegrid-col-frame,
.fc .fc-timegrid-event-harness {
  overflow: hidden !important;
}

.fc .fc-timegrid-slot,
.fc .fc-timegrid-axis,
.fc .fc-timegrid-col,
.fc .fc-scrollgrid,
.fc .fc-scrollgrid td,
.fc .fc-scrollgrid th {
  border-width: 2px !important;
  border-color: rgba(0,0,0,0.25) !important;
}

.fc .fc-timegrid-now-indicator-line {
  border-width: 3px !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# ESTADO INICIAL
# ============================================================
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

df_urgentes = cargar_urgentes("config/urgente.yml", curso_actual=curso_actual)
render_sidebar_urgentes(df_urgentes)

all_secciones = sorted([x for x in df["sección"].dropna().astype(str).unique() if str(x).strip()])

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
    st.session_state.nav_semana = semana_actual_desde_df(df)
    st.session_state.curso_anterior = curso_actual

if "nav_semana" not in st.session_state:
    st.session_state.nav_semana = semana_actual_desde_df(df)

inicializar_widgets_filtros(curso_actual, all_secciones, all_prof_codes)

# tab1, tab2, tab3, tab4 = st.tabs([
#     "📆 Calendario",
#     "📄 Excel Horarios",
#     "🧭 Misiones",
#     "📊 Estadísticas"
# ])
tab1, tab2, tab3 = st.tabs([
    "📆 Calendario",
    "📄 Excel Horarios",
    "🧭 Misiones"
])

mostrar_urgentes_sidebar()

# ============================================================
# TAB 1: CALENDARIO
# ============================================================
with tab1:
    sincronizar_filtros_desde_widgets(curso_actual, all_secciones, all_prof_codes)

    semana_sel = st.session_state.nav_semana
    sec_selected = {s for s, ok in st.session_state.sel_secciones.items() if ok}
    prof_selected = {p for p, ok in st.session_state.sel_profes.items() if ok}

    df_f = df.copy()

    if sec_selected:
        df_f = df_f[df_f["sección"].isin(sec_selected)].copy()
    else:
        df_f = df_f.iloc[0:0].copy()

    if prof_selected:
        df_f = df_f[df_f["profesores"].apply(lambda x: row_has_prof(x, prof_selected))].copy()
    else:
        df_f = df_f.iloc[0:0].copy()

    fechas_semana = df[df["semana"] == semana_sel]["fecha"].dropna().sort_values()

    if not fechas_semana.empty:
        lunes_semana = fechas_semana.min().normalize()
    else:
        min_global = pd.to_datetime(df["fecha"], errors="coerce").min()
        if pd.notna(min_global):
            lunes_semana = (min_global + pd.Timedelta(days=7 * (semana_sel - 1))).normalize()
        else:
            lunes_semana = pd.Timestamp.now().normalize()

    initial_date = lunes_semana.strftime("%Y-%m-%d")
    fechas_semana_ordenadas = [lunes_semana + pd.Timedelta(days=k) for k in range(7)]

    events_cal = build_events_calendario_para_html(df_f)

    df_mis_sem = df_misiones.copy()
    events_mis = []

    if not df_mis_sem.empty:
        df_mis_sem["fecha_limite"] = pd.to_datetime(df_mis_sem["fecha_limite"], errors="coerce")

        fechas_sem = set(pd.Timestamp(x).date() for x in fechas_semana_ordenadas)
        df_mis_sem = df_mis_sem[df_mis_sem["fecha_limite"].dt.date.isin(fechas_sem)].copy()

        if sec_selected:
            df_mis_sem = df_mis_sem[df_mis_sem["sección"].isin(sec_selected)].copy()
        else:
            df_mis_sem = df_mis_sem.iloc[0:0].copy()

        if prof_selected:
            df_mis_sem = df_mis_sem[
                df_mis_sem["responsables"].apply(lambda x: row_has_prof(x, prof_selected))
            ].copy()
        else:
            df_mis_sem = df_mis_sem.iloc[0:0].copy()

        if not df_mis_sem.empty:
            events_mis = build_events_misiones_allday_para_html(df_mis_sem)

    st.subheader("Calendario del curso")

    st.session_state.nav_render_pos = "arriba"
    render_navegacion_semanal(df, curso_actual)

    # html_cal = render_fullcalendar_html_con_misiones(
    #     events_cal=events_cal,
    #     events_mis=events_mis,
    #     initial_date=initial_date,
    #     tz=TIMEZONE,
    #     height_px=980
    # )

    # components.html(html_cal, height=1100, scrolling=False)

    alto_misiones = 260
    if events_mis:
        alto_misiones = max(260, 120 + 48 * max(1, len(events_mis)))

    html_cal = render_fullcalendar_html_con_misiones_abajo(
        events_cal=events_cal,
        events_mis=events_mis,
        initial_date=initial_date,
        tz=TIMEZONE,
        height_px=920,
        height_misiones_px=alto_misiones
    )

    components.html(html_cal, height=1050 + alto_misiones, scrolling=False)

    st.divider()
    st.subheader("Filtros y navegación")

    c_filtros, c_nav = st.columns([2, 1])

    with c_filtros:
        ftop1, ftop2 = st.columns(2)

        with ftop1:
            st.caption("Secciones")
            bsec1, bsec2 = st.columns(2)

            with bsec1:
                if st.button("Todas las secciones", key=f"all_sec_{curso_actual}", use_container_width=True):
                    for s in all_secciones:
                        st.session_state.sel_secciones[s] = True
                        st.session_state[f"sec_{curso_actual}_{s}"] = True
                    st.rerun()

            with bsec2:
                if st.button("Ninguna sección", key=f"none_sec_{curso_actual}", use_container_width=True):
                    for s in all_secciones:
                        st.session_state.sel_secciones[s] = False
                        st.session_state[f"sec_{curso_actual}_{s}"] = False
                    st.rerun()

            for s in all_secciones:
                st.checkbox(s, key=f"sec_{curso_actual}_{s}")

        with ftop2:
            st.caption("Profesores")
            bpro1, bpro2 = st.columns(2)

            with bpro1:
                if st.button("Todos los profes", key=f"all_prof_{curso_actual}", use_container_width=True):
                    for p in all_prof_codes:
                        st.session_state.sel_profes[p] = True
                        st.session_state[f"prof_{curso_actual}_{p}"] = True
                    st.rerun()

            with bpro2:
                if st.button("Ningún profe", key=f"none_prof_{curso_actual}", use_container_width=True):
                    for p in all_prof_codes:
                        st.session_state.sel_profes[p] = False
                        st.session_state[f"prof_{curso_actual}_{p}"] = False
                    st.rerun()

            if not all_prof_codes:
                st.info("No hay profesores.")
            else:
                for p in all_prof_codes:
                    st.checkbox(p, key=f"prof_{curso_actual}_{p}")

    with c_nav:
        st.caption("Navegación semanal")

        max_sem = df["semana"].max()
        if pd.isna(max_sem):
            max_sem = 20
        max_sem = int(max_sem)

        nav1, nav2 = st.columns(2)

        with nav1:
            if st.button("⬅️ Semana anterior", use_container_width=True, key=f"prev_week_{curso_actual}"):
                if st.session_state.nav_semana > 1:
                    st.session_state.nav_semana -= 1
                st.rerun()

        with nav2:
            if st.button("Semana siguiente ➡️", use_container_width=True, key=f"next_week_{curso_actual}"):
                if st.session_state.nav_semana < max_sem:
                    st.session_state.nav_semana += 1
                st.rerun()

        semana_nueva = st.radio(
            "Semana",
            options=list(range(1, max_sem + 1)),
            horizontal=True,
            index=max(0, min(st.session_state.nav_semana - 1, max_sem - 1)),
            key=f"radio_semana_{curso_actual}"
        )

        if semana_nueva != st.session_state.nav_semana:
            st.session_state.nav_semana = semana_nueva
            st.rerun()

    st.markdown("### Navegación rápida")
    st.session_state.nav_render_pos = "abajo"
    render_navegacion_semanal(df, curso_actual)
    sincronizar_filtros_desde_widgets(curso_actual, all_secciones, all_prof_codes)

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
# with tab4:
#     st.subheader("📊 Plots útiles para profesores")

#     df_plot = df.copy()
#     df_plot["semana"] = pd.to_numeric(df_plot["semana"], errors="coerce")
#     df_plot = df_plot.dropna(subset=["semana"])

#     c1, c2 = st.columns(2)

#     with c1:
#         st.markdown("### Eventos por semana")
#         week_counts = df_plot.groupby("semana").size().rename("eventos")
#         st.bar_chart(week_counts)

#     with c2:
#         st.markdown("### Eventos por actividad")
#         act_counts = df_plot.groupby("actividad").size().rename("eventos").sort_values(ascending=False)
#         st.bar_chart(act_counts)

#     st.divider()
#     st.markdown("### Carga por profesor (horarios)")

#     rows = []
#     for _, r in df_plot.iterrows():
#         for p in split_profes(r.get("profesores", "")):
#             rows.append({
#                 "profesor": p,
#                 "actividad": r.get("actividad", ""),
#                 "semana": r.get("semana", None)
#             })

#     if rows:
#         prof_df = pd.DataFrame(rows)
#         prof_counts = prof_df.groupby("profesor").size().rename("eventos").sort_values(ascending=False)
#         st.bar_chart(prof_counts)
#     else:
#         st.info("No hay profesores asignados en el calendario.")

#     st.divider()

#     if not df_misiones.empty:
#         st.markdown("### Misiones por profesor")

#         filas_misiones = []
#         for _, r in df_misiones.iterrows():
#             for p in split_profes(r.get("responsables", "")):
#                 filas_misiones.append({
#                     "profesor": p,
#                     "evento": r.get("evento", ""),
#                     "paso": PASO_LABELS.get(str(r.get("paso", "")).strip(), str(r.get("paso", "")).strip()),
#                     "estado": str(r.get("estado", "")).strip() or "Pendiente"
#                 })

#         if filas_misiones:
#             df_mp = pd.DataFrame(filas_misiones)

#             conteo_misiones = df_mp.groupby("profesor").size().rename("misiones").sort_values(ascending=False)
#             st.bar_chart(conteo_misiones)

#             st.markdown("### Distribución por tipo de paso")
#             conteo_pasos = df_mp.groupby("paso").size().rename("cantidad").sort_values(ascending=False)
#             st.bar_chart(conteo_pasos)

#             st.divider()
#             st.markdown("### Proporción misiones / carga de seminario")
#             st.markdown("#### Pesos por misión")

#             pesos = {}
#             cpes1, cpes2, cpes3 = st.columns(3)
#             claves_pesos = list(PESOS_MISION_DEFAULT.keys())

#             for i, paso in enumerate(claves_pesos):
#                 col = [cpes1, cpes2, cpes3][i % 3]
#                 with col:
#                     pesos[paso] = st.number_input(
#                         f"Peso {paso}",
#                         min_value=0.0,
#                         value=float(PESOS_MISION_DEFAULT[paso]),
#                         step=0.1,
#                         key=f"peso_{curso_actual}_{paso}"
#                     )

#             df_carga = construir_tabla_carga_seminario(
#                 df_cal=df,
#                 df_misiones=df_misiones,
#                 pesos=pesos
#             )

#             if not df_carga.empty:
#                 color_map = {p: color_profesor(p) for p in df_carga["profesor"].unique()}

#                 fig = px.bar(
#                     df_carga,
#                     x="profesor",
#                     y="ratio",
#                     color="profesor",
#                     color_discrete_map=color_map,
#                     custom_data=["misiones_ponderadas", "cupos_semana_1", "clases_estimadas"],
#                     title="Carga relativa de misiones respecto a seminarios asignados"
#                 )

#                 fig.update_traces(
#                     hovertemplate=(
#                         "<b>%{x}</b><br>"
#                         "Ratio: %{y:.3f}<br>"
#                         "Misiones ponderadas: %{customdata[0]:.1f}<br>"
#                         "Cupos semana 1: %{customdata[1]}<br>"
#                         "Clases estimadas: %{customdata[2]}<extra></extra>"
#                     )
#                 )

#                 fig.update_layout(
#                     xaxis_title="Profesor",
#                     yaxis_title="misiones_ponderadas / clases_estimadas",
#                     yaxis=dict(range=[0, 2], fixedrange=False),
#                     showlegend=False,
#                     dragmode="zoom"
#                 )

#                 st.plotly_chart(fig, use_container_width=True)

#                 st.dataframe(
#                     df_carga,
#                     use_container_width=True,
#                     hide_index=True
#                 )
#             else:
#                 st.info("No se pudo construir la tabla de carga relativa.")
#         else:
#             st.info("No hay misiones registradas.")
#     else:
#         st.info("No hay archivo de misiones cargado.")