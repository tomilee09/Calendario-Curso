import os
import json
import base64
import argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import yaml
import pandas as pd

from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


# ============================================================
# CONFIG DE CURSOS
# ============================================================
PROFESORES_PATH = os.path.join("config", "profesores.yml")

CURSOS = {
    "fokito": {
        "config_path": os.path.join("config", "calendario_fokito.yml"),
        "misiones_path": os.path.join("data", "fokito", "misiones.xlsx"),
        "calendario_path": os.path.join("data", "fokito", "calendario.xlsx"),
    },
    "tecnologia_medica": {
        "config_path": os.path.join("config", "calendario_tecnologia_medica.yml"),
        "misiones_path": os.path.join("data", "tecnologia_medica", "misiones.xlsx"),
        "calendario_path": os.path.join("data", "tecnologia_medica", "calendario.xlsx"),
    },
    "medicina": {
        "config_path": os.path.join("config", "calendario_medicina.yml"),
        "misiones_path": os.path.join("data", "medicina", "misiones.xlsx"),
        "calendario_path": os.path.join("data", "medicina", "calendario.xlsx"),
    },
    "enobnu": {
        "config_path": os.path.join("config", "calendario_enobnu.yml"),
        "misiones_path": os.path.join("data", "enobnu", "misiones.xlsx"),
        "calendario_path": os.path.join("data", "enobnu", "calendario.xlsx"),
    },
}


# ============================================================
# HELPERS
# ============================================================
ORDEN_DIAS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

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


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def split_profesores(s):
    if not s or pd.isna(s):
        return []
    return [x.strip() for x in str(s).split(",") if x.strip()]


def fmt_fecha(x):
    ts = pd.to_datetime(x, errors="coerce")
    if pd.isna(ts):
        return ""
    return ts.strftime("%d/%m/%Y")


def hhmm_to_time(s):
    h, m = s.split(":")
    return int(h), int(m)


def nombre_paso(paso):
    paso = str(paso).strip()
    return PASO_LABELS.get(paso, paso)


def curso_label(config, fallback):
    return str(config.get("curso", {}).get("nombre", fallback)).strip() or fallback


def inicio_fin_semana_siguiente(now_local):
    lunes_actual = now_local.date() - timedelta(days=now_local.weekday())
    lunes_siguiente = lunes_actual + timedelta(days=7)
    domingo_siguiente = lunes_siguiente + timedelta(days=6)
    return lunes_siguiente, domingo_siguiente


def normalizar_estado(estado):
    e = str(estado or "").strip().lower()
    if e in ["listo", "ok", "done", "completado", "completada", "finalizado", "finalizada"]:
        return "Completada"
    if e in ["en progreso", "en_progreso", "progreso", "haciendo"]:
        return "En progreso"
    return "Pendiente"


# ============================================================
# LECTURA DE EMAILS DESDE YAML
# ============================================================
# def obtener_diccionario_profesores(emails_cfg):
#     """
#     Devuelve un dict:
#     {
#       "TY": {"nombre": "Tomás", "email": "xxx"},
#       ...
#     }

#     Soporta dos formatos:
#     1) Nuevo:
#        emails:
#          profesores:
#            TY:
#              nombre: "Tomás"
#              email: "..."
#     2) Antiguo:
#        emails:
#          profesor_a_email:
#            TY: "..."
#     """
#     profesores = {}

#     bloque_nuevo = emails_cfg.get("profesores", {}) or {}
#     for codigo, data in bloque_nuevo.items():
#         if isinstance(data, dict):
#             nombre = str(data.get("nombre", codigo)).strip() or codigo
#             email = str(data.get("email", "")).strip()
#         else:
#             nombre = str(codigo).strip()
#             email = str(data).strip()

#         if email:
#             profesores[str(codigo).strip()] = {
#                 "nombre": nombre,
#                 "email": email
#             }

#     bloque_antiguo = emails_cfg.get("profesor_a_email", {}) or {}
#     for codigo, email in bloque_antiguo.items():
#         codigo = str(codigo).strip()
#         email = str(email).strip()
#         if codigo and email and codigo not in profesores:
#             profesores[codigo] = {
#                 "nombre": codigo,
#                 "email": email
#             }

#     return profesores

def cargar_profesores_globales(path):
    if not os.path.exists(path):
        raise RuntimeError(f"No existe archivo global de profesores: {path}")

    data = load_yaml(path) or {}
    profesores = data.get("profesores", {}) or {}

    salida = {}
    for codigo, info in profesores.items():
        codigo = str(codigo).strip()
        if not codigo:
            continue

        if isinstance(info, dict):
            nombre = str(info.get("nombre", codigo)).strip() or codigo
            email = str(info.get("email", "")).strip()
        else:
            nombre = codigo
            email = str(info).strip()

        salida[codigo] = {
            "nombre": nombre,
            "email": email,
        }

    return salida

