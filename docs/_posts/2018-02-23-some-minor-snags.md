---
layout: post
title:  "Minor Snags, Now Solved"
date:   2018-02-23 12:00:00 -0400
categories: devblog jgf parser macros ply
---
_written by [Jake Fenton](https://github.com/bocajnotnef)_

Things have been quiet for a bit in the devblog world and I ran into a few issues that I thought bore mentioning, though none deserve a blog post in their own right. Thus, this.

## Turns out, Ply eats syntax error exceptions

Pepper makes use of the [Python PLY package](https://github.com/dabeaz/ply), a python reimplementation of the lex and yacc language parsing tools. It allows you to specify the specification for tokens which are then used in a parser grammar that you specify.

Part of this grammar is an error state, which you hit if you input something to the parser that doesn't match its syntax--your standard syntax error, really.

PLY requires that you have this rule and that it in some way handles this state--it can do anything it wants, really, but the sensible actions are limited to something like "halt the program" or "ignore the error" or "emit an exception". I chose the last route.

Seeing as Python already had a SyntaxError exception that I could freely `raise`, I made the error rule puke a SyntaxError with the current parse object.

I also didn't test the emission of that exception. Which was arguably my first mistake, since it would have caught the next.

Some time later, I'm making it so we can have macros with arguments and I'm chasing a bug where output is just missing from the emitted intermediate file, which in theory isn't possible.

The way the preprocessor is structured is that it preprocesses input line-by-line and appends the output to a gigantic list (because I have this vauge notion that it'll be useful to have lying around) before writing the whole thing out to file. With this structure it wasn't possible to have a partial line being written out--either you succeeded in parsing the whole line, and then the whole file, and wrote it all out, or you broke somewhere in your single line and crashed the whole program with an exception.

What I was seeing was something like:

```
int main() {
    cout << "some stuff" << endl;
    cout <<
}
```

as output from the preprocessor. What I was expecting was something like:

```
int main() {
    cout << "some stuff" << endl;
    cout << someMacroExpansion(a, b c) << endl;
}
```

Clearly something had gone horribly wrong.

The long and short of it is that PLY was internally eating the SyntaxError my error rule emitted, since the parser was getting something it didn't know how to handle, and it simply returned the truncated parse tree which happily emitted as much output as it could, which then got written to python.

So much for "errors should never pass silently", eh?

In the end I made my own exception, `PepperSyntaxError`, derived from Exception, to emit instead of the default SyntaxError. I'm a little curious what PLY is doing under the hood where eating SyntaxErrors is normal behavior, but I'm not sure I'm motivated to find out.

This ended up feeding nicely into a structure in the preprocessor that catches any internal errors (e.g., ones not caused by bad syntax) and prepends a "Hey, please report this error" with a link to the issue tracker, in the hopes of being proactive in solving user problems when they inevitably hit a corner case I haven't thought of.

## Flirting with Parsing C++

Parsing C++ is one of my worst nightmares.

Somewhat recently I happened across [a blog post](https://eli.thegreenplace.net/2011/05/02/the-context-sensitivity-of-cs-grammar-revisited/) by a fellow compiler fiddler (indeed, someone who built a full on c parser in python to do lexical analysis!) which, initially, got my hopes up about solving a problem I was having; specifically, that I needed to parse list-like-structures from within parentheses to handle function-like macro expansions, since commas can be meaningful in c++ in a bunch of other places and I initially thought I'd have to parse the arguments themselves.

As Eli of TheGreenPlace notes, parsing C++ is phenomenally difficult in general and explicitly impossible with a YACC style parser. I don't pretend to understand why or how, I just know I'd like to avoid that complexity as much as I can since it doesn't seem necessary for the work I'm doing and would add phenomenal complexity--and thus speed cost, in both performance and development--that just isn't needed.

My "reference implementation" of the preprocessor (read: g++'s preprocessor) appears to handle commas rather roughly as well, which may save me. With input like:

```
# define TypedThingyMajig(type) std::Vector<type>

int main() {
   auto c = TypedThingyMajig(pair<int, float>);
}
```

you get error output like:

```
test.cpp:4:46: error: macro "TypedThingyMajig" passed 2 arguments, but takes just 1
    auto c = TypedThingyMajig(pair<int, float>);
                                              ^
test.cpp: In function ‘int main()’:
test.cpp:4:13: error: ‘TypedThingyMajig’ was not declared in this scope
    auto c = TypedThingyMajig(pair<int, float>);
```

So yay, I can be heavy handed with the parsing of c++-like structures and save myself some headache.

## Minor performance concerns

Pepper is primarily a command line tool. As such, many of the tests I've written are assertions against the output written by Pepper when called as a subprocess. This is slow as hell for a python unit testing framework that's expecting to call a ton of library functions, and is remarkably frustrating for me because it's slow and clunky as hell.

At some point I intend to sit down and rewrite the tests so they make use of as many module-level function hooks as they can to test equivalent functionality, but as it stands most of the tests are command line calls on carefully structured input files.

While I was developing the function like macro expansions I ran into several instances of some test cases failing intermittently by whacking into the 2-second timeout I allot for subprocess runs, which seemed like a decently high ceiling for the small test cases I was running.

Doing some profiling with SnakeViz and cprofile it looks like most of the program's time is spend standing up all the individual modules of Pepper--85% of the program's time is spent handling `import` statements and the machinery involved in standing up modules. Obviously this is skewed by the fact that we're using really, really small test cases and aren't actually doing that much heavy lifting within the preprocessor itself. We'll have to construct some larger cases to get a decent look into performance before we start fiddling, but it's something to be aware of as our test case library swells. Nobody likes tests that take forever to run.

## Next steps in development

Handling function like macros was one of the last major components that needed to be finished before we could begin more parallel development. Now that it's done I'm hoping we can start running multiple branches in tandem, and expanding the integration test library.

Next on the docket is handling `#if` directives, which will involve some parsing of code, which I am very not excited about. We'll also be building in `#pragma` functionality and things like `__VA__ARGS__` within macros themselves, a prerequisite for a lot of the macros in the Empirical library, which we'll be using as most of our acceptance tests once we reach a more feature-complete state.

The general roadmap for development is things that block us from compiling a Hello World style program, which really means being able to preprocess a decent amount of the C++ and C standard libraries.