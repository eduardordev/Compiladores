.data
i: .word 0
x: .word 0
y: .word 0
z: .word 0
__str0: .asciiz "Y is greater than X"
__str1: .asciiz "X is equal to Y"
__str2: .asciiz "X is not equal to Y"
__str3: .asciiz "Iteration: "
__str4: .asciiz "Z is greater than or equal to Y"
__str5: .asciiz "Z is less than Y"

.text
    lw $t0, x
    lw $t1, y
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
    lw $t3, x
    lw $t4, y
    move $t9, $t3
    move $t8, $t4
    seq $t5, $t9, $t8
    move $t9, $t5
    beq $t9, $zero, L2
    la $a0, __str1
    li $v0, 4
    syscall
    j L3
L2:
    la $a0, __str2
    li $v0, 4
    syscall
L3:
L4:
    lw $t6, x
    move $t9, $t6
    li $t8, 10
    slt $t7, $t9, $t8
    move $t9, $t7
    beq $t9, $zero, L5
    lw $t8, z
    lw $t9, x
    move $t7, $t8
    move $t1, $t9
    add $t0, $t7, $t1
    lw $t0, x
    move $t7, $t0
    li $t1, 1
    add $t1, $t7, $t1
    j L4
L5:
L6:
    lw $t1, i
    move $t9, $t1
    li $t8, 5
    sle $t2, $t9, $t8
    move $t9, $t2
    beq $t9, $zero, L7
    la $a0, __str3
    li $v0, 4
    syscall
    lw $t3, i
    move $a0, $t3
    li $v0, 1
    syscall
    j L6
L7:
    lw $t4, z
    lw $t5, y
    move $t9, $t4
    move $t8, $t5
    sge $t6, $t9, $t8
    move $t9, $t6
    beq $t9, $zero, L8
    la $a0, __str4
    li $v0, 4
    syscall
    j L9
L8:
    la $a0, __str5
    li $v0, 4
    syscall
L9:
    li $v0, 10                # service: exit
    syscall
