import logging
from gettext import gettext as _
from typing import List, Generator, Tuple, Optional, TypeVar

from aai_framework.interface import ModuleInterface, DialogTestInterface
from aai_framework.utils import VarsRepr
from vendor.partinfo.all import Device
from .l_main import format_items
from .main import Vars, vars_, POINT_ROOT_ID, POINT_BOOT_ID, POINT_EFI_ID, POINT_HOME_ID, POINT_SWAP_ID

logger = logging.getLogger(__name__)

_Options = TypeVar('_Options', bound='Options')


class Options(VarsRepr):
    mount_point: str = None
    partition: str = None
    options: str = None
    command: str = None

    @property
    def _repr__props(self) -> list:
        return ['mount_point', 'partition', 'options', 'command']

    def __init__(self, options: Optional[_Options] = None):
        if options is not None:
            self.mount_point = options.mount_point
            self.partition = options.partition

    def command_run(self) -> bool:
        # todo: нужно доделать
        logger.debug((self.command, self.options, self.partition, self.mount_point))
        return True


class Module(ModuleInterface, DialogTestInterface):
    ID = 'part_format'

    opti_: Options = None

    @property
    def vars_(self) -> Vars:
        return vars_

    def __init__(self, mount_point: str = Options.mount_point, partition: str = Options.partition):
        super().__init__()
        self.opti_ = Options()
        self.opti_.mount_point = mount_point
        self.opti_.partition = partition

    @property
    def name(self) -> str:
        return _('Форматирование разделов')

    def _head_txt(self, help_txt_new: List[str] = None, all_: bool = False) -> List[str]:
        parttype_name = None
        if self.opti_.partition is not None:
            partition = Device(self.opti_.partition)
            parttype_name = partition.parttype_name

        tmp = [
            (_('точка монтирования ({}): {}'), 'mountpoint', self.opti_.mount_point, False),
            (_('раздел ({}): {}'), 'partition', self.opti_.partition, all_),
            (_('тип ({}): {}'), 'type', parttype_name, all_),
            (_('команда ({}): {}'), 'command', self.opti_.command, all_),
            (_('опции ({}): {}'), 'options', self.opti_.options, all_),
        ]
        help_txt = self.format_head_txt(tmp)

        if help_txt_new is not None:
            help_txt = help_txt_new + help_txt

        return help_txt

    @staticmethod
    def _get_parts() -> Generator[Device, None, None]:
        for dev in Device.get_devices():  # type: Device
            if not dev.mountpoint and dev.can_be_formatted:
                yield dev

    def dialog_parts(self) -> Tuple[str, str]:
        items = format_items(self._get_parts())

        default = ''

        # noinspection PyListCreation
        help_txt: List[str] = ['', _('Выберите устройство для форматирования')]

        return self._dialog_menu(items, default, help_txt)

    def dialog_command(self) -> Tuple[str, str]:
        items = [
            ('mkfs.ext4', '-'),
            ('mkfs.ext2', '-'),
            ('mkfs.ext3', '-'),
            # ('mkfs.ext4dev', '-'),
            ('mkfs.f2fs', '-'),
            ('mkfs.btrfs', '-'),
            ('mkfs.reiserfs', '-'),
            ('mkfs.jfs', '-'),
            ('mkfs.xfs', '-'),
            ('mkfs.nilfs2', '-'),
            ('mkfs.ntfs', '-'),
            ('mkfs.exfat', '-'),
            ('mkfs.vfat', '-'),
            # ('mkfs.fat', '-'),
            # ('mkfs.msdos', '-'),
            ('mkfs.minix', '-'),
            # ('mkfs.bfs', '-'),
            # ('mkfs.cramfs', '-'),
            ('mkswap', '-'),
        ]

        partition = Device(self.opti_.partition)
        id_part_entry_type = partition.id_part_entry_type
        if partition.swap:
            default = 'mkswap'
        elif id_part_entry_type == '0x01':  # FAT12
            default = 'mkfs.vfat'
        elif id_part_entry_type == '0x04':  # FAT16 <32M
            default = 'mkfs.vfat'
        elif id_part_entry_type == '0x06':  # FAT16 >=32M
            default = 'mkfs.vfat'
        elif id_part_entry_type == '0x07':  # HPFS/NTFS/exFAT
            default = 'mkfs.exfat' if partition.is_ssd else 'mkfs.ntfs'
        elif id_part_entry_type == '0x0b':  # W95 FAT32
            default = 'mkfs.vfat'
        elif id_part_entry_type == '0x81':  # Minix / old Linux
            default = 'mkfs.minix'
        elif id_part_entry_type == '0x83':  # Linux
            default = 'mkfs.ext4'
            if self.opti_.mount_point == POINT_BOOT_ID:
                default = 'mkfs.ext2'
        elif id_part_entry_type == '0xef':  # EFI (FAT-12/16/32)
            default = 'mkfs.vfat'
        elif id_part_entry_type == '0xee':  # GPT
            default = 'none'
        elif id_part_entry_type == '0x05':  # Extended
            default = 'none'
        elif id_part_entry_type == '024dee41-33e7-11d3-9d69-0008c781f39f':  # MBR partition scheme
            default = 'none'
        elif id_part_entry_type == '21686148-6449-6e6f-744e-656564454649':  # BIOS boot
            default = 'none'
        elif id_part_entry_type == 'c12a7328-f81f-11d2-ba4b-00a0c93ec93b':  # EFI System
            default = 'mkfs.vfat'
        elif id_part_entry_type == 'ebd0a0a2-b9e5-4433-87c0-68b6b72699c7':  # Microsoft basic data
            default = 'mkfs.ntfs'
        elif id_part_entry_type == '0fc63daf-8483-4772-8e79-3d69d8477de4':  # Linux filesystem
            default = 'mkfs.ext4'
            if self.opti_.mount_point == POINT_BOOT_ID:
                default = 'mkfs.ext2'
        elif id_part_entry_type == '933ac7e1-2eb4-4f13-b844-0e14e2aef915':  # Linux home
            default = 'mkfs.ext4'
        elif id_part_entry_type == '3b8f8425-20e0-4f3b-907f-1a25a76f98e8':  # Linux server data
            default = 'mkfs.ext4'
        elif id_part_entry_type == '44479540-f297-41b2-9af7-d131d5f0458a':  # Linux root (x86)
            default = 'mkfs.ext4'
        elif id_part_entry_type == '4f68bce3-e8cd-4db1-96e7-fbcaf984b709':  # Linux root (x86-64)
            default = 'mkfs.ext4'
        else:
            default = 'mkfs.ext4'

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите программу для форматирования')]

        return self._dialog_menu(items, default, help_txt)

    def dialog_options(self) -> Tuple[str, str]:
        partition = Device(self.opti_.partition)
        is_ssd = partition.is_ssd

        label = []
        if self.opti_.mount_point:
            if is_ssd:
                label = ['Flash']
            if self.opti_.mount_point == POINT_ROOT_ID:
                label.append('Root')
            elif self.opti_.mount_point == POINT_BOOT_ID:
                label.append('Boot')
            elif self.opti_.mount_point == POINT_EFI_ID:
                label.append('Efi')
            elif self.opti_.mount_point == POINT_HOME_ID:
                label.append('Home')
            elif self.opti_.mount_point == POINT_SWAP_ID:
                label.append('Swap')
            if self.opti_.mount_point != POINT_EFI_ID:
                label.insert(0, 'Arch')
        label = ''.join(label)

        options = []
        if self.opti_.command == 'mkfs.ntfs':
            options.append('-C')
            if label:
                options.extend(('-L', label))
        elif self.opti_.command in ('mkfs.exfat', 'mkfs.vfat'):
            if label:
                options.extend(('-n', label))
        elif self.opti_.command in ('mkfs.reiserfs', 'mkfs.f2fs'):
            if label:
                options.extend(('-l', label))
        elif self.opti_.command in ('mkfs.ext4', 'mkfs.ext4dev'):
            if self.opti_.mount_point == POINT_ROOT_ID:
                options.extend(('-m', '1'))
            else:
                options.extend(('-m', '0'))
            if self.opti_.mount_point == POINT_BOOT_ID:
                options.extend(('-O', '^has_journal'))
            if is_ssd:
                options.extend(('-E', 'discard'))
            if label:
                options.extend(('-L', label))
        elif self.opti_.command in ('mkfs.btrfs', 'mkfs.xfs'):
            options.append('-f')
            if label:
                options.extend(('-L', label))
        elif self.opti_.command in ('mkswap', 'mkfs.ext2', 'mkfs.ext3', 'mkfs.jfs', 'mkfs.nilfs2'):
            if label:
                options.extend(('-L', label))

        default = ' '.join(options)

        help_txt = self._head_txt()
        help_txt += ['', _('Введите дополнительные опции форматирования'), _('по умолчанию: {}').format(default)]

        return self._dialog_inputbox(default, help_txt)

    @ModuleInterface.decor_can_not_perform
    def run(self, runs: bool = True) -> bool:
        while True:
            self.opti_ = Options(self.opti_)

            if self.opti_.partition is None:
                code, value = self.dialog_parts()
                if code in self.my_dialog.ESC_CANCEL:
                    return False
                self.opti_.partition = value or self.opti_.__class__.partition

            code, value = self.dialog_command()
            if code in self.my_dialog.ESC_CANCEL:
                return False
            self.opti_.command = value or self.opti_.__class__.command

            code, value = self.dialog_options()
            if code in self.my_dialog.ESC_CANCEL:
                return False
            self.opti_.options = value or self.opti_.__class__.options

            code = self.dialog_test()
            # todo: нужно доделать
            if code in self.my_dialog.ESC_CANCEL:
                return False
            elif code == self.my_dialog.OK:
                return self.opti_.command_run()
            elif not runs:
                return False
