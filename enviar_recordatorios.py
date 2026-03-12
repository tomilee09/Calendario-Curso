# import os
# import json
# import base64
# import argparse
# from datetime import datetime, timedelta
# from zoneinfo import ZoneInfo

# import yaml
# import pandas as pd

# from email.mime.text import MIMEText
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build


# # ============================================================
# # CONFIG DE CURSOS
# # ============================================================
# CURSOS = {
#     "fokito": {
#         "config_path": os.path.join("config", "calendario_fokito.yml"),
#         "misiones_path": os.path.join("data", "fokito", "misiones.xlsx"),
#     },
#     "tecnologia_medica": {
#         "config_path": os.path.join("config", "calendario_tecnologia_medica.yml"),
#         "misiones_path": os.path.join("data", "tecnologia_medica", "misiones.xlsx"),
#     },
#     "medicina": {
#         "config_path": os.path.join("config", "calendario_medicina.yml"),
#         "misiones_path": os.path.join("data", "medicina", "misiones.xlsx"),
#     },
#     "enobnu": {
#         "config_path": os.path.join("config", "calendario_enobnu.yml"),
#         "misiones_path": os.path.join("data", "enobnu", "misiones.xlsx"),
#     },
# }


# # ============================================================
# # HELPERS
# # ============================================================
# ORDEN_DIAS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# PASO_LABELS = {
#     "pedir_preguntas": "Proponer preguntas",
#     "construir_control": "Construcción evaluación",
#     "pauta_prueba": "Construcción pauta",
#     "revisar_prueba": "Revisar evaluación",
#     "escanear": "Escanear evaluación",
#     "corregir_y_notas": "Corregir y poner notas",
#     "revisar_tp": "Revisar TP y poner nota",
#     "revision_guia": "Revisión de guía",
#     "subir_pauta_controles": "Subir pauta controles",
#     "pauta_seminario": "Pauta seminario",
#     "presentacion_grupal": "Presentación grupal seminario",
#     "construir_examen": "Construcción examen",
#     "pauta_examen": "Pauta examen",
#     "corregir_examen": "Corregir examen",
#     "revision_actividad_autonoma": "Revisión actividad autónoma",
#     "revision_controles_y_nota": "Revisión controles y poner nota",
#     "revisar_pruebas": "Revisar pruebas",
# }


# def load_yaml(path: str) -> dict:
#     with open(path, "r", encoding="utf-8") as f:
#         return yaml.safe_load(f)


# def split_profesores(s):
#     if not s or pd.isna(s):
#         return []
#     return [x.strip() for x in str(s).split(",") if x.strip()]


# def fmt_fecha(x) -> str:
#     ts = pd.to_datetime(x, errors="coerce")
#     if pd.isna(ts):
#         return ""
#     return ts.strftime("%d/%m/%Y")


# def hhmm_to_time(s: str):
#     h, m = s.split(":")
#     return int(h), int(m)


# def nombre_paso(paso: str) -> str:
#     paso = str(paso).strip()
#     return PASO_LABELS.get(paso, paso)


# def inicio_fin_semana_siguiente(now_local: datetime):
#     # lunes de esta semana
#     lunes_actual = now_local.date() - timedelta(days=now_local.weekday())
#     lunes_siguiente = lunes_actual + timedelta(days=7)
#     domingo_siguiente = lunes_siguiente + timedelta(days=6)
#     return lunes_siguiente, domingo_siguiente


# def curso_label(config: dict, fallback: str) -> str:
#     return str(config.get("curso", {}).get("nombre", fallback)).strip() or fallback


# # ============================================================
# # GMAIL
# # ============================================================
# def load_gmail_credentials(scopes=None):
#     if scopes is None:
#         scopes = ["https://www.googleapis.com/auth/gmail.send"]

#     token_json_env = os.getenv("GMAIL_TOKEN_JSON", "").strip()
#     if token_json_env:
#         token_info = json.loads(token_json_env)
#         return Credentials.from_authorized_user_info(token_info, scopes=scopes)

