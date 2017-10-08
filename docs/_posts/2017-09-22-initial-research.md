---
layout: post
title:  "Initial research"
date:   2017-09-22 12:00:00 -0400
categories: devblog research jgf
---

Before beginning this project I've been assembling some prior work to try and get a handle on what this project will entail. To that end, I initially searched for existing C/C++ preprocessors written in Python. While I found [several](https://stackoverflow.com/questions/4350764/implementation-of-a-c-pre-processor-in-python-or-javascript) [projects](http://jinja.pocoo.org/docs/2.9/) that somehow combined python and C/C++ preprocessing they were, for the most part, somehow inserting C/C++ preprocessor stuff into python and not actually a preprocessor written in python.

I eventually happened upon [CPIP](http://cpip.sourceforge.net/), which was indeed a C/C++ preprocessor that was written in python, but unfortunately was last updated in 2012 and the mailing list and developer email are sadly silent. We considered using CPIP as a starting point for the project but CPIP unfortunately had a homebrew (and thus unmaintained) lexer/parser system. I made the decision to implement the preprocessor from scratch and make use of CPIP as an architectural reference.

To that end, I'm currently making friends with [the GNU C Preprocessor page](https://gcc.gnu.org/onlinedocs/cpp/) (which I made sure to download an offline copy of) and will maintain this blog as I work on this so the next poor soul to attempt a project like this will have somewhere to start.

(Writing this will also hopefully help me to organize and document my thoughts so I don't cowboy code my way through this whole thing.)

## A quick primer on preprocessing

_Disclaimer: this is probably fantastically wrong in some way that I'll discover down the line in an explosive fasion, but until then...._

Preprocessing is the stage before actual compilation of the program occurs, as the preprocessor works to resolve the `#include` statements (and any `#define`s, `#ifdef`s, macros, etc). When the preprocessor is finished you could dump a file that would be perfectly syntactically correct C++ that could get fed to a compiler that knows nothing about preprocessor language or macros. It (very probably) would be a very large file, since all the files `#include`d in would be just copy-pasted in (and all the files _that_ file `#include`d, and all the files _those_ files `#include`d...)

So, thankfully, this means the concerns of this project don't extend to the full length of the 1368 page C++ specifications document I'm working from [the isocpp](https://isocpp.org/std/the-standard) page, and for the most part confines us to the sections on lexical conventions (p. 17-24) and preprocessor directives (p. 426-437).

Also, thank you to the designers of C++ for providing a wonderful lexical tree all ready to go on page 426.

![provided lexical diagram](./assets/provided_lexical_tree.png)

That'll be useful when I'm hacking together my Ply and Lexx setup.

Anyway, back to the primer:

There are a couple things complicating our journey to build a preprocessor. First, most preprocessors don't just construct a massive C++ file that gets handed off to the compiler. If we did, the errors emitted by the compiler would be impossible to trace back to your own code. Most existing preprocessors pass the tokens they extract from the source files to the compiler directly via a binary stream. Since we seek to replace the functionality of existing C++ preprocessors, we'll have to do the same.

There's also the new functionality that we're going to build out, specifically the ability to include snippets of python in preprocessor directives that will be executed at compile time with a shared namespace to access the symbol table used by the standard preprocessor macros. These python directives will be capable of emitting output that will be copied into the program.

Something important to note is that we have no intention of making it possible to define a macro in python that will be executed during runtime--that kind of cross-language weirdness is out of scope. We're just looking to crank up the power of C++ macros, basically.

So, in summary:

 1. Fetch and copy-paste any `#include`d files
 2. Handle the logical/flow control preprocessor directives
     a. Include/remove code as dictated (`#ifdef` and the like)
 3. Expand macros
 4. Remove comments
 5. Pass the token stream, with diagnostic/location metadata, to compiler

I'll start with sketching out a basic lexer setup and then expand it with tests.
