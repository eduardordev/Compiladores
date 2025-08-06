from Estado import *
from Automata import *
from Transiciones import *
import matplotlib.pyplot as plt
import networkx as nx
import graphviz as gv
from collections import OrderedDict

def thompson(expresion_regular):
    """Convierte una expresión regular en un autómata utilizando el algoritmo de Thompson"""
    stack = []
    lista = []
    diccionario = {}
    estados = 0
    epsilon = 'ε'

    for caracter in expresion_regular:
        if caracter == '|':
            # Obtener los dos últimos automatas del stack
            b = stack.pop()
            a = stack.pop()


            # Crear nuevos estados inicial y final
            inicio = Estado(estados)
            estados += 1
            fin = Estado(estados)
            estados += 1

            # Crear transiciones epsilon desde los nuevos estados inicial y final a los automatas a y b.

            # Creando las transiciones epsilon desde el estado inicial al estado inicial de a y b.
            nuevo1 = Transiciones(inicio, 'ε', a.get_estado_inicial())
            nuevo2 = Transiciones(inicio, 'ε', b.get_estado_inicial())
            nuevo3 = Transiciones(a.get_estado_final(), 'ε', fin)
            nuevo4 = Transiciones(b.get_estado_final(), 'ε', fin)

            # Crear el nuevo autómata y apilarlo en el stack  
            nuevo_automata = Automata(inicio, fin)
            
            # Agregando los nuevos estados a la lista de estados.
            lista.append(nuevo1)
            lista.append(nuevo2)
            lista.append(nuevo3)
            lista.append(nuevo4)

            # Guardando el nuevo automata en el stack.
            stack.append(nuevo_automata)

        elif caracter == '*':
            # Obtener el último automata del stack
            a = stack.pop()

            # Crear nuevos estados inicial y final
            inicio = Estado(estados)
            estados += 1
            fin = Estado(estados)
            estados += 1

            # Crear transiciones epsilon desde los nuevos estados inicial y final a los estados inicial y final del automata a
            n1 = Transiciones(inicio, 'ε', a.get_estado_inicial())
            n2 = Transiciones(inicio, 'ε', fin)
            n3 = Transiciones(a.get_estado_final(), 'ε', a.get_estado_inicial())
            n4 = Transiciones(a.get_estado_final(), 'ε', fin)

            # Crear el nuevo autómata y apilarlo en el stack
            nuevo_automata = Automata(inicio, fin)
            stack.append(nuevo_automata)

            # Agregando los nuevos estados a la lista de estados.
            lista.append(n1)
            lista.append(n2)
            lista.append(n3)
            lista.append(n4)

        elif caracter == '+':
            # Obtener el último automata del stack
            a = stack.pop()

            # Crear nuevos estados inicial y final
            inicio = Estado(estados)
            estados += 1
            fin = Estado(estados)
            estados += 1

            # Crear transiciones epsilon desde los nuevos estados inicial y final a los estados inicial y final del automata a
            
            nu1 = Transiciones(inicio, 'ε', a.get_estado_inicial())
            nu2 = Transiciones(a.get_estado_final(), 'ε', a.get_estado_inicial())
            nu3 = Transiciones(a.get_estado_final(), 'ε', fin)

            # Crear el nuevo autómata y apilarlo en el stack
            nuevo_automata = Automata(inicio, fin)
            stack.append(nuevo_automata)
            
            # Agregando los nuevos estados a la lista de estados.
            lista.append(nu1)
            lista.append(nu2)
            lista.append(nu3)

        elif caracter == '.':
            # Obtener los dos últimos automatas del stack
            b = stack.pop()
            a = stack.pop()

            # # Obteniendo el estado final del autómata b. (segundo autómata)
            # print(b.get_estado_final())

            # # Obteniendo el estado inicial del autómata a. (primer autómata)
            # print(a.get_estado_inicial())

            # Sacando la información de los estados.
            estadoFinal = a.get_estado_final()
            estadoInicial = b.get_estado_inicial()

            # print("Estado final: ", estadoFinal)
            # print("Estado inicial: ", estadoInicial)

            # Merge de los estados.
            for transicion in lista: 

                if transicion.getEstadoInicial() == estadoInicial:
                    
                    transicion.setEstadoInicial(estadoFinal)

                # if i.getEstadoInicial() == b.get_estado_inicial():
                #     # Creando una transición desde el estado inicial del autómata a al estado final del autómata b.
                #     n = Transiciones(a.get_estado_final(), i.getSimbolo(), b.get_estado_final())
                #     # Eliminando la transición del estado inicial del autómata b.
                #     lista.remove(i) 
                #     # Agregando la nueva transición a la lista de transiciones.
                #     lista.append(n)

                #     print("Transición: ", n)

            # Crear el nuevo autómata y apilarlo en el stack
            nuevo_automata = Automata(a.get_estado_inicial(), b.get_estado_final())
            stack.append(nuevo_automata)

            # # Crear el nuevo autómata y apilarlo en el stack
            # nuevo_automata = Automata(a.estado_inicial, b.estado_final)
            
            # stack.append(nuevo_automata)
            # lista.append(nuevo_automata)
        
        elif caracter == '?': # Operador de cero o una ocurrencia.
            # Este operador es equivalente a la expresión regular (a|ε).
            
            # Haciendo primero una transición con dos estados y ε.
            inicio1 = Estado(estados)
            estados += 1
            fin1 = Estado(estados)
            estados += 1

            # Creando la transición.
            en1 = Transiciones(inicio1, epsilon, fin1)
            lista.append(en1)
            nuevo_automata1 = Automata(inicio1, fin1)
            stack.append(nuevo_automata1)

            # Obtener los dos últimos automatas del stack
            b = stack.pop()
            a = stack.pop()


            # Crear nuevos estados inicial y final
            inicio2 = Estado(estados)
            estados += 1
            fin2 = Estado(estados)
            estados += 1

            # Crear transiciones epsilon desde los nuevos estados inicial y final a los automatas a y b.

            # Creando las transiciones epsilon desde el estado inicial al estado inicial de a y b.
            ns1 = Transiciones(inicio2, 'ε', a.get_estado_inicial())
            ns2 = Transiciones(inicio2, 'ε', b.get_estado_inicial())
            ns3 = Transiciones(a.get_estado_final(), 'ε', fin2)
            ns4 = Transiciones(b.get_estado_final(), 'ε', fin2)

            # Crear el nuevo autómata y apilarlo en el stack  
            nuevo_automata2 = Automata(inicio2, fin2)
        
            # Guardando el nuevo automata en el stack.
            stack.append(nuevo_automata2)

            # Agregando los nuevos estados a la lista de estados.
            lista.append(ns1)
            lista.append(ns2)
            lista.append(ns3)
            lista.append(ns4)

            #print("Lista: ", str(lista))

        else:
            # Crear nuevos estados inicial y final para el autómata que representa el caracter actual.
            # Crear nuevos estados inicial y final
            inicio = Estado(estados)
            estados += 1
            fin = Estado(estados)
            estados += 1

            # # Crear transición desde el estado inicial al estado final con el caracter actual.
            trans = Transiciones(inicio, caracter, fin)
            
            # # Crear el nuevo autómata y apilarlo en el stack
            nuevo_automata = Automata(inicio, fin)
            
            # print(nuevo_automata.get_estado_inicial())
            # print(nuevo_automata.get_estado_final())
            
            # Guardando las transiciones de la forma (estado_inicial, caracter, estado_final) en un diccionario.
            stack.append(nuevo_automata)

            # Agregando los nuevos estados a la lista de estados.
            lista.append(trans)

    # for automata in lista:
    #     print(str(automata))

    # # Imprimedo el inicio y el final del autómata.
    # print("Estado inicial: " + str(stack[0].get_estado_inicial()))
    # print("Estado final: " + str(stack[0].get_estado_final()))

    # Convirtiendo la lista de transiciones en un diccionario.
    for i in lista:
        if i.getEstadoInicial() in diccionario:
            diccionario[i.getEstadoInicial()].append((i.getSimbolo(), i.getEstadoFinal()))
        else:
            diccionario[i.getEstadoInicial()] = [(i.getSimbolo(), i.getEstadoFinal())]

        # Guardando el estado final del autómata.
        if i.getEstadoFinal() not in diccionario:
            diccionario[i.getEstadoFinal()] = []

    # for key, value in diccionario.items():
    #     print(key, str(value))

    auto = stack.pop() # Regresando los estados iniciales y finales.

    return auto, lista, diccionario