def obtener_info_profesor(profesores_dict, codigo):
    codigo = str(codigo).strip()
    return profesores_dict.get(codigo, {"nombre": codigo, "email": ""})


def obtener_cc_por_secciones(secciones, emails_cfg, profesores_dict):
    """
    Agrega a CC el PEC según sección, sin repetir.
    Soporta:
      pec_por_seccion:
        "Sección 1": "TY"
    donde "TY" se busca en profesores_dict.
    """
    cc_final = []

    cc_directo = emails_cfg.get("cc", []) or []
    for x in cc_directo:
        correo = str(x).strip()
        if correo and correo not in cc_final:
            cc_final.append(correo)

    pec_por_seccion = emails_cfg.get("pec_por_seccion", {}) or {}

    for seccion in sorted(set(secciones)):
        if seccion not in pec_por_seccion:
            continue

        ref = str(pec_por_seccion[seccion]).strip()
        if not ref:
            continue

        # Si parece email, usar directo
        if "@" in ref:
            if ref not in cc_final:
                cc_final.append(ref)
        else:
            info = obtener_info_profesor(profesores_dict, ref)
            correo = str(info.get("email", "")).strip()
            if correo and correo not in cc_final:
                cc_final.append(correo)

    return cc_final


# ============================================================
# GMAIL
# ============================================================
def load_gmail_credentials(scopes=None):
    if scopes is None:
        scopes = ["https://www.googleapis.com/auth/gmail.send"]

    token_json_env = os.getenv("GMAIL_TOKEN_JSON", "").strip()
    if token_json_env:
        token_info = json.loads(token_json_env)
        return Credentials.from_authorized_user_info(token_info, scopes=scopes)

    token_path = os.getenv("GMAIL_TOKEN_PATH", "token.json")
    if not os.path.exists(token_path):
        raise RuntimeError(
            "No encuentro token.json. Define GMAIL_TOKEN_JSON en secrets o coloca token.json local."
        )

    return Credentials.from_authorized_user_file(token_path, scopes=scopes)


def gmail_send(service, to_email, subject, body, cc_list=None, from_name=""):
    if cc_list is None:
        cc_list = []

    msg = MIMEText(body, "plain", "utf-8")
    msg["to"] = to_email
    msg["subject"] = subject
    if from_name:
        msg["from"] = from_name
    if cc_list:
        msg["cc"] = ", ".join([x for x in cc_list if str(x).strip()])

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()


# ============================================================
# LOG
# ============================================================
def load_log(path):
    if not os.path.exists(path):
        return {"sent": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_log(path, log):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def was_sent(log, key):
    return key in log.get("sent", {})


def mark_sent(log, key):
    log.setdefault("sent", {})[key] = datetime.utcnow().isoformat() + "Z"


# ============================================================
# CARGA DE MISIONES
# ============================================================
def cargar_misiones_excel(path):
    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        df = pd.read_excel(path, sheet_name="Misiones")
    except Exception:
        return pd.DataFrame()

    if df.empty:
        return df

    for c in ["fecha_limite", "fecha_evento"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    for c in ["evento", "paso", "sección", "responsables", "detalle", "estado"]:
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str)

    return df


def cargar_calendario_excel(path):
    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        df = pd.read_excel(path, sheet_name="Calendario")
    except Exception:
        return pd.DataFrame()

    if df.empty:
        return df

    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    for c in ["horario", "sección", "actividad", "tema", "evaluación", "profesores", "observaciones"]:
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str)

    return df


def construir_lista_clases_texto(df_prof_clases):
    if df_prof_clases.empty:
        return "No tienes clases asignadas para la próxima semana."

    lineas = []

    for i, (_, r) in enumerate(df_prof_clases.iterrows(), start=1):
        fecha = fmt_fecha(r.get("fecha", ""))
        horario = str(r.get("horario", "")).strip()
        seccion = str(r.get("sección", "")).strip()
        actividad = str(r.get("actividad", "")).strip()
        tema = str(r.get("tema", "")).strip()
        evaluacion = str(r.get("evaluación", "")).strip()
        observaciones = str(r.get("observaciones", "")).strip()

        partes = []
        partes.append(f"{i}. {fecha}")
        if horario:
            partes.append(f"   Horario: {horario}")
        if seccion:
            partes.append(f"   Sección: {seccion}")
        if actividad:
            partes.append(f"   Tipo: {actividad}")
        if tema:
            partes.append(f"   Tema: {tema}")
        if evaluacion:
            partes.append(f"   Evaluación asociada: {evaluacion}")
        if observaciones:
            partes.append(f"   Observaciones: {observaciones}")

        lineas.append("\n".join(partes))

    return "\n\n".join(lineas)


