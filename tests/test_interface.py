import sys
sys.path.insert(0, 'src')
import os
import tempfile
from nose.tools import eq_

from dbdb.interface import DBDB
import pytest

class TestDBDB(object):

    def setup(self):
        self.f = tempfile.NamedTemporaryFile(delete=False)
        self.dbdb = DBDB(self.f)
    
    def test_can_close_and_assert_closed(self):
        self.dbdb.close()
        with pytest.raises(ValueError, match='Database closed.'):
            self.dbdb._assert_not_closed()

    def test_can_set_and_get(self):
        self.dbdb["a"] = "1"
        self.dbdb.commit()
        eq_(self.dbdb["a"], "1")
    
    def test_can_delete(self):
        self.dbdb["a"] = "1"
        self.dbdb.commit()
        eq_(self.dbdb["a"], "1")
        del self.dbdb["a"]
        with pytest.raises(KeyError):
            val = self.dbdb["a"]

    def test_can_set_and_contain_returns_true(self):
        self.dbdb["a"] = "1"
        self.dbdb.commit()
        eq_("a" in self.dbdb, True)
        eq_(self.dbdb["a"], "1")
        eq_("b" in self.dbdb, False)

    def test_can_get_correct_length(self):
        self.dbdb["a"] = "1"
        self.dbdb.commit()
        self.dbdb["b"] = "2"
        self.dbdb.commit()
        self.dbdb["c"] = "3"
        self.dbdb.commit()
        eq_(len(self.dbdb), 3)
        
        
