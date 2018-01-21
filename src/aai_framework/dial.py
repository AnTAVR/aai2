import subprocess
from typing import List, Union, Tuple

from dialog import Dialog


class ColorTxt(str):
    MOD: str = '\Z'
    RESTORE_STRING: str = '{}' + MOD + 'n'
    COLOR_STRING: str = MOD + '{}' + RESTORE_STRING
    MOD_STRING: str = MOD + '{}{}' + MOD + '{}'
    status: list = None

    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.status = []

    def new(self, mod: str):
        ret = self.__class__(mod)
        ret.status = self.status
        return ret

    def _color(self, mod: str):
        self.status.append(mod)
        return self.new(self.COLOR_STRING.format(mod, self))

    def _mod(self, mod: str):
        self.status.append(mod)
        return self.new(self.MOD_STRING.format(mod, self, mod.upper()))

    @property
    def restore(self):
        self.status.append('restore')
        return self.__class__(self.RESTORE_STRING.format(self))

    @property
    def black(self):
        return self._color('0')

    @property
    def red(self):
        return self._color('1')

    @property
    def green(self):
        return self._color('2')

    @property
    def yellow(self):
        return self._color('3')

    @property
    def blue(self):
        return self._color('4')

    @property
    def magenta(self):
        return self._color('5')

    @property
    def cyan(self):
        return self._color('6')

    @property
    def white(self):
        return self._color('7')

    @property
    def bold(self):
        return self._mod('b')

    @property
    def reverse(self):
        return self._mod('r')

    @property
    def underline(self):
        return self._mod('u')


class MyDialog(Dialog):
    ESC_CANCEL = (Dialog.ESC, Dialog.CANCEL)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #    self.add_persistent_args(('--clear', '--colors'))
        self.add_persistent_args(('--colors',))
        self.autowidgetsize = True

    def _quote_arg_for_file_opt(self, argument: str) -> str:
        tmp = ['"']

        for c in argument:
            if c in ('"',):
                tmp.append("\\" + c)
            else:
                tmp.append(c)

        return ''.join(tmp + ['"'])

    def progressbox_cmd(self, cmd: Union[str, List[str]], text: str = None,
                        height: int = 20, width: int = 78, **kwargs) -> Tuple[str, subprocess.Popen]:
        p = subprocess.Popen(cmd, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t = self.progressbox(fd=p.stdout.fileno(), text=text, height=height, width=width, **kwargs)
        p.wait()
        return t, p
