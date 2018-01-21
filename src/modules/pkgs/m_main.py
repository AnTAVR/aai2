import logging
from gettext import gettext as _
from typing import Tuple

from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleInterface
from .main import vars_, Vars

logger = logging.getLogger(__name__)


class Module(ModuleInterface):
    ID = 'pkgs'
    LEN_INSTALL = 2665

    @property
    def vars_(self) -> Vars:
        return vars_

    @property
    def name(self) -> str:
        return _('Дополнительное ПО')

    @property
    def menu_item(self) -> Tuple[str, str]:
        text = [ColorTxt('(' + _('ВЫПОЛНЕНО') + ')').green.bold if self.is_run else '']

        return super().get_menu_item(text)
