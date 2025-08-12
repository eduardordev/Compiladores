from SimpleLangParser import SimpleLangParser
from SimpleLangVisitor import SimpleLangVisitor
from custom_types import IntType, FloatType, StringType, BoolType

def is_number(t):
    return isinstance(t, (IntType, FloatType))

class TypeCheckVisitor(SimpleLangVisitor):

    # expr ('*' | '/' | '%') expr
    def visitMulDivMod(self, ctx: SimpleLangParser.MulDivModContext):
        left_type = self.visit(ctx.expr(0))
        right_type = self.visit(ctx.expr(1))
        op = ctx.op.text

        # Sólo números para *, / y %
        if not (is_number(left_type) and is_number(right_type)):
            raise TypeError(f"Unsupported operand types for {op}: {left_type} and {right_type}")

        if op == '%':
            # Regla: modulo solo int % int
            if not (isinstance(left_type, IntType) and isinstance(right_type, IntType)):
                raise TypeError(f"Modulo requires int % int, got {left_type} % {right_type}")
            return IntType()

        # * y /: si alguno es float => float
        return FloatType() if isinstance(left_type, FloatType) or isinstance(right_type, FloatType) else IntType()

    # expr ('+' | '-') expr
    def visitAddSub(self, ctx: SimpleLangParser.AddSubContext):
        left_type = self.visit(ctx.expr(0))
        right_type = self.visit(ctx.expr(1))
        op = ctx.op.text

        # Concatenación: string + string
        if op == '+' and isinstance(left_type, StringType) and isinstance(right_type, StringType):
            return StringType()

        # Operación numérica: ambos números
        if is_number(left_type) and is_number(right_type):
            # + o - entre números => float si alguno es float
            return FloatType() if isinstance(left_type, FloatType) or isinstance(right_type, FloatType) else IntType()

        raise TypeError(f"Unsupported operand types for {op}: {left_type} and {right_type}")

    # expr '^' expr
    def visitPow(self, ctx: SimpleLangParser.PowContext):
        left_type = self.visit(ctx.expr(0))
        right_type = self.visit(ctx.expr(1))

        # Potencia solo entre números
        if not (is_number(left_type) and is_number(right_type)):
            raise TypeError(f"Unsupported operand types for ^: {left_type} and {right_type}")

        # Si hay float en alguno, resulta float; si ambos int, puede ser int (mantengámoslo int)
        return FloatType() if isinstance(left_type, FloatType) or isinstance(right_type, FloatType) else IntType()

    def visitInt(self, ctx: SimpleLangParser.IntContext):
        return IntType()

    def visitFloat(self, ctx: SimpleLangParser.FloatContext):
        return FloatType()

    def visitString(self, ctx: SimpleLangParser.StringContext):
        return StringType()

    def visitBool(self, ctx: SimpleLangParser.BoolContext):
        return BoolType()

    def visitParens(self, ctx: SimpleLangParser.ParensContext):
        return self.visit(ctx.expr())
