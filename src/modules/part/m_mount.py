import logging
from gettext import gettext as _
from typing import Tuple

import modules.main
from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleInterface, ModuleCollection
from .l_mount import ModulePartMountBase
from .m_mount_boot import Module as ModulePartMountBoot
from .m_mount_efi import Module as ModulePartMountEfi
from .m_mount_home import Module as ModulePartMountHome
from .m_mount_root import Module as ModulePartMountRoot
from .m_mount_swap import Module as ModulePartMountSwap
from .m_mount_swapfile import Module as ModulePartMountSwapFile
from .main import vars_, Vars

logger = logging.getLogger(__name__)


class Module(ModuleInterface):
    ID = 'part_mount'

    UNMOUNT_ITEM_ID = 'unmount'

    @property
    def vars_(self) -> Vars:
        return vars_

    @property
    def name(self) -> str:
        return _('Монтирование разделов')

    @property
    def menu_item(self) -> Tuple[str, str]:
        text = [ColorTxt('(' + _('ВЫПОЛНЕНО') + ')').green.bold if self.is_run else
                ColorTxt('(' + _('ОБЯЗАТЕЛЬНО!!!') + ')').red.bold if not self.conflicts.txt else '']

        return super().get_menu_item(text)

    @property
    def is_run(self) -> bool:
        return vars_.is_ok

    def dialog_menu(self, modules_: ModuleCollection, default: str) -> Tuple[str, str]:
        items = [(self.UNMOUNT_ITEM_ID, _('Размонтировать'))] + modules_.menu_items

        help_txt = [_('Выберите точку монтирования')]

        return self._dialog_menu(items, default, help_txt)

    @ModuleInterface.decor_can_not_perform
    def run(self) -> bool:
        save_menu = ''

        modules_ = ModuleCollection()

        root = ModulePartMountRoot()
        boot = ModulePartMountBoot()
        boot.depends.add(root)
        home = ModulePartMountHome()
        home.depends.add(root)
        swap = ModulePartMountSwap()
        swapfile = ModulePartMountSwapFile()
        swapfile.depends.add(root)
        swap.conflicts.add(swapfile)
        swapfile.conflicts.add(swap)

        modules_.add(root, boot)

        if not modules.main.vars_.config.bios_sys:
            efi = ModulePartMountEfi()
            efi.depends.add(root)
            boot.conflicts.add(efi)
            modules_.add(efi)
        modules_.add(home, swap, swapfile)

        while True:
            code, value = self.dialog_menu(modules_, save_menu)
            if code == self.my_dialog.OK:
                save_menu = value
                if save_menu == self.UNMOUNT_ITEM_ID:
                    vars_.umount()
                    continue
                _module: ModulePartMountBase = modules_[save_menu]
                if _module.run():
                    # @todo: дописать поведение
                    pass
            else:
                break

        return False
