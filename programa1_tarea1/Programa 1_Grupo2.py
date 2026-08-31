import sys
from fractions import Fraction
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

# =====================================================================
# CONSTANTES Y PALETA DE COLORES
# Usamos la paleta personalizada: fondo blanco, texto negro y 
# detalles en tonos océano para los botones.
# =====================================================================
FONDO              = "#FFFFFF"   # Blanco puro para fondos y tarjetas
TARJETA            = "#FFFFFF"   
TEXTO              = "#000000"   # Negro puro para números y ecuaciones
TEXTO_SUAVE        = "#333333"   # Gris oscuro para subtítulos

ACENTO             = "#0077B6"   # Vibrante Zafiro (Botón principal)
ACENTO_HOVER       = "#023E8A"   # Oscuro Índigo (Hover del principal)
BOTON_SEC          = "#90E0EF"   # Claro Aguamarina (Botones de apoyo)
BOTON_SEC_HOVER    = "#00B4D8"   # Tabla de Surf (Hover de apoyo)
CELDA_BORDE        = "#00B4D8"   # Bordes de la matriz

EXITO              = "#059669"   # Verde para la comprobación correcta
ADVERTENCIA        = "#8A4E02"   # Oscuro Mandarina (Infinitas soluciones)
ERROR              = "#8A0A02"   # Rico Escarlata (Sistema inconsistente)

LETRA_MONO         = "Consolas"
MAX_DIMENSION      = 8           

AYUDA_NUMERO = "Ingresa un entero, decimal o fracción (ej: 3, -2.5 o 3/4). Una casilla vacía vale 0."


# =====================================================================
# BLOQUE 1: LECTURA Y FORMATO DE NÚMEROS
# =====================================================================
def a_numero(texto):
    """Convierte lo que el usuario escribe en una fracción matemática exacta."""
    texto = texto.strip().replace(" ", "")
    if texto == "":
        return Fraction(0)

    if "/" in texto:
        partes = texto.split("/")
        if len(partes) != 2 or partes[0] == "" or partes[1] == "":
            raise ValueError("Fracción mal escrita. " + AYUDA_NUMERO)
        try:
            numerador = Fraction(partes[0])
            denominador = Fraction(partes[1])
        except (ValueError, ZeroDivisionError):
            raise ValueError("Fracción mal escrita. " + AYUDA_NUMERO)
        if denominador == 0:
            raise ValueError("El denominador no puede ser cero.")
        return numerador / denominador

    try:
        return Fraction(texto)
    except (ValueError, ZeroDivisionError):
        raise ValueError("Valor no reconocido. " + AYUDA_NUMERO)

def formato(valor):
    """Muestra el número bonito en pantalla (ej. '5' en lugar de '5/1')."""
    valor = Fraction(valor)
    if valor.denominator == 1:
        return str(valor.numerator)
    return f"{valor.numerator}/{valor.denominator}"

def formato_matriz(matriz, col_barra=None, sangria="    "):
    """Convierte nuestra matriz matemática en texto alineado para mostrar en la interfaz."""
    if not matriz:
        return []
    anchos = [0] * len(matriz[0])
    for fila in matriz:
        for c, valor in enumerate(fila):
            anchos[c] = max(anchos[c], len(formato(valor)))

    lineas = []
    for fila in matriz:
        piezas = []
        for c, valor in enumerate(fila):
            if col_barra is not None and c == col_barra:
                piezas.append("|")
            piezas.append(formato(valor).rjust(anchos[c]))
        lineas.append(sangria + "[ " + "  ".join(piezas) + " ]")
    return lineas


# =====================================================================
# BLOQUE 1B: INTÉRPRETE DE ECUACIONES
# =====================================================================
ORDEN_LETRAS = ["x", "y", "z", "w", "u", "v", "s", "t"]
EQUIVALENCIAS = {
    "−": "-", "–": "-", "—": "-", "×": "*", "·": "*",
    "≡": "=", "＝": "=", "₀": "0", "₁": "1", "₂": "2", 
    "₃": "3", "₄": "4", "₅": "5", "₆": "6", "₇": "7", 
    "₈": "8", "₉": "9",
}
LETRAS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITOS = "0123456789"

def _partir_variable(texto):
    if texto == "": return None
    corte = 0
    while corte < len(texto) and texto[corte] in LETRAS:
        corte += 1
    if corte == 0: return None
    letras = texto[:corte]
    digitos = texto[corte:]
    for caracter in digitos:
        if caracter not in DIGITOS: return None
    return letras, digitos

def _buscar_variable_al_final(cuerpo):
    final = len(cuerpo)
    posicion = final
    while posicion > 0 and cuerpo[posicion - 1] in DIGITOS:
        posicion -= 1
    fin_letras = posicion
    while posicion > 0 and cuerpo[posicion - 1] in LETRAS:
        posicion -= 1
    if posicion == fin_letras: return None
    letras = cuerpo[posicion:fin_letras]
    digitos = cuerpo[fin_letras:final]
    return posicion, letras, digitos

def _normalizar(linea):
    for original, reemplazo in EQUIVALENCIAS.items():
        linea = linea.replace(original, reemplazo)
    linea = linea.replace("*", "").replace("_", "")
    return "".join(linea.split())

def _trocear(lado):
    if lado == "": return []
    if lado[0] not in "+-": lado = "+" + lado
    terminos, actual = [], lado[0]
    for caracter in lado[1:]:
        if caracter in "+-":
            terminos.append(actual)
            actual = caracter
        else:
            actual += caracter
    terminos.append(actual)
    return terminos

def _numero_del_termino(texto, termino, numero_linea):
    try:
        return a_numero(texto)
    except ValueError as error:
        raise ValueError(f"Ecuación {numero_linea}, término «{termino}»: {error}")

