import sys
sys.path.insert(0, 'src')
import os
import tempfile
from nose.tools import eq_

from dbdb.physical import Storage
import pytest

class TestStorage(object):

    def setup(self):
        self.f = tempfile.NamedTemporaryFile(delete=False)
        self.p = Storage(self.f)

    def teardown(self):
        for key, value in self.__dict__.items():
            if isinstance(value, type(tempfile.NamedTemporaryFile(delete=False))):
                value.close()               

    def _get_fd_contents(self, fd):
        fd.seek(0, os.SEEK_END)
        fd.flush()
        fd.seek(0)
        return fd.read()

    def _get_superblock_and_data(self, value):
        superblock = value[:Storage.SUPERBLOCK_SIZE]
        data = value[Storage.SUPERBLOCK_SIZE:]
        return superblock, data

    def test_init_ensures_superblock(self):
        EMPTY_SUPERBLOCK = (b'\x00' * Storage.SUPERBLOCK_SIZE)
        value = self._get_fd_contents(self.f)
        eq_(value, EMPTY_SUPERBLOCK)

    def test_can_get_f_contents(self):
        self.ff = tempfile.NamedTemporaryFile(delete=False)
        self.ff.write(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF")
        self.ff.flush()
        self.ff.seek(0)
        self.pp = Storage(self.ff)
        self.pp.write(b"ABCDE")
        value = self.pp._get_all_contents()
        eq_(value, (b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + b'\x00' * (Storage.SUPERBLOCK_SIZE - 8))
                    + b"\x00\x00\x00\x00\x00\x00\x00\x05ABCDE")

    def test_dirty_file_can_init_ensures_superblock(self):
        self.ff = tempfile.NamedTemporaryFile(delete=False)
        self.ff.write(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF")
        self.ff.flush()
        self.ff.seek(0)
        self.pp = Storage(self.ff)
        self.pp.write(b"ABCDE")
        value = self._get_fd_contents(self.ff)
        superblock, data = self._get_superblock_and_data(value)
        DIRTY_SUPERBLOCK = (b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' 
                    + b'\x00' * (Storage.SUPERBLOCK_SIZE - 8))
        eq_(superblock, DIRTY_SUPERBLOCK)
        eq_(data, b"\x00\x00\x00\x00\x00\x00\x00\x05ABCDE")

    def test_can_skip_fill_superblock(self):
        DIRTY_SUPERBLOCK = (b'\xFF' * (Storage.SUPERBLOCK_SIZE))
        self.ff = tempfile.NamedTemporaryFile(delete=False)
        self.ff.write(DIRTY_SUPERBLOCK)
        self.ff.flush()
        self.ff.seek(0)
        self.pp = Storage(self.ff)
        self.pp.write(b"ABCDE")
        value = self._get_fd_contents(self.ff)
        superblock, data = self._get_superblock_and_data(value)
        eq_(superblock, DIRTY_SUPERBLOCK)
        eq_(data, b"\x00\x00\x00\x00\x00\x00\x00\x05ABCDE")

    def test_write(self):
        self.p.write(b"ABCDE")
        value = self._get_fd_contents(self.f)
        superblock, data = self._get_superblock_and_data(value)
        EMPTY_SUPERBLOCK = (b'\x00' * Storage.SUPERBLOCK_SIZE)
        eq_(superblock, EMPTY_SUPERBLOCK)
        eq_(data, b"\x00\x00\x00\x00\x00\x00\x00\x05ABCDE")

    def test_read(self):
        test_of_address = self.p.write(b"TEST")
        data_at_test_of_address = self.p.read(test_of_address)
        eq_(data_at_test_of_address, b"TEST")

    def test_commit_root_address(self):
        self.p.commit_root_address(257)
        root_bytes = self._get_fd_contents(self.f)[:8]
        eq_(root_bytes, b"\x00\x00\x00\x00\x00\x00\x01\x01")

    def test_get_root_address(self):
        self.p.commit_root_address(257)
        root_address = self.p.get_root_address()
        eq_(root_address, 257)

    def test_close_after_open(self):
        self.p.close()
        eq_(True, self.p.closed)

    def test_workflow(self):
        a1 = self.p.write(b"one")
        a2 = self.p.write(b"two")
        self.p.commit_root_address(a2)
        a3 = self.p.write(b"three")
        eq_(self.p.get_root_address(), a2)
        a4 = self.p.write(b"four")
        self.p.commit_root_address(a4)
        eq_(self.p.read(a1), b"one")
        eq_(self.p.read(a2), b"two")
        eq_(self.p.read(a3), b"three")
        eq_(self.p.read(a4), b"four")
        eq_(self.p.get_root_address(), a4)

