.data
a: .word 0

.text
L0:
    lw $t0, a
    move $t9, $t0
    li $t8, 5
    slt $t1, $t9, $t8
    move $t9, $t1
    beq $t9, $zero, L1
    lw $t2, a
    move $a0, $t2
    li $v0, 1
    syscall
    j L0
L1:
