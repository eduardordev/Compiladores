
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
    
    def visit(self, tree):
        """Override the default visit method to ensure our semantic methods are called"""
        if tree is None:
            return None
        
        # Get the method name for this node type
        class_name = tree.__class__.__name__
        
        # Remove 'Context' suffix if present
        if class_name.endswith('Context'):
            base_name = class_name[:-7]  # Remove 'Context'
        else:
            base_name = class_name
            
        method_name = f"visit{base_name}"
        
        # If we have a specific method for this node type, call it
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            result = method(tree)
            # Store the result in node_types for expression nodes
            if base_name in ['Expression', 'AssignmentExpr', 'ConditionalExpr', 'LogicalOrExpr', 
                           'LogicalAndExpr', 'EqualityExpr', 'RelationalExpr', 'AdditiveExpr', 
                           'MultiplicativeExpr', 'UnaryExpr', 'PrimaryExpr', 'LiteralExpr', 
                           'ArrayLiteral', 'LeftHandSide']:
                if result is not None:
                    self.node_types[tree] = result
            return result
        
        # Otherwise, use the default behavior
        result = self.visitChildren(tree)
        # For expression nodes, try to get the type from node_types
        if base_name in ['Expression', 'AssignmentExpr', 'ConditionalExpr', 'LogicalOrExpr', 
                       'LogicalAndExpr', 'EqualityExpr', 'RelationalExpr', 'AdditiveExpr', 
                       'MultiplicativeExpr', 'UnaryExpr', 'PrimaryExpr', 'LiteralExpr', 
                       'ArrayLiteral', 'LeftHandSide']:
            if result is None and tree in self.node_types:
                return self.node_types[tree]
        return result

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
        # Visitar cada statement individualmente
        for stmt in ctx.statement():
            if self.block_terminated[-1]:
                self.warnings.append(f'Código inalcanzable después de return/break/continue en línea {stmt.start.line}')
                break
            self.visit(stmt)
        self.block_terminated.pop()
        return None

    def visitBlock(self, ctx):
        # create a new nested scope for the block
        try:
            self.symtab.push_scope('block')
        except Exception:
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
        try:
            self.symtab.pop_scope()
        except Exception:
            self.symtab.pop()
        return None

    def visitStatement(self, ctx):
        # Visitar el statement específico basado en cuál está presente
        if ctx.variableDeclaration():
            return self.visit(ctx.variableDeclaration())
        elif ctx.constantDeclaration():
            return self.visit(ctx.constantDeclaration())
        elif ctx.assignment():
            return self.visit(ctx.assignment())
        elif ctx.functionDeclaration():
            return self.visit(ctx.functionDeclaration())
        elif ctx.classDeclaration():
            return self.visit(ctx.classDeclaration())
        elif ctx.expressionStatement():
            return self.visit(ctx.expressionStatement())
        elif ctx.printStatement():
            return self.visit(ctx.printStatement())
        elif ctx.block():
            return self.visit(ctx.block())
        elif ctx.ifStatement():
            return self.visit(ctx.ifStatement())
        elif ctx.whileStatement():
            return self.visit(ctx.whileStatement())
        elif ctx.doWhileStatement():
            return self.visit(ctx.doWhileStatement())
        elif ctx.forStatement():
            return self.visit(ctx.forStatement())
        elif ctx.foreachStatement():
            return self.visit(ctx.foreachStatement())
        elif ctx.tryCatchStatement():
            return self.visit(ctx.tryCatchStatement())
        elif ctx.switchStatement():
            return self.visit(ctx.switchStatement())
        elif ctx.breakStatement():
            return self.visit(ctx.breakStatement())
        elif ctx.continueStatement():
            return self.visit(ctx.continueStatement())
        elif ctx.returnStatement():
            return self.visit(ctx.returnStatement())
        else:
            raise at(ctx, 'Statement desconocido')

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
        if not getattr(cond_t, 'is_boolean', lambda: False)():
            raise at(ctx, f'Condición de if debe ser boolean, obtuvo {cond_t}')
        # cuerpo(s)
        if hasattr(ctx, 'statement'):
            st = list(ctx.statement())
            if len(st) >= 1:
                # then-branch in new scope
                try: self.symtab.push_scope('if-then')
                except Exception: self.symtab.push('if-then')
                try:
                    self.visit(st[0])
                finally:
                    try: self.symtab.pop_scope()
                    except Exception: self.symtab.pop()
            if len(st) >= 2:
                # else-branch
                try: self.symtab.push_scope('if-else')
                except Exception: self.symtab.push('if-else')
                try:
                    self.visit(st[1])
                finally:
                    try: self.symtab.pop_scope()
                    except Exception: self.symtab.pop()
        return None

    def visitWhileStatement(self, ctx):
        cond_t = self.visit(ctx.expression())
        if not getattr(cond_t, 'is_boolean', lambda: False)():
            raise at(ctx, f'Condición de while debe ser boolean, obtuvo {cond_t}')
        self.in_loop += 1
        try: self.symtab.push_scope('while')
        except Exception: self.symtab.push('while')
        try:
            self.visit(ctx.statement())
        finally:
            try: self.symtab.pop_scope()
            except Exception: self.symtab.pop()
            self.in_loop -= 1
        return None

    def visitDoWhileStatement(self, ctx):
        self.in_loop += 1
        try: self.symtab.push_scope('do-while')
        except Exception: self.symtab.push('do-while')
        try:
            self.visit(ctx.statement())
        finally:
            try: self.symtab.pop_scope()
            except Exception: self.symtab.pop()
            self.in_loop -= 1
        cond_t = self.visit(ctx.expression())
        if not getattr(cond_t, 'is_boolean', lambda: False)():
            raise at(ctx, f'Condición de do-while debe ser boolean, obtuvo {cond_t}')
        return None

    def visitForStatement(self, ctx):
        # for '(' (variableDeclaration | assignment | )? ';' expression? ';' assignment? ')' statement
        if hasattr(ctx, 'expression') and ctx.expression():
            cond_t = self.visit(ctx.expression())
            if not getattr(cond_t, 'is_boolean', lambda: False)():
                raise at(ctx, f'Condición de for debe ser boolean, obtuvo {cond_t}')
        self.in_loop += 1
        try: self.symtab.push_scope('for')
        except Exception: self.symtab.push('for')
        try:
            self.visit(ctx.statement())
        finally:
            try: self.symtab.pop_scope()
            except Exception: self.symtab.pop()
            self.in_loop -= 1
        return None

    def visitForeachStatement(self, ctx):
        # foreach '(' Identifier 'in' expression ')' statement
        cont_t = self.visit(ctx.expression())
        if not cont_t or not cont_t.is_array():
            raise at(ctx, f'foreach requiere arreglo, obtuvo {cont_t}')
        loop_name = ctx.Identifier().getText()
        try: self.symtab.push_scope('foreach')
        except Exception: self.symtab.push('foreach')
        try:
            self.symtab.define(VarSymbol(loop_name, cont_t.base, False))
        except KeyError:
            raise at(ctx, f'Redeclaración de variable en foreach: {loop_name}')
        self.in_loop += 1
        self.visit(ctx.statement())
        self.in_loop -= 1
        try: self.symtab.pop_scope()
        except Exception: self.symtab.pop()
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
        try: self.symtab.push_scope('try')
        except Exception: self.symtab.push('try')
        self.visit(ctx.block(0))
        try: self.symtab.pop_scope()
        except Exception: self.symtab.pop()
        try: self.symtab.push_scope('catch')
        except Exception: self.symtab.push('catch')
        err_name = ctx.Identifier().getText()
        try:
            self.symtab.define(VarSymbol(err_name, STRING, False))
        except KeyError:
            raise at(ctx, f'Identificador de catch duplicado: {err_name}')
        self.visit(ctx.block(1))
        try: self.symtab.pop_scope()
        except Exception: self.symtab.pop()
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
    def visitExpression(self, ctx):
        # expression: assignmentExpr
        if hasattr(ctx, 'assignmentExpr') and ctx.assignmentExpr():
            return self.visit(ctx.assignmentExpr())
        # Use default behavior to delegate to children
        return self.visitChildren(ctx)

    def visitAssignmentExpr(self, ctx):
        # assignmentExpr: lhs=leftHandSide '=' assignmentExpr | conditionalExpr
        if ctx.leftHandSide() and ctx.assignmentExpr():
            # Assignment case: lhs = assignmentExpr
            lhs = ctx.leftHandSide()
            rhs = ctx.assignmentExpr()
            lhs_t = self.visit(lhs)
            rhs_t = self.visit(rhs)
            if not are_compatible(lhs_t, rhs_t):
                raise at(ctx, f'Asignación incompatible: {lhs_t} := {rhs_t}')
            return rhs_t
        else:
            # Non-assignment case: conditionalExpr
            return self.visit(ctx.conditionalExpr())

    # labeled alternatives for assignmentExpr
    def visitAssignExpr(self, ctx):
        # lhs=leftHandSide '=' assignmentExpr
        lhs_t = self.visit(ctx.leftHandSide())
        rhs_t = self.visit(ctx.assignmentExpr())
        if not are_compatible(lhs_t, rhs_t):
            raise at(ctx, f'Asignación incompatible: {lhs_t} := {rhs_t}')
        return rhs_t

    def visitPropertyAssignExpr(self, ctx):
        # lhs.property = assignmentExpr (propiedades no tipadas, solo validar rhs)
        rhs_t = self.visit(ctx.assignmentExpr())
        return rhs_t

    def visitExprNoAssign(self, ctx):
        return self.visit(ctx.conditionalExpr())

    def visitConditionalExpr(self, ctx):
        # conditionalExpr: logicalOrExpr ('?' expression ':' expression)?
        t = self.visit(ctx.logicalOrExpr())
        if ctx.expression():
            # Ternary operator case
            true_t = self.visit(ctx.expression(0))
            false_t = self.visit(ctx.expression(1))
            if not are_compatible(true_t, false_t):
                raise at(ctx, f'Operador ternario incompatible: {true_t} vs {false_t}')
            return true_t
        return t

    def visitTernaryExpr(self, ctx):
        return self.visitConditionalExpr(ctx)

    def visitLogicalOrExpr(self, ctx):
        # logicalOrExpr: logicalAndExpr ('||' logicalAndExpr)* ;
        t = self.visit(ctx.logicalAndExpr(0))
        for i in range(1, len(ctx.logicalAndExpr())):
            t2 = self.visit(ctx.logicalAndExpr(i))
            if not getattr(t, 'is_boolean', lambda: False)() or not getattr(t2, 'is_boolean', lambda: False)():
                raise at(ctx, f'Operación lógica || requiere booleanos: {t}, {t2}')
            t = BOOLEAN
        return self.set_type(ctx, t)

    def visitLogicalAndExpr(self, ctx):
        t = self.visit(ctx.equalityExpr(0))
        for i in range(1, len(ctx.equalityExpr())):
            t2 = self.visit(ctx.equalityExpr(i))
            if not getattr(t, 'is_boolean', lambda: False)() or not getattr(t2, 'is_boolean', lambda: False)():
                raise at(ctx, f'Operación lógica && requiere booleanos: {t}, {t2}')
            t = BOOLEAN
        return self.set_type(ctx, t)

    def visitEqualityExpr(self, ctx):
        t1 = self.visit(ctx.relationalExpr(0))
        for i in range(1, len(ctx.relationalExpr())):
            t2 = self.visit(ctx.relationalExpr(i))
            if not are_compatible(t1, t2):
                raise at(ctx, f'Igualdad inválida para {t1} y {t2}')
            t1 = BOOLEAN
        return self.set_type(ctx, t1)

    def visitRelationalExpr(self, ctx):
        t1 = self.visit(ctx.additiveExpr(0))
        for i in range(1, len(ctx.additiveExpr())):
            t2 = self.visit(ctx.additiveExpr(i))
            if not result_numeric(t1, t2):
                raise at(ctx, f'Relacional inválida para {t1} y {t2}')
            t1 = BOOLEAN
        return self.set_type(ctx, t1)

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
        if hasattr(ctx, 'literalExpr') and ctx.literalExpr():
            return self.set_type(ctx, self.visit(ctx.literalExpr()))
        if hasattr(ctx, 'leftHandSide') and ctx.leftHandSide():
            return self.set_type(ctx, self.visit(ctx.leftHandSide()))
        if hasattr(ctx, 'expression') and ctx.expression():
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
        base = None
        base_type = VOID

        # resolver identificador/base inicial
        if ctx.primaryAtom():
            base = self.visit(ctx.primaryAtom())
            base_type = base.type if isinstance(base, Symbol) else base
        # por compatibilidad, intentar Identifier directo (aunque la regla no lo expone)
        elif ctx.Identifier():
            name = ctx.Identifier().getText()
            base = self.symtab.resolve(name)
            if not base:
                if self.capture_stack:
                    self.capture_stack[-1].add(name)
                raise at(ctx, f'Identificador no declarado: {name}')
            base_type = base.type

        # procesar sufijos (llamadas, indexación, propiedades)
        for sfx in ctx.suffixOp():
            if isinstance(sfx, CompiscriptParser.CallExprContext):
                if not isinstance(base, FuncSymbol):
                    raise at(sfx, 'Llamada sobre un objetivo que no es función')
                args_ctx = sfx.arguments().expression() if sfx.arguments() else []
                if len(args_ctx) != len(base.params):
                    raise at(sfx, f'Cantidad de argumentos inválida para {base.name}: {len(args_ctx)} vs {len(base.params)}')
                for arg_expr, param in zip(args_ctx, base.params):
                    atype = self.visit(arg_expr)
                    if not are_compatible(param.type, atype):
                        raise at(arg_expr, f'Argumento incompatible para {base.name}: esperado {param.type}, obtuvo {atype}')
                base_type = base.type
                base = None  # después de la llamada, el resultado es un valor
            elif isinstance(sfx, CompiscriptParser.IndexExprContext):
                if not base_type or not base_type.is_array():
                    raise at(sfx, f'Indexación requiere arreglo, obtuvo {base_type}')
                idx_t = self.visit(sfx.expression())
                if not getattr(idx_t, 'is_numeric', lambda: False)():
                    raise at(sfx, f'Índice debe ser numérico, obtuvo {idx_t}')
                base_type = base_type.base
            elif isinstance(sfx, CompiscriptParser.PropertyAccessExprContext):
                # soporte básico: no conocemos miembros, retornamos void para evitar falsos positivos
                base_type = VOID

        return self.set_type(ctx, base_type)

    def visitPrimaryAtom(self, ctx):
        # Identifier | new Identifier '(' arguments? ')' | this
        if isinstance(ctx, CompiscriptParser.IdentifierExprContext):
            name = ctx.Identifier().getText()
            sym = self.symtab.resolve(name)
            if not sym:
                if self.capture_stack:
                    self.capture_stack[-1].add(name)
                raise at(ctx, f'Identificador no declarado: {name}')
            return sym
        if isinstance(ctx, CompiscriptParser.NewExprContext):
            cname = ctx.Identifier().getText()
            sym = self.symtab.resolve(cname)
            if not sym or not isinstance(sym, ClassSymbol):
                raise at(ctx, f'Clase no declarada: {cname}')
            return sym.type
        if isinstance(ctx, CompiscriptParser.ThisExprContext):
            sym = self.symtab.resolve('this')
            return sym.type if sym else Type('this')
        return VOID

    def visitIdentifierExpr(self, ctx):
        return self.visitPrimaryAtom(ctx)

    def visitNewExpr(self, ctx):
        return self.visitPrimaryAtom(ctx)

    def visitThisExpr(self, ctx):
        return self.visitPrimaryAtom(ctx)

    def visitArguments(self, ctx):
        # '(' (expression (',' expression)*)? ')'
        # usado por llamadas; validamos en visitLeftHandSide cuando resolvemos función
        return None
