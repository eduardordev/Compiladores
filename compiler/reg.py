precedence_map = {
'(': 1,
'|': 2,
'.': 3,
'?': 4,
'*': 4,
'+': 4,
'^': 5
}

def get_precedence(c):
    """
    Obtiene la precedencia de un caracter c.
    Si no se encuentra en el diccionario de precedencia, devuelve 6.
    """
    return precedence_map.get(c, 6)

def format_regex(regex):
    """
    Transforma una expresión regular insertando el operador de concatenación '.' explícitamente.
    """
    res = ''
    all_operators = set(['|', '?', '+', '*', '^'])
    binary_operators = set(['^', '|'])

    for i in range(len(regex)):
        c1 = regex[i]

        if i + 1 < len(regex):
            c2 = regex[i + 1]

            res += c1

            if c1 != '(' and c2 != ')' and c2 not in all_operators and c1 not in binary_operators:
                res += '.'

    res += regex[-1]

    # Si hay un +, se copia la expresión regular anterior y se le agrega el operador de cerradura de Kleene.
    if "+" in res:
        res = res.replace("+", "")
        res = res + "." + res + "*"
        print("Res: ", res)
    return res


def evaluar(regex):
    
    stack = []

    postfix = ''
    
    formatted_regex = format_regex(regex)

    for c in formatted_regex:
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack[-1] != '(':
                postfix += stack.pop()
            stack.pop()
        else:
            while len(stack) > 0:
                peeked_char = stack[-1]

                peeked_char_precedence = get_precedence(peeked_char)
                current_char_precedence = get_precedence(c)

                if peeked_char_precedence >= current_char_precedence:
                    postfix += stack.pop()
                else:
                    break

            stack.append(c)

    while len(stack) > 0:
        postfix += stack.pop()
    return postfix