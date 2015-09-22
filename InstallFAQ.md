

# How do I install superpy? #

There are a variety of ways:
  1. If you have easy\_install on your system, simply do "easy\_install superpy" (you can get easy\_install by executing http://peak.telecommunity.com/dist/ez_setup.py with python).
> 2. If you don't have easy\_install and don't want to install it, you can install the appropriate python egg from the [downloads](http://code.google.com/p/superpy/downloads/list) section. If you do that, make sure you install the dependencies (currently Pmw).

Of course, you will also need python installed (see the question on Python later in this FAQ to get a pointer to the python download location).

# Do I need to do anything special on windows? #

Make sure you have installed the python windows tools from https://sourceforge.net/projects/pywin32. Once easy\_install supports pywin32, we will setup dependencies so this is not required.

Also, you may want to see the section on setting up superpy as a windows service in [SuperpyDocs#Superpy\_as\_a\_windows\_service](SuperpyDocs#Superpy_as_a_windows_service.md).

# Where do I download Python? #

You can download python from http://www.python.org/download. Superpy has been tested mainly with version 2.5 of python but should work with most other versions as well.