def req(simbolo):
    # Método para hacer la transición de un estado a otro con epsilon.
        # Crear nuevos estados inicial y final para el autómata que representa el caracter actual.
        # Crear nuevos estados inicial y final
        inicio = Estado(estados)
        estados += 1
        fin = Estado(estados)
        estados += 1

        # # Crear transición desde el estado inicial al estado final con el caracter actual.
        trans = Transiciones(inicio, simbolo, fin)
        
        # # Crear el nuevo autómata y apilarlo en el stack
        nuevo_automata = Automata(inicio, fin)
        
        return trans, nuevo_automata

def alfabeto(regex):
    # Método para obtener el alfabeto de la expresión regular.
    alfabeto = []

    for i in regex:
        if i != '(' and i != ')' and i != '*' and i != '+' and i != '?' and i != '|' and i != 'ε' and i != '.':
            alfabeto.append(i)
            # Quitando los elementos repetidos.
            alfabeto = list(dict.fromkeys(alfabeto))
    
    return alfabeto

def graficar(automata, lista, diccionario): #Método para graficar el autómata.

    # Cambiando el título de la ventana.
    plt.title("Autómata Finito No Determinista - Thompson")

    G = nx.DiGraph() # Creando el grafo.

    #print("Diciconario: " + str(diccionario))

    # Agregando los estados al grafo.
    for estado in diccionario:
        G.add_node(estado)

        # Verificando si el estado es inicial o final.
        if estado == automata.get_estado_inicial():
            G.nodes[estado]['color'] = 'green'
        elif estado == automata.get_estado_final():
            G.nodes[estado]['color'] = 'red'
        else:
            G.nodes[estado]['color'] = 'blue'

    # Añadiendo las aristas al grafo.
    for key, value in diccionario.items():
        for simbolo, estado in value:
            for i in lista:
                G.add_edge(key, estado, label=simbolo)

    
    # Configurar opciones de visualización
    pos = nx.spring_layout(G)
    node_colors = [G.nodes[estado]["color"] for estado in G.nodes()]
    edge_labels = {(origen, destino): datos["label"] for origen, destino, datos in G.edges(data=True)}

    # Dibujar el grafo
    nx.draw_networkx_nodes(G, pos, node_color=node_colors)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.axis("off")
    plt.show()

