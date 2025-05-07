class NodoA:
    def __init__(self, etiqueta=None, left=None, right=None, child=None):
        self.etiqueta = etiqueta
        self.left = left
        self.right = right
        self.child = child
        self.raiz = False
        self.id = None
        self.Null = None
        self.firstP = set()
        self.lastP = set()

    def __iter__(self):

        if self.etiqueta != None:
            yield self.etiqueta
        elif self.child != None:
            yield self.child
        elif self.left != None:
            yield self.left
        elif self.right != None:
            yield self.right

    def __repr__(self):
        
        if self.etiqueta != None:
            return str(self.etiqueta)
        elif self.child != None:
            return str(self.child)
        elif self.left != None:
            return str(self.left)
        elif self.right != None:
            return str(self.right)
