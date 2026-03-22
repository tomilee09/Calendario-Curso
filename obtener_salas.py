# # # # import sys
# # # # import time
# # # # from datetime import datetime

# # # # from bs4 import BeautifulSoup

# # # # from selenium import webdriver
# # # # from selenium.webdriver.common.by import By
# # # # from selenium.webdriver.support.ui import Select, WebDriverWait
# # # # from selenium.webdriver.support import expected_conditions as EC

# # # # URL = "http://consultaaulas.med.uchile.cl/consulta_clase.html"

# # # # CURSOS = {
# # # #     "fokito": {
# # # #         "codigo": "CBA0103",
# # # #         "nombre": "FOKITO",
# # # #         "secciones": [1, 2, 3, 4],
# # # #         "profes": {
# # # #             1: ["IG"],
# # # #             2: ["JCS"],
# # # #             3: ["AR"],
# # # #             4: ["CC"],
# # # #         },
# # # #     },
# # # #     "enobnu": {
# # # #         "codigo": "CBA0102",
# # # #         "nombre": "ENOBNU",
# # # #         "secciones": [1, 2, 3, 4],
# # # #         "profes": {
# # # #             1: [],
# # # #             2: [],
# # # #             3: [],
# # # #             4: [],
# # # #         },
# # # #     },
# # # #     "tecnologia_medica": {
# # # #         "codigo": "TMA01005",
# # # #         "nombre": "TECNOLOGÍA MÉDICA",
# # # #         "secciones": [1],
# # # #         "profes": {
# # # #             1: [],
# # # #         },
# # # #     },
# # # #     "medicina": {
# # # #         "codigo": "MED0101",
# # # #         "nombre": "MEDICINA",
# # # #         "secciones": [1, 2],
# # # #         "profes": {
# # # #             1: [],
# # # #             2: [],
# # # #         },
# # # #     },
# # # # }


# # # # def normalizar(txt):
# # # #     return " ".join(str(txt).replace("\xa0", " ").split()).strip()


# # # # def crear_driver():
# # # #     options = webdriver.ChromeOptions()
# # # #     # options.add_argument("--headless=new")   # si quieres ocultarlo, descomenta
# # # #     options.add_argument("--window-size=1400,1200")
# # # #     options.add_argument("--disable-blink-features=AutomationControlled")
# # # #     options.add_argument("--lang=es-CL")
# # # #     driver = webdriver.Chrome(options=options)
# # # #     return driver


# # # # def esperar_selector(driver, by, value, timeout=20):
# # # #     return WebDriverWait(driver, timeout).until(
# # # #         EC.presence_of_element_located((by, value))
# # # #     )


# # # # def obtener_opciones_select(driver):
# # # #     select_el = esperar_selector(driver, By.ID, "txtSelCurso", timeout=20)

# # # #     opciones = driver.execute_script("""
# # # #         const sel = arguments[0];
# # # #         return Array.from(sel.options).map(o => ({
# # # #             value: (o.value || '').trim(),
# # # #             text: (o.text || '').trim()
# # # #         }));
# # # #     """, select_el)

# # # #     salida = []
# # # #     for op in opciones:
# # # #         val = normalizar(op.get("value", ""))
# # # #         if val:
# # # #             salida.append(val)
# # # #     return salida


# # # # def buscar_opcion(opciones, codigo, seccion):
# # # #     objetivo = f"{codigo}-{seccion}".upper()

# # # #     candidatas = []
# # # #     for op in opciones:
# # # #         if objetivo in op.upper():
# # # #             candidatas.append(op)

# # # #     if not candidatas:
# # # #         return None

# # # #     for op in candidatas:
# # # #         if op.upper().endswith(objetivo):
# # # #             return op

# # # #     return candidatas[0]


# # # # def setear_fecha(driver, fecha_str):
# # # #     fecha_input = esperar_selector(driver, By.ID, "txtFecha", timeout=20)
# # # #     driver.execute_script("""
# # # #         const inp = arguments[0];
# # # #         inp.value = arguments[1];
# # # #         inp.dispatchEvent(new Event('input', { bubbles: true }));
# # # #         inp.dispatchEvent(new Event('change', { bubbles: true }));
# # # #     """, fecha_input, fecha_str)


# # # # def seleccionar_curso(driver, valor_opcion):
# # # #     select_el = esperar_selector(driver, By.ID, "txtSelCurso", timeout=20)

# # # #     # setear valor por JavaScript porque el sitio a veces deja el select no interactuable
# # # #     driver.execute_script("""
# # # #         const sel = arguments[0];
# # # #         const val = arguments[1];
# # # #         sel.value = val;
# # # #         sel.dispatchEvent(new Event('change', { bubbles: true }));
# # # #     """, select_el, valor_opcion)


# # # # def enviar_formulario(driver):
# # # #     form = esperar_selector(driver, By.ID, "form", timeout=20)
# # # #     driver.execute_script("arguments[0].submit();", form)


# # # # def extraer_resultados_html(driver, fecha_str, codigo, seccion):
# # # #     time.sleep(2)
# # # #     html = driver.page_source

# # # #     with open("debug_consultaaulas_selenium.html", "w", encoding="utf-8") as f:
# # # #         f.write(html)

# # # #     soup = BeautifulSoup(html, "html.parser")
# # # #     tablas = soup.find_all("table")

# # # #     objetivo = f"{codigo}-{seccion}".upper()
# # # #     filas_salida = []

# # # #     for tabla in tablas:
# # # #         texto_tabla = normalizar(tabla.get_text(" ", strip=True)).upper()
# # # #         if "ASIGNATURA:" not in texto_tabla:
# # # #             continue
# # # #         if objetivo not in texto_tabla:
# # # #             continue

# # # #         for tr in tabla.find_all("tr"):
# # # #             tds = tr.find_all("td")
# # # #             textos = [normalizar(td.get_text(" ", strip=True)) for td in tds]

# # # #             if len(textos) < 5:
# # # #                 continue

# # # #             cab = " ".join(textos[:5]).lower()
# # # #             if "día" in cab and "fecha" in cab and "horario" in cab and "sala" in cab:
# # # #                 continue

# # # #             dia, fecha, horario, sala, ubicacion = textos[:5]

# # # #             if fecha == fecha_str:
# # # #                 filas_salida.append({
# # # #                     "dia": dia,
# # # #                     "fecha": fecha,
# # # #                     "horario": horario,
# # # #                     "sala": sala,
# # # #                     "ubicacion": ubicacion,
# # # #                 })

# # # #     return filas_salida


# # # # def consultar_curso(fecha_str, curso_key):
# # # #     info = CURSOS[curso_key]
# # # #     driver = crear_driver()
# # # #     resultados = []

# # # #     try:
# # # #         driver.get(URL)

# # # #         opciones = obtener_opciones_select(driver)

# # # #         for seccion in info["secciones"]:
# # # #             driver.get(URL)

# # # #             esperar_selector(driver, By.ID, "txtSelCurso", timeout=20)
# # # #             time.sleep(1)

# # # #             setear_fecha(driver, fecha_str)
# # # #             time.sleep(0.5)

# # # #             opciones = obtener_opciones_select(driver)
# # # #             valor = buscar_opcion(opciones, info["codigo"], seccion)

# # # #             if not valor:
# # # #                 resultados.append({
# # # #                     "seccion": seccion,
# # # #                     "error": f"No encontré {info['codigo']}-{seccion} en el selector",
# # # #                     "filas": [],
# # # #                 })
# # # #                 continue

# # # #             seleccionar_curso(driver, valor)
# # # #             time.sleep(0.5)
# # # #             enviar_formulario(driver)

# # # #             filas = extraer_resultados_html(driver, fecha_str, info["codigo"], seccion)

# # # #             resultados.append({
# # # #                 "seccion": seccion,
# # # #                 "error": None,
# # # #                 "filas": filas,
# # # #             })

# # # #     finally:
# # # #         driver.quit()

# # # #     return resultados


# # # # def formatear_mensaje(fecha_str, curso_key, resultados):
# # # #     info = CURSOS[curso_key]

# # # #     out = []
# # # #     out.append(f"Salas para {info['nombre']} ({info['codigo']}) — {fecha_str}")
# # # #     out.append("")

# # # #     for bloque in resultados:
# # # #         seccion = bloque["seccion"]
# # # #         profes = ", ".join(info["profes"].get(seccion, [])) or "Por definir"

# # # #         out.append(f"Sección {seccion} — Profesor(es): {profes}")

# # # #         if bloque["error"]:
# # # #             out.append(f"  Sin datos: {bloque['error']}")
# # # #             out.append("")
# # # #             continue

# # # #         if not bloque["filas"]:
# # # #             out.append("  Sin sala publicada.")
# # # #             out.append("")
# # # #             continue

# # # #         for fila in bloque["filas"]:
# # # #             out.append(f"  • {fila['horario']} — {fila['sala']} ({fila['ubicacion']})")

# # # #         out.append("")

# # # #     return "\n".join(out).strip()


# # # # def main():
# # # #     if len(sys.argv) < 3:
# # # #         print("Uso: python3 obtener_salas.py DD-MM-AAAA curso")
# # # #         print("Ejemplo: python3 obtener_salas.py 26-03-2026 medicina")
# # # #         return

# # # #     fecha_str = sys.argv[1]
# # # #     curso_key = sys.argv[2].strip().lower()

# # # #     datetime.strptime(fecha_str, "%d-%m-%Y")

# # # #     if curso_key not in CURSOS:
# # # #         raise ValueError(f"Curso no reconocido: {curso_key}")

# # # #     resultados = consultar_curso(fecha_str, curso_key)
# # # #     mensaje = formatear_mensaje(fecha_str, curso_key, resultados)
# # # #     print(mensaje)


# # # # if __name__ == "__main__":
# # # #     main()







# # # import sys
# # # import time
# # # from datetime import datetime

# # # from bs4 import BeautifulSoup

# # # from selenium import webdriver
# # # from selenium.webdriver.common.by import By
# # # from selenium.webdriver.support.ui import WebDriverWait
# # # from selenium.webdriver.support import expected_conditions as EC

# # # URL = "http://consultaaulas.med.uchile.cl/consulta_clase.html"

# # # CURSOS = {
# # #     "fokito": {
# # #         "codigo": "CBA0103",
# # #         "nombre": "FOKITO",
# # #         "secciones": [1, 2, 3, 4],
# # #         "profes": {
# # #             1: ["IG"],
# # #             2: ["JCS"],
# # #             3: ["AR"],
# # #             4: ["CC"],
# # #         },
# # #     },
# # #     "enobnu": {
# # #         "codigo": "CBA0102",
# # #         "nombre": "ENOBNU",
# # #         "secciones": [1, 2, 3, 4],
# # #         "profes": {
# # #             1: [],
# # #             2: [],
# # #             3: [],
# # #             4: [],
# # #         },
# # #     },
# # #     "tecnologia_medica": {
# # #         "codigo": "TMA01005",
# # #         "nombre": "TECNOLOGÍA MÉDICA",
# # #         "secciones": [1, 2, 3, 4],
# # #         "profes": {
# # #             1: [],
# # #             2: [],
# # #             3: [],
# # #             4: [],
# # #         },
# # #     },
# # #     "medicina": {
# # #         "codigo": "MED0101",
# # #         "nombre": "MEDICINA",
# # #         "secciones": [1, 2],
# # #         "profes": {
# # #             1: ["Tomás Yáñez", "Maximiliano Bernal", "Eduardo Guerra", "Alexander Riquelme"],
# # #             2: ["Tomás Yáñez", "Maximiliano Bernal", "Eduardo Guerra", "Alexander Riquelme"],
# # #         },
# # #     },
# # # }


# # # def normalizar(txt):
# # #     return " ".join(str(txt).replace("\xa0", " ").split()).strip()


# # # def titulo_sugerido(fecha_dt):
# # #     meses = {
# # #         1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
# # #         5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
# # #         9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
# # #     }
# # #     return f"salas seminario/teórico {fecha_dt.day} de {meses[fecha_dt.month]}"


# # # def fecha_bonita(fecha_dt):
# # #     dias = {
# # #         0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
# # #         4: "viernes", 5: "sábado", 6: "domingo"
# # #     }
# # #     meses = {
# # #         1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
# # #         5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
# # #         9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
# # #     }
# # #     return f"{dias[fecha_dt.weekday()]} {fecha_dt.day} de {meses[fecha_dt.month]}"


# # # def crear_driver():
# # #     options = webdriver.ChromeOptions()

# # #     # Déjalo visible, suele funcionar mejor así en Mac
# # #     # options.add_argument("--headless=new")

# # #     options.add_argument("--window-size=1400,1200")
# # #     options.add_argument("--disable-blink-features=AutomationControlled")
# # #     options.add_argument("--lang=es-CL")
# # #     options.add_argument("--no-default-browser-check")
# # #     options.add_argument("--disable-dev-shm-usage")
# # #     options.add_argument("--disable-popup-blocking")

# # #     driver = webdriver.Chrome(options=options)
# # #     return driver


# # # def esperar_selector(driver, by, value, timeout=20):
# # #     return WebDriverWait(driver, timeout).until(
# # #         EC.presence_of_element_located((by, value))
# # #     )


# # # def obtener_opciones_select(driver):
# # #     select_el = esperar_selector(driver, By.ID, "txtSelCurso", timeout=20)

# # #     opciones = driver.execute_script("""
# # #         const sel = arguments[0];
# # #         return Array.from(sel.options).map(o => ({
# # #             value: (o.value || '').trim(),
# # #             text: (o.text || '').trim()
# # #         }));
# # #     """, select_el)

# # #     salida = []
# # #     for op in opciones:
# # #         val = normalizar(op.get("value", ""))
# # #         if val:
# # #             salida.append(val)
# # #     return salida


# # # def buscar_opcion(opciones, codigo, seccion):
# # #     objetivo = f"{codigo}-{seccion}".upper()

# # #     candidatas = []
# # #     for op in opciones:
# # #         if objetivo in op.upper():
# # #             candidatas.append(op)

# # #     if not candidatas:
# # #         return None

# # #     for op in candidatas:
# # #         if op.upper().endswith(objetivo):
# # #             return op

# # #     return candidatas[0]


# # # def setear_fecha(driver, fecha_str):
# # #     fecha_input = esperar_selector(driver, By.ID, "txtFecha", timeout=20)
# # #     driver.execute_script("""
# # #         const inp = arguments[0];
# # #         inp.value = arguments[1];
# # #         inp.dispatchEvent(new Event('input', { bubbles: true }));
# # #         inp.dispatchEvent(new Event('change', { bubbles: true }));
# # #     """, fecha_input, fecha_str)