def profesor_en_lista(prof, valor_profesores):
    return prof in split_profesores(valor_profesores)


def obtener_profes_relevantes_del_curso(df_misiones_total, df_cal_total):
    """
    Devuelve solo profes que realmente participan en este curso:
    - aparecen en responsables de misiones
    - o aparecen en profesores del calendario
    """
    profes = set()

    if not df_misiones_total.empty and "responsables" in df_misiones_total.columns:
        for s in df_misiones_total["responsables"].dropna().unique():
            for p in split_profesores(s):
                profes.add(p)

    if not df_cal_total.empty and "profesores" in df_cal_total.columns:
        for s in df_cal_total["profesores"].dropna().unique():
            for p in split_profesores(s):
                profes.add(p)

    return sorted(profes)



# def construir_lista_misiones_texto(df_prof):
#     """
#     Formato legible.
#     """
#     if df_prof.empty:
#         return (
#             "No tienes misiones planificadas originalmente para esta semana.\n\n"
#             "De todos modos, puede haber coordinaciones adicionales conversadas "
#             "con los PEC o con el equipo docente que no estén reflejadas aquí."
#         )

#     lineas = []

#     for i, (_, r) in enumerate(df_prof.iterrows(), start=1):
#         fecha_limite = fmt_fecha(r.get("fecha_limite", ""))
#         fecha_evento = fmt_fecha(r.get("fecha_evento", ""))
#         evento = str(r.get("evento", "")).strip()
#         paso = nombre_paso(r.get("paso", ""))
#         seccion = str(r.get("sección", "")).strip()
#         detalle = str(r.get("detalle", "")).strip()
#         estado = normalizar_estado(r.get("estado", ""))

#         partes = []
#         partes.append(f"{i}. {fecha_limite}")
#         if paso:
#             partes.append(f"   Misión: {paso}")
#         if evento:
#             partes.append(f"   Evaluación: {evento}")
#         if seccion:
#             partes.append(f"   Sección: {seccion}")
#         if fecha_evento:
#             partes.append(f"   Fecha evaluación: {fecha_evento}")
#         if detalle:
#             partes.append(f"   Detalle: {detalle}")
#         partes.append(f"   Estado: {estado}")

#         lineas.append("\n".join(partes))

#     return "\n\n".join(lineas)


def construir_lista_misiones_texto(df_prof):
    if df_prof.empty:
        return (
            "No tienes misiones planificadas originalmente para esta semana.\n\n"
            "De todos modos, puede haber coordinaciones adicionales conversadas "
            "con los PEC o con el equipo docente que no estén reflejadas aquí."
        )

    lineas = []

    for i, (_, r) in enumerate(df_prof.iterrows(), start=1):
        fecha_limite = fmt_fecha(r.get("fecha_limite", ""))
        fecha_evento = fmt_fecha(r.get("fecha_evento", ""))
        evento = str(r.get("evento", "")).strip()
        paso = nombre_paso(r.get("paso", ""))
        seccion = str(r.get("sección", "")).strip()
        detalle = str(r.get("detalle", "")).strip()
        estado = normalizar_estado(r.get("estado", ""))

        partes = []
        partes.append(f"{i}. {fecha_limite}")
        if paso:
            partes.append(f"   Misión: {paso}")
        if evento:
            partes.append(f"   Evaluación: {evento}")
        if seccion:
            partes.append(f"   Sección: {seccion}")
        if fecha_evento:
            partes.append(f"   Fecha evaluación: {fecha_evento}")
        if detalle:
            partes.append(f"   Detalle: {detalle}")
        partes.append(f"   Estado: {estado}")

        lineas.append("\n".join(partes))

    return "\n\n".join(lineas)


# ============================================================
# REGLAS DE ENVÍO
# ============================================================
def debe_enviar_resumen_hoy(now_local, regla, forzar=False):
    if forzar:
        return True

    dia_envio = str(regla.get("dia_envio", "Friday")).strip()
    hora_envio = str(regla.get("hora_envio", "09:00")).strip()

    if dia_envio not in ORDEN_DIAS:
        dia_envio = "Friday"

    idx_objetivo = ORDEN_DIAS.index(dia_envio)
    if now_local.weekday() != idx_objetivo:
        return False

    h, m = hhmm_to_time(hora_envio)
    return (now_local.hour, now_local.minute) >= (h, m)


