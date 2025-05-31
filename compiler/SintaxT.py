"""
Clase para la conversión de un regex a AFD.
"""
from NodoA import *
from EstadoAFD import *
import graphviz as gv
#$from hopcroft import *

class SintaxT:

    def __init__(self, regex, alfabeth): # Se recibe la expresión regular para luego convertirla a AFD.
        self.regex = regex
        self.alfabeth = alfabeth
        self.contador = 1 # Contador de los estados.
        self.followpos = [] # Lista para guardar los followpos.
        self.followposT = []
        self.leaves = dict()
        self.estadosAFD = [] # Lista con los estados a utilizar.
        self.EstadosAceptAFD = [] # Lista con los estados finales a utilizar.
        self.EstadoInicial = None # Estado inicial del AFD.
        self.transiciones = [] # Lista para guaradar las transiciones del AFD final.
        self.estadosAFD_dict = [] # Diccionario para graficar.
        self.terminal = None
        self.DTtrans = {}
        self.dict = {} #Diccionario.

        self.aumento() # Se le agrega un # al final de la expresión regular.
        #print("La expresion regular es: ", self.regex)

        self.tarbol = self.arbol() # Construyendo el árbol.

        self.tree = self.analisis(self.tarbol) # Construyendo el AFD.

        self.construir() # Construyendo el árbol.

        #self.simularAFD() # Simulando el AFD.

        self.grafica() # Método para graficar.

        #self.minimizar() # Minimización.

    def aumento(self): 
        # Paso 1 - Aumentar el árbol para obtener el AFD.

        self.regex = self.regex + "#."
    # Función anulable para cada nodo el árbol.
    def anulable(self, regex):
        if regex.etiqueta == "ε":
            return True
        elif regex.etiqueta == ".":
            return self.anulable(regex.left) and self.anulable(regex.right)
        elif regex.etiqueta == "|":
            return self.anulable(regex.left) or self.anulable(regex.right)
        elif regex.etiqueta == "*":
            return True
        elif regex.etiqueta not in ["|", ".", "*"]:
            return False
            
        
    def arbol(self): # Función para construir el AFD. 
        # Paso 2 - Armar el árbol de la expresión regular.

        stack = []

        resultado = []

        #print("Expresión regular: ", self.regex)

        operaciones = ["|", ".", "*"]

        for c in self.regex:

            if c not in operaciones: # Carateres del regex.
                #print("Caracter: ", c)
                nodo1 = NodoA(etiqueta=c)

                #print("Nodo creado: ", nodo1, "Caracter: ", nodo1.etiqueta)
                stack.append(nodo1)

                resultado.append(nodo1)

            elif c == ".": # Concatenación.
                derecha1 = stack.pop()
                izquierda1 = stack.pop()

                nodo2 = NodoA(etiqueta=c, left=izquierda1, right=derecha1)

                # print("Derecha1: ", derecha1)
                # print("Izquierda1: ", izquierda1)

                #print("Nodo creado: ", nodo2)
                #print("Etiqueta: ", nodo2.etiqueta, "Izquierda: ", nodo2.left, "Derecha: ", nodo2.right)

                stack.append(nodo2)

                resultado.append(nodo2)
            
            elif c == "@": # Signo para la suma.

                print("Suma")

                nodoo = NodoA(etiqueta="+")

                stack.append(nodoo)

                resultado.append(nodoo)
            
            elif c == "~": # Signo para la resta.

                nodoo = NodoA(etiqueta="-")

                stack.append(nodoo)

                resultado.append(nodoo)
            
            elif c == "≡": # Espacio vacío.
                nods = NodoA(etiqueta="≡")

                stack.append(nods)
                resultado.append(nods)

            elif c == "¥": # \t

                nod = NodoA(etiqueta="¥")

                stack.append(nod)
                resultado.append(nod)
            
            elif c == "§": # \n

                no = NodoA(etiqueta="§")

            elif c == "|":

                derecha2 = stack.pop()
                izquierda2 = stack.pop()

                # print("Derecha2: ", derecha2)
                # print("Izquierda2: ", izquierda2)

                nodo3 = NodoA(etiqueta=c, left=izquierda2, right=derecha2)

                #print("Nodo creado: ", nodo3)
                #print("Etiqueta: ", nodo3.etiqueta, "Izquierda: ", nodo3.left, "Derecha: ", nodo3.right)

                stack.append(nodo3)

                resultado.append(nodo3)
            
            elif c == "*":

                hijo = stack.pop()

                # print("")

                nodo4 = NodoA(etiqueta=c, child=hijo)

                #print("Nodo creado: ", nodo4)
                #print("Etiqueta: ", nodo4.etiqueta, "hijo: ", nodo4.child)

                stack.append(nodo4)

                resultado.append(nodo4)


        return resultado
    
    # Función para obtener la posición siguiente de la expresión regular.
    def siguientePosicion(self, n):
    
        if n.etiqueta == ".": # Followpos del punto.
            for i in n.left.lastP:
                self.followpos[i] = self.followpos[i].union(n.right.firstP)
        
        if n.etiqueta == "*": # Followpos del kleene.
            for i in n.child.lastP:
                self.followpos[i] = self.followpos[i].union(n.child.firstP)
    
    def primeraPosicion(self, b):
        if b.etiqueta == "ε":
            pass
        elif b.etiqueta == ".":
            
            if b.left.Null:
                b.firstP = b.left.firstP.union(b.right.firstP)
            else:
                b.firstP = b.left.firstP
        
        
        elif b.etiqueta == "|":

            b.firstP = b.child.firstP
        
        elif b.etiqueta == "*":
        
            b.firstP = b.child.firstP
        
        elif b.etiqueta not in ["|", ".", "*"]:
            
            b.firstP.add(b.id)
    
    def ultimaPosicion(self, b):
        if b.etiqueta == "ε":
            pass
        elif b.etiqueta == ".":
            
            if b.right.Null:
                    b.lastP = b.left.lastP.union(b.right.lastP)
            else:
                b.lastP = b.right.lastP

        elif b.etiqueta == "|":
            
            b.lastP = b.child.lastP

        elif b.etiqueta == "*":
            
            b.lastP = b.child.lastP

        elif b.etiqueta not in ["|", ".", "*"]:
            
            b.lastP.add(b.id)
    
    def analisis(self, arbol): # Función para analizar el AFD.
        # Paso 3 - Analizar el AFD.

        #print("Árbol: ", arbol)

        diccionario = {} # Diccionario del árbol.


        # Identificando el root, que es el último punto después del #.
        # Recorriendo al revés el árbol.
        for i in range(len(arbol)-1, -1, -1):
            if arbol[i].etiqueta == ".":
                arbol[i].raiz = True
                break
        
        # # Imprimiendo cada nodo del árbol.
        # for ele in arbol: 
        #     print("Elemento: ", ele, "Raíz: ", ele.raiz)


        # Identificando los padres e hijos del árbol.
        for c in arbol:
            if c.etiqueta == "|":
                diccionario[c] = [c.left, c.right]

            elif c.etiqueta == ".":
                diccionario[c] = [c.left, c.right]
            
            elif c.etiqueta == "*":
                diccionario[c] = [c.child]
            
        # Colocándole un id a cada caracter del árbol.
        for c in arbol:
            if c.etiqueta not in ["|", ".", "*"]:
                c.id = self.contador
                self.contador += 1

            # if c.id is not None: 
            #     print("Id: ", c.id, "Caracter: ", c.etiqueta)
        
        self.followpos = [set() for i in range(self.contador)]

        # Colocando los valores de anulable.
        for a in arbol:
            a.Null = self.anulable(a)

        # Calculando el firstpos y el lastpos.
        for b in arbol:
            
            if b.etiqueta not in ["|", ".", "*"]:
                # b.firstP.add(b.id)
                # b.lastP.add(b.id)

                self.primeraPosicion(b)
                self.ultimaPosicion(b)

                # self.primeraPosicion(b)
                # self.ultimaPosicion(b)

                #print("Anulable: ", b.Null)
                # print("Label: ", b.etiqueta)
                # print("First pos: ", b.firstP)
                # print("Last pos: ", b.lastP)

            elif b.etiqueta == "|": # Computando el or.
                b.firstP = b.left.firstP.union(b.right.firstP)
                b.lastP = b.left.lastP.union(b.right.lastP)

                #print("Anulable: ", b.Null)
                # print("Or")
                # print("First pos: ", b.firstP)
                # print("Last pos: ", b.lastP)

            elif b.etiqueta == "*": # Computando el asterisco.

                #print("Kleene")
                b.firstP = b.child.firstP
                b.lastP = b.child.lastP
                #print("Anulable: ", b.Null)

                # print("Firstpos del *", b.firstP)
                # print("Lastpos del *", b.lastP)

                # print("Firstpos del hijo: ", b.child.firstP)
                # print("Lastpos del hijo: ", b.child.lastP)
                
                self.siguientePosicion(b) # Haciendo el followpos.

                # print("First pos: ", b.firstP)
                # print("Last pos: ", b.lastP)
            
            elif b.etiqueta == ".": # Computando el punto.
            
                if b.left.Null:
                    b.firstP = b.left.firstP.union(b.right.firstP)
                else:
                    b.firstP = b.left.firstP
                
                if b.right.Null:
                    b.lastP = b.left.lastP.union(b.right.lastP)
                else:
                    b.lastP = b.right.lastP
                

                self.siguientePosicion(b) # Haciendo el followpos.

                #print("Anulable: ", b.Null)
                # print("First pos: ", b.firstP)
                # print("Last pos: ", b.lastP)
            # elif b.etiqueta == "#":
            #     b.firstP = set()
            #     b.lastP = set()

            #     #print("Anulable: ", b.Null)
            #     # print("First pos: ", b.firstP)
            #     # print("Last pos: ", b.lastP)
            
            elif b.etiqueta == "ε":
                pass
        
        #print("Followpos: ", self.followpos)

        #Eliminando el primer set del followpos.
        #self.followpos.pop(0)

        # Guardando cada letra con su id.
        for c in arbol:
            if c.etiqueta not in ["|", ".", "*"]:
                self.leaves[c.id] = c.etiqueta

        #print("Leaves: ", self.leaves)

        #print("Followpos: ", self.followpos)

        return arbol
    
    
    def construir(self): # Método para construir el AFD.

        # Variables a utilizar.
        id_c = 0
        ter = [] # Lista para guardar el terminal.
        first_p = set()

        
        # Guardando el #.
        for i in range(len(self.tree)-1, -1, -1):
            if self.tree[i].etiqueta == "#":
                ter.append(self.tree[i].id)
                break
        
        self.terminal = ter.pop() # Terminal del árbol.


        # Paso 4 - Construir el AFD.

        # print("Árbl en la construcción: ", self.tree)
        # print("Alfabeto en la construcción: ", self.alfabeth)
        
        # Recorriendo el árbol para imprimir su raíz.
        for i in range(len(self.tree)-1, -1, -1):
            if self.tree[i].etiqueta == ".":
                # print("Raíz: ", self.tree[i])
                # print("Firstpos de la raíz: ", self.tree[i].firstP)
                for p in self.tree[i].firstP:
                    first_p.add(p)
                break
    

        # Creando el estado inicial.
        estado_inicial = Estado(alfabeto=self.alfabeth, id_list=first_p, id=id_c, terminal_id=self.terminal)

        # Guardando el estado inicial de forma global.
        self.EstadoInicial = estado_inicial

        #print("Estado inicial: ", estado_inicial)
        
        id_c += 1 # Aumentando en 1 el id del estado.

        self.estadosAFD.append(estado_inicial) # Guardando el estado inicial.

        queue = [estado_inicial] # Haciendo una cola con el estado inicial.
        
        #print("Followpos: ", self.followpos)

        while len(queue) > 0: # Buscando las transisicones a todos los estados.
            st = queue.pop(0)
            nuevo_estado = self.DTran(st, self.terminal)

            for s in nuevo_estado:
                estadoo = Estado(self.alfabeth, s, id_c, self.terminal)
                self.estadosAFD.append(estadoo)
                queue.append(estadoo)
                #print("Cola: ", queue)
                id_c += 1
            
        # Guardando los estados finales en una lista.
        for e in self.estadosAFD:
            # Verificando que el id del estado final esté en el set.
            if self.terminal in e.id_set:
                self.EstadosAceptAFD.append(e)

        # Post processing.
        sin_estado = False
        for estado in self.estadosAFD:
            for a in self.alfabeth:
                if estado.transitions[a] == {}:
                    sin_estado = True
                    estado.transitions[a] == id_c
                
                SET = estado.transitions[a]
                for estado2 in self.estadosAFD:
                    if estado2.id_set == SET:
                        estado.transitions[a] = estado2 # Aquí se cambió algo.
                        #print("Tipo de la transición en el cambio de variables. ", type(estado.transitions[a]), "tipo del estado2", type(estado2.id))
        
        # Imprimiendo las transiciones otra vez.
        # for estado in self.estadosAFD:
        #     print("Estado con transiciones: ", estado.transitions)

    def DTran(self, estado, terminal): # Cálculo de las transiciones.

        nuevo_estado = []
        for i in estado.id_set: # Si el estado final está en el set, se continúa.
            if i == terminal:
                continue
            
            label = self.leaves[i] # Agarrando el label de cada hoja.
            #print(label)

            if estado.transitions[label] == {}: # Transiciones del estado.
                #print("Followpos sin la unión: ", self.followpos[i])

                #print("Label: ", label, estado.transitions[label], "Su followpos: ", self.followpos[i])
                estado.transitions[label] = self.followpos[i]
            
            else: # Si las transiciones están llenas, entonces se unen los estados.
                #print("Followpos en la unión: ", self.followpos[i])
                estado.transitions[label] = estado.transitions[label].union(self.followpos[i])
            
        for a in self.alfabeth: # Transiciones con los símbolos.
            if estado.transitions[a] != {}:
                nuevo = True
                for e in self.estadosAFD:
                    if (e.id_set == estado.transitions[a]) or (estado.transitions[a] in nuevo_estado):
                        #print(e.id_set, estado.transitions[a])
                        nuevo = False
                
                if nuevo:
                    #print("Transición a agregar: ", estado.transitions[a])
                    nuevo_estado.append(estado.transitions[a])
            
        return nuevo_estado
    
    def simularAFD(self): # Simular AFD.
        print("Estados. ", self.estadosAFD)

        diccionario = {}

        trans = []

        # # Guardando localmente las transiciones de cada estado.
        # for estado in self.estadosAFD:
        #     print("Estado: ", estado, "Transiciones: ", estado.transitions)

        # print("Transiciones: ", trans)

        # Guardando el estado con sus transiciones en el diccionario.
        for estado in self.estadosAFD:
            
            diccionario[estado] = estado.transitions

        
        print("Diccionario: ", diccionario)

        cadena = input("Ingrese la cadena a evaluar: ")

        estado_actual = self.EstadoInicial # Estado inicial.

        print("Tipo del estado inicial: ", type(estado_actual))

        # Recorriendo la cadena.
        for simbolo in cadena:
            if simbolo not in self.alfabeth:
                print("La cadena no pertenece al lenguaje.")
                break
            
            # Imprimiendo el diccionario.
            #print("Diccionario: ", diccionario)

            estado_actual = diccionario[estado_actual][simbolo] # Estado actual.
            
            if estado_actual != {}:
                continue
            else: 
                print("Cadena no aceptada")
                break

            #print("Estado actual: ", estado_actual)

        if estado_actual in self.EstadosAceptAFD:
            print("Cadena aceptada por el AFD directo.")
            
        else: 
            print("Cadena rechazada por el AFD directo.")
                    
    def grafica(self): #Método para graficar.
        grafo = gv.Digraph(comment="AFD", format="png")
        grafo.node('title', 'AFD', shape='none')

        # for estado in self.estadosAFD:
        #     print("Estados en el método de gráfica: ", estado)

        # # Imprimiendo los estados y sus tansiciones.
        # for estado in self.estadosAFD:
        #     print("Estado: ", estado, "Transiciones: ", estado.transitions)
        
        # For indicado.
        for estado in self.estadosAFD:
            for a in self.alfabeth:
                
                trans = estado.transitions[a]
                #print("Estado: ", estado, "Trans: ", trans)

                # Eliminar las transiciones vacías.
                if trans == {}:
                    continue
                else:

                    # Cambiando algunos labels.
                    if a == "@": # Símbolo de suma.
                        a = "+"
                    if a == '~': # Símbolo de resta.
                        a = "-"
                    if a == "≡": # Símbolo de " ".
                        a = "bb"
                    if a == "¥": # Símbolo de \t.
                        a = "\yt"
                    if a == "§": # Símbolo de \n.
                        a = "\yn"

                    grafo.edge(str(estado), str(trans), label=a)

        # Dibujando los estados del AFD.
        for esta in self.estadosAFD:
    
            if esta in self.EstadosAceptAFD:
                #print("Estado de aceptación: ", esta)
                grafo.node(str(esta), str(esta), shape="doublecircle")
            
            elif esta == self.EstadoInicial: 

                grafo.node(str(esta), str(esta), shape="circle", color="green")

            else:
                grafo.node(str(esta), str(esta), shape="circle")
        
        # Colocando el autómta de manera horizontal.
        #grafo.graph_attr['rankdir'] = 'LR'

        grafo.render('AFD_Directo', view=True) # Dibujando el grafo.

        for estado in self.estadosAFD:
            self.dict[estado] = estado.transitions
        
        # Cambiando algunos símbolos en el diccionario.
        # Buscar los símbolos.


        #print("Diccionario: ", diccionario)

    # Haciendo la minimización.
    def minimizar(self):
        
        diccionario_m = {}
        finales_m = []
        estados_m = []
        inicial_m = []
        
        diccionario = {}

        # For indicado.
        for estado in self.estadosAFD:

            diccionario[estado] = {}

            for a in self.alfabeth:
                
                trans = estado.transitions[a]
                #print("Estado: ", estado, "Simbolo: ", a,  "Trans: ", trans)
                #print("Tipo de la transición: ", type(trans))

                diccionario[estado][a] = trans

        # print("Alfabeto: ", self.alfabeth)

        # print("Diccionario: ", diccionario)

        # print("Estados: ", self.estadosAFD)
        # print("Estado inicial: ", self.EstadoInicial)
        
        particiones = [[s for s in self.estadosAFD if s in self.EstadosAceptAFD], 
                       [s for s in self.estadosAFD if s not in self.EstadosAceptAFD]]
        
        #print("Particiones en el SintaxT: ", particiones)

        # Función auxiliar para buscar una partición que contenga un estado.
        def buscar_particion(estado):

            # Ordenando las particiones.
            #particiones.sort(key=lambda x: x[0].id)

            #print("Particiones: ", particiones)

            for i, partition in enumerate(particiones):
                
                #print("Estado: ", estado, "partición: ", particion)
                
                #print("Estado en el método de búsqueda: ", estado, "Partición en el método de búsqueda: ", partition, estado in partition)

                if estado in partition:
                    #print("Estado: ", estado, "Partición: ", partition, "i: ", i)
                    return i

                # else: 
                #     pass
                
            #return None
        
        itera = True

        # Iteraciones.
        while itera:
            new_partitions = []
            #Creando una lista de estados equivalentes para cada partición.
            for partition in particiones:
                # Creando una lista de estados equivalentes para cada partición.
                equivalent_states = {}
                for state in partition:
                    transiciones = [diccionario[state][simbolo] for simbolo in self.alfabeth]
                    #print("Transiciones: ", transiciones)
                    #print("Diccionario: ", diccionario)

                    # Si algo no queda bien del resultado, revisar acá las transiciones.

                    # Quitando las parejas que llegan a {}.
                    transiciones = [t for t in transiciones if t != {}]

                    #print("Transiciones: ", transiciones)

                    equivalent_states.setdefault(tuple(transiciones), []).append(state)
                
                #print("Equivalent states: ", equivalent_states)

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
                
                #else:
                
                particiones = new_partitions # Guardando las particiones finales.

                for i, partition in enumerate(particiones):
                    # Buscando el estado inicial.
                    if self.EstadoInicial in partition:
                        inicial_m.append(self.EstadoInicial.id)

                #print("Particiones finales: ", particione)

        # Construyendo el AFD minimizado.
        new_states = [tuple(partition) for partition in particiones]
        
        new_transitions = {}

        for estad in self.estadosAFD:
            particion = buscar_particion(estad)

            #print("Partición: ", particion)
            

            # Buscando las transiciones de cada estado.
            for simbolo in self.alfabeth:


                llegada = diccionario[estad][simbolo]

                #print("Diccionario: ", diccionario)
                
                # Parseando la transición a tipo estado.
                #transicion = Estado(id=transicion)

                # Imprimiendo los resultados.
                #print("Resultado: ", buscar_particion(llegada))

                # #print("Tipo de la transición en el método de minimización: ", type(transicion))
                #new = tuple(sorted([buscar_particion(llegada)]))

                new = tuple(sorted([buscar_particion(llegada)]))

                #print("New: ", new)

                # print("Estado: ", estad ,"New: ", new, "símbolo: ", simbolo)

                #print("New states: ", new_states)

                # Buscando a que estado llegó de la partición.


                # print("New states: ", new_states[particion])

                #print("Partición a crear: ", (new_states[particion], simbolo))

                if new[0] is None: 
                    continue

                new_transitions[(new_states[particion], simbolo)] = new_states[new[0]]
                


        # # print("Estados: ", new_states)

        # #print("Transiciones: ", new_transitions)
        #new_final_states = set([buscar_particion(state) for state in self.EstadosAceptAFD])

        new_finals = []
        
        for estadoA in self.EstadosAceptAFD:
            final = buscar_particion(estadoA)

            # print("Final: ", final)

            # print("New states: ", new_states)

            new_finals.append(new_states[final])
        
        #print("New finals: ", new_finals)
        
        #print("Transiciones: ", new_transitions)

        """
        old_dict: new_transitions.
        new_dict: final_trasitions.
        """

        
        # print("Final transitions: ", final_transitions)

        # Reordenando los estados.
        for tupla in new_states:
            if tupla in new_finals:
                #print("Tupla con el estado final: ", tupla)
                indice = new_states.index(tupla)
                new_states.append(new_states.pop(indice))
    

        # Creando un diccionario con los nuevos estados y sus íd's nuevos.
        new_dict = {}

        for i, tupla in enumerate(new_states):
            #print("Id: ", i)

            new_dict[tupla] = i

        #print("New dict: ", new_dict)

        for tup, val in new_transitions.items(): # Dándole más estética al diciconario.
            diccionario_m[(new_dict[tup[0]], tup[1])] = new_dict[val]

            # if tup[0] in new_finals:
            #     #print("Estado final: ", new_dict[val])
            #     finales_m.append(new_dict[tup[0]])
            
            if tup[0] in inicial_m or val in inicial_m:
                #print("Estado final: ", new_dict[val])
                inicial_m.append(new_dict[val])
                inicial_m.append[new_dict[tup[0]]]

            estados_m.append(new_dict[val])
            estados_m.append(new_dict[tup[0]])
        
        for estado in new_states: 
            print("Estado en el sintaxT: ", estado)
            if estado in new_finals:
                finales_m.append(new_dict[estado])

        # Quitando repeticiones.
        inicial_m = list(set(inicial_m))
        finales_m = list(set(finales_m))
        estados_m = list(set(estados_m))

        # Pasando todos los estados a tipo int.
        for i, estado in enumerate(estados_m):
            estados_m[i] = int(estado)
        
        for i, estado in enumerate(finales_m):
            #print(type(estado))
            finales_m[i] = int(estado)
        
        for i, estado in enumerate(inicial_m):
            inicial_m[i] = int(estado)

        #print("Estado inicial del AFD directo: ", inicial_m)


        """
        Listas a utilizar: 
        diccionario_m: Diccionario con las transiciones.
        finales_m: Lista con los estados finales.
        estados_m: Lista con los estados.
        """
        
        # Facilitando un poco la graficada.
        diccionario_temporal = {}

        for c, v in diccionario_m.items():
            if c[0] not in diccionario_temporal:
                diccionario_temporal[c[0]] = {}
            diccionario_temporal[c[0]][c[1]] = v

        diccionario_m = diccionario_temporal.copy()

        # Cambios
        new_t = {} 
        for keys, values in diccionario_m.items():
            new_t[keys] = [(k, v) for k, v in values.items()]
        
        diccionario_m = new_t.copy()
    
        #print("Diccionario final: ", diccionario_m)
        # print("Finales: ", finales_m)
        # print("Inicial: ", inicial_m)
        # print("Estados: ", estados_m)
        # print("Inicial: ", inicial_m)

        for estado in estados_m:
            if estado not in diccionario_m:
            # Quitando el estado de la lista de estados.
                estados_m.remove(estado)

            if estado in inicial_m: 
                # Quitando el estado de la lista de estados iniciales.
                inicial_m.remove(estado)


        inicial_m.append(estados_m[0])

        print("Inicial en SintaxT: ", inicial_m)
        print("Final en el SintaxT: ", finales_m)

        self.simular_AFD_min(diccionario_m, estados_m, inicial_m, finales_m)

        # Gráfica
        grafo = gv.Digraph(comment="AFD_Directo_Minimizado", format="png")
        grafo.node('title', 'AFD Minimizado', shape='none')

        for ke, va in diccionario_m.items():
            
            for ks, vs in va: # Transiciones.
                grafo.edge(str(ke), str(vs), label=str(ks))

        # Dibujando los estados.
        for estado in estados_m:
            
            #print("Estado: ", estado, "Finales: ", self.finales_m, "Iniciales: ", self.inicial_m.

            if estado in finales_m:
                
                #print("Llegué al final: ", estado)
                grafo.node(str(estado), str(estado), shape="doublecircle")
            
            elif estado in inicial_m:

                grafo.node(str(estado), str(estado), shape="circle", color="green")
            
            else:
            
                grafo.node(str(estado), str(estado), shape="circle")

        # Colocando título a la imagen.

        # Colocando el autómta de manera horizontal.
        grafo.graph_attr['rankdir'] = 'LR'

        grafo.render('AFD_Directo_Minimizado', view=True) # Dibujando el grafo.

    def simular_AFD_min(self, diccionario_m, estados_m, inicial_m, finales_m):
        
        # print("Diccionario: ", diccionario_m)
        # print("Estados: ", estados_m)
        # print("Inicial ", inicial_m)
        # print("Finales: ", finales_m)

        # Creando un diccionario para simular.
        diccionario_simulacion = {}

        for c, v in diccionario_m.items():
            estado_actual = c
            trans = {}

            for simb, sig in v: 
                trans[simb] = sig
            
            diccionario_simulacion[estado_actual] = trans
        
        print("Diccionario simulación: ", diccionario_simulacion)

        # Simulando el AFD.
        cadena = input("Ingrese la cadena a simular: ")

        estado_actual = inicial_m.pop()


        for simbolo in cadena:
            if simbolo not in self.alfabeth:
                print("El símbolo no pertenece al alfabeto.")
                return
            
            if simbolo in diccionario_simulacion[estado_actual]:
                estado_actual = diccionario_simulacion[estado_actual][simbolo]
            else:
                continue

        if estado_actual in finales_m:
            print("Cadena aceptada por el AFD_min.")
        else:
            print("Cadena rechazada el AFD_min")