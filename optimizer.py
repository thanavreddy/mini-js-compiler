# =============================================================================
# PHASE 5 — OPTIMIZER
# Applies optimization passes on the TAC instruction list.
#
# Passes implemented:
#   1. Constant Folding    — evaluates BINOPs with two constant operands at
#                            compile time (e.g. 10 + 20  →  30)
#   2. Copy Propagation    — replaces uses of a variable with its known
#                            constant value when safe
#   3. Dead Code Elimination — removes ASSIGN instructions whose destination
#                              is never read again
# =============================================================================

def is_number(val):
    return isinstance(val, (int, float))


# =============================================================================
# Pass 1: Constant Folding
# =============================================================================
def constant_folding(instructions):
    result = []
    for instr in instructions:
        if instr['op'] == 'BINOP' and is_number(instr['left']) and is_number(instr['right']):
            op = instr['operator']
            l, r = instr['left'], instr['right']
            if   op == '+': folded = l + r
            elif op == '-': folded = l - r
            elif op == '*': folded = l * r
            elif op == '/' and r != 0: folded = l / r
            else: folded = None

            if folded is not None:
                # Collapse to integer if no fractional part
                if isinstance(folded, float) and folded.is_integer():
                    folded = int(folded)
                result.append({'op': 'ASSIGN', 'dest': instr['dest'], 'src': folded})
                continue
        result.append(instr)
    return result


# =============================================================================
# Pass 2: Copy Propagation
# =============================================================================
def copy_propagation(instructions):
    # Build a map: variable -> constant value (only track constants)
    const_map = {}
    result = []

    for instr in instructions:
        op = instr['op']

        if op == 'ASSIGN':
            src = instr['src']
            # If src is itself in the const_map, propagate further
            if src in const_map:
                src = const_map[src]
                instr = {**instr, 'src': src}
            if is_number(src):
                const_map[instr['dest']] = src
            else:
                # If assigned from a non-constant, invalidate
                const_map.pop(instr['dest'], None)
            result.append(instr)

        elif op == 'BINOP':
            left  = const_map.get(instr['left'],  instr['left'])
            right = const_map.get(instr['right'], instr['right'])
            instr = {**instr, 'left': left, 'right': right}
            result.append(instr)

        elif op == 'PRINT':
            src = instr['src']
            src = const_map.get(src, src)
            result.append({**instr, 'src': src})

        else:
            result.append(instr)

    return result


# =============================================================================
# Pass 3: Dead Code Elimination
# =============================================================================
def dead_code_elimination(instructions):
    # Find all variables/temps that are actually read
    used = set()
    for instr in instructions:
        op = instr['op']
        if op == 'BINOP':
            if not is_number(instr['left']):
                used.add(instr['left'])
            if not is_number(instr['right']):
                used.add(instr['right'])
        elif op == 'ASSIGN':
            if not is_number(instr['src']):
                used.add(instr['src'])
        elif op == 'PRINT':
            src = instr['src']
            if not is_number(src) and not isinstance(src, str) or isinstance(src, str) and not src.startswith('"'):
                used.add(src)
        elif op == 'CALL':
            for a in instr.get('args', []):
                if not is_number(a):
                    used.add(a)

    result = []
    for instr in instructions:
        if instr['op'] == 'ASSIGN' and instr['dest'] not in used:
            # Only eliminate pure temporaries (t0, t1, ...), not user variables
            if instr['dest'].startswith('t') and instr['dest'][1:].isdigit():
                continue  # dead temp — drop it
        result.append(instr)

    return result


# =============================================================================
# Entry
# =============================================================================
def optimize(instructions):
    instructions = constant_folding(instructions)
    instructions = copy_propagation(instructions)
    instructions = dead_code_elimination(instructions)
    return instructions