# ============================================================
# ENVÍO POR CURSO
# ============================================================
# def procesar_curso(curso_key, info, now_local, dry_run, forzar, service):
#     config_path = info["config_path"]
#     misiones_path = info["misiones_path"]

#     if not os.path.exists(config_path):
#         print(f"[WARN] No existe config para {curso_key}: {config_path}")
#         return 0, None

#     config = load_yaml(config_path)
#     emails_cfg = config.get("emails", {}) or {}
#     regla = emails_cfg.get("resumen_semanal", {}) or {}

#     if not regla:
#         print(f"[WARN] {curso_key}: no tiene bloque emails.resumen_semanal")
#         return 0, None

#     if not debe_enviar_resumen_hoy(now_local, regla, forzar=forzar):
#         print(f"[INFO] {curso_key}: hoy no corresponde enviar resumen semanal.")
#         return 0, None

#     profesores_dict = obtener_diccionario_profesores(emails_cfg)
#     from_name = str(emails_cfg.get("from_name", "")).strip()
#     log_path = emails_cfg.get("estado_envios_path", "data/email_log.json")

#     df = cargar_misiones_excel(misiones_path)

#     lunes_sig, domingo_sig = inicio_fin_semana_siguiente(now_local)

#     if not df.empty:
#         df = df.dropna(subset=["fecha_limite"]).copy()
#         df = df[
#             (df["fecha_limite"].dt.date >= lunes_sig) &
#             (df["fecha_limite"].dt.date <= domingo_sig)
#         ].copy()

#     log = load_log(log_path)
#     enviados = 0
#     nombre_curso = curso_label(config, curso_key)

#     # Profesores a considerar:
#     # 1) todos los definidos en emails.profesores / profesor_a_email
#     # 2) aunque no tengan misiones, igual reciben correo
#     profes_a_considerar = sorted(profesores_dict.keys())

#     # Si quieres restringir solo a quienes aparecen como responsables alguna vez, comenta lo de arriba
#     # y usa esto:
#     # profes_a_considerar = set()
#     # if not df.empty and "responsables" in df.columns:
#     #     for s in df["responsables"].dropna().unique():
#     #         for p in split_profesores(s):
#     #             profes_a_considerar.add(p)
#     # profes_a_considerar = sorted(profes_a_considerar)

#     for prof in profes_a_considerar:
#         info_prof = obtener_info_profesor(profesores_dict, prof)
#         to_email = str(info_prof.get("email", "")).strip()
#         nombre_prof = str(info_prof.get("nombre", prof)).strip() or prof

#         if not to_email:
#             print(f"[WARN] {curso_key}: no hay email para {prof}")
#             continue

#         if df.empty:
#             df_prof = pd.DataFrame()
#         else:
#             df_prof = df[df["responsables"].apply(lambda x: prof in split_profesores(x))].copy()

#         if not df_prof.empty:
#             df_prof = df_prof.sort_values(["fecha_limite", "evento", "paso", "sección"])

#         secciones_prof = []
#         if not df_prof.empty and "sección" in df_prof.columns:
#             secciones_prof = [str(x).strip() for x in df_prof["sección"].dropna().unique() if str(x).strip()]

#         cc_list = obtener_cc_por_secciones(secciones_prof, emails_cfg, profesores_dict)

#         send_key = f"resumen_semanal|{curso_key}|{prof}|{lunes_sig.isoformat()}"
#         if was_sent(log, send_key) and not forzar:
#             print(f"[INFO] {curso_key}: ya enviado a {prof} para semana {lunes_sig}")
#             continue

#         lista_misiones = construir_lista_misiones_texto(df_prof)

#         ctx = {
#             "curso": nombre_curso,
#             "nombre_prof": nombre_prof,
#             "codigo_prof": prof,
#             "fecha_inicio_semana": fmt_fecha(lunes_sig),
#             "fecha_fin_semana": fmt_fecha(domingo_sig),
#             "lista_misiones": lista_misiones,
#             "from_name": from_name,
#         }

#         subject = str(
#             regla.get("asunto", "[{curso}] Misiones para la semana del {fecha_inicio_semana}")
#         ).format(**ctx)

#         body = str(
#             regla.get(
#                 "cuerpo",
#                 "Hola {nombre_prof}:\n\n{lista_misiones}\n\n— {from_name}"
#             )
#         ).format(**ctx)

