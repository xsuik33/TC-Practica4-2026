import flet as ft
import xml.etree.ElementTree as ET
import re

# ==========================================
# LÓGICA CORE: CADENAS Y AFD
# ==========================================

def get_substrings(s: str) -> list[str]:
    seen, result = set(), []
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            sub = s[i:j]
            if sub not in seen:
                seen.add(sub)
                result.append(sub)
    return sorted(result, key=lambda x: (len(x), x))

def get_prefixes(s: str) -> list[str]: return [s[: i + 1] for i in range(len(s))]
def get_suffixes(s: str) -> list[str]: return [s[i:] for i in range(len(s))]

class AFD:
    def __init__(self):
        self.states = []
        self.alphabet = []
        self.initial_state = ""
        self.accept_states = set()
        self.transitions = {}

    def validate(self, string: str):
        if not self.initial_state: return False, []
        current = self.initial_state
        trace = [{"step": 0, "state": current, "remaining": string, "symbol": None}]
        for i, symbol in enumerate(string):
            if symbol not in self.alphabet: return False, trace
            key = (current, symbol)
            if key not in self.transitions: return False, trace
            current = self.transitions[key]
            trace.append({"step": i+1, "state": current, "remaining": string[i+1:], "symbol": symbol})
        return current in self.accept_states, trace

    def from_jff(self, content: str):
        """Importa un AFD desde un archivo JFLAP (.jff)"""
        root = ET.fromstring(content)
        self.states, self.transitions, self.accept_states = [], {}, set()
        id_to_name = {}
        
        for state in root.findall(".//state"):
            sid, name = state.get("id"), state.get("name")
            id_to_name[sid] = name
            self.states.append(name)
            if state.find("initial") is not None: self.initial_state = name
            if state.find("final") is not None: self.accept_states.add(name)
            
        symbols = set()
        for trans in root.findall(".//transition"):
            frm = id_to_name.get(trans.findtext("from"))
            to = id_to_name.get(trans.findtext("to"))
            sym = trans.findtext("read") or "ε"
            if frm and to:
                self.transitions[(frm, sym)] = to
                if sym != "ε": symbols.add(sym)
        self.alphabet = sorted(list(symbols))

    def to_regex_step_by_step(self):
        """Convierte el AFD a ER mediante eliminación de estados (GNFA)"""
        trans = {}
        for (s, sym), dst in self.transitions.items():
            if (s, dst) in trans: trans[(s, dst)] += f"|{sym}"
            else: trans[(s, dst)] = sym

        start, accept = "Q_init", "Q_final"
        trans[(start, self.initial_state)] = "ε"
        for f in self.accept_states: trans[(f, accept)] = "ε"

        steps = []
        estados_a_eliminar = list(self.states)

        for q_k in estados_a_eliminar:
            steps.append(f"➔ Eliminando estado: {q_k}")
            incoming = [s for (s, d) in trans.keys() if d == q_k and s != q_k]
            outgoing = [d for (s, d) in trans.keys() if s == q_k and d != q_k]
            loop = trans.get((q_k, q_k), "")

            for q_i in incoming:
                for q_j in outgoing:
                    r_ik = trans[(q_i, q_k)]
                    r_kj = trans[(q_k, q_j)]
                    r_kk = f"({loop})*" if loop else ""

                    path = f"({r_ik}){r_kk}({r_kj})"
                    path = path.replace("(ε)", "").replace("ε", "")
                    if not path: path = "ε"

                    existing = trans.get((q_i, q_j), "")
                    trans[(q_i, q_j)] = f"({existing}|{path})" if existing else path

            trans = {k: v for k, v in trans.items() if k[0] != q_k and k[1] != q_k}
            
            estado_actual = ", ".join([f"δ({k[0]} -> {k[1]}) = {v}" for k, v in trans.items()])
            steps.append(f"   Transiciones resultantes:\n   {estado_actual}")

        final_regex = trans.get((start, accept), "∅")
        final_regex = final_regex.replace("((", "(").replace("))", ")")
        steps.append(f"⭐ Expresión Regular Final:\n{final_regex}")
        
        return final_regex, steps


# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================

