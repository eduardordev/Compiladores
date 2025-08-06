class Transiciones: 

    def __init__(self, estadoInicial, simbolo, estadoFinal):
        self.estadoInicial = estadoInicial
        self.estadoFinal = estadoFinal
        self.simbolo = simbolo

    def getEstadoInicial(self):
        return self.estadoInicial
    
    def getEstadoFinal(self):
        return self.estadoFinal
    
    def getSimbolo(self):
        return self.simbolo
    
    def setEstadoInicial(self, estadoInicial):
        self.estadoInicial = estadoInicial

    def setEstadoFinal(self, estadoFinal):
        self.estadoFinal = estadoFinal
    
    def __str__(self):
        # Regresando el estado inicial, el símbolo y el estado final.
        return str(self.estadoInicial) + " -- " + str(self.simbolo) + " --> " + str(self.estadoFinal)