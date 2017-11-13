Getting Started with Pepper Development
=======================================

It is highly recommended that you make use of a `virtual environment
<http://docs.python-guide.org/en/latest/dev/virtualenvs/>`__ when you work on developing Pepper.
This will isolate any third-party dependencies from the rest of our system, and will allow you to
install development versions of Pepper without conflicting with a system version.

Installing Pepper
-----------------


 0. Install the system-wide prerequisites, Python 3 and pip. You can follow the directions in the
    `Python Packaging reference <https://packaging.python.org/tutorials/installing-packages/>`__ to make sure everything gets set up right.
 #. Run `pip install -e . dev` in the Pepper repository folder. This will install pepper in editable mode, where the installed package points to
    the work directory containing the source files of the package. This will allow you to make changes to the local source files without having to
    re-install the package to test them. This also installes the 'dev' dependencies, which include things like the test runner, coverage hooks,
    documentation generator and so on.
 #. Run `make test`. This will run the automated tests against the installed package. The tests should all pass.

 You are now ready to contribute to Pepper development!


Choosing an issue
-----------------

Pepper development is planned and tracked within the `Github repository <https://github.com/devosoft/Pepper>`__. Tasks are maintained within the Issues.
If you're new to working on Pepper it is recommended you start with some issues that are tagged as "low-hanging-fruit", since these don't require as much
initial knowledge of the codebase and should give you a nice entry point to the project.

Once you've selected an issue to work on you should assign yourself to it, or comment that you're taking it so that a project maintainer can assign it to you.
This will prevent duplicated work where someone else begins working on the issue in parallel to you, without your knowlegde.

Once you start working you should immediately create a pull request against the source branch. This will allow easy conversations about any problems you
run into with context. It will also make the CI server auto-test your commits as you work on them,
which should help you catch any issues before they become too big.

When you've finished work you should complete the following checklist (copy-paste it into a comment
within the pull request, then check off boxes as they're compelted)::

    - [ ] Is it mergeable? (pull master into your branch, resolve any conflicts)
    - [ ] Did it pass the tests?
    - [ ] If it introduces new functionality is it tested?
    Check for code coverage with `make diff-cover`
    - [ ] Is it well formatted? Look at `make diff-quality` and `make doc-html` output.
    - [ ] Did it change the command-line interface? Only additions are allowed
    without a major version increment. Changing file formats also requires a
    major version number increment.
    - [ ] Was a spellchecker run on the source code and documentation after
    changes were made?
    - [ ] Is the Copyright year up to date?

Once the checklist is complete you should request a review from a project maintainer. You should @mention them in a comment so they're notified.
The reviewer will then comment on any changes that need to be made to your code, if there are any. If so, you must fix them and then re-request a review.
If the review comes up clean then the reviewer will merge your branch into the project.

