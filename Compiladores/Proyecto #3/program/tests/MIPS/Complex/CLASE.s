.data
juan: .word 0
__str0: .asciiz "Juan"
__str1: .asciiz "Pedro"
heap: .space 4096
heap_ptr: .word heap

.text
    addi $sp, $sp, -12
    move $t9, $t0
    sw $t9, 0($sp)
    la $t9, __str0
    sw $t9, 4($sp)
    li $t9, 20
    sw $t9, 8($sp)
    jal method_Persona_init
    addi $sp, $sp, 12
    addi $sp, $sp, -8
    la $t9, __str0
    sw $t9, 0($sp)
    li $t9, 20
    sw $t9, 4($sp)
    jal newPersona
    addi $sp, $sp, 8
    move $t1, $v0
    lw $t1, juan
    move $t9, $t1
    lw $t2, 0($t9)
    move $a0, $t2
    li $v0, 1
    syscall
    lw $t3, juan
    move $t9, $t3
    addi $t9, $t9, 4
    lw $t4, 0($t9)
    move $a0, $t4
    li $v0, 1
    syscall
    lw $t5, juan
    addi $sp, $sp, -8
    move $t9, $t5
    sw $t9, 0($sp)
    la $t9, __str1
    sw $t9, 4($sp)
    jal saludar
    addi $sp, $sp, 8
    move $t6, $v0
