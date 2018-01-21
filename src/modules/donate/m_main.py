import logging
import os
from gettext import gettext as _
from typing import Tuple

import modules.main
from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleInterface
from .main import vars_, Vars

logger = logging.getLogger(__name__)


class Module(ModuleInterface):
    ID = 'donate'

    FILE_NAME = 'aai-donate.txt'

    @property
    def vars_(self) -> Vars:
        return vars_

    @property
    def name(self) -> str:
        return _('Пожалуйста, поддержите разработку')

    @property
    def menu_item(self) -> Tuple[str, str]:
        return self.ID, ColorTxt(self.name).green.bold

    def dialog_textbox(self) -> str:
        file_path = os.path.join(modules.main.vars_.config.db_path, self.FILE_NAME)

        return self.my_dialog.textbox(file_path, title=self.name, exit_label=_('Главное меню'))

    def run(self) -> bool:
        self.dialog_textbox()
        return False
