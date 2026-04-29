# =============================================================================
# PHASE 2 — PARSER (Syntactic Analysis)
# Converts token list into an Abstract Syntax Tree (AST).
#
# Grammar supported:
#   program         := statement*
#   statement       := var_decl | expr_stmt
#   var_decl        := ('let'|'const'|'var') IDENTIFIER '=' expression ';'
#   expr_stmt       := expression ';'
#   expression      := additive
#   additive        := multiplicative (('+' | '-') multiplicative)*
#   multiplicative  := primary (('*' | '/') primary)*
#   primary         := NUMBER | STRING | IDENTIFIER | call_expr | '(' expression ')'
#   call_expr       := IDENTIFIER ('.' IDENTIFIER)* '(' args ')'
# =============================================================================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def peek(self):
        return self.tokens[self.pos]

    def consume(self, expected_type=None, expected_value=None):
        tok = self.tokens[self.pos]
        if expected_type and tok.type != expected_type:
            raise SyntaxError(
                f"[Parser] Expected type {expected_type} but got {tok.type} "
                f"('{tok.value}') at line {tok.line}"
            )
        if expected_value and tok.value != expected_value:
            raise SyntaxError(
                f"[Parser] Expected '{expected_value}' but got '{tok.value}' "
                f"at line {tok.line}"
            )
        self.pos += 1
        return tok

    def match(self, type_, value=None):
        tok = self.peek()
        if tok.type == type_ and (value is None or tok.value == value):
            return True
        return False

    # -------------------------------------------------------------------------
    # Entry
    # -------------------------------------------------------------------------
    def parse(self):
        body = []
        while not self.match('EOF'):
            body.append(self.parse_statement())
        return {'type': 'Program', 'body': body}

    # -------------------------------------------------------------------------
    # Statements
    # -------------------------------------------------------------------------
    def parse_statement(self):
        tok = self.peek()

        if tok.type == 'KEYWORD' and tok.value in ('let', 'var', 'const'):
            return self.parse_var_decl()

        return self.parse_expr_stmt()

    def parse_var_decl(self):
        kind_tok = self.consume('KEYWORD')
        name_tok = self.consume('IDENTIFIER')
        self.consume('ASSIGN')
        init = self.parse_expression()
        if self.match('SEMI'):
            self.consume('SEMI')
        return {
            'type': 'VarDecl',
            'kind': kind_tok.value,
            'name': name_tok.value,
            'init': init,
            'line': kind_tok.line
        }

    def parse_expr_stmt(self):
        expr = self.parse_expression()
        if self.match('SEMI'):
            self.consume('SEMI')
        return {'type': 'ExprStmt', 'expression': expr}

    # -------------------------------------------------------------------------
    # Expressions
    # -------------------------------------------------------------------------
    def parse_expression(self):
        return self.parse_additive()

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.match('OPERATOR') and self.peek().value in ('+', '-'):
            op = self.consume('OPERATOR').value
            right = self.parse_multiplicative()
            left = {'type': 'BinaryExpr', 'op': op, 'left': left, 'right': right}
        return left

    def parse_multiplicative(self):
        left = self.parse_primary()
        while self.match('OPERATOR') and self.peek().value in ('*', '/'):
            op = self.consume('OPERATOR').value
            right = self.parse_primary()
            left = {'type': 'BinaryExpr', 'op': op, 'left': left, 'right': right}
        return left

    def parse_primary(self):
        tok = self.peek()

        if tok.type == 'NUMBER':
            self.consume()
            return {'type': 'NumLiteral', 'value': tok.value}

        if tok.type == 'STRING':
            self.consume()
            return {'type': 'StrLiteral', 'value': tok.value}

        if tok.type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr

        if tok.type == 'IDENTIFIER':
            self.consume()
            node = {'type': 'Identifier', 'name': tok.value, 'line': tok.line}

            # Member expression: console.log
            while self.match('DOT'):
                self.consume('DOT')
                prop = self.consume('IDENTIFIER')
                node = {
                    'type': 'MemberExpr',
                    'object': node,
                    'property': prop.value,
                    'line': tok.line
                }

            # Call expression: (...)
            if self.match('LPAREN'):
                self.consume('LPAREN')
                args = []
                while not self.match('RPAREN'):
                    args.append(self.parse_expression())
                    if self.match('COMMA'):
                        self.consume('COMMA')
                self.consume('RPAREN')
                node = {'type': 'CallExpr', 'callee': node, 'args': args, 'line': tok.line}

            return node

        raise SyntaxError(f"[Parser] Unexpected token '{tok.value}' at line {tok.line}")


def parse(tokens):
    return Parser(tokens).parse()