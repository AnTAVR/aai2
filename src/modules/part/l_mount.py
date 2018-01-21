import logging
from abc import abstractmethod
from gettext import gettext as _
from typing import List, Generator, Tuple

from aai_framework.interface import ModuleInterface, DialogTestInterface
from vendor.partinfo.all import Device
from .l_main import format_items, NONE_ITEM_ID
from .m_format import Module as ModulePartFormat
from .main import Options, Vars, vars_

logger = logging.getLogger(__name__)


# noinspection PyAbstractClass
class ModulePartMountBase(ModuleInterface, DialogTestInterface):
    opti_: Options = None

    NO_PART = ('0x00',
               '0x0',
               '00000000-0000-0000-0000-000000000000',
               '0x05',
               '0x5',
               '21686148-6449-6e6f-744e-656564454649',
               '024dee41-33e7-11d3-9d69-0008c781f39f',
               '0xee')
    NO_PART = tuple(x.lower() for x in NO_PART)

    @property
    def vars_(self) -> Vars:
        return vars_

    @property
    @abstractmethod
    def is_run(self) -> bool:
        return False

    def _head_txt(self, help_txt_new: List[str] = None, all_: bool = False) -> List[str]:
        id_fs_type = None
        if self.opti_.partition is not None:
            partition = Device(self.opti_.partition)
            id_fs_type = partition.id_fs_type

        tmp = [
            (_('точка монтирования ({}): {}'), 'mountpoint', self.ID, all_),
            (_('раздел ({}): {}'), 'partition', self.opti_.partition, all_),
            (_('файловая система ({}): {}'), 'fs', id_fs_type, False),
            (_('опции ({}): {}'), 'options', self.opti_.options, all_),
        ]
        help_txt = self.format_head_txt(tmp)

        if help_txt_new is not None:
            help_txt = help_txt_new + help_txt

        return help_txt

    def _get_parts(self) -> Generator[Device, None, None]:
        for dev in Device.get_devices():  # type: Device
            if not dev.mountpoint and dev.parttype not in self.NO_PART and dev.can_be_formatted and not dev.swap:
                yield dev

    def dialog_format_ok(self) -> str:
        partition = Device(self.opti_.partition)
        id_fs_type = partition.id_fs_type

        if id_fs_type is None:
            return self.my_dialog.OK

        help_txt = self._head_txt()
        help_txt += [_('Раздел {} уже отформатирован в {}').format(self.opti_.partition, id_fs_type),
                     _('Отформатировать еще раз?')]
        help_txt = '\n'.join(help_txt)

        return self.my_dialog.yesno(help_txt, title=self.name,
                                    defaultno=True)

    def test_format(self) -> bool:
        partition = Device(self.opti_.partition)
        id_fs_type = partition.id_fs_type

        if id_fs_type is not None:
            return True

        text_err: str = _('Раздел {} не отформатирован!!!').format(self.opti_.partition)

        self._dialog_err(text_err)
        return False

    def run_format(self) -> bool:
        format_dev = ModulePartFormat(self.opti_.mount_point, self.opti_.partition)

        while True:
            code = self.dialog_format_ok()
            if code in self.my_dialog.ESC:
                return False
            elif code == self.my_dialog.CANCEL:
                return True

            if not format_dev.run(False):
                return False

            if self.test_format():
                return True

    def dialog_part(self) -> Tuple[str, str]:
        items = format_items(self._get_parts())

        help_txt = self._head_txt()
        help_txt += ['', _('Символом * помечены загрузочные разделы'),
                     '', _('Выберите раздел для монтирования')]

        return self._dialog_menu(items, help_txt=help_txt)

    def dialog_options(self) -> Tuple[str, str]:
        default = 'defaults'

        if self.ID != ModulePartMountSwap.ID:
            default += ',lazytime'

            partition = Device(self.opti_.partition)
            if partition.id_fs_type in ('ext4', 'vfat', 'xfs', 'jfs') and partition.is_ssd:
                default += ',discard'
            elif partition.id_fs_type in ('btrfs',):
                default += ',compress=lzo'
                if partition.is_ssd:
                    default += ',ssd'

            if self.ID != ModulePartMountRoot.ID:
                default += ',noauto,x-systemd.automount'

        help_txt = self._head_txt()
        help_txt += ['', _('Введите дополнительные опции монтирования'), _('по умолчанию: {}').format(default)]

        return self._dialog_inputbox(default, help_txt)

    def run(self) -> bool:
        code, value = self.dialog_part()
        if code in self.my_dialog.ESC_CANCEL:
            return False

        if value == NONE_ITEM_ID:
            return False

        self.opti_.partition = value or self.opti_.__class__.partition

        if not self.run_format():
            return False

        code, value = self.dialog_options()
        if code in self.my_dialog.ESC_CANCEL:
            return False
        self.opti_.options = value or self.opti_.__class__.options

        code = self.dialog_test()
        if code == self.my_dialog.OK:
            return True


from .m_mount_swap import Module as ModulePartMountSwap
from .m_mount_root import Module as ModulePartMountRoot
