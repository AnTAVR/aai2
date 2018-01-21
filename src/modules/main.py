import logging
import os

from aai_framework.utils import VarsRepr
from libs.utils import is_bios_sys


class Args(VarsRepr):
    new_sys_path: str = '/tmp/aai'
    gdialog: bool = False
    debug: bool = False
    mini: bool = False
    loglevel: str = logging.getLevelName(logging.DEBUG)

    @property
    def _repr__props(self) -> list:
        return ['new_sys_path', 'loglevel', 'mini', 'debug', 'mini', 'loglevel']


class Config(VarsRepr):
    version: str = '0.1'
    bios_sys: bool = is_bios_sys()
    bios_sys_txt: str = 'BIOS' if bios_sys else 'EFI'
    db_path: str = os.path.abspath(os.path.join(os.path.curdir, 'db'))
    prog_name: str = 'Arch AnTAVR Installer 2 ver. {} <<{}>>'.format(version, bios_sys_txt)

    @property
    def _repr__props(self) -> list:
        return ['version', 'bios_sys', 'bios_sys_txt', 'db_path', 'prog_name']


class Vars(VarsRepr):
    config: Config = None
    cmd_arg: Args = None

    def __init__(self):
        self.config = Config()
        self.cmd_arg = Args()

    @property
    def _repr__props(self) -> list:
        return ['config', 'cmd_arg']


vars_ = Vars()
