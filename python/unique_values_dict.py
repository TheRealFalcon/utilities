from collections.abc import Sequence, Mapping
from weakref import WeakKeyDictionary


class UniqueValuesDict(dict):
    """
    Dict that ensures values are unique *between instances*. Duplicate values are fine within the same instance
    Example:
        x = UniqueValuesDict({'a': 1, 'b': 2, 'c': 1})  # Works fine!
        y = UniqueValuesDict({'d': 1})  # Raises ValueError
    """
    all_values_by_instance = WeakKeyDictionary()
    duplicate_error_message = "The same value cannot be used across multiple instances"

    def __init__(self, other=None, **kwargs):
        super(UniqueValuesDict, self).__init__()
        self.__class__.all_values_by_instance[self] = set()
        self.update(other, **kwargs)

    def update(self, other=None, **kwargs):
        removed_value = None
        if other:
            is_mapping = isinstance(other, Mapping)
            if not (is_mapping or isinstance(other, Sequence)):
                raise ValueError("Argument must be mapping or sequence instance")
            if is_mapping:
                other = other.items()
            for key, value in other:
                removed_value = self._remove_overwrite(key)
                self._check_duplicate(value)
        for key, value in kwargs.items():
            removed_value = self._remove_overwrite(key)
            self._check_duplicate(value)

        try:
            if other:
                super(UniqueValuesDict, self).update(other, **kwargs)
            else:
                super(UniqueValuesDict, self).update(**kwargs)
        except Exception as e:
            self._add_to_class_values([removed_value])
            raise e
        self._add_to_class_values(self.values())

    def __setitem__(self, key, value):
        self._check_duplicate(value)
        self.update(((key, value),))

    def __delitem__(self, key):
        value = self[key]
        super(UniqueValuesDict, self).__delitem__(key)
        self._remove_value_from_class_values(value)

    def pop(self, *args):
        value = super(UniqueValuesDict, self).pop(*args)
        value_is_default = len(args) == 2 and args[1] == value
        try:
            self._remove_value_from_class_values(value)
        except KeyError as e:
            if not value_is_default:
                raise e
        return value

    def popitem(self):
        results = super(UniqueValuesDict, self).popitem()
        value = results[1]
        self._remove_value_from_class_values(value)
        return results

    def setdefault(self, *args):
        update_after_super = False
        if len(args) == 2:
            if args[0] not in self:
                self._check_duplicate(args[1])
                update_after_super = True
        result = super(UniqueValuesDict, self).setdefault(*args)
        if update_after_super:
            self._add_to_class_values([args[1]])
        return result

    def copy(self):
        raise Exception("copy not supported for instances of UniqueValuesDict.")

    def __hash__(self):
        # Mutable structures usually aren't hashable so you don't do silly things like
        # {{}: 1}. But since we're stuffing instances into our class level
        # dictionary, we need a hash to index it with.
        return id(self)

    def _check_duplicate(self, value):
        for instance, profiles in self.__class__.all_values_by_instance.items():
            if instance != self:
                if value in profiles:
                    raise ValueError(self.duplicate_error_message)

    def _remove_overwrite(self, key):
        if key in self:
            old_value = self[key]
            if old_value in self.__class__.all_values_by_instance[self]:
                self.__class__.all_values_by_instance[self].remove(old_value)
                return old_value
        return None
                
    def _remove_value_from_class_values(self, value):
        self.__class__.all_values_by_instance[self].remove(value)

    def _add_to_class_values(self, values):
        for value in values:
            self.__class__.all_values_by_instance[self].add(value)

