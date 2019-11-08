import sys
sys.path.insert(0, 'src')
import os
import tempfile
import mock
from nose.tools import eq_
import pytest

from dbdb.logical import ValueRef, LogicalBase
from dbdb.physical import Storage

class TestValueRef(object):
    
    def setup(self):
        self.value_ref = ValueRef()

    def teardown(self):
        pass

    def test_get_with_actual_Storage(self):
        fd = tempfile.NamedTemporaryFile(delete=False)
        p = Storage(fd)
        test_ref_address = p.write(b"12345")
        self.value_ref._address = test_ref_address
        referent = self.value_ref.get(p)
        p.close()
        eq_(referent, "12345")
        
    def test_get_with_mock_Storage(self):
        p = mock.Mock()
        p.read.return_value = b"12345"
        self.value_ref._address = 4096
        test_referent = self.value_ref.get(p)
        eq_(test_referent, "12345")

    def test_store_with_actual_Storage(self):
        fd = tempfile.NamedTemporaryFile(delete=False)
        p = Storage(fd)
        self.value_ref._referent = "ABCDE"
        self.value_ref.store(p)
        p.close()
        eq_(self.value_ref._address, 4096)

    def test_store_with_mock_Storage(self):
        p = mock.Mock()
        p.write.return_value = 2333
        self.value_ref._referent = "ABCDE"
        self.value_ref.store(p)
        eq_(self.value_ref._address, 2333)

    def test_can_get_property_address(self):
        test_value_ref = ValueRef()
        test_value_ref._referent = "12345"
        test_value_ref._address = 4096
        test_value_ref_address = test_value_ref.address
        eq_(test_value_ref_address, 4096)
    
    def test_can_skip_in_store(self):
        test_value_ref = ValueRef()
        p = mock.Mock()
        test_value_ref.store(p)
        eq_(test_value_ref._address, 0)

    