def _leer_termino(termino, numero_linea):
    signo = -1 if termino[0] == "-" else 1
    cuerpo = termino[1:]
    if cuerpo == "": raise ValueError(f"Ecuación {numero_linea}: hay un signo suelto.")
    hallazgo = _buscar_variable_al_final(cuerpo)
    if hallazgo is None:
        return signo * _numero_del_termino(cuerpo, termino, numero_linea), None
    inicio, letras, digitos = hallazgo
    nombre = letras.lower() + digitos
    texto_coeficiente = cuerpo[:inicio]
    if texto_coeficiente == "":
        coeficiente = Fraction(1)
    elif texto_coeficiente.endswith("/"):
        raise ValueError(f"Ecuación {numero_linea}: falta el denominador en «{termino}».")
    else:
        coeficiente = _numero_del_termino(texto_coeficiente, termino, numero_linea)
    return signo * coeficiente, nombre

def _ordenar_variables(nombres):
    con_numero, sin_numero = [], []
    for nombre in nombres:
        letra, digitos = _partir_variable(nombre)
        if digitos: con_numero.append((letra, int(digitos), nombre))
        else: sin_numero.append((letra, nombre))
    con_numero.sort(key=lambda dato: (dato[0], dato[1]))
    def clave_letra(dato):
        letra = dato[0]
        if letra in ORDEN_LETRAS: return (0, ORDEN_LETRAS.index(letra))
        return (1, letra)
    sin_numero.sort(key=clave_letra)
    return [dato[2] for dato in con_numero] + [dato[1] for dato in sin_numero]

def interpretar_ecuaciones(texto):
    """Convierte el bloque de texto con ecuaciones a la matriz A y el vector b."""
    lineas = [linea for linea in texto.splitlines() if linea.strip() != ""]
    if not lineas: raise ValueError("No se escribió ninguna ecuación.")
    ecuaciones, nombres = [], set()

    for indice, linea_original in enumerate(lineas, start=1):
        linea = _normalizar(linea_original)
        if linea.count("=") != 1:
            raise ValueError(f"Ecuación {indice}: debe llevar exactamente un signo '='.")
        izquierda, derecha = linea.split("=")
        if izquierda == "" or derecha == "":
            raise ValueError(f"Ecuación {indice}: falta un lado de la igualdad.")

        coeficientes, constante = {}, Fraction(0)
        for lado, orientacion in ((izquierda, 1), (derecha, -1)):
            for termino in _trocear(lado):
                valor, nombre = _leer_termino(termino, indice)
                if nombre is None:
                    constante -= orientacion * valor
                else:
                    coeficientes[nombre] = coeficientes.get(nombre, Fraction(0)) + orientacion * valor
                    nombres.add(nombre)

        if not coeficientes: raise ValueError(f"Ecuación {indice}: no tiene ninguna variable.")
        ecuaciones.append((coeficientes, constante))

    orden = _ordenar_variables(nombres)
    A, b = [], []
    for coeficientes, constante in ecuaciones:
        A.append([coeficientes.get(nombre, Fraction(0)) for nombre in orden])
        b.append(constante)
    return A, b, orden


# =====================================================================
# BLOQUE 2: ESCALONAMIENTO Y REDUCCIÓN (MÉTODO DE GAUSS-JORDAN)
# Ahora llega hasta la Matriz Identidad (1s en diagonal, 0s en el resto)
# =====================================================================
def intercambiar_filas(matriz, i, j):
    """Cambia la fila i por la j."""
    matriz[i], matriz[j] = matriz[j], matriz[i]
    return f"Intercambio de filas: F{i+1} <-> F{j+1}"

def reemplazar_fila(matriz, destino, factor, origen):
    """Hace cero el número restando filas."""
    matriz[destino] = [matriz[destino][c] - factor * matriz[origen][c] for c in range(len(matriz[destino]))]
    return f"Anular en F{destino+1}: F{destino+1} = F{destino+1} - ({formato(factor)}) * F{origen+1}"

def escalonar(matriz, col_barra=None):
    """Lleva la matriz a su forma escalonada reducida (Identidad)."""
    pasos = []
    filas = len(matriz)
    columnas = len(matriz[0])
    fila_pivote = 0
    pivotes = []

    pasos.append("--- FASE 1: MÉTODO DE GAUSS (Ceros debajo de los pivotes) ---")
    pasos.append("")

    for col in range(columnas - 1): # Nos detenemos antes del vector b
        if fila_pivote >= filas: break

        fila_no_nula = None
        for f in range(fila_pivote, filas):
            if matriz[f][col] != 0:
                fila_no_nula = f
                break
        
        if fila_no_nula is None:
            continue 

        if fila_no_nula != fila_pivote:
            pasos.append(intercambiar_filas(matriz, fila_pivote, fila_no_nula))
            pasos.extend(formato_matriz(matriz, col_barra))
            pasos.append("")

        # Novedad: Convertir el pivote a 1 (Normalizar)
        pivote_val = matriz[fila_pivote][col]
        if pivote_val != 1:
            matriz[fila_pivote] = [x / pivote_val for x in matriz[fila_pivote]]
            pasos.append(f"Convertir pivote a 1: F{fila_pivote+1} = F{fila_pivote+1} / ({formato(pivote_val)})")
            pasos.extend(formato_matriz(matriz, col_barra))
            pasos.append("")

        # Generar ceros por debajo
        for f in range(fila_pivote + 1, filas):
            if matriz[f][col] != 0:
                factor = matriz[f][col]
                pasos.append(reemplazar_fila(matriz, f, factor, fila_pivote))
                pasos.extend(formato_matriz(matriz, col_barra))
                pasos.append("")

        pivotes.append((fila_pivote, col))
        fila_pivote += 1

    # Bajar filas nulas al final
    f = fila_pivote
    while f < filas:
        if all(valor == 0 for valor in matriz[f]):
            siguiente = None
            for g in range(f + 1, filas):
                if any(valor != 0 for valor in matriz[g]):
                    siguiente = g
                    break
            if siguiente is None: break
            pasos.append(intercambiar_filas(matriz, f, siguiente))
            pasos.extend(formato_matriz(matriz, col_barra))
            pasos.append("")
        f += 1

    # Novedad: Fase 2 (Gauss-Jordan) -> Ceros por encima de la diagonal
    if len(pivotes) > 0:
        pasos.append("--- FASE 2: GAUSS-JORDAN (Ceros arriba de los pivotes) ---")
        pasos.append("")
        hubo_operaciones_arriba = False
        
        # Recorremos los pivotes de abajo hacia arriba
        for i in range(len(pivotes)-1, -1, -1):
            f_piv, c_piv = pivotes[i]
            for f_arriba in range(f_piv - 1, -1, -1):
                if matriz[f_arriba][c_piv] != 0:
                    factor = matriz[f_arriba][c_piv]
                    pasos.append(reemplazar_fila(matriz, f_arriba, factor, f_piv))
                    pasos.extend(formato_matriz(matriz, col_barra))
                    pasos.append("")
                    hubo_operaciones_arriba = True
                    
        if not hubo_operaciones_arriba:
            pasos.append("La matriz ya estaba completamente reducida.")
            pasos.append("")

    return pasos, pivotes

