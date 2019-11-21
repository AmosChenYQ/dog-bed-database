import sys
sys.path.insert(0, 'src')
import os
import tempfile
import portalocker
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
        self.f = tempfile.NamedTemporaryFile(delete=False)
        self.storage = Storage(self.f)
        self.tree = BinaryTree(self.storage)
        
    def teardown(self):
        pass

    def test_get_missing_key_raises_key_error(self):
        with assert_raises(KeyError):
            self.tree.get('Not A Key In The Tree')
    
    def test_set_and_get_key(self):
        self.tree.set('b', '1')
        self.tree.set('a', '2')
        self.tree.set('c', '3')
        self.tree.commit()
        
        eq_(self.tree.get('a'), '2')
        eq_(self.tree.get('b'), '1')
        eq_(self.tree.get('c'), '3')

    def test_set_and_reset_key(self):
        self.tree.set('a', '1')
        eq_(self.tree.get('a'), '1')

        self.tree.set('a', '2')
        eq_(self.tree.get('a'), '2')

    def test_delete_a_non_key(self):
        with assert_raises(KeyError):
            self.tree.pop('a')

    def test_set_and_delete_key(self):
        self.tree.set('a', '1')
        self.tree.set('b', '2')
        self.tree.set('c', '3')
        self.tree.commit()

        eq_(self.tree.get('a'), '1')
        eq_(self.tree.get('b'), '2')
        eq_(self.tree.get('c'), '3')

        self.tree.pop('a')
        eq_(self.tree.get('b'), '2')
        eq_(self.tree.get('c'), '3')
        with assert_raises(KeyError):
            self.tree.get('a')

    def test_set_and_delete_left_node(self):
        self.tree.set('b', '2')
        self.tree.set('a', '1')
        self.tree.set('c', '3')
        self.tree.commit()

        eq_(self.tree.get('a'), '1')
        eq_(self.tree.get('b'), '2')
        eq_(self.tree.get('c'), '3')

        self.tree.pop('a')
        eq_(self.tree.get('b'), '2')
        eq_(self.tree.get('c'), '3')
        with assert_raises(KeyError):
            self.tree.get('a')

    def test_set_and_delete_right_node(self):
        self.tree.set('b', '2')
        self.tree.set('a', '1')
        self.tree.set('c', '3')
        self.tree.commit()

        eq_(self.tree.get('a'), '1')
        eq_(self.tree.get('b'), '2')
        eq_(self.tree.get('c'), '3')

        self.tree.pop('c')
        eq_(self.tree.get('a'), '1')
        eq_(self.tree.get('b'), '2')
        with assert_raises(KeyError):
            self.tree.get('c')

    def test_set_and_delete_root_node(self):
        self.tree.set('b', '2')
        self.tree.set('a', '1')
        self.tree.set('c', '3')
        self.tree.commit()

        eq_(self.tree.get('a'), '1')
        eq_(self.tree.get('b'), '2')
        eq_(self.tree.get('c'), '3')

        self.tree.pop('b')
        eq_(self.tree.get('a'), '1')
        eq_(self.tree.get('c'), '3')
        with assert_raises(KeyError):
            self.tree.get('b')
    
    def test_set_and_delete_root_node_without_its_left_node(self):
        self.tree.set('b', '2')
        self.tree.set('c', '3')
        self.tree.commit()

        eq_(self.tree.get('b'), '2')
        eq_(self.tree.get('c'), '3')

        self.tree.pop('b')
        eq_(self.tree.get('c'), '3')
        with assert_raises(KeyError):
            self.tree.get('b')

    def test_set_and_delete_root_node_without_its_right_node(self):
        self.tree.set('b', '2')
        self.tree.set('a', '1')
        self.tree.commit()

        eq_(self.tree.get('b'), '2')
        eq_(self.tree.get('a'), '1')

        self.tree.pop('b')
        eq_(self.tree.get('a'), '1')
        with assert_raises(KeyError):
            self.tree.get('b')


    # def test_uni(self):
    #     if self.tree._storage.lock():
    #         self.tree._refresh_tree_ref()
        
    #     self.tree._tree_ref = self.tree._insert(
    #         self.tree._follow(self.tree._tree_ref), 'a', self.tree.value_ref_class('1'))