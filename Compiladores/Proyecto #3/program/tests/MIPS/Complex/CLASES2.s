.data
e: .word 0
edad: .word 0
juan: .word 0
n: .word 0
nombre: .word 0
this: .word 0
__str0: .asciiz "Hola"
__str1: .asciiz "Juan"
__str2: .asciiz "Pedro"
heap: .space 4096
heap_ptr: .word heap

.text
method_Persona_init:
    addi $sp, $sp, -32
    sw $ra, 28($sp)
    sw $fp, 24($sp)
    move $fp, $sp
    lw $t0, n
    lw $t1, this
    lw $t9, nombre
    move $t8, $t1
    sw $t8, 0($t9)
    lw $t0, e
    lw $t2, this
    lw $t9, edad
    move $t8, $t2
    sw $t8, 0($t9)
    move $sp, $fp
    lw $ra, 28($sp)
    lw $fp, 24($sp)
    addi $sp, $sp, 32
    jr $ra
end_init:
method_Persona_saludar:
    addi $sp, $sp, -32
    sw $ra, 28($sp)
    sw $fp, 24($sp)
    move $fp, $sp
    la $a0, __str0
    li $v0, 4
    syscall
    lw $t0, nombre
    move $a0, $t0
    li $v0, 1
    syscall
    move $sp, $fp
    lw $ra, 28($sp)
    lw $fp, 24($sp)
    addi $sp, $sp, 32
    jr $ra
end_saludar:
    addi $sp, $sp, -12
    move $t9, $t3
    sw $t9, 0($sp)
    la $t9, __str1
    sw $t9, 4($sp)
    li $t9, 20
    sw $t9, 8($sp)
    jal method_Persona_init
    addi $sp, $sp, 12
    move $t4, $v0
    lw $t4, juan
    move $t9, $t4
    addi $t9, $t9, 4
    lw $t5, 0($t9)
    move $a0, $t5
    li $v0, 1
    syscall
    lw $t6, juan
    move $t9, $t6
    addi $t9, $t9, 8
    lw $t7, 0($t9)
    move $a0, $t7
    li $v0, 1
    syscall
    lw $t8, juan
    lw $t0, juan
    addi $sp, $sp, -8
    move $t9, $t8
    sw $t9, 0($sp)
    la $t9, __str2
    sw $t9, 4($sp)
    jal method_Unknown_saludar
    addi $sp, $sp, 8
    move $t9, $v0
    li $v0, 10                # service: exit
    syscall
