from typing import Union, Tuple


class SizeConvert:
    SUFFIXES = 'KMGTPEZY'
    BIN_BASE = 10 ** 3
    BIN = 'B'
    I_BIN_BASE = 2 ** 10
    I_BIN = 'iB'
    _binary: str
    _base: int

    def __init__(self, binary: bool = True):
        self.set_binary(binary)

    def set_binary(self, binary: bool):
        if binary:
            self._binary = self.I_BIN
            self._base = self.I_BIN_BASE
        else:
            # noinspection PyAttributeOutsideInit
            self._binary = self.BIN
            # noinspection PyAttributeOutsideInit
            self._base = self.BIN_BASE

    def natural_size(self, value: Union[int, float]) -> Tuple[float, str]:
        value = float(value)

        if value < self._base:
            return value, self.BIN

        for i, suffix in enumerate(self.SUFFIXES):  # type: int, str
            unit = self._base ** (i + 2)
            ret = self._base * value / unit
            if value < unit:
                return ret, suffix + self._binary
        # noinspection PyUnboundLocalVariable
        return ret, suffix + self._binary

    def size_to(self, value: Union[int, float], suffix: str = None) -> Tuple[float, str]:
        value = float(value)
        suffix = str(suffix).upper()

        if suffix not in self.SUFFIXES:
            return value, self.BIN

        unit = self._base ** (self.SUFFIXES.index(suffix) + 1)
        value = value / unit

        return value, suffix + self._binary
