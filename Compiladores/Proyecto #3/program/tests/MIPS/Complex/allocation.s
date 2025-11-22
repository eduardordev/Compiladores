.data
x: .word 0

.text
    move $t0, $v0
    lw $t0, x
    move $a0, $t0
    li $v0, 1
    syscall
    li $v0, 10                # service: exit
    syscall
