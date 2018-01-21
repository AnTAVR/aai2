import logging
from gettext import gettext as _
from math import ceil
from typing import Tuple, List

from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleInterface, DialogTestInterface
from libs.part import size_convert
from vendor.partinfo.all import Device
from .l_main import default_size_swap, SWAP_FS_TYPES
from .m_mount_root import Module as ModulePartMountRoot
from .main import Options, vars_, Vars, POINT_SWAP_FILE_ID

logger = logging.getLogger(__name__)


class Module(ModuleInterface, DialogTestInterface):
    ID = POINT_SWAP_FILE_ID

    opti_: Options

    mem_size: Tuple[int, int, str] = None

    MIN_ROOT_SIZE = 6000

    @property
    def vars_(self) -> Vars:
        return vars_

    @property
    def is_run(self) -> bool:
        return vars_.swap_file.is_mount

    def __init__(self):
        super().__init__()
        self.opti_ = Options(self.ID)
        self.conflicts.add(self)
        self.mem_size = default_size_swap()

    @property
    def name(self) -> str:
        return _('Файл подкачки')

    @property
    def menu_item(self) -> Tuple[str, str]:
        text = [self.opti_.swap_size,
                ColorTxt('(' + _('ВЫПОЛНЕНО') + ')').green.bold if self.is_run else '']

        return super().get_menu_item(text)

    def _head_txt(self, help_txt_new: List[str] = None, all_: bool = False) -> List[str]:
        tmp = [
            (_('точка монтирования ({}): {}'), 'mountpoint', self.ID, all_),
            (_('файл подкачки ({}): {}'), 'swap_file', self.opti_.partition, False),
            (_('размер файла подкачки ({}): {}'), 'swap_size', self.opti_.swap_size, False),
            (_('единица измерения ({}): {}'), 'unit', self.mem_size[2], False),
            (_('опции ({}): {}'), 'options', self.opti_.options, all_),
        ]
        help_txt = self.format_head_txt(tmp)

        if help_txt_new is not None:
            help_txt = help_txt_new + help_txt

        return help_txt

    @property
    def max_size(self) -> int:
        _module: ModulePartMountRoot = self.depends[ModulePartMountRoot.ID]
        partition = Device(_module.opti_.partition)

        size = size_convert.size_to(partition.id_part_entry_size, self.mem_size[2][0])[0]
        # @todo: доделать вычитание из общего размера раздела предполагаемый размер установленных пакетов
        return int(ceil(round(size, 1)))

    def test_size(self, val: str) -> bool:
        try:
            size = int(val)
        except ValueError:
            pass
        else:
            if size <= self.max_size:
                return True

        text_err: str = _('Не правильный размер ({})').format(val)

        self._dialog_err(text_err)
        return False

    def dialog_size(self) -> Tuple[str, str]:
        default = ''

        help_txt = self._head_txt()
        help_txt += ['', _('Введите размер swap файла в {}').format(self.mem_size[2]),
                     _('максимально возможный размер: {}').format(self.max_size),
                     _('рекомендуемый размер: {}-{} {}').format(*self.mem_size),
                     ]

        while True:
            code, value = self._dialog_inputbox(default, help_txt)  # type: str str
            if code in self.my_dialog.ESC_CANCEL:
                return code, value
            if self.test_size(value):
                return code, value
            default = value

    @property
    def is_root_ext(self) -> bool:
        _module: ModulePartMountRoot = self.depends[ModulePartMountRoot.ID]
        partition = Device(_module.opti_.partition)
        return partition.id_fs_type in SWAP_FS_TYPES

    def dialog_options(self) -> Tuple[str, str]:
        default = 'defaults'

        help_txt = self._head_txt()
        help_txt += ['', _('Введите дополнительные опции монтирования'), _('по умолчанию: {}').format(default)]

        return self._dialog_inputbox(default, help_txt)

    @ModuleInterface.decor_can_not_perform
    def run(self) -> bool:
        # if not self.is_root_ext:
        #     self.dialog_can_not_perform([_('Root раздел должен быть в {}').format('|'.join(SWAP_FS_TYPES))])
        #     return False

        code, value = self.dialog_size()
        if code in self.my_dialog.ESC_CANCEL:
            return False
        self.opti_.swap_size = value or self.opti_.__class__.swap_size

        code, value = self.dialog_options()
        if code in self.my_dialog.ESC_CANCEL:
            return False
        self.opti_.options = value or self.opti_.__class__.options

        code = self.dialog_test()
        if code == self.my_dialog.OK:
            vars_.swap_file = self.opti_
            vars_.swap_file.mount()
            return True
