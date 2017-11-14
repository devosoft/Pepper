---
layout: post
title:  "Best Practices"
date:   2017-11-14 12:00:00 -0400
categories: devblog jgf best-practices
---
_written by [Jake Fenton](https://github.com/bocajnotnef)_

In my first programming job, as a freshman at Michigan State, I was told by the lead engineer of the project [(Michael Crusoe)](https://twitter.com/biocrusoe) that, for best practices, you should write policy and then write software to enforce that policy. That's been my goal with how I've set up best practices for the Pepper project.

There's really three things, I think, that are important in a library, from a development perspective. It should have automated tests, it should be readable code and it should have documentation. All of this is important in general but it's absolutely critical if a project is to be open-source and to have outside contributors.

Here's a quick overview of how we use these within Pepper:

## Testing

I was lucky enough to be introduced to automated testing very early in on in my development career. The [khmer project](https://github.com/dib-lab/khmer), which you'll note is where a lot of these insights come from, made extensive use of automated tests. They had about 80% coverage when I joined the project and above 90% when I left. (Very little of which actually had to do with me, honestly.)

The tests were fantastic peace of mind--you could run them after you added new code to an existing script to make sure the rest of the script ran as expected. You could run the tests after a major refactor to make sure everything worked still. Dependency update? New release? Pull request from an unknown, outside contributor? You can run the tests and make sure nothing is broken.

The Pepper project has an automates test framework in place, pytest, that can be run locally and by the CI server. If any test fails, the CI will fail your branch and you won't be able to merge it in. (Thanks to Github for adding that policy.)

Also like the khmer project, Pepper enforces test coverage. If you add code that isn't covered by the test suite, the CI will fail your build. This ensures that if you add new functionality you have to add the corresponding tests pass well. The coverage check is run against the diff of what you add, however, so you won't get yelled at for existing holes in coverage. (Though, in theory, if we start fully covered and we require that everything added is fully covered, no coverage holes can happen.)

Of course, you could just write a test that passes always, no matter what your code does. We don't have a way to automate enforcement of writing good tests--that will still require human eyes. Code review is still also important.

With the automated enforcement of both passing tests and test coverage Pepper should remain a well tested library, covered by easy-to-use automated tests which are enforced by CI and can be run locally.

## Readable Code

Most will agree that having a consistent coding style (naming scheme, tab format, brace format, etc) across a project is important, especially when accepting things from outside contributors--typically people disagree on what that style ought to be, but that's beside the point.

Pepper is no exception to this. Pepper uses the Flake8 linter to run pep8, pyflakes and prevent circular dependencies. This, as with testing, is enforced by CI, just as adding tests is--and the lint check is run against the diff, so you won't get yelled at for style problems that someone else introduced. (Though, again, if we start with none and we don't allow any in merges then there shouldn't ever be any.)

Enforcing style like this should prevent unreadable, confusing code down the line, keeping the project's barrier for entry relatively low.

## Documentation

Currently we don't have automated enforcement for documentation coverage, but there do appear to be packages that will allow for enforcement of that. Currently we have documentation for the master branch being built by [ReadTheDocs](http://readthedocs.io/), though GitHub doesn't view ReadTheDocs as a CI server, which is unfortunate. As it stands though, there's a neat little badge on the readme that shows the status of the documentation builder.

Some parts of the documentation are also auto-generated from the docstrings of the source code, making it easy to directly document code and parameters.

Having documentation easily accessible, both for the contributors and for people looking to use the library, is important to keeping the barrier to entry low. This is part of why I maintain this blog alongside the official documentation.

## Next Steps

Now that theres automated enforcement of best practices in place, development can begin in earnest. The project is probably still too immature to attract many outside contributors, but my hope is that with all this infrastructure in place it will be easy for them to join and for the existing team (i.e., me) to trust the contributions they make.