# # # def seleccionar_curso(driver, valor_opcion):
# # #     select_el = esperar_selector(driver, By.ID, "txtSelCurso", timeout=20)
# # #     driver.execute_script("""
# # #         const sel = arguments[0];
# # #         const val = arguments[1];
# # #         sel.value = val;
# # #         sel.dispatchEvent(new Event('change', { bubbles: true }));
# # #     """, select_el, valor_opcion)


# # # def enviar_formulario(driver):
# # #     form = esperar_selector(driver, By.ID, "form", timeout=20)
# # #     driver.execute_script("arguments[0].submit();", form)


# # # def deduplicar_filas(filas):
# # #     vistas = set()
# # #     salida = []

# # #     for fila in filas:
# # #         clave = (
# # #             normalizar(fila.get("dia", "")),
# # #             normalizar(fila.get("fecha", "")),
# # #             normalizar(fila.get("horario", "")),
# # #             normalizar(fila.get("sala", "")),
# # #             normalizar(fila.get("ubicacion", "")),
# # #         )
# # #         if clave not in vistas:
# # #             vistas.add(clave)
# # #             salida.append(fila)

# # #     return salida


# # # def extraer_resultados_html(driver, fecha_str, codigo, seccion):
# # #     time.sleep(2)
# # #     html = driver.page_source

# # #     with open("debug_consultaaulas_selenium.html", "w", encoding="utf-8") as f:
# # #         f.write(html)

# # #     soup = BeautifulSoup(html, "html.parser")
# # #     tablas = soup.find_all("table")

# # #     objetivo = f"{codigo}-{seccion}".upper()
# # #     filas_salida = []

# # #     for tabla in tablas:
# # #         texto_tabla = normalizar(tabla.get_text(" ", strip=True)).upper()
# # #         if "ASIGNATURA:" not in texto_tabla:
# # #             continue
# # #         if objetivo not in texto_tabla:
# # #             continue

# # #         for tr in tabla.find_all("tr"):
# # #             tds = tr.find_all("td")
# # #             textos = [normalizar(td.get_text(" ", strip=True)) for td in tds]

# # #             if len(textos) < 5:
# # #                 continue

# # #             cab = " ".join(textos[:5]).lower()
# # #             if "día" in cab and "fecha" in cab and "horario" in cab and "sala" in cab:
# # #                 continue

# # #             dia, fecha, horario, sala, ubicacion = textos[:5]

# # #             if fecha == fecha_str and sala:
# # #                 filas_salida.append({
# # #                     "dia": dia,
# # #                     "fecha": fecha,
# # #                     "horario": horario,
# # #                     "sala": sala,
# # #                     "ubicacion": ubicacion,
# # #                 })

# # #     return deduplicar_filas(filas_salida)


# # # def consultar_curso(driver, fecha_str, curso_key):
# # #     info = CURSOS[curso_key]
# # #     resultados = []

# # #     for seccion in info["secciones"]:
# # #         driver.get(URL)

# # #         esperar_selector(driver, By.ID, "txtSelCurso", timeout=20)
# # #         time.sleep(1)

# # #         setear_fecha(driver, fecha_str)
# # #         time.sleep(0.5)

# # #         opciones = obtener_opciones_select(driver)
# # #         valor = buscar_opcion(opciones, info["codigo"], seccion)

# # #         if not valor:
# # #             resultados.append({
# # #                 "seccion": seccion,
# # #                 "error": f"No encontré {info['codigo']}-{seccion} en el selector",
# # #                 "filas": [],
# # #             })
# # #             continue

# # #         seleccionar_curso(driver, valor)
# # #         time.sleep(0.5)
# # #         enviar_formulario(driver)

# # #         filas = extraer_resultados_html(driver, fecha_str, info["codigo"], seccion)

# # #         resultados.append({
# # #             "seccion": seccion,
# # #             "error": None,
# # #             "filas": filas,
# # #         })

# # #     return resultados


# # # def profes_a_texto(lista_profes):
# # #     if not lista_profes:
# # #         return "Por definir"
# # #     return ", ".join(lista_profes)


# # # def formatear_bloque_curso_bonito(curso_key, resultados):
# # #     info = CURSOS[curso_key]
# # #     out = []

# # #     out.append(f"{info['nombre']}:")
# # #     out.append("")

# # #     hubo_algo = False

# # #     for bloque in resultados:
# # #         seccion = bloque["seccion"]
# # #         profes = profes_a_texto(info["profes"].get(seccion, []))

# # #         if bloque["error"]:
# # #             out.append(f"Grupo {seccion} (profe(s) {profes}): revisar manualmente.")
# # #             continue

# # #         filas = bloque["filas"]

# # #         if not filas:
# # #             out.append(f"Grupo {seccion} (profe(s) {profes}): sin sala publicada.")
# # #             continue

# # #         hubo_algo = True

# # #         if len(filas) == 1:
# # #             fila = filas[0]
# # #             sala_txt = fila["sala"]
# # #             if normalizar(fila["ubicacion"]):
# # #                 sala_txt += f" ({fila['ubicacion']})"

# # #             out.append(
# # #                 f"Grupo {seccion} (profe(s) {profes}) [{fila['horario']}]: {sala_txt}."
# # #             )
# # #         else:
# # #             horarios = sorted(set(normalizar(x["horario"]) for x in filas if normalizar(x["horario"])))
# # #             horario_txt = horarios[0] if horarios else "horario no informado"

# # #             salas = []
# # #             for fila in filas:
# # #                 sala_txt = fila["sala"]
# # #                 if normalizar(fila["ubicacion"]):
# # #                     sala_txt += f" ({fila['ubicacion']})"
# # #                 salas.append(sala_txt)

# # #             out.append(
# # #                 f"Grupo {seccion} (profe(s) {profes}) [{horario_txt}]: " + "; ".join(salas) + "."
# # #             )

# # #     out.append("")
# # #     return "\n".join(out), hubo_algo


# # # def formatear_mensaje_global(fecha_str, resultados_por_curso):
# # #     fecha_dt = datetime.strptime(fecha_str, "%d-%m-%Y")

# # #     out = []
# # #     out.append(f"Título sugerido: {titulo_sugerido(fecha_dt)}")
# # #     out.append("")
# # #     out.append("Buen día,")
# # #     out.append("")
# # #     out.append(f"Las salas para el día de hoy {fecha_bonita(fecha_dt)} son:")
# # #     out.append("")

# # #     hubo_algo_total = False

# # #     for curso_key in ["fokito", "enobnu", "tecnologia_medica", "medicina"]:
# # #         if curso_key not in resultados_por_curso:
# # #             continue

# # #         bloque_txt, hubo_algo = formatear_bloque_curso_bonito(
# # #             curso_key, resultados_por_curso[curso_key]
# # #         )
# # #         out.append(bloque_txt)
# # #         if hubo_algo:
# # #             hubo_algo_total = True

# # #     if not hubo_algo_total:
# # #         out.append("No encontré salas publicadas para esa fecha.")
# # #         out.append("")

# # #     out.append("Que les vaya muy bien.")
# # #     return "\n".join(out).strip()


# # # def formatear_mensaje_un_curso(fecha_str, curso_key, resultados):
# # #     fecha_dt = datetime.strptime(fecha_str, "%d-%m-%Y")
# # #     info = CURSOS[curso_key]

# # #     out = []
# # #     out.append(f"Título sugerido: {titulo_sugerido(fecha_dt)}")
# # #     out.append("")
# # #     out.append("Buen día,")
# # #     out.append("")
# # #     out.append(f"Las salas para el día de hoy {fecha_bonita(fecha_dt)} son:")
# # #     out.append("")
# # #     out.append(f"{info['nombre']}:")
# # #     out.append("")

# # #     hubo_algo = False

# # #     for bloque in resultados:
# # #         seccion = bloque["seccion"]
# # #         profes = profes_a_texto(info["profes"].get(seccion, []))

# # #         if bloque["error"]:
# # #             out.append(f"Grupo {seccion} (profe(s) {profes}): revisar manualmente.")
# # #             continue

# # #         filas = bloque["filas"]

# # #         if not filas:
# # #             out.append(f"Grupo {seccion} (profe(s) {profes}): sin sala publicada.")
# # #             continue

# # #         hubo_algo = True

# # #         if len(filas) == 1:
# # #             fila = filas[0]
# # #             sala_txt = fila["sala"]
# # #             if normalizar(fila["ubicacion"]):
# # #                 sala_txt += f" ({fila['ubicacion']})"

# # #             out.append(
# # #                 f"Grupo {seccion} (profe(s) {profes}) [{fila['horario']}]: {sala_txt}."
# # #             )
# # #         else:
# # #             horarios = sorted(set(normalizar(x["horario"]) for x in filas if normalizar(x["horario"])))
# # #             horario_txt = horarios[0] if horarios else "horario no informado"

# # #             salas = []
# # #             for fila in filas:
# # #                 sala_txt = fila["sala"]
# # #                 if normalizar(fila["ubicacion"]):
# # #                     sala_txt += f" ({fila['ubicacion']})"
# # #                 salas.append(sala_txt)

# # #             out.append(
# # #                 f"Grupo {seccion} (profe(s) {profes}) [{horario_txt}]: " + "; ".join(salas) + "."
# # #             )

# # #     out.append("")

# # #     if not hubo_algo:
# # #         out.append("No encontré salas publicadas para esa fecha.")
# # #         out.append("")

# # #     out.append("Que les vaya muy bien.")
# # #     return "\n".join(out).strip()


# # # def main():
# # #     if len(sys.argv) < 2:
# # #         print("Uso:")
# # #         print("  python3 obtener_salas.py DD-MM-AAAA")
# # #         print("  python3 obtener_salas.py DD-MM-AAAA curso")
# # #         print("")
# # #         print("Ejemplos:")
# # #         print("  python3 obtener_salas.py 26-03-2026")
# # #         print("  python3 obtener_salas.py 26-03-2026 medicina")
# # #         return

# # #     fecha_str = sys.argv[1]
# # #     datetime.strptime(fecha_str, "%d-%m-%Y")

# # #     curso_key = None
# # #     if len(sys.argv) >= 3:
# # #         curso_key = sys.argv[2].strip().lower()
# # #         if curso_key not in CURSOS:
# # #             raise ValueError(f"Curso no reconocido: {curso_key}")

# # #     driver = crear_driver()

# # #     try:
# # #         if curso_key is not None:
# # #             resultados = consultar_curso(driver, fecha_str, curso_key)
# # #             mensaje = formatear_mensaje_un_curso(fecha_str, curso_key, resultados)
# # #             print(mensaje)
# # #         else:
# # #             resultados_por_curso = {}
# # #             for ck in ["fokito", "enobnu", "tecnologia_medica", "medicina"]:
# # #                 resultados_por_curso[ck] = consultar_curso(driver, fecha_str, ck)

# # #             mensaje = formatear_mensaje_global(fecha_str, resultados_por_curso)
# # #             print(mensaje)

# # #     finally:
# # #         driver.quit()


# # # if __name__ == "__main__":
# # #     main()




# # import sys
# # import time
# # import re
# # import unicodedata
# # from datetime import datetime

# # from bs4 import BeautifulSoup

# # from selenium import webdriver
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC


# # URL = "http://consultaaulas.med.uchile.cl/consulta_clase.html"
# # TEXTO_BUSQUEDA = "MATEM"


# # # CURSOS = {
# # #     "fokito": {
# # #         "codigo": "CBA0103",
# # #         "nombre": "FOKITO",
# # #         "secciones": [1, 2, 3, 4],
# # #         "profes": {
# # #             1: ["Nathalie Varas", "Jose Mondaca", "Maximiliano Bernal"],
# # #             2: ["José Mondaca", "Nathalie Varas", "Rosa Muñoz"],
# # #             3: ["José Mondaca", "Rosa Muñoz", "Nathalie Varas"],
# # #             4: ["Gabriel Fraczinet", "Eduardo Guerra", "Sebastián Marconi"],
# # #         },
# # #     },
# # #     "enobnu": {
# # #         "codigo": "CBA0102",
# # #         "nombre": "ENOBNU",
# # #         "secciones": [1, 2, 3, 4],
# # #         "profes": {
# # #             1: ["Maximiliano Bernal", "José Mondaca", "Valeria Brancacho"],
# # #             2: ["Nathalie Varas", "Rosa Muñoz", "Sebastián Marconi"],
# # #             3: ["Maximiliano Bernal", "Diego Hidalgo", "Gabriela Martinez"],
# # #             4: ["Gabriela Martinez", "Valeria Brancacho", "Diego Hidalgo"],
# # #         },
# # #     },
# # #     "tecnologia_medica": {
# # #         "codigo": "TMA01005",
# # #         "nombre": "TECNOLOGÍA MÉDICA",
# # #         "secciones": [1],
# # #         "profes": {
# # #             1: ["J. Tomás Yáñez", "Maximiliano Bernal", "Gabriela Martínez", "Gabriel Fraczinet"],
# # #         },
# # #     },
# # #     "medicina": {
# # #         "codigo": "MED0101",
# # #         "nombre": "MEDICINA",
# # #         "secciones": [1, 2],
# # #         "profes": {
# # #             1: ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
# # #             2: ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
# # #         },
# # #     },
# # # }