def main(page: ft.Page):
    page.title = "Omni-Automata & Compiler Lab - ESCOM IPN"
    page.theme_mode = "dark"
    page.padding = 20
    
    # Paleta ESCOM
    BG = "#0D1117"
    PURPLE = "#7b61ff"
    ACCENT = "#58A6FF"
    NEON = "#00ffb3"
    DANGER = "#F85149"
    page.bgcolor = BG

    # ---------------------------------------------------------
    # TAB 1: CADENAS Y CERRADURAS
    # ---------------------------------------------------------
    txt_cadena = ft.TextField(label="Cadena σ", hint_text="ej: escom", border_color=PURPLE)
    col_resultados_cadenas = ft.Column(scroll="auto", expand=True)

    def chip(text, color, bg):
        return ft.Container(
            content=ft.Text(text, font_family="monospace", size=13, color=color),
            bgcolor=bg, border_radius=6, padding=ft.padding.symmetric(horizontal=10, vertical=5),
        )

    def calcular_cadenas(e):
        s = txt_cadena.value.strip()
        if not s: return
        col_resultados_cadenas.controls.clear()
        subs, pres, sufs = get_substrings(s), get_prefixes(s), get_suffixes(s)
        col_resultados_cadenas.controls.append(ft.Text(f"SUBCADENAS ({len(subs)})", color=NEON, weight="bold"))
        col_resultados_cadenas.controls.append(ft.Row([chip(t, NEON, "#00ffb31A") for t in subs], wrap=True))
        col_resultados_cadenas.controls.append(ft.Text(f"PREFIJOS ({len(pres)})", color=PURPLE, weight="bold"))
        col_resultados_cadenas.controls.append(ft.Row([chip(t, PURPLE, "#7b61ff1A") for t in pres], wrap=True))
        page.update()

    tab_cadenas = ft.Container(
        content=ft.Column([
            ft.Text("Operaciones de Cadenas", size=20, weight="bold", color=NEON),
            ft.Row([txt_cadena, ft.ElevatedButton("Calcular", on_click=calcular_cadenas, bgcolor=PURPLE, color="white")]),
            ft.Divider(height=20, color="white24"),
            col_resultados_cadenas
        ]), padding=20
    )

    # ---------------------------------------------------------
    # TAB 2: SIMULADOR AFD & CONVERSIÓN ER
    # ---------------------------------------------------------
    afd = AFD()
    txt_estados = ft.TextField(label="Estados (ej: q0,q1)", width=150)
    txt_alfabeto = ft.TextField(label="Alfabeto (ej: 0,1)", width=150)
    txt_inicial = ft.TextField(label="Inicial", width=100)
    txt_aceptacion = ft.TextField(label="Aceptación", width=150)
    
    col_tabla_trans = ft.Column()
    trans_inputs = {}

    def generar_tabla(e):
        col_tabla_trans.controls.clear()
        trans_inputs.clear()
        estados = [s.strip() for s in txt_estados.value.split(",") if s.strip()]
        alfabeto = [a.strip() for a in txt_alfabeto.value.split(",") if a.strip()]
        if not estados or not alfabeto: return
        
        col_tabla_trans.controls.append(ft.Row([ft.Container(width=60)] + [ft.Text(sym, width=60, color=ACCENT, weight="bold") for sym in alfabeto]))
        for est in estados:
            fila = [ft.Text(est, width=60, weight="bold")]
            for sym in alfabeto:
                tf = ft.TextField(width=60, height=40, content_padding=5)
                trans_inputs[(est, sym)] = tf
                fila.append(tf)
            col_tabla_trans.controls.append(ft.Row(fila))
        page.update()

    def guardar_afd(e):
        afd.states = [s.strip() for s in txt_estados.value.split(",") if s.strip()]
        afd.alphabet = [a.strip() for a in txt_alfabeto.value.split(",") if a.strip()]
        afd.initial_state = txt_inicial.value.strip()
        afd.accept_states = set([s.strip() for s in txt_aceptacion.value.split(",") if s.strip()])
        afd.transitions = {k: v.value.strip() for k, v in trans_inputs.items() if v.value.strip()}
        page.snack_bar = ft.SnackBar(ft.Text("AFD Guardado", color="white"), bgcolor="green")
        page.snack_bar.open = True
        page.update()

    # --- Importar JFLAP (Versión Manual a prueba de fallos) ---
    txt_ruta_jff = ft.TextField(label="Ruta del archivo .jff (ej: C:/descargas/auto.jff)", expand=True)

    def cargar_jflap_manual(e):
        ruta = txt_ruta_jff.value.strip()
        ruta = ruta.replace('"', '').replace("'", "") 
        if not ruta: return
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                afd.from_jff(f.read())
            txt_estados.value = ",".join(afd.states)
            txt_alfabeto.value = ",".join(afd.alphabet)
            txt_inicial.value = afd.initial_state
            txt_aceptacion.value = ",".join(afd.accept_states)
            page.snack_bar = ft.SnackBar(ft.Text("JFLAP Importado con éxito", color="white"), bgcolor=ACCENT)
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al leer: {ex}", color="white"), bgcolor=DANGER)
            page.snack_bar.open = True
        page.update()

    # --- Conversión a ER ---
    col_pasos_er = ft.Column(scroll="auto", height=200)
    def convertir_a_er(e):
        col_pasos_er.controls.clear()
        if not afd.states:
            col_pasos_er.controls.append(ft.Text("Primero guarda o importa un AFD.", color=DANGER))
            page.update()
            return
        
        er, pasos = afd.to_regex_step_by_step()
        for paso in pasos:
            col_pasos_er.controls.append(ft.Text(paso, font_family="monospace", color="white70"))
        page.update()

    tab_afd = ft.Container(
        content=ft.Column([
            ft.Text("1. Definición / Importación AFD", size=20, weight="bold", color=ACCENT),
            ft.Row([
                txt_ruta_jff, 
                ft.ElevatedButton("Cargar .jff", icon="upload_file", on_click=cargar_jflap_manual)
            ]),
            ft.Row([txt_estados, txt_alfabeto, txt_inicial, txt_aceptacion], wrap=True),
            ft.Row([ft.ElevatedButton("Generar Tabla", on_click=generar_tabla), ft.ElevatedButton("Guardar AFD", on_click=guardar_afd, bgcolor=ACCENT, color="white")]),
            col_tabla_trans,
            ft.Divider(height=20, color="white24"),
            ft.Text("2. Conversión a Expresión Regular (Eliminación de Estados)", size=20, weight="bold", color=NEON),
            ft.FilledButton("Convertir AFD a ER", on_click=convertir_a_er, bgcolor=NEON, color="black"),
            ft.Container(content=col_pasos_er, border=ft.border.all(1, "white24"), padding=10, border_radius=5)
        ], scroll="auto"), padding=20
    )

    # ---------------------------------------------------------
    # TAB 3: MOTOR AFND (Tiempo Real)
    # ---------------------------------------------------------
    tabla_afnd = {}
    estados_activos = set(["q0"])
    txt_origen = ft.TextField(label="Origen", width=100)
    txt_simb_afnd = ft.TextField(label="Símbolo", width=80)
    txt_destino = ft.TextField(label="Destino", width=100)
    lista_trans_afnd = ft.ListView(height=100)
    row_activos = ft.Row(wrap=True)
    txt_entrada_sim = ft.TextField(label="Símbolo", width=120)

    def update_activos():
        row_activos.controls.clear()
        for e in estados_activos: row_activos.controls.append(ft.Chip(label=ft.Text(e), bgcolor="blue700"))
        page.update()

    def add_trans_afnd(e):
        o, s, d = txt_origen.value.strip(), txt_simb_afnd.value.strip(), txt_destino.value.strip()
        if o and s and d:
            if (o, s) not in tabla_afnd: tabla_afnd[(o, s)] = []
            tabla_afnd[(o, s)].append(d)
            lista_trans_afnd.controls.append(ft.Text(f"δ({o}, {s}) -> {d}"))
            txt_destino.value = ""
            page.update()

    def paso_afnd(e):
        sim = txt_entrada_sim.value.strip()
        if sim:
            nuevos = set()
            for est in estados_activos:
                if (est, sim) in tabla_afnd: nuevos.update(tabla_afnd[(est, sim)])
            estados_activos.clear()
            estados_activos.update(nuevos)
            txt_entrada_sim.value = ""
            update_activos()

    tab_afnd = ft.Container(
        content=ft.Column([
            ft.Text("Definición AFND", size=20, weight="bold"),
            ft.Row([txt_origen, txt_simb_afnd, txt_destino, ft.ElevatedButton("Agregar", on_click=add_trans_afnd)]),
            ft.Container(content=lista_trans_afnd, border=ft.border.all(1, "white54"), padding=10),
            ft.Divider(),
            ft.Text("Estados Activos (Simulación):"), row_activos,
            ft.Row([txt_entrada_sim, ft.FilledButton("Paso", on_click=paso_afnd, icon="play_arrow")])
        ]), padding=20
    )

    # ---------------------------------------------------------
    # TAB 4: VALIDADORES PRÁCTICOS (EXPRESIONES REGULARES)
    # ---------------------------------------------------------
    dd_validador = ft.Dropdown(
        label="Selecciona el Validador",
        options=[
            ft.dropdown.Option("email", "1. Correo Electrónico"),
            ft.dropdown.Option("telefono", "2. Teléfono (10 dígitos)"),
            ft.dropdown.Option("fecha", "3. Fecha (DD/MM/YYYY)"),
        ],
        width=300,
        value="email"
    )
    
    txt_prueba_er = ft.TextField(label="Texto a validar", width=300)
    lbl_er_info = ft.Text("ER: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", font_family="monospace", color=ACCENT)
    lbl_er_feedback = ft.Text("", weight="bold")
    
    def on_dropdown_change(e):
        if dd_validador.value == "email":
            lbl_er_info.value = "ER: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$\nEstructura AFD: [Usuario] -> @ -> [Dominio] -> . -> [TLD]"
        elif dd_validador.value == "telefono":
            lbl_er_info.value = "ER: ^\\d{10}$\nEstructura AFD: q0 -(d)-> q1 -(d)-> ... -(d)-> q10(Final)"
        elif dd_validador.value == "fecha":
            lbl_er_info.value = "ER: ^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\\d{4}$\nEstructura AFD: [Día] -> / -> [Mes] -> / -> [Año(4)]"
        lbl_er_feedback.value = ""
        page.update()

    dd_validador.on_change = on_dropdown_change

    def probar_regex(e):
        texto = txt_prueba_er.value.strip()
        valido = False
        sugerencia = ""

        if dd_validador.value == "email":
            patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            valido = re.match(patron, texto)
            if not valido: sugerencia = "Falta un '@' o un dominio válido (ej. '.com')"
        elif dd_validador.value == "telefono":
            patron = r"^\d{10}$"
            valido = re.match(patron, texto)
            if not valido: sugerencia = "Deben ser exactamente 10 números, sin espacios ni letras."
        elif dd_validador.value == "fecha":
            patron = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
            valido = re.match(patron, texto)
            if not valido: sugerencia = "El formato debe ser estricto DD/MM/YYYY (ej: 25/04/2026)."

        if valido:
            lbl_er_feedback.value = "✓ CADENA VÁLIDA (Cumple con el patrón)"
            lbl_er_feedback.color = "green"
        else:
            lbl_er_feedback.value = f"✗ INVÁLIDA. Sugerencia: {sugerencia}"
            lbl_er_feedback.color = DANGER
        page.update()

    tab_regex = ft.Container(
        content=ft.Column([
            ft.Text("Validadores Prácticos con Expresiones Regulares", size=20, weight="bold", color=PURPLE),
            ft.Text("Selecciona un caso de uso práctico para ver su ER y probar validaciones."),
            dd_validador,
            ft.Container(content=lbl_er_info, padding=10, bgcolor="white10", border_radius=5),
            ft.Row([txt_prueba_er, ft.ElevatedButton("Validar", on_click=probar_regex, bgcolor=PURPLE, color="white")]),
            lbl_er_feedback
        ]), padding=20
    )

    # ---------------------------------------------------------
    # NAVEGACIÓN MANUAL (Bypass ft.Tabs)
    # ---------------------------------------------------------
    update_activos()
    content_area = ft.Container(content=tab_cadenas, expand=True)

    def switch_tab(index):
        vistas = [tab_cadenas, tab_afd, tab_afnd, tab_regex]
        content_area.content = vistas[index]
        page.update()

    nav_bar = ft.Row([
        ft.ElevatedButton("1. Cadenas", on_click=lambda _: switch_tab(0), bgcolor=PURPLE, color="white"),
        ft.ElevatedButton("2. Simulador AFD & ER", on_click=lambda _: switch_tab(1), bgcolor=ACCENT, color="white"),
        ft.ElevatedButton("3. Motor AFND", on_click=lambda _: switch_tab(2), bgcolor="blue700", color="white"),
        ft.ElevatedButton("4. Validadores ER", on_click=lambda _: switch_tab(3), bgcolor=NEON, color="black"),
    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)

    page.add(ft.Column([nav_bar, ft.Divider(height=10, color="white24"), content_area], expand=True))

if __name__ == "__main__":
    ft.app(target=main)