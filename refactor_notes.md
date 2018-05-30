# Evil Refactor Plan

## Two parsers

We will have a parser for the preprocessor language, since that's mostly separate from the rest of what we have to care about, and a parser for c++ that might contain macro calls and such. This should reduce complexity in both parsers.

## Handling lines

Since c++ statements can span multiple lines we're just going to chunk files between their preprocessor directives. Everything inbetween a directive gets ingested at once, which should let us handle multiline statements without too much trouble.

## list structures

We'll consume braces, brackets, and parens structures, since they can be used to group macro arguments. We need to make sure we can write them out relatively unchanged if they aren't relevant to macros.

## whitespace

binary, there-or-not-there; will still complicate parse structures a little, sadly.