# # CURSOS = {
# #     "fokito": {
# #         "codigo": "CBA0103",
# #         "nombre": "FOKITO",
# #         "secciones": [1, 2, 3, 4],
# #         "secciones_info": {
# #             1: {
# #                 "profe_teorico": "IG",
# #                 "profes_laboratorio": ["Nathalie Varas", "Jose Mondaca", "Maximiliano Bernal", "POR DEFINIR"],
# #                 "profes_seminario": ["Nathalie Varas", "Jose Mondaca", "Maximiliano Bernal"],
# #             },
# #             2: {
# #                 "profe_teorico": "JCS",
# #                 "profes_laboratorio": ["José Mondaca", "Nathalie Varas", "Rosa Muñoz", "POR DEFINIR"],
# #                 "profes_seminario": ["José Mondaca", "Nathalie Varas", "Rosa Muñoz"],
# #             },
# #             3: {
# #                 "profe_teorico": "AR",
# #                 "profes_laboratorio": ["José Mondaca", "Rosa Muñoz", "Nathalie Varas", "POR DEFINIR"],
# #                 "profes_seminario": ["José Mondaca", "Rosa Muñoz", "Nathalie Varas"],
# #             },
# #             4: {
# #                 "profe_teorico": "CC",
# #                 "profes_laboratorio": ["Gabriel Fraczinet", "Eduardo Guerra", "Sebastián Marconi", "POR DEFINIR"],
# #                 "profes_seminario": ["Gabriel Fraczinet", "Eduardo Guerra", "Sebastián Marconi"],
# #             },
# #         },
# #     },
# #     "enobnu": {
# #         "codigo": "CBA0102",
# #         "nombre": "ENOBNU",
# #         "secciones": [1, 2, 3, 4],
# #         "secciones_info": {
# #             1: {
# #                 "profe_teorico": "POR DEFINIR",
# #                 "profes_laboratorio": ["Maximiliano Bernal", "José Mondaca", "Valeria Brancacho", "POR DEFINIR"],
# #                 "profes_seminario": ["Maximiliano Bernal", "José Mondaca", "Valeria Brancacho"],
# #             },
# #             2: {
# #                 "profe_teorico": "POR DEFINIR",
# #                 "profes_laboratorio": ["Nathalie Varas", "Rosa Muñoz", "Sebastián Marconi", "POR DEFINIR"],
# #                 "profes_seminario": ["Nathalie Varas", "Rosa Muñoz", "Sebastián Marconi"],
# #             },
# #             3: {
# #                 "profe_teorico": "POR DEFINIR",
# #                 "profes_laboratorio": ["Maximiliano Bernal", "Diego Hidalgo", "Gabriela Martinez", "POR DEFINIR"],
# #                 "profes_seminario": ["Maximiliano Bernal", "Diego Hidalgo", "Gabriela Martinez"],
# #             },
# #             4: {
# #                 "profe_teorico": "POR DEFINIR",
# #                 "profes_laboratorio": ["Gabriela Martinez", "Valeria Brancacho", "Diego Hidalgo", "POR DEFINIR"],
# #                 "profes_seminario": ["Gabriela Martinez", "Valeria Brancacho", "Diego Hidalgo"],
# #             },
# #         },
# #     },
# #     "tecnologia_medica": {
# #         "codigo": "TMA01005",
# #         "nombre": "TECNOLOGÍA MÉDICA",
# #         "secciones": [1],
# #         "secciones_info": {
# #             1: {
# #                 "profe_teorico": "J. Tomás Yáñez",
# #                 "profes_laboratorio": ["J. Tomás Yáñez", "Maximiliano Bernal", "Gabriela Martínez", "Gabriel Fraczinet"],
# #                 "profes_seminario": ["J. Tomás Yáñez", "Maximiliano Bernal", "Gabriela Martínez", "Gabriel Fraczinet"],
# #             },
# #         },
# #     },
# #     "medicina": {
# #         "codigo": "MED0101",
# #         "nombre": "MEDICINA",
# #         "secciones": [1, 2],
# #         "secciones_info": {
# #             1: {
# #                 "profe_teorico": "J. Tomás Yáñez",
# #                 "profes_laboratorio": ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
# #                 "profes_seminario": ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
# #             },
# #             2: {
# #                 "profe_teorico": "J. Tomás Yáñez",
# #                 "profes_laboratorio": ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
# #                 "profes_seminario": ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
# #             },
# #         },
# #     },
# # }




# # def normalizar(txt):
# #     return " ".join(str(txt).replace("\xa0", " ").split()).strip()


# # def sin_tildes(txt):
# #     txt = str(txt)
# #     return "".join(
# #         c for c in unicodedata.normalize("NFD", txt)
# #         if unicodedata.category(c) != "Mn"
# #     )


# # def normalizar_busqueda(txt):
# #     return sin_tildes(normalizar(txt)).upper()


# # def crear_driver():
# #     options = webdriver.ChromeOptions()

# #     # Si después quieres ocultarlo, prueba descomentando esta línea:
# #     # options.add_argument("--headless=new")

# #     options.add_argument("--window-size=1400,1200")
# #     options.add_argument("--disable-blink-features=AutomationControlled")
# #     options.add_argument("--lang=es-CL")
# #     options.add_argument("--start-maximized")

# #     driver = webdriver.Chrome(options=options)
# #     return driver


# # def esperar_selector(driver, by, value, timeout=20):
# #     return WebDriverWait(driver, timeout).until(
# #         EC.presence_of_element_located((by, value))
# #     )


# # def abrir_pagina(driver):
# #     driver.get(URL)
# #     esperar_selector(driver, By.ID, "form", timeout=20)
# #     esperar_selector(driver, By.ID, "txtFecha", timeout=20)
# #     esperar_selector(driver, By.ID, "txtCurso", timeout=20)
# #     time.sleep(1.0)


# # def setear_fecha(driver, fecha_str):
# #     fecha_input = esperar_selector(driver, By.ID, "txtFecha", timeout=20)
# #     driver.execute_script("""
# #         const inp = arguments[0];
# #         inp.value = arguments[1];
# #         inp.dispatchEvent(new Event('input', { bubbles: true }));
# #         inp.dispatchEvent(new Event('change', { bubbles: true }));
# #     """, fecha_input, fecha_str)


# # def setear_texto_busqueda(driver, texto):
# #     txt_input = esperar_selector(driver, By.ID, "txtCurso", timeout=20)
# #     driver.execute_script("""
# #         const inp = arguments[0];
# #         inp.value = '';
# #         inp.dispatchEvent(new Event('input', { bubbles: true }));
# #         inp.dispatchEvent(new Event('change', { bubbles: true }));
# #     """, txt_input)
# #     time.sleep(0.2)

# #     driver.execute_script("""
# #         const inp = arguments[0];
# #         inp.value = arguments[1];
# #         inp.dispatchEvent(new Event('input', { bubbles: true }));
# #         inp.dispatchEvent(new Event('change', { bubbles: true }));
# #     """, txt_input, texto)


# # def limpiar_selector_curso(driver):
# #     try:
# #         select_el = esperar_selector(driver, By.ID, "txtSelCurso", timeout=5)
# #         driver.execute_script("""
# #             const sel = arguments[0];
# #             sel.value = '';
# #             sel.dispatchEvent(new Event('change', { bubbles: true }));
# #         """, select_el)
# #     except Exception:
# #         pass


# # def enviar_formulario(driver):
# #     form = esperar_selector(driver, By.ID, "form", timeout=20)
# #     driver.execute_script("arguments[0].submit();", form)


# # def extraer_codigo_seccion_desde_texto(texto, pares_validos):
# #     """
# #     Busca patrones tipo MED0101-2 en el texto.
# #     """
# #     texto_norm = normalizar_busqueda(texto)

# #     encontrados = re.findall(r"[A-Z]{3,}\d{4,5}-\d+", texto_norm)
# #     for e in encontrados:
# #         if e in pares_validos:
# #             return e

# #     for par in pares_validos:
# #         if par in texto_norm:
# #             return par

# #     return None


# # def parsear_tabla_resultado(tabla, fecha_str, pares_validos):
# #     texto_tabla = normalizar(tabla.get_text(" ", strip=True))
# #     curso_detectado = extraer_codigo_seccion_desde_texto(texto_tabla, pares_validos)

# #     if not curso_detectado:
# #         return None, []

# #     filas = []
# #     vistos = set()

# #     for tr in tabla.find_all("tr"):
# #         tds = tr.find_all("td")
# #         textos = [normalizar(td.get_text(" ", strip=True)) for td in tds]

# #         if len(textos) < 5:
# #             continue

# #         cab = normalizar_busqueda(" ".join(textos[:5]))
# #         if "DIA" in cab and "FECHA" in cab and "HORARIO" in cab and "SALA" in cab:
# #             continue

# #         dia, fecha, horario, sala, ubicacion = textos[:5]

# #         if fecha != fecha_str:
# #             continue

# #         clave = (
# #             normalizar(horario),
# #             normalizar(sala),
# #             normalizar(ubicacion),
# #         )

# #         if clave in vistos:
# #             continue
# #         vistos.add(clave)

# #         filas.append({
# #             "dia": dia,
# #             "fecha": fecha,
# #             "horario": normalizar(horario),
# #             "sala": normalizar(sala),
# #             "ubicacion": normalizar(ubicacion),
# #         })

# #     return curso_detectado, filas


# # def extraer_resultados_html(driver, fecha_str):
# #     time.sleep(2.0)
# #     html = driver.page_source

# #     with open("debug_consultaaulas.html", "w", encoding="utf-8") as f:
# #         f.write(html)

# #     soup = BeautifulSoup(html, "html.parser")
# #     tablas = soup.find_all("table")

# #     pares_validos = set()
# #     for info in CURSOS.values():
# #         for sec in info["secciones"]:
# #             pares_validos.add(f"{info['codigo']}-{sec}".upper())

# #     resultados = {par: [] for par in pares_validos}

# #     for tabla in tablas:
# #         curso_detectado, filas = parsear_tabla_resultado(tabla, fecha_str, pares_validos)
# #         if not curso_detectado:
# #             continue
# #         if not filas:
# #             continue

# #         existentes = {
# #             (x["horario"], x["sala"], x["ubicacion"])
# #             for x in resultados[curso_detectado]
# #         }

# #         for fila in filas:
# #             clave = (fila["horario"], fila["sala"], fila["ubicacion"])
# #             if clave not in existentes:
# #                 resultados[curso_detectado].append(fila)
# #                 existentes.add(clave)

# #     return resultados


# # def consultar_todo_el_dia(fecha_str):
# #     driver = crear_driver()

# #     try:
# #         abrir_pagina(driver)
# #         setear_fecha(driver, fecha_str)
# #         limpiar_selector_curso(driver)
# #         setear_texto_busqueda(driver, TEXTO_BUSQUEDA)
# #         time.sleep(0.5)
# #         enviar_formulario(driver)

# #         resultados = extraer_resultados_html(driver, fecha_str)
# #         return resultados

# #     finally:
# #         driver.quit()


# # def fecha_bonita(fecha_str):
# #     fecha = datetime.strptime(fecha_str, "%d-%m-%Y")

# #     dias = {
# #         0: "lunes",
# #         1: "martes",
# #         2: "miércoles",
# #         3: "jueves",
# #         4: "viernes",
# #         5: "sábado",
# #         6: "domingo",
# #     }

# #     meses = {
# #         1: "enero",
# #         2: "febrero",
# #         3: "marzo",
# #         4: "abril",
# #         5: "mayo",
# #         6: "junio",
# #         7: "julio",
# #         8: "agosto",
# #         9: "septiembre",
# #         10: "octubre",
# #         11: "noviembre",
# #         12: "diciembre",
# #     }

# #     dia_semana = dias[fecha.weekday()]
# #     return f"{dia_semana} {fecha.day} de {meses[fecha.month]}"


# # def titulo_sugerido(fecha_str):
# #     fecha = datetime.strptime(fecha_str, "%d-%m-%Y")
# #     meses = {
# #         1: "enero",
# #         2: "febrero",
# #         3: "marzo",
# #         4: "abril",
# #         5: "mayo",
# #         6: "junio",
# #         7: "julio",
# #         8: "agosto",
# #         9: "septiembre",
# #         10: "octubre",
# #         11: "noviembre",
# #         12: "diciembre",
# #     }
# #     return f"salas seminario/teórico {fecha.day} de {meses[fecha.month]}"



# # def salas_unicas_en_orden(filas):
# #     salas = []
# #     vistas = set()

# #     for fila in filas:
# #         sala = normalizar(fila.get("sala", ""))
# #         if sala and sala not in vistas:
# #             salas.append(sala)
# #             vistas.add(sala)

# #     return salas


# # def asignar_profes_a_salas(profes, filas):
# #     """
# #     Asigna profesores a salas en orden:
# #     profe 1 -> sala 1
# #     profe 2 -> sala 2
# #     etc.

# #     Si hay menos salas que profes, el resto queda como 'revisar manualmente'.
# #     Si hay más salas que profes, las salas sobrantes se ignoran.
# #     """
# #     salas = salas_unicas_en_orden(filas)
# #     asignaciones = []

# #     for i, profe in enumerate(profes):
# #         if i < len(salas):
# #             asignaciones.append({
# #                 "profe": profe,
# #                 "sala": salas[i]
# #             })
# #         else:
# #             asignaciones.append({
# #                 "profe": profe,
# #                 "sala": "revisar manualmente"
# #             })

# #     return asignaciones


# # def formatear_bloque_seccion(seccion, profes, filas):
# #     """
# #     Devuelve un bloque tipo:

# #     Grupo 1
# #     - Profe A: Sala X
# #     - Profe B: Sala Y
# #     - Profe C: Sala Z
# #     """
# #     out = []
# #     out.append(f"Grupo {seccion}")

# #     if not profes:
# #         profes = ["Por definir"]

# #     if not filas:
# #         for profe in profes:
# #             out.append(f"- {profe}: revisar manualmente")
# #         return "\n".join(out)

# #     grupos_horario = agrupar_por_horario(filas)

# #     # Si solo hay un horario, mostrar simple
# #     if len(grupos_horario) == 1:
# #         horario = list(sorted(grupos_horario.keys()))[0]
# #         asignaciones = asignar_profes_a_salas(profes, grupos_horario[horario])

# #         out.append(f"Horario: {horario}")
# #         for a in asignaciones:
# #             out.append(f"- {a['profe']}: {a['sala']}")
# #         return "\n".join(out)

# #     # Si hay varios horarios, mostrar por horario
# #     for horario in sorted(grupos_horario.keys()):
# #         out.append(f"Horario: {horario}")
# #         asignaciones = asignar_profes_a_salas(profes, grupos_horario[horario])

# #         for a in asignaciones:
# #             out.append(f"- {a['profe']}: {a['sala']}")
# #         out.append("")

# #     # quitar salto extra final
# #     while out and out[-1] == "":
# #         out.pop()

# #     return "\n".join(out)


# # def agrupar_por_horario(filas):
# #     """
# #     Agrupa filas por horario para mostrarlas más limpio.
# #     """
# #     grupos = {}
# #     for fila in filas:
# #         horario = fila["horario"]
# #         grupos.setdefault(horario, [])
# #         grupos[horario].append(fila)

# #     return grupos


# # # def resumir_salas(filas):
# # #     """
# # #     Devuelve texto tipo:
# # #     08:30 - 10:00: Sala A, Sala B
# # #     o si hay varios horarios:
# # #     08:30 - 10:00: Sala A, Sala B / 12:00 - 13:30: Sala C
# # #     """
# # #     if not filas:
# # #         return "revisar manualmente"

# # #     grupos = agrupar_por_horario(filas)
# # #     partes = []

# # #     for horario in sorted(grupos.keys()):
# # #         salas = []
# # #         vistas = set()

# # #         for fila in grupos[horario]:
# # #             sala = fila["sala"]
# # #             if sala not in vistas:
# # #                 salas.append(sala)
# # #                 vistas.add(sala)

# # #         partes.append(f"{horario}: {', '.join(salas)}")

# # #     return " / ".join(partes)


# # def construir_bloques_por_curso(resultados):
# #     """
# #     Convierte resultados globales en estructura por curso y sección.
# #     """
# #     salida = {}

