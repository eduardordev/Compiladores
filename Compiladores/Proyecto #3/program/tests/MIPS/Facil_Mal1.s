.data
res: .word 0

.text
.globl main

main:
    # Prólogo
    addi $sp, $sp, -8
    sw $ra, 4($sp)
    sw $fp, 0($sp)
    move $fp, $sp

    # Pasar argumentos (por ejemplo, 5 y 7)
    li $a0, 5
    li $a1, 7
    jal suma         # Llamada a la función

    # Guardar el resultado retornado en res
    sw $v0, res

    # Epílogo
    move $sp, $fp
    lw $ra, 4($sp)
    lw $fp, 0($sp)
    addi $sp, $sp, 8
    jr $ra

suma:
    # Prólogo
    addi $sp, $sp, -8
    sw $ra, 4($sp)
    sw $fp, 0($sp)
    move $fp, $sp

    # Sumar argumentos
    add $v0, $a0, $a1

    # Epílogo
    move $sp, $fp
    lw $ra, 4($sp)
    lw $fp, 0($sp)
    addi $sp, $sp, 8
    jr $ra