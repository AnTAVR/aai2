import logging
from typing import List

from aai_framework.utils import VarsRepr

logger = logging.getLogger(__name__)


class Options(VarsRepr):
    mirrorlist: List[str] = None
    country: str = None
    timezone: str = None
    localtime: str = None
    locale: str = None
    keymap: str = None
    keymap_toggle: str = None
    font: str = None
    font_map: str = None
    font_unimap: str = None
    hostname: str = None

    @property
    def _repr__props(self) -> list:
        return ['mirrorlist', 'country', 'timezone', 'localtime', 'locale',
                'keymap', 'keymap_toggle',
                'font', 'font_map', 'font_unimap', 'hostname']


class Vars(VarsRepr):
    opti_: Options = None

    @property
    def is_ok(self) -> bool:
        return False

    @property
    def _repr__props(self) -> list:
        return ['opti_', 'is_ok']


vars_ = Vars()