# #     for curso_key, info in CURSOS.items():
# #         salida[curso_key] = {
# #             "nombre": info["nombre"],
# #             "codigo": info["codigo"],
# #             "secciones": []
# #         }

# #         for seccion in info["secciones"]:
# #             par = f"{info['codigo']}-{seccion}".upper()
# #             filas = resultados.get(par, [])
# #             profes = info["profes"].get(seccion, [])

# #             salida[curso_key]["secciones"].append({
# #                 "seccion": seccion,
# #                 "profes": profes,
# #                 "filas": filas,
# #             })

# #     return salida


# # # def formatear_mensaje_bonito(fecha_str, resultados):
# # #     bloques = construir_bloques_por_curso(resultados)

# # #     out = []
# # #     out.append(f"Título sugerido: {titulo_sugerido(fecha_str)}")
# # #     out.append("")
# # #     out.append("Buen día,")
# # #     out.append("")
# # #     out.append(f"Las salas para el día de hoy {fecha_bonita(fecha_str)} son:")
# # #     out.append("")

# # #     hay_algo = False

# # #     orden_cursos = ["fokito", "enobnu", "tecnologia_medica", "medicina"]

# # #     for curso_key in orden_cursos:
# # #         info = bloques[curso_key]
# # #         out.append(f"{info['nombre']}:")
# # #         out.append("")

# # #         for item in info["secciones"]:
# # #             seccion = item["seccion"]
# # #             profes = item["profes"]
# # #             filas = item["filas"]

# # #             if filas:
# # #                 hay_algo = True

# # #             profes_txt = ", ".join(profes) if profes else "Por definir"
# # #             salas_txt = resumir_salas(filas)

# # #             out.append(f"Grupo {seccion} ({profes_txt}): {salas_txt}")
# # #             out.append("")

# # #     if not hay_algo:
# # #         out.append("No encontré salas publicadas para esa fecha.")
# # #         out.append("")

# # #     out.append("Que les vaya muy bien.")

# # #     return "\n".join(out).strip()


# # def formatear_mensaje_bonito(fecha_str, resultados):
# #     bloques = construir_bloques_por_curso(resultados)

# #     out = []
# #     out.append(f"Título sugerido: {titulo_sugerido(fecha_str)}")
# #     out.append("")
# #     out.append("Buen día,")
# #     out.append("")
# #     out.append(f"Las salas para el día de hoy {fecha_bonita(fecha_str)} son:")
# #     out.append("")

# #     hay_algo = False
# #     orden_cursos = ["fokito", "enobnu", "tecnologia_medica", "medicina"]

# #     for curso_key in orden_cursos:
# #         info = bloques[curso_key]
# #         out.append(f"{info['nombre']}:")
# #         out.append("")

# #         for item in info["secciones"]:
# #             seccion = item["seccion"]
# #             profes = item["profes"]
# #             filas = item["filas"]

# #             if filas:
# #                 hay_algo = True

# #             bloque = formatear_bloque_seccion(seccion, profes, filas)
# #             out.append(bloque)
# #             out.append("")

# #     if not hay_algo:
# #         out.append("No encontré salas publicadas para esa fecha.")
# #         out.append("")

# #     out.append("Que les vaya muy bien.")

# #     return "\n".join(out).strip()






# # def salas_unicas_en_orden(filas):
# #     salas = []
# #     vistas = set()

# #     for fila in filas:
# #         sala = normalizar(fila.get("sala", ""))
# #         horario = normalizar(fila.get("horario", ""))

# #         clave = (horario, sala)
# #         if sala and clave not in vistas:
# #             vistas.add(clave)
# #             salas.append({
# #                 "horario": horario,
# #                 "sala": sala,
# #             })

# #     return salas


# # def nombre_bonito_fecha(fecha_str):
# #     dt = datetime.strptime(fecha_str, "%d-%m-%Y")
# #     dias = {
# #         0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
# #         4: "viernes", 5: "sábado", 6: "domingo"
# #     }
# #     meses = {
# #         1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
# #         5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
# #         9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
# #     }
# #     return f"{dias[dt.weekday()]} {dt.day} de {meses[dt.month]}"


# # def titulo_sugerido(fecha_str):
# #     dt = datetime.strptime(fecha_str, "%d-%m-%Y")
# #     meses = {
# #         1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
# #         5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
# #         9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
# #     }
# #     return f"salas seminario/teórico {dt.day} de {meses[dt.month]}"


# # def bloque_teorico(seccion, info_sec, salas):
# #     profe = info_sec.get("profe_teorico", "Por definir")
# #     sala = salas[0]["sala"]
# #     horario = salas[0]["horario"]
# #     return f"Grupo {seccion} ({profe}): {sala} ({horario})"


# # def bloque_laboratorio(seccion, info_sec, salas):
# #     profes_lab = info_sec.get("profes_laboratorio", [])
# #     profes_txt = ", ".join(profes_lab) if profes_lab else "Por definir"

# #     lineas = []
# #     lineas.append(f"Grupo {seccion} laboratorio ({profes_txt}):")

# #     for i, item in enumerate(salas[:2], start=1):
# #         lineas.append(f"Laboratorio {i}: {item['sala']} ({item['horario']})")

# #     return "\n".join(lineas)


# # def bloque_seminario(seccion, info_sec, salas):
# #     profes_sem = info_sec.get("profes_seminario", [])
# #     profes_txt = ", ".join(profes_sem) if profes_sem else "Por definir"

# #     lineas = []
# #     lineas.append(f"Grupo {seccion} seminario ({profes_txt}):")

# #     for i, item in enumerate(salas, start=1):
# #         lineas.append(f"Sala {i}: {item['sala']} ({item['horario']})")

# #     return "\n".join(lineas)


# # def formatear_bloque_seccion(curso_info, bloque):
# #     seccion = bloque["seccion"]
# #     info_sec = curso_info.get("secciones_info", {}).get(seccion, {})

# #     if bloque.get("error"):
# #         return f"Grupo {seccion}: revisar manualmente"

# #     filas = bloque.get("filas", [])
# #     if not filas:
# #         return f"Grupo {seccion}: sin sala publicada"

# #     salas = salas_unicas_en_orden(filas)
# #     n = len(salas)

# #     if n == 0:
# #         return f"Grupo {seccion}: sin sala publicada"

# #     if n == 1:
# #         return bloque_teorico(seccion, info_sec, salas)

# #     if n == 2:
# #         return bloque_laboratorio(seccion, info_sec, salas)

# #     return bloque_seminario(seccion, info_sec, salas)


# # def construir_mensaje_bonito(fecha_str, resultados_por_curso):
# #     fecha_linda = nombre_bonito_fecha(fecha_str)
# #     titulo = titulo_sugerido(fecha_str)

# #     lineas = []
# #     lineas.append(f"Título sugerido: {titulo}")
# #     lineas.append("")
# #     lineas.append("Buen día,")
# #     lineas.append("")
# #     lineas.append(f"Las salas para el día de hoy {fecha_linda} son:")
# #     lineas.append("")

# #     hubo_datos = False

# #     for curso_key in ["fokito", "enobnu", "tecnologia_medica", "medicina"]:
# #         if curso_key not in resultados_por_curso:
# #             continue

# #         info = CURSOS[curso_key]
# #         resultados = resultados_por_curso[curso_key]

# #         bloques_texto = []
# #         for bloque in resultados:
# #             txt = formatear_bloque_seccion(info, bloque)
# #             if txt:
# #                 bloques_texto.append(txt)

# #                 if "sin sala publicada" not in txt.lower() and "revisar manualmente" not in txt.lower():
# #                     hubo_datos = True

# #         if bloques_texto:
# #             lineas.append(f"{info['nombre']}:")
# #             lineas.append("")
# #             lineas.append("\n\n".join(bloques_texto))
# #             lineas.append("")

# #     if not hubo_datos:
# #         lineas.append("No encontré salas publicadas para esa fecha.")
# #         lineas.append("")

# #     lineas.append("Que les vaya muy bien.")

# #     return "\n".join(lineas).strip()



# # # def main():
# # #     if len(sys.argv) < 2:
# # #         print("Uso: python3 obtener_salas.py DD-MM-AAAA")
# # #         print("Ejemplo: python3 obtener_salas.py 26-03-2026")
# # #         return

# # #     fecha_str = sys.argv[1]
# # #     datetime.strptime(fecha_str, "%d-%m-%Y")

# # #     resultados = consultar_todo_el_dia(fecha_str)
# # #     mensaje = formatear_mensaje_bonito(fecha_str, resultados)
# # #     print(mensaje)



# # def main():
# #     if len(sys.argv) < 2:
# #         print("Uso: python3 obtener_salas.py DD-MM-AAAA")
# #         print("Ejemplo: python3 obtener_salas.py 26-03-2026")
# #         return

# #     fecha_str = sys.argv[1]
# #     datetime.strptime(fecha_str, "%d-%m-%Y")

# #     driver = crear_driver()
# #     try:
# #         resultados_por_curso = consultar_todo_el_dia(fecha_str)
# #         mensaje = construir_mensaje_bonito(fecha_str, resultados_por_curso)
# #         print(mensaje)
# #     finally:
# #         driver.quit()


# # if __name__ == "__main__":
# #     main()





# import sys
# import time
# import re
# import unicodedata
# from datetime import datetime

# from bs4 import BeautifulSoup

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


# URL = "http://consultaaulas.med.uchile.cl/consulta_clase.html"
# TEXTO_BUSQUEDA = "MATEM"


# CURSOS = {
#     "fokito": {
#         "codigo": "CBA0103",
#         "nombre": "FOKITO",
#         "secciones": [1, 2, 3, 4],
#         "secciones_info": {
#             1: {
#                 "profe_teorico": "IG",
#                 "profes_laboratorio": ["Nathalie Varas", "Jose Mondaca", "Maximiliano Bernal", "POR DEFINIR"],
#                 "profes_seminario": ["Nathalie Varas", "Jose Mondaca", "Maximiliano Bernal"],
#             },
#             2: {
#                 "profe_teorico": "JCS",
#                 "profes_laboratorio": ["José Mondaca", "Nathalie Varas", "Rosa Muñoz", "POR DEFINIR"],
#                 "profes_seminario": ["José Mondaca", "Nathalie Varas", "Rosa Muñoz"],
#             },
#             3: {
#                 "profe_teorico": "AR",
#                 "profes_laboratorio": ["José Mondaca", "Rosa Muñoz", "Nathalie Varas", "POR DEFINIR"],
#                 "profes_seminario": ["José Mondaca", "Rosa Muñoz", "Nathalie Varas"],
#             },
#             4: {
#                 "profe_teorico": "CC",
#                 "profes_laboratorio": ["Gabriel Fraczinet", "Eduardo Guerra", "Sebastián Marconi", "POR DEFINIR"],
#                 "profes_seminario": ["Gabriel Fraczinet", "Eduardo Guerra", "Sebastián Marconi"],
#             },
#         },
#     },
#     "enobnu": {
#         "codigo": "CBA0102",
#         "nombre": "ENOBNU",
#         "secciones": [1, 2, 3, 4],
#         "secciones_info": {
#             1: {
#                 "profe_teorico": "POR DEFINIR",
#                 "profes_laboratorio": ["Maximiliano Bernal", "José Mondaca", "Valeria Brancacho", "POR DEFINIR"],
#                 "profes_seminario": ["Maximiliano Bernal", "José Mondaca", "Valeria Brancacho"],
#             },
#             2: {
#                 "profe_teorico": "POR DEFINIR",
#                 "profes_laboratorio": ["Nathalie Varas", "Rosa Muñoz", "Sebastián Marconi", "POR DEFINIR"],
#                 "profes_seminario": ["Nathalie Varas", "Rosa Muñoz", "Sebastián Marconi"],
#             },
#             3: {
#                 "profe_teorico": "POR DEFINIR",
#                 "profes_laboratorio": ["Maximiliano Bernal", "Diego Hidalgo", "Gabriela Martinez", "POR DEFINIR"],
#                 "profes_seminario": ["Maximiliano Bernal", "Diego Hidalgo", "Gabriela Martinez"],
#             },
#             4: {
#                 "profe_teorico": "POR DEFINIR",
#                 "profes_laboratorio": ["Gabriela Martinez", "Valeria Brancacho", "Diego Hidalgo", "POR DEFINIR"],
#                 "profes_seminario": ["Gabriela Martinez", "Valeria Brancacho", "Diego Hidalgo"],
#             },
#         },
#     },
#     "tecnologia_medica": {
#         "codigo": "TMA01005",
#         "nombre": "TECNOLOGÍA MÉDICA",
#         "secciones": [1],
#         "secciones_info": {
#             1: {
#                 "profe_teorico": "J. Tomás Yáñez",
#                 "profes_laboratorio": ["J. Tomás Yáñez", "Maximiliano Bernal", "Gabriela Martínez", "Gabriel Fraczinet"],
#                 "profes_seminario": ["J. Tomás Yáñez", "Maximiliano Bernal", "Gabriela Martínez", "Gabriel Fraczinet"],
#             },
#         },
#     },
#     "medicina": {
#         "codigo": "MED0101",
#         "nombre": "MEDICINA",
#         "secciones": [1, 2],
#         "secciones_info": {
#             1: {
#                 "profe_teorico": "J. Tomás Yáñez",
#                 "profes_laboratorio": ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
#                 "profes_seminario": ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
#             },
#             2: {
#                 "profe_teorico": "J. Tomás Yáñez",
#                 "profes_laboratorio": ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
#                 "profes_seminario": ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
#             },
#         },
#     },
# }


# def normalizar(txt):
#     return " ".join(str(txt).replace("\xa0", " ").split()).strip()


# def sin_tildes(txt):
#     txt = str(txt)
#     return "".join(
#         c for c in unicodedata.normalize("NFD", txt)
#         if unicodedata.category(c) != "Mn"
#     )


# def normalizar_busqueda(txt):
#     return sin_tildes(normalizar(txt)).upper()


# def crear_driver():
#     options = webdriver.ChromeOptions()
#     # options.add_argument("--headless=new")
#     options.add_argument("--window-size=1400,1200")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--lang=es-CL")
#     options.add_argument("--start-maximized")
#     return webdriver.Chrome(options=options)


# def esperar_selector(driver, by, value, timeout=20):
#     return WebDriverWait(driver, timeout).until(
#         EC.presence_of_element_located((by, value))
#     )


# def abrir_pagina(driver):
#     driver.get(URL)
#     esperar_selector(driver, By.ID, "form", timeout=20)
#     esperar_selector(driver, By.ID, "txtFecha", timeout=20)
#     esperar_selector(driver, By.ID, "txtCurso", timeout=20)
#     time.sleep(1.0)


