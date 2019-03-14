import pytest

import time


@pytest.mark.benchmark
def test_numba_addition(benchmark):
    def _test():
        time.sleep(1)

    benchmark(_test)


@pytest.mark.benchmark
def test_numba_addition_index(benchmark):
    def _test():
        time.sleep(1)

    benchmark(_test)
