from .binary_tree import BinaryTree
from .physical import Storage


# Kind of wrapper for logical and physical layers
# The class which the user will interact with
class DBDB(object):

    def __init__(self, f):
        self._storage = Storage(f) # Reference to storage so it can enforce preconditions
        self._tree = BinaryTree(self._storage)

    def _assert_not_closed(self):
        if self._storage.closed:
            raise ValueError('Database closed.')

    def close(self):
        self._storage.close()

    def commit(self):
        self._assert_not_closed()
        self._tree.commit()

    # Implements dict functions
    def __getitem__(self, key):         # operator [<key>]
        self._assert_not_closed()
        return self._tree.get(key)

    def __setitem__(self, key, value):  # operator [<new_key>] = <value>
        self._assert_not_closed()
        return self._tree.set(key, value)

    def __delitem__(self, key):         # operator del dict[<key>]
        self._assert_not_closed()
        return self._tree.pop(key)

    def __contains__(self, key):        # operator <key> in dict
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __len__(self):                  # operator len(dbdb)
        return len(self._tree)
