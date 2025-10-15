from CompiscriptVisitor import CompiscriptVisitor
from CompiscriptParser import CompiscriptParser
from codegen.tac import Emitter


class CodeGenVisitor(CompiscriptVisitor):
    def __init__(self):
        super().__init__()
        self.em = Emitter()
        
    def visitProgram(self, ctx: CompiscriptParser.ProgramContext):
        print("[DEBUG] Entró a visitProgram")

        for i, child in enumerate(ctx.getChildren()):
            print(f"[DEBUG] -> Hijo {i}: {child.getText()} ({type(child).__name__})")
            if type(child).__name__ == "StatementContext":
                print(f"[DEBUG] Descendiendo manualmente a Statement {i}")
                self.visitStatement(child)
            elif hasattr(child, "accept"):
                self.visit(child)

        print("[DEBUG] Terminó visitProgram, total instrucciones:", len(self.em.instrs))
        return self.em

    def visitStatement(self, ctx):
        print("[DEBUG] visitStatement ->", ctx.getText())

        for ch in ctx.getChildren():
            cname = type(ch).__name__
            ctext = ch.getText()
            print(f"[DEBUG]   -> Subnodo: {cname} -> {ctext}")

            if hasattr(ch, "accept"):
                if cname == "VariableDeclarationContext":
                    print("[DEBUG]   -> Forzando visita manual a VariableDeclaration()")
                    self.visitVariableDeclaration(ch)
                    continue
                if cname == "AssignmentContext":
                    print("[DEBUG]   -> Forzando visita manual a Assignment()")
                    self.visitAssignment(ch)
                    continue
                result = self.visit(ch)
                if result is not None:
                    return result
        return None

    def visitVariableDeclarationStatement(self, ctx):
        print("[DEBUG] visitVariableDeclarationStatement ->", ctx.getText())
        if ctx.variableDeclaration():
            return self.visit(ctx.variableDeclaration())

    def visitVariableDeclaration(self, ctx):
        print("[DEBUG] visitVariableDeclaration ->", ctx.getText())
        name = ctx.Identifier().getText()

        val = None
        if ctx.initializer():
            init = ctx.initializer()
            print(f"[DEBUG]   initializer detectado: {init.getText()}")

            for ch in init.getChildren():
                cname = type(ch).__name__
                ctext = ch.getText()
                print(f"[DEBUG]   -> Buscando dentro de initializer: {cname} -> {ctext}")

                if "Expr" in cname or "Expression" in cname or "Literal" in cname:
                    print(f"[DEBUG]   -> Forzando visita manual a {cname}")
                    val = self.visitAnyExpression(ch)
                    break

        if val is None:
            print(f"[DEBUG]   No se encontró valor para {name}, usando undefined")
            val = "undefined"

        self.em.emit("STORE", dst=name, a=val)
        print(f"[DEBUG] Emitido: STORE {val} -> {name}")

        if isinstance(val, str) and val.startswith("t"):
            self.em.free_temp(val)


    def visitAnyExpression(self, ctx):
        """Visita recursivamente cualquier tipo de expresión hasta llegar a un valor o literal."""
        cname = type(ctx).__name__
        ctext = ctx.getText()
        print(f"[DEBUG] visitAnyExpression({cname}) -> {ctext}")

        if not hasattr(ctx, "getChildCount"):
            return None

        if "Literal" in cname:
            print(f"[DEBUG]   Literal detectado: {ctext}")
            return ctext

        if "AdditiveExpr" in cname and ctx.getChildCount() > 1:
            left = self.visitAnyExpression(ctx.getChild(0))
            op = ctx.getChild(1).getText()
            right = self.visitAnyExpression(ctx.getChild(2))
            dst = self.em.new_temp()
            self.em.emit("ADD" if op == "+" else "SUB", dst=dst, a=left, b=right)
            print(f"[DEBUG]   Emitido: {dst} = {left} {op} {right}")
            return dst

        if "MultiplicativeExpr" in cname and ctx.getChildCount() > 1:
            left = self.visitAnyExpression(ctx.getChild(0))
            op = ctx.getChild(1).getText()
            right = self.visitAnyExpression(ctx.getChild(2))
            dst = self.em.new_temp()
            self.em.emit("MUL" if op == "*" else "DIV", dst=dst, a=left, b=right)
            print(f"[DEBUG]   Emitido: {dst} = {left} {op} {right}")
            return dst

        if "LeftHandSide" in cname or "PrimaryAtom" in cname or "Identifier" in cname:
            name = ctx.getText()
            tmp = self.em.new_temp()
            self.em.emit("LOAD", dst=tmp, a=name)
            print(f"[DEBUG]   Emitido: {tmp} = LOAD {name}")
            return tmp

        if ctext.startswith("(") and ctext.endswith(")"):
            for ch in ctx.getChildren():
                if hasattr(ch, "accept"):
                    return self.visitAnyExpression(ch)

        for ch in ctx.getChildren():
            if hasattr(ch, "accept"):
                val = self.visitAnyExpression(ch)
                if val is not None:
                    return val

        return None

    def visitAssignment(self, ctx):
        print("[DEBUG] visitAssignment ->", ctx.getText())
        name = ctx.leftHandSide().Identifier().getText()
        val = self.visit(ctx.expression())
        if val is not None:
            self.em.emit("STORE", dst=name, a=val)
            print(f"[DEBUG] Emitido: STORE {val} -> {name}")
            if isinstance(val, str) and val.startswith("t"):
                self.em.free_temp(val)

    def visitAdditiveExpr(self, ctx):
        left = self.visit(ctx.multiplicativeExpr(0))
        for i in range(1, len(ctx.multiplicativeExpr())):
            right = self.visit(ctx.multiplicativeExpr(i))
            op = "+" if "+" in ctx.getText() else "-"
            dst = self.em.new_temp()
            self.em.emit("ADD" if op == "+" else "SUB", dst=dst, a=left, b=right)
            print(f"[DEBUG] Emitido: {dst} = {left} {op} {right}")
            if isinstance(left, str) and left.startswith("t"):
                self.em.free_temp(left)
            if isinstance(right, str) and right.startswith("t"):
                self.em.free_temp(right)
            left = dst
        return left

    def visitMultiplicativeExpr(self, ctx):
        left = self.visit(ctx.unaryExpr(0))
        for i in range(1, len(ctx.unaryExpr())):
            right = self.visit(ctx.unaryExpr(i))
            op = "*" if "*" in ctx.getText() else "/"
            dst = self.em.new_temp()
            self.em.emit("MUL" if op == "*" else "DIV", dst=dst, a=left, b=right)
            print(f"[DEBUG] Emitido: {dst} = {left} {op} {right}")
            if isinstance(left, str) and left.startswith("t"):
                self.em.free_temp(left)
            if isinstance(right, str) and right.startswith("t"):
                self.em.free_temp(right)
            left = dst
        return left


    def visitLiteralExpr(self, ctx):
        val = ctx.getText()
        print(f"[DEBUG] Literal detectado: {val}")
        return val

    def visitLeftHandSide(self, ctx):
        name = ctx.Identifier().getText()
        tmp = self.em.new_temp()
        self.em.emit("LOAD", dst=tmp, a=name)
        print(f"[DEBUG] Emitido: {tmp} = LOAD {name}")
        return tmp