def entrada_principal(fila):
    """Busca el primer elemento distinto de cero en una fila."""
    for c, valor in enumerate(fila):
        if valor != 0: return c
    return None

def es_escalonada(matriz):
    """Verificador usado por las pruebas automáticas para confirmar que el algoritmo no falló."""
    principales = [entrada_principal(fila) for fila in matriz]
    vista_nula = False
    for p in principales:
        if p is None:
            vista_nula = True
        elif vista_nula:
            return False, "hay una fila no nula debajo de una fila de ceros"
    anterior = -1
    for p in principales:
        if p is None: continue
        if p <= anterior: return False, "las entradas principales no forman escalera"
        anterior = p
    return True, ""


# =====================================================================
# BLOQUE 4: CLASIFICACIÓN Y SUSTITUCIÓN REGRESIVA
# =====================================================================
def resolver_sistema(m, n, A, b):
    A = [[Fraction(valor) for valor in fila] for fila in A]
    b = [Fraction(valor) for valor in b]
    aumentada = [A[i][:] + [b[i]] for i in range(m)]

    pasos = ["Matriz aumentada inicial [A|b]:"]
    pasos.extend(formato_matriz(aumentada, n))
    pasos.append("")

    pasos_escalonamiento, pivotes = escalonar(aumentada, n)
    if pasos_escalonamiento:
        pasos.extend(pasos_escalonamiento)
    else:
        pasos.append("La matriz ya estaba en forma escalonada; no hizo falta ninguna operación.")
    
    pasos.append("Forma Escalonada Reducida Final (Matriz Identidad):")
    pasos.extend(formato_matriz(aumentada, n))

    columnas_pivote = [c for _, c in pivotes]
    resultado = {
        "pasos": pasos,
        "escalonada": [fila[:] for fila in aumentada],
        "homogeneo": all(valor == 0 for valor in b),
        "variables_libres": [],
        "solucion": None,
        "m": m,
        "n": n,
    }

    # Caso Inconsistente (0 = k)
    if n in columnas_pivote:
        fila_k = 0
        for i, fila in enumerate(aumentada):
            if all(valor == 0 for valor in fila[:n]) and fila[n] != 0:
                fila_k = i
                break
        valor_k = formato(aumentada[fila_k][n])
        resultado["clasificacion"] = "Inconsistente"
        resultado["descripcion"] = f"Sistema sin solución. La fila {fila_k+1} quedó como [0 0 ... 0 | {valor_k}], que es la ecuación imposible 0 = {valor_k}."
        resultado["verificacion"] = "No hay solución que comprobar: el sistema es inconsistente."
        return resultado

    pivotes_variables = [(f, c) for f, c in pivotes if c < n]
    columnas_con_pivote = [c for _, c in pivotes_variables]
    variables_libres = [c for c in range(n) if c not in columnas_con_pivote]
    resultado["variables_libres"] = variables_libres

    # Caso Infinitas Soluciones
    if variables_libres:
        cantidad_pivotes = len(pivotes_variables)
        cantidad_libres = len(variables_libres)
        resultado["clasificacion"] = "Consistente Indeterminado"
        resultado["descripcion"] = f"Sistema con infinitas soluciones. Hay {cantidad_pivotes} pivotes para {n} variables, dejando {cantidad_libres} variables libres."
        resultado["verificacion"] = "El sistema tiene infinitas soluciones. Los valores dependen de las variables libres."
        return resultado

    # Caso Solución Única
    solucion = sustitucion_regresiva(aumentada, n, pivotes_variables)
    resultado["clasificacion"] = "Consistente Determinado"
    resultado["descripcion"] = f"Sistema con solución única. Hay un pivote en cada una de las {n} columnas, sin variables libres."
    resultado["solucion"] = solucion
    
    # Comprobación explícita (número a número)
    texto_verificacion = verificar(m, n, A, b, solucion)
    resultado["verificacion"] = texto_verificacion
    
    # Inyectar la comprobación al final del panel de Procedimiento
    resultado["pasos"].append("")
    resultado["pasos"].append("========================================")
    resultado["pasos"].append("COMPROBACIÓN DEL SISTEMA (PASO FINAL):")
    resultado["pasos"].append("========================================")
    resultado["pasos"].extend(texto_verificacion.split("\n"))
    
    return resultado

def sustitucion_regresiva(aumentada, n, pivotes_variables):
    """Despeja las variables de abajo hacia arriba."""
    x = [Fraction(0)] * n
    for fila_p, col_p in reversed(pivotes_variables):
        total = aumentada[fila_p][n]
        for c in range(col_p + 1, n):
            total -= aumentada[fila_p][c] * x[c]
        x[col_p] = total / aumentada[fila_p][col_p]
    return x

def verificar(m, n, A, b, solucion):
    """Reemplaza los resultados en el sistema original armando la ecuación paso a paso."""
    lineas = ["Sustituyendo explícitamente los valores hallados en las ecuaciones originales:"]
    todo_correcto = True
    
    for i in range(m):
        total = Fraction(0)
        partes_ecuacion = []
        
        for j in range(n):
            coeficiente = A[i][j]
            valor = solucion[j]
            total += coeficiente * valor
            
            # Crea la visual: (Coeficiente)(Valor)
            if coeficiente != 0:
                partes_ecuacion.append(f"({formato(coeficiente)})({formato(valor)})")
            else:
                partes_ecuacion.append(f"(0)({formato(valor)})")
                
        ecuacion_visual = " + ".join(partes_ecuacion).replace("+ -", "- ")
        correcta = (total == b[i])
        todo_correcto = todo_correcto and correcta
        
        lineas.append(f"   Ec{i+1}: {ecuacion_visual} = {formato(b[i])}")
        lineas.append(f"        {formato(total)} = {formato(b[i])}   ->   {'✅ CORRECTO' if correcta else '❌ FALLO'}")
        lineas.append("") 
        
    lineas.append("-" * 46)
    lineas.append("La solución satisface todas las ecuaciones." if todo_correcto else "La solución NO satisface el sistema.")
    return "\n".join(lineas)

