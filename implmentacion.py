
import re

diccionarios = [{0: {' ': 1, '\t': 1, '\n': 1}, 1: {' ': {}, '\t': {}, '\n': {}}}, {0: {' ': 1, '\t': 1, '\n': 1}, 1: {' ': 1, '\t': 1, '\n': 1}}, {0: {'0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1}, 1: {'0': {}, '1': {}, '2': {}, '3': {}, '4': {}, '5': {}, '6': {}, '7': {}, '8': {}, '9': {}}}, {0: {'0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1}, 1: {'0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1}}, {0: {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'h': 1, 'i': 1, 'j': 1, 'k': 1, 'l': 1, 'm': 1, 'n': 1, 'o': 1, 'p': 1, 'q': 1, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 1, 'w': 1, 'x': 1, 'y': 1, 'z': 1, 'A': 1, 'B': 1, 'C': 1, 'D': 1, 'E': 1, 'F': 1, 'G': 1, 'H': 1, 'I': 1, 'J': 1, 'K': 1, 'L': 1, 'M': 1, 'N': 1, 'O': 1, 'P': 1, 'Q': 1, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 1, 'W': 1, 'X': 1, 'Y': 1, 'Z': 1}, 1: {'a': {}, 'b': {}, 'c': {}, 'd': {}, 'e': {}, 'f': {}, 'g': {}, 'h': {}, 'i': {}, 'j': {}, 'k': {}, 'l': {}, 'm': {}, 'n': {}, 'o': {}, 'p': {}, 'q': {}, 'r': {}, 's': {}, 't': {}, 'u': {}, 'v': {}, 'w': {}, 'x': {}, 'y': {}, 'z': {}, 'A': {}, 'B': {}, 'C': {}, 'D': {}, 'E': {}, 'F': {}, 'G': {}, 'H': {}, 'I': {}, 'J': {}, 'K': {}, 'L': {}, 'M': {}, 'N': {}, 'O': {}, 'P': {}, 'Q': {}, 'R': {}, 'S': {}, 'T': {}, 'U': {}, 'V': {}, 'W': {}, 'X': {}, 'Y': {}, 'Z': {}}}, {0: {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'h': 1, 'i': 1, 'j': 1, 'k': 1, 'l': 1, 'm': 1, 'n': 1, 'o': 1, 'p': 1, 'q': 1, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 1, 'w': 1, 'x': 1, 'y': 1, 'z': 1, 'A': 1, 'B': 1, 'C': 1, 'D': 1, 'E': 1, 'F': 1, 'G': 1, 'H': 1, 'I': 1, 'J': 1, 'K': 1, 'L': 1, 'M': 1, 'N': 1, 'O': 1, 'P': 1, 'Q': 1, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 1, 'W': 1, 'X': 1, 'Y': 1, 'Z': 1, ' ': {}, '0': {}, '1': {}, '2': {}, '3': {}, '4': {}, '5': {}, '6': {}, '7': {}, '8': {}, '9': {}}, 1: {'a': 2, 'b': 2, 'c': 2, 'd': 2, 'e': 2, 'f': 2, 'g': 2, 'h': 2, 'i': 2, 'j': 2, 'k': 2, 'l': 2, 'm': 2, 'n': 2, 'o': 2, 'p': 2, 'q': 2, 'r': 2, 's': 2, 't': 2, 'u': 2, 'v': 2, 'w': 2, 'x': 2, 'y': 2, 'z': 2, 'A': 2, 'B': 2, 'C': 2, 'D': 2, 'E': 2, 'F': 2, 'G': 2, 'H': 2, 'I': 2, 'J': 2, 'K': 2, 'L': 2, 'M': 2, 'N': 2, 'O': 2, 'P': 2, 'Q': 2, 'R': 2, 'S': 2, 'T': 2, 'U': 2, 'V': 2, 'W': 2, 'X': 2, 'Y': 2, 'Z': 2, ' ': 3, '0': {}, '1': {}, '2': {}, '3': {}, '4': {}, '5': {}, '6': {}, '7': {}, '8': {}, '9': {}}, 2: {'a': {}, 'b': {}, 'c': {}, 'd': {}, 'e': {}, 'f': {}, 'g': {}, 'h': {}, 'i': {}, 'j': {}, 'k': {}, 'l': {}, 'm': {}, 'n': {}, 'o': {}, 'p': {}, 'q': {}, 'r': {}, 's': {}, 't': {}, 'u': {}, 'v': {}, 'w': {}, 'x': {}, 'y': {}, 'z': {}, 'A': {}, 'B': {}, 'C': {}, 'D': {}, 'E': {}, 'F': {}, 'G': {}, 'H': {}, 'I': {}, 'J': {}, 'K': {}, 'L': {}, 'M': {}, 'N': {}, 'O': {}, 'P': {}, 'Q': {}, 'R': {}, 'S': {}, 'T': {}, 'U': {}, 'V': {}, 'W': {}, 'X': {}, 'Y': {}, 'Z': {}, ' ': 1, '0': {}, '1': {}, '2': {}, '3': {}, '4': {}, '5': {}, '6': {}, '7': {}, '8': {}, '9': {}}, 3: {'a': {}, 'b': {}, 'c': {}, 'd': {}, 'e': {}, 'f': {}, 'g': {}, 'h': {}, 'i': {}, 'j': {}, 'k': {}, 'l': {}, 'm': {}, 'n': {}, 'o': {}, 'p': {}, 'q': {}, 'r': {}, 's': {}, 't': {}, 'u': {}, 'v': {}, 'w': {}, 'x': {}, 'y': {}, 'z': {}, 'A': {}, 'B': {}, 'C': {}, 'D': {}, 'E': {}, 'F': {}, 'G': {}, 'H': {}, 'I': {}, 'J': {}, 'K': {}, 'L': {}, 'M': {}, 'N': {}, 'O': {}, 'P': {}, 'Q': {}, 'R': {}, 'S': {}, 'T': {}, 'U': {}, 'V': {}, 'W': {}, 'X': {}, 'Y': {}, 'Z': {}, ' ': {}, '0': 4, '1': 4, '2': 4, '3': 4, '4': 4, '5': 4, '6': 4, '7': 4, '8': 4, '9': 4}, 4: {'a': 2, 'b': 2, 'c': 2, 'd': 2, 'e': 2, 'f': 2, 'g': 2, 'h': 2, 'i': 2, 'j': 2, 'k': 2, 'l': 2, 'm': 2, 'n': 2, 'o': 2, 'p': 2, 'q': 2, 'r': 2, 's': 2, 't': 2, 'u': 2, 'v': 2, 'w': 2, 'x': 2, 'y': 2, 'z': 2, 'A': 2, 'B': 2, 'C': 2, 'D': 2, 'E': 2, 'F': 2, 'G': 2, 'H': 2, 'I': 2, 'J': 2, 'K': 2, 'L': 2, 'M': 2, 'N': 2, 'O': 2, 'P': 2, 'Q': 2, 'R': 2, 'S': 2, 'T': 2, 'U': 2, 'V': 2, 'W': 2, 'X': 2, 'Y': 2, 'Z': 2, ' ': 3, '0': 4, '1': 4, '2': 4, '3': 4, '4': 4, '5': 4, '6': 4, '7': 4, '8': 4, '9': 4}}]
iniciales = [[0], [0], [0], [0], [0], [0]]
finales = [[1], [1], [1], [1], [1], [1, 4]]
archiv = 'C:/Users/jquez/Desktop/2025/Compis/Compiladores/baja.txt'
reservadas = ['IF', 'FOR', 'WHILE', 'ELSE']
operadores_reservados = ['(', ')', '*', '+', '-', '/']
tokens = ['digits', 'id', 'ws']
tabla = {'delim': '( |\t|\n)', 'ws': '( |\t|\n)( |\t|\n)*', 'digit': '(0|1|2|3|4|5|6|7|8|9)', 'digits': '(0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*', 'letter': '(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)', 'id': '(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)((a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z) | (0|1|2|3|4|5|6|7|8|9)(0|1|2|3|4|5|6|7|8|9)*)*'}
diccionario_cadenas = {}
cadena_strings = []
vacio = {}
vacio2 = {}

def main():
    lista = []
    lista.extend(reservadas)
    lista.extend(operadores_reservados)
    lista.extend(tokens)
    res_copy = reservadas.copy()
    cad_s = []
    t = []
    cads = []
    with open(archiv, "r", encoding="utf-8") as archivo:
        for line_num, linea in enumerate(archivo, 1):
            linea = linea.strip()
            if not linea:
                continue
            if linea[0] == '"' and linea[-1] == '"':
                cad_s.append(linea)
                cads.append(linea)
            else:
                partes = re.findall(r"\d+|[a-zA-Z_]\w*|[()+\-*/]", linea)
                for cadena in partes:
                    cad_s.append(cadena)
                    cads.append(linea)
                t.extend(partes)
    simular_cadenas(diccionarios, cad_s, iniciales, finales)
    simular_res()

def simular_cadenas(diccionarios, cad_s, iniciales, finales, resultado=None):
    if resultado is None:
        resultado = []
    if not diccionarios or len(cad_s) == 0:
        return resultado
    cadena_actual = cad_s.pop(0)
    cadena_copy = cadena_actual
    if cadena_actual[0] == '"' and cadena_actual[-1] == '"':
        cadena_actual = cadena_actual.replace('"', '')
    valores_cadena = []
    for i in range(len(diccionarios)):
        diccionario = diccionarios[i]
        estado_ini = iniciales[i]
        estados_acept = finales[i]
        estado_actual = estado_ini[0]
        if len(cadena_actual) == 1:
            if cadena_actual in operadores_reservados:
                if i == len(diccionarios) - 1:
                    valores_cadena.append(True)
            else:
                if i == len(diccionarios) - 1:
                    valores_cadena.append(False)
        for j in range(len(cadena_actual) - 1):
            caracter_actual = cadena_actual[j]
            caracter_siguiente = cadena_actual[j+1]
            v, estado_actual = simular_cadena(diccionario, estado_actual, caracter_actual, caracter_siguiente, estados_acept)
            if estado_actual == vacio:
                estado_actual = estado_ini[0]
            if j == len(cadena_actual) - 2:
                valores_cadena.append(v)
    if 'string' in tabla:
        if cadena_copy[0] == '"' and cadena_copy[-1] == '"':
            cadena_strings.append(cadena_copy)
            if valores_cadena:
                valores_cadena[-1] = True
        else:
            if valores_cadena:
                valores_cadena[-1] = False
    if 'endline' in tabla and len(valores_cadena) > 8:
        endline = tabla['endline'].replace('(', '').replace(')', '')
        if valores_cadena[7] and valores_cadena[8]:
            pass
        elif not valores_cadena[7] and not valores_cadena[8]:
            pass
        elif not valores_cadena[7] and valores_cadena[8]:
            if cadena_actual in reservadas:
                pass
            else:
                for k in range(len(valores_cadena)):
                    valores_cadena[k] = False
    diccionario_cadenas[cadena_copy] = valores_cadena
    resultado.append(valores_cadena)
    if True not in valores_cadena:
        # Find the line number for error reporting
        with open(archiv, "r", encoding="utf-8") as ar:
            for line_num, linea in enumerate(ar, 1):
                if cadena_copy in linea:
                    print(f"Sintax error: {cadena_copy} line: {line_num}")
    return simular_cadenas(diccionarios, cad_s, iniciales, finales, resultado)

def simular_cadena(diccionario, estado_actual, caracter_actual, caracter_siguiente, estados_acept):
    transiciones = diccionario[estado_actual]
    if caracter_actual in transiciones:
        estado_siguiente = transiciones[caracter_actual]
        if estado_siguiente in estados_acept:
            return True, estado_actual
        if estado_siguiente == vacio:
            return False, estado_actual
        elif estado_siguiente in estados_acept:
            return True, estado_actual
        else:
            return True, estado_siguiente
    elif caracter_siguiente in transiciones:
        estado_siguiente = transiciones[caracter_siguiente]
        if estado_siguiente in estados_acept:
            return True, estado_siguiente
        if estado_siguiente == vacio:
            return False, estado_siguiente
        elif estado_siguiente in estados_acept:
            return True, estado_siguiente
        else:
            return True, estado_siguiente
    elif caracter_actual not in transiciones:
        return False, estado_actual
    else:
        if transiciones != vacio:
            return True, estado_actual
        else:
            return False, estado_actual

def simular_res():
    ultima_vez_operador = False
    ultima_vez_reservada = False
    ultima_vez_token = {}
    diccionario = {}
    for clave in tokens:
        ultima_vez_token[clave] = False
    for clave, lista in diccionario_cadenas.items():
        if len(lista) == 1:
            if lista[0] is True:
                print(f"Operador detectado: {clave}")
            elif lista[0] is False:
                # Find the line number for error reporting
                with open(archiv, "r", encoding="utf-8") as ar:
                    for line_num, linea in enumerate(ar, 1):
                        if clave in linea:
                            print(f"Sintax error: {clave} line: {line_num}")
        for i, valor in enumerate(lista):
            for s, (key, value) in enumerate(tabla.items()):
                if valor is True:
                    if i == s:
                        if key in tokens:
                            if clave in reservadas:
                                print(f"Palabra reservada: {clave}")
                                ultima_vez_reservada = True
                                ultima_vez_token[key] = False
                                ultima_vez_operador = False
                            elif key in operadores_reservados:
                                if not ultima_vez_operador:
                                    print(f"Operador reservado: {clave}")
                                    ultima_vez_operador = True
                                    ultima_vez_reservada = False
                                    ultima_vez_token[key] = False
                            else:
                                ultima_vez_operador = False
                                ultima_vez_reservada = False
                                ultima_vez_token[key] = True
                                diccionario[clave] = key
    new_dict = {}
    for k, v in diccionario.items():
        if not isinstance(v, bool):
            new_dict[k] = v
    for keys, value in new_dict.items():
        if value == "string":
            if cadena_strings:
                string2 = cadena_strings.pop()
                comillas = 0
                palabra = ''
                for c in string2:
                    if c == '"':
                        comillas += 1
                        if comillas == 2:
                            print('"' + palabra.strip() + '" type: ' + value)
                            palabra = ''
                            comillas = 0
                    else:
                        palabra += c
                if palabra:
                    print('"' + palabra.strip() + '"')
        else:
            print("Token: " + str(keys) + " type: " + str(value))

if __name__ == "__main__":
    main()
