# MIPS generado por Compiscript IDE
[Semantic] line 1:0 Asignación incompatible: integer[] := integer
.data
x: .word 0
xs: .word 0
xs[1]: .word 0

.text
    sw [1,2,3], xs
    lw $t0, xs[1]
    sw $t0, x
