from CompiscriptVisitor import CompiscriptVisitor
from CompiscriptParser import CompiscriptParser
from codegen.tac import Emitter


class CodeGenVisitor(CompiscriptVisitor):
    def __init__(self):
        super().__init__()
        self.em = Emitter()

    def _expr_node(self, node):
        """Helper: ANTLR may return a single node or a list; normalize to single node or None."""
        if node is None:
            return None
        try:
            # list-like from ANTLR
            if isinstance(node, list) or (hasattr(node, '__len__') and not hasattr(node, 'getChildCount')):
                return node[0] if len(node) > 0 else None
        except Exception:
            pass
        return node

    def visit(self, tree):  # type: ignore[override]
        if tree is None:
            return None
        method_name = 'visit' + type(tree).__name__.replace('Context', '')
        visitor = getattr(self, method_name, None)
        if visitor:
            return visitor(tree)
        return super().visit(tree)

    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        # Visitar explícitamente cada statement para asegurar recorrido completo
        idx = 0
        while True:
            st = ctx.statement(idx)
            if st is None:
                break
            self.visit(st)
            idx += 1
    def visit(self, tree):
        # Robust: if given a list of nodes, visit each and return last result
        if tree is None:
            return None
        if isinstance(tree, list):
            last = None
            for t in tree:
                last = self.visit(t)
            return last

        class_name = tree.__class__.__name__
        base_name = class_name[:-7] if class_name.endswith('Context') else class_name
        method_name = f"visit{base_name}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(tree)
        return self.visitChildren(tree)

    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        # Visit every top-level statement explicitly
        if hasattr(ctx, 'statement'):
            for st in ctx.statement():
                self.visit(st)
        return self.em

    def visitStatement(self, ctx):
        for ch in ctx.getChildren():
            if hasattr(ch, 'accept'):
                if type(ch).__name__ == 'VariableDeclarationContext':
                    self.visitVariableDeclaration(ch)
                    continue
                if type(ch).__name__ == 'AssignmentContext':
                    self.visitAssignment(ch)
                    continue
                self.visit(ch)
        return None

    def visitVariableDeclarationStatement(self, ctx):
        if ctx.variableDeclaration():
            return self.visit(ctx.variableDeclaration())

    def visitVariableDeclaration(self, ctx):
        name = ctx.Identifier().getText()

        val = None
        if ctx.initializer():
            init = ctx.initializer()
            for ch in init.getChildren():
                cname = type(ch).__name__
                if 'Expr' in cname or 'Expression' in cname or 'Literal' in cname:
                    val = self.visitAnyExpression(ch)
                    break

        if val is None:
            val = 'undefined'

        self.em.emit('STORE', dst=name, a=val)
        if isinstance(val, str) and val.startswith('t'):
            self.em.free_temp(val)

    def visitAnyExpression(self, ctx):
        """Recursively visit expressions to produce a value or temporary."""
        cname = type(ctx).__name__
        ctext = ctx.getText()
        children = list(ctx.getChildren()) if hasattr(ctx, 'getChildren') else []

        if not hasattr(ctx, 'getChildCount'):
            return None

        if 'Literal' in cname:
            return ctext

        if 'AdditiveExpr' in cname and ctx.getChildCount() > 1:
            left = self.visitAnyExpression(ctx.getChild(0))
            op = ctx.getChild(1).getText()
            right = self.visitAnyExpression(ctx.getChild(2))
            dst = self.em.new_temp()
            self.em.emit('ADD' if op == '+' else 'SUB', dst=dst, a=left, b=right)
            return dst

        if ('RelationalExpr' in cname or 'EqualityExpr' in cname) and ctx.getChildCount() > 1:
            left = self.visitAnyExpression(ctx.getChild(0))
            op = ctx.getChild(1).getText()
            right = self.visitAnyExpression(ctx.getChild(2))
            dst = self.em.new_temp()
            map_op = {
                '==': 'EQ', '!=': 'NE', '<': 'LT', '<=': 'LE', '>': 'GT', '>=': 'GE'
            }
            opcode = map_op.get(op, 'SUB')
            self.em.emit(opcode, dst=dst, a=left, b=right)
            return dst

        # function call handling: detect CallExpr or arguments anywhere in subtree
        def find_call_node(node):
            try:
                if 'CallExpr' in type(node).__name__:
                    return node
                if hasattr(node, 'arguments') and node.arguments():
                    return node
            except Exception:
                pass
            try:
                for i in range(node.getChildCount()):
                    ch = node.getChild(i)
                    res = find_call_node(ch)
                    if res:
                        return res
            except Exception:
                # not a parser node
                return None
            return None

        call_node = find_call_node(ctx)
        if call_node is None:
            # fallback: if textual pattern looks like a call
            if '(' in ctext and ctext.endswith(')'):
                call_node = ctx

        if call_node:
            # HANDLE: constructor 'new Class(...)' -> NEWOBJ
            try:
                if isinstance(ctext, str) and ctext.strip().startswith('new'):
                    # extract class name after 'new'
                    class_name = ctext.replace('new', '', 1).split('(')[0].strip()
                    dst_new = self.em.new_temp()
                    self.em.emit('NEWOBJ', dst=dst_new, a=class_name)
                    return dst_new
            except Exception:
                pass
            # collect evaluated arguments (if present)
            args = []
            try:
                if hasattr(call_node, 'arguments') and call_node.arguments():
                    for ex in call_node.arguments().expression():
                        val = self.visitAnyExpression(ex)
                        if val is not None:
                            args.append(val)
            except Exception:
                pass
            # if no explicit arguments collected, scan children for expressions
            if not args:
                for ch in children:
                    if hasattr(ch, 'accept') and 'Expression' in type(ch).__name__:
                        val = self.visitAnyExpression(ch)
                        if val is not None:
                            args.append(val)
            # if this is a method call like obj.method(...), pass the object as implicit first arg
            emit_args = []
            try:
                left_text = ctext.split('(')[0].strip()
                if '.' in left_text:
                    # method call like obj.method(...)
                    # load receiver and pass as first (implicit) arg
                    obj_name = left_text.split('.', 1)[0].strip()
                    if obj_name:
                        tmp_obj = self.em.new_temp()
                        self.em.emit('LOAD', dst=tmp_obj, a=obj_name)
                        # prefer ARG + CALL to remain compatible with current backend
                        emit_args.append(tmp_obj)
            except Exception:
                pass
            # then append explicit arguments
            for a in args:
                emit_args.append(a)
            for a in emit_args:
                self.em.emit('ARG', a=a)
            dst = self.em.new_temp()
            # find function name: prefer textual extraction from call text before '('
            fname = 'unknown'
            try:
                left = ctext.split('(')[0].strip()
                # Detectar llamada tipo obj.metodo(...)
                if '.' in left:
                    obj_name, method_name = left.split('.', 1)
                    # Nombre real de la función es el método
                    # (el receptor ya fue cargado y añadido a `emit_args` más arriba)
                    fname = method_name.strip()
                else:
                    # Nombre por defecto: texto antes de '('
                    if left:
                        fname = left
                    else:
                        # fallback: search identifier in subtree
                        def find_identifier(node):
                            try:
                                if hasattr(node, 'Identifier') and node.Identifier():
                                    return node.Identifier().getText()
                            except Exception:
                                pass
                            try:
                                for i in range(node.getChildCount()):
                                    ch = node.getChild(i)
                                    res = find_identifier(ch)
                                    if res:
                                        return res
                            except Exception:
                                return None
                            return None
                        f = find_identifier(call_node)
                        if f:
                            fname = f
            except Exception:
                pass
            # Emitir CALL
            self.em.emit('CALL', dst=dst, a=fname)
            return dst

        if 'MultiplicativeExpr' in cname and ctx.getChildCount() > 1:
            left = self.visitAnyExpression(ctx.getChild(0))
            op = ctx.getChild(1).getText()
            right = self.visitAnyExpression(ctx.getChild(2))
            dst = self.em.new_temp()
            self.em.emit('MUL' if op == '*' else 'DIV', dst=dst, a=left, b=right)
            return dst

        if 'LeftHandSide' in cname or 'PrimaryAtom' in cname or 'Identifier' in cname:
            name = ctx.getText()
            # property access like obj.prop -> GETPROP
            try:
                if isinstance(name, str) and '.' in name:
                    obj_name, prop = name.split('.', 1)
                    obj_tmp = self.em.new_temp()
                    self.em.emit('LOAD', dst=obj_tmp, a=obj_name)
                    dst_prop = self.em.new_temp()
                    self.em.emit('GETPROP', dst=dst_prop, a=obj_tmp, b=prop)
                    return dst_prop
            except Exception:
                pass
            tmp = self.em.new_temp()
            self.em.emit('LOAD', dst=tmp, a=name)
            return tmp

        if ctext.startswith('(') and ctext.endswith(')'):
            for ch in ctx.getChildren():
                if hasattr(ch, 'accept'):
                    return self.visitAnyExpression(ch)

        for ch in children:
            if hasattr(ch, 'accept'):
                val = self.visitAnyExpression(ch)
                if val is not None:
                    return val

        return None

    def visitAssignment(self, ctx):
        # Robustly obtain left-hand side name or node
        name = None
        lhs_node = None
        if hasattr(ctx, 'leftHandSide') and ctx.leftHandSide():
            lhs_node = ctx.leftHandSide()
        elif hasattr(ctx, 'assignment') and ctx.assignment():
            # some parse variants may nest assignment inside a wrapper
            try:
                lhs_node = ctx.assignment().leftHandSide()
            except Exception:
                lhs_node = None
        else:
            # fallback: inspect children for a LeftHandSide or Identifier
            for ch in ctx.getChildren():
                tname = type(ch).__name__
                if 'LeftHandSide' in tname or 'Identifier' in tname or 'PrimaryAtom' in tname:
                    lhs_node = ch
                    break

        if lhs_node is not None:
            try:
                if hasattr(lhs_node, 'Identifier') and lhs_node.Identifier():
                    name = lhs_node.Identifier().getText()
                else:
                    # fallback to text of node
                    name = lhs_node.getText()
            except Exception:
                try:
                    name = lhs_node.getText()
                except Exception:
                    name = None

        # If still no name, some assignment productions provide Identifier() directly
        if name is None and hasattr(ctx, 'Identifier') and ctx.Identifier():
            try:
                name = ctx.Identifier().getText()
            except Exception:
                pass

        val = None
        # Try to locate RHS expression robustly. Prefer the last expression() if it's a list.
        expr_node = None
        if hasattr(ctx, 'expression') and ctx.expression():
            try:
                exprs = ctx.expression()
                # ANTLR sometimes returns a list-like object for expression(); pick last
                if isinstance(exprs, list) or (hasattr(exprs, '__len__') and not hasattr(exprs, 'getChildCount')):
                    expr_node = exprs[-1] if len(exprs) > 0 else None
                else:
                    expr_node = exprs
            except Exception:
                expr_node = self._expr_node(ctx.expression())
        # evaluate RHS using expression-aware visitor
        if expr_node is not None:
            try:
                val = self.visitAnyExpression(expr_node)
            except Exception:
                # last resort: try the generic visitor but avoid visiting lhs_node again
                try:
                    if expr_node is not lhs_node:
                        val = self.visit(expr_node)
                except Exception:
                    val = None
        # fallback: inspect children for an expression node that isn't the LHS
        if val is None:
            for ch in ctx.getChildren():
                if hasattr(ch, 'accept') and 'Expr' in type(ch).__name__:
                    if lhs_node is not None and ch is lhs_node:
                        continue
                    val = self.visitAnyExpression(ch)
                    if val is not None:
                        break

        if val is not None:
            # if this is assignment to a property: obj.prop = val -> SETPROP
            try:
                lhs_text = lhs_node.getText() if lhs_node is not None else (name if name is not None else None)
                if isinstance(lhs_text, str) and '.' in lhs_text:
                    obj_name, prop = lhs_text.split('.', 1)
                    obj_tmp = self.em.new_temp()
                    self.em.emit('LOAD', dst=obj_tmp, a=obj_name)
                    # SETPROP: receiver temp, property name, value
                    self.em.emit('SETPROP', dst=obj_tmp, a=prop, b=val)
                    if isinstance(val, str) and val.startswith('t'):
                        self.em.free_temp(val)
                    return lhs_text
            except Exception:
                pass
            # Fallback: sometimes the parse tree separates the Identifier of the property
            # from the full left-hand text. Inspect the full assignment text as a last resort.
            try:
                full_text = ctx.getText() if hasattr(ctx, 'getText') else None
                if isinstance(full_text, str) and '=' in full_text:
                    left_part = full_text.split('=')[0].strip()
                    if '.' in left_part:
                        obj_name, prop = left_part.split('.', 1)
                        obj_tmp = self.em.new_temp()
                        self.em.emit('LOAD', dst=obj_tmp, a=obj_name)
                        self.em.emit('SETPROP', dst=obj_tmp, a=prop, b=val)
                        if isinstance(val, str) and val.startswith('t'):
                            self.em.free_temp(val)
                        return left_part
            except Exception:
                pass
            # if name is None (complex LHS), attempt to use lhs_node text
            dst_name = name if name is not None else (lhs_node.getText() if lhs_node is not None else None)
            self.em.emit('STORE', dst=dst_name, a=val)
            if isinstance(val, str) and val.startswith('t'):
                self.em.free_temp(val)
            return dst_name
        return None

    def visitAdditiveExpr(self, ctx):
        left = self.visit(ctx.multiplicativeExpr(0))
        for i in range(1, len(ctx.multiplicativeExpr())):
            right = self.visit(ctx.multiplicativeExpr(i))
            op = '+' if '+' in ctx.getText() else '-'
            dst = self.em.new_temp()
            self.em.emit('ADD' if op == '+' else 'SUB', dst=dst, a=left, b=right)
            if isinstance(left, str) and left.startswith('t'):
                self.em.free_temp(left)
            if isinstance(right, str) and right.startswith('t'):
                self.em.free_temp(right)
            left = dst
        return left

    def visitMultiplicativeExpr(self, ctx):
        left = self.visit(ctx.unaryExpr(0))
        for i in range(1, len(ctx.unaryExpr())):
            right = self.visit(ctx.unaryExpr(i))
            op = '*' if '*' in ctx.getText() else '/'
            dst = self.em.new_temp()
            self.em.emit('MUL' if op == '*' else 'DIV', dst=dst, a=left, b=right)
            if isinstance(left, str) and left.startswith('t'):
                self.em.free_temp(left)
            if isinstance(right, str) and right.startswith('t'):
                self.em.free_temp(right)
            left = dst
        return left

    def visitLiteralExpr(self, ctx):
        return ctx.getText()

    def visitLeftHandSide(self, ctx):
        name = ctx.Identifier().getText()
        tmp = self.em.new_temp()
        self.em.emit('LOAD', dst=tmp, a=name)
        return tmp

    # Blocks and control flow
    def visitBlock(self, ctx):
        if hasattr(ctx, 'statement') and ctx.statement():
            for st in ctx.statement():
                self.visit(st)
        return None

    def visitIfStatement(self, ctx):
        # if '(' expression ')' block ('else' block)?;
        # evaluate condition using expression visitor (robust for relational/etc.)
        cond = self.visitAnyExpression(self._expr_node(ctx.expression())) if hasattr(ctx, 'expression') and ctx.expression() else None
        else_lbl = self.em.new_label()
        end_lbl = self.em.new_label()
        self.em.emit('IFZ', dst=else_lbl, a=cond)
        # then-block
        if hasattr(ctx, 'block') and ctx.block(0):
            self.visit(ctx.block(0))
        elif hasattr(ctx, 'statement') and ctx.statement():
            # accept single-statement then-branch
            self.visit(ctx.statement(0))
        self.em.emit('GOTO', dst=end_lbl)
        # else-block
        self.em.emit('LABEL', dst=else_lbl)
        if hasattr(ctx, 'block') and ctx.block(1):
            self.visit(ctx.block(1))
        elif hasattr(ctx, 'statement') and len(list(ctx.statement())) > 1:
            self.visit(ctx.statement(1))
        self.em.emit('LABEL', dst=end_lbl)
        return None

    def visitWhileStatement(self, ctx):
        start = self.em.new_label()
        end = self.em.new_label()
        self.em.emit('LABEL', dst=start)
        cond = self.visitAnyExpression(self._expr_node(ctx.expression())) if hasattr(ctx, 'expression') and ctx.expression() else None
        self.em.emit('IFZ', dst=end, a=cond)
        # Robust: accept both block and statement as body
        if hasattr(ctx, 'block') and ctx.block() is not None:
            self.visit(ctx.block())
        elif hasattr(ctx, 'statement') and ctx.statement() is not None:
            self.visit(ctx.statement())
        self.em.emit('GOTO', dst=start)
        self.em.emit('LABEL', dst=end)
        return None

    def visitDoWhileStatement(self, ctx):
        start = self.em.new_label()
        end = self.em.new_label()
        self.em.emit('LABEL', dst=start)
        # Robust: accept both block and statement as body
        if hasattr(ctx, 'block') and ctx.block() is not None:
            self.visit(ctx.block())
        elif hasattr(ctx, 'statement') and ctx.statement() is not None:
            self.visit(ctx.statement())
        cond = self.visitAnyExpression(self._expr_node(ctx.expression())) if hasattr(ctx, 'expression') and ctx.expression() else None
        # if condition false -> end
        self.em.emit('IFZ', dst=end, a=cond)
        self.em.emit('GOTO', dst=start)
        self.em.emit('LABEL', dst=end)
        return None

    def visitForStatement(self, ctx):
        # initializer may be var decl or assignment or ';'
        try:
            # initializer is child index 2 in grammar 'for' '(' (variableDeclaration | assignment | ';') expression? ';' expression? ')'
            init_child = ctx.getChild(2)
            if hasattr(init_child, 'accept') and init_child.getText() != ';':
                self.visit(init_child)
        except Exception:
            pass
        start = self.em.new_label()
        end = self.em.new_label()
        self.em.emit('LABEL', dst=start)
        # condition is expression(0) if present
        cond = None
        try:
            if ctx.expression() and len(ctx.expression()) >= 1:
                cond = self.visitAnyExpression(ctx.expression(0))
        except Exception:
            cond = None
        if cond is not None:
            self.em.emit('IFZ', dst=end, a=cond)
        # body
        if hasattr(ctx, 'block') and ctx.block() is not None:
            self.visit(ctx.block())
        elif hasattr(ctx, 'statement') and ctx.statement() is not None:
            self.visit(ctx.statement())
        # increment expression(1)
        try:
            if ctx.expression() and len(ctx.expression()) >= 2:
                self.visit(ctx.expression(1))
        except Exception:
            pass
        self.em.emit('GOTO', dst=start)
        self.em.emit('LABEL', dst=end)
        return None

    def visitReturnStatement(self, ctx):
        val = None
        if ctx.expression():
            expr_node = self._expr_node(ctx.expression())
            try:
                val = self.visitAnyExpression(expr_node)
            except Exception:
                val = self.visit(expr_node)
        self.em.emit('RET', dst=val)
        return None

    def visitFunctionDeclaration(self, ctx):
        fname = ctx.Identifier().getText()
        label = f'func_{fname}'
        self.em.emit('LABEL', dst=label)
        # parameters are already in symbol table (semantic phase) but for TAC we visit body
        # body may be block or single statement
        if hasattr(ctx, 'block') and ctx.block():
            self.visit(ctx.block())
        elif hasattr(ctx, 'statement') and ctx.statement():
            self.visit(ctx.statement())
        # emit a RET only if function body did not already emit one
        if not (self.em.instrs and getattr(self.em.instrs[-1], 'op', None) == 'RET'):
            self.em.emit('RET')
        # mark end of function for clarity in TAC
        self.em.emit('LABEL', dst=f'end_{fname}')
        return None

    def emit_goto(self, label):
        self.em.emit('GOTO', dst=label)
