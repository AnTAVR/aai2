from typing import List

import pytest

from ..utils import VarsRepr


def test_not_abstract_methods_repr__props():
    # noinspection PyUnusedLocal
    with pytest.raises(TypeError, match=r'.*abstract methods _repr__props.*') as excinfo:
        # noinspection PyUnusedLocal
        t = VarsRepr()


def test_no_attribute():
    class TMP(VarsRepr):
        @property
        def _repr__props(self) -> List[str]:
            return ['a', 'b']

    tmp = TMP()
    # noinspection PyUnusedLocal
    with pytest.raises(AttributeError, match=r'.*object has no attribute.*') as excinfo:
        # noinspection PyUnusedLocal
        s = tmp.__repr__()


def test_attribute():
    class TMP(VarsRepr):
        def __init__(self):
            self.a = 1
            self.b = 'b'

        @property
        def _repr__props(self) -> List[str]:
            return ['a', 'b']

    tmp = TMP()
    assert tmp.a == 1
    assert tmp.b == 'b'
    assert tmp.__repr__() == "aai_framework.tests.test_utils.TMP{'a': 1, 'b': 'b'}"
