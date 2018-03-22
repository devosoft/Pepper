Making Pepper Releases
======================

The release process is relatively simple--Create a git tag with the
release candidate (e.g. '0.0.4-rc1'), run the integration tests
(once some are in place), run the built-in tests, ensure everything
works as intended. If so, re-tag with the version (e.g. '0.0.4') and
continue to the 'Release to PyPi' section.

Note that the Pepper project uses `semantic versioning <https://semver.org/>`__, which makes use of the MAJOR.MINOR.PATCH numbering system.

The summary from semver.org::

    Given a version number MAJOR.MINOR.PATCH, increment the:

        MAJOR version when you make incompatible API changes,
        MINOR version when you add functionality in a backwards-compatible manner, and
        PATCH version when you make backwards-compatible bug fixes.

Releasing to PyPi
-----------------

The guide I originally followed was written by `Peter Downs <http://peterdowns.com/posts/first-time-with-pypi.html>`__

The pre-requisites are that you have created accounts on both
pypi.python.org and testpypi.python.org, and that those accounts have
admin rights to the package on PyPi.

You should follow the instructions on Peter Downs' site as to creating
a `.pypirc` file, which is used to authenticate into the server.

Once that is done, test that the package uploads::

        python setup.py sdist upload -r pypitest

If it does, upload it to the deployment server:

        python setup.py sdist upload -r pypi

Congratulations! You've released a version of Pepper!
