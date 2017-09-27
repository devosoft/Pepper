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