#     token_path = os.getenv("GMAIL_TOKEN_PATH", "token.json")
#     if not os.path.exists(token_path):
#         raise RuntimeError(
#             "No encuentro token.json. Define GMAIL_TOKEN_JSON en secrets o coloca token.json local."
#         )

#     return Credentials.from_authorized_user_file(token_path, scopes=scopes)


# def gmail_send(service, to_email: str, subject: str, body: str, cc_list=None, from_name=""):
#     if cc_list is None:
#         cc_list = []

#     msg = MIMEText(body, "plain", "utf-8")
#     msg["to"] = to_email
#     msg["subject"] = subject
#     if from_name:
#         msg["from"] = from_name
#     if cc_list:
#         msg["cc"] = ", ".join([x for x in cc_list if str(x).strip()])

#     raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
#     return service.users().messages().send(userId="me", body={"raw": raw}).execute()


# # ============================================================
# # LOG
# # ============================================================
# def load_log(path: str) -> dict:
#     if not os.path.exists(path):
#         return {"sent": {}}
#     with open(path, "r", encoding="utf-8") as f:
#         return json.load(f)


# def save_log(path: str, log: dict):
#     os.makedirs(os.path.dirname(path), exist_ok=True)
#     with open(path, "w", encoding="utf-8") as f:
#         json.dump(log, f, ensure_ascii=False, indent=2)


# def was_sent(log: dict, key: str) -> bool:
#     return key in log.get("sent", {})


# def mark_sent(log: dict, key: str):
#     log.setdefault("sent", {})[key] = datetime.utcnow().isoformat() + "Z"


# # ============================================================
# # CARGA DE MISIONES
# # ============================================================
# def cargar_misiones_excel(path: str) -> pd.DataFrame:
#     if not os.path.exists(path):
#         return pd.DataFrame()

#     try:
#         df = pd.read_excel(path, sheet_name="Misiones")
#     except Exception:
#         return pd.DataFrame()

#     if df.empty:
#         return df

#     for c in ["fecha_limite", "fecha_evento"]:
#         if c in df.columns:
#             df[c] = pd.to_datetime(df[c], errors="coerce")

#     for c in ["evento", "paso", "sección", "responsables", "detalle", "estado"]:
#         if c in df.columns:
#             df[c] = df[c].fillna("").astype(str)

#     return df


# def construir_lista_misiones_texto(df_prof: pd.DataFrame) -> str:
#     lineas = []

#     for _, r in df_prof.iterrows():
#         fecha_limite = fmt_fecha(r.get("fecha_limite", ""))
#         fecha_evento = fmt_fecha(r.get("fecha_evento", ""))
#         evento = str(r.get("evento", "")).strip()
#         paso = nombre_paso(r.get("paso", ""))
#         seccion = str(r.get("sección", "")).strip()
#         detalle = str(r.get("detalle", "")).strip()
#         estado = str(r.get("estado", "")).strip()

#         bloque = f"- {fecha_limite} | {paso}"
#         if evento:
#             bloque += f" | {evento}"
#         if seccion:
#             bloque += f" | {seccion}"
#         if fecha_evento:
#             bloque += f" | evalúa: {fecha_evento}"
#         if detalle:
#             bloque += f"\n  {detalle}"
#         if estado:
#             bloque += f"\n  Estado: {estado}"

#         lineas.append(bloque)

#     if not lineas:
#         return "No tienes misiones asignadas para la próxima semana."

#     return "\n\n".join(lineas)


# # ============================================================
# # REGLAS DE ENVÍO
# # ============================================================
# def debe_enviar_resumen_hoy(now_local: datetime, regla: dict, forzar: bool = False) -> bool:
#     if forzar:
#         return True

#     dia_envio = str(regla.get("dia_envio", "Friday")).strip()
#     hora_envio = str(regla.get("hora_envio", "09:00")).strip()

