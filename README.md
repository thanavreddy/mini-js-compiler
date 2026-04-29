# Mini JS — Educational Mini Compiler

This repository implements a small, educational JavaScript-like compiler demonstrating a complete 6-phase compilation pipeline. It's intended for learning and experimentation rather than production use.

## What it does
- Takes a small subset of JavaScript (variable declarations, arithmetic, string concatenation, and simple call expressions like `console.log`).
- Runs the code through six phases: Lexical analysis, Parsing (AST), Semantic analysis, IR generation (three-address code), Optimization, and Code generation (pseudo-assembly).

## Pipeline (phases)
1. Lexer (`lexer.py`) — tokenizes source text into tokens (numbers, strings, identifiers, operators, punctuation).
2. Parser (`parser.py`) — recursive-descent parser that builds an AST for a tiny grammar (var decls, expressions, call/member expressions).
3. Semantic Analyzer (`semantic.py`) — builds a symbol table and enforces simple rules: no use-before-declare, no redeclaration, and basic type checks for arithmetic.
4. IR Generator (`ir_generator.py`) — lowers the AST to flat three-address code (TAC) using temporaries `t0`, `t1`, ...
5. Optimizer (`optimizer.py`) — three passes: constant folding, copy propagation, and dead-code elimination (targets temporaries and constants).
6. Code Generator (`code_generator.py`) — emits readable pseudo-assembly using a small register allocator (R0–R7).

## How to run
From the project root, use the CLI implemented in `compiler.py`.

- Run default sample (embedded example):

```bash
python "compiler.py"
```

- Run a source file:

```bash
python "compiler.py" -f samples/basic_arithmetic.js
```

- Provide code on the command line:

```bash
python "compiler.py" -c "let a = 1; console.log(a);"
```

- Read source from STDIN:

```bash
cat mycode.js | python "compiler.py" -
```

## Samples
See the `samples/` folder for example inputs (arithmetic, strings, optimizer tests, and semantic error examples). The file `samples/README.md` shows commands to run them.

## Limitations
- Very small language subset: no control flow (`if`, `while`) or user-defined functions.
- Semantic analysis is intentionally simple and conservative; many calls and members are treated as `unknown`.
- Code generation targets a pseudo-assembly for illustration only.

## Extending the compiler
- Add grammar rules in `parser.py` and corresponding AST node visitors in `ir_generator.py` and `semantic.py`.
- Add optimization passes in `optimizer.py`.
- Replace pseudo-assembly generation in `code_generator.py` with a real backend or emitter.

## Where to look first
- `compiler.py` — entrypoint and CLI
- `lexer.py` / `parser.py` — for language front-end
- `ir_generator.py` / `optimizer.py` / `code_generator.py` — for IR and backend

If you'd like, I can:
- run one of the samples now, or
- add an example that exercises a specific pass (e.g., dead-code elimination), or
- add `if`/`while` support.
