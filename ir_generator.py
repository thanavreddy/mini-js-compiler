# =============================================================================
# PHASE 4 — IR GENERATION (Three-Address Code)
# Converts AST into flat Three-Address Code (TAC) instructions.
#
# TAC instruction format (each is a dict):
#   {'op': 'ASSIGN',  'dest': 'x',  'src': 't0'}
#   {'op': 'BINOP',   'dest': 't0', 'left': 10, 'operator': '+', 'right': 20}
#   {'op': 'PRINT',   'src': 't1'}
#   {'op': 'LOAD_STR','dest': 't2', 'value': 'hello'}
#
# Temporaries are named t0, t1, t2 ...
# =============================================================================

class IRGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0

    def new_temp(self):
        name = f"t{self.temp_count}"
        self.temp_count += 1
        return name

    def emit(self, instruction):
        self.instructions.append(instruction)

    # -------------------------------------------------------------------------
    # Entry
    # -------------------------------------------------------------------------
    def generate(self, ast):
        for node in ast['body']:
            self.visit(node)
        return self.instructions

    # -------------------------------------------------------------------------
    # Visitors
    # -------------------------------------------------------------------------
    def visit(self, node):
        method = f"visit_{node['type']}"
        visitor = getattr(self, method, None)
        if visitor is None:
            raise NotImplementedError(f"[IR] No visitor for node type: {node['type']}")
        return visitor(node)

    def visit_VarDecl(self, node):
        src = self.visit(node['init'])
        self.emit({'op': 'ASSIGN', 'dest': node['name'], 'src': src})
        return node['name']

    def visit_ExprStmt(self, node):
        return self.visit(node['expression'])

    def visit_BinaryExpr(self, node):
        left  = self.visit(node['left'])
        right = self.visit(node['right'])
        dest  = self.new_temp()
        self.emit({
            'op': 'BINOP',
            'dest': dest,
            'left': left,
            'operator': node['op'],
            'right': right
        })
        return dest

    def visit_NumLiteral(self, node):
        return node['value']

    def visit_StrLiteral(self, node):
        dest = self.new_temp()
        self.emit({'op': 'LOAD_STR', 'dest': dest, 'value': node['value']})
        return dest

    def visit_Identifier(self, node):
        return node['name']

    def visit_MemberExpr(self, node):
        # Returns a string label like "console.log"
        obj  = node['object']['name'] if node['object']['type'] == 'Identifier' else '?'
        prop = node['property']
        return f"{obj}.{prop}"

    def visit_CallExpr(self, node):
        callee = self.visit(node['callee'])

        # Resolve arguments
        arg_refs = [self.visit(arg) for arg in node['args']]

        if callee == 'console.log':
            for ref in arg_refs:
                self.emit({'op': 'PRINT', 'src': ref})
        else:
            dest = self.new_temp()
            self.emit({'op': 'CALL', 'dest': dest, 'callee': callee, 'args': arg_refs})
            return dest

        return None


def generate_ir(ast):
    gen = IRGenerator()
    return gen.generate(ast)


# -------------------------------------------------------------------------
# Pretty printer for TAC
# -------------------------------------------------------------------------
def format_ir(instructions):
    lines = []
    for instr in instructions:
        op = instr['op']
        if op == 'ASSIGN':
            lines.append(f"  {instr['dest']}  =  {instr['src']}")
        elif op == 'BINOP':
            lines.append(f"  {instr['dest']}  =  {instr['left']} {instr['operator']} {instr['right']}")
        elif op == 'LOAD_STR':
            lines.append(f"  {instr['dest']}  =  \"{instr['value']}\"")
        elif op == 'PRINT':
            lines.append(f"  PRINT  {instr['src']}")
        elif op == 'CALL':
            args = ', '.join(str(a) for a in instr['args'])
            lines.append(f"  {instr['dest']}  =  CALL {instr['callee']}({args})")
        else:
            lines.append(f"  {instr}")
    return "\n".join(lines)