# def setear_fecha(driver, fecha_str):
#     fecha_input = esperar_selector(driver, By.ID, "txtFecha", timeout=20)
#     driver.execute_script("""
#         const inp = arguments[0];
#         inp.value = arguments[1];
#         inp.dispatchEvent(new Event('input', { bubbles: true }));
#         inp.dispatchEvent(new Event('change', { bubbles: true }));
#     """, fecha_input, fecha_str)


# def setear_texto_busqueda(driver, texto):
#     txt_input = esperar_selector(driver, By.ID, "txtCurso", timeout=20)
#     driver.execute_script("""
#         const inp = arguments[0];
#         inp.value = '';
#         inp.dispatchEvent(new Event('input', { bubbles: true }));
#         inp.dispatchEvent(new Event('change', { bubbles: true }));
#     """, txt_input)
#     time.sleep(0.2)

#     driver.execute_script("""
#         const inp = arguments[0];
#         inp.value = arguments[1];
#         inp.dispatchEvent(new Event('input', { bubbles: true }));
#         inp.dispatchEvent(new Event('change', { bubbles: true }));
#     """, txt_input, texto)


# def limpiar_selector_curso(driver):
#     try:
#         select_el = esperar_selector(driver, By.ID, "txtSelCurso", timeout=5)
#         driver.execute_script("""
#             const sel = arguments[0];
#             sel.value = '';
#             sel.dispatchEvent(new Event('change', { bubbles: true }));
#         """, select_el)
#     except Exception:
#         pass


# def enviar_formulario(driver):
#     form = esperar_selector(driver, By.ID, "form", timeout=20)
#     driver.execute_script("arguments[0].submit();", form)


# def extraer_codigo_seccion_desde_texto(texto, pares_validos):
#     texto_norm = normalizar_busqueda(texto)

#     encontrados = re.findall(r"[A-Z]{3,}\d{4,5}-\d+", texto_norm)
#     for e in encontrados:
#         if e in pares_validos:
#             return e

#     for par in pares_validos:
#         if par in texto_norm:
#             return par

#     return None


# def parsear_tabla_resultado(tabla, fecha_str, pares_validos):
#     texto_tabla = normalizar(tabla.get_text(" ", strip=True))
#     curso_detectado = extraer_codigo_seccion_desde_texto(texto_tabla, pares_validos)

#     if not curso_detectado:
#         return None, []

#     filas = []
#     vistos = set()

#     for tr in tabla.find_all("tr"):
#         tds = tr.find_all("td")
#         textos = [normalizar(td.get_text(" ", strip=True)) for td in tds]

#         if len(textos) < 5:
#             continue

#         cab = normalizar_busqueda(" ".join(textos[:5]))
#         if "DIA" in cab and "FECHA" in cab and "HORARIO" in cab and "SALA" in cab:
#             continue

#         dia, fecha, horario, sala, ubicacion = textos[:5]

#         if normalizar(fecha) != fecha_str:
#             continue

#         clave = (
#             normalizar(horario),
#             normalizar(sala),
#             normalizar(ubicacion),
#         )

#         if clave in vistos:
#             continue
#         vistos.add(clave)

#         filas.append({
#             "dia": normalizar(dia),
#             "fecha": normalizar(fecha),
#             "horario": normalizar(horario),
#             "sala": normalizar(sala),
#             "ubicacion": normalizar(ubicacion),
#         })

#     return curso_detectado, filas


# def extraer_resultados_html(driver, fecha_str):
#     time.sleep(2.0)
#     html = driver.page_source

#     with open("debug_consultaaulas.html", "w", encoding="utf-8") as f:
#         f.write(html)

#     soup = BeautifulSoup(html, "html.parser")
#     tablas = soup.find_all("table")

#     pares_validos = set()
#     for info in CURSOS.values():
#         for sec in info["secciones"]:
#             pares_validos.add(f"{info['codigo']}-{sec}".upper())

#     resultados = {par: [] for par in pares_validos}

#     for tabla in tablas:
#         curso_detectado, filas = parsear_tabla_resultado(tabla, fecha_str, pares_validos)
#         if not curso_detectado or not filas:
#             continue

#         existentes = {
#             (x["horario"], x["sala"], x["ubicacion"])
#             for x in resultados[curso_detectado]
#         }

#         for fila in filas:
#             clave = (fila["horario"], fila["sala"], fila["ubicacion"])
#             if clave not in existentes:
#                 resultados[curso_detectado].append(fila)
#                 existentes.add(clave)

#     return resultados


# def consultar_todo_el_dia(fecha_str):
#     driver = crear_driver()
#     try:
#         abrir_pagina(driver)
#         setear_fecha(driver, fecha_str)
#         limpiar_selector_curso(driver)
#         setear_texto_busqueda(driver, TEXTO_BUSQUEDA)
#         time.sleep(0.5)
#         enviar_formulario(driver)
#         return extraer_resultados_html(driver, fecha_str)
#     finally:
#         driver.quit()


# def nombre_bonito_fecha(fecha_str):
#     dt = datetime.strptime(fecha_str, "%d-%m-%Y")
#     dias = {
#         0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
#         4: "viernes", 5: "sábado", 6: "domingo"
#     }
#     meses = {
#         1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
#         5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
#         9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
#     }
#     return f"{dias[dt.weekday()]} {dt.day} de {meses[dt.month]}"


# def titulo_sugerido(fecha_str):
#     dt = datetime.strptime(fecha_str, "%d-%m-%Y")
#     meses = {
#         1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
#         5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
#         9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
#     }
#     return f"salas seminario/teórico {dt.day} de {meses[dt.month]}"


# def salas_unicas_en_orden(filas):
#     salas = []
#     vistas = set()

#     for fila in filas:
#         sala = normalizar(fila.get("sala", ""))
#         horario = normalizar(fila.get("horario", ""))

#         clave = (horario, sala)
#         if sala and clave not in vistas:
#             vistas.add(clave)
#             salas.append({
#                 "horario": horario,
#                 "sala": sala,
#             })

#     return salas


# def construir_bloques_por_curso(resultados_planos):
#     salida = {}

#     for curso_key, info in CURSOS.items():
#         bloques = []

#         for seccion in info["secciones"]:
#             par = f"{info['codigo']}-{seccion}".upper()
#             filas = resultados_planos.get(par, [])

#             bloques.append({
#                 "seccion": seccion,
#                 "error": None,
#                 "filas": filas,
#             })

#         salida[curso_key] = bloques

#     return salida


# def bloque_teorico(seccion, info_sec, salas):
#     profe = info_sec.get("profe_teorico", "Por definir")
#     sala = salas[0]["sala"]
#     horario = salas[0]["horario"]
#     return f"Grupo {seccion} ({profe}): {sala} ({horario})"


# def bloque_laboratorio(seccion, info_sec, salas):
#     profes_lab = info_sec.get("profes_laboratorio", [])
#     profes_txt = ", ".join(profes_lab) if profes_lab else "Por definir"

#     lineas = []
#     lineas.append(f"Grupo {seccion} laboratorio ({profes_txt}):")
#     for i, item in enumerate(salas[:2], start=1):
#         lineas.append(f"- Laboratorio {i}: {item['sala']} ({item['horario']})")
#     return "\n".join(lineas)


# def bloque_seminario(seccion, info_sec, salas):
#     profes_sem = info_sec.get("profes_seminario", [])
#     profes_txt = ", ".join(profes_sem) if profes_sem else "Por definir"

#     lineas = []
#     lineas.append(f"Grupo {seccion} seminario ({profes_txt}):")
#     for i, item in enumerate(salas, start=1):
#         lineas.append(f"- Sala {i}: {item['sala']} ({item['horario']})")
#     return "\n".join(lineas)


# def formatear_bloque_seccion(curso_info, bloque):
#     seccion = bloque["seccion"]
#     info_sec = curso_info.get("secciones_info", {}).get(seccion, {})

#     if bloque.get("error"):
#         return f"Grupo {seccion}: revisar manualmente"

#     filas = bloque.get("filas", [])
#     if not filas:
#         return f"Grupo {seccion}: sin sala publicada"

#     salas = salas_unicas_en_orden(filas)
#     n = len(salas)

#     if n == 0:
#         return f"Grupo {seccion}: sin sala publicada"

#     if n == 1:
#         return bloque_teorico(seccion, info_sec, salas)

#     if n == 2:
#         return bloque_laboratorio(seccion, info_sec, salas)

#     return bloque_seminario(seccion, info_sec, salas)


# def construir_mensaje_bonito(fecha_str, resultados_planos):
#     resultados_por_curso = construir_bloques_por_curso(resultados_planos)

#     fecha_linda = nombre_bonito_fecha(fecha_str)
#     titulo = titulo_sugerido(fecha_str)

#     lineas = []
#     lineas.append(f"Título sugerido: {titulo}")
#     lineas.append("")
#     lineas.append("Buen día,")
#     lineas.append("")
#     lineas.append(f"Las salas para el día de hoy {fecha_linda} son:")
#     lineas.append("")

#     hubo_datos = False

#     for curso_key in ["fokito", "enobnu", "tecnologia_medica", "medicina"]:
#         info = CURSOS[curso_key]
#         resultados = resultados_por_curso[curso_key]

#         bloques_texto = []
#         for bloque in resultados:
#             txt = formatear_bloque_seccion(info, bloque)
#             bloques_texto.append(txt)

#             filas = bloque.get("filas", [])
#             if filas:
#                 hubo_datos = True

#         lineas.append(f"{info['nombre']}:")
#         lineas.append("")
#         lineas.append("\n\n".join(bloques_texto))
#         lineas.append("")

#     if not hubo_datos:
#         lineas.append("No encontré salas publicadas para esa fecha.")
#         lineas.append("")

#     lineas.append("Que les vaya muy bien.")

#     return "\n".join(lineas).strip()


# def main():
#     if len(sys.argv) < 2:
#         print("Uso: python3 obtener_salas.py DD-MM-AAAA")
#         print("Ejemplo: python3 obtener_salas.py 26-03-2026")
#         return

#     fecha_str = sys.argv[1]
#     datetime.strptime(fecha_str, "%d-%m-%Y")

#     resultados = consultar_todo_el_dia(fecha_str)
#     mensaje = construir_mensaje_bonito(fecha_str, resultados)
#     print(mensaje)


# if __name__ == "__main__":
#     main()




import sys
import time
import re
import unicodedata
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = "http://consultaaulas.med.uchile.cl/consulta_clase.html"
TEXTO_BUSQUEDA = "MATEM"


# ============================================================
# CONFIGURACIÓN MANUAL
# ============================================================
CURSOS = {
    "fokito": {
        "codigo": "CBA0103",
        "nombre": "FOKITO",
        "secciones": [1, 2, 3, 4],
        "secciones_info": {
            1: {
                "pec": "Ingrid Galaz",
                "profe_teorico": "Ingrid Galaz",
                "profes_laboratorio": ["Ingrid Galaz", "Nathalie Varas", "Gabriela Martinez", "Valeria Brancacho"],
                "profes_seminario": ["Nathalie Varas", "Jose Mondaca", "Maximiliano Bernal"],
            },
            2: {
                "pec": "Juan Carlos Salas",
                "profe_teorico": "Juan Carlos Salas",
                "profes_laboratorio": ["Juan Carlos Salas", "Gabriela Martinez", "Valeria Brancacho", "Eduardo Guerra"],
                "profes_seminario": ["José Mondaca", "Nathalie Varas", "Rosa Muñoz"],
            },
            3: {
                "pec": "Alexander Riquelme",
                "profe_teorico": "Alexander Riquelme",
                "profes_laboratorio": ["Alexander Riquelme", "José Mondaca", "Maximiliano Bernal", "Eduardo Guerra"],
                "profes_seminario": ["José Mondaca", "Rosa Muñoz", "Nathalie Varas"],
            },
            4: {
                "pec": "Caroll Cuellar",
                "profe_teorico": "Caroll Cuellar",
                "profes_laboratorio": ["Eduardo Guerra", "Sebastián Marconi", "Caroll Cuellar", "Gabriel Fraczinet"],
                "profes_seminario": ["Gabriel Fraczinet", "Eduardo Guerra", "Sebastián Marconi"],
            },
        },
    },
    "enobnu": {
        "codigo": "CBA0102",
        "nombre": "ENOBNU",
        "secciones": [1, 2, 3, 4],
        "secciones_info": {
            1: {
                "pec": "Juan Carlos Salas",
                "profe_teorico": "Juan Carlos Salas",
                "profes_laboratorio": [],
                "profes_seminario": ["Maximiliano Bernal", "José Mondaca", "Valeria Brancacho"],
            },
            2: {
                "pec": "Alexander Riquelme",
                "profe_teorico": "Alexander Riquelme",
                "profes_laboratorio": [],
                "profes_seminario": ["Nathalie Varas", "Rosa Muñoz", "Sebastián Marconi"],
            },
            3: {
                "pec": "Ingrid Galaz",
                "profe_teorico": "Ingrid Galaz",
                "profes_laboratorio": [],
                "profes_seminario": ["Maximiliano Bernal", "Diego Hidalgo", "Gabriela Martinez"],
            },
            4: {
                "pec": "Caroll Cuellar",
                "profe_teorico": "Caroll Cuellar",
                "profes_laboratorio": [],
                "profes_seminario": ["Gabriela Martinez", "Valeria Brancacho", "Diego Hidalgo"],
            },
        },
    },
    "tecnologia_medica": {
        "codigo": "TMA01005",
        "nombre": "TECNOLOGÍA MÉDICA",
        "secciones": [1],
        "secciones_info": {
            1: {
                "pec": "Caroll Cuellar",
                "profe_teorico": "Caroll Cuellar",
                "profes_laboratorio": [],
                "profes_seminario": ["J. Tomás Yáñez", "Maximiliano Bernal", "Gabriela Martínez", "Gabriel Fraczinet"],
            },
        },
    },
    "medicina": {
        "codigo": "MED0101",
        "nombre": "MEDICINA",
        "secciones": [1, 2],
        "secciones_info": {
            1: {
                "pec": "Ingrid Galaz",
                "profe_teorico": "Ingrid Galaz",
                "profes_laboratorio": [],
                "profes_seminario": ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
            },
            2: {
                "pec": "Ingrid Galaz",
                "profe_teorico": "Ingrid Galaz",
                "profes_laboratorio": [],
                "profes_seminario": ["J. Tomás Yáñez", "Juan Carlos Salas", "Alexander Riquelme", "Eduardo Guerra"],
            },
        },
    },
}

