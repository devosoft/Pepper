# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information


def assert_raises(thing, raise_type, messages, *args, **kwargs):
    exception_raised = False
    try:
        thing(*args, **kwargs)
        assert(False and f"The above should have raised an error of type {type(raise_type)}")
    except raise_type as err:
        exception_raised = True
        for message in messages:
            assert(message in str(err))
    except:  # NOQA
        assert(False and "Emitted exception of wrong type")
    assert(exception_raised)
