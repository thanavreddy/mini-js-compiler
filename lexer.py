# =============================================================================
# PHASE 1 — LEXER (Lexical Analysis)
# Converts raw JS source string into a flat list of tokens.
# =============================================================================

class Token:
    def __init__(self, type_, value, line=1):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line})"


KEYWORDS = {'let', 'var', 'const', 'if', 'else', 'while', 'function', 'return', 'true', 'false'}


def tokenize(source):
    tokens = []
    i = 0
    line = 1

    while i < len(source):
        ch = source[i]

        # Newline tracking
        if ch == '\n':
            line += 1
            i += 1
            continue

        # Whitespace
        if ch in (' ', '\t', '\r'):
            i += 1
            continue

        # Single-line comments
        if ch == '/' and i + 1 < len(source) and source[i + 1] == '/':
            while i < len(source) and source[i] != '\n':
                i += 1
            continue

        # Numbers (integers and floats)
        if ch.isdigit():
            val = ''
            while i < len(source) and (source[i].isdigit() or source[i] == '.'):
                val += source[i]
                i += 1
            tokens.append(Token('NUMBER', float(val) if '.' in val else int(val), line))
            continue

        # Strings (double or single quoted)
        if ch in ('"', "'"):
            quote = ch
            i += 1
            val = ''
            while i < len(source) and source[i] != quote:
                val += source[i]
                i += 1
            i += 1  # closing quote
            tokens.append(Token('STRING', val, line))
            continue

        # Identifiers and keywords
        if ch.isalpha() or ch == '_':
            val = ''
            while i < len(source) and (source[i].isalnum() or source[i] == '_'):
                val += source[i]
                i += 1
            ttype = 'KEYWORD' if val in KEYWORDS else 'IDENTIFIER'
            tokens.append(Token(ttype, val, line))
            continue

        # Two-character operators
        two = source[i:i+2]
        if two in ('==', '!=', '<=', '>=', '&&', '||'):
            tokens.append(Token('OPERATOR', two, line))
            i += 2
            continue

        # Single-character tokens
        single_map = {
            '+': 'OPERATOR', '-': 'OPERATOR', '*': 'OPERATOR', '/': 'OPERATOR',
            '<': 'OPERATOR', '>': 'OPERATOR',
            '=': 'ASSIGN',
            ';': 'SEMI', ',': 'COMMA', '.': 'DOT',
            '(': 'LPAREN', ')': 'RPAREN',
            '{': 'LBRACE', '}': 'RBRACE',
        }
        if ch in single_map:
            tokens.append(Token(single_map[ch], ch, line))
            i += 1
            continue

        raise SyntaxError(f"[Lexer] Unknown character '{ch}' at line {line}")

    tokens.append(Token('EOF', None, line))
    return tokens