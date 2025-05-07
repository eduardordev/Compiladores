class Automata:
    """Clase que representa el autómata generado por el algoritmo de Thompson"""
    def __init__(self, inicio, fin):
        self.estado_inicial = inicio
        self.estado_final = fin
        self.estado_general = None

    # Devolver el estado inicial del autómata.
    def get_estado_inicial(self):
        return self.estado_inicial
    
    # Devolver el estado final del autómata.
    def get_estado_final(self):
        return self.estado_final

    def __str__(self):
        return str(self.estado_inicial) + " -- " + str(self.estado_final)