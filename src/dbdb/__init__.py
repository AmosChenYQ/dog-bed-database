import os

from .interface import DBDB

# Defines a list of module names that should be imported when from package import * is encountered

__all__ = ['DBDB', 'connect']

# open() creates new file objects, os.open() creates OS-level file descriptors, and os.fdopen() creates a file object out of a file descriptor.
def connect(dbname):
    try:
        f = open(dbname, 'r+b') # r+ won't create the file
    except IOError: #In case file is not found, create it
        fd = os.open(dbname, os.O_RDWR | os.O_CREAT)
        f = os.fdopen(fd, 'r+b')
    return DBDB(f)
