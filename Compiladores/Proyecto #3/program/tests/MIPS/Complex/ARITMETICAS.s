.data
x: .word 0
y: .word 0

.text
    move $t0, $v0
    lw $t0, x
    lw $t1, y
    move $t7, $t0
    div $t7, $t1
    mflo $t2
    lw $t2, x
    lw $t3, y
    move $t7, $t2
    move $t1, $t3
    div $t7, $t1
    mflo $t4
    li $v0, 10                # service: exit
    syscall
