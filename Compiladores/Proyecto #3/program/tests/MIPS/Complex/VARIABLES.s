.data
a: .word 0
b: .word 0
c: .word 0

.text
    lw $t0, a
    lw $t1, b
    move $t7, $t0
    add $t2, $t7, $t1
    lw $t2, c
    move $t7, $t2
    li $t1, 3
    sub $t3, $t7, $t1
    lw $t3, a
    move $t7, $t3
    li $t1, 2
    mul $t4, $t7, $t1
    li $v0, 10                # service: exit
    syscall
