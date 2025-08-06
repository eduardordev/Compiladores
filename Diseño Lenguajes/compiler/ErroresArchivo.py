# ErroresArchivo.py

# Helpers (idénticos a Errores.py)
def check_parenthesis_balance(exp):
    stack = []
    for c in exp:
        if c == '(':
            stack.append(c)
        elif c == ')':
            if not stack:
                return False
            stack.pop()
    return len(stack) == 0

def check_brackets_balance(exp):
    return exp.count('[') == exp.count(']')

def starts_with_invalid_operator(exp):
    return bool(exp) and exp[0] in ('*', '+')

def ends_with_invalid_operator(exp):
    return bool(exp) and exp[-1] == '|'

VALID_SYMBOLS = set(
    list("abcdefghijklmnopqrstuvwxyz"
         "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
         "0123456789") +
    ['(', ')', '[', ']', '*', '+', '?', '|', 'ε']
)

def contains_only_valid_characters(exp):
    return all(c in VALID_SYMBOLS for c in exp)

# Función de detección en archivos .yal
def deteccion2(regex):
    if not check_brackets_balance(regex):
        print("Error: La expresión regular no tiene corchetes balanceados.")
        return "Corchetes", regex
    if not check_parenthesis_balance(regex):
        print("Error: La expresión regular no tiene paréntesis balanceados.")
        return "Parent", regex
    if starts_with_invalid_operator(regex):
        print("Error: La expresión regular no puede empezar con '*' o '+'.")
        return "BB", regex
    if ends_with_invalid_operator(regex):
        print("Error: La expresión regular no puede terminar con '|'.")
        return "OF", regex
    if not contains_only_valid_characters(regex):
        print("Error: La expresión regular contiene caracteres inválidos.")
        return False, regex
    return True, regex
