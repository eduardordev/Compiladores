from CompiscriptVisitor import CompiscriptVisitor
from CompiscriptParser import CompiscriptParser
from codegen.tac import Emitter


class CodeGenVisitor(CompiscriptVisitor):
    def __init__(self):
        super().__init__()
        self.em = Emitter()

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
        if tree is None:
            return None

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

        # function call handling: CallExpr or pattern like Identifier '(' arguments ')'
        if 'CallExpr' in cname or (hasattr(ctx, 'arguments') and ctx.arguments()) or ('(' in ctext and ctext.endswith(')') and any('Identifier' in type(ch).__name__ for ch in children[:2])):
            # crude: first child (or primaryAtom) contains function name
            # collect arguments (if any) and emit ARG op per evaluated argument
            args = []
            if hasattr(ctx, 'arguments') and ctx.arguments():
                for ex in ctx.arguments().expression():
                    val = self.visitAnyExpression(ex)
                    if val is not None:
                        args.append(val)
            if not args:
                for ch in children:
                    if hasattr(ch, 'accept') and ('Expr' in type(ch).__name__ or 'Expression' in type(ch).__name__):
        call_ctx = ctx if 'CallExpr' in cname else None
        if not call_ctx:
            for ch in children:
                if 'CallExpr' in type(ch).__name__:
                    call_ctx = ch
                    break
        if call_ctx or ('(' in ctext and ctext.endswith(')') and any('Identifier' in type(ch).__name__ for ch in children[:2])):
            # crude: first child (or primaryAtom) contains function name
            # collect arguments (if any) and emit ARG op per evaluated argument
            args = []
            arg_source = call_ctx if call_ctx else ctx
            if hasattr(arg_source, 'arguments') and arg_source.arguments():
                for ex in arg_source.arguments().expression():
                    val = self.visitAnyExpression(ex)
                    if val is not None:
                        args.append(val)
            else:
                for ch in children:
                    if hasattr(ch, 'accept') and 'Expression' in type(ch).__name__:
                        val = self.visitAnyExpression(ch)
                        if val is not None:
                            args.append(val)
            for a in args:
                self.em.emit('ARG', a=a)
            # call: produce a temp to receive return
            dst = self.em.new_temp()
            # function name: extract as text from first child (fallback)
            try:
                first = ctx.getChild(0)
                fname = first.getText()
            except Exception:
                fname = 'unknown'
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
        name = ctx.leftHandSide().Identifier().getText()
        val = self.visit(ctx.expression())
        if val is not None:
            self.em.emit('STORE', dst=name, a=val)
            if isinstance(val, str) and val.startswith('t'):
                self.em.free_temp(val)

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
        cond = self.visit(ctx.expression())
        else_lbl = self.em.new_label()
        end_lbl = self.em.new_label()
        self.em.emit('IFZ', dst=else_lbl, a=cond)
        # then-block
        self.visit(ctx.block(0))
        self.em.emit('GOTO', dst=end_lbl)
        # else-block
        self.em.emit('LABEL', dst=else_lbl)
        if ctx.block(1):
            self.visit(ctx.block(1))
        self.em.emit('LABEL', dst=end_lbl)
        return None

    def visitWhileStatement(self, ctx):
        start = self.em.new_label()
        end = self.em.new_label()
        self.em.emit('LABEL', dst=start)
        cond = self.visit(ctx.expression())
        self.em.emit('IFZ', dst=end, a=cond)
        self.visit(ctx.statement())
        self.em.emit('GOTO', dst=start)
        self.em.emit('LABEL', dst=end)
        return None

    def visitDoWhileStatement(self, ctx):
        start = self.em.new_label()
        end = self.em.new_label()
        self.em.emit('LABEL', dst=start)
        self.visit(ctx.statement())
        cond = self.visit(ctx.expression())
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
                cond = self.visit(ctx.expression(0))
        except Exception:
            cond = None
        if cond is not None:
            self.em.emit('IFZ', dst=end, a=cond)
        # body
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
            val = self.visit(ctx.expression())
        self.em.emit('RET', dst=val)
        return None

    def visitFunctionDeclaration(self, ctx):
        fname = ctx.Identifier().getText()
        label = f'func_{fname}'
        self.em.emit('LABEL', dst=label)
        # parameters are already in symbol table (semantic phase) but for TAC we visit body
        self.visit(ctx.block())
        self.em.emit('RET')
        return None

    def emit_goto(self, label):
        self.em.emit('GOTO', dst=label)
