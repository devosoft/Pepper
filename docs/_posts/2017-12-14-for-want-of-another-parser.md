---
layout: post
title:  "Best Practices"
date:   2017-11-14 12:00:00 -0400
categories: devblog jgf macros parser
---
_written by [Jake Fenton](https://github.com/bocajnotnef)_

Here's my current problem: Macro expansion

Suppose you have a macro:

~~~
#define quail(a, b) a + b
~~~

Suppose you have another macro:

~~~
#define potato(a, b, c) quail(a, b) + c
~~~

And then you have code:

~~~
int something = potato(1, 2, 3);
~~~

If you're the preprocessor, you'll have some kind of parser that scans the incoming code for identifiers to expand. You see `potato` and go "Oh, hey, I have a `potato` macro defined in my symbol table! I should expand that." And the parser pulls the arguments for potato, builds the syntax tree, builds some magic and then outputs `int something = quail(a, b) + c`.

Which is great! We expanded the `potato` macro....but now we have the `quail` macro to also expand. The preprocessor spec is aware of this, and has the following to say:

    All arguments to a macro are completely macro-expanded before they are substituted into the macro body. After substitution, the complete text is scanned again for macros to expand, including the arguments. This rule may seem strange, but it is carefully designed so you need not worry about whether any function call is actually a macro invocation.

This is a relatively straightforward rule: If you expand a macro, you should parse the expanded line to see if there are any other macros in the expansion. Unfortunately this introduces some complexity in the lexer and parser themselves.

The PLY lex/parse stack takes an input stream and tokenizes it, according to the language specification in the lexer. This is an on-line (i.e., streamable) but single-pass process. The token stream, once ended, then gets passed to the parser which determines if it can build a valid parse tree. (This process requires the incoming token stream to be finished.) Once the parse tree is built, we execute the Preprocess() function call on the root node, which begins building the output from the preprocessor which, in theory, can be handled by just the C/C++ compiler.

### Aside: the Abstract Syntax Tree

This should probably be a post in and of itself, but it's necessary for full understanding of the issue:

The Abstract Syntax Tree (AST) is the structure that holds sets of tokens, as specified by the language specification (lexer) and the grammar specification (parser). The tree holds the entire structure of a program--the root node is typically a Program node, which contains many Statement nodes. The Statement nodes can derive to things like control statements, arithmetic operations, etc.

![an Abstract Syntax Tree](https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Abstract_syntax_tree_for_Euclidean_algorithm.svg/400px-Abstract_syntax_tree_for_Euclidean_algorithm.svg.png)

_From [Wikipedia](https://en.wikipedia.org/wiki/Abstract_syntax_tree)_

The tree is abstract in that the 'arguments' to each of the nodes are variable, so long as they fit the format of the node. Thus, you can have abstract 'statements' within a 'for' or 'while' type of node.

To build the output from this tree, be it intermediate code for a compiler or c++ code without preprocessor directives for a compiler, you'd call some method on the root node that would cascade down the tree, building the output from each of the nodes and stitching it together to fit the language.

### ...back to the problem...

So, the issue we have is that when you expand a macro you're substituting C++ code--maybe with some arguments--into an existing token stream. This changes the stream significantly, but there isn't a way to re-lex and re-parse it. We're in the parsing stage, which means lexing is complete. Re-lexing the string could result in input that cannot be parsed, if it doesn't use the grammar correctly. If we can't re-lex and re-parse the string, how do we check for additional macros to expand?

Some possible solutions:

 1. Parse all macros for identifiers of other macros--if found, auto-expand.
     * Problem: macros-within-macros could have argument lists that would need to be parsed and expanded. Difficult to do with variables.
 1. Instantiate a second parser/lexer stack to chew through 'lines' of preprocessor output, within the preprocessor, to check for additional macros to expand.
     * Good: relatively lightweight, allows preprocessing to be a contiguous process (e.g. no multi-pass), which should have performance benefits
     * Bad: requires building another 'preprocessor' stack to handle finding identifiers and processing argument lists for expansion; more code to maintain
 1. Re-parse the entirety of the output from the preprocessor to check for more macros to expand
    * Good: Simple-ish to implement, less repeated code
    * Bad: Have to handle including the macro definitions for the re-run instances, inefficient as all hell, gonna be ridiculously slow.

## The plan

I'm going to build a simplified parser that will scan for identifiers in a line and work to expand macros. It'll inherit a symbol table of macro expansions from the root parser. Hopefully this will bypass the issues with having to "re-parse" a line, since we'll be using an external parser, and won't give too much trouble with expanding macros.

This method should be more efficient than others, since we'll only be re-scanning individual lines that have had a macro expanded in them, and not the entire program.

_Caveat:_ Before I build an entirely new (though simple) parser, I'll try some experiments to see if we can get away with making a second instance of the existing parser.