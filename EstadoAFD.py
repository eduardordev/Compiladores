class Estado:
    """Clase que representa un estado en el autómata"""
    def __init__(self, alfabeto, id_list, id, terminal_id):
        self.id = id
        self.id_set = set(id_list) # Estados a analizar.
        self.transitions = dict() # Transiciones del estado.
        self.final = terminal_id in self.id_set # Va a ser verdadero si es el estado final.

        for a in alfabeto: # Guardando las transiciones con el estado.
            self.transitions[a] = {} # Guardando las transiciones de cada estado.
        

    def __repr__(self):
        return str(self.id)

    def __str__(self):
        return str(self.id)