#     if dia_envio not in ORDEN_DIAS:
#         dia_envio = "Friday"

#     idx_objetivo = ORDEN_DIAS.index(dia_envio)
#     if now_local.weekday() != idx_objetivo:
#         return False

#     h, m = hhmm_to_time(hora_envio)
#     return (now_local.hour, now_local.minute) >= (h, m)


# # ============================================================
# # ENVÍO POR CURSO
# # ============================================================
# def procesar_curso(curso_key: str, info: dict, now_local: datetime, dry_run: bool, forzar: bool, service):
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

#     profesor_a_email = emails_cfg.get("profesor_a_email", {}) or {}
#     from_name = str(emails_cfg.get("from_name", "")).strip()
#     cc_list = emails_cfg.get("cc", []) or []
#     log_path = emails_cfg.get("estado_envios_path", "data/email_log.json")

#     df = cargar_misiones_excel(misiones_path)
#     if df.empty:
#         print(f"[INFO] {curso_key}: no hay misiones en {misiones_path}")
#         return 0, log_path

#     lunes_sig, domingo_sig = inicio_fin_semana_siguiente(now_local)

#     df = df.dropna(subset=["fecha_limite"]).copy()
#     df = df[
#         (df["fecha_limite"].dt.date >= lunes_sig) &
#         (df["fecha_limite"].dt.date <= domingo_sig)
#     ].copy()

#     if df.empty:
#         print(f"[INFO] {curso_key}: no hay misiones para la semana siguiente.")
#         return 0, log_path

#     log = load_log(log_path)
#     enviados = 0
#     nombre_curso = curso_label(config, curso_key)

#     # profesores presentes en responsables
#     profes_presentes = set()
#     for s in df["responsables"].dropna().unique():
#         for p in split_profesores(s):
#             profes_presentes.add(p)

#     for prof in sorted(profes_presentes):
#         to_email = str(profesor_a_email.get(prof, "")).strip()
#         if not to_email:
#             print(f"[WARN] {curso_key}: no hay email para {prof}")
#             continue

#         df_prof = df[df["responsables"].apply(lambda x: prof in split_profesores(x))].copy()
#         if df_prof.empty:
#             continue

#         df_prof = df_prof.sort_values(["fecha_limite", "evento", "paso", "sección"])

#         send_key = f"resumen_semanal|{curso_key}|{prof}|{lunes_sig.isoformat()}"
#         if was_sent(log, send_key) and not forzar:
#             print(f"[INFO] {curso_key}: ya enviado a {prof} para semana {lunes_sig}")
#             continue

#         lista_misiones = construir_lista_misiones_texto(df_prof)

#         ctx = {
#             "curso": nombre_curso,
#             "nombre_prof": prof,
#             "fecha_inicio_semana": fmt_fecha(lunes_sig),
#             "fecha_fin_semana": fmt_fecha(domingo_sig),
#             "lista_misiones": lista_misiones,
#             "from_name": from_name,
#         }

#         subject = str(regla.get("asunto", "[{curso}] Misiones semana")).format(**ctx)
#         body = str(regla.get("cuerpo", "Hola {nombre_prof}:\n\n{lista_misiones}\n\n— {from_name}")).format(**ctx)

#         if dry_run:
#             print("\n==============================")
#             print(f"CURSO: {curso_key}")
#             print(f"TO: {to_email}")
#             print(f"SUBJECT: {subject}")
#             print(body)
#             print("==============================\n")
#         else:
#             gmail_send(service, to_email, subject, body, cc_list=cc_list, from_name=from_name)

#         mark_sent(log, send_key)
#         enviados += 1

#     save_log(log_path, log)
#     return enviados, log_path


