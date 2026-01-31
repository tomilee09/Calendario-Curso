# enviar_recordatorios.py
import os
import json
import base64
import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, time as dtime, date
from zoneinfo import ZoneInfo

import yaml
import pandas as pd

from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


# -----------------------------
# Helpers YAML / Time
# -----------------------------
ORDEN_DIAS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def hhmm_to_time(s: str) -> dtime:
    h, m = s.split(":")
    return dtime(int(h), int(m))

def fmt_fecha(d: date) -> str:
    return pd.Timestamp(d).strftime("%d/%m/%Y")

def split_profesores(s: str):
    if not s:
        return []
    # "AR, JCS" -> ["AR","JCS"]
    return [x.strip() for x in s.split(",") if x.strip()]

def dia_en_semana(lunes: pd.Timestamp, dia_semana: str) -> pd.Timestamp:
    idx = ORDEN_DIAS.index(dia_semana)
    return pd.Timestamp(lunes.date()) + pd.Timedelta(days=idx)


# -----------------------------
# Construir “eventos” desde YAML
# -----------------------------
@dataclass
class Evento:
    tipo: str                 # "mision" | "evaluacion" | "examen"
    titulo: str               # texto principal
    seccion: str
    fecha: date
    hora: str                 # "HH:MM" o "" (si all-day)
    profesores: str           # "TY, IG"
    actividad: str = ""
    evaluacion: str = ""
    tema: str = ""
    semana: str = ""
    observaciones: str = ""

    def uid(self):
        # identificador estable para logging (incluye tipo+fecha+titulo+seccion)
        return f"{self.tipo}|{self.fecha.isoformat()}|{self.seccion}|{self.titulo}"


def construir_eventos(config: dict) -> list[Evento]:
    inicio = pd.Timestamp(config["periodo"]["fecha_inicio"])
    nsem = int(config["periodo"]["numero_semanas"])
    secciones = config["secciones"]

    # mapa profesores base por seccion+actividad
    prof_base = {}
    for r in config.get("profesores_base", []) or []:
        prof_base[(r["seccion"], r["actividad"])] = r.get("profesores", "")

    # temas por semana
    temas_sem = {int(k): str(v) for k, v in (config.get("temas_por_semana", {}) or {}).items()}

    eventos: list[Evento] = []

    # ---- MISIONES ----
    for m in config.get("misiones", []) or []:
        fecha_ts = pd.Timestamp(m["fecha"]).date()
        eventos.append(Evento(
            tipo="mision",
            titulo=m.get("mision", "Misión"),
            seccion=m.get("seccion", "Equipo docente"),
            fecha=fecha_ts,
            hora="",  # all-day
            profesores=m.get("profesores", ""),
            observaciones=m.get("observaciones", "")
        ))

    # ---- EXÁMENES ----
    ex = config.get("examenes", {}) or {}
    for e in ex.get("eventos", []) or []:
        fecha_ts = pd.Timestamp(e["fecha"]).date()
        hora = f"{e.get('inicio','')}-{e.get('fin','')}".strip("-")
        eventos.append(Evento(
            tipo="examen",
            titulo=e.get("actividad", "Examen"),
            seccion=e.get("seccion", ""),
            fecha=fecha_ts,
            hora=hora,
            profesores=e.get("profesores", ""),
            observaciones=e.get("observaciones", "")
        ))

    # ---- EVALUACIONES por_filtro: reconstruimos fecha/hora a partir del horario base ----
    for ev in config.get("evaluaciones", []) or []:
        if ev.get("modo") != "por_filtro":
            continue

        secc = ev["seccion"]
        semana = int(ev["semana"])
        actividad = ev["actividad"]  # "Clase teórica" / "Seminario" / "Laboratorio"
        tipo_eval = ev.get("tipo", "")
        obs = ev.get("observaciones", "")

        # obtener cfg por actividad
        cfg = secciones[secc]
        if actividad == "Clase teórica":
            clave = "teorica"
        elif actividad == "Seminario":
            clave = "seminario"
        elif actividad == "Laboratorio":
            clave = "lab"
        else:
            # si inventas otra cosa, no sabremos calcular
            continue

        lunes = inicio + pd.Timedelta(days=7*(semana-1))
        fecha_evento = dia_en_semana(lunes, cfg[clave]["dia_semana"]).date()
        hora = f"{cfg[clave]['inicio']}-{cfg[clave]['fin']}"

        profesores = prof_base.get((secc, actividad), "")

        eventos.append(Evento(
            tipo="evaluacion",
            titulo=f"Evaluación: {tipo_eval}",
            seccion=secc,
            fecha=fecha_evento,
            hora=hora,
            profesores=profesores,
            actividad=actividad,
            evaluacion=tipo_eval,
            tema=temas_sem.get(semana, ""),
            semana=str(semana),
            observaciones=obs
        ))

    return eventos


