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
    li $t7, 0
    li $t1, 4
    mul $t1, $t7, $t1
    move $t7, $t0
    add $t2, $t7, $t1
    lw $t3, 0($t2)
    la $t4, xs
    li $t7, 4
    li $t1, 4
    mul $t5, $t7, $t1
    move $t7, $t4
    move $t1, $t5
    add $t6, $t7, $t1
    lw $t7, 0($t6)
    la $t8, xs
    li $t7, 1
    li $t1, 4
    mul $t9, $t7, $t1
    move $t7, $t8
    move $t1, $t9
    add $t0, $t7, $t1
    lw $t1, 0($t0)
    mul $t2, $t7, $t1
    move $t7, $t3
    move $t1, $t2
    add $t3, $t7, $t1
    lw $t3, r
    move $v0, $t3
    move $sp, $fp
    lw $ra, 28($sp)
    lw $fp, 24($sp)
    addi $sp, $sp, 32
    li $v0, 10                # service: exit
    syscall
