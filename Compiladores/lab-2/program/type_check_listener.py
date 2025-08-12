from SimpleLangListener import SimpleLangListener
from SimpleLangParser import SimpleLangParser
from custom_types import IntType, FloatType, StringType, BoolType

def is_number(t):
    return isinstance(t, (IntType, FloatType))

class TypeCheckListener(SimpleLangListener):
    def __init__(self):
        self.errors = []
        # Mapeamos cada ctx a su tipo inferido
        self.types = {}

    # ---------- MulDivMod ----------
    def enterMulDivMod(self, ctx: SimpleLangParser.MulDivModContext):
        pass

    def exitMulDivMod(self, ctx: SimpleLangParser.MulDivModContext):
        left_type = self.types[ctx.expr(0)]
        right_type = self.types[ctx.expr(1)]
        op = ctx.op.text

        if not (is_number(left_type) and is_number(right_type)):
            self.errors.append(f"Unsupported operand types for {op}: {left_type} and {right_type}")
            return

        if op == '%':
            if not (isinstance(left_type, IntType) and isinstance(right_type, IntType)):
                self.errors.append(f"Modulo requires int % int, got {left_type} % {right_type}")
                return
            self.types[ctx] = IntType()
            return

        # * y /
        self.types[ctx] = FloatType() if isinstance(left_type, FloatType) or isinstance(right_type, FloatType) else IntType()

    # ---------- AddSub ----------
    def enterAddSub(self, ctx: SimpleLangParser.AddSubContext):
        pass

    def exitAddSub(self, ctx: SimpleLangParser.AddSubContext):
        left_type = self.types[ctx.expr(0)]
        right_type = self.types[ctx.expr(1)]
        op = ctx.op.text

        # string + string => string
        if op == '+' and isinstance(left_type, StringType) and isinstance(right_type, StringType):
            self.types[ctx] = StringType()
            return

        # num +/- num
        if is_number(left_type) and is_number(right_type):
            self.types[ctx] = FloatType() if isinstance(left_type, FloatType) or isinstance(right_type, FloatType) else IntType()
            return

        self.errors.append(f"Unsupported operand types for {op}: {left_type} and {right_type}")

    # ---------- Pow ----------
    def enterPow(self, ctx: SimpleLangParser.PowContext):
        pass

    def exitPow(self, ctx: SimpleLangParser.PowContext):
        left_type = self.types[ctx.expr(0)]
        right_type = self.types[ctx.expr(1)]

        if not (is_number(left_type) and is_number(right_type)):
            self.errors.append(f"Unsupported operand types for ^: {left_type} and {right_type}")
            return

        self.types[ctx] = FloatType() if isinstance(left_type, FloatType) or isinstance(right_type, FloatType) else IntType()

    # ---------- Átomos ----------
    def enterInt(self, ctx: SimpleLangParser.IntContext):
        self.types[ctx] = IntType()

    def enterFloat(self, ctx: SimpleLangParser.FloatContext):
        self.types[ctx] = FloatType()

    def enterString(self, ctx: SimpleLangParser.StringContext):
        self.types[ctx] = StringType()

    def enterBool(self, ctx: SimpleLangParser.BoolContext):
        self.types[ctx] = BoolType()

    def enterParens(self, ctx: SimpleLangParser.ParensContext):
        pass

    def exitParens(self, ctx: SimpleLangParser.ParensContext):
        self.types[ctx] = self.types[ctx.expr()]