#         if dry_run:
#             print("\n==================================================")
#             print(f"CURSO: {curso_key}")
#             print(f"PROFESOR: {prof} ({nombre_prof})")
#             print(f"TO: {to_email}")
#             print(f"CC: {', '.join(cc_list) if cc_list else '(sin cc)'}")
#             print(f"SUBJECT: {subject}")
#             print("--------------------------------------------------")
#             print(body)
#             print("==================================================\n")
#         else:
#             gmail_send(service, to_email, subject, body, cc_list=cc_list, from_name=from_name)

#         mark_sent(log, send_key)
#         enviados += 1

#     save_log(log_path, log)
#     return enviados, log_path


def procesar_curso(curso_key, info, now_local, dry_run, forzar, service):
    config_path = info["config_path"]
    misiones_path = info["misiones_path"]
    calendario_path = info["calendario_path"]

    if not os.path.exists(config_path):
        print(f"[WARN] No existe config para {curso_key}: {config_path}")
        return 0, None

    config = load_yaml(config_path)
    emails_cfg = config.get("emails", {}) or {}
    regla = emails_cfg.get("resumen_semanal", {}) or {}

    if not regla:
        print(f"[WARN] {curso_key}: no tiene bloque emails.resumen_semanal")
        return 0, None

    if not debe_enviar_resumen_hoy(now_local, regla, forzar=forzar):
        print(f"[INFO] {curso_key}: hoy no corresponde enviar resumen semanal.")
        return 0, None

    profesores_dict = obtener_diccionario_profesores(emails_cfg)
    from_name = str(emails_cfg.get("from_name", "")).strip()
    log_path = emails_cfg.get("estado_envios_path", "data/email_log.json")

    df_misiones_total = cargar_misiones_excel(misiones_path)
    df_cal_total = cargar_calendario_excel(calendario_path)

    lunes_sig, domingo_sig = inicio_fin_semana_siguiente(now_local)

    # Misiones de la semana siguiente
    if not df_misiones_total.empty:
        df_misiones_sem = df_misiones_total.dropna(subset=["fecha_limite"]).copy()
        df_misiones_sem = df_misiones_sem[
            (df_misiones_sem["fecha_limite"].dt.date >= lunes_sig) &
            (df_misiones_sem["fecha_limite"].dt.date <= domingo_sig)
        ].copy()
    else:
        df_misiones_sem = pd.DataFrame()

    # Clases de la semana siguiente
    if not df_cal_total.empty:
        df_cal_sem = df_cal_total.dropna(subset=["fecha"]).copy()
        df_cal_sem = df_cal_sem[
            (df_cal_sem["fecha"].dt.date >= lunes_sig) &
            (df_cal_sem["fecha"].dt.date <= domingo_sig)
        ].copy()
    else:
        df_cal_sem = pd.DataFrame()

    log = load_log(log_path)
    enviados = 0
    nombre_curso = curso_label(config, curso_key)

    # SOLO profes que realmente pertenecen al curso
    profes_relevantes = obtener_profes_relevantes_del_curso(df_misiones_total, df_cal_total)

    for prof in profes_relevantes:
        info_prof = obtener_info_profesor(profesores_dict, prof)
        to_email = str(info_prof.get("email", "")).strip()
        nombre_prof = str(info_prof.get("nombre", prof)).strip() or prof

        if not to_email:
            print(f"[WARN] {curso_key}: no hay email para {prof}")
            continue

        # Misiones del profesor esta semana
        if df_misiones_sem.empty:
            df_prof_mis = pd.DataFrame()
        else:
            df_prof_mis = df_misiones_sem[
                df_misiones_sem["responsables"].apply(lambda x: profesor_en_lista(prof, x))
            ].copy()

        if not df_prof_mis.empty:
            df_prof_mis = df_prof_mis.sort_values(["fecha_limite", "evento", "paso", "sección"])

        # Clases del profesor esta semana
        if df_cal_sem.empty:
            df_prof_clases = pd.DataFrame()
        else:
            df_prof_clases = df_cal_sem[
                df_cal_sem["profesores"].apply(lambda x: profesor_en_lista(prof, x))
            ].copy()

        if not df_prof_clases.empty:
            df_prof_clases = df_prof_clases.sort_values(["fecha", "horario", "sección", "actividad"])

        secciones_prof = []

        if not df_prof_mis.empty and "sección" in df_prof_mis.columns:
            secciones_prof.extend([str(x).strip() for x in df_prof_mis["sección"].dropna().unique() if str(x).strip()])

        if not df_prof_clases.empty and "sección" in df_prof_clases.columns:
            secciones_prof.extend([str(x).strip() for x in df_prof_clases["sección"].dropna().unique() if str(x).strip()])

        cc_list = obtener_cc_por_secciones(secciones_prof, emails_cfg, profesores_dict)

        send_key = f"resumen_semanal|{curso_key}|{prof}|{lunes_sig.isoformat()}"
        if was_sent(log, send_key) and not forzar:
            print(f"[INFO] {curso_key}: ya enviado a {prof} para semana {lunes_sig}")
            continue

        lista_misiones = construir_lista_misiones_texto(df_prof_mis)
        lista_clases = construir_lista_clases_texto(df_prof_clases)

        ctx = {
            "curso": nombre_curso,
            "nombre_prof": nombre_prof,
            "codigo_prof": prof,
            "fecha_inicio_semana": fmt_fecha(lunes_sig),
            "fecha_fin_semana": fmt_fecha(domingo_sig),
            "lista_misiones": lista_misiones,
            "lista_clases": lista_clases,
            "from_name": from_name,
        }

        subject = str(
            regla.get("asunto", "[{curso}] Misiones para la semana del {fecha_inicio_semana}")
        ).format(**ctx)

        body = str(
            regla.get(
                "cuerpo",
                "Hola {nombre_prof}:\n\nMISIÓNES:\n{lista_misiones}\n\nCLASES:\n{lista_clases}\n\n— {from_name}"
            )
        ).format(**ctx)

        if dry_run:
            print("\n==================================================")
            print(f"CURSO: {curso_key}")
            print(f"PROFESOR: {prof} ({nombre_prof})")
            print(f"TO: {to_email}")
            print(f"CC: {', '.join(cc_list) if cc_list else '(sin cc)'}")
            print(f"SUBJECT: {subject}")
            print("--------------------------------------------------")
            print(body)
            print("==================================================\n")
        else:
            gmail_send(service, to_email, subject, body, cc_list=cc_list, from_name=from_name)

        mark_sent(log, send_key)
        enviados += 1

    save_log(log_path, log)
    return enviados, log_path


