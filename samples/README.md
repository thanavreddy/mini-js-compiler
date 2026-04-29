# Sample JS files for Mini Compiler

Run any sample with the `compiler.py` CLI. From the workspace root:

```bash
python "compiler.py" -f samples/basic_arithmetic.js
python "compiler.py" -f samples/string_concat.js
python "compiler.py" -f samples/optimizer_examples.js
python "compiler.py" -f samples/console_log.js
python "compiler.py" -f samples/float_and_parentheses.js
```

To see semantic errors (this will raise `SemanticError` and print diagnostics):

```bash
python "compiler.py" -f samples/semantic_errors.js
```

You can also pass code directly:

```bash
python "compiler.py" -c "let a = 1; console.log(a);"
```
