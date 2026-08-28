# -*- coding: utf-8 -*-
"""
=====================================================================
 PROGRAMA 1 - GRUPO 2
 Calculadora de Álgebra Lineal
 Solución de Sistemas de Ecuaciones Lineales por Eliminación por Filas
 Aplicación de escritorio (Tkinter) - Python estándar
=====================================================================
 UNIVERSIDAD AMERICANA
 Facultad de Ingeniería y Arquitectura (FIA)
 Asignatura: Álgebra Lineal (MTM0120)
 Primer Corte Evaluativo

 Descripción general:
   - El programa solicita el número de ecuaciones (m) y de variables (n).
   - Pide los coeficientes de la matriz A y los términos independientes b,
     formando la matriz aumentada [ A | b ].
   - Aplica eliminación por filas (Gauss) con pivoteo parcial, mostrando la
     matriz en cada paso representativo.
   - Clasifica el sistema (Consistente Determinado / Consistente
     Indeterminado / Inconsistente).
   - Halla las variables (si aplica) mediante sustitución regresiva.
   - Comprueba la solución sustituyendo los valores en el sistema original.

 Restricción cumplida:
   - Solo se usa Python estándar (tkinter, math, fractions). NO se usan
     NumPy, SciPy ni funciones integradas de álgebra lineal de math.
=====================================================================
"""

import math          # Solo se usan math.isclose (comparar flotantes) y abs
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

# =====================================================================
# CONSTANTES DE DISEÑO (Estética iOS / Apple)
# =====================================================================
FONDO         = "#F5F5F7"   # Fondo general gris claro Apple
TARJETA       = "#FFFFFF"   # Superficie de tarjetas
TEXTO         = "#1D1D1F"   # Texto principal
TEXTO_SUAVE   = "#6E6E73"   # Texto secundario
ACENTO        = "#0071E3"   # Azul Apple (CTA)
ACENTO_CLARO  = "#E8F0FE"   # Azul muy claro (hover / resaltado)
BORDE         = "#E5E5E5"   # Borde sutil
EXITO         = "#059669"   # Verde éxito
ADVERTENCIA   = "#B45309"   # Ámbar (indeterminado)
ERROR         = "#DC2626"   # Rojo (inconsistente / errores)
CELDA_BORDE   = "#D1D1D6"   # Borde de celdas de la matriz
LETRA_MONO    = "Consolas"  # Fuente monoespaciada para la matriz

TOL = 1e-9     # Tolerancia para considerar un número como cero


# =====================================================================
# BLOQUE: NÚCLEO MATEMÁTICO
# Eliminación por filas, clasificación, sustitución regresiva y
# verificación. Funciones puras de Python estándar, reutilizables
# también desde consola.
# =====================================================================
def casi_cero(valor):
    """Devuelve True si un número es aproximadamente cero."""
    return abs(valor) < TOL


def a_numero(texto):
    """Convierte un texto en número. Acepta enteros, decimales y
    fracciones (ej. '3/4'). Lanza ValueError si no es válido."""
    texto = texto.strip()
    if "/" in texto:
        # Convertir fracción usando numerador / denominador
        num, den = texto.split("/", 1)
        return float(int(num)) / float(int(den))
    return float(texto)


