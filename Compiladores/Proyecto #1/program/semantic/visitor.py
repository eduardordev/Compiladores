
from typing import Any, Dict, Optional, List
from antlr4 import ParserRuleContext

from .typesys import *
from .symbols import *
from .errors import SemanticError, at

from CompiscriptVisitor import CompiscriptVisitor
from CompiscriptParser import CompiscriptParser

class SemanticVisitor(CompiscriptVisitor):
    def __init__(self):
        super().__init__()
        self.symtab = SymbolTable()
        self.node_types: Dict[ParserRuleContext, Type] = {}
        self.in_loop: int = 0
        self.in_function: int = 0
        self.expected_return: List[Type] = []
        self.capture_stack: List[set] = []
        self.block_terminated: List[bool] = []
        self.warnings: List[str] = []

    # util
    def set_type(self, ctx, t: Type):
        self.node_types[ctx] = t
        return t
    def get_type(self, ctx):
        return self.node_types.get(ctx)
    def mark_terminated(self):
        if self.block_terminated:
            self.block_terminated[-1] = True

    # program / block
    def visitProgram(self, ctx):
        self.block_terminated.append(False)
        res = self.visitChildren(ctx)
        self.block_terminated.pop()
        return res

    def visitBlock(self, ctx):
        self.symtab.push('block')
        self.block_terminated.append(False)
        # recorrer statements si existen
        stmts = []
        if hasattr(ctx, 'statement'):  # block: '{' statement* '}'
            stmts = list(ctx.statement())
        for st in stmts:
            if self.block_terminated[-1]:
                self.warnings.append(f'Código inalcanzable después de return/break/continue en línea {st.start.line}')
                break
            self.visit(st)
        self.block_terminated.pop()
        self.symtab.pop()
        return None

    # declarations
    def visitVariableDeclaration(self, ctx):
        # 'let' Identifier typeAnnotation? initializer? ';'
        name = ctx.Identifier().getText() if hasattr(ctx, 'Identifier') and ctx.Identifier() else None
        if not name:
            raise at(ctx, 'Declaración de variable sin identificador')
        declared_type = None
        if hasattr(ctx, 'typeAnnotation') and ctx.typeAnnotation():
            declared_type = self.visit(ctx.typeAnnotation())
        if hasattr(ctx, 'initializer') and ctx.initializer():
            expr_t = self.visit(ctx.initializer())
            if declared_type and not are_compatible(declared_type, expr_t):
                raise at(ctx, f'Asignación incompatible: {declared_type} := {expr_t}')
            if not declared_type:
                declared_type = expr_t
        else:
            if not declared_type:
                raise at(ctx, f"Variable '{name}' requiere tipo o inicialización")
        try:
            self.symtab.define(VarSymbol(name, declared_type, False))
        except KeyError:
            raise at(ctx, f'Redeclaración de identificador: {name}')
        return None

    def visitConstantDeclaration(self, ctx):
        # 'const' Identifier typeAnnotation? initializer ';'  (inicialización obligatoria)
        name = ctx.Identifier().getText()
        declared_type = None
        if hasattr(ctx, 'typeAnnotation') and ctx.typeAnnotation():
            declared_type = self.visit(ctx.typeAnnotation())
        if not (hasattr(ctx, 'initializer') and ctx.initializer()):
            raise at(ctx, f"Constante '{name}' debe inicializarse")
        expr_t = self.visit(ctx.initializer())
        if declared_type and not are_compatible(declared_type, expr_t):
            raise at(ctx, f'Asignación incompatible: {declared_type} := {expr_t}')
        if not declared_type:
            declared_type = expr_t
        try:
            self.symtab.define(VarSymbol(name, declared_type, True))
        except KeyError:
            raise at(ctx, f'Redeclaración de identificador: {name}')
        return None

    def visitTypeAnnotation(self, ctx):
        # ':' type
        return self.visit(ctx.type_())

    def visitType(self, ctx):
        # may include array e.g., baseType '[]'*
        txt = ctx.getText()
        if txt.endswith('[]'):
            base = txt[:-2]
            base_t = PRIMS.get(base)
            if not base_t:
                raise at(ctx, f'Tipo base de arreglo no soportado: {base}')
            return array_of(base_t)
        if txt in PRIMS:
            return PRIMS[txt]
        return Type(txt)  # para clases

    def visitInitializer(self, ctx):
        # '=' expression
        # compatible con grammar: initializer: '=' expression ;
        # Tomamos tipo de expression
        # buscar subnodo expression
        if hasattr(ctx, 'expression') and ctx.expression():
            return self.visit(ctx.expression())
        # fallback
        for ch in ctx.getChildren():
            if hasattr(ch, 'accept'):
                t = self.visit(ch)
                if t is not None:
                    return t
        return VOID

    # assignment
    def visitAssignment(self, ctx):
        # leftHandSide '=' expression ';'
        # Tomamos nombre de Identifier del leftHandSide si aplica
        lhs_t = None
        name = None
        if hasattr(ctx, 'leftHandSide') and ctx.leftHandSide():
            # leftHandSide -> Identifier | member access | index
            lhs = ctx.leftHandSide()
            # intentar extraer Identifier simple
            if hasattr(lhs, 'Identifier') and lhs.Identifier():
                name = lhs.Identifier().getText()
                sym = self.symtab.resolve(name)
                if not sym or not isinstance(sym, VarSymbol):
                    raise at(ctx, f'Variable no declarada: {name}')
                if sym.is_const:
                    raise at(ctx, f'No se puede asignar a constante: {name}')
                lhs_t = sym.type
            else:
                # acceso a arreglo u objeto -> visit para conocer tipo esperado
                lhs_t = self.visit(lhs)
        rhs_t = self.visit(ctx.expression())
        if lhs_t and not are_compatible(lhs_t, rhs_t):
            # si no conocemos lhs_t (p.ej., atributo), no podemos validar fuerte
            raise at(ctx, f'Asignación incompatible: {lhs_t} := {rhs_t}')
        return None

    # expressionStatement
    def visitExpressionStatement(self, ctx):
        if hasattr(ctx, 'expression'):
            self.visit(ctx.expression())
        return None

    # printStatement (si se usa)
    def visitPrintStatement(self, ctx):
        if hasattr(ctx, 'arguments') and ctx.arguments():
            for e in ctx.arguments().expression():
                self.visit(e)
        return None

    # control flow
    def visitIfStatement(self, ctx):
        cond_t = self.visit(ctx.expression())
        if cond_t != BOOLEAN:
            raise at(ctx, f'Condición de if debe ser boolean, obtuvo {cond_t}')
        # cuerpo(s)
        if hasattr(ctx, 'statement'):
            st = list(ctx.statement())
            if len(st) >= 1:
                self.visit(st[0])
            if len(st) >= 2:
                self.visit(st[1])
        return None

    def visitWhileStatement(self, ctx):
        cond_t = self.visit(ctx.expression())
        if cond_t != BOOLEAN:
            raise at(ctx, f'Condición de while debe ser boolean, obtuvo {cond_t}')
        self.in_loop += 1
        self.visit(ctx.statement())
        self.in_loop -= 1
        return None

    def visitDoWhileStatement(self, ctx):
        self.in_loop += 1
        self.visit(ctx.statement())
        self.in_loop -= 1
        cond_t = self.visit(ctx.expression())
        if cond_t != BOOLEAN:
            raise at(ctx, f'Condición de do-while debe ser boolean, obtuvo {cond_t}')
        return None

    def visitForStatement(self, ctx):
        # for '(' (variableDeclaration | assignment | )? ';' expression? ';' assignment? ')' statement
        if hasattr(ctx, 'expression') and ctx.expression():
            cond_t = self.visit(ctx.expression())
            if cond_t != BOOLEAN:
                raise at(ctx, f'Condición de for debe ser boolean, obtuvo {cond_t}')
        self.in_loop += 1
        self.visit(ctx.statement())
        self.in_loop -= 1
        return None

    def visitForeachStatement(self, ctx):
        # foreach '(' Identifier 'in' expression ')' statement
        cont_t = self.visit(ctx.expression())
        if not cont_t or not cont_t.is_array():
            raise at(ctx, f'foreach requiere arreglo, obtuvo {cont_t}')
        loop_name = ctx.Identifier().getText()
        self.symtab.push('foreach')
        try:
            self.symtab.define(VarSymbol(loop_name, cont_t.base, False))
        except KeyError:
            raise at(ctx, f'Redeclaración de variable en foreach: {loop_name}')
        self.in_loop += 1
        self.visit(ctx.statement())
        self.in_loop -= 1
        self.symtab.pop()
        return None

    def visitBreakStatement(self, ctx):
        if self.in_loop == 0:
            raise at(ctx, "'break' sólo dentro de bucles")
        self.mark_terminated()
        return None

    def visitContinueStatement(self, ctx):
        if self.in_loop == 0:
            raise at(ctx, "'continue' sólo dentro de bucles")
        self.mark_terminated()
        return None

    # try/catch
    def visitTryCatchStatement(self, ctx):
        self.symtab.push('try')
        self.visit(ctx.block(0))
        self.symtab.pop()
        self.symtab.push('catch')
        err_name = ctx.Identifier().getText()
        try:
            self.symtab.define(VarSymbol(err_name, STRING, False))
        except KeyError:
            raise at(ctx, f'Identificador de catch duplicado: {err_name}')
        self.visit(ctx.block(1))
        self.symtab.pop()
        return None

    # switch/case
    def visitSwitchStatement(self, ctx):
        discr_t = self.visit(ctx.expression())
        for cc in ctx.switchCase():
            lit_t = self.visit(cc.expression())
            if not are_compatible(discr_t, lit_t):
                raise at(cc, f"Tipo de 'case' incompatible con switch: {lit_t} vs {discr_t}")
            for st in cc.statement():
                self.visit(st)
        if ctx.defaultCase():
            for st in ctx.defaultCase().statement():
                self.visit(st)
        return None

    # functions
    def visitFunctionDeclaration(self, ctx):
        fname = ctx.Identifier().getText()
        ret = VOID
        if ctx.type_():
            ret = self.visit(ctx.type_())
        params: List[VarSymbol] = []
        if ctx.parameters():
            for p in ctx.parameters().parameter():
                pname = p.Identifier().getText()
                ptype = self.visit(p.type_()) if p.type_() else VOID
                params.append(VarSymbol(pname, ptype))
        fsym = FuncSymbol(fname, ret, params)
        try:
            self.symtab.define(fsym)
        except KeyError:
            raise at(ctx, f'Función ya definida: {fname}')
        self.symtab.push(f'func {fname}')
        for ps in params:
            try: self.symtab.define(ps)
            except KeyError: raise at(ctx, f'Parámetro duplicado: {ps.name}')
        self.in_function += 1
        self.expected_return.append(ret)
        self.capture_stack.append(set())
        self.visit(ctx.block())
        self.capture_stack.pop()
        self.expected_return.pop()
        self.in_function -= 1
        self.symtab.pop()
        return None

    def visitReturnStatement(self, ctx):
        if self.in_function == 0:
            raise at(ctx, "'return' sólo permitido dentro de funciones")
        expected = self.expected_return[-1] if self.expected_return else VOID
        got = VOID
        if ctx.expression():
            got = self.visit(ctx.expression())
        if expected == VOID and got != VOID:
            raise at(ctx, f'La función es void; return con valor {got} no permitido')
        if expected != VOID and got == VOID:
            raise at(ctx, f'La función debe devolver {expected}; return sin valor')
        if expected != VOID and not are_compatible(expected, got):
            raise at(ctx, f'Tipo de retorno incompatible: esperado {expected}, obtuvo {got}')
        self.mark_terminated()
        return None

    # classes
    def visitClassDeclaration(self, ctx):
        cname = ctx.Identifier(0).getText()
        csym = ClassSymbol(cname, Type(cname))
        try:
            self.symtab.define(csym)
        except KeyError:
            raise at(ctx, f'Clase ya definida: {cname}')
        self.symtab.push(f'class {cname}')
        for m in ctx.classMember():
            self.visit(m)
        self.symtab.pop()
        return None

    def visitClassMember(self, ctx):
        # puede ser functionDeclaration | variableDeclaration | constantDeclaration
        if ctx.functionDeclaration():
            self.visit(ctx.functionDeclaration())
        elif ctx.variableDeclaration():
            self.visit(ctx.variableDeclaration())
        elif ctx.constantDeclaration():
            self.visit(ctx.constantDeclaration())
        return None

    # expressions (precedence)
    def visitLogicalOrExpr(self, ctx):
        # logicalOrExpr: logicalAndExpr ('||' logicalAndExpr)* ;
        t = self.visit(ctx.logicalAndExpr(0))
        for i in range(1, len(ctx.logicalAndExpr())):
            t2 = self.visit(ctx.logicalAndExpr(i))
            if t != BOOLEAN or t2 != BOOLEAN:
                raise at(ctx, f'Operación lógica || requiere booleanos: {t}, {t2}')
            t = BOOLEAN
        return self.set_type(ctx, BOOLEAN)

    def visitLogicalAndExpr(self, ctx):
        t = self.visit(ctx.equalityExpr(0))
        for i in range(1, len(ctx.equalityExpr())):
            t2 = self.visit(ctx.equalityExpr(i))
            if t != BOOLEAN or t2 != BOOLEAN:
                raise at(ctx, f'Operación lógica && requiere booleanos: {t}, {t2}')
            t = BOOLEAN
        return self.set_type(ctx, BOOLEAN)

    def visitEqualityExpr(self, ctx):
        t1 = self.visit(ctx.relationalExpr(0))
        for i in range(1, len(ctx.relationalExpr())):
            t2 = self.visit(ctx.relationalExpr(i))
            if not are_compatible(t1, t2):
                raise at(ctx, f'Igualdad inválida para {t1} y {t2}')
            t1 = BOOLEAN
        return self.set_type(ctx, BOOLEAN)

    def visitRelationalExpr(self, ctx):
        t1 = self.visit(ctx.additiveExpr(0))
        for i in range(1, len(ctx.additiveExpr())):
            t2 = self.visit(ctx.additiveExpr(i))
            if not result_numeric(t1, t2):
                raise at(ctx, f'Relacional inválida para {t1} y {t2}')
            t1 = BOOLEAN
        return self.set_type(ctx, BOOLEAN)

    def visitAdditiveExpr(self, ctx):
        t = self.visit(ctx.multiplicativeExpr(0))
        for i in range(1, len(ctx.multiplicativeExpr())):
            t2 = self.visit(ctx.multiplicativeExpr(i))
            # '+' permite string+string
            txt = ctx.getText()
            if '\"' in txt and '+' in txt and t == STRING and t2 == STRING:
                t = STRING
            else:
                rt = result_numeric(t, t2)
                if not rt:
                    raise at(ctx, f"'+'/'-' inválido para {t} y {t2}")
                t = rt
        return self.set_type(ctx, t)

    def visitMultiplicativeExpr(self, ctx):
        t = self.visit(ctx.unaryExpr(0))
        for i in range(1, len(ctx.unaryExpr())):
            t2 = self.visit(ctx.unaryExpr(i))
            rt = result_numeric(t, t2)
            if not rt:
                raise at(ctx, f"'*'/'/' inválido para {t} y {t2}")
            t = rt
        return self.set_type(ctx, t)

    def visitUnaryExpr(self, ctx):
        # ('!' | '-' | '+')* primaryExpr
        t = self.visit(ctx.primaryExpr())
        ops = []
        for ch in ctx.getChildren():
            tx = getattr(ch, 'getText', lambda: '')()
            if tx in ('!', '-', '+'):
                ops.append(tx)
        for op in ops:
            if op == '!':
                if t != BOOLEAN:
                    raise at(ctx, f"'!' requiere boolean, obtuvo {t}")
                t = BOOLEAN
            else:
                if not is_numeric(t):
                    raise at(ctx, f"Operador '{op}' requiere integer/float, obtuvo {t}")
        return self.set_type(ctx, t)

    def visitPrimaryExpr(self, ctx):
        # puede delegar a literalExpr, leftHandSide, arrayLiteral, '(' expression ')'
        if ctx.literalExpr():
            return self.set_type(ctx, self.visit(ctx.literalExpr()))
        if ctx.arrayLiteral():
            return self.set_type(ctx, self.visit(ctx.arrayLiteral()))
        if ctx.leftHandSide():
            return self.set_type(ctx, self.visit(ctx.leftHandSide()))
        if ctx.expression():
            return self.set_type(ctx, self.visit(ctx.expression()))
        return self.set_type(ctx, VOID)

    def visitLiteralExpr(self, ctx):
        tx = ctx.getText()
        if tx in ('true','false'):
            return BOOLEAN
        if tx == 'null':
            return NULL
        if tx.startswith('\"') and tx.endswith('\"'):
            return STRING
        # si es número
        return FLOAT if '.' in tx else INTEGER

    def visitArrayLiteral(self, ctx):
        # '[' (expression (',' expression)*)? ']'
        if len(ctx.expression()) == 0:
            raise at(ctx, 'Arreglo vacío requiere anotación de tipo')
        elem_t = self.visit(ctx.expression(0))
        for i in range(1, len(ctx.expression())):
            ti = self.visit(ctx.expression(i))
            if not are_compatible(elem_t, ti):
                raise at(ctx, f'Elementos de arreglo no homogéneos: {elem_t} y {ti}')
        return array_of(elem_t)

    # leftHandSide / primaryAtom / suffixOp / arguments (según gramática)
    def visitLeftHandSide(self, ctx):
        # Puede ser Identifier | acceso con '.' | indexación '[]' | llamada
        if ctx.Identifier():
            name = ctx.Identifier().getText()
            sym = self.symtab.resolve(name)
            if not sym:
                # captura tentativa en closures
                if self.capture_stack:
                    self.capture_stack[-1].add(name)
                raise at(ctx, f'Identificador no declarado: {name}')
            return sym.type
        # Si tiene primaryAtom() u otros, delegamos
        for ch in ctx.getChildren():
            if hasattr(ch, 'accept'):
                t = self.visit(ch)
                if t is not None:
                    return t
        return VOID

    def visitArguments(self, ctx):
        # '(' (expression (',' expression)*)? ')'
        # usado por llamadas; validamos en visitLeftHandSide cuando resolvemos función
        return None
