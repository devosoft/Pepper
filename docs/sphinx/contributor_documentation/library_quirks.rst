Library Quirks
==============

Exceptions in Pepper
--------------------

A quirk of the PLY library that Pepper relies on for the parser and lexer evaluation is that PLY consumes any SyntaxErrors
emitted within the parser--which essentially includes any syntax errors that also get emitted by the Abstract Syntax Tree
or the Symbol Table, since such errors are likely generated in the course of running the parser.

To work around this, the SymbolTable defines a couple extra exception types; the `PepperSyntaxError` and the `PepperInternalError`.
The `PepperSyntaxError` is for when someone bungles the syntax of a macro or directive. This can be detected in either the parser or
in error-checking code within Pepper (like the `_validate_args` function in `symbol_table.MacroExpansion`) or in the parser's `p_error`
function.

Alternatively if Pepper encounters a different problem--a KeyError in a dictionary or a failed file write, etc--the preprocessor will catch
and rethrow the exception within a `PepperInternalError`, which also prompts the user to report the issue to the repository.