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
                # Si la cadena empieza y termina con "", no se separa.
                if linea[0] == '"' and linea[-1] == '"':
                    self.cad_s.append(linea.strip())
                    self.cads.append(linea.strip())
                else:
                    # Separar usando expresiones regulares para separar operadores y paréntesis
                    import re
                    # Expresión: separa números, identificadores y operadores/paréntesis
                    partes = re.findall(r'\d+|[a-zA-Z_]\w*|[()+\-*/]', linea.strip())
                    for cadena in partes:
                        self.cad_s.append(cadena)
                        self.cads.append(linea.strip())
                    self.t.extend(partes)
                    self.cads.extend(linea.strip())
                    self.cad_s.extend(partes)
        
        # print("self.t: ", self.t)
        # print("self.cad_s: ", self.cad_s)

        resultados_txt = self.simular_cadenas(diccionarios, iniciales, finales, resultado=[])

        #self.impresion_txt(resultados_txt) # Imprimiendo los resultados de la simulación de los archivos txt.

        resultados_res = self.simular_res()

        #self.impresion_res(resultados_res)
        
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
import re

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
                partes = re.findall(r"\\d+|[a-zA-Z_]\\w*|[()+\-*/]", linea)
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
                    print(f"Sintax error: {{cadena_copy}} line: {{line_num}}")
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
    ultima_vez_token = {{}}
    diccionario = {{}}
    for clave in tokens:
        ultima_vez_token[clave] = False
    for clave, lista in diccionario_cadenas.items():
        if len(lista) == 1:
            if lista[0] is True:
                print(f"Operador detectado: {{clave}}")
            elif lista[0] is False:
                # Find the line number for error reporting
                with open(archiv, "r", encoding="utf-8") as ar:
                    for line_num, linea in enumerate(ar, 1):
                        if clave in linea:
                            print(f"Sintax error: {{clave}} line: {{line_num}}")
        for i, valor in enumerate(lista):
            for s, (key, value) in enumerate(tabla.items()):
                if valor is True:
                    if i == s:
                        if key in tokens:
                            if clave in reservadas:
                                print(f"Palabra reservada: {{clave}}")
                                ultima_vez_reservada = True
                                ultima_vez_token[key] = False
                                ultima_vez_operador = False
                            elif key in operadores_reservados:
                                if not ultima_vez_operador:
                                    print(f"Operador reservado: {{clave}}")
                                    ultima_vez_operador = True
                                    ultima_vez_reservada = False
                                    ultima_vez_token[key] = False
                            else:
                                ultima_vez_operador = False
                                ultima_vez_reservada = False
                                ultima_vez_token[key] = True
                                diccionario[clave] = key
    new_dict = {{}}
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
"""
        with open(nombre, 'w', encoding='utf-8') as f:
            f.write(datas)
            
    def get_tokens_for_parser(self):
        """Devuelve los tokens válidos como tuplas (TOKEN_NAME, valor), listos para el parser."""
        resultado = []
        # Mapear el nombre del token al índice del AFD (por el orden en baja.yal)
        token_map = list(self.tabla.keys())
        print("token_map:", token_map)  # DEPURACIÓN
        for cadena, valores in self.diccionario_cadenas.items():
            print("cadena:", cadena, "valores:", valores)  # DEPURACIÓN
            try:
                idx = valores.index(True)
            except ValueError:
                continue
            # Usar el nombre del token real según la tabla, no self.tokens
            if idx < len(token_map):
                token_name = token_map[idx]
            else:
                continue  # Si no se reconoce, ignorar
            # Clasificación explícita
            if token_name in ("digits", "digit", "NUMERO"):
                resultado.append(("NUMERO", cadena))
            elif token_name == "number":
                resultado.append(("NÚMERO CON DECIMAL", cadena))
            elif token_name == "hexdigit":
                resultado.append(("NÚMERO HEXADECIMAL", cadena))
            elif token_name in ("id", "IDENTIFICADOR"):
                resultado.append(("IDENTIFICADOR", cadena))
            elif token_name == "WS":
                continue  # Ignorar espacios en blanco
            elif cadena == "+":
                resultado.append(("SUMA", cadena))
            elif cadena == "-":
                resultado.append(("RESTA", cadena))
            elif cadena == "*":
                resultado.append(("MULTIPLICACION", cadena))
            elif cadena == "/":
                resultado.append(("DIVISION", cadena))
            elif cadena == "(":
                resultado.append(("PARENTESIS_IZQUIERDO", cadena))
            elif cadena == ")":
                resultado.append(("PARENTESIS_DERECHO", cadena))
            elif cadena.upper() == "IF":
                resultado.append(("IF", cadena))
            elif cadena.upper() == "FOR":
                resultado.append(("FOR", cadena))
            elif cadena.upper() == "WHILE":
                resultado.append(("WHILE", cadena))
            elif token_name == "string":
                resultado.append(("STRING", cadena))
            else:
                resultado.append((token_name.upper(), cadena))
        return resultado