def resolver_sistema(m, n, A, b):
    """
    Resuelve el sistema A x = b mediante eliminación por filas (Gauss)
    con pivoteo parcial.

    Parámetros:
        m (int): número de ecuaciones.
        n (int): número de variables.
        A (list): matriz de coeficientes (m x n).
        b (list): vector de términos independientes (tamaño m).

    Retorna un diccionario con:
        pasos          : lista de strings con cada paso representativo.
        escalonada     : lista de listas con la forma escalonada final.
        clasificacion  : "Consistente Determinado" | "Consistente
                         Indeterminado" | "Inconsistente".
        descripcion    : texto explicativo de la clasificación.
        variables_libres : lista de índices de variables libres (0-based),
                           vacía si no las hay.
        solucion       : lista de soluciones (None si no aplica).
        verificacion   : texto con la verificación automática.
    """
    pasos = []
    # Construir la matriz aumentada copiando A y añadiendo la columna b
    aug = [list(A[i]) + [b[i]] for i in range(m)]

    pasos.append("Matriz aumentada inicial [A|b]:")
    pasos += _formato_matriz(aug)

    # ---- Fase de escalonamiento (ceros debajo del pivote) ----
    fila_piv = 0
    col_piv = 0
    pivote_columna = []   # (fila, columna) de cada pivote

    while fila_piv < m and col_piv < n:
        # Buscar la fila con mayor valor absoluto en la columna (pivoteo
        # parcial) para mejorar la estabilidad numérica.
        fila_max = fila_piv
        for f in range(fila_piv, m):
            if abs(aug[f][col_piv]) > abs(aug[fila_max][col_piv]):
                fila_max = f

        # Si toda la columna es cero (columna de pivote), es una variable
        # libre: avanzamos a la siguiente columna sin hacer pivote.
        if casi_cero(aug[fila_max][col_piv]):
            col_piv += 1
            continue

        # Intercambiar filas si es necesario
        if fila_max != fila_piv:
            aug[fila_piv], aug[fila_max] = aug[fila_max], aug[fila_piv]
            pasos.append(
                f"Intercambio de filas: F{fila_piv+1} <-> F{fila_max+1}")
            pasos += _formato_matriz(aug)

        # Normalizar el pivote a 1
        pivote = aug[fila_piv][col_piv]
        if not casi_cero(pivote - 1.0):
            aug[fila_piv] = [x / pivote for x in aug[fila_piv]]
            pasos.append(
                f"Normalizar pivote de F{fila_piv+1}: dividir toda la fila "
                f"entre {_fmt(pivote)}")
            pasos += _formato_matriz(aug)

        # Generar ceros debajo del pivote
        for f in range(fila_piv + 1, m):
            factor = aug[f][col_piv]
            if not casi_cero(factor):
                aug[f] = [aug[f][c] - factor * aug[fila_piv][c]
                          for c in range(n + 1)]
                pasos.append(
                    f"Anular F{f+1}: F{f+1} = F{f+1} - "
                    f"({_fmt(factor)}) * F{fila_piv+1}")
                pasos += _formato_matriz(aug)

        pivote_columna.append((fila_piv, col_piv))
        fila_piv += 1
        col_piv += 1

    pasos.append("Forma escalonada final:")
    pasos += _formato_matriz(aug)

    # ---- Clasificación del sistema ----
    # Inconsistente: existe una fila [0 ... 0 | k] con k != 0
    inconsistente = False
    for f in aug:
        if all(casi_cero(val) for val in f[:-1]) and not casi_cero(f[-1]):
            inconsistente = True
            break

    variables_libres = []
    if inconsistente:
        clasificacion = "Inconsistente"
        descripcion = ("Sistema sin solución. Existe una fila de la forma "
                       "[0 0 ... 0 | k] con k diferente de 0.")
        solucion = None
    else:
        num_pivotes = len(pivote_columna)
        # Columnas que no tienen pivote => variables libres
        con_pivote = set(c for _, c in pivote_columna)
        variables_libres = [c for c in range(n) if c not in con_pivote]

        if num_pivotes == n:
            clasificacion = "Consistente Determinado"
            descripcion = ("Sistema con solución única (todos los pivotes "
                           "están en columnas de variables).")
            solucion = _sustitucion_regresiva(aug, n, pivote_columna)
        else:
            clasificacion = "Consistente Indeterminado"
            descripcion = ("Sistema con infinitas soluciones. Existen "
                           "variables libres.")
            solucion = None

    # ---- Verificación automática (sólo si hay solución única) ----
    verificacion = ""
    if solucion is not None:
        verificacion = _verificar(m, n, A, b, solucion)
    elif inconsistente:
        verificacion = ("No se puede verificar: el sistema no tiene "
                        "solución (inconsistente).")
    else:
        verificacion = ("El sistema tiene infinitas soluciones; la "
                        "comprobación se expresa en términos de las "
                        "variables libres.")

    return {
        "pasos": pasos,
        "escalonada": aug,
        "clasificacion": clasificacion,
        "descripcion": descripcion,
        "variables_libres": variables_libres,
        "solucion": solucion,
        "verificacion": verificacion,
    }


