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
                    # Eliminando saltos de línea y separando las cadenas.
                    cadenas = linea.strip().split()
                    # Agregando las cadenas a la lista global cad_s.
                    for cadena in cadenas:
                        if cadena[0] == '"' and cadena[-1] == '"':
                            self.cad_s.append(cadena.strip())
                            self.cads.append(linea.strip())
                        else:
                            self.cad_s.extend(cadena.split())
                            self.cads.append(linea.strip())
                    # Agregando los tokens a la lista global tokens.
                    self.t.extend(cadenas)

                    self.cads.extend(linea.strip())

                    # Regresar las cadenas separadas a self.cad_s.
                    self.cad_s.extend(cadenas)
        
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

            # Imprime los tokens encontrados.
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

        # print(diccionarios)
        # print(iniciales)
        # print(finales)
        # print(archivo)
        # print(reservadas)
        vacio = {}
        diccionario_cadenas = {}
        vacio2 = {}
        cadena_strings = []
    

        datas = f"""
diccionarios = {'{}'}
iniciales = {'{}'}
finales = {'{}'}
archiv = {'{}'}
reservadas = {'{}'}
vacio = {'{}'}
operadores_reservados = {'{}'}
tokens = {'{}'}
tabla = {'{}'}
diccionario_cadenas = {'{}'}
vacio2 = {'{}'}
cadena_strings = {'{}'}
    
def main():
    
    # Juntando la lista de reservadas, operadores_reservados y tokens.
    lista = []
    lista.extend(reservadas)
    lista.extend(operadores_reservados)
    lista.extend(tokens)

    res_copy = reservadas.copy()
    
    cad_s = [] # Arreglo para las cadenas a simular.
    t = []
    cads = []


    with open(archiv, "r") as archivo:
        for linea in archivo:
            # Si la cadena empieza y termina con "", no se separa.
            if linea[0] == '"' and linea[-1] == '"':
                cad_s.append(linea.strip())
                cads.append(linea.strip())
            else:
                # Eliminando saltos de línea y separando las cadenas.
                cadenas = linea.strip().split()
                # Agregando las cadenas a la lista global cad_s.
                for cadena in cadenas:
                    if cadena[0] == '"' and cadena[-1] == '"':
                        cad_s.append(cadena.strip())
                        cads.append(linea.strip())
                    else:
                        cad_s.extend(cadena.split())
                        cads.append(linea.strip())
                # Agregando los tokens a la lista global tokens.
                t.extend(cadenas)

                cads.extend(linea.strip())

                # Regresar las cadenas separadas a self.cad_s.
                cad_s.extend(cadenas)
    
    simular_cadenas(diccionarios, cad_s, iniciales, finales) # Simulando las cadenas del txt.

    simular_res() # Haciendo otras cosas.
    
    #print("Listas: ", cad_s, t, cads)

# Método para simular las cadenas.
def simular_cadenas(diccionarios, cad_s, iniciales, finales, resultado=[]):
    
    if not diccionarios:
        return resultado
    
    if len(cad_s) == 0:
        # Si ya no quedan más cadenas por simular, se devuelve el resultado.
        return resultado
    else: 

        # Se toma la primera cadena en la lista de cadenas.
        cadena_actual = cad_s.pop(0)

        #print("Cadena actual ", cadena_actual)

        # Sacando una copia de la cadena.
        cadena_copy = cadena_actual
        
        # Si la cadena empieza y termina con comillas dobes, es porque es una cadena entera la que se debe simular.
        if cadena_actual[0] == '"' and cadena_actual[-1] == '"':
            # Si la cadena empieza y termina con comiilas, entonces se simula todo de un solo, sin dividirlo.
            # Se quitan las comillas.
            cadena_actual = cadena_actual.replace('"', '')

        
        valores_cadena = []
        for i in range(len(diccionarios)):
            diccionario = diccionarios[i]
            estado_ini = iniciales[i]
            estados_acept = finales[i]
            estado_actual = estado_ini[0]

            if len(cadena_actual) == 1:
                
                # Detectando los operadores.
                if cadena_actual in operadores_reservados:
                    
                    if i == len(diccionarios) - 1:
                        valores_cadena.append(True)
                
                else:

                    # Verificando que se haya llegado al último diccionario.
                    if i == len(diccionarios) - 1:
                        valores_cadena.append(False)
            
            # Se simula la cadena en el diccionario actual.
            for j in range(len(cadena_actual) - 1):
                caracter_actual = cadena_actual[j]
                caracter_siguiente = cadena_actual[j+1]

                v, estado_actual = simular_cadena(diccionario, estado_actual, caracter_actual, caracter_siguiente, estados_acept)
                
                #print("v: ", v, "estado_actual: ", estado_actual)
                #print(valores_cadena)

                # Si hay un estado igual a vacío, entonces regresarlo al inicial.
                if estado_actual == vacio:
                    estado_actual = estado_ini[0]
                
                if j == len(cadena_actual) - 2:
                    valores_cadena.append(v)
        
        # Verificando si en la tabla está la definición de string.
        if 'string' in tabla: 
            
            # Si la cadena actual tenía " al principio y al final, entonces es string.
            if cadena_copy[0] == '"' and cadena_copy[-1] == '"':
                
                cadena_strings.append(cadena_copy)

                valores_cadena[-1] = True
            else:
                valores_cadena[-1] = False
        
        # Verificando si hay un endline en la tabla.
        if 'endline' in tabla:
            endline = tabla['endline']

            # Quitando los paréntesis al endline.
            endline = endline.replace('(', '')
            endline = endline.replace(')', '')

            # 8 y 9.
            if valores_cadena[7] == True and valores_cadena[8] == True:
                pass
            elif valores_cadena[7] == False and valores_cadena[8] == False:
                pass
            elif valores_cadena[7] == False and valores_cadena[8] == True:

                if cadena_actual in reservadas: # Si la cadena es reservada, entonces no pasa nada. 
                    pass
                
                else:
                    for i in range(len(valores_cadena)):
                        valores_cadena[i] == False
        
        # Guardando la cadena y sus resultados en un diccionario.
        diccionario_cadenas[cadena_actual] = valores_cadena

        # Se agrega la lista de valores de la cadena actual al resultado.
        resultado.append(valores_cadena)

        # Verificando si hay un true en la lista de valores cadena.
        if True in valores_cadena:
            pass
        else: 
            with open(archiv, "r") as ar:
                for a, linea in enumerate(ar):
                    if cadena_actual in linea:
                        print("Sintax error: " + cadena_actual + " line: ", a+1)


    #print("Resultado: ", diccionario_cadenas)
    return simular_cadenas(diccionarios, cad_s, iniciales, finales, resultado) # Recursión.


def simular_cadena(diccionario, estado_actual, caracter_actual, caracter_siguiente, estados_acept):
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

        if estado_siguiente == vacio:

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

        if estado_siguiente == vacio:
            
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

        if transiciones != vacio:
            # Si no hay transición para el caracter actual ni para el siguiente.
            return True, estado_actual
        
        else: 
        
            # Si no hay transición para el caracter actual ni para el siguiente.
            return False, estado_actual

def simular_res(): # Simulando otras cosas.

    # Variables de seguimiento.
    ultima_vez_operador = False
    ultima_vez_reservada = False
    ultima_vez_token = vacio

    diccionario = vacio

    for clave in tokens:
        ultima_vez_token[clave] = False
    
    print(diccionario_cadenas)

    for clave in diccionario_cadenas:
        lista = diccionario_cadenas[clave]

        # Detectando los errores.
        if len(lista) == 1:
            if lista[0] == True:
                print("Operador detectado")
            
            elif lista[0] == False:
                # Abriendo el archivo para buscar el caracter.
                with open(archiv, "r") as ar:
                    for a, linea in enumerate(ar):
                        if clave in linea:
                            print("Sintax error: " + clave + " line: ", a+1)
        
        for i, valor in enumerate(lista):

            # BUscando el token en la tabla de símbolos definida.
            for s, (key, value) in enumerate(tabla.items()):

                if valor == True:

                    if i == s:
                        # En el caso de los tokens encontrados, imprime el último que se encontró de cada uno.
                        if key in tokens:
                            if clave in reservadas:
                                # Si la cadena actual es una palabra reservada, se agrega a la lista de resultados.
                                print("Palabra reservada: ", clave)
                                ultima_vez_reservada = True
                                ultima_vez_token[key] = False
                                ultima_vez_operador = False
                            
                            elif key in operadores_reservados:

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

    print("Diccionario: ", diccionario)    
    
    new_dict =  vacio2

    for k, v in diccionario.items():
        if not isinstance(v, bool):
            new_dict[k] = v
    
    print("Diccionario: ", new_dict)
    
    # Imprimiendo los tokens encontrados.
    for keys, value in new_dict.items():


        if value == "string":
            #print("Token: "" + keys + "" type: " + value)

            string2 = cadena_strings.pop()

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

        else: 
            print("Token: " + keys + " type: " + value)
                

if __name__ == "__main__":
    main()

""".format(diccionarios, iniciales, finales, str('"{}"'.format(archivo)), reservadas, vacio, operadores_reservados, tokens, tabla, diccionario_cadenas, vacio2, cadena_strings)
        
        with open(nombre, 'w', encoding='utf-8') as f:
            f.write(datas)