def grafo(automata, lista, diccionario): # Método para graficar el AFN.
    grafo = gv.Digraph('G', filename='grafo', format='png')
    
    grafo.node('title', 'AFN', shape='none')

    estados = [ str(estado) for estado in diccionario.keys() ]

    # Dibujando los nodos.
    for estado in estados:
        if estado == str(automata.get_estado_inicial()):
            grafo.node(estado, estado, color='green')
        elif estado == str(automata.get_estado_final()):
            grafo.node(estado, estado, color='red')
        else:
            grafo.node(estado, estado, color='blue')
    
    # Dibujando las aristas.
    # print("Estados: " + str(estados))

    # Dibujando las transiciones.
    for key, value in diccionario.items():
        for simbolo, estado in value:
            grafo.edge(str(key), str(estado), label=simbolo)

    # Colocando el autómta de manera horizontal.
    grafo.graph_attr['rankdir'] = 'LR'

    grafo.render('AFN', view=True)

    # Obteniendo los estados del AFN.
    estados = list(diccionario.keys())

    # Obteniendo el alfabeto del AFN.
    alfabeto = set()

    for estado in estados: 
        for transicion in diccionario[estado]:
            alfabeto.add(transicion[0])
    
    # Creando la tabla de transiciones.
    tabla = {}

    for estado in estados: 
        tabla[estado] = {}
        for simbolo in alfabeto:
            tabla[estado][simbolo] = set()

            for transicion in diccionario[estado]:
                if transicion[0] == simbolo:
                    tabla[estado][simbolo].add(transicion[1])
            if not tabla[estado][simbolo]:
                tabla[estado][simbolo] = None
            
    # # Imprimiendo las transiciones.
    # print("Tabla de transiciones del AFN: ")
    # print("Estado | ", end="")

    # for simbolo in sorted(alfabeto):
    #     print(simbolo, end=" | ")

    # print()
    # print("-" * (8 + 4 * len(alfabeto)))

    # for estado in estados: 
    #     print(f"{estado}".ljust(7), end="| ")
    #     for simbolo in sorted(alfabeto):
    #         if tabla[estado][simbolo] is None:
    #             print("".ljust(3), end="| ")
    #         else: 
    #           print(",".join(str(x) for x in tabla[estado][simbolo]).ljust(3), end=" | ")

    #     print()


def simular(automata, diccionario): # Método para simular el AFN.
    print("Simulación del AFN")
    # print("Diccionario: ", diccionario)
    # print("Automata: ", automata)

    # Creando un set con los estados del autómata.
    estados = set(diccionario.keys())

    # Obteniendo un set con el alfabeto desde el diccionario.
    alfabeto = set()

    for key, value in diccionario.items():
        for simbolo, estado in value:
            alfabeto.add(simbolo)
    
    # Quitando el epsilon del alfabeto.
    #alfabeto.remove('ε')

    #print("Alfabeto: ", alfabeto)

    # Guardando el estado inicial.
    estado_inicial = [automata.estado_inicial]
    
    # Guardando el estado final en un set.
    estado_final = set()

    estado_final.add(automata.estado_final)

    # print("Estado inicial: ", estado_inicial)
    # print("Estado final: ", estado_final)

    # Pidiéndole al usuario que ingrese una cadena.
    cadena = input("Ingrese una cadena: ")

    # Lista para guardar los estados alcanzables.
    s = cerradura_epsilon(estado_inicial, diccionario)
    
    # Jalando el siguiente estado.
    for simbolo in cadena:
        
        # Verificando si el símbolo pertenece al alfabeto.
        if simbolo in alfabeto:
            s = mover(s, simbolo, diccionario)
            s = cerradura_epsilon(s, diccionario)
        else:
            print("El símbolo no pertenece al alfabeto.")
            break
    
    # Verificando si hay un estado de aceptación en s.
    if estado_final.intersection(s):
        print("La cadena es aceptada.")
    else:
        print("La cadena no es aceptada.")

