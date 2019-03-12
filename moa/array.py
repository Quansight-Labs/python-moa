"""Pure python slow array "indexing" class. It is intentional that
numpy is not used. This is an class that will try to implement the
universal array interface with MOA in mind. Psi reduction will soon be
implemented and I will be able to reduce the expectations of this
class (specifically the psi method taking a tuple). All the dunder
madness occurs from trying to treat scalar operations appropriately.

Eventually this will turn into a lazy array moa interface. MOA needs
to stabilize and more work before that happens.

"""

class Array:
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

        self._shape = shape

        if fmt != 'row':
            raise NotImplementedError('only "row" based format implmented')
        self.fmt = fmt

    @property
    def shape(self):
        return self._shape

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

    def __repr__(self):
        return f'Array(shape={self.shape}, value={self.value})'

    # scalar operations
    def __add__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return self[()] + other

    def __radd__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return other + self[()]

    def __sub__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return self[()] - other

    def __rsub__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return other - self[()]

    def __mul__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return self[()] * other

    def __rmul__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return other * self[()]

    def __truediv__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return self[()] / other

    def __rtruediv__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return other / self[()]

    # scalar comparison
    def __lt__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return self[()] < other

    def __le__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return self[()] <= other

    def __gt__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return self[()] > other

    def __ge__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return self[()] >= other

    def __eq__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return self[()] == other

    def __ne__(self, other):
        if len(self.shape) != 0:
            raise TypeError('only scalar operations allowed')
        return self[()] != other
