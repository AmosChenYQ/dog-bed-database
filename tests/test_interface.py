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
    
    