CALENDAR_PATHS = {
    "fokito": "data/fokito/calendario.xlsx",
    "enobnu": "data/enobnu/calendario.xlsx",
    "tecnologia_medica": "data/tecnologia_medica/calendario.xlsx",
    "medicina": "data/medicina/calendario.xlsx",
}


# ============================================================
# HELPERS GENERALES
# ============================================================
def normalizar(txt):
    return " ".join(str(txt).replace("\xa0", " ").split()).strip()


def sin_tildes(txt):
    txt = str(txt)
    return "".join(
        c for c in unicodedata.normalize("NFD", txt)
        if unicodedata.category(c) != "Mn"
    )


def normalizar_busqueda(txt):
    return sin_tildes(normalizar(txt)).upper()


def safe_strip(x):
    if x is None:
        return ""
    try:
        if pd.isna(x):
            return ""
    except Exception:
        pass
    return str(x).strip()


def normalizar_horario(h):
    h = normalizar(h).replace("–", "-")
    m = re.match(r"^\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*$", h)
    if not m:
        return h
    ini = m.group(1)
    fin = m.group(2)

    def pad(x):
        hh, mm = x.split(":")
        return f"{int(hh):02d}:{mm}"

    return f"{pad(ini)} - {pad(fin)}"


def fecha_bonita(fecha_str):
    dt = datetime.strptime(fecha_str, "%d-%m-%Y")
    dias = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    return f"{dias[dt.weekday()]} {dt.day} de {meses[dt.month]}"


def titulo_sugerido(fecha_str):
    dt = datetime.strptime(fecha_str, "%d-%m-%Y")
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    return f"salas seminario/teórico {dt.day} de {meses[dt.month]}"


# ============================================================
# SELENIUM
# ============================================================
def crear_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,1200")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=es-CL")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def esperar_selector(driver, by, value, timeout=20):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def abrir_pagina(driver):
    driver.get(URL)
    esperar_selector(driver, By.ID, "form", timeout=20)
    esperar_selector(driver, By.ID, "txtFecha", timeout=20)
    esperar_selector(driver, By.ID, "txtCurso", timeout=20)
    time.sleep(1.0)


def setear_fecha(driver, fecha_str):
    fecha_input = esperar_selector(driver, By.ID, "txtFecha", timeout=20)
    driver.execute_script("""
        const inp = arguments[0];
        inp.value = arguments[1];
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        inp.dispatchEvent(new Event('change', { bubbles: true }));
    """, fecha_input, fecha_str)


def setear_texto_busqueda(driver, texto):
    txt_input = esperar_selector(driver, By.ID, "txtCurso", timeout=20)
    driver.execute_script("""
        const inp = arguments[0];
        inp.value = '';
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        inp.dispatchEvent(new Event('change', { bubbles: true }));
    """, txt_input)
    time.sleep(0.2)

    driver.execute_script("""
        const inp = arguments[0];
        inp.value = arguments[1];
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        inp.dispatchEvent(new Event('change', { bubbles: true }));
    """, txt_input, texto)


def limpiar_selector_curso(driver):
    try:
        select_el = esperar_selector(driver, By.ID, "txtSelCurso", timeout=5)
        driver.execute_script("""
            const sel = arguments[0];
            sel.value = '';
            sel.dispatchEvent(new Event('change', { bubbles: true }));
        """, select_el)
    except Exception:
        pass


def enviar_formulario(driver):
    form = esperar_selector(driver, By.ID, "form", timeout=20)
    driver.execute_script("arguments[0].submit();", form)


# ============================================================
# SCRAPING HTML RESULTADOS
# ============================================================
def extraer_codigo_seccion_exacto(texto):
    texto_norm = normalizar_busqueda(texto)
    m = re.search(r"\b([A-Z]{3,}\d{4,5}-\d+)\b", texto_norm)
    if not m:
        return None
    return m.group(1)


def parsear_tabla_horarios(tabla, fecha_str):
    filas = []
    vistos = set()

    for tr in tabla.find_all("tr"):
        tds = tr.find_all("td")
        textos = [normalizar(td.get_text(" ", strip=True)) for td in tds]

        if len(textos) < 5:
            continue

        cab = normalizar_busqueda(" ".join(textos[:5]))
        if "DIA" in cab and "FECHA" in cab and "HORARIO" in cab and "SALA" in cab:
            continue

        dia, fecha, horario, sala, ubicacion = textos[:5]

        if normalizar(fecha) != fecha_str:
            continue

        horario_n = normalizar_horario(horario)
        sala_n = normalizar(sala)
        ubic_n = normalizar(ubicacion)

        clave = (horario_n, sala_n, ubic_n)
        if clave in vistos:
            continue
        vistos.add(clave)

        filas.append({
            "dia": normalizar(dia),
            "fecha": normalizar(fecha),
            "horario": horario_n,
            "sala": sala_n,
            "ubicacion": ubic_n,
        })

    return filas


def extraer_resultados_html(driver, fecha_str):
    time.sleep(2.0)
    html = driver.page_source

    with open("debug_consultaaulas.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")

    pares_validos = set()
    for info in CURSOS.values():
        for sec in info["secciones"]:
            pares_validos.add(f"{info['codigo']}-{sec}".upper())

    resultados = {par: [] for par in pares_validos}

    # Buscamos SOLO bloques "Asignatura: ..."
    bloques = []
    for nodo in soup.find_all(string=re.compile(r"Asignatura\s*:", re.I)):
        parent = nodo.parent
        titulo = normalizar(parent.get_text(" ", strip=True))
        if "Asignatura:" not in titulo:
            continue

        codigo = extraer_codigo_seccion_exacto(titulo)
        if not codigo or codigo not in pares_validos:
            continue

        tabla_horarios = parent.find_next("table")
        if tabla_horarios is None:
            continue

        filas = parsear_tabla_horarios(tabla_horarios, fecha_str)
        if not filas:
            continue

        bloques.append((codigo, filas))

    for codigo, filas in bloques:
        existentes = {(x["horario"], x["sala"], x["ubicacion"]) for x in resultados[codigo]}
        for fila in filas:
            clave = (fila["horario"], fila["sala"], fila["ubicacion"])
            if clave not in existentes:
                resultados[codigo].append(fila)
                existentes.add(clave)

    return resultados


def consultar_todo_el_dia(fecha_str):
    driver = crear_driver()
    try:
        abrir_pagina(driver)
        setear_fecha(driver, fecha_str)
        limpiar_selector_curso(driver)
        setear_texto_busqueda(driver, TEXTO_BUSQUEDA)
        time.sleep(0.5)
        enviar_formulario(driver)
        return extraer_resultados_html(driver, fecha_str)
    finally:
        driver.quit()


# ============================================================
# CALENDARIO ESPERADO DEL DÍA DESDE EXCEL
# ============================================================
def actividad_valida_del_dia(row):
    actividad = safe_strip(row.get("actividad", ""))
    tema = safe_strip(row.get("tema", ""))
    observaciones = safe_strip(row.get("observaciones", ""))

    if actividad not in ["Clase teórica", "Seminario", "Laboratorio"]:
        return False

    txt = normalizar_busqueda(f"{actividad} {tema} {observaciones}")

    if "SIN CLASE" in txt:
        return False
    if "SIN SEMINARIO" in txt:
        return False
    if "SIN LABORATORIO" in txt:
        return False
    if "NO HAY" in txt and actividad == "Laboratorio":
        return False
    if "TRABAJO AUTONOMO" in txt:
        return False
    if "SEMANA RECESO" in txt:
        return False
    if "FERIADO" in txt:
        return False

    return True


def cargar_calendario_del_dia(curso_key, fecha_str):
    path = CALENDAR_PATHS[curso_key]
    fecha_obj = pd.to_datetime(fecha_str, format="%d-%m-%Y", errors="coerce")
    if pd.isna(fecha_obj):
        return []

    df = pd.read_excel(path, sheet_name="Calendario")
    df.columns = [safe_strip(c) for c in df.columns]

    rename = {}
    for c in df.columns:
        cl = c.lower()
        if cl == "seccion":
            rename[c] = "sección"
        elif cl == "evaluacion":
            rename[c] = "evaluación"
        elif cl == "dia":
            rename[c] = "día"
    df = df.rename(columns=rename)

    for c in ["fecha", "horario", "sección", "actividad", "tema", "observaciones", "evaluación"]:
        if c not in df.columns:
            df[c] = ""

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df[df["fecha"].dt.date == fecha_obj.date()].copy()

    esperadas = []
    for _, r in df.iterrows():
        if not actividad_valida_del_dia(r):
            continue

        seccion_txt = safe_strip(r.get("sección", ""))
        m = re.search(r"(\d+)", seccion_txt)
        if not m:
            continue
        seccion = int(m.group(1))

        horario = normalizar_horario(r.get("horario", ""))
        actividad = safe_strip(r.get("actividad", ""))
        tema = safe_strip(r.get("tema", ""))
        evaluacion = safe_strip(r.get("evaluación", ""))

        esperadas.append({
            "curso_key": curso_key,
            "seccion": seccion,
            "actividad": actividad,
            "horario": horario,
            "tema": tema,
            "evaluacion": evaluacion,
        })

    esperadas.sort(key=lambda x: (x["seccion"], x["horario"], x["actividad"]))
    return esperadas


def cargar_todas_las_clases_esperadas(fecha_str):
    salida = {}
    for curso_key in CURSOS.keys():
        salida[curso_key] = cargar_calendario_del_dia(curso_key, fecha_str)
    return salida


# ============================================================
# MATCH ENTRE CALENDARIO Y SALAS
# ============================================================
def agrupar_salas_por_horario(filas):
    grupos = {}
    for fila in filas:
        h = normalizar_horario(fila["horario"])
        grupos.setdefault(h, [])
        grupos[h].append(fila)

    for h in grupos:
        vistos = set()
        limpias = []
        for f in grupos[h]:
            clave = (f["sala"], f["ubicacion"])
            if clave in vistos:
                continue
            vistos.add(clave)
            limpias.append(f)
        grupos[h] = limpias

    return grupos


def construir_resultados_comparados(fecha_str, resultados_salas, esperadas_por_curso):
    comparado = {}
    alertas_sin_sala = []
    alertas_horarios_extra = []

    for curso_key, info in CURSOS.items():
        comparado[curso_key] = []

        for seccion in info["secciones"]:
            codigo_sec = f"{info['codigo']}-{seccion}".upper()
            filas_salas = resultados_salas.get(codigo_sec, [])
            salas_por_horario = agrupar_salas_por_horario(filas_salas)

            esperadas_sec = [
                x for x in esperadas_por_curso[curso_key]
                if x["seccion"] == seccion
            ]

            horarios_esperados = set(x["horario"] for x in esperadas_sec)
            horarios_publicados = set(salas_por_horario.keys())

            # Clases esperadas
            for ev in esperadas_sec:
                horario = ev["horario"]
                filas_match = salas_por_horario.get(horario, [])

                comparado[curso_key].append({
                    "seccion": seccion,
                    "actividad": ev["actividad"],
                    "horario": horario,
                    "tema": ev["tema"],
                    "evaluacion": ev["evaluacion"],
                    "filas": filas_match,
                    "tiene_sala": len(filas_match) > 0,
                })

                if len(filas_match) == 0:
                    info_sec = info["secciones_info"][seccion]
                    alertas_sin_sala.append({
                        "curso_key": curso_key,
                        "curso_nombre": info["nombre"],
                        "seccion": seccion,
                        "actividad": ev["actividad"],
                        "horario": horario,
                        "tema": ev["tema"],
                        "pec": info_sec.get("pec", "POR DEFINIR"),
                    })

            # Horarios publicados que no existen en calendario
            extras = sorted(horarios_publicados - horarios_esperados)
            for h in extras:
                alertas_horarios_extra.append({
                    "curso_key": curso_key,
                    "curso_nombre": info["nombre"],
                    "seccion": seccion,
                    "horario": h,
                    "filas": salas_por_horario[h],
                })

        comparado[curso_key].sort(key=lambda x: (x["seccion"], x["horario"], x["actividad"]))

    return comparado, alertas_sin_sala, alertas_horarios_extra


# ============================================================
# FORMATEO MENSAJE PRINCIPAL
# ============================================================
def bloque_teorico(seccion, info_sec, filas, horario):
    profe = info_sec.get("profe_teorico", "Por definir")
    if not filas:
        return f"Grupo {seccion} teórico ({profe}) {horario}: ⚠️ sin sala publicada"
    sala = filas[0]["sala"]
    return f"Grupo {seccion} teórico ({profe}): {sala} ({horario})"


def bloque_laboratorio(seccion, info_sec, filas, horario):
    profes_lab = info_sec.get("profes_laboratorio", [])
    profes_txt = ", ".join(profes_lab) if profes_lab else "Por definir"

    if not filas:
        return f"Grupo {seccion} laboratorio ({profes_txt}) {horario}: ⚠️ sin sala publicada"

    lineas = []
    lineas.append(f"Grupo {seccion} laboratorio ({profes_txt}):")
    for i, fila in enumerate(filas[:2], start=1):
        lineas.append(f"- Laboratorio {i}: {fila['sala']} ({horario})")
    if len(filas) > 2:
        for i, fila in enumerate(filas[2:], start=3):
            lineas.append(f"- Sala extra {i}: {fila['sala']} ({horario})")
    return "\n".join(lineas)


def bloque_seminario(seccion, info_sec, filas, horario):
    profes_sem = info_sec.get("profes_seminario", [])
    if not filas:
        profes_txt = ", ".join(profes_sem) if profes_sem else "Por definir"
        return f"Grupo {seccion} seminario ({profes_txt}) {horario}: ⚠️ sin sala publicada"

    salas = [f["sala"] for f in filas]
    lineas = [f"Grupo {seccion} seminario:"]

    n_asignar = min(len(profes_sem), len(salas))
    for i in range(n_asignar):
        lineas.append(f"- {profes_sem[i]}: {salas[i]} ({horario})")

    if len(salas) > len(profes_sem):
        for j in range(len(profes_sem), len(salas)):
            lineas.append(f"- Sala extra {j+1}: {salas[j]} ({horario})")

    if len(profes_sem) > len(salas):
        for j in range(len(salas), len(profes_sem)):
            lineas.append(f"- {profes_sem[j]}: revisar manualmente ({horario})")

    return "\n".join(lineas)


def formatear_bloque_evento(curso_info, evento):
    seccion = evento["seccion"]
    actividad = evento["actividad"]
    horario = evento["horario"]
    filas = evento["filas"]
    info_sec = curso_info["secciones_info"][seccion]

    if actividad == "Clase teórica":
        return bloque_teorico(seccion, info_sec, filas, horario)

    if actividad == "Laboratorio":
        return bloque_laboratorio(seccion, info_sec, filas, horario)

    return bloque_seminario(seccion, info_sec, filas, horario)