# Definiendo las funciones de para la simulada.
def mover(estados, simbolo, diccionario):

    resultado = []

    for estado in estados:
        # Verificando si el estado tiene transiciones con el símbolo actual.
        if estado in diccionario:
            # Si tiene transiciones con el símbolo actual, se agregan a la lista de estados alcanzables.
            for simbolo2, estado2 in diccionario[estado]:
                if simbolo == simbolo2:
                    # Guardando los estados en la lista de estados alcanzables.
                    resultado.append(estado2)
    
    return resultado

# Definiendo la función para cerradura epsilon.
def cerradura_epsilon(estados, diccionario):

    # Lista para el resultado.
    resultado = []

    # Stack para guardar los estados.
    stack = []

    for est in estados: 
        stack.append(est)

    while len(stack) > 0:
        # Obteniendo el estado actual.
        estado = stack.pop()

        # Verificando si el estado actual ya se encuentra en la lista de estados alcanzables.
        if estado not in resultado:
            # Si no se encuentra en la lista, se agrega.
            resultado.append(estado)

            # Verificando si el estado actual tiene transiciones con epsilon.
            if estado in diccionario:
                for simbolo, estado2 in diccionario[estado]:
                    if simbolo == 'ε':
                        stack.append(estado2)
    
    return resultado

# Método para unir los AFNs resultantes.
def union_AFNs(automatas, listas, diccionarios):
    
    # print("Automatas: ", automatas)
    # print("Listas: ", listas)
    # print("Diccionarios: ", diccionarios)

    #dicts = {}

    # # Guardando cada autómata con su lista y diccionario dentro del dicts.
    # for automata, lista, diccionario in zip(automatas, listas, diccionarios):
    #     dicts[automata] = [lista, diccionario]
    
    # print("Dicts: ", dicts)

    # Creando el nuevo autómata.
    # Creando un nuevo estado.

    nuevo_estado = Estado(2000)

    # Conectando el estado a cada estado inicial de los autómatas.
    for automata in automatas:
        #print("Automata: ", automata)
        pass
    
    # Creando una nueva transición con el nuevo_estado y el estado inicial de cada autómata.
    for automata in automatas:
        nueva_transicion = Transiciones(nuevo_estado, 'ε', automata.estado_inicial)

        print("Nueva transición: ", nueva_transicion)

        # Guardando la transición en la lista de transiciones que corresponde al índice del autómata.
        for automata2, lista in zip(automatas, listas):
            if automata == automata2:
                lista.append(nueva_transicion)
                # Colocando la nueva transición hasta el principio de la lista.
                lista.insert(0, lista.pop())

                for trans in lista:
                    #print("Transición: ", trans)
                    pass
        
        # Colocando la nueva transición en el diccionario que corresponde al índice del autómata.
        for automata3, diccionario in zip(automatas, diccionarios):
            if automata == automata3:
                #print("Autómata: ", automata, "Autómata 3: ", automata3)

                # Agregando el nuevo estado al diccionario.
                diccionario[nuevo_estado] = []

                # Agregando la nueva transición al diccionario.
                diccionario[nuevo_estado].append(('ε', automata.estado_inicial))
                
                automata.estado_general = nuevo_estado

                # print("Estado inicial: ", automata.estado_inicial)
                # print("Estado final: ", automata.estado_final)
                #print("Estado general: ", automata.estado_general)
                    
    # Graficando el primer diccionario.
    grafo = gv.Digraph('G', filename='grafo', format='png')

    # Recorriendo la lista de diccionarios.
    for i, diccionario in enumerate(diccionarios):
        
        # Crear un subgrafo para cada grafo en la lista.
        with grafo.subgraph(name=f'cluster_{i}') as subgraph:
            subgraph.attr(label=f'Grafo {i+1}')

            # Recorrer las claves y valores de cada diccionario.
            for key, value in diccionario.items():

                # Agregar el nodo al subgrafo.
                subgraph.node(str(key), str(key))
            
                # Pintando de color verde el estado inicial.
                if key == nuevo_estado:
                    subgraph.node(str(key), style='filled', color='green')

                # Leer las transiciones de cada estado.
                for transicion in value:
                    # Agregar la arista al subgrafo.
                    subgraph.edge(str(key), str(transicion[1]), label=str(transicion[0]))

    
    # Colocando el autómta de manera horizontal.
    grafo.graph_attr['rankdir'] = 'LR'

    grafo.render('AFN', view=True)
    
