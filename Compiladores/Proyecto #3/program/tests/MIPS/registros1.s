.data
a: .word 0
b: .word 0
c: .word 0
d: .word 0
e: .word 0
f: .word 0
g: .word 0
h: .word 0
i: .word 0
j: .word 0
k: .word 0
r1: .word 0
r2: .word 0
r3: .word 0
r4: .word 0
r5: .word 0
r6: .word 0
r7: .word 0
r8: .word 0
r9: .word 0
r10: .word 0

.text
.globl main

main:
    # prologo
    addi $sp, $sp, -16
    sw $ra, 12($sp)
    sw $fp, 8($sp)
    move $fp, $sp

    # inicialización
    li $t9, 1
    sw $t9, a
    li $t9, 2
    sw $t9, b
    li $t9, 3
    sw $t9, c
    li $t9, 4
    sw $t9, d
    li $t9, 5
    sw $t9, e
    li $t9, 6
    sw $t9, f
    li $t9, 7
    sw $t9, g
    li $t9, 8
    sw $t9, h
    li $t9, 9
    sw $t9, i
    li $t9, 10
    sw $t9, j
    li $t9, 11
    sw $t9, k

    # r1 = a + b
    lw $t1, a
    lw $t2, b
    add $t0, $t1, $t2
    sw $t0, r1

    # r2 = c + d
    lw $t1, c
    lw $t2, d
    add $t0, $t1, $t2
    sw $t0, r2

    # r3 = e + f
    lw $t1, e
    lw $t2, f
    add $t0, $t1, $t2
    sw $t0, r3

    # r4 = g + h
    lw $t1, g
    lw $t2, h
    add $t0, $t1, $t2
    sw $t0, r4

    # r5 = i + j
    lw $t1, i
    lw $t2, j
    add $t0, $t1, $t2
    sw $t0, r5

    # r6 = k + r1
    lw $t1, k
    lw $t2, r1
    add $t0, $t1, $t2
    sw $t0, r6

    # r7 = r2 + r3
    lw $t1, r2
    lw $t2, r3
    add $t0, $t1, $t2
    sw $t0, r7

    # r8 = r4 + r5
    lw $t1, r4
    lw $t2, r5
    add $t0, $t1, $t2
    sw $t0, r8

    # r9 = r6 + r7
    lw $t1, r6
    lw $t2, r7
    add $t0, $t1, $t2
    sw $t0, r9

    # r10 = r8 + r9
    lw $t1, r8
    lw $t2, r9
    add $t0, $t1, $t2
    sw $t0, r10

    lw $t0, r10
    move $v0, $t0

    # epilogo
    move $sp, $fp
    lw $ra, 12($sp)
    lw $fp, 8($sp)
    addi $sp, $sp, 16
    jr $ra