def recopilar_resumenes_globales(now_local):
    lunes_sig, domingo_sig = inicio_fin_semana_siguiente(now_local)
    profesores_globales = cargar_profesores_globales(PROFESORES_PATH)

    resumen_global = {}

    for curso_key, info in CURSOS.items():
        config_path = info["config_path"]
        misiones_path = info["misiones_path"]
        calendario_path = info["calendario_path"]

        if not os.path.exists(config_path):
            print(f"[WARN] No existe config para {curso_key}: {config_path}")
            continue

        config = load_yaml(config_path)
        emails_cfg = config.get("emails", {}) or {}
        nombre_curso = curso_label(config, curso_key)

        df_misiones_total = cargar_misiones_excel(misiones_path)
        df_cal_total = cargar_calendario_excel(calendario_path)

        if not df_misiones_total.empty:
            df_misiones_sem = df_misiones_total.dropna(subset=["fecha_limite"]).copy()
            df_misiones_sem = df_misiones_sem[
                (df_misiones_sem["fecha_limite"].dt.date >= lunes_sig) &
                (df_misiones_sem["fecha_limite"].dt.date <= domingo_sig)
            ].copy()
        else:
            df_misiones_sem = pd.DataFrame()

        if not df_cal_total.empty:
            df_cal_sem = df_cal_total.dropna(subset=["fecha"]).copy()
            df_cal_sem = df_cal_sem[
                (df_cal_sem["fecha"].dt.date >= lunes_sig) &
                (df_cal_sem["fecha"].dt.date <= domingo_sig)
            ].copy()
        else:
            df_cal_sem = pd.DataFrame()

        profes_relevantes = obtener_profes_relevantes_del_curso(df_misiones_total, df_cal_total)

        for prof in profes_relevantes:
            info_prof = profesores_globales.get(prof, {"nombre": prof, "email": ""})
            email = str(info_prof.get("email", "")).strip()
            nombre = str(info_prof.get("nombre", prof)).strip() or prof

            if not email:
                print(f"[WARN] {curso_key}: no hay email global para {prof}")
                continue

            if prof not in resumen_global:
                resumen_global[prof] = {
                    "nombre": nombre,
                    "email": email,
                    "cursos": {},
                    "cc": set(),
                }

            if df_misiones_sem.empty:
                df_prof_mis = pd.DataFrame()
            else:
                df_prof_mis = df_misiones_sem[
                    df_misiones_sem["responsables"].apply(lambda x: profesor_en_lista(prof, x))
                ].copy()

            if not df_prof_mis.empty:
                df_prof_mis = df_prof_mis.sort_values(["fecha_limite", "evento", "paso", "sección"])

            if df_cal_sem.empty:
                df_prof_clases = pd.DataFrame()
            else:
                df_prof_clases = df_cal_sem[
                    df_cal_sem["profesores"].apply(lambda x: profesor_en_lista(prof, x))
                ].copy()

            if not df_prof_clases.empty:
                df_prof_clases = df_prof_clases.sort_values(["fecha", "horario", "sección", "actividad"])

            secciones_prof = []
            if not df_prof_mis.empty and "sección" in df_prof_mis.columns:
                secciones_prof.extend([str(x).strip() for x in df_prof_mis["sección"].dropna().unique() if str(x).strip()])

            if not df_prof_clases.empty and "sección" in df_prof_clases.columns:
                secciones_prof.extend([str(x).strip() for x in df_prof_clases["sección"].dropna().unique() if str(x).strip()])

            cc_list = obtener_cc_por_secciones(secciones_prof, emails_cfg, profesores_globales)
            for cc in cc_list:
                resumen_global[prof]["cc"].add(cc)

            # Solo agrega el curso si tiene algo relevante ahí
            if (not df_prof_mis.empty) or (not df_prof_clases.empty):
                resumen_global[prof]["cursos"][curso_key] = {
                    "label": nombre_curso,
                    "misiones": df_prof_mis.copy(),
                    "clases": df_prof_clases.copy(),
                }

    return resumen_global, lunes_sig, domingo_sig




