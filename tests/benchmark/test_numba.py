import time


def test_numba_addition(benchmark):
    def _test():
        time.sleep(1)

    benchmark(_test)


def test_numba_addition_index(benchmark):
    def _test():
        time.sleep(1)

    benchmark(_test)
