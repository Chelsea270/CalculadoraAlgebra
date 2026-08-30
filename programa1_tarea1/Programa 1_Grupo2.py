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
   - También permite escribir el sistema tal como aparece en el enunciado
     (por ejemplo "x1 + 2x3 + x4 = 4") y lo convierte automáticamente a la
     matriz aumentada, poniendo 0 en las variables que no aparecen.
   - Aplica eliminación por filas (Gauss), mostrando la matriz después de
     cada operación elemental realizada.
   - Clasifica el sistema (Consistente Determinado / Consistente
     Indeterminado / Inconsistente).
   - Halla las variables (si aplica) mediante sustitución regresiva.
   - Comprueba la solución sustituyendo los valores en el sistema original.

 Restricción cumplida:
   - Solo se usa Python estándar: listas anidadas, condicionales, bucles y
     funciones. NO se usan NumPy, SciPy ni funciones integradas de álgebra
     lineal. Se importa 'fractions' (biblioteca estándar de Python, no de
     álgebra lineal) para trabajar con números racionales exactos, y
     'tkinter' (también estándar) para la ventana de escritorio.

 Modo de uso:
   - Doble clic sobre el archivo, o desde la terminal:  python "Programa 1_Grupo2.py"
   - Para ejecutar las pruebas automáticas del algoritmo:
         python "Programa 1_Grupo2.py" --pruebas
