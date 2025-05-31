"""
Archivo que se encargará de convertir el autómata finito no determinista a un autómata finito determinista.
"""
from EstadoAFD import *
from TransicionesAFD import *
import graphviz as gv

class AFD:

    def __init__(self, alfabeto, automata, transiciones, diccionario):
        self.alfabeto = alfabeto
        self.automata = automata
        self.transiciones = transiciones
        self.diccionario = diccionario
        self.estado_num = 0
        self.trans_AFD = []
        self.estados_Finales = []
        self.estados_FinalesE = []
        self.estados_AFD = []

        # Listas para guardar los estados en su forma de integer.
        self.estados_AFD_in = []
        self.estados_Finales_I = []
        self.estado_inicial_I = []
        self.diccionario_estados_I = {}
        self.diccionario_transiciones_I = {}

        self.estadoInicial = []
        self.dict = []
        self.estado_inicial = []
        self.diccionario_estados = {}

        # AFD minimizado.
        self.diccionario_m = {}
        self.finales_m = []
        self.estados_m = []
        self.inicial_m = []

        self.conversion()
        self.graficar()
        self.simular()
        self.minimizar()

    def conversion(self): # Método para convertir el AFD a AFD.
        # Imprimiendo los datos del autómata.

        #print("Estado inicial del autómata: ", self.automata)
        #print(self.diccionario)

        temp = [] # Lista temporal para el estado inicial.

        temp.append(self.automata.estado_inicial) # Agregando el estado inicial a la lista temporal.

        self.estado_inicial = self.eclosure(temp) # Calculand el estado inicial del autómata.

        #print(type(self.estado_inicial))

        #print("Estado inicial: ", estado_inicial) # Imprimiendo el estado inicial.

        #print(estado_inicial) # Imprimiendo el estado inicial.

        estdos_AFD = [self.estado_inicial] # Creando la lista de estados_AFD y guardando su primer estado.
        
        #trans_AFD = [] # Creando la tabla de transición de los estados.

        estados_a_revisar = [self.estado_inicial] # Creando la lista de estados a revisar.

        #print("Estados a revisar: ", estados_a_revisar)

        while len(estados_a_revisar) > 0:
            estado_actual_AFD = estados_a_revisar.pop(0) # Sacando el último estado de la lista de estados a revisar.

            #print("Estado actual AFD: ", estado_actual_AFD)
            transiciones_act = {} # Transiciones actuales.

            for simbolo in self.alfabeto: # Recorriendo el alfabeto.


                # Lista para los estados alcanzables.
                estados_alcanzables = []

                # Enviando el estado actual y el símbolo actual para calcular el move.
                res = self.move(estado_actual_AFD, simbolo)

                estadoo = self.eclosure(res)

                estados_alcanzables.append(estadoo)
                
                if len(estados_alcanzables) > 0: 
                    for estad in estados_alcanzables: # Recorriendo los estados alcanzables y guardándolos en los estados del AFD.
                        if estad not in estdos_AFD:
                            estdos_AFD.append(estad)
                            estados_a_revisar.append(estad)
                    
                    # Guardando las transiciones actuales con el símbolo actual.
                    transiciones_act[simbolo] = estad
                
            #print("Transiciones: ", transiciones_act)

            #print("Estado actual: ", estado_actual_AFD, "transiciones: ", transiciones_act)

            #print("Estados AFD: ", estdos_AFD)
    
            # Recorriendo las transiciones actuales.
            for simboloo, estado_ll in transiciones_act.items():
                #print("Estado actual: ", estado_actual_AFD, "Simbolo: ", simboloo, "Estado: ", estado_ll)
                
                # Si el estado actual y el estado de llegada están vacíos, entonces no se incluyen.
                if estado_actual_AFD == []:
                    continue


                # Creando la transición del AFD.
                trans = TransicionesAFD(estado_actual_AFD, simboloo, estado_ll)

                self.trans_AFD.append(trans)

        # # Quitando el estado trampa.
        # for estadoAFD in estdos_AFD:
        #     # Si el esatdo está vacío, entonces se quita.
        #     if estadoAFD == []:
        #         estdos_AFD.remove(estadoAFD)
    

        # Eliminando el estado vacío.
        #print("Estados del AFD convertido: ", estdos_AFD)
        for est in estdos_AFD:
            if est == []:
                estdos_AFD.remove(est) 

        # print("Estados del AFD: ", estdos_AFD)
        
        # for trans in self.trans_AFD:
        #     print("Transición: ", trans)

        # Creando un diccionario para guardar los estados con sus etiquetas.
        #diccionario_estados = {}

        # Recorriendo los estados del AFD.
        for estado in estdos_AFD:
            #print("Estado: ", estado)

            # Dando una etiqueta al estado.
            #etiqueta = "q" + str(self.estado_num)
            etiqueta = self.estado_num
            self.estado_num += 1

            # Guardando el estado con su etiqueta.
            self.diccionario_estados[etiqueta] = estado
        
        #print("Diccionario de estados: ", self.diccionario_estados)

        #print("Diccionario de estados: ", diccionario_estados)

        # Cambiando los estados del AFD por sus etiquetas en la tabla de transiciones.
        for transion in self.trans_AFD:
            for etiqueta, estado in self.diccionario_estados.items():
                if transion.estadoInicial == estado:
                    transion.estadoInicial = etiqueta
                
                if transion.estadoFinal == estado:
                    transion.estadoFinal = etiqueta


        #print("Transiciones: ", self.trans_AFD)

        #print("Estados del AFD: ", estdos_AFD)
        #print("Diccionario estados: ", self.diccionario_estados)

        # Colocándole a los estados del AFD una etiqueta numérica.
        id = 0
        for estado in estdos_AFD:
            for etiqueta, estad in self.diccionario_estados.items():
                if estado == estad:
                    self.estados_AFD_in.append(id)
                    id += 1
        
        # Guardando los estados finales del AFD con su etiqueta numérica.
        id2 = 0
        # Identificando los estados finales del AFD.
        for estado in estdos_AFD:
            if self.automata.estado_final in estado:
                # Guardando el índice del estado.
                # Obtener el índice del estado final en la lista.
                indice = estdos_AFD.index(estado)
                self.estados_Finales_I.append(indice)

        # Guardando el id numérico de cada estado en otro diccionario.
        for estado in estdos_AFD:
            for etiqueta, estad in self.diccionario_estados.items():
                if estado == estad:
                    self.diccionario_estados_I[etiqueta] = id2
                    id2 += 1
        
        #print("DiccionarioI ", self.diccionario_estados_I)
        
        # print("Estados int: ", self.estados_AFD_in)
        # print("Finales int: ", self.estados_Finales_I)
        # Creando diccionario de transiciones con su etiqueta numérica.

        # Guardando el estado inicial del AFD con su etiqueta numérica.
        for estado in estdos_AFD:
            if estado == self.estado_inicial:
                # Guardando el índice del estado inicial.
                indice = estdos_AFD.index(estado)
                self.estado_inicial_I.append(indice)
        
        # Identificando los estados finales del AFD.
        for estado in estdos_AFD:
            if self.automata.estado_final in estado:
                self.estados_Finales.append(estado)

        # Etiqutando los estados finales del AFD.
        for estadoss in self.estados_Finales:
            for etiqueta, estadso in self.diccionario_estados.items():
                if estadoss == estadso:
                    self.estados_FinalesE.append(etiqueta)

        # Guardando los estados etiquetados en una lista.
        for estado in estdos_AFD:
            for etiqueta, estad in self.diccionario_estados.items():
                if estado == estad:
                    self.estados_AFD.append(etiqueta)

        # Guardando el estado inicial del AFD.
        for estado in estdos_AFD:
            if estado == self.estado_inicial:
                # Buscando la etiqueta del estado inicial.
                for etiqueta, estadd in self.diccionario_estados.items():
                    if estado == estadd:
                        self.estado_inicial_AFD = etiqueta
        

        # # Cambiando el estado de llegada por su etiqueta.
        # for transicion in self.trans_AFD:
        #     for etiqueta, estado in self.diccionario_estados.items():
        #         #print("Estado: ", estado)
        #         print("Transiciones: ", transicion)
        #return self.trans_AFD

    def move(self, estado, simbolo): # Método para calcular el move del estado.
        # Lista para los estados alcanzables.

        resultado = []

        #print("Diccionario del AFN: ", self.diccionario)

        # Recorriendo los estados del estado actual del AFD.
        for est in estado:
            # Verificando si el estado tiene transiciones con el símbolo actual.
            if est in self.diccionario:
                # Si tiene transiciones con el símbolo actual, se agregan a la lista de estados alcanzables.
                for transicion in self.diccionario[est]:
                    if transicion[0] == simbolo:
                        # Guardando los estados en la lista de estados alcanzables.
                        resultado.append(transicion[1])

        return resultado

    def eclosure(self, estado): #Método para calcular el cierre epsilon de un estado.
        
        # Lista para el resultado.
        resultado = []

        # Stack para realizar el procedimiento.
        pila = []

        for est in estado:
            pila.append(est)


            while len(pila) > 0: 
                # Sacando el último elemento de la pila.
                estado = pila.pop()

                # Si el estado no está en el resultado, se agrega.
                if estado not in resultado:
                    #print("Estado: ", estado)
                    resultado.append(estado)
                else: 
                    continue

                # Verificando si el estado tiene transiciones epsilon.
                if estado in self.diccionario:
                    # Si tiene transiciones epsilon, se agregan a la pila.
                    for transicion in self.diccionario[estado]:
                        #print(transicion[0])

                        if transicion[0] == "ε":
                            #print("Sí hay transiciones epsilon.")
                            pila.append(transicion[1])


        # # Ordenando el resultado.
        # resultado.sort()
        
        #print("Resultado: ", resultado)

        # Retornando el resultado.
        return resultado
    
    def simular(self): # Método para simular.
        """
        
        self.trans_AFD = []
        self.estados_Finales = []
        self.estados_FinalesE = []
        self.estados_AFD = []

        # Listas para guardar los estados en su forma de integer.
        self.estados_AFD_in = []
        self.estados_Finales_I = []
        self.estado_inicial_I = []
        self.diccionario_estados_I = {}
        self.diccionario_transiciones_I = {}

        self.estadoInicial = []
        self.dict = []
        self.estado_inicial = []
        self.diccionario_estados = {}
        
        
        """
        #print("Transiciones del AFD: ", self.trans_AFD)

        # for trans in self.trans_AFD:
        #     print(trans)

        temp = {}

        # Convertir la lista de transiciones a un diccionario.
        for i in self.trans_AFD:
            # Guardando la transición en un diccionario.
            temp[i.estadoInicial, i.simbolo] = i.estadoFinal
        
        #print("Diccionario local: ", temp)

        nuevo_diccionario = {}

        for clave, valor in temp.items():
            estado_act, simbolo = clave
            estado_sig = valor

            if estado_act not in nuevo_diccionario:
                nuevo_diccionario[estado_act] = {}
            
            nuevo_diccionario[estado_act][simbolo] = estado_sig

            # Si el estado llega a [], quitar la transición.
            if nuevo_diccionario[estado_act][simbolo] == []:
                nuevo_diccionario[estado_act].pop(simbolo)

        # print("Nuevo diccionario: ", nuevo_diccionario)

        # # Guardando el alfabeto.
        # print("Alfabeto: ", self.alfabeto)

        estado_I = None

        # Obteniendo el estado inicial de su lista.
        for estado in self.estado_inicial_I:
            estado_I = estado

        
        #print("Estado inicial del AFD: ", estado_I, " estado finaL: ", self.estados_Finales_I)

        # Simulando el AFD.
        cadena = input("Ingrese la cadena a simular: ")

        estado_actual = estado_I

        # Recorriendo la cadena.
        for simbolo in cadena: 
            # Verificando si el símbolo está en el alfabeto.
            if simbolo not in self.alfabeto:
                print("La cadena no pertenece al lenguaje.")
                break
            
            print("Diccionario: ", nuevo_diccionario)

            # Obteniendo el estado siguiente.
            if simbolo in nuevo_diccionario[estado_actual]:
                
                estado_actual = nuevo_diccionario[estado_actual][simbolo]
            else: 
                print("La cadena no es aceptada")
                break

        if estado_actual in self.estados_Finales_I:
            print("Cadena aceptada por el AFN2AFD")
        else: 
            print("Cadena rechazada por el AFN2AFD")
    
    def minimizar(self): # Método para minimizar el AFD construído.
        #print("Minimización")

        #print("Diccionario del AFD: ", self.diccionario)

        # # Diccionario local para hacer un cambio de formato.
        # diccionario_local = {}
        # for state, transitions_list in self.diccionario.items():
        #     diccionario_local[state] = {}
        #     for symbol, next_state in transitions_list:
        
        #         diccionario_local[state][symbol] = next_state

        #print("Diccionario local: ", diccionario_local)

        #temp = {}  

        # for transiion in self.trans_AFD:
            
        #     print("Transiciones", transiion)

        #     # Cambiando las transiciones a un diccionario.
        #     temp[transiion.estadoInicial] = (transiion.simbolo, transiion.estadoFinal)

        #print("Temp: ", temp)

        #print("Nuevo diccionario: ", diccionario_local)

        # Convirtiendo la lista de estados en un diccionario.
        diccionario_estados = {}

        for i in self.trans_AFD:
            if i.estadoInicial in diccionario_estados:
                diccionario_estados[i.estadoInicial].append((i.simbolo, i.estadoFinal))
            else: 
                diccionario_estados[i.estadoInicial] = [(i.simbolo, i.estadoFinal)]


        #print("Diccionario: ", diccionario_estados)

        diccionario = {}

        for estado, transiciones in diccionario_estados.items():
            diccionario[estado] = {}
            for simbolo, destino in transiciones:
                diccionario[estado][simbolo] = destino


        """
        Variables en uso: 

        self.estados_AFD_in = estados del AFD.
        self.estados_Finales_I = estados finales del AFD.
        self.estado_inicial_I = estado inicial del AFD.
        diccionario = diccionario del AFD.

        """

        # print("Diccionario de transiciones: ", diccionario)
        # print("Estados del AFD: ", self.estados_AFD_in)
        # print("Estados finales del AFD: ", self.estados_Finales_I)
        # print("Estado inicial del AFD: ", self.estado_inicial_I)


        """
        Dividiendo los estados en dos listas: 
        Q = estados de no aceptación.
        F = estados de aceptación.        
        """

        Q = []
        F = []

        #print("Estados del AFD: ", self.estados_AFD_in)

        

        # Haaciendo una lista de listas para guardar las particiones.
        particiones = [[s for s in self.estados_AFD_in if s in self.estados_Finales_I], 
                       [s for s in self.estados_AFD_in if s not in self.estados_Finales_I]]

        #print("Particiones: ", particiones)

        def buscar_particion(estado):
            # Función para buscar la partición de un estado.
            for i, partition in enumerate(particiones):
                if estado in partition:
                    return i
            
        
        itera = True # Variable para controlar el ciclo while.
        
        #print("Diccionario: ", diccionario)

        while itera: 
            new_partitions = [] # Lista para guardar las nuevas particiones.
            for partition in particiones:
                #Creando un diccionario de estados equivalentes.
                equivalent_states = {}
                for state in partition:
                    #print("Diccionario: ", diccionario)
                    transiciones = [diccionario[state][symbol] for symbol in self.alfabeto]

                    #print("Transiciones: ", transiciones)

                    # Quitando las parejas que llegan a {}.
                    #transiciones = [t for t in transiciones if t != {}]

                    #print("Transiciones en la línea 407: ", transiciones)

                    # Si hay una transición vacía en transiciones, continuar,
                    # de lo contrario, buscar la partición del estado destino.

                    lista_sin_vacios = list(filter(lambda x: x != [], transiciones))

                    #print("Transiciones:", lista_sin_vacios)

                    equivalent_states.setdefault(tuple(lista_sin_vacios), []).append(state)

                # Dividiendo la partición en nuevas particiones, de ser posible.
                subpartitions = list(equivalent_states.values())
                if len(subpartitions) > 0:
                    new_partitions.extend(subpartitions)
                else: 
                    new_partitions.append(partition)
                
                # Si no se han creado nuevas particiones, el proceso termina.
                #print("Particiones: ", particiones)
                
                # Pasando la lista de particiones a una lista de listas por cada estado.
                particione = []
                for particion in new_partitions:
                    particione.append([estado for estado in particion])
            
                if new_partitions == particione:
                    itera = False             

                particiones = new_partitions # Guardando las particiones finales.

                # Guardando el estado inicial.
                for i, partition in enumerate(particiones):
                    if self.estado_inicial_I in partition:
                        self.estado_inicial_I = i
                
                #print("Estado inicial del AFD minimizado: ", self.estado_inicial_I)
                for es in self.estado_inicial_I:
                    self.inicial_m.append(es)

        # Construyendo el AFD minimizado.
        new_states = [tuple(partition) for partition in particiones]

        #print("New states: ", new_states)

        new_transitions = {} #Transiciones nuevas.

        for est in self.estados_AFD_in:
            particion = buscar_particion(est)

            # BUscando las transiciones de cada estado.
            for simbolo in self.alfabeto: 
                llegada = diccionario[est][simbolo]

                # Si la llegada es vacía, entonces continuar.
                if llegada == []:
                    continue

                new = tuple(sorted([buscar_particion(llegada)]))


                new_transitions[(new_states[particion], simbolo)] = new_states[new[0]]


        # Buscando la partición y el estado final en las particiones.
        new_finals = []

        for estadoA in self.estados_Finales_I:
            final = buscar_particion(estadoA)

            new_finals.append(new_states[final])

        # Sacando de la partición el estado o estados de aceptación.
    



        # for estadoA in self.estados_Finales_I: 
        #     final = buscar_particion(estadoA)

        #     print("Final: ", final, "estadoA: ", estadoA)

        #     #print("New states: ", new_states)

        #     new_finals.append(new_states[final])

        new_initial = []

        for estadoB in self.inicial_m:
            inicial = buscar_particion(estadoB)

            new_initial.append(new_states[inicial])

        #print("New initial: ", new_initial)
        
        #print("New finals: ", new_finals)
        """
        old_dict: new_transitions.
        new_dict: final_trasitions.
        """


        # Ir corriendo el estado final hasta el último índice de los new_states.
        for tupla in new_states:
            #print("Tupla: ", tupla)

            #print("New finals: ", new_finals, " new states: ", new_states)

            # Si la tupla está en new_finals, correrlo hasta el final.
            if tupla in new_finals:
                #print("Si llegué")
                #print("Tupla: ", tupla)
                indice = new_states.index(tupla)
                #print("Índice: ", indice)
                new_states.append(new_states.pop(indice))
            else: 
                continue

        # Creando un diccionario con los nuevos estados y sus íd's nuevos.
        new_dict = {}

        for i, tupla in enumerate(new_states):
            #print("Id: ", i)

            new_dict[tupla] = i
        

        # # Imprimiendo el diccionario de transiciones.
        #print("New transitions en afd converter: ", new_transitions)
        #print("New dict: ", new_dict)

        #diccionario_n = {}

        print("New transitions: ", new_transitions)
        print("New finals: ", new_finals)

        for tupla, valor in new_transitions.items():
            #print("Tupla[0]: ", tupla[0], "valor: ", valor)


            self.diccionario_m[(new_dict[tupla[0]], tupla[1])] = new_dict[valor]

            # # Guardando el estado final en otra variable.
            # if tupla[0] in new_finals or valor in new_finals:
            #     #print("Valor: ", valor)

            #     self.finales_m.append(new_dict[tupla[0]])
            #     self.finales_m.append(new_dict[valor])
            
            # #if tupla[0] in new_initial or valor in new_initial:
            #     #print("Tupla en inicial: ", valor)
            #     #self.inicial_m.append(new_dict[valor])
            #     #self.inicial_m.append(new_dict[tupla[0]])
            
            # # Obteniendo el estado inicial del AFD.
            # if tupla[0] in new_initial:
            #     self.inicial_m.append(new_dict[tupla[0]])


            #print("new_dict[valor]: ", new_dict[valor])

            #print("Diccionario: ", self.diccionario_m)

            self.estados_m.append(new_dict[valor])
            self.estados_m.append(new_dict[tupla[0]])

            # Si la tupla está en el new_finals, entonces se agrega.
            if tupla[0] in new_finals:
                print("New finals: ", new_finals)
                self.finales_m.append(new_dict[tupla[0]])
            

        for estado in new_states: 
            if estado in new_finals:
                self.finales_m.append(new_dict[estado])



        self.finales_m = list(set(self.finales_m)) # Quitando repeticiones.
        self.inicial_m = list(set(self.inicial_m)) # Quitando repeticiones.
        self.estados_m = list(set(self.estados_m)) # Quitando repeticiones.

        #print("Estados: ", self.estados_m)
        
        # Guardando el estado inicial.
        #self.inicial_m = new_dict[self.inicial_m]
        # print("Iniciales: ", self.inicial_m)
        # print("Finales: ", self.finales_m)

        # for ini in self.inicial_m:
        #     print(type(ini))
        


        # Diccionario temporal.
        diccionario_temp = {}

        for clave, valor in self.diccionario_m.items():
            if clave[0] not in diccionario_temp:
                diccionario_temp[clave[0]] = {}
            diccionario_temp[clave[0]][clave[1]] = valor
        
        self.diccionario_m = diccionario_temp.copy()
        
        #print("Diccionario temporal: ", diccionario_temp)
        #original_dict = {0: {'a': 1, 'b': 0}, 1: {'a': 1, 'b': 2}, 2: {'a': 1, 'b': 3}, 3: {'a': 1, 'b': 0}}
        
        new_t = {} # Cambios

        for key, value in self.diccionario_m.items():
            new_t[key] = [(k, v) for k, v in value.items()]
            
        #print(new_t)

        self.diccionario_m =new_t.copy() 

        # print("Diccionario minimizado: ", self.diccionario_m)
        # print("Estados del AFD minimizado: ", self.estados_m)
        #print("Estados finales del AFD minimizado: ", self.finales_m)

        self.simularAFD_min() # Simulando el AFD minimizado.
  

        """
        Estructuras a usar: 
        self.diccionario_m = diccionario minimizado.
        self.estados_m = estados del diccionario minimizado.
        self.finales = estados finales del AFD minimizado.
        self.alfabeto = alfabeto del AFD.
        """

        #print("New transitions. ", self.diccionario_m)

        # Graficando el diccionario.
        grafo = gv.Digraph(comment="AFN2AFD_Minimizado", format="png")

        # Colocando título.
        grafo.node('title', 'AFN2AFD: Minimizado', shape='none')

        for key, value in self.diccionario_m.items():

            for simbolo, estado in value:
                grafo.edge(str(key), str(estado), label=simbolo)
        
        # Dibujando los estados.
        for estado in self.estados_m:
            
            #print("Estado: ", estado, "Finales: ", self.finales_m, "Iniciales: ", self.inicial_m)

            if estado in self.finales_m:
                
                #print("Llegué al final: ", estado)
                grafo.node(str(estado), str(estado), shape="doublecircle")
            
            elif estado in self.inicial_m:


                grafo.node(str(estado), str(estado), shape="circle", color="green")
            
            else:
            
                grafo.node(str(estado), str(estado), shape="circle")

        # Colocando el autómta de manera horizontal.
        grafo.graph_attr['rankdir'] = 'LR'

        grafo.render('AFN2AFD_min', view=True) # Dibujando el grafo.
    
    def simularAFD_min(self): # Simulando el AFD minimizado.
        
        #estadoI = self.inicial_m.pop(0)

        # print("Diccionario del AFD minimizado: ", self.diccionario_m)
        # print("Estados del AFD minimizado: ", self.estados_m)
        # print("Estados finales del AFD minimizado: ", self.finales_m)
        # print("Estado inicial del AFD minimizado: ", estadoI)
        # print("Alfabeto del AFD minimizado: ", self.alfabeto)

        # Quitando los estados trampa de la lista de estados.
        for estado in self.estados_m:
            # Verificando que los estados no tengan transiciones.
            if estado not in self.diccionario_m:
                self.estados_m.remove(estado)

            # Si el estado era inicial, cambiarlo por el que le sigue.
            if estado in self.inicial_m:
                self.inicial_m.pop(estado)
            self.inicial_m.append(self.estados_m[0])

        print("Estados: ", self.estados_m)
        print("Estado inicial: ", self.inicial_m)

        nuevo_dict_m = {} # Diccionario para representar el diccionario de las transiciones.

        for clave, valor in self.diccionario_m.items():
            estado_act = clave
            transiciones = {}

            # Creando el diccionario para las transiciones del estado actual.
            for simbolo, estado_sig in valor:
                transiciones[simbolo] = estado_sig
            
            nuevo_dict_m[estado_act] = transiciones

       # print("Nuevo diccionario", nuevo_dict_m)

        # Simulando el AFD minimizado.
        cadena = input("Ingrese la cadena a evaluar: ")
        estado_actual = self.inicial_m.pop()

        print("Nuevo diccionario: ", nuevo_dict_m)
        print("Estado inicial: ", estado_actual)

        for simbolo in cadena:
            if simbolo not in self.alfabeto:
                print("El símbolo ", simbolo, " no pertenece al alfabeto.")
                break
            
            # print("Nuevo diccionario: ", nuevo_dict_m)
            # print("Estado inicial: ", estado_actual)


            if simbolo in nuevo_dict_m[estado_actual]:
                estado_actual = nuevo_dict_m[estado_actual][simbolo]
                print("Estado en evaluación: ", estado_act)
            else:
                continue

        if estado_actual in self.finales_m:
            print("Cadena aceptada por el AFN2AFD_min.")
        else:
            print("Cadena rechazada por el AFN2AFD_min")


    def graficar(self, grafo_padre=None):  # Método para dibujar el AFD (individual o como parte de un supergrafo)

        # Usar subgrafo si se proporciona un grafo padre
        nombre_cluster = f"cluster_{self.nombre if hasattr(self, 'nombre') else 'AFD'}"
        grafo = grafo_padre.subgraph(name=nombre_cluster) if grafo_padre else gv.Digraph(comment=f"AFD_{self.nombre}", format="png")

        grafo.attr(label=f"AFN2AFD: {self.nombre if hasattr(self, 'nombre') else 'AFD'}")
        grafo.graph_attr['rankdir'] = 'LR'  # Colocar el autómata horizontal

        estados = self.estados_AFD
        diccionario_estados = {}

        # Construir transiciones por estado
        for i in self.trans_AFD:
            if i.estadoInicial in diccionario_estados:
                diccionario_estados[i.estadoInicial].append((i.simbolo, i.estadoFinal))
            else:
                diccionario_estados[i.estadoInicial] = [(i.simbolo, i.estadoFinal)]

        # Dibujar transiciones
        for key, value in diccionario_estados.items():
            for simbolo, estado in value:
                if estado == []:
                    continue
                grafo.edge(str(key), str(estado), label=simbolo)

        # Dibujar nodos del AFD
        for estado in estados:
            attrs = {"shape": "circle"}
            if estado in self.estados_FinalesE:
                attrs["shape"] = "doublecircle"
            if estado == self.estado_inicial_AFD:
                attrs["color"] = "green"
            grafo.node(str(estado), str(estado), **attrs)

        # Si no es parte de un grafo padre, renderiza solo este AFD
        if grafo_padre is None:
            grafo.render(f"afd_{self.nombre if hasattr(self, 'nombre') else 'AFD'}", view=True)