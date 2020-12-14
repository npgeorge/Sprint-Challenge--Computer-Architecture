"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
PUSH = 0b01000101
POP = 0b01000110
ADD = 0b10100000
MUL = 0b10100010
DIV = 0b10100011

# sprint
CMP = 0b10100111 # compare
JMP = 0b01010100 # jump
JEQ = 0b01010101 # If `equal` flag is set (true), jump to the address stored in the given register.
JNE = 0b01010110 # If `E` flag is clear (false, 0), jump to the address stored in the given register.

class CPU:
	"""Main CPU class."""

	def __init__(self):
		"""Construct a new CPU."""

		self.memory = [0] * 8
		self.ram = [0] * 256
		self.registers = [0] * 8
		self.registers[7] = 0xF4
		self.flags = [0] * 8
		self.pc = 0

		self.branch_table = {
			HLT: self.hlt, #halt
			LDI: self.ldi,
			PRN: self.prn,
			PUSH: self.push, # push
			POP: self.pop, # pop
			ADD: self.alu, # add
			MUL: self.alu, # multiply
			DIV: self.alu, # divide
            
            # Sprint
            CMP: self.alu,
            JMP: self.jmp,
			JEQ: self.jeq,
			JNE: self.jne
		}


	def load(self):
		"""Load a program into memory."""

		if (len(sys.argv)) != 2:
			print("Add sys file name")
			print("ex.): python3 ls8.py <sys_file.py>")
			sys.exit()

        # initiate address
		address = 0
        
		try:
			with open(sys.argv[1]) as f:
                # parse the file
				for line in f:
					possible_number = line[:line.find('#')]
					if possible_number == '':
                        # continue
						continue
					
                    # make integer
					instruction = int(possible_number, 2)

                    # assign address to instruction
					self.ram[address] = instruction

                    # count up by one
					address += 1

        # exception on missing file
		except FileNotFoundError:
			print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')
			sys.exit()

    # mem address register
	def ram_read(self, MAR):
		return self.ram[MAR]

    # mem data register
	def ram_write(self, MAR, MDR):
		self.ram[MAR] = MDR

	def alu(self, IR, operand_a, operand_b):
		"""ALU operations."""

		if IR == MUL:
			self.registers[operand_a] *= self.registers[operand_b]

		elif IR == CMP:
			if self.registers[operand_a] < self.registers[operand_b]:
				self.flags = [0] * 8
				self.flags[5] = 1

			elif self.registers[operand_a] > self.registers[operand_b]:
				self.flags = [0] * 8
				self.flags[6] = 1

			else:
				self.flags = [0] * 8
				self.flags[7] = 1

		elif IR == ADD:
			self.registers[operand_a] += self.registers[operand_b]

		elif IR == AND:
			self.registers[operand_a] = self.registers[operand_a] & self.registers[operand_b]

		elif IR == DIV:
			if self.registers[operand_b] == 0:
				print('ERROR: Cannot Divide by Zero')
				sys.exit()

			else:
				self.registers[operand_a] /= self.registers[operand_b]

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

	def run(self):
		"""Run the CPU."""

		self.running = True

		while self.running:
			#instruction register
			IR = self.ram_read(self.pc)

			operand_a = self.ram_read(self.pc + 1)

			operand_b = self.ram_read(self.pc + 2)

			num_operands = IR >> 6

			self.pc += 1 + num_operands

			is_alu_op = ((IR >> 5) & 0b001) == 1

			if is_alu_op:
				self.alu(IR, operand_a, operand_b)

			else:
				self.branch_table[IR](operand_a, operand_b)

	def hlt(self, operand_a, operand_b):
		self.running = False

	def ldi(self, operand_a, operand_b):
		self.registers[operand_a] = operand_b

	def prn(self, operand_a, operand_b):
		print(self.registers[operand_a])

	def push(self, operand_a, operand_b):
		#decrement stack pointer(SP)
		self.registers[7] -= 1

		#get value from register
		value = self.registers[operand_a]

		#put on the stack at SP
		SP = self.registers[7]
		self.ram_write(SP, value)

	def pop(self, operand_a, operand_b):
		#get value from stack
		SP = self.registers[7]
		value = self.ram_read(SP)

		#put value into register, indicated by operand_a
		self.registers[operand_a] = value

		#increment stack pointer
		self.registers[7] += 1

	def jmp(self, operand_a, operand_b):
		"""
        `JMP register`
        Jump to the address stored in the given register.
        Set the `PC` to the address stored in the given register.
        Machine code:
        ```
        01010100 00000rrr
        54 0r
        ```
        """
		self.pc = self.registers[operand_a]

	def jeq(self, operand_a, operand_b):
		"""
        `JEQ register`
        If `equal` flag is set (true), jump to the address stored in the given register.
        Machine code:
        ```
        01010101 00000rrr
        55 0r
        ```
        """
		if self.flags[7] == 1:
			self.pc = self.registers[operand_a]

	def jne(self, operand_a, operand_b):
		"""
        `JNE register`
        If `E` flag is clear (false, 0), jump to the address stored in the given
        register.
        Machine code:
        ```
        01010110 00000rrr
        56 0r
        ```
        """
		if self.flags[7] == 0:
			self.pc = self.registers[operand_a]