# yal_utils.py

import os
from reg import evaluar
from Thompson import alfabeto
from ErroresArchivo import deteccion2
from Errores import deteccion
from SintaxT import SintaxT

def _preprocess_expr(expr: str) -> str:
    """
    Si expr está en corchetes [...], lo convierte
    en una clase de carácter válida [a-zA-Z...].
    """
    e = expr.strip()
    if e.startswith('[') and e.endswith(']'):
        inner = e[1:-1].replace("'", "")
        parts = inner.split()
        ranges = []
        for p in parts:
            if len(p) == 3 and p[1] == '-':        # caso 'a-z'
                ranges.append(f"{p[0]}-{p[2]}")
            else:
                if p == '\\t': ranges.append(r'\t')
                elif p == '\\n': ranges.append(r'\n')
                else: ranges.append(p)
        return '[' + ''.join(ranges) + ']'
    return expr

def parse_yal(path):
    """
    Parsea un .yal y devuelve:
     (lista_diccionarios, lista_iniciales, lista_finales,
      tabla, operadores_reservados, tokens)
    aplicando la preprocesación de corchetes antes de validar.
    """
    data = open(path, encoding='utf-8').read()

    # 1) Extraer let X = R
    variables = []
    for line in data.splitlines():
        s = line.strip()
        if s.startswith("let ") and "=" in s:
            name, expr = s[len("let "):].split("=", 1)
            variables.append((name.strip(), expr.strip()))

    # 2) Transformar y validar cada expr
    tabla = {}
    for name, raw in variables:
        expr = _preprocess_expr(raw)
        ok, _ = deteccion2(expr)
        if not ok:
            print(f"[WARN] Regex inválida tras preprocesar '{name}': {expr}")
        tabla[name] = expr

    # 3) Extraer operadores / tokens de "rule gettoken ="
    operadores_reservados = []
    tokens = []
    marker = "rule gettoken ="
    idx = data.find(marker)
    if idx != -1:
        part = data[idx + len(marker):]
        for seg in part.split("|"):
            if "return" in seg:
                val = seg.split("return",1)[1].strip().strip('"')
                tokens.append(val)
        for v in tokens[:]:
            if v in ["*","^","+","-","/","(",")","{","}","[","]","<",">","="]:
                operadores_reservados.append(v)
                tokens.remove(v)

    # 4) Construir AFDs con SintaxT
    lista_diccionarios = []
    lista_iniciales  = []
    lista_finales    = []
    for expr in tabla.values():
        r = expr.replace("?", "|ε").replace("'", "")
        if not deteccion(r):
            print(f"[WARN] No se pudo validar regex: {expr}")
            continue
        post = evaluar(r)
        alf  = alfabeto(r)
        arbol = SintaxT(post, alf)
        lista_diccionarios.append(arbol.dict)
        lista_iniciales .append([arbol.EstadoInicial])
        lista_finales   .append(arbol.EstadosAceptAFD)

    return lista_diccionarios, lista_iniciales, lista_finales, tabla, operadores_reservados, tokens

def generate_afd_diagrams(parsed, output_dir):
    """
    Exporta un PNG por cada AFD usando graphviz.
    """
    try:
        import graphviz
    except ImportError:
        print("[ERROR] Instala graphviz: pip install graphviz")
        return

    Ld, _, Lf, _, _, _ = parsed
    os.makedirs(output_dir, exist_ok=True)
    for i, trans in enumerate(Ld):
        dot = graphviz.Digraph(comment=f'AFD_{i}')
        for st in trans:
            shape = 'doublecircle' if st in Lf[i] else 'circle'
            dot.node(str(st), shape=shape)
        for st, edges in trans.items():
            for sym, dst in edges.items():
                dot.edge(str(st), str(dst), label=sym)
        out = os.path.join(output_dir, f'afd_{i}')
        dot.render(out, format='png', cleanup=True)
        print(f"[OK] Diagrama AFD {i}: {out}.png")