# # ============================================================
# # MAIN
# # ============================================================
# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("--curso", default="todos", help="fokito | tecnologia_medica | medicina | enobnu | todos")
#     ap.add_argument("--dry-run", action="store_true", help="No envía correos, solo imprime.")
#     ap.add_argument("--forzar", action="store_true", help="Envía aunque hoy no sea el día/hora configurado.")
#     ap.add_argument("--fecha", default="", help="Fecha/hora simulada local, formato YYYY-MM-DD o YYYY-MM-DD HH:MM")
#     args = ap.parse_args()

#     # timezone: usamos el del primer YAML disponible, o Chile por defecto
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
CURSOS = {
    "fokito": {
        "config_path": os.path.join("config", "calendario_fokito.yml"),
        "misiones_path": os.path.join("data", "fokito", "misiones.xlsx"),
    },
    "tecnologia_medica": {
        "config_path": os.path.join("config", "calendario_tecnologia_medica.yml"),
        "misiones_path": os.path.join("data", "tecnologia_medica", "misiones.xlsx"),
    },
    "medicina": {
        "config_path": os.path.join("config", "calendario_medicina.yml"),
        "misiones_path": os.path.join("data", "medicina", "misiones.xlsx"),
    },
    "enobnu": {
        "config_path": os.path.join("config", "calendario_enobnu.yml"),
        "misiones_path": os.path.join("data", "enobnu", "misiones.xlsx"),
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
def obtener_diccionario_profesores(emails_cfg):
    """
    Devuelve un dict:
    {
      "TY": {"nombre": "Tomás", "email": "xxx"},
      ...
    }

    Soporta dos formatos:
    1) Nuevo:
       emails:
         profesores:
           TY:
             nombre: "Tomás"
             email: "..."
    2) Antiguo:
       emails:
         profesor_a_email:
           TY: "..."
    """
    profesores = {}

    bloque_nuevo = emails_cfg.get("profesores", {}) or {}
    for codigo, data in bloque_nuevo.items():
        if isinstance(data, dict):
            nombre = str(data.get("nombre", codigo)).strip() or codigo
            email = str(data.get("email", "")).strip()
        else:
            nombre = str(codigo).strip()
            email = str(data).strip()

        if email:
            profesores[str(codigo).strip()] = {
                "nombre": nombre,
                "email": email
            }

    bloque_antiguo = emails_cfg.get("profesor_a_email", {}) or {}
    for codigo, email in bloque_antiguo.items():
        codigo = str(codigo).strip()
        email = str(email).strip()
        if codigo and email and codigo not in profesores:
            profesores[codigo] = {
                "nombre": codigo,
                "email": email
            }

    return profesores


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


def construir_lista_misiones_texto(df_prof):
    """
    Formato legible.
    """
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
def procesar_curso(curso_key, info, now_local, dry_run, forzar, service):
    config_path = info["config_path"]
    misiones_path = info["misiones_path"]

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

    df = cargar_misiones_excel(misiones_path)

    lunes_sig, domingo_sig = inicio_fin_semana_siguiente(now_local)

    if not df.empty:
        df = df.dropna(subset=["fecha_limite"]).copy()
        df = df[
            (df["fecha_limite"].dt.date >= lunes_sig) &
            (df["fecha_limite"].dt.date <= domingo_sig)
        ].copy()

    log = load_log(log_path)
    enviados = 0
    nombre_curso = curso_label(config, curso_key)

    # Profesores a considerar:
    # 1) todos los definidos en emails.profesores / profesor_a_email
    # 2) aunque no tengan misiones, igual reciben correo
    profes_a_considerar = sorted(profesores_dict.keys())

    # Si quieres restringir solo a quienes aparecen como responsables alguna vez, comenta lo de arriba
    # y usa esto:
    # profes_a_considerar = set()
    # if not df.empty and "responsables" in df.columns:
    #     for s in df["responsables"].dropna().unique():
    #         for p in split_profesores(s):
    #             profes_a_considerar.add(p)
    # profes_a_considerar = sorted(profes_a_considerar)

    for prof in profes_a_considerar:
        info_prof = obtener_info_profesor(profesores_dict, prof)
        to_email = str(info_prof.get("email", "")).strip()
        nombre_prof = str(info_prof.get("nombre", prof)).strip() or prof

        if not to_email:
            print(f"[WARN] {curso_key}: no hay email para {prof}")
            continue

        if df.empty:
            df_prof = pd.DataFrame()
        else:
            df_prof = df[df["responsables"].apply(lambda x: prof in split_profesores(x))].copy()

        if not df_prof.empty:
            df_prof = df_prof.sort_values(["fecha_limite", "evento", "paso", "sección"])

        secciones_prof = []
        if not df_prof.empty and "sección" in df_prof.columns:
            secciones_prof = [str(x).strip() for x in df_prof["sección"].dropna().unique() if str(x).strip()]

        cc_list = obtener_cc_por_secciones(secciones_prof, emails_cfg, profesores_dict)

        send_key = f"resumen_semanal|{curso_key}|{prof}|{lunes_sig.isoformat()}"
        if was_sent(log, send_key) and not forzar:
            print(f"[INFO] {curso_key}: ya enviado a {prof} para semana {lunes_sig}")
            continue

        lista_misiones = construir_lista_misiones_texto(df_prof)

        ctx = {
            "curso": nombre_curso,
            "nombre_prof": nombre_prof,
            "codigo_prof": prof,
            "fecha_inicio_semana": fmt_fecha(lunes_sig),
            "fecha_fin_semana": fmt_fecha(domingo_sig),
            "lista_misiones": lista_misiones,
            "from_name": from_name,
        }

        subject = str(
            regla.get("asunto", "[{curso}] Misiones para la semana del {fecha_inicio_semana}")
        ).format(**ctx)

        body = str(
            regla.get(
                "cuerpo",
                "Hola {nombre_prof}:\n\n{lista_misiones}\n\n— {from_name}"
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


# ============================================================
# MAIN
# ============================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--curso", default="todos", help="fokito | tecnologia_medica | medicina | enobnu | todos")
    ap.add_argument("--dry-run", action="store_true", help="No envía correos, solo imprime.")
    ap.add_argument("--forzar", action="store_true", help="Envía aunque hoy no sea el día/hora configurado.")
    ap.add_argument("--fecha", default="", help="Fecha/hora simulada local, formato YYYY-MM-DD o YYYY-MM-DD HH:MM")
    args = ap.parse_args()

    tz_name = "America/Santiago"
    for _, info in CURSOS.items():
        if os.path.exists(info["config_path"]):
            try:
                cfg = load_yaml(info["config_path"])
                tz_name = cfg.get("curso", {}).get("timezone", tz_name)
                break
            except Exception:
                pass

    tz = ZoneInfo(tz_name)

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

    service = None
    if not args.dry_run:
        creds = load_gmail_credentials()
        service = build("gmail", "v1", credentials=creds)

    if args.curso == "todos":
        cursos_a_procesar = list(CURSOS.keys())
    else:
        if args.curso not in CURSOS:
            raise SystemExit(f"Curso inválido: {args.curso}")
        cursos_a_procesar = [args.curso]

    total = 0
    logs_tocados = set()

    print(f"[INFO] Fecha local usada: {now_local.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"[INFO] Dry run: {args.dry_run}")
    print(f"[INFO] Forzar: {args.forzar}")

    for curso_key in cursos_a_procesar:
        enviados, log_path = procesar_curso(
            curso_key=curso_key,
            info=CURSOS[curso_key],
            now_local=now_local,
            dry_run=args.dry_run,
            forzar=args.forzar,
            service=service,
        )
        total += enviados
        if log_path:
            logs_tocados.add(log_path)

    print(f"\nListo. Correos enviados/simulados: {total}")
    if logs_tocados:
        print("Logs actualizados:")
        for p in sorted(logs_tocados):
            print("-", p)


if __name__ == "__main__":
    main()