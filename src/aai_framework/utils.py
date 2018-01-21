from abc import ABCMeta, abstractmethod
from pprint import pformat
from typing import List


class VarsRepr(metaclass=ABCMeta):
    INDENT = 4
    __indent = [0]

    @property
    @abstractmethod
    def _repr__props(self) -> List[str]:
        return []

    def __repr__(self):
        ret = {prop: self.__getattribute__(prop) for prop in self._repr__props}
        self.__indent[0] += self.INDENT
        ret = '{}{}'.format(self.__class__.__module__ + '.' + self.__class__.__name__,
                            pformat(ret, indent=self.__indent[0]))
        self.__indent[0] -= self.INDENT
        return ret
