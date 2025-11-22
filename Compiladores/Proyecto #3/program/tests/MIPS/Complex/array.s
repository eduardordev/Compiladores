.data
xs: .word 4, 9, 2, 7, 6
r: .word 0

.text
.globl main
main:
    addi $sp, $sp, -32
    sw $ra, 28($sp)
    sw $fp, 24($sp)
    move $fp, $sp
    la $t0, xs
    li $t9, 0
    li $t8, 4
    mul $t1, $t9, $t8
    move $t9, $t0
    move $t8, $t1
    add $t2, $t9, $t8
    lw $t3, 0($t2)
    la $t4, xs
    li $t9, 4
    li $t8, 4
    mul $t5, $t9, $t8
    move $t9, $t4
    move $t8, $t5
    add $t6, $t9, $t8
    lw $t7, 0($t6)
    la $t8, xs
    li $t9, 1
    li $t8, 4
    mul $t9, $t9, $t8
    move $t9, $t8
    move $t8, $t9
    add $t0, $t9, $t8
    lw $t1, 0($t0)
    move $t9, $t7
    move $t8, $t1
    mul $t2, $t9, $t8
    move $t9, $t3
    move $t8, $t2
    add $t3, $t9, $t8
    lw $t3, r
    move $v0, $t3
    move $sp, $fp
    lw $ra, 28($sp)
    lw $fp, 24($sp)
    addi $sp, $sp, 32
    jr $ra
