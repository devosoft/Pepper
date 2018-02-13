---
layout: post
title: "Building Integration Tests"
date: 2018-01-30 8:50:00 -0400
categories: devblog research cmi
---

_written by [Cyndy Ishida](https://github.com/cyndyishida)_

Building Integration Tests is my first notable contribution to the Pepper Project.
I'm hoping that the tests I design will later be the way we actually pipeline Pepper into a normal compiler.
Currently the chain of steps is to run a command like:

~~~
Pepper some_file.cpp --output_file some_file.ii
~~~

Here it invokes Pepper and runs the output of the preprocessor to the same file name with 
the extension of 'ii' which is just an extension that signals to the compiler to skip the pre-processing stage. 

Only in the GNU compiler, you can actually avoid changing the file name with using the '-fpreprocessed' flag. 

Based on a global variable 'CXX_FLAG' which I'm hoping in the future to read the environment variable for it 
when it's being ran for either G++ or Clang. I don't see there being a huge need to support MSVC compilers, 
but what do I know. 
~~~
CXX_FLAG -Wall -std=c++17 -o output some_file.ii
~~~

Currently I run that to build the pepper-ed executable and also run the original c++ file to the normal compilation
 stage and compare both standard outputs, as per Jake's suggestion.
 
 
 ###Concerns for Pepper with Compilation
I would like to actually run Pepper in production and redirect the output from the compiler to the Pepper interface.
This would be pretty simple with the subprocess module and storing the information from standard out and error. 
A few things that trouble me about my current stream of execution moving to production is portability. I don't really see 
 spawning a ton of threads as a viable way of pipeline-ing Pepper, especially if this would ever be used in a memory and
  processor(s) intensive situation. I think it would be worth looking into.
  
  ###GPU Support
  As stated above, I really only thought about using Pepper with clang or g++ but applying NVICC support would be cool. 
  Well maybe just, modularized enough to support any C++ compiler. 
