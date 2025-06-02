class SimuladorTxT:

    def __init__(self, diccionarios, iniciales, finales, archivo, reservadas=[], operadores_reservados=[], tokens=[], tabla={}):
        self.diccionarios = diccionarios
        self.iniciales = iniciales
        self.finales = finales
        self.archivo = archivo
        self.reservadas = reservadas
        self.operadores_reservados = operadores_reservados
        self.tokens = tokens
        self.tabla = tabla
        if "digits" not in self.tokens:
            self.tokens.append("digits")
        self.diccionario_cadenas = {} # Diccionario para las cadenas.

        self.cadena_strings = [] # Lista para guardar los strings sin comas.

        self.reservadas = ["IF", "FOR", "WHILE", "ELSE"]

        # Quitando las palabras reservadas de los tokens.
        for palabra in self.reservadas:
            if palabra in self.tokens:
                self.tokens.remove(palabra)
        
        for i, token in enumerate(self.tokens):
            self.tokens[i] = token.replace('rule gettoken =\n', '').strip()

        print(self.tokens)
        # Cambiando cosas de la tabla.
        
        # Cambiando el signo negativo.
        new_m = "-"
        for key in self.tabla:
            if "~" in self.tabla[key]:
                value = self.tabla[key].replace("~", new_m)
                self.tabla[key] = value
        
        # Cambiando el signo positivo.
        new_m = "+"
        for key in self.tabla:
            if "@" in self.tabla[key]:
                value = self.tabla[key].replace("@", new_m)
                self.tabla[key] = value
        
        # Cambiando los delimitadores.

        # Espacio en blanco.
        new_m = " "
        for key in self.tabla:
            if "≡" in self.tabla[key]:
                value = self.tabla[key].replace("≡", new_m)
                self.tabla[key] = value
        
        # Tabulador.
        new_m = "\t"
        for key in self.tabla:
            if "¥" in self.tabla[key]:
                value = self.tabla[key].replace("¥", new_m)
                self.tabla[key] = value
        
        # Quiebre de línea.
        new_m = "\n"
        for key in self.tabla:
            if "§" in self.tabla[key]:
                value = self.tabla[key].replace("§", new_m)
                self.tabla[key] = value

        print("Tabla: ", self.tabla)

        # Juntando las listas de reservadas, operadores_reservado y tokens.
        self.lista = []
        self.lista.extend(self.reservadas)
        self.lista.extend(self.operadores_reservados)
        self.lista.extend(self.tokens)

        res_copy = self.reservadas.copy()

        #print("Palabras reservadas: ", self.reservadas)

        
        self.cad_s = [] # Arreglo para las cadenas a simular.
        self.t = []
        self.cads = []

        with open(self.archivo, "r") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if not linea:
                    continue
                # Si la cadena empieza y termina con "", no se separa.
                if linea[0] == '"' and linea[-1] == '"':
                    self.cad_s.append(linea)
                    self.cads.append(linea)
                else:
                    partes = separar_tokens(linea)
                    for cadena in partes:
                        self.cad_s.append(cadena)
                        self.cads.append(linea)
                    self.t.extend(partes)
        # print("self.t: ", self.t)
        # print("self.cad_s: ", self.cad_s)

        resultados_txt = self.simular_cadenas(diccionarios, iniciales, finales, resultado=[])
        resultados_res = self.simular_res()
        # Generando el archivo py. 
        self.archivopy = "implmentacion.py"
        print("Tokens: ", self.tokens)
        self.generar_py(self.archivopy, self.diccionarios, self.iniciales, self.finales, self.archivo, res_copy, self.operadores_reservados, self.tokens, self.tabla)

    def simular_cadenas(self, diccionarios, iniciales, finales, resultado=[]): # Simulando las cadenas que vienen en el archivo txt.

        if not diccionarios:
            #print("Resultado: ", resultado)
            return resultado
        
        # # Detectando los operadores.
        # if len(caracter_actual) == 1: # Detectando primero su longitud.
        #     if caracter_actual in self.operadores_reservados: # Detectando si es un operador.
        #         print("Operador detectado")
        #         return True, estado_actual


        if len(self.cad_s) == 0:
            # Si ya no quedan más cadenas por simular, se devuelve el resultado.
            #print("Resultado: ", resultado)
            return resultado
        else:

            #print("Cad_s", self.cad_s)

            # Se toma la primera cadena en la lista de cadenas.
            cadena_actual = self.cad_s.pop(0)

            # Sacando una copia de la cadena.
            self.cadena_copy = cadena_actual

            #print("Cadena actual: ", cadena_actual)

            # Si la cadena empieza y termina con comillas dobes, es porque es una cadena entera la que se debe simular.
            if cadena_actual[0] == '"' and cadena_actual[-1] == '"':
                #print("Cadena: ", cadena_actual)

                # Si la cadena empieza y termina con comiilas, entonces se simula todo de un solo, sin dividirlo.
                # Se quitan las comillas.
                cadena_actual = cadena_actual.replace('"', '')

                #print("Cadena actual: ", cadena_actual)

            # Se simula la cadena en cada diccionario en la lista de diccionarios.
            valores_cadena = []
            for i in range(len(diccionarios)):
                diccionario = diccionarios[i]
                estado_ini = iniciales[i]
                estados_acept = finales[i]
                estado_actual = estado_ini[0]
                

                # Detectando los operadores.
                if len(cadena_actual) == 1:
                    if cadena_actual in self.operadores_reservados:

                        #print("Cadena actual: ", cadena_actual)
                        #valores_cadena.append(True)

                        # Verificando que se haya llegado al último diccionario.
                        if i == len(diccionarios) - 1:
                            # Si se llegó al último diccionario, se agrega el valor a la lista de valores de la cadena actual.
                            valores_cadena.append(True)

                    else: 
                        
                        # Verificando que se haya llegado al último diccionario.
                        if i == len(diccionarios) - 1:
                            # Si se llegó al último diccionario, se agrega el valor a la lista de valores de la cadena actual.
                            valores_cadena.append(False)

                # Se simula la cadena en el diccionario actual.
                for j in range(len(cadena_actual) - 1):
                    caracter_actual = cadena_actual[j]
                    caracter_siguiente = cadena_actual[j+1]

                    #print("Estado actual: ", estado_actual)

                    v, estado_actual = self.simular_cadena(diccionario, estado_actual, caracter_actual, caracter_siguiente, estados_acept)

                    # Si hay un estado igual a {}, entonces regresarlo al inicial.
                    if estado_actual == {}:
                        estado_actual = estado_ini[0]
                        
                    if j == len(cadena_actual) - 2:
                        valores_cadena.append(v)

                    # Verificando si en la tabla está la definición de string.
            if 'string' in self.tabla: 
                
                # Si la cadena actual tenía " al principio y al final, entonces es string.
                if self.cadena_copy[0] == '"' and self.cadena_copy[-1] == '"':
                    
                    #print("Copia: ", self.cadena_copy)
                    self.cadena_strings.append(self.cadena_copy)

                    valores_cadena[-1] = True
                else:
                    valores_cadena[-1] = False

            # Verificando si hay un endline en la tabla y solo si tenemos al menos 9 valores.
            if 'endline' in self.tabla and len(valores_cadena) > 8:
                endline = self.tabla['endline']
                # Quitando los paréntesis al endline.
                endline = endline.replace('(', '').replace(')', '')

                # Índices 7 y 8
                if valores_cadena[7] and valores_cadena[8]:
                    pass
                elif not valores_cadena[7] and not valores_cadena[8]:
                    pass
                elif not valores_cadena[7] and valores_cadena[8]:
                    if cadena_actual in self.reservadas:
                        pass
                    else:
                        # Poner todos los valores a False
                        for k in range(len(valores_cadena)):
                            valores_cadena[k] = False
                        
            # Guardando la cadena y sus resultados en un diccionario.
            self.diccionario_cadenas[cadena_actual] = valores_cadena

            # Se agrega la lista de valores de la cadena actual al resultado.
            resultado.append(valores_cadena)

            #print("Cadena: ", cadena_actual, "resultados: ", valores_cadena)

            # Verificando si hay un true en la lista de valores cadena.
            if True in valores_cadena:
                pass
            else:
                # Buscando el número de línea en donde se encuentra la cadena actual en el archivo.
                with open(self.archivo, "r") as archivos:
                    for i, linea in enumerate(archivos):
                        if cadena_actual in linea:
                            print("Sintax error: " + cadena_actual + " line: ", i+1)

            # if cadena_actual in self.reservadas:
            #     # Si la cadena actual es una palabra reservada, se agrega a la lista de resultados.
            #     print("Palabra reservada", cadena_actual)
            #     #resultado.append(True)
            #     #print("Cadena: ", cadena_actual, "resultados: ", True)

            # Se llama recursivamente a la función con las listas actualizadas.
            return self.simular_cadenas(diccionarios, iniciales, finales, resultado)
    
    def simular_res(self):
        # Variables de seguimiento.
        ultima_vez_operador = False
        ultima_vez_reservada = False
        ultima_vez_token = {}

        diccionario = {}

        for clave in self.tokens:
            ultima_vez_token[clave] = False
        
        print(self.tokens)

        for clave in self.diccionario_cadenas:
            lista = self.diccionario_cadenas[clave]

            # Detectando los errores.
            if len(lista) == 1:
                if lista[0] == True:
                    print("Operador detectado")
                
                elif lista[0] == False:
                    # Abriendo el archivo para buscar el caracter.
                    with open(self.archivo, "r") as ar:
                        for a, linea in enumerate(ar):
                            if clave in linea:
                                print("Sintax error: " + clave + " line: ", a+1)
            
            for i, valor in enumerate(lista):

                # BUscando el token en la tabla de símbolos definida.
                for s, (key, value) in enumerate(self.tabla.items()):

                    if valor == True:

                        if i == s:
                            # En el caso de los tokens encontrados, imprime el último que se encontró de cada uno.
                            if key in self.tokens:
                                if clave in self.reservadas:
                                    # Si la cadena actual es una palabra reservada, se agrega a la lista de resultados.
                                    print("Palabra reservada: ", clave)
                                    ultima_vez_reservada = True
                                    ultima_vez_token[key] = False
                                    ultima_vez_operador = False
                                
                                elif key in self.operadores_reservados:

                                    if not ultima_vez_operador:
                                        print("Operador reservado: ", clave)
                                        ultima_vez_operador = True
                                        ultima_vez_reservada = False
                                        ultima_vez_token[key] = False
                                else: 

                                    ultima_vez_operador = False
                                    ultima_vez_reservada = False
                                    ultima_vez_token[key] = True

                                    diccionario[clave] = key

        #print("Diccionario: ", diccionario)    
        
            #print("Cadena strings: ", self.cadena_strings)

        new_dict =  {}

        for k, v in diccionario.items():
            if not isinstance(v, bool):
                new_dict[k] = v
        
        # Imprimiendo los tokens encontrados.
        for keys, value in new_dict.items():


            if value == "string":
                
                #print("S: ", self.cadena_strings)

                string2 = self.cadena_strings.pop()

                comillas = 0
                palabra = ''
                for c in string2:
                    if c == '"':
                        comillas += 1
                        if comillas == 2:
                            print('"' + palabra.strip() + '"' + " type: " + value)
                            palabra = ''
                            comillas = 0
                    else:
                        palabra += c
                if palabra:
                    print('"' + palabra.strip() + '"')

                #print("Token: \"" + keys + "\" type: " + value)
            else: 
                print("Token: " + keys + " type: " + value)
        
        #print("New_dict: ", new_dict)

        # if len(self.cadena_strings) > 0:

        #     print("Copia: ", self.cadena_strings)

        #     # Sacar antes una copia de lo que hay adentro.
        #     cadena_stringss = self.cadena_strings.copy()

        #     self.cadena_strings = [x.strip('"') for x in self.cadena_strings]
        #     result = ', '.join(self.cadena_strings).split('" ')
        #     print(cadena_stringss)
        #     print(result)

        #     print(result.pop())

        #strs = []

        # keys_to_modify = [key for key, value in new_dict.items() if value == 'string']

        # # Iterar sobre la lista de claves para modificar el diccionario
        # for key in keys_to_modify:
        #     new_dict['"' + key + '"'] = new_dict.pop(key)
            
        # print(new_dict)

            # Imprimiendo los tokens encontrados.
            #print("Tokens encontrados: ", diccionario)

            #print(diccionario)

            # # Imprimiendo el diccionario llave por llave.
            # for keys, value in diccionario.items():

            #     if value == "string":
            #         print("Token: \"" + keys + "\" type: " + value)
            #     else:
            #         print("Token: " + keys + " type: " + value)

    def simular_cadena(self, diccionario, estado_actual, caracter_actual, caracter_siguiente, estados_acept):

        #print("Caracter: ", caracter_actual)

        #print("Estados de aceptación: ", estados_acept)

        transiciones = diccionario[estado_actual]

        #print("Transiciones; ", transiciones)

        # print("Caracter actual: ", caracter_actual)
    
        if caracter_actual in transiciones:
            estado_siguiente = transiciones[caracter_actual]

            #print("Estado siguiente: ", estado_siguiente)

            if estado_siguiente in estados_acept:
                #print("Cadena aceptada.")
                return True, estado_actual
            
            # if estado_actual in estados_acept:
            #     print("Cadena aceptada.")
            #     return True, estado_actual

            if estado_siguiente == {}:

                #print("Falso en caracter actual", estado_siguiente)
                # print("Estado actual: ", estado_actual)
                # print("Estado siguiente: ", estado_siguiente)

                return False, estado_actual
            
            elif estado_siguiente in estados_acept:
                #print("Cadena aceptada.")
                return True, estado_actual
        
            else:

                #print("Estado: ",estado_actual, estado_actual in estados_acept)

                # Si el estado siguiente es vacío.
                return True, estado_siguiente
            
        elif caracter_siguiente in transiciones:

            # Si no hay transición para el caracter actual, pero sí para el siguiente.
            estado_siguiente = transiciones[caracter_siguiente]

            if estado_siguiente in estados_acept:
                #print("Cadena aceptada.")
                return True, estado_siguiente

            if estado_siguiente == {}:
                
                #print("Falso en caracter siguiente", estado_siguiente)

                # Si el estado siguiente no es vacío.
                return False, estado_siguiente
            
            elif estado_siguiente in estados_acept:
                #print("Cadena aceptada.")
                return True, estado_siguiente
        
            else:
                #print("Estado: ", estado_siguiente)
                #print("Estado: ", estado_siguiente in estados_acept)
                # Si el estado siguiente es vacío.
                return True, estado_siguiente
        
        elif caracter_actual not in transiciones:

            return False, estado_actual
            
        else:
    
            #print("Estado actual: ", estado_actual, transiciones)

            if transiciones != {}:
                # Si no hay transición para el caracter actual ni para el siguiente.
                return True, estado_actual
            
            else: 
            
                # Si no hay transición para el caracter actual ni para el siguiente.
                return False, estado_actual

    # Generando el archivo .py.
    def generar_py(self, nombre, diccionarios, iniciales, finales, archivo, reservadas, operadores_reservados, tokens, tabla):
        """
        Genera un archivo Python autocontenible para simular el análisis léxico y sintáctico.
        Incluye todas las variables necesarias y asegura que no haya problemas de alcance o variables indefinidas.
        """
        datas = f"""

# Variables necesarias para la simulación

diccionarios = {diccionarios}
iniciales = {iniciales}
finales = {finales}
archiv = {repr(archivo)}
reservadas = {reservadas}
operadores_reservados = {operadores_reservados}
tokens = {tokens}
tabla = {tabla}
diccionario_cadenas = {{}}
cadena_strings = []
vacio = {{}}
vacio2 = {{}}

# Función para dividir líneas

def dividir_linea(linea):
    operadores = ['(', ')', '*', '+', '-', '/']
    partes = []
    palabra = ''

    for caracter in linea:
        if caracter.isalnum() or caracter == '_':
            palabra += caracter
        elif caracter in operadores:
            if palabra:
                partes.append(palabra)
                palabra = ''
            partes.append(caracter)
        else:
            if palabra:
                partes.append(palabra)
                palabra = ''

    if palabra:
        partes.append(palabra)

    return partes

# Función principal

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
                partes = dividir_linea(linea)
                for cadena in partes:
                    cad_s.append(cadena)
                    cads.append(linea)
                t.extend(partes)
    simular_cadenas(diccionarios, cad_s, iniciales, finales)
    simular_res()

"""
        with open(nombre, 'w', encoding='utf-8') as f:
            f.write(datas)
            
    def get_tokens_for_parser(self):
        """
        Devuelve los tokens válidos como tuplas (TOKEN_NAME, valor), agrupados por línea.
        Retorna: [[(TOKEN_NAME, valor), ...], ...]  # Una sublista por línea
        """
        resultado = []
        token_map = list(self.tabla.keys())
        # Leer el archivo de entrada para obtener las líneas originales
        with open(self.archivo, "r", encoding="utf-8") as f:
            lineas = [line.rstrip('\n') for line in f]
        # Para cada línea, genera su lista de tokens
        for linea in lineas:
            if not linea.strip() or linea.strip().startswith("//"):
                resultado.append([])
                continue  # Ignora líneas vacías o comentarios
            tokens_linea = []
            partes = separar_tokens(linea.strip())
            for cadena in partes:
                valores = self.diccionario_cadenas.get(cadena, [])
                token_name = None
                for idx, v in enumerate(valores):
                    if v is True and idx < len(token_map):
                        token_name = token_map[idx]
                        break
                # --- Ajuste robusto para identificadores y números ---
                if cadena.isdigit():
                    tokens_linea.append(("NUMERO", cadena))
                elif (token_name is not None and token_name.lower() in ("id", "identificador")) or (token_name is None and (cadena.isalpha() or (cadena and cadena[0].isalpha() and all(c.isalnum() or c == '_' for c in cadena)))):
                    tokens_linea.append(("IDENTIFICADOR", cadena))
                elif token_name == "number":
                    tokens_linea.append(("NÚMERO CON DECIMAL", cadena))
                elif token_name == "hexdigit":
                    tokens_linea.append(("NÚMERO HEXADECIMAL", cadena))
                elif token_name == "WS":
                    continue
                elif cadena == "+":
                    tokens_linea.append(("SUMA", cadena))
                elif cadena == "-":
                    tokens_linea.append(("RESTA", cadena))
                elif cadena == "*":
                    tokens_linea.append(("MULTIPLICACION", cadena))
                elif cadena == "/":
                    tokens_linea.append(("DIVISION", cadena))
                elif cadena == "(":
                    tokens_linea.append(("PARENTESIS_IZQUIERDO", cadena))
                elif cadena == ")":
                    tokens_linea.append(("PARENTESIS_DERECHO", cadena))
                elif cadena.upper() == "IF":
                    tokens_linea.append(("IF", cadena))
                elif cadena.upper() == "FOR":
                    tokens_linea.append(("FOR", cadena))
                elif cadena.upper() == "WHILE":
                    tokens_linea.append(("WHILE", cadena))
                elif token_name == "string":
                    tokens_linea.append(("STRING", cadena))
                elif token_name is not None and token_name.lower() == "digit":
                    # Si el token_name es 'digit' pero la cadena no es numérica, tratar de identificar si es identificador
                    if cadena and cadena[0].isalpha() and all(c.isalnum() or c == '_' for c in cadena):
                        tokens_linea.append(("IDENTIFICADOR", cadena))
                    else:
                        tokens_linea.append(("ERROR", cadena))
                elif token_name is None:
                    tokens_linea.append(("ERROR", cadena))
                else:
                    tokens_linea.append((token_name.upper(), cadena))
            resultado.append(tokens_linea)
        print("Tokens enviados al parser:", resultado)
        return resultado

def separar_tokens(linea):
    """
    Separa una línea en tokens: números, identificadores, operadores y paréntesis.
    No usa la librería re.
    """
    tokens = []
    i = 0
    while i < len(linea):
        c = linea[i]
        # Ignorar espacios
        if c.isspace():
            i += 1
            continue
        # Números (soporta secuencias como 123, pero también separa bien en 1-2, 6/9, (5+2))
        if c.isdigit():
            num = c
            i += 1
            while i < len(linea) and linea[i].isdigit():
                num += linea[i]
                i += 1
            tokens.append(num)
            continue
        # Identificadores (letra o _ seguido de letras, dígitos o _)
        if c.isalpha() or c == "_":
            ident = c
            i += 1
            while i < len(linea) and (linea[i].isalnum() or linea[i] == "_"):
                ident += linea[i]
                i += 1
            tokens.append(ident)
            continue
        # Operadores y paréntesis (uno por uno)
        if c in "+-*/()":
            tokens.append(c)
            i += 1
            continue
        # Si no es nada de lo anterior, solo avanza
        i += 1
    return tokens
