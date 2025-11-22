.data
xs: .word 4, 9, 2, 7, 6
r:  .word 0

.text
.globl main
main:
    addi $sp, $sp, -32
    sw   $ra, 28($sp)
    sw   $fp, 24($sp)
    move $fp, $sp
    la   $t0, xs
    lw   $t3, 0($t0)          
    la   $t0, xs
    li   $t1, 4
    mul  $t1, $t1, 4         
    add  $t0, $t0, $t1
    lw   $t7, 0($t0)         
    la   $t0, xs
    li   $t1, 1
    mul  $t1, $t1, 4         
    add  $t0, $t0, $t1
    lw   $t1, 0($t0)        
    mul  $t2, $t7, $t1
    add  $t3, $t3, $t2
    sw   $t3, r
    lw   $v0, r               
    move $sp, $fp
    lw   $ra, 28($sp)
    lw   $fp, 24($sp)
    addi $sp, $sp, 32
    li $v0, 10                
    syscall
