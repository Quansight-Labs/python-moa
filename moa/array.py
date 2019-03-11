"""Pure python slow array "indexing" class. "psi reduction" will soon
be implemented and this module will be unnecissary.

"""

class Array:
    """This will be changed to a simple namedtuple once psi reduction is
    fully implemented. "row" based format is assumed.
    """
    def __init__(self, shape, value=None, fmt='row'):
        total = 1
        for i in shape:
            total *= i

        if value:
            if total != len(value):
                raise ValueError('number of values must match shape')

            self.value = list(value)
        else:
            self.value = [0] * total

        self.shape = shape
        self.fmt = fmt

    @property
    def dimension(self):
        return len(self.shape)

    def _offset(self, index):
        if len(index) != len(self.shape):
            raise IndexError('index is not a full index')

        stride = 1
        offset = 0
        for i, s in zip(index[::-1], self.shape[::-1]):
            if i >= s:
                raise IndexError(f'index {i} >= {s} is incompatible with shape')

            offset += stride * i
            stride *= s

        return offset

    def __getitem__(self, index):
        return self.value[self._offset(index)]

    def __setitem__(self, index, value):
        self.value[self._offset(index)] = value
