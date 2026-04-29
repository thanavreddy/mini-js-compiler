# =============================================================================
# PHASE 6 — CODE GENERATION (Pseudo-Assembly)
# Converts optimized TAC into pseudo-assembly instructions.
#
# Register file: R0 – R7 (8 general purpose registers)
# Instructions:
#   LOAD   Rdest, value/variable   — load immediate or memory into register
#   STORE  variable, Rsrc          — store register to named memory location
#   ADD    Rdest, Rleft, Rright    — arithmetic
#   SUB    Rdest, Rleft, Rright
#   MUL    Rdest, Rleft, Rright
#   DIV    Rdest, Rleft, Rright
#   PRINT  Rsrc                    — output register value
#   LOAD_STR Rdest, "string"       — load string constant
# =============================================================================

class RegisterAllocator:
    """Simple round-robin register allocator."""
    def __init__(self, count=8):
        self.count = count
        self.next = 0
        self.var_reg = {}   # variable/temp name -> register name

    def alloc(self, name=None):
        reg = f"R{self.next % self.count}"
        self.next += 1
        if name:
            self.var_reg[name] = reg
        return reg

    def get(self, name):
        return self.var_reg.get(name)

    def get_or_alloc(self, name):
        if name in self.var_reg:
            return self.var_reg[name]
        return self.alloc(name)


OP_MAP = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}


class CodeGenerator:
    def __init__(self):
        self.output = []
        self.regs = RegisterAllocator()

    def emit(self, line):
        self.output.append(line)

    def resolve(self, val):
        """Return either a register (if val is a known var/temp) or the raw value."""
        if isinstance(val, (int, float)):
            return str(int(val) if isinstance(val, float) and val.is_integer() else val)
        reg = self.regs.get(val)
        if reg:
            return reg
        return val   # unresolved name — emit as-is (memory reference)

    def generate(self, instructions):
        self.emit("; ============================")
        self.emit("; Generated Pseudo-Assembly")
        self.emit("; ============================")
        self.emit("")

        for instr in instructions:
            op = instr['op']

            # ------------------------------------------------------------------
            if op == 'ASSIGN':
                dest_reg = self.regs.alloc(instr['dest'])
                src      = self.resolve(instr['src'])
                self.emit(f"  LOAD   {dest_reg}, {src}")
                # If destination is a user variable (not a temp), also STORE
                d = instr['dest']
                if not (d.startswith('t') and d[1:].isdigit()):
                    self.emit(f"  STORE  {d}, {dest_reg}")

            # ------------------------------------------------------------------
            elif op == 'BINOP':
                left_resolved  = self.resolve(instr['left'])
                right_resolved = self.resolve(instr['right'])

                # If left is a raw value (not a register), load it first
                if not left_resolved.startswith('R'):
                    r_left = self.regs.alloc()
                    self.emit(f"  LOAD   {r_left}, {left_resolved}")
                else:
                    r_left = left_resolved

                # If right is a raw value, load it first
                if not right_resolved.startswith('R'):
                    r_right = self.regs.alloc()
                    self.emit(f"  LOAD   {r_right}, {right_resolved}")
                else:
                    r_right = right_resolved

                dest_reg = self.regs.alloc(instr['dest'])
                asm_op   = OP_MAP.get(instr['operator'], instr['operator'])
                self.emit(f"  {asm_op:<6} {dest_reg}, {r_left}, {r_right}")

            # ------------------------------------------------------------------
            elif op == 'LOAD_STR':
                dest_reg = self.regs.alloc(instr['dest'])
                self.emit(f"  LOAD_STR {dest_reg}, \"{instr['value']}\"")

            # ------------------------------------------------------------------
            elif op == 'PRINT':
                src = instr['src']
                reg = self.resolve(src)
                if not reg.startswith('R'):
                    # Need to load into a register first
                    r = self.regs.alloc()
                    self.emit(f"  LOAD   {r}, {reg}")
                    reg = r
                self.emit(f"  PRINT  {reg}")

            # ------------------------------------------------------------------
            elif op == 'CALL':
                args_resolved = [self.resolve(a) for a in instr.get('args', [])]
                args_str = ', '.join(args_resolved)
                dest_reg = self.regs.alloc(instr['dest'])
                self.emit(f"  CALL   {instr['callee']}({args_str}) -> {dest_reg}")

        self.emit("")
        self.emit("; ============================")
        self.emit("; End of Program")
        self.emit("; ============================")

        return "\n".join(self.output)


def generate_code(instructions):
    gen = CodeGenerator()
    return gen.generate(instructions)