def _formato_matriz(matriz):
    """Convierte una matriz en una lista de strings alineados."""
    if not matriz:
        return []
    # Determinar ancho por columna para alinear
    cols = len(matriz[0])
    anchos = [0] * cols
    for fila in matriz:
        for c, val in enumerate(fila):
            anchos[c] = max(anchos[c], len(_fmt(val)))
    lineas = []
    for fila in matriz:
        celdas = [_fmt(val).rjust(anchos[c]) for c, val in enumerate(fila)]
        # Separar la última columna (b) con un "|"
        izquierda = "  ".join(celdas[:-1])
        linea = f"  [{izquierda}  |  {celdas[-1]}]"
        lineas.append(linea)
    return lineas


def _fmt(valor):
    """Da formato numérico compacto para mostrar (evita -0 y notación
    científica)."""
    if casi_cero(valor):
        return "0"
    # Redondear a 6 decimales para una salida limpia
    redondeado = round(valor, 6)
    if redondeado == int(redondeado):
        return str(int(redondeado))
    return f"{redondeado:g}"


def _sustitucion_regresiva(aug, n, pivote_columna):
    """Sustitución regresiva sobre la forma escalonada (ceros debajo del
    pivote) para obtener la solución única."""
    x = [0.0] * n
    # Recorrer los pivotes de abajo hacia arriba
    for fi, ci in reversed(pivote_columna):
        suma = aug[fi][-1]
        for c in range(ci + 1, n):
            suma -= aug[fi][c] * x[c]
        x[ci] = suma / aug[fi][ci]
    return x


def _verificar(m, n, A, b, solucion):
    """Comprueba la solución sustituyendo en el sistema original."""
    lineas = [f"Verificación del sistema original A·x = b con "
              f"x = {[round(v, 6) for v in solucion]}:",
              "-" * 40]
    ok_total = True
    for i in range(m):
        # Reconstruir A·x sin librerías (suma de productos)
        resultado = sum(A[i][j] * solucion[j] for j in range(n))
        ok = casi_cero(resultado - b[i])
        if not ok:
            ok_total = False
        signo = "OK" if ok else "FALLO"
        lineas.append(
            f"  Ec{i+1}: {_fmt(resultado)} == {_fmt(b[i])}   ->   {signo}")
    lineas.append("-" * 40)
    if ok_total:
        lineas.append("La solución satisface todas las ecuaciones. [OK]")
    else:
        lineas.append("La solución NO satisface el sistema.")
    return "\n".join(lineas)


