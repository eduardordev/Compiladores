.data
a: .word 0
b: .word 0
c: .word 0
__str0: .asciiz "B is greater than A"
__str1: .asciiz "A is greater than B"
__str2: .asciiz "A is greater than or equal to B"
__str3: .asciiz "A is less than or equal to B"
__str4: .asciiz "C is greater than or equal to B"
__str5: .asciiz "C is less than or equal to B"

.text
    lw $t0, a
    lw $t1, b
    move $t9, $t0
    move $t8, $t1
    slt $t2, $t9, $t8
    move $t9, $t2
    beq $t9, $zero, L0
    la $a0, __str0
    li $v0, 4
    syscall
    j L1
L0:
L1:
    lw $t3, a
    lw $t4, b
    move $t9, $t3
    move $t8, $t4
    sgt $t5, $t9, $t8
    move $t9, $t5
    beq $t9, $zero, L2
    la $a0, __str1
    li $v0, 4
    syscall
    j L3
L2:
L3:
    lw $t6, a
    lw $t7, b
    move $t9, $t6
    move $t8, $t7
    sge $t8, $t9, $t8
    move $t9, $t8
    beq $t9, $zero, L4
    la $a0, __str2
    li $v0, 4
    syscall
    j L5
L4:
L5:
    lw $t9, a
    lw $t0, b
    move $t8, $t0
    sle $t1, $t9, $t8
    move $t9, $t1
    beq $t9, $zero, L6
    la $a0, __str3
    li $v0, 4
    syscall
    j L7
L6:
L7:
    lw $t2, c
    lw $t3, b
    move $t9, $t2
    move $t8, $t3
    sge $t4, $t9, $t8
    move $t9, $t4
    beq $t9, $zero, L8
    la $a0, __str4
    li $v0, 4
    syscall
    j L9
L8:
L9:
    lw $t5, c
    lw $t6, b
    move $t9, $t5
    move $t8, $t6
    sle $t7, $t9, $t8
    move $t9, $t7
    beq $t9, $zero, L10
    la $a0, __str5
    li $v0, 4
    syscall
    j L11
L10:
L11:
