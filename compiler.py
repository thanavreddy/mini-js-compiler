# =============================================================================
# COMPILER ENTRYPOINT
# Chains all 6 phases and prints the output of each phase clearly.
# =============================================================================

from lexer           import tokenize
from parser          import parse
from semantic        import analyze
from ir_generator    import generate_ir, format_ir
from optimizer       import optimize
from code_generator  import generate_code

# ─────────────────────────────────────────────────────────────────────────────
DIVIDER  = "=" * 60
SDIVIDER = "-" * 60

def section(title):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)

# ─────────────────────────────────────────────────────────────────────────────

def compile_code(source):
    print(f"\n{DIVIDER}")
    print("  MINI JS COMPILER  —  6-Phase Pipeline")
    print(DIVIDER)
    print("\n[Input JavaScript Source]")
    print(SDIVIDER)
    print(source.strip())

    # ── Phase 1: Lexer ────────────────────────────────────────────────────────
    section("PHASE 1 — LEXER  (Lexical Analysis)")
    tokens = tokenize(source)
    for tok in tokens:
        if tok.type != 'EOF':
            print(f"  {tok.type:<12} {repr(tok.value):<20}  line {tok.line}")

    # ── Phase 2: Parser ───────────────────────────────────────────────────────
    section("PHASE 2 — PARSER  (Syntactic Analysis → AST)")
    ast = parse(tokens)
    import json
    print(json.dumps(ast, indent=2))

    # ── Phase 3: Semantic Analysis ────────────────────────────────────────────
    section("PHASE 3 — SEMANTIC ANALYSIS")
    symbol_table = analyze(ast)
    print("  Symbol Table:")
    print(f"  {'Variable':<15} {'Kind':<8} {'Type'}")
    print(f"  {SDIVIDER[:40]}")
    for name, info in symbol_table.items():
        print(f"  {name:<15} {info['kind']:<8} {info['type']}")
    print("\n  [OK] No semantic errors found.")

    # ── Phase 4: IR Generation ────────────────────────────────────────────────
    section("PHASE 4 — IR GENERATION  (Three-Address Code)")
    ir = generate_ir(ast)
    print(format_ir(ir))

    # ── Phase 5: Optimizer ────────────────────────────────────────────────────
    section("PHASE 5 — OPTIMIZER")
    optimized_ir = optimize(ir)
    print("  [Passes: Constant Folding → Copy Propagation → Dead Code Elimination]")
    print()
    print(format_ir(optimized_ir))

    # ── Phase 6: Code Generation ──────────────────────────────────────────────
    section("PHASE 6 — CODE GENERATION  (Pseudo-Assembly)")
    asm = generate_code(optimized_ir)
    print(asm)

    return asm


# ─────────────────────────────────────────────────────────────────────────────
# Sample programs — change this to test different inputs
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Mini JS Compiler — run pipeline on input')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--file', help='Read source from file')
    group.add_argument('-c', '--code', help='Provide source code as a command-line string')
    group.add_argument('-', dest='stdin', action='store_true', help='Read source from STDIN')
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as fh:
            source = fh.read()
    elif args.code:
        source = args.code
    elif args.stdin:
        source = sys.stdin.read()
    else:
        # default sample
        source = """
        let x = 10 + 20;
        let y = x * 2;
        let z = y + 5;
        console.log(z);
        """

    compile_code(source)