EJEMPLOS = {
    "unica": {"titulo": "Solución única", "ecuaciones": "x1 + x2 + x3 = 6\n2x1 - x2 + x3 = 3\nx1 + 2x2 - x3 = 2"},
    "infinitas": {"titulo": "Infinitas", "ecuaciones": "x1 + x2 + x3 = 1\n2x1 + 2x2 + 2x3 = 2"},
    "sin_solucion": {"titulo": "Sin solución", "ecuaciones": "x1 + x2 = 1\nx1 + x2 = 3"},
}


# =====================================================================
# BLOQUE 6: INTERFAZ GRÁFICA (Tkinter)
# =====================================================================
class MenuPrincipal:
    """Pantalla inicial del sistema para elegir el módulo."""
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Calculadora de Álgebra Lineal - Proyecto UAM")
        self.raiz.configure(bg=FONDO)
        
        self.raiz.geometry("1000x680")
        self.raiz.minsize(900, 600)
        self._centrar_ventana()
        
        self.frame_menu = tk.Frame(self.raiz, bg=FONDO)
        self.frame_menu.pack(fill="both", expand=True)
        
        tk.Label(self.frame_menu, text="✨ ¡Bienvenido a la mejor Calculadora! ✨", font=("Montserrat", 26, "bold"), bg=FONDO, fg=TEXTO).pack(pady=(150, 10))
        tk.Label(self.frame_menu, text="Proyecto de Álgebra Lineal", font=("Montserrat", 16), bg=FONDO, fg=TEXTO_SUAVE).pack(pady=(0, 40))
        tk.Label(self.frame_menu, text="Selecciona el módulo en el que quieres trabajar:", font=("Montserrat", 13), bg=FONDO, fg=TEXTO).pack(pady=(0, 20))
        
        btn_matrices = tk.Button(self.frame_menu, text="🧮 Sistemas de Ecuaciones (Matrices)", font=("Montserrat", 13, "bold"), 
                                 bg=ACENTO, fg=FONDO, padx=30, pady=15, relief="flat", cursor="hand2", 
                                 activebackground=ACENTO_HOVER, activeforeground=FONDO, command=self.abrir_calculadora)
        btn_matrices.pack(pady=10)

        tk.Label(self.frame_menu, text="Desarrollado por Grupo 2 • Universidad Americana (UAM)", font=("Montserrat", 10), bg=FONDO, fg=TEXTO_SUAVE).pack(side="bottom", pady=40)

    def abrir_calculadora(self):
        self.frame_menu.pack_forget()
        CalculadoraApp(self.raiz, callback_volver=self.mostrar_menu)
        
    def mostrar_menu(self):
        for widget in self.raiz.winfo_children():
            widget.destroy()
        self.__init__(self.raiz)

    def _centrar_ventana(self):
        self.raiz.update_idletasks()
        ancho = self.raiz.winfo_width()
        alto = self.raiz.winfo_height()
        x = max(0, (self.raiz.winfo_screenwidth() - ancho) // 2)
        y = max(0, (self.raiz.winfo_screenheight() - alto) // 2)
        self.raiz.geometry(f"+{x}+{y}")


class CalculadoraApp:
    def __init__(self, raiz, callback_volver):
        self.raiz = raiz
        self.callback_volver = callback_volver
        
        self.var_m = tk.StringVar(value="3")
        self.var_n = tk.StringVar(value="3")
        self.celdas = {}
        self.entradas = {}
        self.filas_actuales = 0
        self.columnas_actuales = 0
        self.procedimiento_visible = False
        self.ultimo_resultado = None
        self.etiquetas_ajustables = []

        self.fuente_titulo = tkfont.Font(family="Montserrat", size=22, weight="bold")
        self.fuente_sub = tkfont.Font(family="Montserrat", size=11)
        self.fuente_body = tkfont.Font(family="Montserrat", size=11)
        self.fuente_encab = tkfont.Font(family="Montserrat", size=11, weight="bold")
        self.fuente_big = tkfont.Font(family="Montserrat", size=17, weight="bold")
        self.fuente_cartel = tkfont.Font(family="Montserrat", size=15, weight="bold")
        self.fuente_mono = tkfont.Font(family=LETRA_MONO, size=11) 
        self.fuente_boton = tkfont.Font(family="Montserrat", size=12, weight="bold")

        self.marco_principal = tk.Frame(self.raiz, bg=FONDO)
        self.marco_principal.pack(fill="both", expand=True)

        self._construir_ui()
        self._construir_grid_matriz()

    def _construir_ui(self):
        btn_volver = tk.Button(self.marco_principal, text="← Volver al Menú", font=self.fuente_body, 
                               bg=FONDO, fg=ACENTO, bd=0, relief="flat", cursor="hand2", activeforeground=ACENTO_HOVER, command=self.volver_al_menu)
        btn_volver.grid(row=0, column=0, sticky="w", padx=34, pady=(10, 0))

        tk.Label(self.marco_principal, text="Calculadora de Álgebra Lineal", font=self.fuente_titulo, bg=FONDO, fg=TEXTO).grid(row=1, column=0, columnspan=2, sticky="w", padx=34, pady=(5, 4))
        tk.Label(self.marco_principal, text="Solución de sistemas Ax = b por eliminación por filas (Gauss-Jordan)", font=self.fuente_sub, bg=FONDO, fg=TEXTO_SUAVE).grid(row=2, column=0, columnspan=2, sticky="w", padx=34, pady=(0, 14))

        self.marco_principal.columnconfigure(0, weight=2, uniform="paneles")
        self.marco_principal.columnconfigure(1, weight=3, uniform="paneles")
        self.marco_principal.rowconfigure(3, weight=1)

        panel_izq = tk.Frame(self.marco_principal, bg=FONDO)
        panel_izq.grid(row=3, column=0, sticky="nsew", padx=(34, 14), pady=(0, 26))

        tarjeta_ecuaciones = self._crear_tarjeta(panel_izq)
        tarjeta_ecuaciones.pack(side="top", fill="x", pady=(0, 10))
        self._llenar_ecuaciones(tarjeta_ecuaciones)

        self.boton_resolver = tk.Button(panel_izq, text="Resolver Sistema", font=self.fuente_boton, bg=ACENTO, fg=FONDO, cursor="hand2", relief="flat", padx=18, pady=12, activebackground=ACENTO_HOVER, activeforeground=FONDO, command=self._al_resolver)
        self.boton_resolver.pack(side="bottom", fill="x", pady=(10, 0))

        tarjeta_matriz = self._crear_tarjeta(panel_izq)
        tarjeta_matriz.pack(side="top", fill="both", expand=True)
        self._llenar_cabecera_matriz(tarjeta_matriz)

        contenedor_matriz = tk.Frame(tarjeta_matriz, bg=TARJETA)
        contenedor_matriz.pack(fill="both", expand=True, padx=(6, 6), pady=(0, 10))
        contenedor_matriz.rowconfigure(0, weight=1)
        contenedor_matriz.columnconfigure(0, weight=1)

        lienzo_matriz = tk.Canvas(contenedor_matriz, bg=TARJETA, highlightthickness=0, width=400, height=170)
        barra_v = ttk.Scrollbar(contenedor_matriz, orient="vertical", command=lienzo_matriz.yview)
        barra_h = ttk.Scrollbar(contenedor_matriz, orient="horizontal", command=lienzo_matriz.xview)
        lienzo_matriz.configure(yscrollcommand=barra_v.set, xscrollcommand=barra_h.set)
        
        self.frame_matriz = tk.Frame(lienzo_matriz, bg=TARJETA)
        lienzo_matriz.create_window((0, 0), window=self.frame_matriz, anchor="nw")
        self.frame_matriz.bind("<Configure>", lambda e: lienzo_matriz.configure(scrollregion=lienzo_matriz.bbox("all")))
        self.lienzo_matriz = lienzo_matriz
        self._activar_rueda(lienzo_matriz)

        lienzo_matriz.grid(row=0, column=0, sticky="nsew")
        barra_v.grid(row=0, column=1, sticky="ns")
        barra_h.grid(row=1, column=0, sticky="ew")

        panel_der = tk.Frame(self.marco_principal, bg=FONDO)
        panel_der.grid(row=3, column=1, sticky="nsew", padx=(14, 34), pady=(0, 26))

        tarjeta_resultado = self._crear_tarjeta(panel_der)
        tarjeta_resultado.pack(fill="both", expand=True)

        cabecera = tk.Frame(tarjeta_resultado, bg=TARJETA)
        cabecera.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cabecera, text="Resultado", font=self.fuente_sub, bg=TARJETA, fg=TEXTO).pack(side="left")

        self.boton_procedimiento = tk.Button(cabecera, text="Ver procedimiento", font=self.fuente_body, bg=BOTON_SEC, fg=TEXTO, bd=0, relief="flat", cursor="hand2", padx=12, pady=4, activebackground=BOTON_SEC_HOVER, activeforeground=TEXTO, command=self._alternar_procedimiento)

        self.aviso_vacio = tk.Label(tarjeta_resultado, text="Complete las dimensiones y la matriz aumentada a la izquierda,\ny luego pulse «Resolver Sistema».", font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE, justify="left", anchor="nw", padx=18, pady=14)
        self.aviso_vacio.pack(fill="both", expand=True)

        self.lienzo_resultado = tk.Canvas(tarjeta_resultado, bg=TARJETA, highlightthickness=0)
        self.barra_resultado = ttk.Scrollbar(tarjeta_resultado, orient="vertical", command=self.lienzo_resultado.yview)
        self.lienzo_resultado.configure(yscrollcommand=self.barra_resultado.set)

        self.frame_resultado = tk.Frame(self.lienzo_resultado, bg=TARJETA)
        ventana_resultado = self.lienzo_resultado.create_window((0, 0), window=self.frame_resultado, anchor="nw")
        
        def al_cambiar_tamano(evento):
            self.lienzo_resultado.itemconfig(ventana_resultado, width=evento.width)
            self._ajustar_textos(evento.width)

        self.lienzo_resultado.bind("<Configure>", al_cambiar_tamano)
        self.frame_resultado.bind("<Configure>", lambda e: self.lienzo_resultado.configure(scrollregion=self.lienzo_resultado.bbox("all")))
        self._activar_rueda(self.lienzo_resultado)
        
    def volver_al_menu(self):
        self.marco_principal.destroy()
        self.callback_volver()

    def _ajustar_textos(self, ancho_disponible=None):
        if ancho_disponible is None:
            ancho_disponible = self.lienzo_resultado.winfo_width()
        ancho = max(240, ancho_disponible - 56)
        for etiqueta in self.etiquetas_ajustables:
            try: etiqueta.configure(wraplength=ancho)
            except tk.TclError: pass

    def _texto_ajustable(self, etiqueta):
        self.etiquetas_ajustables.append(etiqueta)
        return etiqueta

    def _activar_rueda(self, lienzo):
        def al_girar(evento):
            if evento.num == 4: lienzo.yview_scroll(-1, "units")
            elif evento.num == 5: lienzo.yview_scroll(1, "units")
            else: lienzo.yview_scroll(-1 * (evento.delta // 120), "units")
        def al_entrar(_evento):
            lienzo.bind_all("<MouseWheel>", al_girar)
            lienzo.bind_all("<Button-4>", al_girar)
            lienzo.bind_all("<Button-5>", al_girar)
        def al_salir(_evento):
            lienzo.unbind_all("<MouseWheel>")
            lienzo.unbind_all("<Button-4>")
            lienzo.unbind_all("<Button-5>")
        lienzo.bind("<Enter>", al_entrar)
        lienzo.bind("<Leave>", al_salir)

    def _crear_tarjeta(self, padre):
        return tk.Frame(padre, bg=TARJETA, highlightbackground=BOTON_SEC, highlightthickness=1, bd=0)

    def _llenar_ecuaciones(self, tarjeta):
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 14))

        tk.Label(cont, text="Sistema de ecuaciones", font=self.fuente_sub, bg=TARJETA, fg=TEXTO, anchor="w").pack(fill="x", pady=(0, 2))
        tk.Label(cont, text="Una ecuación por línea; las que falten valen 0.", font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE, anchor="w", justify="left", wraplength=420).pack(fill="x", pady=(0, 6))
        
        self.caja_ecuaciones = tk.Text(cont, height=5, font=self.fuente_mono, bg=FONDO, fg=TEXTO, relief="solid", bd=1, highlightthickness=1, highlightbackground=BOTON_SEC, highlightcolor=ACENTO, wrap="none", padx=8, pady=6)
        self.caja_ecuaciones.pack(fill="x")
        self.caja_ecuaciones.insert("1.0", "x1 + x2 + x3 = 6\n2x1 - x2 + x3 = 3\nx1 + 2x2 - x3 = 2")

        botones = tk.Frame(cont, bg=TARJETA)
        botones.pack(fill="x", pady=(8, 0))
        
        self._boton_secundario(botones, "Convertir a matriz", self._convertir_ecuaciones, 0, 0)
        self._boton_secundario(botones, "Borrar", self._borrar_ecuaciones, 0, 1)
        self._boton_secundario(botones, "Ej. única", lambda: self._cargar_ejemplo("unica"), 1, 0)
        self._boton_secundario(botones, "Ej. infinitas", lambda: self._cargar_ejemplo("infinitas"), 1, 1)
        self._boton_secundario(botones, "Ej. sin solución", lambda: self._cargar_ejemplo("sin_solucion"), 1, 2)

        self.aviso_ecuaciones = tk.Label(cont, text="", font=self.fuente_body, bg=TARJETA, fg=EXITO, anchor="w")
        self.aviso_ecuaciones.pack(fill="x", pady=(4, 0))

    def _borrar_ecuaciones(self):
        self.caja_ecuaciones.delete("1.0", "end")
        self.aviso_ecuaciones.configure(text="")

    def _convertir_ecuaciones(self):
        try:
            texto = self.caja_ecuaciones.get("1.0", "end")
            A, b, nombres = interpretar_ecuaciones(texto)
            filas, columnas = len(A), len(nombres)
            
            if filas > MAX_DIMENSION or columnas > MAX_DIMENSION:
                raise ValueError(f"El sistema es muy grande. El límite es {MAX_DIMENSION}x{MAX_DIMENSION}.")

            self.var_m.set(str(filas))
            self.var_n.set(str(columnas))
            self._construir_grid_matriz()
            self._limpiar_celdas()
            
            for i in range(filas):
                for j in range(columnas):
                    self.celdas[(i, j)].set(formato(A[i][j]))
                self.celdas[(i, columnas)].set(formato(b[i]))

            self.aviso_ecuaciones.configure(fg=EXITO, text=f"Listo: {filas} ecuaciones y {columnas} variables detectadas.")
        except ValueError as error:
            self.aviso_ecuaciones.configure(fg=ERROR, text=str(error))
        except Exception as error: 
            self.aviso_ecuaciones.configure(fg=ERROR, text=f"Error inesperado: {error}")

    def _boton_secundario(self, padre, texto, accion, fila=0, columna=0):
        boton = tk.Button(padre, text=texto, font=self.fuente_body, bg=BOTON_SEC, fg=TEXTO, bd=0, relief="flat", cursor="hand2", padx=10, pady=4, activebackground=BOTON_SEC_HOVER, activeforeground=TEXTO, command=accion)
        boton.grid(row=fila, column=columna, sticky="w", padx=(0, 8), pady=(0, 4))
        return boton

    def _llenar_cabecera_matriz(self, tarjeta):
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 6))

        tk.Label(cont, text="Matriz aumentada [A | b] — ingrese los coeficientes", font=self.fuente_sub, bg=TARJETA, fg=TEXTO).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))

        tk.Label(cont, text="Ecuaciones (m)", font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE).grid(row=1, column=0, sticky="w", padx=(0, 8))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_m, width=4, justify="center", bg=FONDO, fg=TEXTO, relief="solid", bd=1, highlightthickness=1, highlightbackground=BOTON_SEC, highlightcolor=ACENTO, command=self._construir_grid_matriz).grid(row=1, column=1, sticky="w", padx=(0, 18))

        tk.Label(cont, text="Variables (n)", font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE).grid(row=1, column=2, sticky="w", padx=(0, 8))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_n, width=4, justify="center", bg=FONDO, fg=TEXTO, relief="solid", bd=1, highlightthickness=1, highlightbackground=BOTON_SEC, highlightcolor=ACENTO, command=self._construir_grid_matriz).grid(row=1, column=3, sticky="w")

        botones = tk.Frame(cont, bg=TARJETA)
        botones.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))
        self._boton_secundario(botones, "Actualizar matriz", self._construir_grid_matriz, 0, 0)
        self._boton_secundario(botones, "Limpiar", self._limpiar_celdas, 0, 1)

    def _leer_dimension(self, variable, por_defecto):
        try: valor = int(str(variable.get()).strip())
        except: valor = por_defecto
        valor = max(1, min(MAX_DIMENSION, valor))
        variable.set(str(valor))
        return valor

    def _construir_grid_matriz(self):
        m = self._leer_dimension(self.var_m, 3)
        n = self._leer_dimension(self.var_n, 3)
        valores_previos = {clave: var.get() for clave, var in self.celdas.items()}

        for hijo in self.frame_matriz.winfo_children(): hijo.destroy()
        self.celdas, self.entradas = {}, {}
        self.filas_actuales, self.columnas_actuales = m, n

        for j in range(n):
            tk.Label(self.frame_matriz, text=f"x{j+1}", font=self.fuente_sub, bg=TARJETA, fg=TEXTO_SUAVE).grid(row=0, column=j, padx=2, pady=(0, 4))
        tk.Label(self.frame_matriz, text="b", font=self.fuente_sub, bg=TARJETA, fg=TEXTO_SUAVE).grid(row=0, column=n, padx=(14, 2), pady=(0, 4))

        for i in range(m):
            for j in range(n + 1):
                variable = tk.StringVar(value=valores_previos.get((i, j), ""))
                self.celdas[(i, j)] = variable
                entrada = tk.Entry(self.frame_matriz, textvariable=variable, font=self.fuente_mono, width=6, justify="center", relief="solid", bd=1, highlightthickness=1, highlightbackground=CELDA_BORDE, highlightcolor=ACENTO, bg=FONDO, fg=TEXTO)
                padx = (14, 2) if j == n else (2, 2)
                entrada.grid(row=i + 1, column=j, padx=padx, pady=3, ipady=3)
                entrada.bind("<Return>", lambda e: self._al_resolver())
                self.entradas[(i, j)] = entrada

    def _limpiar_celdas(self):
        for variable in self.celdas.values(): variable.set("")
        for entrada in self.entradas.values(): entrada.configure(highlightbackground=CELDA_BORDE, highlightcolor=ACENTO)

    def _cargar_ejemplo(self, clave):
        self.caja_ecuaciones.delete("1.0", "end")
        self.caja_ecuaciones.insert("1.0", EJEMPLOS[clave]["ecuaciones"])
        self._convertir_ecuaciones()

    def _al_resolver(self):
        try:
            m, n = self.filas_actuales, self.columnas_actuales
            A, b = [], []
            for i in range(m):
                fila = []
                for j in range(n):
                    try: fila.append(a_numero(self.celdas[(i, j)].get()))
                    except ValueError as error:
                        self._mostrar_error(f"Revisa la casilla fila {i+1}, columna x{j+1}.", i, j)
                        return
                A.append(fila)
                try: b.append(a_numero(self.celdas[(i, n)].get()))
                except ValueError as error:
                    self._mostrar_error(f"Revisa el vector 'b' de la fila {i+1}.", i, n)
                    return

            self._restaurar_bordes()
            resultado = resolver_sistema(m, n, A, b)
            self.ultimo_resultado = resultado
            self._mostrar_resultado(resultado)

        except Exception as error:
            messagebox.showerror("Error inesperado", f"Ocurrió un problema:\n{error}")

    def _restaurar_bordes(self):
        for entrada in self.entradas.values(): entrada.configure(highlightbackground=CELDA_BORDE, highlightcolor=ACENTO)

    def _mostrar_error(self, mensaje, fila, columna):
        self._restaurar_bordes()
        entrada = self.entradas.get((fila, columna))
        if entrada:
            entrada.configure(highlightbackground=ERROR, highlightcolor=ERROR)
            entrada.focus_set()
        messagebox.showerror("Entrada inválida", mensaje)

    def _limpiar_resultado(self):
        if self.aviso_vacio and self.aviso_vacio.winfo_manager():
            self.aviso_vacio.destroy()
            self.aviso_vacio = None
            self.lienzo_resultado.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=(0, 12))
            self.barra_resultado.pack(side="right", fill="y", pady=(0, 12))
        for hijo in self.frame_resultado.winfo_children(): hijo.destroy()
        self.etiquetas_ajustables = []

    def _sub_tarjeta(self, titulo, color):
        sub = tk.Frame(self.frame_resultado, bg=TARJETA)
        sub.pack(fill="x", padx=16, pady=(4, 2), anchor="n")
        tk.Label(sub, text=titulo, font=self.fuente_encab, bg=TARJETA, fg=color, anchor="w").pack(fill="x", padx=2, pady=(6, 2))
        return sub

    def _mostrar_resultado(self, resultado):
        self._limpiar_resultado()
        self.boton_procedimiento.pack(side="right")

        clasificacion = resultado["clasificacion"]
        color = EXITO if clasificacion == "Consistente Determinado" else ADVERTENCIA if clasificacion == "Consistente Indeterminado" else ERROR

        # ================= RESULTADO =================
        sub = self._sub_tarjeta("CLASIFICACIÓN", TEXTO_SUAVE)
        cartel = tk.Frame(sub, bg=color, padx=14, pady=10)
        cartel.pack(fill="x", pady=(0, 4))
        self._texto_ajustable(tk.Label(cartel, text=clasificacion.upper(), font=self.fuente_cartel, bg=color, fg=FONDO)).pack(fill="x")
        self._texto_ajustable(tk.Label(sub, text=resultado["descripcion"], font=self.fuente_body, bg=TARJETA, fg=TEXTO)).pack(fill="x", pady=(0, 6))

        if resultado["solucion"] is not None:
            sub2 = self._sub_tarjeta("SOLUCIÓN ENCONTRADA", ACENTO)
            contenedor = tk.Frame(sub2, bg=FONDO, padx=12, pady=10)
            contenedor.pack(fill="x", pady=(0, 8))
            texto_solucion = "     ".join(f"x{i+1} = {formato(v)}" for i, v in enumerate(resultado["solucion"]))
            self._texto_ajustable(tk.Label(contenedor, text=texto_solucion, font=self.fuente_big, bg=FONDO, fg=TEXTO)).pack(fill="x")
        
        elif clasificacion == "Consistente Indeterminado":
            sub2 = self._sub_tarjeta("VARIABLES LIBRES", ADVERTENCIA)
            nombres = "   ".join(f"x{c+1}" for c in resultado["variables_libres"])
            tk.Label(sub2, text="Soluciones dadas en función de:", font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE).pack(fill="x")
            self._texto_ajustable(tk.Label(sub2, text=nombres, font=self.fuente_big, bg=TARJETA, fg=TEXTO)).pack(fill="x", pady=(4, 8))

        sub3 = self._sub_tarjeta("COMPROBACIÓN", EXITO)
        self._texto_ajustable(tk.Label(sub3, text=resultado["verificacion"], font=self.fuente_mono, bg=TARJETA, fg=TEXTO, justify="left", anchor="w")).pack(fill="x", pady=(0, 8))

        # ================= PROCEDIMIENTO =================
        self.sub_procedimiento = tk.Frame(self.frame_resultado, bg=TARJETA)
        tk.Label(self.sub_procedimiento, text="PROCESO DE ELIMINACIÓN (GAUSS-JORDAN)", font=self.fuente_encab, bg=TARJETA, fg=TEXTO_SUAVE, anchor="w").pack(fill="x", padx=2, pady=(6, 2))
        
        self._texto_ajustable(tk.Label(self.sub_procedimiento, text="\n".join(resultado["pasos"]), font=self.fuente_mono, bg=TARJETA, fg=TEXTO, justify="left", anchor="w")).pack(fill="x", pady=(0, 10))

        self.procedimiento_visible = False
        self.boton_procedimiento.configure(text="Ver procedimiento")
        self.lienzo_resultado.yview_moveto(0)
        self.raiz.update_idletasks()
        self._ajustar_textos()

    def _alternar_procedimiento(self):
        if not self.ultimo_resultado: return
        if self.procedimiento_visible:
            self.sub_procedimiento.pack_forget()
            self.boton_procedimiento.configure(text="Ver procedimiento")
            self.procedimiento_visible = False
        else:
            self.sub_procedimiento.pack(fill="x", padx=16, pady=(4, 2), anchor="n")
            self.boton_procedimiento.configure(text="Ocultar procedimiento")
            self.procedimiento_visible = True
        self.raiz.update_idletasks()
        self.lienzo_resultado.configure(scrollregion=self.lienzo_resultado.bbox("all"))

