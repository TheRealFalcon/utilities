# Created by Oren Tirosh on Thu, 2 Aug 2012
# Taken from http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
def memoize(func):
    ''' Memoization decorator for function taking a single argument. '''
    class memoize(dict):
        def __missing__(self, key):
            ret = self[key] = func(key)
            return ret
    return memoize().__getitem__

# Created by Oren Tirosh on Thu, 2 Aug 2012
# Taken from http://code.activestate.com/recipes/578233-immutable-class-decorator/
def immutable(mutableclass):
    ''' Apply decorator to class with __slots__, and members
    will be made mutable during execution of __init__
    but read-only afterwards. '''
    
    if not isinstance(type(mutableclass), type):
        raise TypeError('@immutable: must be applied to a new-style class')
    if not hasattr(mutableclass, '__slots__'):
        raise TypeError('@immutable: class must have __slots__')

    class immutableclass(mutableclass):
        __slots__ = ()                      # No __dict__, please   

        def __new__(cls, *args, **kw):
            new = mutableclass(*args, **kw) # __init__ gets called while still mutable
            new.__class__ = immutableclass  # locked for writing now
            return new 

        def __init__(self, *args, **kw):    # Prevent re-init after __new__
            pass

    # Copy class identity:
    immutableclass.__name__ = mutableclass.__name__
    immutableclass.__module__ = mutableclass.__module__

    # Make read-only:
    for name, member in mutableclass.__dict__.items():
        if hasattr(member, '__set__'):
            setattr(immutableclass, name, property(member.__get__))

    return immutableclass
