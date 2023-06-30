.gba

.create "payload.bin",0


.thumb
    
    BX PC
    .dcb 0, 0, 0, 0, 0, 0
    
.arm
    
    NOP
    NOP
    
    ; Fix ARM7 PC bit1 bug caused by the Thumb instruction in the original savefile
    BIC PC, PC, #3
    
    NOP
    NOP
    
    ; Above BIC should skip the two NOPs above
    NOP
    NOP
    
    BKPT #0
    
    STMFD SP!, {r0-r6, LR}
    
    LDR r3, =(0x080860c8 | 1) ; CB2_ReturnToField
    MOV LR, PC
    BX r3
    NOP
    
    BKPT #0
    
    LDMFD SP!, {r0-r6, LR}
    BX LR
    
.align 4
.pool

.close