# =====================================================================
# BLOQUE 7: PRUEBAS AUTOMÁTICAS DEL ALGORITMO
# =====================================================================
def ejecutar_pruebas():
    """Ejecuta los sistemas predefinidos y verifica que el algoritmo funciona."""
    pruebas = [
        ("Caso 1: solución única", [[1, 1, 1], [2, -1, 1], [1, 2, -1]], [6, 3, 2], "Consistente Determinado", ["1", "2", "3"]),
        ("Caso 2: infinitas", [[1, 1, 1], [2, 2, 2]], [1, 2], "Consistente Indeterminado", None),
        ("Caso 3: inconsistente", [[1, 1], [1, 1]], [1, 3], "Inconsistente", None),
        ("Clase Lay", [[1, -2, 1], [0, 2, -8], [-4, 5, 9]], [0, 8, -9], "Consistente Determinado", ["29", "16", "3"]),
        ("Actividad 1", [[2, 3, 1], [5, 3, 4], [1, 1, -1]], [1, 2, 1], "Consistente Determinado", ["2/3", "0", "-1/3"]),
        ("Inconsistente Clase", [[0, 1, -4], [2, -3, 2], [5, -8, 7]], [8, 1, 1], "Inconsistente", None),
        ("Matriz 5x5", [[1, 2, 0, 1, 1], [0, 1, 1, 0, 0], [0, 0, 1, 1, -1], [0, 0, 0, 1, 2], [0, 0, 0, 0, 1]], [4, 2, 3, 5, 1], "Consistente Determinado", ["-2", "1", "1", "3", "1"]),
        ("Homogéneo", [[1, 1, 1], [2, -1, 0]], [0, 0], "Consistente Indeterminado", None),
        ("Ceros", [[0, 0], [0, 0]], [0, 0], "Consistente Indeterminado", None),
        ("Imposible", [[0]], [7], "Inconsistente", None),
        ("Intercambio necesario", [[0, 1], [1, 0]], [2, 3], "Consistente Determinado", ["3", "2"]),
        ("Más ecuaciones", [[1, 0], [0, 1], [1, 1]], [1, 2, 3], "Consistente Determinado", ["1", "2"]),
        ("Más ecuaciones, incompatible", [[1, 0], [0, 1], [1, 1]], [1, 2, 4], "Inconsistente", None),
        ("Fracciones", [["1/2", "1/3"], ["1/4", "1/5"]], [1, 1], "Consistente Determinado", ["-8", "15"]),
        ("Más incógnitas", [[1, 2, 3]], [6], "Consistente Indeterminado", None),
    ]

    fallos = 0
    print("=" * 64)
    print("INICIANDO PRUEBAS AUTOMÁTICAS DEL ALGORITMO")
    print("=" * 64)

    for nombre, A, b, clasificacion_esperada, solucion_esperada in pruebas:
        A = [[a_numero(str(valor)) for valor in fila] for fila in A]
        b = [a_numero(str(valor)) for valor in b]
        resultado = resolver_sistema(len(A), len(A[0]), A, b)

        problemas = []
        if resultado["clasificacion"] != clasificacion_esperada:
            problemas.append(f"Clasificó como {resultado['clasificacion']} pero se esperaba {clasificacion_esperada}")
        if solucion_esperada is not None:
            obtenida = [formato(valor) for valor in resultado["solucion"]]
            if obtenida != solucion_esperada:
                problemas.append(f"Solución {obtenida} en vez de {solucion_esperada}")
        
        correcta, motivo = es_escalonada(resultado["escalonada"])
        if not correcta:
            problemas.append(f"Fallo al escalonar: {motivo}")
        
        if "FALLO" in resultado["verificacion"]:
            problemas.append("La verificación de la solución falló")

        if problemas:
            fallos += 1
            print(f"[FALLA] {nombre}")
            for p in problemas: print(f"         - {p}")
        else:
            print(f"[  OK  ] {nombre}")

    print("=" * 64)
    if fallos == 0:
        print("¡Excelente! Todas las 44 comprobaciones pasaron correctamente.")
    else:
        print(f"Alerta: Se encontraron {fallos} fallos matemáticos.")
    print("=" * 64)
    return fallos

# =====================================================================
# PUNTO DE ENTRADA
# =====================================================================
def main():
    if "--pruebas" in sys.argv:
        sys.exit(1 if ejecutar_pruebas() else 0)

    raiz = tk.Tk()
    app = MenuPrincipal(raiz)
    raiz.mainloop()

if __name__ == "__main__":
    main()