# =============================================================================
# PHASE 3 — SEMANTIC ANALYSIS
# Walks the AST and enforces semantic rules:
#   1. No use of undeclared variables
#   2. No re-declaration of a variable in the same scope
#   3. Type consistency check for binary expressions (numbers only for arithmetic)
# Reports all errors with line numbers.
# =============================================================================

class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}   # name -> {'kind': 'let'|'const'|'var', 'type': 'number'|'string'|'unknown'}
        self.errors = []

    def analyze(self, ast):
        for node in ast['body']:
            self.visit(node)
        if self.errors:
            raise SemanticError("\n".join(self.errors))
        return self.symbol_table

    # -------------------------------------------------------------------------
    # Visitors
    # -------------------------------------------------------------------------
    def visit(self, node):
        method = f"visit_{node['type']}"
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        return 'unknown'

    def visit_VarDecl(self, node):
        name = node['name']
        line = node.get('line', '?')

        if name in self.symbol_table:
            self.errors.append(
                f"[Semantic] Line {line}: Variable '{name}' has already been declared."
            )

        init_type = self.visit(node['init'])
        self.symbol_table[name] = {'kind': node['kind'], 'type': init_type}
        return init_type

    def visit_ExprStmt(self, node):
        return self.visit(node['expression'])

    def visit_BinaryExpr(self, node):
        left_type  = self.visit(node['left'])
        right_type = self.visit(node['right'])

        if left_type == 'string' or right_type == 'string':
            if node['op'] != '+':
                self.errors.append(
                    f"[Semantic] Operator '{node['op']}' cannot be applied to string operands."
                )
            return 'string'
        return 'number'

    def visit_NumLiteral(self, node):
        return 'number'

    def visit_StrLiteral(self, node):
        return 'string'

    def visit_Identifier(self, node):
        name = node['name']
        line = node.get('line', '?')
        if name not in self.symbol_table:
            self.errors.append(
                f"[Semantic] Line {line}: Variable '{name}' is used before declaration."
            )
            return 'unknown'
        return self.symbol_table[name]['type']

    def visit_MemberExpr(self, node):
        # console.log etc — treat as valid, return unknown
        return 'unknown'

    def visit_CallExpr(self, node):
        for arg in node['args']:
            self.visit(arg)
        return 'unknown'


def analyze(ast):
    analyzer = SemanticAnalyzer()
    symbol_table = analyzer.analyze(ast)
    return symbol_table