def construir_cuerpo_global(nombre_prof, fecha_inicio, fecha_fin, resumen_prof, from_name):
    bloques = []

    for curso_key, data in resumen_prof["cursos"].items():
        label = data["label"]
        df_mis = data["misiones"]
        df_clases = data["clases"]

        bloque = []
        bloque.append("========================================")
        bloque.append(f"CURSO: {label}")
        bloque.append("========================================")
        bloque.append("")
        bloque.append("MISIONES")
        bloque.append("--------")
        bloque.append(construir_lista_misiones_texto(df_mis))
        bloque.append("")
        bloque.append("CLASES")
        bloque.append("------")
        bloque.append(construir_lista_clases_texto(df_clases))
        bloque.append("")

        bloques.append("\n".join(bloque))

    if not bloques:
        bloques.append(
            "No tienes misiones ni clases asignadas para la próxima semana "
            "en los cursos monitoreados."
        )

    cuerpo = f"""Buen día {nombre_prof},

Este es tu resumen semanal del {fecha_inicio} al {fecha_fin}.

{chr(10).join(bloques)}
Puedes revisar el calendario completo aquí:
https://calendario-curso.streamlit.app

Saludos,
{from_name}
"""
    return cuerpo

# ============================================================
# MAIN
# ============================================================
# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--curso", default="todos", help="fokito | tecnologia_medica | medicina | enobnu | todos")
#     ap.add_argument("--dry-run", action="store_true", help="No envía correos, solo imprime.")
#     ap.add_argument("--forzar", action="store_true", help="Envía aunque hoy no sea el día/hora configurado.")
#     ap.add_argument("--fecha", default="", help="Fecha/hora simulada local, formato YYYY-MM-DD o YYYY-MM-DD HH:MM")
#     args = ap.parse_args()

#     tz_name = "America/Santiago"
#     for _, info in CURSOS.items():
#         if os.path.exists(info["config_path"]):
#             try:
#                 cfg = load_yaml(info["config_path"])
#                 tz_name = cfg.get("curso", {}).get("timezone", tz_name)
#                 break
#             except Exception:
#                 pass

#     tz = ZoneInfo(tz_name)

#     if args.fecha.strip():
#         txt = args.fecha.strip()
#         try:
#             if len(txt) == 10:
#                 now_local = datetime.strptime(txt, "%Y-%m-%d").replace(hour=9, minute=0, tzinfo=tz)
#             else:
#                 now_local = datetime.strptime(txt, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
#         except ValueError:
#             raise SystemExit("Formato inválido en --fecha. Usa YYYY-MM-DD o YYYY-MM-DD HH:MM")
#     else:
#         now_local = datetime.now(tz)

#     service = None
#     if not args.dry_run:
#         creds = load_gmail_credentials()
#         service = build("gmail", "v1", credentials=creds)

#     if args.curso == "todos":
#         cursos_a_procesar = list(CURSOS.keys())
#     else:
#         if args.curso not in CURSOS:
#             raise SystemExit(f"Curso inválido: {args.curso}")
#         cursos_a_procesar = [args.curso]

