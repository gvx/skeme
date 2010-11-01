# Skeme #

This is a top-down scheme generator, using PyCairo.

## Dependencies ##

Skeme depends only on Python 2.6(-ish, 2.5 or 2.7 probably won't cause
problems) and PyCairo.

On most Linux systems, you can probably install everything in one go by using
`sudo apt-get install python-cairo` or similar.

## Running ##

Skeme consists of a back-end and various front-ends.

The back-end (`libskeme.py`) is usable as a library or in the Python
interactive interpreter.

Currently, there are two front-ends:

### sk ###

A command-line program, a filter to be exact. Supply the input file on stdin,
and get a PNG on stdout. It is very configurable with command line arguments
and the `sk.layout` file.

### webskeme ###

Not yet ready. webskeme is a cgi script together with an HTML form. Almost as
configurable as sk.