import os
import yaml


# ============================================================
# CONFIG
# ============================================================
CURSOS = {
    "fokito": "config/calendario_fokito.yml",
    "tecnologia_medica": "config/calendario_tecnologia_medica.yml",
    "medicina": "config/calendario_medicina.yml",
    "ennuob": "config/calendario_enobnu.yml",
}

CARPETA_SALIDA = "data/correos_misiones_por_grupo"

COLUMNAS = ["Conocimiento", "Comprensión", "Análisis"]

PATRONES_TEMAS = [
    ["Lógica 1", "Lógica 2", "Lógica 3"],
    ["Lógica 2", "Lógica 3", "Lógica 1"],
    ["Lógica 3", "Lógica 1", "Lógica 2"],
    ["Lógica 1", "Lógica 3", "Lógica 2"],
]


# ============================================================
# HELPERS
# ============================================================
def cargar_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def asegurar_directorio(path):
    if not os.path.exists(path):
        os.makedirs(path)


def split_profes(valor):
    if valor is None:
        return []

    if isinstance(valor, list):
        return [str(x).strip() for x in valor if str(x).strip()]

    texto = str(valor).strip()
    if not texto:
        return []

    return [x.strip() for x in texto.split(",") if x.strip()]


def obtener_nombre_bonito_curso(config, codigo_curso):
    nombre = str(config.get("curso", {}).get("nombre", "")).strip()
    if nombre:
        return nombre

    mapa = {
        "fokito": "Fokito",
        "tecnologia_medica": "Tecnología Médica",
        "medicina": "Medicina",
        "ennuob": "Ennuob",
    }
    return mapa.get(codigo_curso, codigo_curso.replace("_", " ").title())


def obtener_profes_seminario_por_seccion(config):
    """
    Devuelve:
    {
        "Sección 1": ["JM", "MB", "VB"],
        "Sección 2": ["NV", "RM", "SM"],
        ...
    }
    """
    salida = {}
    base = config.get("calendario", {}).get("profesores_base", []) or []

    for fila in base:
        seccion = str(fila.get("seccion", "")).strip()
        actividad = str(fila.get("actividad", "")).strip()

        if actividad != "Seminario":
            continue

        profes = split_profes(fila.get("profesores", []))
        if seccion:
            salida[seccion] = profes

    return salida


def construir_tabla_automatica(profes_yaml):
    tabla = {}

    for i, prof in enumerate(profes_yaml):
        tabla[prof] = PATRONES_TEMAS[i % len(PATRONES_TEMAS)]

    return tabla


def formatear_tabla_html(tabla_dict):
    profes = list(tabla_dict.keys())

    if not profes:
        return "<p>(Sin profesores asignados)</p>"

    filas = []
    filas.append("""
    <table style="border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; margin: 12px 0;">
      <tr>
        <th style="border:1px solid #999; padding:6px 10px; background:#f2f2f2; text-align:left;">Profesor</th>
        <th style="border:1px solid #999; padding:6px 10px; background:#f2f2f2; text-align:left;">Conocimiento</th>
        <th style="border:1px solid #999; padding:6px 10px; background:#f2f2f2; text-align:left;">Comprensión</th>
        <th style="border:1px solid #999; padding:6px 10px; background:#f2f2f2; text-align:left;">Análisis</th>
      </tr>
    """)

    for p in profes:
        v1 = str(tabla_dict[p][0]) if len(tabla_dict[p]) > 0 else ""
        v2 = str(tabla_dict[p][1]) if len(tabla_dict[p]) > 1 else ""
        v3 = str(tabla_dict[p][2]) if len(tabla_dict[p]) > 2 else ""

        filas.append(f"""
      <tr>
        <td style="border:1px solid #999; padding:6px 10px;"><b>{p}</b></td>
        <td style="border:1px solid #999; padding:6px 10px;">{v1}</td>
        <td style="border:1px solid #999; padding:6px 10px;">{v2}</td>
        <td style="border:1px solid #999; padding:6px 10px;">{v3}</td>
      </tr>
        """)

    filas.append("</table>")
    return "\n".join(filas)


def slugificar(texto):
    texto = str(texto).strip().lower()
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    texto = texto.replace("ñ", "n")
    texto = texto.replace(" ", "_")
    return texto


def construir_correo(nombre_curso, seccion, tabla_dict):
    tabla_html = formatear_tabla_html(tabla_dict)

    asunto = f"[{nombre_curso} - {seccion}] Solicitud de preguntas para la prueba"

    cuerpo = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>{asunto}</title>
</head>
<body style="font-family: Arial, sans-serif; font-size: 14px; color: #111;">

<p>Buen día,</p>

<p>Tenemos la misión de realizar preguntas para el primer certamen, les pedimos hagan preguntas de acuerdo a la siguiente distribución.</p>

{tabla_html}

<p>Para ver el tipo de preguntas que se les piden pueden ver las preguntas de los seminarios, las preguntas autónomas, los controles formativos y los controles sumativos.</p>

<p>La idea es que las preguntas tengan un contexto de salud.</p>

<p>Las preguntas deben subirse al onedrive en formato word o latex (puede ser link a overleaf), y debe venir con la solución en cualquier formato, es decir, solución escrita a mano o en el mismo word/latex (se debe diferenciar claramente la pregunta con las alternativas de la sección de la solución).</p>

<p>Las preguntas deben venir listas para poner en la prueba y deben tener 4 alternativas. Se debe indicar los motivos por los cuales se eligió a los 3 distractores de forma rápida, por ejemplo puede ser algo así: d) Verdadero (distractor, pues les puede faltar una negación al aplicar morgan).</p>

<p><b>Plazo de entrega:</b> jueves 09 de abril a las 23:59</p>

<p><b>Responder este correo indicando que fue leído</b></p>

<p>¡Que les vaya muy bien!</p>

<p>J. Tomás Yáñez</p>

</body>
</html>
"""
    return asunto, cuerpo


# ============================================================
# MAIN
# ============================================================
def main():
    asegurar_directorio(CARPETA_SALIDA)

    for codigo_curso, path_yml in CURSOS.items():
        if not os.path.exists(path_yml):
            print(f"⚠️ No existe {path_yml}")
            continue

        config = cargar_yaml(path_yml)
        nombre_bonito = obtener_nombre_bonito_curso(config, codigo_curso)
        profes_por_seccion = obtener_profes_seminario_por_seccion(config)

        for seccion, profes_yaml in profes_por_seccion.items():
            tabla_filtrada = construir_tabla_automatica(profes_yaml)

            asunto, cuerpo = construir_correo(
                nombre_curso=nombre_bonito,
                seccion=seccion,
                tabla_dict=tabla_filtrada
            )

            nombre_archivo = f"correo_{codigo_curso}_{slugificar(seccion)}.html"
            path_salida = os.path.join(CARPETA_SALIDA, nombre_archivo)

            with open(path_salida, "w", encoding="utf-8") as f:
                f.write(cuerpo)

            print("=" * 80)
            print(f"CURSO: {nombre_bonito}")
            print(f"SECCIÓN: {seccion}")
            print(f"Archivo: {path_salida}")
            print("-" * 80)
            print(f"Asunto: {asunto}")

    print("✅ Correos por grupo generados.")


if __name__ == "__main__":
    main()