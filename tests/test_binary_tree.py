import sys
sys.path.insert(0, 'src')
import os
import tempfile
from nose.tools import eq_, assert_raises
from dbdb.binary_tree import BinaryNode, BinaryNodeRef, BinaryTree
from dbdb.physical import Storage
import pytest

class MockStorage(object):
    def __init__(self):
        self.d = [0]
        self.locked = False

    def lock(self):
        if not self.locked:
            self.locked = True
            return True
        else:
            return False

    def unlock(self):
        pass

    def get_root_address(self):
        return 0

    def write(self, string):
        address = len(self.d)
        self.d.append(string)
        return address

    def read(self, address):
        return self.d[address]

class TestBinaryTree(object):
    def setup(self):
        self.fd = os.open("dbname.txt", os.O_RDWR | os.O_CREAT)
        self.f = open("dbname.txt", 'r+b')
        # self.f = tempfile.NamedTemporaryFile(delete=False)
        self.storage = Storage(self.f)
        self.tree = BinaryTree(self.storage)

    def teardown(self):
        pass

    def test_get_missing_key_raises_key_error(self):
        with assert_raises(KeyError):
            self.tree.get('Not A Key In The Tree')
    
    def test_set_and_get_key(self):
        self.tree.set('a', 'b')
        self.tree.set('c', 'd')
        
        eq_(self.tree.get('a'), 'b')
        eq_(self.tree.get('c'), 'd')