def construir_mensaje_principal(fecha_str, comparado):
    fecha_linda = fecha_bonita(fecha_str)
    titulo = titulo_sugerido(fecha_str)

    lineas = []
    lineas.append(f"Título sugerido: {titulo}")
    lineas.append("")
    lineas.append("Buen día,")
    lineas.append("")
    lineas.append(f"Las salas para el día de hoy {fecha_linda} son:")
    lineas.append("")

    orden = ["fokito", "enobnu", "tecnologia_medica", "medicina"]
    hubo_algo = False

    for curso_key in orden:
        info = CURSOS[curso_key]
        eventos = comparado.get(curso_key, [])

        if not eventos:
            continue

        lineas.append(f"{info['nombre']}:")
        lineas.append("")

        for ev in eventos:
            bloque = formatear_bloque_evento(info, ev)
            lineas.append(bloque)
            lineas.append("")
            hubo_algo = True

    if not hubo_algo:
        lineas.append("No encontré clases esperadas para esa fecha.")
        lineas.append("")

    lineas.append("Que les vaya muy bien.")

    return "\n".join(lineas).strip()


# ============================================================
# ALERTAS Y CORREOS
# ============================================================
def construir_alerta_para_ti(alertas_horarios_extra):
    if not alertas_horarios_extra:
        return "Sin alertas de horarios extra."

    lineas = []
    lineas.append("ALERTA PARA TI")
    lineas.append("")
    lineas.append("Encontré salas publicadas en horarios que no coinciden con el calendario esperado del día:")
    lineas.append("")

    for x in alertas_horarios_extra:
        lineas.append(f"- {x['curso_nombre']} | Sección {x['seccion']} | Horario {x['horario']}")
        for fila in x["filas"]:
            lineas.append(f"  • {fila['sala']} ({fila['ubicacion']})")
        lineas.append("")

    lineas.append("Esto podría corresponder a certámenes, recuperativos o actividades especiales que conviene revisar manualmente.")
    return "\n".join(lineas).strip()


def construir_resumen_faltantes(alertas_sin_sala):
    if not alertas_sin_sala:
        return "Sin clases sin sala publicada."

    lineas = []
    lineas.append("CLASES ESPERADAS SIN SALA PUBLICADA")
    lineas.append("")

    for x in alertas_sin_sala:
        tema_txt = f" | {x['tema']}" if x["tema"] else ""
        lineas.append(
            f"- {x['curso_nombre']} | Sección {x['seccion']} | {x['actividad']} | {x['horario']} | PEC: {x['pec']}{tema_txt}"
        )

    return "\n".join(lineas).strip()


def construir_correos_pec(fecha_str, alertas_sin_sala):
    if not alertas_sin_sala:
        return "No hay correos para PEC: no faltan salas."

    agrupado = {}
    for x in alertas_sin_sala:
        clave = (x["curso_key"], x["pec"])
        agrupado.setdefault(clave, [])
        agrupado[clave].append(x)

    bloques = []
    fecha_linda = fecha_bonita(fecha_str)

    for (curso_key, pec), items in agrupado.items():
        curso_nombre = CURSOS[curso_key]["nombre"]

        asunto = f"Solicitud urgente de salas — {curso_nombre} — {fecha_linda}"
        cuerpo = []
        cuerpo.append(f"Asunto sugerido: {asunto}")
        cuerpo.append("")
        cuerpo.append(f"Hola {pec},")
        cuerpo.append("")
        cuerpo.append(f"Hoy {fecha_linda} aparecen clases de {curso_nombre} sin sala publicada:")
        cuerpo.append("")

        for it in items:
            tema_txt = f" | {it['tema']}" if it["tema"] else ""
            cuerpo.append(
                f"- Sección {it['seccion']} | {it['actividad']} | {it['horario']}{tema_txt}"
            )

        cuerpo.append("")
        cuerpo.append("¿Podrías pedir la(s) sala(s) con urgencia, por favor?")
        cuerpo.append("")
        cuerpo.append("Quedo atento.")
        cuerpo.append("")

        bloques.append("\n".join(cuerpo).strip())

    return "\n\n" + ("\n\n" + ("=" * 70) + "\n\n").join(bloques)




from collections import defaultdict


def hora_inicio_horario(horario):
    horario = normalizar_horario(horario)
    if "-" in horario:
        return horario.split("-")[0].strip()
    return horario.strip()


def fecha_titulo(fecha_str):
    dt = datetime.strptime(fecha_str, "%d-%m-%Y")
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    return f"{dt.day} de {meses[dt.month]}"


def fecha_cuerpo(fecha_str):
    dt = datetime.strptime(fecha_str, "%d-%m-%Y")
    dias = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    return f"{dias[dt.weekday()]} {dt.day} de {meses[dt.month]}"


def nombre_tipo_simple(actividad):
    if actividad == "Clase teórica":
        return "clase teórica"
    if actividad == "Seminario":
        return "seminario"
    if actividad == "Laboratorio":
        return "laboratorio"
    return actividad.lower()

# def introduccion_evento_para_correo(actividad, fecha_txt_cuerpo, horario, es_primera, n_lineas_evento):
#     tipo_simple = nombre_tipo_simple(actividad)

#     if n_lineas_evento == 1:
#         verbo = "es"
#         sala_txt = "La sala"
#     else:
#         verbo = "son"
#         sala_txt = "Las salas"

#     if es_primera:
#         return f"{sala_txt} de {tipo_simple} para el día de hoy {fecha_txt_cuerpo} a las {horario} {verbo}:"
#     else:
#         return f"{sala_txt} de {tipo_simple} a las {horario} {verbo}:"


def introduccion_evento_para_correo(actividad, fecha_txt_cuerpo, horario, es_primera, n_lineas_evento):
    tipo_simple = nombre_tipo_simple(actividad)
    hora_inicio = hora_inicio_horario(horario)

    if n_lineas_evento == 1:
        verbo = "es"
        sala_txt = "La sala"
    else:
        verbo = "son"
        sala_txt = "Las salas"

    if es_primera:
        return f"{sala_txt} de {tipo_simple} para el día de hoy {fecha_txt_cuerpo} a las {hora_inicio} {verbo}:"
    else:
        return f"{sala_txt} de {tipo_simple} a las {hora_inicio} {verbo}:"


def nombre_tipo_titulo(actividad):
    if actividad == "Clase teórica":
        return "clase teórica"
    if actividad == "Seminario":
        return "seminario"
    if actividad == "Laboratorio":
        return "laboratorio"
    return "clase"


def nombre_tipo_bloque(actividad):
    if actividad == "Clase teórica":
        return "Teórico"
    if actividad == "Seminario":
        return "Seminario"
    if actividad == "Laboratorio":
        return "Laboratorio"
    return actividad


def construir_lineas_teorico(info_sec, filas, horario):
    profe = info_sec.get("profe_teorico", "Por definir")

    if not filas:
        return [f"{nombre_tipo_bloque('Clase teórica')} ({profe}): sin sala publicada ({horario})"]

    sala = filas[0]["sala"]
    return [f"{nombre_tipo_bloque('Clase teórica')} ({profe}): {sala}"]


def construir_lineas_seminario(info_sec, filas, horario):
    profes = info_sec.get("profes_seminario", [])

    if not filas:
        if not profes:
            return [f"Grupo 1 (Por definir): sin sala publicada ({horario})"]
        return [f"Grupo {i+1} ({profes[i]}): sin sala publicada ({horario})" for i in range(len(profes))]

    salas = [f["sala"] for f in filas]
    lineas = []

    n = min(len(profes), len(salas))
    for i in range(n):
        lineas.append(f"Grupo {i+1} ({profes[i]}): {salas[i]}")

    if len(profes) > len(salas):
        for i in range(len(salas), len(profes)):
            lineas.append(f"Grupo {i+1} ({profes[i]}): revisar manualmente")

    if len(salas) > len(profes):
        for i in range(len(profes), len(salas)):
            lineas.append(f"Grupo {i+1}: {salas[i]}")

    return lineas


def construir_lineas_laboratorio(info_sec, filas, horario):
    profes = info_sec.get("profes_laboratorio", [])

    if not filas:
        return [f"Laboratorio: sin sala publicada ({horario})"]

    lineas = []

    # Si quieres con nombres asociados sala a sala:
    salas = [f["sala"] for f in filas]
    n = min(len(profes), len(salas))
    for i in range(n):
        lineas.append(f"Grupo laboratorio {i+1} ({profes[i]}): {salas[i]}")

    if len(salas) > len(profes):
        for i in range(len(profes), len(salas)):
            lineas.append(f"Grupo laboratorio {i+1}: {salas[i]}")

    if len(profes) > len(salas):
        for i in range(len(salas), len(profes)):
            lineas.append(f"Grupo laboratorio {i+1} ({profes[i]}): revisar manualmente")

    return lineas


# def construir_lineas_evento(curso_info, evento):
#     seccion = evento["seccion"]
#     actividad = evento["actividad"]
#     horario = evento["horario"]
#     filas = evento["filas"]

#     info_sec = curso_info["secciones_info"][seccion]

#     if actividad == "Clase teórica":
#         return construir_lineas_teorico(info_sec, filas, horario)

#     if actividad == "Seminario":
#         return construir_lineas_seminario(info_sec, filas, horario)

#     if actividad == "Laboratorio":
#         return construir_lineas_laboratorio(info_sec, filas, horario)

#     return [f"{actividad}: revisar manualmente ({horario})"]

# def construir_lineas_evento(curso_info, ev):
#     actividad = ev["actividad"]
#     info_sec = curso_info["secciones_info"][ev["seccion"]]
#     salas = ev.get("salas", [])

#     # TEÓRICO
#     if actividad == "Clase teórica":
#         profe = info_sec.get("profe_teorico", "Por definir")
#         if not salas:
#             return [f"Teórico ({profe}): sala no informada"]
#         return [f"Teórico ({profe}): {salas[0]}"]

#     # SEMINARIO
#     if actividad == "Seminario":
#         profes = info_sec.get("profes_seminario", [])
#         if not salas:
#             if not profes:
#                 return ["Grupo seminario: sala no informada"]
#             return [f"Grupo {i+1} ({profe}): sala no informada" for i, profe in enumerate(profes)]

#         lineas = []
#         n = min(len(profes), len(salas))
#         for i in range(n):
#             lineas.append(f"Grupo {i+1} ({profes[i]}): {salas[i]}")

#         if len(profes) > len(salas):
#             for i in range(len(salas), len(profes)):
#                 lineas.append(f"Grupo {i+1} ({profes[i]}): sala no informada")

#         if len(salas) > len(profes):
#             for i in range(len(profes), len(salas)):
#                 lineas.append(f"Grupo {i+1}: {salas[i]}")

#         return lineas

#     # LABORATORIO
#     if actividad == "Laboratorio":
#         if not salas:
#             return ["Sala no informada"]

#         return [sala for sala in salas]

#     return []



def construir_lineas_evento(curso_info, ev):
    actividad = ev["actividad"]
    info_sec = curso_info["secciones_info"][ev["seccion"]]
    filas = ev.get("filas", [])
    horario = ev.get("horario", "")

    salas = []
    vistas = set()
    for fila in filas:
        sala = normalizar(fila.get("sala", ""))
        if sala and sala not in vistas:
            salas.append(sala)
            vistas.add(sala)

    # TEÓRICO
    if actividad == "Clase teórica":
        profe = info_sec.get("profe_teorico", "Por definir")
        if not salas:
            return [f"Teórico ({profe}): sin sala publicada ({horario})"]
        return [f"Teórico ({profe}): {salas[0]}"]

    # SEMINARIO
    if actividad == "Seminario":
        profes = info_sec.get("profes_seminario", [])

        if not salas:
            if not profes:
                return [f"Grupo 1: sin sala publicada ({horario})"]
            return [f"Grupo {i+1} ({profe}): sin sala publicada ({horario})" for i, profe in enumerate(profes)]

        lineas = []
        n = min(len(profes), len(salas))

        for i in range(n):
            lineas.append(f"Grupo {i+1} ({profes[i]}): {salas[i]}")

        if len(profes) > len(salas):
            for i in range(len(salas), len(profes)):
                lineas.append(f"Grupo {i+1} ({profes[i]}): revisar manualmente")

        if len(salas) > len(profes):
            for i in range(len(profes), len(salas)):
                lineas.append(f"Grupo {i+1}: {salas[i]}")

        return lineas

    # LABORATORIO
    if actividad == "Laboratorio":
        if not salas:
            return [f"Laboratorio: sin sala publicada ({horario})"]

        # como me pediste: sin nombres de profes
        return [sala for sala in salas]

    return []


# def construir_mensajes_por_seccion(fecha_str, comparado):
#     """
#     Devuelve una lista de dicts:
#     {
#         "curso_key": ...,
#         "curso_nombre": ...,
#         "codigo_seccion": "MED0101-1",
#         "titulo": "...",
#         "cuerpo": "..."
#     }
#     """
#     mensajes = []
#     fecha_txt_titulo = fecha_titulo(fecha_str)
#     fecha_txt_cuerpo = fecha_cuerpo(fecha_str)

#     for curso_key, eventos in comparado.items():
#         curso_info = CURSOS[curso_key]
#         codigo = curso_info["codigo"]

#         por_seccion = defaultdict(list)
#         for ev in eventos:
#             por_seccion[ev["seccion"]].append(ev)

#         for seccion in sorted(por_seccion.keys()):
#             eventos_sec = sorted(
#                 por_seccion[seccion],
#                 key=lambda x: (x["horario"], x["actividad"])
#             )

#             if not eventos_sec:
#                 continue

#             codigo_seccion = f"{codigo}-{seccion}"

#             actividades_unicas = list(dict.fromkeys([ev["actividad"] for ev in eventos_sec]))

#             # -------------------------
#             # TITULO
#             # -------------------------
#             if len(eventos_sec) == 1:
#                 tipo = nombre_tipo_titulo(eventos_sec[0]["actividad"])
#                 titulo = f"salas de {tipo} {fecha_txt_titulo}"
#             else:
#                 titulo = f"salas de clases {fecha_txt_titulo}"

#             # -------------------------
#             # CUERPO
#             # -------------------------
#             lineas = []

#             if len(eventos_sec) == 1:
#                 tipo = nombre_tipo_simple(eventos_sec[0]["actividad"])
#                 lineas.append(f"Buen día,")
#                 lineas.append("")
#                 lineas.append(f"Las salas de {tipo} para el día de hoy {fecha_txt_cuerpo} son:")
#                 lineas.append("")

#                 for linea in construir_lineas_evento(curso_info, eventos_sec[0]):
#                     lineas.append(linea)