=====================================================================
"""

import sys
from fractions import Fraction
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

MAX_DIMENSION = 8           # Tope de ecuaciones y variables admitidas

AYUDA_NUMERO = ("Escriba un número entero, un decimal o una fracción "
                "(por ejemplo 3, -2.5 o 3/4). Una casilla vacía vale 0.")


# =====================================================================
# BLOQUE 1: LECTURA Y FORMATO DE NÚMEROS
#
# Todo el programa trabaja con números racionales exactos (Fraction) en
# lugar de decimales (float). La razón es que la eliminación por filas
# divide constantemente, y con decimales aparecen errores de redondeo
# como 0.30000000000000004. Con fracciones el resultado es exacto y se
# muestra igual que en el cuaderno: 1/3 en vez de 0.333333.
# =====================================================================
def a_numero(texto):
    """Convierte el texto de una casilla en un número racional exacto.

    Acepta enteros ('3'), negativos ('-2'), decimales ('2.5') y
    fracciones ('3/4', '-1/2'). Una casilla vacía se interpreta como 0,
    porque en un sistema grande la mayoría de coeficientes son cero.

    Lanza ValueError con un mensaje entendible si el texto no es válido
    o si el denominador de la fracción es cero.
    """
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
            raise ValueError("El denominador de una fracción no puede ser "
                             "cero.")
        return numerador / denominador

    try:
        return Fraction(texto)
    except (ValueError, ZeroDivisionError):
        raise ValueError("Valor no reconocido. " + AYUDA_NUMERO)


def formato(valor):
    """Muestra un número racional de forma compacta: '5' si es entero,
    '3/4' si es fracción."""
    valor = Fraction(valor)
    if valor.denominator == 1:
        return str(valor.numerator)
    return f"{valor.numerator}/{valor.denominator}"


def formato_matriz(matriz, col_barra=None, sangria="   "):
    """Convierte una matriz en una lista de líneas de texto alineadas.

    col_barra indica antes de qué columna se dibuja la barra vertical
    que separa A de b en la matriz aumentada [A|b].
    """
    if not matriz:
        return []
    # Primero se calcula el ancho que necesita cada columna para que
    # todos los números queden alineados uno debajo del otro.
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
#
# Convierte un sistema escrito como en el enunciado
#     x1 + 2x3 + x4 + 3x5 = 4
# en la matriz aumentada [A|b]. Las variables que no aparecen en una
# ecuación reciben coeficiente 0 automáticamente, que es justo donde más
# se equivoca uno al llenar la matriz a mano.
# =====================================================================

# Orden preferido cuando las variables son letras sueltas (x, y, z...).
ORDEN_LETRAS = ["x", "y", "z", "w", "u", "v", "s", "t"]

# Caracteres que suele traer un texto copiado de un PDF o de Word y que
# hay que traducir antes de interpretar la ecuación.
EQUIVALENCIAS = {
    "−": "-", "–": "-", "—": "-",          # signos menos y guiones largos
    "×": "*", "·": "*",                    # signos de multiplicación
    "≡": "=", "＝": "=",                    # signos igual anchos
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",   # x₁ -> x1
}

LETRAS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITOS = "0123456789"


def _partir_variable(texto):
    """Separa un nombre de variable en (letras, número).

    'x'   -> ('x', '')          'x12' -> ('x', '12')
    Devuelve None si el texto no tiene la forma de una variable, es
    decir, una o más letras seguidas de cero o más dígitos.
    """
    if texto == "":
        return None
    corte = 0
    while corte < len(texto) and texto[corte] in LETRAS:
        corte += 1
    if corte == 0:
        return None                    # no empieza con letra
    letras = texto[:corte]
    digitos = texto[corte:]
    for caracter in digitos:
        if caracter not in DIGITOS:
            return None                # hay algo que no es dígito
    return letras, digitos


def _buscar_variable_al_final(cuerpo):
    """Busca la variable al final de un término y devuelve
    (posicion_donde_empieza, letras, digitos), o None si el término no
    lleva variable.

    Por ejemplo, en '3/4x12' devuelve (3, 'x', '12'), de modo que
    cuerpo[:3] = '3/4' es el coeficiente.
    """
    # Se recorre el término desde el final hacia atrás mientras haya
    # dígitos, y luego mientras haya letras.
    final = len(cuerpo)
    posicion = final
    while posicion > 0 and cuerpo[posicion - 1] in DIGITOS:
        posicion -= 1
    fin_letras = posicion
    while posicion > 0 and cuerpo[posicion - 1] in LETRAS:
        posicion -= 1
    if posicion == fin_letras:
        return None                    # no hay letras: es una constante
    letras = cuerpo[posicion:fin_letras]
    digitos = cuerpo[fin_letras:final]
    return posicion, letras, digitos


def _normalizar(linea):
    """Deja la línea lista para trocear: sin espacios, sin caracteres
    raros y sin símbolos de multiplicación ni guiones bajos."""
    for original, reemplazo in EQUIVALENCIAS.items():
        linea = linea.replace(original, reemplazo)
    linea = linea.replace("*", "").replace("_", "")
    return "".join(linea.split())


def _trocear(lado):
    """Parte un lado de la ecuación en términos, cada uno con su signo.

    '2x1-3x2+4' se convierte en ['+2x1', '-3x2', '+4'].
    """
    if lado == "":
        return []
    if lado[0] not in "+-":
        lado = "+" + lado

    terminos = []
    actual = lado[0]
    for caracter in lado[1:]:
        if caracter in "+-":
            terminos.append(actual)
            actual = caracter
        else:
            actual += caracter
    terminos.append(actual)
    return terminos


def _numero_del_termino(texto, termino, numero_linea):
    """Lee el coeficiente de un término y, si algo está mal, avisa
    diciendo en qué ecuación y en qué término ocurrió."""
    try:
        return a_numero(texto)
    except ValueError as error:
        raise ValueError(f"Ecuación {numero_linea}, término «{termino}»: "
                         f"{error}")


def _leer_termino(termino, numero_linea):
    """Devuelve (coeficiente, nombre de variable). El nombre es None si
    el término es una constante."""
    signo = -1 if termino[0] == "-" else 1
    cuerpo = termino[1:]
    if cuerpo == "":
        raise ValueError(f"Ecuación {numero_linea}: hay un signo suelto "
                         f"sin nada después.")

    hallazgo = _buscar_variable_al_final(cuerpo)
    if hallazgo is None:
        return signo * _numero_del_termino(cuerpo, termino,
                                           numero_linea), None

    inicio, letras, digitos = hallazgo
    nombre = letras.lower() + digitos
    texto_coeficiente = cuerpo[:inicio]
    if texto_coeficiente == "":
        coeficiente = Fraction(1)          # "x1" significa "1 * x1"
    elif texto_coeficiente.endswith("/"):
        raise ValueError(f"Ecuación {numero_linea}: falta el denominador "
                         f"en «{termino}».")
    else:
        coeficiente = _numero_del_termino(texto_coeficiente, termino,
                                          numero_linea)
    return signo * coeficiente, nombre


def _ordenar_variables(nombres):
    """Ordena las variables como se leen en clase: primero x1, x2, x3...
    y si son letras sueltas, en el orden x, y, z, w."""
    con_numero = []
    sin_numero = []
    for nombre in nombres:
        letra, digitos = _partir_variable(nombre)
        if digitos:
            con_numero.append((letra, int(digitos), nombre))
        else:
            sin_numero.append((letra, nombre))

    con_numero.sort(key=lambda dato: (dato[0], dato[1]))

    def clave_letra(dato):
        letra = dato[0]
        if letra in ORDEN_LETRAS:
            return (0, ORDEN_LETRAS.index(letra))
        return (1, letra)

    sin_numero.sort(key=clave_letra)
    return ([dato[2] for dato in con_numero] +
            [dato[1] for dato in sin_numero])


def interpretar_ecuaciones(texto):
    """Convierte un sistema escrito en lenguaje de ecuaciones a [A|b].

    Ejemplos que acepta:
        x1 + 2x3 + x4 + 3x5 = 4
        2x - 3y + 2z = 1
        4x1 - 5x2 + 2 = x1        (términos a ambos lados del igual)
        1/2x1 - 0.25x2 = 3        (fracciones y decimales)

    Devuelve (A, b, nombres_de_variables).
    """
    lineas = [linea for linea in texto.splitlines() if linea.strip() != ""]
    if not lineas:
        raise ValueError("No se escribió ninguna ecuación.")

    ecuaciones = []      # lista de (coeficientes, término independiente)
    nombres = set()

    for indice, linea_original in enumerate(lineas, start=1):
        linea = _normalizar(linea_original)
        if linea.count("=") != 1:
            raise ValueError(
                f"Ecuación {indice}: debe llevar exactamente un signo «=». "
                f"Se leyó: «{linea_original.strip()}».")
        izquierda, derecha = linea.split("=")
        if izquierda == "" or derecha == "":
            raise ValueError(f"Ecuación {indice}: falta un lado del signo "
                             f"«=».")

        coeficientes = {}
        constante = Fraction(0)

        # Se recorren los dos lados. Lo que está a la derecha entra con
        # signo cambiado, porque se pasa todo al lado izquierdo; las
        # constantes hacen el viaje contrario, hacia el término
        # independiente b.
        for lado, orientacion in ((izquierda, 1), (derecha, -1)):
            for termino in _trocear(lado):
                valor, nombre = _leer_termino(termino, indice)
                if nombre is None:
                    constante -= orientacion * valor
                else:
                    coeficientes[nombre] = (
                        coeficientes.get(nombre, Fraction(0))
                        + orientacion * valor)
                    nombres.add(nombre)

        if not coeficientes:
            raise ValueError(f"Ecuación {indice}: no tiene ninguna "
                             f"variable.")
        ecuaciones.append((coeficientes, constante))

    orden = _ordenar_variables(nombres)
    A = []
    b = []
    for coeficientes, constante in ecuaciones:
        A.append([coeficientes.get(nombre, Fraction(0)) for nombre in orden])
        b.append(constante)
    return A, b, orden


# =====================================================================
# BLOQUE 2: OPERACIONES ELEMENTALES POR FILAS
#
# Cada función realiza UNA operación elemental sobre la matriz y
# devuelve el texto que describe lo que hizo, para poder mostrar el
# procedimiento paso a paso.
# =====================================================================
def intercambiar_filas(matriz, i, j):
    """Operación elemental: intercambiar la fila i con la fila j."""
    matriz[i], matriz[j] = matriz[j], matriz[i]
    return f"Intercambio de filas: F{i+1} <-> F{j+1}"


def reemplazar_fila(matriz, destino, factor, origen):
    """Operación elemental de reemplazo: a la fila 'destino' se le resta
    la fila 'origen' multiplicada por 'factor'. Es la operación que
    genera los ceros debajo del pivote."""
    matriz[destino] = [matriz[destino][c] - factor * matriz[origen][c]
                       for c in range(len(matriz[destino]))]
    return (f"Anular F{destino+1}: F{destino+1} = F{destino+1} - "
            f"({formato(factor)}) * F{origen+1}")


# =====================================================================
# BLOQUE 3: ELIMINACIÓN POR FILAS (FORMA ESCALONADA)
# =====================================================================
def escalonar(matriz, col_barra=None):
    """Lleva la matriz aumentada a la forma escalonada por filas.

    Procedimiento, igual al que se hace a mano:
      1. Se recorre cada columna de izquierda a derecha buscando pivote.
      2. Si la casilla del pivote vale cero, se busca debajo una fila con
         entrada distinta de cero y SOLO entonces se intercambian filas.
      3. Se generan ceros debajo del pivote restando múltiplos de la fila
         pivote.
      4. Se repite con la siguiente columna y la siguiente fila.
    Al final, las filas que quedaron completamente en cero se bajan al
    fondo, como exige la definición de forma escalonada.

    No se normaliza el pivote a 1 porque la forma escalonada solo exige
    que la entrada principal sea distinta de cero; convertirla en 1
    corresponde a la forma escalonada reducida.

    Devuelve (pasos, pivotes) y modifica la matriz en el lugar.
    """
    pasos = []
    filas = len(matriz)
    columnas = len(matriz[0])
    fila_pivote = 0
    pivotes = []          # lista de parejas (fila, columna) de cada pivote

    for col in range(columnas):
        if fila_pivote >= filas:
            break

        # --- Paso 2: buscar una entrada distinta de cero en la columna ---
        fila_no_nula = None
        for f in range(fila_pivote, filas):
            if matriz[f][col] != 0:
                fila_no_nula = f
                break
        if fila_no_nula is None:
            # Columna sin pivote: corresponde a una variable libre.
            continue

        if fila_no_nula != fila_pivote:
            pasos.append(intercambiar_filas(matriz, fila_pivote, fila_no_nula))
            pasos.extend(formato_matriz(matriz, col_barra))

        # --- Paso 3: generar ceros debajo del pivote ---
        for f in range(fila_pivote + 1, filas):
            if matriz[f][col] != 0:
                factor = matriz[f][col] / matriz[fila_pivote][col]
                pasos.append(reemplazar_fila(matriz, f, factor, fila_pivote))
                pasos.extend(formato_matriz(matriz, col_barra))

        pivotes.append((fila_pivote, col))
        fila_pivote += 1

    # --- Las filas completamente nulas se bajan al fondo ---
    # Ojo: una fila [0 0 ... 0 | k] con k distinto de cero NO es una fila
    # nula, por eso debe quedar por encima de las que sí lo son.
    f = fila_pivote
    while f < filas:
        if all(valor == 0 for valor in matriz[f]):
            siguiente = None
            for g in range(f + 1, filas):
                if any(valor != 0 for valor in matriz[g]):
                    siguiente = g
                    break
            if siguiente is None:
                break
            pasos.append(intercambiar_filas(matriz, f, siguiente))
            pasos.extend(formato_matriz(matriz, col_barra))
        f += 1

    return pasos, pivotes


def entrada_principal(fila):
    """Índice del primer elemento distinto de cero de una fila.
    Devuelve None si la fila es nula."""
    for c, valor in enumerate(fila):
        if valor != 0:
            return c
    return None


def es_escalonada(matriz):
    """Comprueba las tres propiedades de la forma escalonada. Se usa en
    las pruebas automáticas para confirmar que el algoritmo trabaja
    bien."""
    principales = [entrada_principal(fila) for fila in matriz]

    # Propiedad 1: las filas nulas van al fondo.
    vista_nula = False
    for p in principales:
        if p is None:
            vista_nula = True
        elif vista_nula:
            return False, "hay una fila no nula debajo de una fila de ceros"

    # Propiedad 2: patrón de escalera (cada entrada principal más a la
    # derecha que la de la fila anterior). Esto implica la propiedad 3.
    anterior = -1
    for p in principales:
        if p is None:
            continue
        if p <= anterior:
            return False, "las entradas principales no forman escalera"
        anterior = p

    return True, ""


# =====================================================================
# BLOQUE 4: CLASIFICACIÓN Y SOLUCIÓN DEL SISTEMA
# =====================================================================
def resolver_sistema(m, n, A, b):
    """Resuelve el sistema A x = b por eliminación por filas.

    Parámetros:
        m (int): número de ecuaciones.
        n (int): número de variables.
        A (list): matriz de coeficientes (m filas por n columnas).
        b (list): vector de términos independientes (m elementos).

    Devuelve un diccionario con:
        pasos            : líneas del procedimiento paso a paso.
        escalonada       : matriz aumentada en forma escalonada.
        clasificacion    : 'Consistente Determinado' | 'Consistente
                           Indeterminado' | 'Inconsistente'.
        descripcion      : explicación de la clasificación.
        homogeneo        : True si todos los términos de b son cero.
        variables_libres : índices (base 0) de las variables libres.
        solucion         : lista con el valor de cada variable, o None.
        verificacion     : texto con la comprobación de la solución.
    """
    # Se copia todo a Fraction para no depender del tipo que llegue.
    A = [[Fraction(valor) for valor in fila] for fila in A]
    b = [Fraction(valor) for valor in b]

    # --- Construcción de la matriz aumentada [A|b] ---
    aumentada = [A[i][:] + [b[i]] for i in range(m)]

    pasos = ["Matriz aumentada inicial [A|b]:"]
    pasos.extend(formato_matriz(aumentada, n))

    # --- Fase de escalonamiento ---
    pasos_escalonamiento, pivotes = escalonar(aumentada, n)
    if pasos_escalonamiento:
        pasos.extend(pasos_escalonamiento)
    else:
        pasos.append("La matriz ya estaba en forma escalonada; no hizo "
                     "falta ninguna operación.")
    pasos.append("Forma escalonada final:")
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

    # --- Caso 1: sistema inconsistente ---
    # Aparece una fila [0 0 ... 0 | k] con k distinto de cero, es decir,
    # la ecuación imposible 0 = k.
    if n in columnas_pivote:
        fila_k = 0
        for i, fila in enumerate(aumentada):
            if all(valor == 0 for valor in fila[:n]) and fila[n] != 0:
                fila_k = i
                break
        valor_k = formato(aumentada[fila_k][n])
        resultado["clasificacion"] = "Inconsistente"
        resultado["descripcion"] = (
            f"Sistema sin solución. La fila F{fila_k+1} quedó de la forma "
            f"[0 0 ... 0 | k] con k = {valor_k}, que corresponde a la "
            f"ecuación imposible 0 = {valor_k}.")
        resultado["verificacion"] = (
            "No hay ninguna solución que comprobar: el sistema es "
            "inconsistente.")
        return resultado

    # Solo interesan los pivotes que caen en columnas de variables.
    pivotes_variables = [(f, c) for f, c in pivotes if c < n]
    columnas_con_pivote = [c for _, c in pivotes_variables]
    variables_libres = [c for c in range(n) if c not in columnas_con_pivote]
    resultado["variables_libres"] = variables_libres

    # --- Caso 2: infinitas soluciones ---
    if variables_libres:
        cantidad_pivotes = len(pivotes_variables)
        cantidad_libres = len(variables_libres)
        texto_pivotes = ("1 pivote" if cantidad_pivotes == 1
                         else f"{cantidad_pivotes} pivotes")
        texto_libres = ("1 variable libre" if cantidad_libres == 1
                        else f"{cantidad_libres} variables libres")
        resultado["clasificacion"] = "Consistente Indeterminado"
        resultado["descripcion"] = (
            f"Sistema con infinitas soluciones. Hay {texto_pivotes} para "
            f"{n} variables, de modo que hay {texto_libres}: cada valor "
            f"que se le asigne produce una solución distinta.")
        resultado["verificacion"] = (
            "El sistema tiene infinitas soluciones, por lo que no hay un "
            "único valor numérico que comprobar: el valor de las variables "
            "básicas depende del que se asigne a las variables libres.")
        return resultado

    # --- Caso 3: solución única ---
    solucion = sustitucion_regresiva(aumentada, n, pivotes_variables)
    resultado["clasificacion"] = "Consistente Determinado"
    resultado["descripcion"] = (
        "Sistema con solución única. Hay un pivote en cada una de las "
        f"{n} columnas de variables, así que no existen variables libres.")
    resultado["solucion"] = solucion
    resultado["verificacion"] = verificar(m, n, A, b, solucion)
    return resultado


def sustitucion_regresiva(aumentada, n, pivotes_variables):
    """Obtiene el valor de cada variable recorriendo la forma escalonada
    de abajo hacia arriba: en cada fila se despeja la variable del pivote
    usando las que ya se conocen."""
    x = [Fraction(0)] * n
    for fila_p, col_p in reversed(pivotes_variables):
        total = aumentada[fila_p][n]
        for c in range(col_p + 1, n):
            total -= aumentada[fila_p][c] * x[c]
        x[col_p] = total / aumentada[fila_p][col_p]
    return x


def verificar(m, n, A, b, solucion):
    """Comprueba la solución sustituyendo los valores obtenidos en el
    sistema original: reconstruye A·x sumando productos y lo compara
    con b, ecuación por ecuación."""
    lineas = ["Se sustituyen los valores hallados en el sistema original:",
              "-" * 46]
    todo_correcto = True
    for i in range(m):
        total = Fraction(0)
        for j in range(n):
            total += A[i][j] * solucion[j]
        correcta = (total == b[i])
        todo_correcto = todo_correcto and correcta
        lineas.append(f"   Ec{i+1}:  {formato(total)} = {formato(b[i])}"
                      f"   ->  {'CORRECTO' if correcta else 'FALLO'}")
    lineas.append("-" * 46)
    if todo_correcto:
        lineas.append("La solución satisface todas las ecuaciones.")
    else:
        lineas.append("La solución NO satisface el sistema.")
    return "\n".join(lineas)


# =====================================================================
# BLOQUE 5: EJEMPLOS PRECARGADOS
# Los tres casos del informe, para poder mostrarlos rápido en la
# presentación sin teclear la matriz cada vez.
# =====================================================================
EJEMPLOS = {
    "unica": {
        "titulo": "Solución única",
        "ecuaciones": ("x1 + x2 + x3 = 6\n"
                       "2x1 - x2 + x3 = 3\n"
                       "x1 + 2x2 - x3 = 2"),
    },
    "infinitas": {
        "titulo": "Infinitas soluciones",
        "ecuaciones": ("x1 + x2 + x3 = 1\n"
                       "2x1 + 2x2 + 2x3 = 2"),
    },
    "sin_solucion": {
        "titulo": "Sin solución",
        "ecuaciones": ("x1 + x2 = 1\n"
                       "x1 + x2 = 3"),
    },
}


# =====================================================================
# BLOQUE 6: INTERFAZ GRÁFICA DE ESCRITORIO (Tkinter)
# Estética minimalista tipo iOS/Apple: fondo claro, tarjetas blancas,
# botón azul de acción principal y tipografía limpia.
# =====================================================================
class CalculadoraApp:
    """Ventana principal de la calculadora."""

    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Calculadora de Álgebra Lineal · Grupo 2")
        self.raiz.configure(bg=FONDO)
        # La ventana se adapta a la pantalla del equipo: pide el tamaño
        # cómodo, pero nunca más de lo que cabe.
        ancho = min(1300, self.raiz.winfo_screenwidth() - 80)
        alto = min(830, self.raiz.winfo_screenheight() - 120)
        self.raiz.geometry(f"{max(1120, ancho)}x{max(640, alto)}")
        self.raiz.minsize(1120, 640)

        # Variables de control de dimensiones y celdas
        self.var_m = tk.StringVar(value="3")   # número de ecuaciones
        self.var_n = tk.StringVar(value="3")   # número de variables
        self.celdas = {}       # (fila, columna) -> StringVar
        self.entradas = {}     # (fila, columna) -> widget Entry
        self.filas_actuales = 0
        self.columnas_actuales = 0
        self.procedimiento_visible = False
        self.ultimo_resultado = None
        # Etiquetas del panel de resultados cuyo ancho de ajuste de línea
        # se recalcula cada vez que cambia el tamaño de la ventana, para
        # que ningún texto quede cortado.
        self.etiquetas_ajustables = []

        # Fuentes
        self.fuente_titulo = tkfont.Font(family="Segoe UI", size=22,
                                         weight="bold")
        self.fuente_sub = tkfont.Font(family="Segoe UI", size=11)
        self.fuente_body = tkfont.Font(family="Segoe UI", size=11)
        self.fuente_encab = tkfont.Font(family="Segoe UI", size=11,
                                        weight="bold")
        self.fuente_big = tkfont.Font(family="Segoe UI", size=17,
                                      weight="bold")
        self.fuente_cartel = tkfont.Font(family="Segoe UI", size=15,
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
        muestran los resultados. Cada panel desplaza su propio contenido."""

        fondo = tk.Frame(self.raiz, bg=FONDO)
        fondo.pack(fill="both", expand=True)
        # Los dos paneles se reparten el ancho en proporción 2 a 3: el
        # izquierdo para escribir el ejercicio, el derecho para el
        # resultado, que necesita más espacio por el procedimiento.
        fondo.columnconfigure(0, weight=2, uniform="paneles")   # izquierdo
        fondo.columnconfigure(1, weight=3, uniform="paneles")   # derecho
        fondo.rowconfigure(2, weight=1)

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

        # Tarjeta 1: escribir el sistema tal como viene en el enunciado
        tarjeta_ecuaciones = self._crear_tarjeta(panel_izq)
        tarjeta_ecuaciones.pack(side="top", fill="x", pady=(0, 10))
        self._llenar_ecuaciones(tarjeta_ecuaciones)

        # El botón principal se coloca antes que la tarjeta de la matriz y
        # anclado abajo: así siempre tiene su espacio reservado y nunca
        # queda fuera de la ventana aunque la matriz sea grande.
        self.boton_resolver = tk.Button(
            panel_izq, text="Resolver Sistema", font=self.fuente_boton,
            bg=ACENTO, fg="#FFFFFF", activebackground="#0062C4",
            activeforeground="#FFFFFF", bd=0, cursor="hand2", relief="flat",
            padx=18, pady=12, command=self._al_resolver)
        self.boton_resolver.pack(side="bottom", fill="x", pady=(10, 0))

        # Tarjeta 2: dimensiones y cuadrícula de la matriz aumentada
        tarjeta_matriz = self._crear_tarjeta(panel_izq)
        tarjeta_matriz.pack(side="top", fill="both", expand=True)
        self._llenar_cabecera_matriz(tarjeta_matriz)

        # Área de la matriz dentro de un lienzo desplazable. Lleva barra
        # vertical y horizontal, porque una matriz de 8 variables es más
        # ancha que el panel.
        contenedor_matriz = tk.Frame(tarjeta_matriz, bg=TARJETA)
        contenedor_matriz.pack(fill="both", expand=True, padx=(6, 6),
                               pady=(0, 10))
        contenedor_matriz.rowconfigure(0, weight=1)
        contenedor_matriz.columnconfigure(0, weight=1)

        lienzo_matriz = tk.Canvas(contenedor_matriz, bg=TARJETA,
                                  highlightthickness=0, width=400,
                                  height=170)
        barra_v = ttk.Scrollbar(contenedor_matriz, orient="vertical",
                                command=lienzo_matriz.yview)
        barra_h = ttk.Scrollbar(contenedor_matriz, orient="horizontal",
                                command=lienzo_matriz.xview)
        lienzo_matriz.configure(yscrollcommand=barra_v.set,
                                xscrollcommand=barra_h.set)
        self.frame_matriz = tk.Frame(lienzo_matriz, bg=TARJETA)
        lienzo_matriz.create_window((0, 0), window=self.frame_matriz,
                                    anchor="nw")
        self.frame_matriz.bind(
            "<Configure>",
            lambda e: lienzo_matriz.configure(
                scrollregion=lienzo_matriz.bbox("all")))
        self.lienzo_matriz = lienzo_matriz
        self._activar_rueda(lienzo_matriz)

        lienzo_matriz.grid(row=0, column=0, sticky="nsew")
        barra_v.grid(row=0, column=1, sticky="ns")
        barra_h.grid(row=1, column=0, sticky="ew")

        # La ayuda va fuera de la cuadrícula: si estuviera dentro, al ser
        # una línea larga obligaría a las columnas de la matriz a
        # ensancharse para acomodarla.
        tk.Label(tarjeta_matriz,
                 text="Enteros, decimales o fracciones. Vacío = 0.",
                 font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                 anchor="w", justify="left"
                 ).pack(fill="x", padx=18, pady=(0, 12))

        # ================= PANEL DERECHO: RESULTADO =================
        panel_der = tk.Frame(fondo, bg=FONDO)
        panel_der.grid(row=2, column=1, sticky="nsew", padx=(14, 34),
                       pady=(0, 26))

        tarjeta_resultado = self._crear_tarjeta(panel_der)
        tarjeta_resultado.pack(fill="both", expand=True)

        cabecera = tk.Frame(tarjeta_resultado, bg=TARJETA)
        cabecera.pack(fill="x", padx=18, pady=(14, 6))
        tk.Label(cabecera, text="Resultado", font=self.fuente_sub,
                 bg=TARJETA, fg=TEXTO, anchor="w").pack(side="left")

        # Botón para mostrar u ocultar el procedimiento. Se crea aquí pero
        # solo se muestra después de resolver un sistema.
        self.boton_procedimiento = tk.Button(
            cabecera, text="Ver procedimiento", font=self.fuente_body,
            bg=FONDO, fg=ACENTO, activebackground=ACENTO_CLARO,
            activeforeground=ACENTO, bd=0, relief="flat", cursor="hand2",
            padx=12, pady=4, command=self._alternar_procedimiento)

        self.aviso_vacio = tk.Label(
            tarjeta_resultado,
            text="Complete las dimensiones y la matriz aumentada a la "
                 "izquierda,\ny luego pulse «Resolver Sistema».",
            font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE, justify="left",
            anchor="nw", padx=18, pady=14)
        self.aviso_vacio.pack(fill="both", expand=True)

        # Lienzo de resultados con su propio desplazamiento. Se crea sin
        # empacar; aparece la primera vez que se resuelve un sistema.
        self.lienzo_resultado = tk.Canvas(tarjeta_resultado, bg=TARJETA,
                                          highlightthickness=0)
        self.barra_resultado = ttk.Scrollbar(
            tarjeta_resultado, orient="vertical",
            command=self.lienzo_resultado.yview)
        self.lienzo_resultado.configure(
            yscrollcommand=self.barra_resultado.set)

        self.frame_resultado = tk.Frame(self.lienzo_resultado, bg=TARJETA)
        ventana_resultado = self.lienzo_resultado.create_window(
            (0, 0), window=self.frame_resultado, anchor="nw")
        def al_cambiar_tamano(evento):
            # El contenido ocupa todo el ancho disponible y, además, se
            # recalcula dónde deben cortar la línea los textos largos.
            self.lienzo_resultado.itemconfig(ventana_resultado,
                                             width=evento.width)
            self._ajustar_textos(evento.width)

        self.lienzo_resultado.bind("<Configure>", al_cambiar_tamano)
        self.frame_resultado.bind(
            "<Configure>",
            lambda e: self.lienzo_resultado.configure(
                scrollregion=self.lienzo_resultado.bbox("all")))
        self._activar_rueda(self.lienzo_resultado)

    def _ajustar_textos(self, ancho_disponible=None):
        """Recalcula el ancho de ajuste de línea de los textos del panel
        de resultados. Sin esto, al encoger la ventana las frases largas
        quedarían cortadas por el borde."""
        if ancho_disponible is None:
            ancho_disponible = self.lienzo_resultado.winfo_width()
        ancho = max(240, ancho_disponible - 56)
        for etiqueta in self.etiquetas_ajustables:
            try:
                etiqueta.configure(wraplength=ancho)
            except tk.TclError:
                pass   # la etiqueta ya fue destruida

    def _texto_ajustable(self, etiqueta):
        """Registra una etiqueta para que su texto se reajuste al
        cambiar el tamaño de la ventana."""
        self.etiquetas_ajustables.append(etiqueta)
        return etiqueta

    def _activar_rueda(self, lienzo):
        """Permite desplazar un lienzo con la rueda del ratón cuando el
        puntero está encima. Se usa bind_all mientras el puntero entra y
        se suelta al salir, para que cada panel desplace solo lo suyo."""
        def al_girar(evento):
            if evento.num == 4:          # Linux: rueda hacia arriba
                lienzo.yview_scroll(-1, "units")
            elif evento.num == 5:        # Linux: rueda hacia abajo
                lienzo.yview_scroll(1, "units")
            else:                        # Windows y macOS
                lienzo.yview_scroll(-1 * (evento.delta // 120), "units")

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
        """Crea un marco tipo tarjeta blanca con borde sutil."""
        return tk.Frame(padre, bg=TARJETA, highlightbackground=BORDE,
                        highlightthickness=1, bd=0)

    def _llenar_ecuaciones(self, tarjeta):
        """Caja de texto donde se escribe el sistema de ecuaciones tal
        como aparece en el enunciado, con su botón de conversión."""
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 14))

        tk.Label(cont, text="Sistema de ecuaciones",
                 font=self.fuente_sub, bg=TARJETA, fg=TEXTO, anchor="w"
                 ).pack(fill="x", pady=(0, 2))
        tk.Label(cont,
                 text="Una ecuación por línea; las que falten valen 0.",
                 font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                 anchor="w", justify="left", wraplength=420
                 ).pack(fill="x", pady=(0, 6))

        self.caja_ecuaciones = tk.Text(
            cont, height=5, font=self.fuente_mono, bg="#FFFFFF", fg=TEXTO,
            relief="solid", bd=1, highlightthickness=1,
            highlightbackground=CELDA_BORDE, highlightcolor=ACENTO,
            wrap="none", padx=8, pady=6, insertbackground=TEXTO)
        self.caja_ecuaciones.pack(fill="x")
        self.caja_ecuaciones.insert("1.0", "x1 + x2 + x3 = 6\n"
                                           "2x1 - x2 + x3 = 3\n"
                                           "x1 + 2x2 - x3 = 2")

        botones = tk.Frame(cont, bg=TARJETA)
        botones.pack(fill="x", pady=(8, 0))
        # Primera fila: acciones sobre lo escrito. Segunda fila: los tres
        # ejemplos. Repartidos así caben incluso en la ventana más
        # pequeña que admite el programa.
        acciones = [
            (0, 0, "Convertir a matriz", self._convertir_ecuaciones),
            (0, 1, "Borrar", self._borrar_ecuaciones),
            (1, 0, "Ej. única", lambda: self._cargar_ejemplo("unica")),
            (1, 1, "Ej. infinitas", lambda: self._cargar_ejemplo("infinitas")),
            (1, 2, "Ej. sin solución",
             lambda: self._cargar_ejemplo("sin_solucion")),
        ]
        for fila, columna, texto, accion in acciones:
            self._boton_secundario(botones, texto, accion, fila=fila,
                                   columna=columna)

        self.aviso_ecuaciones = tk.Label(
            cont, text="", font=self.fuente_body, bg=TARJETA, fg=EXITO,
            anchor="w", justify="left")
        self.aviso_ecuaciones.pack(fill="x", pady=(4, 0))

    def _borrar_ecuaciones(self):
        """Vacía la caja de ecuaciones."""
        self.caja_ecuaciones.delete("1.0", "end")
        self.aviso_ecuaciones.configure(text="")

    def _convertir_ecuaciones(self):
        """Lee las ecuaciones escritas, arma la matriz aumentada y llena
        la cuadrícula. Si algo no se entiende, avisa sin cerrarse."""
        try:
            texto = self.caja_ecuaciones.get("1.0", "end")
            A, b, nombres = interpretar_ecuaciones(texto)

            filas = len(A)
            columnas = len(nombres)
            if filas > MAX_DIMENSION or columnas > MAX_DIMENSION:
                raise ValueError(
                    f"El sistema tiene {filas} ecuaciones y {columnas} "
                    f"variables, y el programa admite como máximo "
                    f"{MAX_DIMENSION} de cada una.")

            self.var_m.set(str(filas))
            self.var_n.set(str(columnas))
            self._construir_grid_matriz()
            self._limpiar_celdas()
            for i in range(filas):
                for j in range(columnas):
                    self.celdas[(i, j)].set(formato(A[i][j]))
                self.celdas[(i, columnas)].set(formato(b[i]))

            self.aviso_ecuaciones.configure(
                fg=EXITO,
                text=f"Listo: {filas} ecuaciones y {columnas} variables "
                     f"({', '.join(nombres)}).")

        except ValueError as error:
            self.aviso_ecuaciones.configure(fg=ERROR, text=str(error))
            messagebox.showerror("No se pudo leer el sistema", str(error))
        except Exception as error:                      # red de seguridad
            mensaje = (f"{type(error).__name__}: {error}")
            self.aviso_ecuaciones.configure(fg=ERROR, text=mensaje)
            messagebox.showerror("No se pudo leer el sistema", mensaje)

    def _boton_secundario(self, padre, texto, accion, fila=0, columna=0):
        """Botón plano de apoyo, en azul sobre fondo claro."""
        boton = tk.Button(padre, text=texto, font=self.fuente_body,
                          bg=FONDO, fg=ACENTO, activebackground=ACENTO_CLARO,
                          activeforeground=ACENTO, bd=0, relief="flat",
                          cursor="hand2", padx=10, pady=4, command=accion)
        boton.grid(row=fila, column=columna, sticky="w", padx=(0, 8),
                   pady=(0, 4))
        return boton

    def _llenar_cabecera_matriz(self, tarjeta):
        """Cabecera de la matriz aumentada: título, dimensiones del
        sistema y botones para regenerar o vaciar la cuadrícula."""
        cont = tk.Frame(tarjeta, bg=TARJETA)
        cont.pack(fill="x", padx=18, pady=(14, 6))

        tk.Label(cont,
                 text="Matriz aumentada [A | b] — ingrese los coeficientes",
                 font=self.fuente_sub, bg=TARJETA, fg=TEXTO, anchor="w"
                 ).grid(row=0, column=0, columnspan=6, sticky="w",
                        pady=(0, 8))

        self._estilo_cajas()

        tk.Label(cont, text="Ecuaciones (m)", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE
                 ).grid(row=1, column=0, sticky="w", padx=(0, 8))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_m,
                   font=self.fuente_body, width=4, justify="center",
                   bg="#FFFFFF", fg=TEXTO, relief="solid", bd=1,
                   highlightthickness=0, command=self._construir_grid_matriz
                   ).grid(row=1, column=1, sticky="w", padx=(0, 18))

        tk.Label(cont, text="Variables (n)", font=self.fuente_body,
                 bg=TARJETA, fg=TEXTO_SUAVE
                 ).grid(row=1, column=2, sticky="w", padx=(0, 8))
        tk.Spinbox(cont, from_=1, to=MAX_DIMENSION, textvariable=self.var_n,
                   font=self.fuente_body, width=4, justify="center",
                   bg="#FFFFFF", fg=TEXTO, relief="solid", bd=1,
                   highlightthickness=0, command=self._construir_grid_matriz
                   ).grid(row=1, column=3, sticky="w")

        # Los botones van en su propia fila para que quepan también en
        # ventanas angostas.
        botones = tk.Frame(cont, bg=TARJETA)
        botones.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))
        self._boton_secundario(botones, "Actualizar matriz",
                               self._construir_grid_matriz, fila=0, columna=0)
        self._boton_secundario(botones, "Limpiar", self._limpiar_celdas,
                               fila=0, columna=1)

    def _estilo_cajas(self):
        """Estilo consistente para los controles ttk."""
        estilo = ttk.Style(self.raiz)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass   # si el tema no existe se conserva el que traiga el sistema
        estilo.configure("TEntry", fieldbackground="#FFFFFF",
                         foreground=TEXTO, bordercolor=BORDE, relief="flat")

    # ------------------------------------------------------------------
    # Generación dinámica de la matriz
    # ------------------------------------------------------------------
    def _leer_dimension(self, variable, por_defecto):
        """Lee un Spinbox de forma segura. Si el usuario escribió algo que
        no es un número válido, se devuelve el valor por defecto en vez de
        dejar que el programa falle."""
        try:
            valor = int(str(variable.get()).strip())
        except (ValueError, TypeError):
            valor = por_defecto
        valor = max(1, min(MAX_DIMENSION, valor))
        variable.set(str(valor))
        return valor

    def _construir_grid_matriz(self):
        """Reconstruye la cuadrícula de casillas según m y n, con una
        columna extra para el vector b. Conserva los valores que ya
        estaban escritos en las casillas que siguen existiendo."""
        m = self._leer_dimension(self.var_m, 3)
        n = self._leer_dimension(self.var_n, 3)

        valores_previos = {clave: var.get()
                           for clave, var in self.celdas.items()}

        for hijo in self.frame_matriz.winfo_children():
            hijo.destroy()
        self.celdas = {}
        self.entradas = {}
        self.filas_actuales = m
        self.columnas_actuales = n

        # Encabezado de columnas: x1, x2, ... y la columna b
        for j in range(n):
            tk.Label(self.frame_matriz, text=f"x{j+1}", font=self.fuente_sub,
                     bg=TARJETA, fg=TEXTO_SUAVE
                     ).grid(row=0, column=j, padx=2, pady=(0, 4))
        tk.Label(self.frame_matriz, text="b", font=self.fuente_sub,
                 bg=TARJETA, fg=TEXTO_SUAVE
                 ).grid(row=0, column=n, padx=(14, 2), pady=(0, 4))

        # Casillas de entrada
        for i in range(m):
            for j in range(n + 1):
                variable = tk.StringVar(value=valores_previos.get((i, j), ""))
                self.celdas[(i, j)] = variable
                entrada = tk.Entry(
                    self.frame_matriz, textvariable=variable,
                    font=self.fuente_mono, width=6, justify="center",
                    relief="solid", bd=1, highlightthickness=1,
                    highlightbackground=CELDA_BORDE, highlightcolor=ACENTO,
                    bg="#FFFFFF", fg=TEXTO)
                padx = (14, 2) if j == n else (2, 2)
                entrada.grid(row=i + 1, column=j, padx=padx, pady=3, ipady=3)
                entrada.bind("<Return>", lambda e: self._al_resolver())
                self.entradas[(i, j)] = entrada

    def _limpiar_celdas(self):
        """Vacía todas las casillas de la matriz."""
        for variable in self.celdas.values():
            variable.set("")
        for entrada in self.entradas.values():
            entrada.configure(highlightbackground=CELDA_BORDE,
                              highlightcolor=ACENTO)

    def _cargar_ejemplo(self, clave):
        """Escribe uno de los tres ejemplos en la caja de ecuaciones y lo
        convierte a matriz, de modo que se vean los dos pasos."""
        self.caja_ecuaciones.delete("1.0", "end")
        self.caja_ecuaciones.insert("1.0", EJEMPLOS[clave]["ecuaciones"])
        self._convertir_ecuaciones()

    # ------------------------------------------------------------------
    # Acción principal: leer, resolver y mostrar
    # ------------------------------------------------------------------
    def _al_resolver(self):
        """Lee las casillas, valida, resuelve y despliega los resultados.

        Todo el cuerpo está protegido: si ocurriera cualquier error
        inesperado se muestra un aviso y la ventana sigue funcionando, en
        lugar de cerrarse."""
        try:
            m = self.filas_actuales
            n = self.columnas_actuales

            A = []
            b = []
            for i in range(m):
                fila = []
                for j in range(n):
                    try:
                        fila.append(a_numero(self.celdas[(i, j)].get()))
                    except ValueError as error:
                        self._mostrar_error(
                            f"Revise la casilla de la fila {i+1}, columna "
                            f"x{j+1}.\n\n{error}", i, j)
                        return
                A.append(fila)
                try:
                    b.append(a_numero(self.celdas[(i, n)].get()))
                except ValueError as error:
                    self._mostrar_error(
                        f"Revise el término independiente de la ecuación "
                        f"{i+1}.\n\n{error}", i, n)
                    return

            self._restaurar_bordes()
            resultado = resolver_sistema(m, n, A, b)
            self.ultimo_resultado = resultado
            self._mostrar_resultado(resultado)

        except Exception as error:                      # red de seguridad
            messagebox.showerror(
                "Error inesperado",
                "Ocurrió un problema al resolver el sistema:\n\n"
                f"{type(error).__name__}: {error}\n\n"
                "Revise los datos ingresados e inténtelo de nuevo.")

    def _restaurar_bordes(self):
        """Devuelve todas las casillas a su borde normal."""
        for entrada in self.entradas.values():
            entrada.configure(highlightbackground=CELDA_BORDE,
                              highlightcolor=ACENTO)

    def _mostrar_error(self, mensaje, fila, columna):
        """Avisa del error, marca en rojo la casilla y le pone el foco."""
        self._restaurar_bordes()
        entrada = self.entradas.get((fila, columna))
        if entrada is not None:
            entrada.configure(highlightbackground=ERROR, highlightcolor=ERROR)
            entrada.focus_set()
            entrada.selection_range(0, "end")
        messagebox.showerror("Entrada inválida", mensaje)

    # ------------------------------------------------------------------
    # Presentación de resultados
    # ------------------------------------------------------------------
    def _limpiar_resultado(self):
        """Quita el contenido anterior del panel de resultados y, la
        primera vez, sustituye el aviso inicial por el lienzo."""
        if self.aviso_vacio is not None and self.aviso_vacio.winfo_manager():
            self.aviso_vacio.destroy()
            self.aviso_vacio = None
            self.lienzo_resultado.pack(side="left", fill="both", expand=True,
                                       padx=(6, 0), pady=(0, 12))
            self.barra_resultado.pack(side="right", fill="y", pady=(0, 12))
        for hijo in self.frame_resultado.winfo_children():
            hijo.destroy()
        self.etiquetas_ajustables = []

    def _sub_tarjeta(self, titulo, color):
        """Crea una sub-sección con su título de color."""
        sub = tk.Frame(self.frame_resultado, bg=TARJETA)
        sub.pack(fill="x", padx=16, pady=(4, 2), anchor="n")
        tk.Label(sub, text=titulo, font=self.fuente_encab, bg=TARJETA,
                 fg=color, anchor="w").pack(fill="x", padx=2, pady=(6, 2))
        return sub

    def _mostrar_resultado(self, resultado):
        """Dibuja el resultado: clasificación, solución y verificación.
        El procedimiento se arma pero queda oculto hasta que el usuario
        pulse «Ver procedimiento»."""
        self._limpiar_resultado()
        self.boton_procedimiento.pack(side="right")

        clasificacion = resultado["clasificacion"]
        if clasificacion == "Consistente Determinado":
            color = EXITO
        elif clasificacion == "Consistente Indeterminado":
            color = ADVERTENCIA
        else:
            color = ERROR

        # ---- Clasificación del sistema ----
        sub = self._sub_tarjeta("CLASIFICACIÓN DEL SISTEMA", TEXTO_SUAVE)
        cartel = tk.Frame(sub, bg=color, padx=14, pady=10)
        cartel.pack(fill="x", pady=(0, 4))
        self._texto_ajustable(
            tk.Label(cartel, text=clasificacion.upper(),
                     font=self.fuente_cartel, bg=color, fg="#FFFFFF",
                     justify="left", anchor="w")).pack(fill="x")
        self._texto_ajustable(
            tk.Label(sub, text=resultado["descripcion"],
                     font=self.fuente_body, bg=TARJETA, fg=TEXTO,
                     justify="left", anchor="w")).pack(fill="x", padx=2,
                                                       pady=(0, 6))
        if resultado["homogeneo"]:
            self._texto_ajustable(
                tk.Label(sub,
                         text="Además es un sistema homogéneo: todos los "
                              "términos independientes son cero.",
                         font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                         justify="left", anchor="w")).pack(fill="x", padx=2,
                                                           pady=(0, 6))

        # ---- Solución ----
        if resultado["solucion"] is not None:
            sub2 = self._sub_tarjeta("SOLUCIÓN DEL SISTEMA", ACENTO)
            contenedor = tk.Frame(sub2, bg=FONDO, padx=12, pady=10)
            contenedor.pack(fill="x", pady=(0, 8))
            # Se arma una sola línea con todas las variables para que el
            # texto se acomode solo cuando hay muchas incógnitas.
            texto_solucion = "     ".join(
                f"x{indice+1} = {formato(valor)}"
                for indice, valor in enumerate(resultado["solucion"]))
            self._texto_ajustable(
                tk.Label(contenedor, text=texto_solucion,
                         font=self.fuente_big, bg=FONDO, fg=ACENTO,
                         justify="left", anchor="w")).pack(fill="x")
        elif clasificacion == "Consistente Indeterminado":
            sub2 = self._sub_tarjeta("VARIABLES LIBRES", ADVERTENCIA)
            libres = resultado["variables_libres"]
            nombres = "   ".join(f"x{c+1}" for c in libres)
            tk.Label(sub2, text="Infinitas soluciones, en función de:",
                     font=self.fuente_body, bg=TARJETA, fg=TEXTO_SUAVE,
                     anchor="w").pack(fill="x", padx=2)
            self._texto_ajustable(
                tk.Label(sub2, text=nombres, font=self.fuente_big,
                         bg=TARJETA, fg=ADVERTENCIA, justify="left",
                         anchor="w")).pack(fill="x", padx=2, pady=(4, 8))
        else:
            sub2 = self._sub_tarjeta("SIN SOLUCIÓN", ERROR)
            self._texto_ajustable(
                tk.Label(sub2,
                         text="El sistema es inconsistente: no existe "
                              "ningún valor de las variables que satisfaga "
                              "todas las ecuaciones a la vez.",
                         font=self.fuente_body, bg=TARJETA, fg=TEXTO,
                         justify="left", anchor="w")).pack(fill="x", padx=2,
                                                           pady=(0, 8))

        # ---- Verificación automática ----
        sub3 = self._sub_tarjeta("VERIFICACIÓN AUTOMÁTICA", EXITO)
        self._texto_ajustable(
            tk.Label(sub3, text=resultado["verificacion"],
                     font=self.fuente_mono, bg=TARJETA, fg=TEXTO,
                     justify="left", anchor="w")).pack(fill="x", padx=2,
                                                       pady=(0, 8))

        # ---- Procedimiento (oculto por omisión) ----
        self.sub_procedimiento = tk.Frame(self.frame_resultado, bg=TARJETA)
        tk.Label(self.sub_procedimiento,
                 text="PROCESO DE ELIMINACIÓN POR FILAS",
                 font=self.fuente_encab, bg=TARJETA, fg=TEXTO, anchor="w"
                 ).pack(fill="x", padx=2, pady=(6, 2))
        self._texto_ajustable(
            tk.Label(self.sub_procedimiento,
                     text="\n".join(resultado["pasos"]),
                     font=self.fuente_mono, bg=TARJETA, fg=TEXTO,
                     justify="left", anchor="w")).pack(fill="x", padx=2,
                                                       pady=(0, 10))

        self.procedimiento_visible = False
        self.boton_procedimiento.configure(text="Ver procedimiento")
        self.lienzo_resultado.yview_moveto(0)
        self.raiz.update_idletasks()
        self._ajustar_textos()

    def _alternar_procedimiento(self):
        """Muestra u oculta el bloque con el paso a paso."""
        if self.ultimo_resultado is None:
            return
        if self.procedimiento_visible:
            self.sub_procedimiento.pack_forget()
            self.boton_procedimiento.configure(text="Ver procedimiento")
            self.procedimiento_visible = False
        else:
            self.sub_procedimiento.pack(fill="x", padx=16, pady=(4, 2),
                                        anchor="n")
            self.boton_procedimiento.configure(text="Ocultar procedimiento")
            self.procedimiento_visible = True
        self.raiz.update_idletasks()
        self.lienzo_resultado.configure(
            scrollregion=self.lienzo_resultado.bbox("all"))

    # ------------------------------------------------------------------
    # Utilidades de ventana
    # ------------------------------------------------------------------
    def _centrar_ventana(self):
        """Centra la ventana en la pantalla."""
        self.raiz.update_idletasks()
        ancho = self.raiz.winfo_width()
        alto = self.raiz.winfo_height()
        x = max(0, (self.raiz.winfo_screenwidth() - ancho) // 2)
        y = max(0, (self.raiz.winfo_screenheight() - alto) // 2)
        self.raiz.geometry(f"+{x}+{y}")


# =====================================================================
# BLOQUE 7: PRUEBAS AUTOMÁTICAS DEL ALGORITMO
# Se ejecutan con:  python "Programa 1_Grupo2.py" --pruebas
# Comprueban que la clasificación y la solución son correctas en casos
# de los tres tipos, incluidos los ejercicios vistos en clase y varios
# casos límite.
# =====================================================================
def ejecutar_pruebas():
    """Recorre una lista de sistemas de prueba y compara el resultado
    obtenido con el esperado. Devuelve el número de fallos."""
    pruebas = [
        # (nombre, A, b, clasificación esperada, solución esperada)
        ("Caso 1 del informe: solución única",
         [[1, 1, 1], [2, -1, 1], [1, 2, -1]], [6, 3, 2],
         "Consistente Determinado", ["1", "2", "3"]),
        ("Caso 2 del informe: infinitas soluciones",
         [[1, 1, 1], [2, 2, 2]], [1, 2],
         "Consistente Indeterminado", None),
        ("Caso 3 del informe: sin solución",
         [[1, 1], [1, 1]], [1, 3],
         "Inconsistente", None),
        ("Ejemplo de la Sesión 2 (Lay)",
         [[1, -2, 1], [0, 2, -8], [-4, 5, 9]], [0, 8, -9],
         "Consistente Determinado", ["29", "16", "3"]),
        ("Actividad #1 de la Sesión 2",
         [[2, 3, 1], [5, 3, 4], [1, 1, -1]], [1, 2, 1],
         "Consistente Determinado", ["2/3", "0", "-1/3"]),
        ("Sistema inconsistente de la Sesión 2",
         [[0, 1, -4], [2, -3, 2], [5, -8, 7]], [8, 1, 1],
         "Inconsistente", None),
        ("Sistema de 5 variables con solución única",
         [[1, 2, 0, 1, 1], [0, 1, 1, 0, 0], [0, 0, 1, 1, -1],
          [0, 0, 0, 1, 2], [0, 0, 0, 0, 1]], [4, 2, 3, 5, 1],
         "Consistente Determinado", ["-2", "1", "1", "3", "1"]),
        ("Sistema homogéneo con infinitas soluciones",
         [[1, 1, 1], [2, -1, 0]], [0, 0],
         "Consistente Indeterminado", None),
        ("Matriz de ceros con términos nulos",
         [[0, 0], [0, 0]], [0, 0],
         "Consistente Indeterminado", None),
        ("Ecuación imposible 0 = 7",
         [[0]], [7], "Inconsistente", None),
        ("Necesita intercambio de filas",
         [[0, 1], [1, 0]], [2, 3],
         "Consistente Determinado", ["3", "2"]),
        ("Más ecuaciones que incógnitas, compatible",
         [[1, 0], [0, 1], [1, 1]], [1, 2, 3],
         "Consistente Determinado", ["1", "2"]),
        ("Más ecuaciones que incógnitas, incompatible",
         [[1, 0], [0, 1], [1, 1]], [1, 2, 4],
         "Inconsistente", None),
        ("Coeficientes fraccionarios",
         [["1/2", "1/3"], ["1/4", "1/5"]], [1, 1],
         "Consistente Determinado", ["-8", "15"]),
        ("Más incógnitas que ecuaciones",
         [[1, 2, 3]], [6], "Consistente Indeterminado", None),
    ]

    fallos = 0
    print("=" * 64)
    print("PRUEBAS AUTOMÁTICAS DEL ALGORITMO DE ELIMINACIÓN POR FILAS")
    print("=" * 64)

    for nombre, A, b, clasificacion_esperada, solucion_esperada in pruebas:
        A = [[a_numero(str(valor)) for valor in fila] for fila in A]
        b = [a_numero(str(valor)) for valor in b]
        resultado = resolver_sistema(len(A), len(A[0]), A, b)

        problemas = []
        if resultado["clasificacion"] != clasificacion_esperada:
            problemas.append(f"clasificó como {resultado['clasificacion']} "
                             f"y se esperaba {clasificacion_esperada}")
        if solucion_esperada is not None:
            obtenida = [formato(valor) for valor in resultado["solucion"]]
            if obtenida != solucion_esperada:
                problemas.append(f"solución {obtenida} en vez de "
                                 f"{solucion_esperada}")
        correcta, motivo = es_escalonada(resultado["escalonada"])
        if not correcta:
            problemas.append(f"la forma escalonada no es válida: {motivo}")
        if "FALLO" in resultado["verificacion"]:
            problemas.append("la verificación de la solución falló")

        if problemas:
            fallos += 1
            print(f"[FALLA] {nombre}")
            for problema in problemas:
                print(f"         - {problema}")
        else:
            print(f"[  OK  ] {nombre}")

    # Pruebas de lectura de números: ninguna debe tumbar el programa.
    print("-" * 64)
    entradas_validas = {"": "0", "3": "3", "-2": "-2", "2.5": "5/2",
                        "3/4": "3/4", "-1/2": "-1/2", " 7 ": "7"}
    for texto, esperado in entradas_validas.items():
        try:
            obtenido = formato(a_numero(texto))
        except Exception as error:
            fallos += 1
            print(f"[FALLA] a_numero({texto!r}) lanzó {error!r}")
            continue
        if obtenido != esperado:
            fallos += 1
            print(f"[FALLA] a_numero({texto!r}) dio {obtenido}, se esperaba "
                  f"{esperado}")
        else:
            print(f"[  OK  ] a_numero({texto!r}) = {obtenido}")

    entradas_invalidas = ["1/0", "abc", "3/", "/3", "1/2/3", "--3", "2/0"]
    for texto in entradas_invalidas:
        try:
            a_numero(texto)
        except ValueError:
            print(f"[  OK  ] a_numero({texto!r}) avisa del error, no falla")
        except Exception as error:
            fallos += 1
            print(f"[FALLA] a_numero({texto!r}) lanzó {type(error).__name__} "
                  f"en vez de un aviso controlado")
        else:
            fallos += 1
            print(f"[FALLA] a_numero({texto!r}) debió rechazarse")

    # ---- Pruebas del intérprete de ecuaciones ----
    print("-" * 64)
    sistemas_escritos = [
        ("Ejercicio de 5 variables de la Sesión 3",
         "x1 + 2x3 + x4 + 3x5 = 4\n"
         "x2 + x3 + 2x4 + x5 = 3\n"
         "2x1 + 4x3 + 2x4 + 6x5 = 8\n"
         "x1 + x2 + 3x3 + 3x4 + 4x5 = 7",
         ["x1", "x2", "x3", "x4", "x5"],
         [["1", "0", "2", "1", "3"], ["0", "1", "1", "2", "1"],
          ["2", "0", "4", "2", "6"], ["1", "1", "3", "3", "4"]],
         ["4", "3", "8", "7"]),
        ("Actividad #1 de la Sesión 2",
         "2x1 + 3x2 + x3 = 1\n5x1 + 3x2 + 4x3 = 2\nx1 + x2 - x3 = 1",
         ["x1", "x2", "x3"],
         [["2", "3", "1"], ["5", "3", "4"], ["1", "1", "-1"]],
         ["1", "2", "1"]),
        ("Variables con letras x, y, z",
         "2x - 3y + 2z = 1\nx + y = 0\nz = 5",
         ["x", "y", "z"],
         [["2", "-3", "2"], ["1", "1", "0"], ["0", "0", "1"]],
         ["1", "0", "5"]),
        ("Términos a ambos lados del igual",
         "4x1 - 5x2 + 2 = x1\nx2 = 2x1 - 6",
         ["x1", "x2"],
         [["3", "-5"], ["-2", "1"]],
         ["-2", "-6"]),
        ("Fracciones, decimales y subíndices",
         "1/2x₁ + 0.25x₂ = 1\n-3/4x₁ - x₂ = 2.5",
         ["x1", "x2"],
         [["1/2", "1/4"], ["-3/4", "-1"]],
         ["1", "5/2"]),
    ]

    for nombre, texto, vars_esperadas, A_esperada, b_esperada in sistemas_escritos:
        try:
            A, b, nombres = interpretar_ecuaciones(texto)
        except Exception as error:
            fallos += 1
            print(f"[FALLA] {nombre}: lanzó {type(error).__name__}: {error}")
            continue
        problemas = []
        if nombres != vars_esperadas:
            problemas.append(f"variables {nombres} en vez de {vars_esperadas}")
        obtenida = [[formato(valor) for valor in fila] for fila in A]
        if obtenida != A_esperada:
            problemas.append(f"matriz A {obtenida} en vez de {A_esperada}")
        obtenido_b = [formato(valor) for valor in b]
        if obtenido_b != b_esperada:
            problemas.append(f"vector b {obtenido_b} en vez de {b_esperada}")
        if problemas:
            fallos += 1
            print(f"[FALLA] {nombre}")
            for problema in problemas:
                print(f"         - {problema}")
        else:
            print(f"[  OK  ] {nombre}")

    sistemas_mal_escritos = [
        ("sin signo igual", "x1 + x2"),
        ("dos signos igual", "x1 = x2 = 3"),
        ("texto vacío", "   \n  "),
        ("sin variables", "3 + 2 = 5"),
        ("signo suelto", "x1 + = 3"),
        ("lado vacío", "= 3"),
        ("denominador cero", "1/0x1 = 3"),
    ]
    for nombre, texto in sistemas_mal_escritos:
        try:
            interpretar_ecuaciones(texto)
        except ValueError:
            print(f"[  OK  ] sistema con {nombre}: avisa del error, no falla")
        except Exception as error:
            fallos += 1
            print(f"[FALLA] sistema con {nombre}: lanzó "
                  f"{type(error).__name__} en vez de un aviso controlado")
        else:
            fallos += 1
            print(f"[FALLA] sistema con {nombre}: debió rechazarse")

    print("=" * 64)
    if fallos == 0:
        print("Todas las pruebas pasaron correctamente.")
    else:
        print(f"Se encontraron {fallos} fallo(s).")
    print("=" * 64)
    return fallos


# =====================================================================
# BLOQUE 8: PUNTO DE ENTRADA
# =====================================================================
def main():
    """Inicia la aplicación de escritorio, o las pruebas si se ejecuta
    con la opción --pruebas."""
    if "--pruebas" in sys.argv:
        sys.exit(1 if ejecutar_pruebas() else 0)

    raiz = tk.Tk()
    CalculadoraApp(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