# -----------------------------
# Gmail API auth (token + credentials)
# -----------------------------
def load_gmail_credentials(scopes=None):
    if scopes is None:
        scopes = ["https://www.googleapis.com/auth/gmail.send"]

    # 1) Preferir secrets en env (ideal para GitHub Actions)
    token_json_env = os.getenv("GMAIL_TOKEN_JSON", "").strip()
    creds_json_env = os.getenv("GMAIL_CREDENTIALS_JSON", "").strip()

    if token_json_env:
        token_info = json.loads(token_json_env)
        creds = Credentials.from_authorized_user_info(token_info, scopes=scopes)
        # Si viene refresh_token, google-auth refresca solo
        return creds

    # 2) Si no hay env, usar archivos locales por defecto
    # token.json debe existir si ya hiciste OAuth en tu máquina
    token_path = os.getenv("GMAIL_TOKEN_PATH", "token.json")
    if not os.path.exists(token_path):
        raise RuntimeError(
            "No encuentro token.json. Define env GMAIL_TOKEN_JSON (recomendado en CI) "
            "o coloca token.json junto al script."
        )

    creds = Credentials.from_authorized_user_file(token_path, scopes=scopes)
    return creds


def gmail_send(service, to_email: str, subject: str, body: str, cc_list=None, from_name=""):
    if cc_list is None:
        cc_list = []

    msg = MIMEText(body, "plain", "utf-8")
    msg["to"] = to_email
    msg["subject"] = subject
    if from_name:
        msg["from"] = from_name
    if cc_list:
        msg["cc"] = ", ".join([x for x in cc_list if x.strip()])

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()


# -----------------------------
# Log persistente (no reenviar)
# -----------------------------
def load_log(path: str) -> dict:
    if not os.path.exists(path):
        return {"sent": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_log(path: str, log: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def mark_sent(log: dict, key: str):
    log.setdefault("sent", {})[key] = datetime.utcnow().isoformat() + "Z"

def was_sent(log: dict, key: str) -> bool:
    return key in log.get("sent", {})


# -----------------------------
# Motor de recordatorios
# -----------------------------
def should_send_today(event_date: date, send_days_before: int, now_local: datetime, hora_envio: dtime):
    """
    Enviamos si hoy == (fecha_evento - send_days_before) y ya pasamos la hora_envio.
    """
    target_day = event_date - timedelta(days=send_days_before)
    if now_local.date() != target_day:
        return False
    return now_local.time() >= hora_envio


def format_template(tpl: str, ctx: dict) -> str:
    # tpl usa {campo}
    return tpl.format(**ctx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="calendario_config.yml")
    ap.add_argument("--dry-run", action="store_true", help="No envía correos, solo imprime lo que haría.")
    args = ap.parse_args()

    config = load_yaml(args.config)
    tz = ZoneInfo(config["curso"]["timezone"])
    now_local = datetime.now(tz)

    emails_cfg = config.get("emails", {}) or {}
    rules = emails_cfg.get("reglas", {}) or {}
    prof_map = emails_cfg.get("profesor_a_email", {}) or {}
    cc_list = emails_cfg.get("cc", []) or []
    from_name = emails_cfg.get("from_name", "")
    log_path = emails_cfg.get("estado_envios_path", "data/email_log.json")

    eventos = construir_eventos(config)
    log = load_log(log_path)

    # preparar Gmail
    service = None
    if not args.dry_run:
        creds = load_gmail_credentials()
        service = build("gmail", "v1", credentials=creds)

    enviados = 0

    for ev in eventos:
        if ev.tipo not in rules:
            continue

        regla = rules[ev.tipo]
        dias_antes = regla.get("enviar_dias_antes", []) or []
        hora_envio = hhmm_to_time(regla.get("hora_envio", "09:00"))
        asunto_tpl = regla.get("asunto", "[Curso] Recordatorio")
        cuerpo_tpl = regla.get("cuerpo", "Hola {nombre_prof}...")

        # contexto base
        base_ctx = {
            "from_name": from_name,
            "titulo": ev.titulo,
            "seccion": ev.seccion,
            "fecha": fmt_fecha(ev.fecha),
            "hora": ev.hora or "(sin horario)",
            "actividad": ev.actividad,
            "evaluacion": ev.evaluacion,
            "tema": ev.tema,
            "semana": ev.semana,
            "observaciones": ev.observaciones or "",
        }

        for d_before in dias_antes:
            if not should_send_today(ev.fecha, int(d_before), now_local, hora_envio):
                continue

            # clave única por (evento + d_before)
            send_key = ev.uid() + f"|d_before={int(d_before)}"
            if was_sent(log, send_key):
                continue

            # a quién enviar
            profs = split_profesores(ev.profesores)
            if not profs:
                # si no hay profesores, no enviamos
                continue

            for prof in profs:
                to_email = prof_map.get(prof, "").strip()
                if not to_email:
                    # si falta map, salta pero no falla todo
                    print(f"[WARN] No hay email para profesor '{prof}' (evento: {ev.uid()})")
                    continue

                ctx = dict(base_ctx)
                ctx["nombre_prof"] = prof

                subject = format_template(asunto_tpl, ctx)
                body = format_template(cuerpo_tpl, ctx)

                if args.dry_run:
                    print("---- DRY RUN ----")
                    print("TO:", to_email)
                    print("SUBJECT:", subject)
                    print(body)
                    print("-----------------")
                else:
                    gmail_send(service, to_email, subject, body, cc_list=cc_list, from_name=from_name)

                enviados += 1

            # marcar como enviado (una sola vez por evento+lead)
            mark_sent(log, send_key)
            save_log(log_path, log)

    print(f"Listo. Correos enviados (o simulados): {enviados}")
    print(f"Log: {log_path}")


if __name__ == "__main__":
    main()