#             else:
#                 lineas.append("Buen día,")
#                 lineas.append("")
#                 if len(actividades_unicas) == 1:
#                     lineas.append(f"La sala de clases para el día de hoy {fecha_txt_cuerpo} es:")
#                 else:
#                     lineas.append(f"Las salas de clases para el día de hoy {fecha_txt_cuerpo} son:")
#                 lineas.append("")

#                 for actividad in ["Clase teórica", "Seminario", "Laboratorio"]:
#                     sub = [ev for ev in eventos_sec if ev["actividad"] == actividad]
#                     if not sub:
#                         continue

#                     lineas.append(f"{nombre_tipo_bloque(actividad)}:")
#                     for ev in sub:
#                         for linea in construir_lineas_evento(curso_info, ev):
#                             lineas.append(linea)
#                     lineas.append("")

#                 while lineas and lineas[-1] == "":
#                     lineas.pop()

#             lineas.append("")
#             lineas.append("Que les vaya muy bien.")
            
#             lineas.append("")
#             lineas.append("J. Tomás Yáñez")

#             mensajes.append({
#                 "curso_key": curso_key,
#                 "curso_nombre": curso_info["nombre"],
#                 "codigo_seccion": codigo_seccion,
#                 "titulo": titulo,
#                 "cuerpo": "\n".join(lineas).strip(),
#             })

#     return mensajes



# def construir_mensajes_por_seccion(fecha_str, comparado):
#     """
#     Devuelve una lista de dicts:
#     {
#         "curso_key": ...,
#         "curso_nombre": ...,
#         "codigo_seccion": "MED0101-1",
#         "titulo": "...",
#         "cuerpo": "..."
#     }
#     """
#     mensajes = []
#     fecha_txt_titulo = fecha_titulo(fecha_str)
#     fecha_txt_cuerpo = fecha_cuerpo(fecha_str)

#     for curso_key, eventos in comparado.items():
#         curso_info = CURSOS[curso_key]
#         codigo = curso_info["codigo"]

#         por_seccion = defaultdict(list)
#         for ev in eventos:
#             por_seccion[ev["seccion"]].append(ev)

#         for seccion in sorted(por_seccion.keys()):
#             eventos_sec = sorted(
#                 por_seccion[seccion],
#                 key=lambda x: (x["horario"], x["actividad"])
#             )

#             if not eventos_sec:
#                 continue

#             codigo_seccion = f"{codigo}-{seccion}"
#             actividades_unicas = list(dict.fromkeys([ev["actividad"] for ev in eventos_sec]))

#             # -------------------------------------------------
#             # Contar cuántas líneas reales habrá en el mensaje
#             # -------------------------------------------------
#             lineas_eventos = []
#             for ev in eventos_sec:
#                 lineas_eventos.extend(construir_lineas_evento(curso_info, ev))

#             n_lineas_eventos = len(lineas_eventos)

#             # =====================================================
#             # TITULO
#             # =====================================================
#             if len(actividades_unicas) == 1:
#                 tipo = nombre_tipo_titulo(actividades_unicas[0])

#                 if n_lineas_eventos == 1:
#                     titulo = f"sala de {tipo} {fecha_txt_titulo}"
#                 else:
#                     titulo = f"salas de {tipo} {fecha_txt_titulo}"
#             else:
#                 if n_lineas_eventos == 1:
#                     titulo = f"sala de clase {fecha_txt_titulo}"
#                 else:
#                     titulo = f"salas de clases {fecha_txt_titulo}"

#             # =====================================================
#             # CUERPO
#             # =====================================================
#             lineas = []
#             lineas.append("Buen día,")
#             lineas.append("")

#             if len(actividades_unicas) == 1:
#                 tipo = nombre_tipo_simple(actividades_unicas[0])

#                 if n_lineas_eventos == 1:
#                     lineas.append(f"La sala de {tipo} para el día de hoy {fecha_txt_cuerpo} es:")
#                 else:
#                     lineas.append(f"Las salas de {tipo} para el día de hoy {fecha_txt_cuerpo} son:")
#                 lineas.append("")

#                 for ev in eventos_sec:
#                     for linea in construir_lineas_evento(curso_info, ev):
#                         lineas.append(linea)

#             else:
#                 if n_lineas_eventos == 1:
#                     lineas.append(f"La sala de clase para el día de hoy {fecha_txt_cuerpo} es:")
#                 else:
#                     lineas.append(f"Las salas de clases para el día de hoy {fecha_txt_cuerpo} son:")
#                 lineas.append("")

#                 for actividad in ["Clase teórica", "Seminario", "Laboratorio"]:
#                     sub = [ev for ev in eventos_sec if ev["actividad"] == actividad]
#                     if not sub:
#                         continue

#                     lineas.append(f"{nombre_tipo_bloque(actividad)}:")
#                     for ev in sub:
#                         for linea in construir_lineas_evento(curso_info, ev):
#                             lineas.append(linea)
#                     lineas.append("")

#                 while lineas and lineas[-1] == "":
#                     lineas.pop()

#             lineas.append("")
#             lineas.append("Que les vaya muy bien.")
#             lineas.append("")
#             lineas.append("J. Tomás Yáñez")

#             mensajes.append({
#                 "curso_key": curso_key,
#                 "curso_nombre": curso_info["nombre"],
#                 "codigo_seccion": codigo_seccion,
#                 "titulo": titulo,
#                 "cuerpo": "\n".join(lineas).strip(),
#             })

#     return mensajes


# def construir_mensajes_por_seccion(fecha_str, comparado):
#     """
#     Devuelve una lista de dicts:
#     {
#         "curso_key": ...,
#         "curso_nombre": ...,
#         "codigo_seccion": "MED0101-1",
#         "titulo": "...",
#         "cuerpo": "..."
#     }
#     """
#     mensajes = []
#     fecha_txt_titulo = fecha_titulo(fecha_str)
#     fecha_txt_cuerpo = fecha_cuerpo(fecha_str)

#     for curso_key, eventos in comparado.items():
#         curso_info = CURSOS[curso_key]
#         codigo = curso_info["codigo"]

#         por_seccion = defaultdict(list)
#         for ev in eventos:
#             por_seccion[ev["seccion"]].append(ev)

#         for seccion in sorted(por_seccion.keys()):
#             eventos_sec = sorted(
#                 por_seccion[seccion],
#                 key=lambda x: (x["horario"], x["actividad"])
#             )

#             if not eventos_sec:
#                 continue

#             codigo_seccion = f"{codigo}-{seccion}"
#             actividades_unicas = list(dict.fromkeys([ev["actividad"] for ev in eventos_sec]))

#             lineas_eventos = []
#             for ev in eventos_sec:
#                 lineas_eventos.extend(construir_lineas_evento(curso_info, ev))

#             n_lineas_eventos = len(lineas_eventos)

#             # -------------------------
#             # TÍTULO
#             # -------------------------
#             if len(actividades_unicas) == 1:
#                 tipo = nombre_tipo_titulo(actividades_unicas[0])
#                 if n_lineas_eventos == 1:
#                     titulo = f"sala de {tipo} {fecha_txt_titulo}"
#                 else:
#                     titulo = f"salas de {tipo} {fecha_txt_titulo}"
#             else:
#                 if n_lineas_eventos == 1:
#                     titulo = f"sala de clase {fecha_txt_titulo}"
#                 else:
#                     titulo = f"salas de clases {fecha_txt_titulo}"

#             # -------------------------
#             # CUERPO
#             # -------------------------
#             lineas = []
#             lineas.append("Buen día,")
#             lineas.append("")

#             if len(actividades_unicas) == 1:
#                 # tipo = nombre_tipo_simple(actividades_unicas[0])

#                 # if n_lineas_eventos == 1:
#                 #     lineas.append(f"La sala de {tipo} para el día de hoy {fecha_txt_cuerpo} es:")
#                 # else:
#                 #     lineas.append(f"Las salas de {tipo} para el día de hoy {fecha_txt_cuerpo} son:")
#                 # lineas.append("")
                
#                 tipo = nombre_tipo_simple(actividades_unicas[0])

#                 if n_lineas_eventos == 1:
#                     lineas.append(f"La sala de {tipo} para el día de hoy {fecha_txt_cuerpo} es:")
#                 else:
#                     lineas.append(f"Las salas de {tipo} para el día de hoy {fecha_txt_cuerpo} son:")

#                 for ev in eventos_sec:
#                     for linea in construir_lineas_evento(curso_info, ev):
#                         lineas.append(linea)

#             else:
#                 if n_lineas_eventos == 1:
#                     lineas.append(f"La sala de clase para el día de hoy {fecha_txt_cuerpo} es:")
#                 else:
#                     lineas.append(f"Las salas de clases para el día de hoy {fecha_txt_cuerpo} son:")
#                 lineas.append("")

#                 for actividad in ["Clase teórica", "Seminario", "Laboratorio"]:
#                     sub = [ev for ev in eventos_sec if ev["actividad"] == actividad]
#                     if not sub:
#                         continue

#                     # Si hay solo un bloque de ese tipo, no pongas encabezado repetido
#                     if len(sub) == 1:
#                         ev = sub[0]
#                         for linea in construir_lineas_evento(curso_info, ev):
#                             lineas.append(linea)
#                         lineas.append("")
#                     else:
#                         lineas.append(f"{nombre_tipo_bloque(actividad)}:")
#                         for ev in sub:
#                             for linea in construir_lineas_evento(curso_info, ev):
#                                 lineas.append(linea)
#                         lineas.append("")

#                 while lineas and lineas[-1] == "":
#                     lineas.pop()

#             lineas.append("")
#             lineas.append("Que les vaya muy bien.")
#             lineas.append("")
#             lineas.append("J. Tomás Yáñez")

#             mensajes.append({
#                 "curso_key": curso_key,
#                 "curso_nombre": curso_info["nombre"],
#                 "codigo_seccion": codigo_seccion,
#                 "titulo": titulo,
#                 "cuerpo": "\n".join(lineas).strip(),
#             })

#     return mensajes




def construir_mensajes_por_seccion(fecha_str, comparado):
    """
    Devuelve una lista de dicts:
    {
        "curso_key": ...,
        "curso_nombre": ...,
        "codigo_seccion": "MED0101-1",
        "titulo": "...",
        "cuerpo": "..."
    }
    """
    mensajes = []
    fecha_txt_titulo = fecha_titulo(fecha_str)
    fecha_txt_cuerpo = fecha_cuerpo(fecha_str)

    for curso_key, eventos in comparado.items():
        curso_info = CURSOS[curso_key]
        codigo = curso_info["codigo"]

        por_seccion = defaultdict(list)
        for ev in eventos:
            por_seccion[ev["seccion"]].append(ev)

        for seccion in sorted(por_seccion.keys()):
            eventos_sec = sorted(
                por_seccion[seccion],
                key=lambda x: (x["horario"], x["actividad"])
            )

            if not eventos_sec:
                continue

            codigo_seccion = f"{codigo}-{seccion}"
            actividades_unicas = list(dict.fromkeys([ev["actividad"] for ev in eventos_sec]))

            # contar líneas reales de salida
            total_lineas_eventos = 0
            for ev in eventos_sec:
                total_lineas_eventos += len(construir_lineas_evento(curso_info, ev))

            # -------------------------
            # TÍTULO
            # -------------------------
            if len(eventos_sec) == 1:
                tipo = nombre_tipo_titulo(eventos_sec[0]["actividad"])
                n_lineas = len(construir_lineas_evento(curso_info, eventos_sec[0]))
                if n_lineas == 1:
                    titulo = f"sala de {tipo} {fecha_txt_titulo}"
                else:
                    titulo = f"salas de {tipo} {fecha_txt_titulo}"
            else:
                if total_lineas_eventos == 1:
                    titulo = f"sala de clase {fecha_txt_titulo}"
                else:
                    titulo = f"salas de clases {fecha_txt_titulo}"

            # -------------------------
            # CUERPO
            # -------------------------
            lineas = []
            lineas.append("Hola buen día,")
            lineas.append("")

            primer_bloque = True

            for ev in eventos_sec:
                lineas_evento = construir_lineas_evento(curso_info, ev)
                n_lineas_evento = len(lineas_evento)

                intro = introduccion_evento_para_correo(
                    actividad=ev["actividad"],
                    fecha_txt_cuerpo=fecha_txt_cuerpo,
                    horario=ev["horario"],
                    es_primera=primer_bloque,
                    n_lineas_evento=n_lineas_evento
                )

                lineas.append(intro)
                lineas.append("")

                for linea in lineas_evento:
                    lineas.append(linea)

                lineas.append("")
                primer_bloque = False

            while lineas and lineas[-1] == "":
                lineas.pop()

            lineas.append("")
            lineas.append("¡Que les vaya muy bien!,")
            lineas.append("")
            lineas.append("J. Tomás Yáñez")

            mensajes.append({
                "curso_key": curso_key,
                "curso_nombre": curso_info["nombre"],
                "codigo_seccion": codigo_seccion,
                "titulo": titulo,
                "cuerpo": "\n".join(lineas).strip(),
            })

    return mensajes



def imprimir_mensajes_por_seccion(fecha_str, comparado):
    mensajes = construir_mensajes_por_seccion(fecha_str, comparado)

    if not mensajes:
        print("No hay mensajes por sección para esa fecha.")
        return

    for msg in mensajes:
        print("=" * 90)
        print(f"SECCIÓN: {msg['codigo_seccion']} ({msg['curso_nombre']})")
        print(f"TÍTULO: {msg['titulo']}")
        print("")
        print(msg["cuerpo"])
        print("")


# ============================================================
# MAIN
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("Uso: python3 obtener_salas.py DD-MM-AAAA")
        print("Ejemplo: python3 obtener_salas.py 23-03-2026")
        return

    fecha_str = sys.argv[1]
    datetime.strptime(fecha_str, "%d-%m-%Y")

    resultados_salas = consultar_todo_el_dia(fecha_str)
    esperadas_por_curso = cargar_todas_las_clases_esperadas(fecha_str)

    comparado, alertas_sin_sala, alertas_horarios_extra = construir_resultados_comparados(
        fecha_str=fecha_str,
        resultados_salas=resultados_salas,
        esperadas_por_curso=esperadas_por_curso,
    )

    imprimir_mensajes_por_seccion(fecha_str, comparado)

    print("\n" + "=" * 80 + "\n")
    print(construir_resumen_faltantes(alertas_sin_sala))

    print("\n" + "=" * 80 + "\n")
    print(construir_alerta_para_ti(alertas_horarios_extra))

    print("\n" + "=" * 80 + "\n")
    print("BORRADORES DE CORREO A PEC")
    print(construir_correos_pec(fecha_str, alertas_sin_sala))


if __name__ == "__main__":
    main()