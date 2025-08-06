from regex_tree import RegexTree
import graphviz

# Definir la expresión regular como una cadena
regex_str = "a(b|c)*d"

# Crear una instancia de la clase RegexTree
regex_tree = RegexTree(regex_str)

# Construir las tablas de followpos, firstpos y lastpos
regex_tree.build_positions()

# Construir el AFD correspondiente utilizando las tablas de followpos, firstpos y lastpos
regex_tree.build_afd()

# Generar el diagrama del AFD en formato DOT
dot_data = regex_tree.afd_to_dot()

# Renderizar el diagrama del AFD utilizando la biblioteca graphviz
graph = graphviz.Source(dot_data)
graph.render('afd', view=True)