# =====================================================================
# BLOQUE: INTERFAZ GRÁFICA DE ESCRITORIO (Tkinter)
# Estética iOS / Apple: fondo claro, tarjetas blancas redondeadas,
# botón azul de acción principal y tipografía limpia.
# =====================================================================
class CalculadoraApp:
    """Ventana principal de la calculadora."""

    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Calculadora de Álgebra Lineal · Grupo 2")
        self.raiz.configure(bg=FONDO)
        self.raiz.geometry("1200x700")
        self.raiz.minsize(1000, 620)

        # Variables de control de dimensiones y celdas
        self.var_m = tk.IntVar(value=3)     # número de ecuaciones
        self.var_n = tk.IntVar(value=3)     # número de variables
        self.celdas = []                     # grid de StringVar (A y b)

        # Fuentes
        self.fuente_titulo = tkfont.Font(family="Segoe UI", size=22,
                                         weight="bold")
        self.fuente_sub = tkfont.Font(family="Segoe UI", size=11)
        self.fuente_body = tkfont.Font(family="Segoe UI", size=11)
        self.fuente_encab = tkfont.Font(family="Segoe UI", size=11,
                                        weight="bold")
        self.fuente_big = tkfont.Font(family="Segoe UI", size=17,
                                      weight="bold")
        self.fuente_mono = tkfont.Font(family=LETRA_MONO, size=11)
        self.fuente_boton = tkfont.Font(family="Segoe UI", size=12,
                                        weight="bold")

        self._construir_ui()
        self._construir_grid_matriz()
        self._centrar_ventana()

    # ------------------------------------------------------------------
    # Construcción de la interfaz (dos paneles: izquierda/derecha)
    # ------------------------------------------------------------------
    def _construir_ui(self):
        """Crea la ventana con dos paneles: a la izquierda se escribe el
        ejercicio (dimensiones y matriz aumentada) y a la derecha se
        muestran los resultados. No hay scroll de página: cada panel
        desplaza su propio contenido interno."""

        # ---- Contenedor raíz de la ventana ----
        fondo = tk.Frame(self.raiz, bg=FONDO)
        fondo.pack(fill="both", expand=True)
        fondo.columnconfigure(0, weight=3)   # panel izquierdo
        fondo.columnconfigure(1, weight=4)   # panel derecho
        fondo.rowconfigure(1, weight=1)

        # ---- Encabezado (ancho completo) ----
        tk.Label(fondo, text="Calculadora de Álgebra Lineal",
                 font=self.fuente_titulo, bg=FONDO, fg=TEXTO, anchor="w"
                 ).grid(row=0, column=0, columnspan=2, sticky="w",
                        padx=34, pady=(26, 4))
        tk.Label(fondo,
                 text="Solución de sistemas Ax = b por eliminación por "
                      "filas (Gauss)",
                 font=self.fuente_sub, bg=FONDO, fg=TEXTO_SUAVE, anchor="w"
                 ).grid(row=1, column=0, columnspan=2, sticky="w",
                        padx=34, pady=(0, 14))

        # ================= PANEL IZQUIERDO: EJERCICIO =================
        panel_izq = tk.Frame(fondo, bg=FONDO)
        panel_izq.grid(row=2, column=0, sticky="nsew", padx=(34, 14),
                       pady=(0, 26))

        # Tarjeta: Dimensiones del sistema
        card1 = self._crear_tarjeta(panel_izq)
        card1.pack(fill="x", pady=(0, 10))
        self._llenar_configuracion(card1)

        # Tarjeta: Matriz aumentada (con scroll interno propio)
        card2 = self._crear_tarjeta(panel_izq)
        card2.pack(fill="both", expand=True)
        self._llenar_cabecera_matriz(card2)

        # Área de la matriz dentro de un lienzo desplazable
        lienzo_matriz = tk.Canvas(card2, bg=TARJETA, highlightthickness=0)
        barra_matriz = ttk.Scrollbar(card2, orient="vertical",
                                     command=lienzo_matriz.yview)
        lienzo_matriz.configure(yscrollcommand=barra_matriz.set)
        self.frame_matriz = tk.Frame(lienzo_matriz, bg=TARJETA)

        ventana_matriz = lienzo_matriz.create_window(
            (0, 0), window=self.frame_matriz, anchor="nw")
        # Ajustar ancho interno del lienzo y su región de desplazamiento
        lienzo_matriz.bind(
            "<Configure>",
            lambda e: lienzo_matriz.itemconfig(ventana_matriz, width=e.width))
        self.frame_matriz.bind(
            "<Configure>",
            lambda e: lienzo_matriz.configure(
                scrollregion=lienzo_matriz.bbox("all")))
        self.lienzo_matriz = lienzo_matriz

        lienzo_matriz.pack(side="left", fill="both", expand=True,
                           padx=(6, 0), pady=(0, 12))
        barra_matriz.pack(side="right", fill="y", pady=(0, 12))

        # Botón principal dentro del panel izquierdo
        self.boton_resolver = tk.Button(
            panel_izq, text="Resolver Sistema", font=self.fuente_boton,
            bg=ACENTO, fg="#FFFFFF", activebackground="#0062C4",
            activeforeground="#FFFFFF", bd=0, cursor="hand2", relief="flat",
            padx=18, pady=12, command=self._al_resolver)
        self.boton_resolver.pack(fill="x", pady=(10, 0))

        # ================= PANEL DERECHO: RESULTADO =================
        panel_der = tk.Frame(fondo, bg=FONDO)
        panel_der.grid(row=2, column=1, sticky="nsew", padx=(14, 34),
                       pady=(0, 26))

        card3 = self._crear_tarjeta(panel_der)
        card3.pack(fill="both", expand=True)

        # Cabecera del panel de resultados
        cabecera = tk.Frame(card3, bg=TARJETA)
        cabecera.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cabecera, text="Resultado", font=self.fuente_sub,
                 bg=TARJETA, fg=TEXTO, anchor="w").pack(side="left")
        self.cabecera_resultado = cabecera

        # Aviso inicial antes de resolver
        self.aviso_vacio = tk.Label(
            card3, text="Completa las dimensiones y la matriz aumentada a la "
                        "izquierda,\n luego pulsa «Resolver Sistema».",
            font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE, justify="left",
            anchor="nw", padx=18, pady=14)
        self.aviso_vacio.pack(fill="both", expand=True)

        # Lienzo de resultados (con scroll interno independiente).
        # Se crea sin empacar; se muestra la primera vez que se resuelve.
        self.card_resultado = tk.Canvas(card3, bg=TARJETA,
                                        highlightthickness=0)
        barra_resultado = ttk.Scrollbar(card3, orient="vertical",
                                        command=self.card_resultado.yview)
        self.card_resultado.configure(
            yscrollcommand=barra_resultado.set)
        self.barra_resultado = barra_resultado

        self.frame_resultado = tk.Frame(self.card_resultado, bg=TARJETA)
        ventana_resultado = self.card_resultado.create_window(
            (0, 0), window=self.frame_resultado, anchor="nw")
        self.card_resultado.bind(
            "<Configure>",
            lambda e: self.card_resultado.itemconfig(ventana_resultado,
                                                     width=e.width))
        self.frame_resultado.bind(
            "<Configure>",
            lambda e: self.card_resultado.configure(
                scrollregion=self.card_resultado.bbox("all")))
        self.card_resultado.bind(
            "<MouseWheel>",
            lambda e: self.card_resultado.yview_scroll(
                -1 * (e.delta // 120), "units"))

    def _crear_tarjeta(self, padre):
        """Crea un frame tipo tarjeta blanca con resultado redondeado."""
        frame = tk.Frame(padre, bg=TARJETA, highlightbackground=BORDE,
                         highlightthickness=1)
        # Simular esquinas redondeadas con padding interno
        frame.configure(bd=0)
        return frame

    def _llenar_configuracion(self, card):
        """Crea los controles para elegir m (ecuaciones) y n (variables)."""
        cont = tk.Frame(card, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=16)
        tk.Label(cont, text="Dimensiones del sistema",
                 font=self.fuente_sub, bg=TARJETA, fg=TEXTO, anchor="w"
                 ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        # Spinbox: número de ecuaciones
        tk.Label(cont, text="Ecuaciones (m)", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE
                 ).grid(row=1, column=0, sticky="w", padx=(0, 12))
        self._estilo_cajas()
        spin_m = tk.Spinbox(cont, from_=1, to=8, textvariable=self.var_m,
                            font=self.fuente_body, width=5, justify="center",
                            bg="#FFFFFF", fg=TEXTO, relief="solid",
                            bd=1, highlightthickness=0)
        spin_m.grid(row=1, column=1, sticky="w", padx=(0, 28))

        # Spinbox: número de variables
        tk.Label(cont, text="Variables (n)", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE
                 ).grid(row=1, column=2, sticky="w", padx=(0, 12))
        spin_n = tk.Spinbox(cont, from_=1, to=8, textvariable=self.var_n,
                            font=self.fuente_body, width=5, justify="center",
                            bg="#FFFFFF", fg=TEXTO, relief="solid",
                            bd=1, highlightthickness=0)
        spin_n.grid(row=1, column=3, sticky="w")

        # Botón para regenerar el grid de la matriz
        tk.Button(cont, text="Actualizar Matriz", font=self.fuente_body,
                  bg=FONDO, fg=ACENTO, activebackground=ACENTO_CLARO,
                  activeforeground=ACENTO, bd=0, relief="flat", cursor="hand2",
                  padx=10, pady=4, command=self._construir_grid_matriz
                  ).grid(row=2, column=0, columnspan=4, sticky="w",
                         pady=(14, 0))

    def _llenar_cabecera_matriz(self, card):
        """Título de la sección de matriz aumentada."""
        cont = tk.Frame(card, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cont, text="Matriz aumentada [A | b] — ingrese los "
                            "coeficientes",
                 font=self.fuente_sub, bg=TARJETA, fg=TEXTO, anchor="w"
                 ).pack(side="left")

    def _estilo_cajas(self):
        """Define un estilo Theme consistente para las cajas de texto."""
        estilo = ttk.Style(self.raiz)
        estilo.theme_use("clam")
        estilo.configure("TEntry", fieldbackground="#FFFFFF",
                         foreground=TEXTO, bordercolor=BORDE, relief="flat")

    # ------------------------------------------------------------------
    # Generación dinámica de la matriz
    # ------------------------------------------------------------------
    def _construir_grid_matriz(self):
        """Limpia y reconstruye el grid de celdas según m y n (con una
        columna extra para el vector b)."""
        m = self.var_m.get()
        n = self.var_n.get()

        # Limpiar widgets anteriores
        for hijo in self.frame_matriz.winfo_children():
            hijo.destroy()

        self.celdas = []
        for i in range(m):
            fila_vars = []
            for j in range(n + 1):
                var = tk.StringVar(value="")
                fila_vars.append(var)
            self.celdas.append(fila_vars)

        # Encabezado de columnas de variables
        for j in range(n):
            tk.Label(self.frame_matriz, text=f"x{j+1}", font=self.fuente_sub,
                     bg=TARJETA, fg=TEXTO_SUAVE
                     ).grid(row=0, column=j, padx=2, pady=(0, 4))
        tk.Label(self.frame_matriz, text="b", font=self.fuente_sub,
                 bg=TARJETA, fg=TEXTO_SUAVE
                 ).grid(row=0, column=n, padx=(14, 2), pady=(0, 4))

        # Celdas de entrada
        for i in range(m):
            for j in range(n + 1):
                ancho = 6
                entrada = tk.Entry(self.frame_matriz, textvariable=self.celdas[i][j],
                                   font=self.fuente_mono, width=ancho,
                                   justify="center", relief="solid", bd=1,
                                   highlightthickness=1,
                                   highlightbackground=CELDA_BORDE,
                                   highlightcolor=ACENTO, bg="#FFFFFF", fg=TEXTO)
                # Columna b separada visualmente con más margen
                padx = (14, 2) if j == n else (2, 2)
                entrada.grid(row=i + 1, column=j, padx=padx, pady=3, ipady=3)

        # Recordatorio de formato
        tk.Label(self.frame_matriz,
                 text="Puedes ingresar enteros, decimales o fracciones "
                      "(ej. 3/4).",
                 font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE, anchor="w"
                 ).grid(row=m + 2, column=0, columnspan=n + 1, sticky="w",
                        pady=(8, 0))

    # ------------------------------------------------------------------
    # Acción principal: leer, resolver y mostrar
    # ------------------------------------------------------------------
    def _al_resolver(self):
        """Lee las celdas, valida, resuelve y despliega los resultados."""
        m = self.var_m.get()
        n = self.var_n.get()

        # Leer coeficientes y términos independientes, validando entradas
        A = []
        b = []
        for i in range(m):
            fila = []
            for j in range(n):
                texto = self.celdas[i][j].get()
                try:
                    fila.append(a_numero(texto))
                except ValueError:
                    self._mostrar_error(
                        f"Valor inválido en la posición A[{i+1},{j+1}]: "
                        f"'{texto}'. Ingresa un número o fracción.",
                        i * (n + 1) + j)
                    return
            A.append(fila)
            try:
                b.append(a_numero(self.celdas[i][n].get()))
            except ValueError:
                self._mostrar_error(
                    f"Valor inválido en el término independiente de la "
                    f"ecuación {i+1}: '{self.celdas[i][n].get()}'.",
                    i * (n + 1) + n)
                return

        # Resolver con el núcleo matemático
        resultado = resolver_sistema(m, n, A, b)
        self._mostrar_resultado(resultado)

    def _mostrar_error(self, mensaje, indice_celda):
        """Muestra un error y coloca el foco en la celda problemática."""
        messagebox.showerror("Entrada inválida", mensaje)
        # Colocar foco en la celda correspondiente
        fila = indice_celda // (self.var_n.get() + 1)
        col = indice_celda % (self.var_n.get() + 1)
        # Rebuscar la Entry correspondiente (widgets del frame_matriz)
        widgets = self.frame_matriz.winfo_children()
        for w in widgets:
            if isinstance(w, tk.Entry) and w.grid_info().get("column") == col \
                    and w.grid_info().get("row") == fila + 1:
                w.focus_set()
                w.configure(highlightcolor=ERROR, highlightbackground=ERROR)
                break

    def _limpiar_resultado(self):
        """Destruye el contenido anterior del panel de resultados y, si el
        aviso inicial sigue visible, lo sustituye por el lienzo de
        resultados."""
        # Quitar aviso inicial la primera vez
        if self.aviso_vacio.winfo_manager():
            self.aviso_vacio.destroy()
            self.card_resultado.pack(side="left", fill="both", expand=True,
                                     padx=(6, 0), pady=(0, 12))
            self.barra_resultado.pack(side="right", fill="y", pady=(0, 12))
        # Limpiar tarjetas del contenido previo
        for hijo in self.frame_resultado.winfo_children():
            hijo.destroy()

    def _sub_tarjeta(self, titulo_texto, color_acento):
        """Crea una sub-tarjeta con un título de color dentro del panel de
        resultados."""
        sub = tk.Frame(self.frame_resultado, bg=TARJETA)
        sub.pack(fill="x", padx=16, pady=(4, 2), anchor="n")
        tk.Label(sub, text=titulo_texto, font=self.fuente_encab,
                 bg=TARJETA, fg=color_acento, anchor="w"
                 ).pack(fill="x", padx=2, pady=(6, 2))
        return sub

    def _mostrar_resultado(self, r):
        """Renderiza el resultado en el panel derecho con tarjetas
        visuales: clasificación, solución, verificación y pasos."""
        self._limpiar_resultado()
        fr = self.frame_resultado

        # Color según la clasificación
        color = TEXTO
        if r["clasificacion"] == "Consistente Determinado":
            color = EXITO
        elif r["clasificacion"] == "Consistente Indeterminado":
            color = ADVERTENCIA
        else:
            color = ERROR

        # ---- Tarjeta: Clasificación ----
        sub = self._sub_tarjeta("CLASIFICACIÓN DEL SISTEMA", TEXTO_SUAVE)
        cartel = tk.Frame(sub, bg=color, padx=14, pady=10)
        cartel.pack(fill="x", pady=(0, 4))
        tk.Label(cartel, text=r["clasificacion"].upper(),
                 font=self.fuente_big, bg=color, fg="#FFFFFF",
                 anchor="w").pack(fill="x")
        tk.Label(sub, text=r["descripcion"], font=self.fuente_body, bg=TARJETA,
                 fg=TEXTO, justify="left", anchor="w", wraplength=520
                 ).pack(fill="x", padx=2, pady=(0, 6))

        # ---- Tarjeta: Solución ----
        if r["solucion"] is not None:
            sub2 = self._sub_tarjeta("SOLUCIÓN DEL SISTEMA", ACENTO)
            cont_sol = tk.Frame(sub2, bg=FONDO, padx=12, pady=10)
            cont_sol.pack(fill="x", pady=(0, 8))
            for idx, val in enumerate(r["solucion"]):
                tk.Label(cont_sol, text=f"x{idx+1} = {_fmt(val)}",
                         font=self.fuente_big, bg=FONDO, fg=ACENTO,
                         anchor="w").pack(side="left", padx=(0, 18))
        elif r["clasificacion"] == "Consistente Indeterminado":
            sub2 = self._sub_tarjeta("VARIABLES LIBRES", ADVERTENCIA)
            if r["variables_libres"]:
                nombres = "  ".join(f"x{c+1}"
                                    for c in r["variables_libres"])
            else:
                nombres = "(ninguna)"
            tk.Label(sub2, text="Infinitas soluciones en función de:",
                     font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                     anchor="w").pack(fill="x", padx=2)
            tk.Label(sub2, text=nombres, font=self.fuente_big, bg=TARJETA,
                     fg=ADVERTENCIA, anchor="w").pack(fill="x", padx=2,
                                                      pady=(4, 8))
        else:
            sub2 = self._sub_tarjeta("SIN SOLUCIÓN", ERROR)
            tk.Label(sub2, text="El sistema es inconsistente: no existe un "
                                "valor de las variables que satisfaga todas "
                                "las ecuaciones a la vez.",
                     font=self.fuente_body, bg=TARJETA, fg=TEXTO,
                     justify="left", anchor="w", wraplength=520
                     ).pack(fill="x", padx=2, pady=(0, 8))

        # ---- Tarjeta: Verificación ----
        sub3 = self._sub_tarjeta("VERIFICACIÓN AUTOMÁTICA", EXITO)
        tk.Label(sub3, text=r["verificacion"], font=self.fuente_mono,
                 bg=sub3.cget("bg"), fg=TEXTO, justify="left", anchor="w",
                 wraplength=540).pack(fill="x", padx=2, pady=(0, 8))

        # ---- Tarjeta: Pasos de la eliminación ----
        sub4 = self._sub_tarjeta("PROCESO DE ELIMINACIÓN POR FILAS", TEXTO)
        for linea in r["pasos"]:
            tk.Label(sub4, text=linea, font=self.fuente_mono, bg=TARJETA,
                     fg=TEXTO, justify="left", anchor="w"
                     ).pack(fill="x", padx=2)

        # Desplazar al inicio del resultado
        self.card_resultado.yview_moveto(0)
        self.raiz.update_idletasks()

    # ------------------------------------------------------------------
    # Utilidades de ventana
    # ------------------------------------------------------------------
    def _centrar_ventana(self):
        """Centra la ventana en la pantalla."""
        self.raiz.update_idletasks()
        ancho = self.raiz.winfo_width()
        alto = self.raiz.winfo_height()
        x = (self.raiz.winfo_screenwidth() - ancho) // 2
        y = (self.raiz.winfo_screenheight() - alto) // 2
        self.raiz.geometry(f"+{x}+{y}")


# =====================================================================
# BLOQUE: PUNTO DE ENTRADA
# =====================================================================
def main():
    """Inicia la aplicación de escritorio."""
    raiz = tk.Tk()
    app = CalculadoraApp(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
