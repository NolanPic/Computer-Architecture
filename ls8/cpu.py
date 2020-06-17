"""CPU functionality."""

import sys

LDI = 0b10000010 # load value into register
PRN = 0b01000111 # print value
HLT = 0b00000001 # halt execution
MUL = 0b10100010 # multiply
PUSH = 0b01000101 # push to stack
POP = 0b01000110 # pop off stack

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        
        self.ram = [0] * 256
        # 8 registers
        self.reg = [0] * 8
        # Program Counter
        self.pc = 0 
        # set register 7 to point to the top of the stack
        self.reg[7] = 0xf4
        # branch table for instruction set
        self.instruction_set = {}
        # load the branch table
        self.instruction_set[LDI] = self.LDI
        self.instruction_set[PRN] = self.PRN
        self.instruction_set[HLT] = self.HLT
        self.instruction_set[MUL] = self.MUL
        self.instruction_set[PUSH] = self.PUSH
        self.instruction_set[POP] = self.POP
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
        
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
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
        
    
    def HLT(self):
        self.running = False

    def run(self):
        """Run the CPU."""
        
        self.running = True
        while self.running:
            ir = self.ram_read(self.pc)
            
            # if the instruction exists in the instruction set,
            if ir in self.instruction_set:
                
                # do the instruction
                self.instruction_set[ir]()
                
                # increment the pc using bitwise and shifting
                instruction_length = (ir & 0b11000000) >> 6
                
                # pc should be incremented by this much
                pc_move_to = instruction_length + 1
                
                # increment pc
                self.pc += pc_move_to
                
            else:
                print(f'Unknown instruction {ir} at address {self.pc}')
                sys.exit(1)
