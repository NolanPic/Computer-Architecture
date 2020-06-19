"""CPU functionality."""

import sys
      # AABCDDDD
LDI = 0b10000010 # load value into register
PRN = 0b01000111 # print value
HLT = 0b00000001 # halt execution
MUL = 0b10100010 # multiplication
ADD = 0b10100000 # addition
PUSH = 0b01000101 # push to stack
POP = 0b01000110 # pop off stack
CMP = 0b10100111 # compare two registers
JMP = 0b01010100 # jump to address
JEQ = 0b01010101 # jump if equal
JNE = 0b01010110 # jump if not equal
CALL = 0b01010000 # call a subroutine
RET = 0b00010001 # return from a subroutine
AND = 0b10101000 # bitwise-AND
OR = 0b10101010 # bitwise-OR
XOR = 0b10101011 # bitwise-XOR

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        
        self.ram = [0] * 256
        # 8 registers
        self.reg = [0] * 8
        # Program Counter
        self.pc = 0 
        # set the fl: 00000LGE less,greater,equal
        self.fl = 0b00000000
        # set register 7 to point to the top of the stack
        self.reg[7] = 0xf4
        # branch table for instruction set
        self.instruction_set = {}
        # load the branch table
        self.instruction_set[LDI] = self.LDI
        self.instruction_set[PRN] = self.PRN
        self.instruction_set[HLT] = self.HLT
        self.instruction_set[MUL] = self.MUL
        self.instruction_set[ADD] = self.ADD
        self.instruction_set[PUSH] = self.PUSH
        self.instruction_set[POP] = self.POP
        self.instruction_set[CMP] = self.CMP
        self.instruction_set[JMP] = self.JMP
        self.instruction_set[JEQ] = self.JEQ
        self.instruction_set[JNE] = self.JNE
        self.instruction_set[CALL] = self.CALL
        self.instruction_set[RET] = self.RET
        self.instruction_set[AND] = self.AND
        self.instruction_set[OR] = self.OR
        self.instruction_set[XOR] = self.XOR
        self.running = False
        
    def ram_read(self, mar):
        return self.ram[mar]
    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def load(self):
        """Load a program into memory."""
        
        # -- LOAD PROGRAM --
        
        # handle no argument for program
        if len(sys.argv) < 2:
            print('You must enter a program to run')
            sys.exit(1)
            
        filename = sys.argv[1]
        
        address = 0
        
        with open(filename) as f:
            for line in f:
                line = line.split('#')
                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue
                
                self.ram_write(address, v)
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == "CMP":
            # 00000LGE less,greater,equal
            # get the values
            val_a = self.reg[reg_a]
            val_b = self.reg[reg_b]
            # set what the flags should be
            if val_a == val_b:
                self.fl =  0b00000001
            elif val_a > val_b:
                self.fl = 0b00000010
            else: # val_a is less
                self.fl = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: {self.pc}", end='')
        print(f" | %02X %02X %02X |" % (
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
        
    def LDI(self):
        # get the register slot we want to write the value to
        reg_num = self.ram_read(self.pc+1)
        # get the value that we want to write to the register
        value = self.ram_read(self.pc+2) 
        # set the register at the desired slot to the desired value
        self.reg[reg_num] = value
        
    def PRN(self):
        # get the register slot we want to print the value of
        reg_num = self.ram_read(self.pc+1)
        # get that value by its slot
        value = self.reg[reg_num]
        # print!
        print(value)
        
    def MUL(self):
        # get the register slot of the first number
        reg_num1 = self.ram_read(self.pc+1)
        # get the register slot of the second number
        reg_num2 = self.ram_read(self.pc+2)
        # pass them off to the ALU
        self.alu("MUL", reg_num1, reg_num2)
        
    def ADD(self):
        # get the register slot of the first number
        reg_num1 = self.ram_read(self.pc+1)
        # get the register slot of the second number
        reg_num2 = self.ram_read(self.pc+2)
        # pass them off to the ALU
        self.alu("ADD", reg_num1, reg_num2)
        
    def PUSH(self):
        SP = 7
        # decrement SP--remember that it stacks going towards the bottom
        self.reg[SP] -=1
        
        # get the value we want to store
        reg_num = self.ram_read(self.pc+1)
        # get the value
        value = self.reg[reg_num]
        
        # figure out where to store it
        top_of_stack_addr = self.reg[SP]
        
        # store it
        self.ram_write(top_of_stack_addr, value)
        
    def POP(self):
        SP = 7
        # get the address that the SP is pointing to
        address = self.reg[SP]
        # get the value of that address from RAM
        value = self.ram_read(address)
        # get the number for the given register
        reg_num = self.ram_read(self.pc+1)
        # write the value to this register
        self.reg[reg_num] = value
        # increment the SP--remember that it stacks going towards the bottom
        self.reg[SP] +=1
        
    def CMP(self):
        # get the first reg address
        reg_a = self.ram_read(self.pc+1)
        # get the second reg address
        reg_b = self.ram_read(self.pc+2)
        
        # pass to the ALU
        self.alu("CMP", reg_a, reg_b)
        
    def JMP(self):
        # get the register value to jump to
        reg_num = self.ram_read(self.pc+1)
        address_to_jump_to = self.reg[reg_num]
        # jump the PC to this address
        self.pc = address_to_jump_to
        
        # return true to indicate that we ARE jumping.
        # Useful for conditional jumps
        return True
        
    def JEQ(self):
        if self.fl == 0b00000001:
            # the equal flag is set to 1 (true)
            self.JMP()
            return True
            
        
    def JNE(self):
        if self.fl != 0b00000001:
            # the equal flag is set to 0 (false)
            self.JMP()
            return True
        
    def CALL(self):
        # get the return address
        return_addr = self.pc+2 # this command has one parameter, so increment by 2
        
        # push the return address onto the stack
        SP = 7
        # decrement SP--remember that it stacks going towards the bottom
        self.reg[SP] -=1
        # write to the stack with the return address
        self.ram_write(self.reg[SP], return_addr)
        
        # now, get the address that we want to call (move pc to)
        reg_num = self.ram_read(self.pc+1)
        subroutine_addr = self.reg[reg_num]
        
        # call the subroutine
        self.pc = subroutine_addr
        
        # This has to return true because we are moving--not ideal, but necessary for now
        return True
        
    def RET(self):
        SP = 7
        # get the address that the SP is pointing to
        address = self.reg[SP]
        #print(bin(address))
        # get the value of that address from RAM
        return_addr = self.ram_read(address)
        
        # set the PC to the return address
        self.pc = return_addr
        # increment the SP--remember that it stacks going towards the bottom
        self.reg[SP] +=1
        
        return True
    
    def AND(self):
        # get the register slot of the first number
        reg_num1 = self.ram_read(self.pc+1)
        # get the register slot of the second number
        reg_num2 = self.ram_read(self.pc+2)
        # pass them off to the ALU
        self.alu("AND", reg_num1, reg_num2)
        
    def OR(self):
        # get the register slot of the first number
        reg_num1 = self.ram_read(self.pc+1)
        # get the register slot of the second number
        reg_num2 = self.ram_read(self.pc+2)
        # pass them off to the ALU
        self.alu("OR", reg_num1, reg_num2)
        
    def XOR(self):
        # get the register slot of the first number
        reg_num1 = self.ram_read(self.pc+1)
        # get the register slot of the second number
        reg_num2 = self.ram_read(self.pc+2)
        # pass them off to the ALU
        self.alu("XOR", reg_num1, reg_num2)
        
    
    def HLT(self):
        self.running = False

    def run(self):
        """Run the CPU."""
        
        self.running = True
        while self.running:
            ir = self.ram_read(self.pc)
            
            #self.trace()
            
            # if the instruction exists in the instruction set,
            if ir in self.instruction_set:
                
                # do the instruction
                # if jumping is true, it means this is a comparison
                # op (JEQ, JGE, JGT, etc.) and it WILL be jumping
                jumping = self.instruction_set[ir]()
                
                # whether the instruction increments the PC itself or not
                sets_pc = (ir & 0b00010000) >> 4
                # increment the pc using bitwise and shifting
                instruction_length = (ir & 0b11000000) >> 6
                
                # if the instruction does not increment the PC itself,
                # manually increment it. Additionally, if we are in an
                # instruction that increments conditionally, 'jumping'
                # will determine if it jumps
                if (sets_pc == 0) or (sets_pc == 1 and not jumping):
                    # pc should be incremented by this much
                    pc_move_to = instruction_length + 1
                    # increment pc
                    self.pc += pc_move_to
                    
                
            else:
                print(f'Unknown instruction {ir} at address {self.pc}')
                sys.exit(1)
