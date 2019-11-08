from functools import wraps

'''
used to log method call stack
def _log_method(method_func):
    @wraps(method_func)
    def wrapper(*args, **kwargs):
        print('calling', method_func.__name__)
        method_func(*args, **kwargs)
    return wrapper

class MetaLogMethodCalls(type):
    def __new__(cls, cls_name, bases, namespace,**kwargs):
        for name, attr in namespace.items():
            if callable(attr):
                namespace[name] = _log_method(attr)
            elif isinstance(attr, (classmethod, staticmethod)):
                namespace[name] = type(attr)(_log_method(attr.__func__))
        return type.__new__(cls, cls_name, bases, namespace, **kwargs)
'''

class ValueRef(object):
    def prepare_to_store(self, storage):
        pass

    @staticmethod
    def referent_to_string(referent):
        return referent.encode('utf-8')

    @staticmethod
    def string_to_referent(string):
        return string.decode('utf-8')

    def __init__(self, referent=None, address=0):
        self._referent = referent
        self._address = address

    @property
    def address(self):
        return self._address

    # If referent is not set, loads it.
    # Returns the referent
    # String to referent function generates a BinaryNodeRef but only loading the adrs for its children
    def get(self, storage):
        if self._referent is None and self._address:
            self._referent = self.string_to_referent(storage.read(self._address))
        return self._referent

    def store(self, storage):
        # No address -> No physically stored -> store it
        if self._referent is not None and not self._address:
            self.prepare_to_store(storage) # Hook, before store. In BinaryNodeRef will be used to recursive store
            self._address = storage.write(self.referent_to_string(self._referent))


class LogicalBase(object):
    node_ref_class = None       # Will be BinaryNodeRef
    value_ref_class = ValueRef

    def __init__(self, storage):
        self._storage = storage
        print("init")
        self._refresh_tree_ref()
        print(self._tree_ref._referent)
        print(self._tree_ref._address)

    def commit(self):
        self._tree_ref.store(self._storage)
        self._storage.commit_root_address(self._tree_ref.address)

    # Regenerate the tree by recreating the root addr
    def _refresh_tree_ref(self):
        self._tree_ref = self.node_ref_class(
            address=self._storage.get_root_address()) # Reference to the parent node

    # Get the key value
    def get(self, key):
        if not self._storage.locked:
            print("get f")
            self._refresh_tree_ref() # If not locked, update the tree with storage data
            print(self._tree_ref._referent)
            print(self._tree_ref._address)
            print(self._follow(self._tree_ref))
        return self._get(self._follow(self._tree_ref), key) # Do not care about "dirty read"

    # Set a value to a key
    def set(self, key, value):
        if self._storage.lock():
            self._refresh_tree_ref()
        
        self._tree_ref = self._insert(
            self._follow(self._tree_ref), key, self.value_ref_class(value))

    # Delete a key
    def pop(self, key):
        if self._storage.lock():
            self._refresh_tree_ref()
        self._tree_ref = self._delete(
            self._follow(self._tree_ref), key)

    def _follow(self, ref):
        return ref.get(self._storage) # Get the referent

    # Override len() operator
    def __len__(self):
        if not self._storage.locked:
            self._refresh_tree_ref()
        root = self._follow(self._tree_ref)
        if root:
            return root.length
        else:
            return 0