#     total = 0
#     logs_tocados = set()

#     print(f"[INFO] Fecha local usada: {now_local.strftime('%Y-%m-%d %H:%M %Z')}")
#     print(f"[INFO] Dry run: {args.dry_run}")
#     print(f"[INFO] Forzar: {args.forzar}")

#     for curso_key in cursos_a_procesar:
#         enviados, log_path = procesar_curso(
#             curso_key=curso_key,
#             info=CURSOS[curso_key],
#             now_local=now_local,
#             dry_run=args.dry_run,
#             forzar=args.forzar,
#             service=service,
#         )
#         total += enviados
#         if log_path:
#             logs_tocados.add(log_path)

#     print(f"\nListo. Correos enviados/simulados: {total}")
#     if logs_tocados:
#         print("Logs actualizados:")
#         for p in sorted(logs_tocados):
#             print("-", p)


# if __name__ == "__main__":
#     main()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--curso", default="todos", help="Se mantiene por compatibilidad, pero el envío global usa todos.")
    ap.add_argument("--dry-run", action="store_true", help="No envía correos, solo imprime.")
    ap.add_argument("--forzar", action="store_true", help="Envía aunque hoy no sea el día/hora configurado.")
    ap.add_argument("--fecha", default="", help="Fecha/hora simulada local, formato YYYY-MM-DD o YYYY-MM-DD HH:MM")
    args = ap.parse_args()

    tz = ZoneInfo("America/Santiago")

    if args.fecha.strip():
        txt = args.fecha.strip()
        try:
            if len(txt) == 10:
                now_local = datetime.strptime(txt, "%Y-%m-%d").replace(hour=9, minute=0, tzinfo=tz)
            else:
                now_local = datetime.strptime(txt, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
        except ValueError:
            raise SystemExit("Formato inválido en --fecha. Usa YYYY-MM-DD o YYYY-MM-DD HH:MM")
    else:
        now_local = datetime.now(tz)

    # Tomamos la regla desde un curso base, o podrías crear config global también
    cfg_base = load_yaml(CURSOS["medicina"]["config_path"])
    emails_cfg_base = cfg_base.get("emails", {}) or {}
    regla = emails_cfg_base.get("resumen_semanal", {}) or {}

    if not regla:
        raise SystemExit("No encontré emails.resumen_semanal en el YAML base.")

    if not debe_enviar_resumen_hoy(now_local, regla, forzar=args.forzar):
        print("[INFO] Hoy no corresponde enviar resumen semanal.")
        return

    service = None
    if not args.dry_run:
        creds = load_gmail_credentials()
        service = build("gmail", "v1", credentials=creds)

    resumen_global, lunes_sig, domingo_sig = recopilar_resumenes_globales(now_local)

    log_path = "data/email_log.json"
    log = load_log(log_path)
    from_name = str(emails_cfg_base.get("from_name", "")).strip() or "Calendario del Curso"

    total = 0

    print(f"[INFO] Fecha local usada: {now_local.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"[INFO] Dry run: {args.dry_run}")
    print(f"[INFO] Forzar: {args.forzar}")

    for prof, data in sorted(resumen_global.items()):
        nombre_prof = data["nombre"]
        to_email = data["email"]
        cc_list = sorted(data["cc"])

        send_key = f"resumen_global|{prof}|{lunes_sig.isoformat()}"
        if was_sent(log, send_key) and not args.forzar:
            print(f"[INFO] Ya enviado a {prof} para semana {lunes_sig}")
            continue

        subject = f"Resumen semanal {fmt_fecha(lunes_sig)}–{fmt_fecha(domingo_sig)}"
        body = construir_cuerpo_global(
            nombre_prof=nombre_prof,
            fecha_inicio=fmt_fecha(lunes_sig),
            fecha_fin=fmt_fecha(domingo_sig),
            resumen_prof=data,
            from_name=from_name
        )

        if args.dry_run:
            print("\n==================================================")
            print(f"PROFESOR: {prof} ({nombre_prof})")
            print(f"TO: {to_email}")
            print(f"CC: {', '.join(cc_list) if cc_list else '(sin cc)'}")
            print(f"SUBJECT: {subject}")
            print("--------------------------------------------------")
            print(body)
            print("==================================================\n")
        else:
            gmail_send(service, to_email, subject, body, cc_list=cc_list, from_name=from_name)

        mark_sent(log, send_key)
        total += 1

    save_log(log_path, log)
    print(f"\nListo. Correos enviados/simulados: {total}")
    print("Log actualizado:", log_path)
    
    
    
if __name__ == "__main__":
    main()