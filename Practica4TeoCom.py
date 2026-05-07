import flet as ft
import xml.etree.ElementTree as ET
import re
import os
import traceback

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

    def validate_is_afd(self):
        """Verifica que el autómata cargado sea un AFD válido (sin épsilon ni ambigüedad)"""
        for (frm, sym), to in self.transitions.items():
            if sym == "ε" or sym == "":
                return False, f"Transición ε detectada en el estado {frm}. Es un AFND."
        if not self.initial_state:
            return False, "No hay estado inicial definido (recuerda marcarlo en JFLAP)."
        return True, "AFD Válido."

    def from_jff(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            root = ET.fromstring(f.read())
            
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
                if (frm, sym) in self.transitions:
                    raise ValueError(f"AFND detectado: El estado {frm} tiene múltiples transiciones con '{sym}'.")
                if sym == "ε":
                    raise ValueError(f"AFND-ε detectado: El estado {frm} tiene una transición vacía (ε).")
                self.transitions[(frm, sym)] = to
                symbols.add(sym)
        self.alphabet = sorted(list(symbols))

    def to_regex_step_by_step(self):
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
                    r_ik, r_kj = trans[(q_i, q_k)], trans[(q_k, q_j)]
                    r_kk = f"({loop})*" if loop else ""
                    path = f"({r_ik}){r_kk}({r_kj})".replace("(ε)", "").replace("ε", "")
                    if not path: path = "ε"
                    existing = trans.get((q_i, q_j), "")
                    trans[(q_i, q_j)] = f"({existing}|{path})" if existing else path
            trans = {k: v for k, v in trans.items() if k[0] != q_k and k[1] != q_k}
            estado_actual = ", ".join([f"δ({k[0]} -> {k[1]}) = {v}" for k, v in trans.items()])
            steps.append(f"   Transiciones resultantes:\n   {estado_actual}")

        final_regex = trans.get((start, accept), "∅")
        steps.append(f"⭐ Expresión Regular Final:\n{final_regex}") 
        return final_regex, steps

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================

def main(page: ft.Page):
    page.title = "Práctica 4"
    page.theme_mode = "dark"
    page.padding = 20
    
    BG, PURPLE, ACCENT, NEON, DANGER = "#0D1117", "#7b61ff", "#58A6FF", "#00ffb3", "#F85149"
    page.bgcolor = BG

    # --- TAB 1: CADENAS ---
    txt_cadena = ft.TextField(label="Cadena σ", hint_text="ej: escom", border_color=PURPLE)
    col_resultados_cadenas = ft.Column(scroll="auto", expand=True)

    def chip(text, color, bg):
        return ft.Container(content=ft.Text(text, font_family="monospace", size=13, color=color), bgcolor=bg, border_radius=6, padding=ft.padding.symmetric(horizontal=10, vertical=5))

    def calcular_cadenas(e):
        s = txt_cadena.value.strip()
        if not s: return
        col_resultados_cadenas.controls.clear()
        subs, pres, sufs = get_substrings(s), get_prefixes(s), get_suffixes(s)
        col_resultados_cadenas.controls.append(ft.Text(f"SUBCADENAS ({len(subs)})", color=NEON, weight="bold"))
        col_resultados_cadenas.controls.append(ft.Row([chip(t, NEON, "#00ffb31A") for t in subs], wrap=True))
        col_resultados_cadenas.controls.append(ft.Text(f"PREFIJOS ({len(pres)})", color=PURPLE, weight="bold"))
        col_resultados_cadenas.controls.append(ft.Row([chip(t, PURPLE, "#7b61ff1A") for t in pres], wrap=True))
        col_resultados_cadenas.controls.append(ft.Text(f"SUFIJOS ({len(sufs)})", color=ACCENT, weight="bold"))
        col_resultados_cadenas.controls.append(ft.Row([chip(t, ACCENT, "#58A6FF1A") for t in sufs], wrap=True))
        page.update()

    tab_cadenas = ft.Container(content=ft.Column([
        ft.Text("Operaciones de Cadenas", size=20, weight="bold", color=NEON),
        ft.Row([txt_cadena, ft.ElevatedButton("Calcular", on_click=calcular_cadenas, bgcolor=PURPLE, color="white")]),
        ft.Divider(height=20, color="white24"), col_resultados_cadenas
    ]), padding=20)

    # --- TAB 2: AFD ---
    afd = AFD()
    txt_estados = ft.TextField(label="Estados (ej: q0,q1)", width=150)
    txt_alfabeto = ft.TextField(label="Alfabeto (ej: 0,1)", width=150)
    txt_inicial = ft.TextField(label="Inicial", width=100)
    txt_aceptacion = ft.TextField(label="Aceptación", width=150)
    
    txt_ruta_jff = ft.TextField(label="Ruta de tu archivo JFLAP (ej: C:/Users/tu_usuario/Desktop/auto.jff)", expand=True)
    
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

    def volcar_ui_a_memoria():
        afd.states = [s.strip() for s in txt_estados.value.split(",") if s.strip()]
        afd.alphabet = [a.strip() for a in txt_alfabeto.value.split(",") if a.strip()]
        afd.initial_state = txt_inicial.value.strip()
        afd.accept_states = set([s.strip() for s in txt_aceptacion.value.split(",") if s.strip()])
        afd.transitions = {k: v.value.strip() for k, v in trans_inputs.items() if v.value.strip()}

    def actualizar_ui_desde_memoria():
        txt_estados.value = ",".join(afd.states)
        txt_alfabeto.value = ",".join(afd.alphabet)
        txt_inicial.value = afd.initial_state
        txt_aceptacion.value = ",".join(afd.accept_states)
        generar_tabla(None)
        for (frm, sym), to in afd.transitions.items():
            if (frm, sym) in trans_inputs: trans_inputs[(frm, sym)].value = to
        page.update()

    def guardar_afd_memoria_btn(e):
        volcar_ui_a_memoria()
        valido, msg = afd.validate_is_afd()
        if not valido:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error de Validación: {msg}", color="white"), bgcolor=DANGER)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("AFD Guardado en Memoria Correctamente", color="white"), bgcolor="green")
        page.snack_bar.open = True
        page.update()

    def cargar_jflap_manual(e):
        ruta = txt_ruta_jff.value.strip().replace('"', '').replace("'", "") 
        if not ruta: 
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, ingresa una ruta primero", color="white"), bgcolor=DANGER)
            page.snack_bar.open = True
            page.update()
            return
            
        if not os.path.exists(ruta):
            page.snack_bar = ft.SnackBar(ft.Text("El archivo no existe. Revisa que la ruta sea correcta.", color="white"), bgcolor=DANGER)
            page.snack_bar.open = True
            page.update()
            return
            
        try:
            afd.from_jff(ruta)
            valido, msg = afd.validate_is_afd()
            if not valido: raise ValueError(msg)
            actualizar_ui_desde_memoria()
            page.snack_bar = ft.SnackBar(ft.Text("✓ JFLAP Importado y Válido", color="white"), bgcolor="green")
        except Exception as ex:
            traceback.print_exc()
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al cargar: {ex}", color="white"), bgcolor=DANGER)
            
        page.snack_bar.open = True
        page.update()

    col_pasos_er = ft.Column(scroll="auto", height=200)
    def convertir_a_er(e):
        col_pasos_er.controls.clear()
        volcar_ui_a_memoria()
        valido, msg = afd.validate_is_afd()
        if not afd.states or not valido:
            col_pasos_er.controls.append(ft.Text(f"Error: {msg}", color=DANGER))
        else:
            er, pasos = afd.to_regex_step_by_step()
            for paso in pasos: col_pasos_er.controls.append(ft.Text(paso, font_family="monospace", color="white70"))
        page.update()

    tab_afd = ft.Container(content=ft.Column([
        ft.Text("1. Importación JFLAP (.jff)", size=20, weight="bold", color=ACCENT),
        ft.Row([txt_ruta_jff, ft.ElevatedButton("Cargar JFLAP", icon="upload_file", on_click=cargar_jflap_manual)]),
        ft.Divider(height=20, color="white24"),
        
        ft.Text("2. Definición Manual / Vista de Tabla", size=20, weight="bold", color=ACCENT),
        ft.Row([txt_estados, txt_alfabeto, txt_inicial, txt_aceptacion], wrap=True),
        ft.Row([
            ft.ElevatedButton("Generar Tabla Manual", on_click=generar_tabla),
            ft.ElevatedButton("Guardar AFD en Memoria", on_click=guardar_afd_memoria_btn, bgcolor="green", color="white")
        ]), 
        col_tabla_trans,
        ft.Divider(height=20, color="white24"),
        
        ft.Text("3. Conversión a ER (Eliminación de Estados)", size=20, weight="bold", color=NEON),
        ft.FilledButton("Convertir AFD a ER", on_click=convertir_a_er, bgcolor=NEON, color="black"),
        ft.Container(content=col_pasos_er, border=ft.border.all(1, "white24"), padding=10, border_radius=5)
    ], scroll="auto"), padding=20)

    # --- TAB 3: AFND ---
    tabla_afnd, estados_activos = {}, set(["q0"])
    txt_origen, txt_simb_afnd, txt_destino = ft.TextField(label="Origen", width=100), ft.TextField(label="Símbolo", width=80), ft.TextField(label="Destino", width=100)
    lista_trans_afnd, row_activos, txt_entrada_sim = ft.ListView(height=100), ft.Row(wrap=True), ft.TextField(label="Símbolo", width=120)

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

    tab_afnd = ft.Container(content=ft.Column([
        ft.Text("Definición AFND", size=20, weight="bold"),
        ft.Row([txt_origen, txt_simb_afnd, txt_destino, ft.ElevatedButton("Agregar", on_click=add_trans_afnd)]),
        ft.Container(content=lista_trans_afnd, border=ft.border.all(1, "white54"), padding=10), ft.Divider(),
        ft.Text("Estados Activos:"), row_activos,
        ft.Row([txt_entrada_sim, ft.FilledButton("Paso", on_click=paso_afnd, icon="play_arrow")])
    ]), padding=20)

    # --- TAB 4: VALIDATORES (PESTAÑAS PERSONALIZADAS SEGURAS) ---
    validador_state = [0] # 0: Correo, 1: Telefono, 2: Fecha
    
    txt_prueba_er = ft.TextField(label="Ingresa texto a validar", expand=True)
    lbl_er_info = ft.Text("", font_family="monospace", color=ACCENT)
    lbl_er_feedback = ft.Text("", weight="bold")
    row_visual_afd = ft.Row(scroll="auto", vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # Botones que simulan pestañas
    btn_tab_email = ft.ElevatedButton("1. Correo", bgcolor=PURPLE, color="white")
    btn_tab_tel = ft.ElevatedButton("2. Teléfono", bgcolor="#1A1A24", color="white")
    btn_tab_fecha = ft.ElevatedButton("3. Fecha", bgcolor="#1A1A24", color="white")
    
    def draw_afd_node(state, is_final=False):
        return ft.Container(content=ft.Text(state, weight="bold"), width=50, height=50, border_radius=25, alignment=ft.Alignment.CENTER, border=ft.border.all(2, NEON if is_final else ACCENT), bgcolor="#1A1A24")
    
    def draw_afd_transition(label):
        return ft.Row([ft.Text("─"), ft.Text(label, size=12, color=PURPLE), ft.Text("→")], spacing=0)

    def on_validador_tab_change(idx):
        validador_state[0] = idx
        
        # Cambiar colores de las "pestañas"
        btn_tab_email.bgcolor = PURPLE if idx == 0 else "#1A1A24"
        btn_tab_tel.bgcolor = PURPLE if idx == 1 else "#1A1A24"
        btn_tab_fecha.bgcolor = PURPLE if idx == 2 else "#1A1A24"
        
        row_visual_afd.controls.clear()
        
        if idx == 0:
            lbl_er_info.value, nodos = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", [("q0", "[a-z]"), ("q1", "@"), ("q2", "[a-z]"), ("q3", "."), ("q4", "Final")]
        elif idx == 1:
            lbl_er_info.value, nodos = "^\\d{10}$", [("q0", "\\d"), ("q1", "..."), ("q9", "\\d"), ("q10", "Final")]
        elif idx == 2:
            lbl_er_info.value, nodos = "^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\\d{4}$", [("q0", "Día"), ("q1", "/"), ("q2", "Mes"), ("q3", "/"), ("q4", "Final")]
            
        for i, (q, t) in enumerate(nodos):
            row_visual_afd.controls.append(draw_afd_node(q, is_final=(i==len(nodos)-1)))
            if i < len(nodos)-1: row_visual_afd.controls.append(draw_afd_transition(t))
            
        lbl_er_feedback.value = ""
        txt_prueba_er.value = ""
        page.update()

    # Asignar los eventos a los botones-pestaña
    btn_tab_email.on_click = lambda _: on_validador_tab_change(0)
    btn_tab_tel.on_click = lambda _: on_validador_tab_change(1)
    btn_tab_fecha.on_click = lambda _: on_validador_tab_change(2)

    def probar_regex(e):
        texto, valido, sugerencia = txt_prueba_er.value.strip(), False, ""
        idx = validador_state[0]
        
        if idx == 0:
            patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            valido = re.match(patron, texto)
            if not valido: sugerencia = "Falta '@' o dominio"
        elif idx == 1:
            patron = r"^\d{10}$"
            valido = re.match(patron, texto)
            if not valido: sugerencia = "Deben ser 10 dígitos"
        elif idx == 2:
            patron = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
            valido = re.match(patron, texto)
            if not valido: sugerencia = "Formato DD/MM/YYYY"
            
        lbl_er_feedback.value = "✓ VÁLIDA" if valido else f"✗ INVÁLIDA: {sugerencia}"
        lbl_er_feedback.color = "green" if valido else DANGER
        page.update()

    txt_prueba_er.on_submit = probar_regex

    tab_regex = ft.Container(content=ft.Column([
        ft.Text("Validadores Prácticos", size=20, weight="bold", color=PURPLE),
        ft.Row([btn_tab_email, btn_tab_tel, btn_tab_fecha]), # Menú de Pestañas Personalizado
        ft.Container(content=lbl_er_info, padding=10, bgcolor="white10", border_radius=5),
        ft.Text("Estructura AFD (Desliza si es necesario):", color=ACCENT, weight="bold"),
        ft.Container(content=row_visual_afd, padding=10, border=ft.border.all(1, "white24"), border_radius=5),
        ft.Row([txt_prueba_er, ft.ElevatedButton("Validar", on_click=probar_regex, bgcolor=PURPLE, color="white")]), 
        lbl_er_feedback
    ]), padding=20)

    update_activos()
    on_validador_tab_change(0) # Iniciar en la pestaña de Correo
    content_area = ft.Container(content=tab_cadenas, expand=True)

    def switch_tab(index):
        vistas = [tab_cadenas, tab_afd, tab_afnd, tab_regex]
        content_area.content = vistas[index]
        page.update()

    nav_bar = ft.Row([
        ft.ElevatedButton("1. Cadenas", on_click=lambda _: switch_tab(0), bgcolor=PURPLE),
        ft.ElevatedButton("2. AFD & ER", on_click=lambda _: switch_tab(1), bgcolor=ACCENT),
        ft.ElevatedButton("3. AFND", on_click=lambda _: switch_tab(2), bgcolor="blue700"),
        ft.ElevatedButton("4. Validadores", on_click=lambda _: switch_tab(3), bgcolor=NEON, color="black"),
    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)

    page.add(ft.Column([nav_bar, ft.Divider(height=10, color="white24"), content_area], expand=True))

if __name__ == "__main__":
    ft.app(target=main)
