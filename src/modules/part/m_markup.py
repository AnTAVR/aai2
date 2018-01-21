import logging
from gettext import gettext as _
from typing import List, Generator, Tuple

from aai_framework.dial import ColorTxt
from aai_framework.interface import ModuleInterface, DialogTestInterface
from aai_framework.utils import VarsRepr
from vendor.partinfo.all import Device
from .l_main import default_size_swap, SWAP_FS_TYPES, format_items
from .main import Vars, vars_

logger = logging.getLogger(__name__)


TWO_SPACE = ' ' * 2


class Options(VarsRepr):
    dev: str = None
    command: str = None

    @property
    def _repr__props(self) -> list:
        return ['dev', 'command']

    def command_run(self) -> bool:
        # todo: нужно доделать
        logger.debug((self.command, self.dev))
        return True


class Module(ModuleInterface, DialogTestInterface):
    ID = 'part_markup'

    opti_: Options = None

    @property
    def vars_(self) -> Vars:
        return vars_

    def __init__(self):
        super().__init__()
        self.opti_ = Options()

    @property
    def name(self) -> str:
        return _('Разметка диска')

    def _head_txt(self, help_txt_new: List[str] = None, all_: bool = False) -> List[str]:
        tmp = [
            (_('раздел ({}): {}'), 'dev', self.opti_.dev, all_),
            (_('команда ({}): {}'), 'command', self.opti_.command, all_),
        ]
        help_txt = self.format_head_txt(tmp)

        if help_txt_new is not None:
            help_txt = help_txt_new + help_txt

        return help_txt

    @staticmethod
    def _get_parts() -> Generator[Device, None, None]:
        for dev in Device.get_devices():  # type: Device
            if not dev.mountpoint and dev.devtype == 'disk':
                yield dev

    def dialog_parts(self) -> Tuple[str, str]:
        items = format_items(self._get_parts())

        default = ''

        type_txt = _('тип {}')

        # noinspection PyListCreation
        help_txt: List[str] = []

        help_txt.append(_('Цветом отмечены форматы таблицы разделов {}').format(' '.join((
            ColorTxt('MBR').cyan.bold,
            ColorTxt('GPT').magenta.bold,
        ))))
        help_txt.append('')
        help_txt.append(_('Загрузка BIOS GPT - 2MiB, {}').format(
            type_txt.format(ColorTxt('(4) BIOS boot').magenta.bold),
        ))
        # help_txt.append('MBR GPT - 2MiB, {}'.format(
        #     type_txt.format('(ee) GPT'),
        # ))
        # help_txt.append('GPT MBR - 2MiB, {}'.format(
        #     type_txt.format('(2) MBR partition scheme'),
        # ))

        help_txt.append('/boot/efi - 128MiB-512MiB ({}) {}'.format(
            ColorTxt('128MiB').green.bold,
            type_txt.format(' | '.join((
                ColorTxt('(ef) EFI (FAT-12/16/32)').cyan.bold,
                ColorTxt('(1) EFI System').magenta.bold,
            ))),
        ))
        help_txt.append(TWO_SPACE + 'FLASH DRIVE ({}) {}'.format(
            ColorTxt('32MiB').green.bold,
            ''))

        help_txt.append('/boot - 32MiB-512MiB ({}) {}'.format(
            ColorTxt('128MiB').green.bold,
            type_txt.format(' | '.join((
                ColorTxt('(83) Linux').cyan.bold,
                ColorTxt('(15) Linux filesystem').magenta.bold,
            ))) + ' ' + ColorTxt('(' + _('Рекомендуется') + ')').yellow.bold,
        ))
        help_txt.append(TWO_SPACE + 'FLASH DRIVE ({}) {}'.format(
            ColorTxt('32MiB').green.bold,
            type_txt.format(' | '.join((
                ColorTxt('(07) HPFS/NTFS/exFAT').cyan.bold,
                ColorTxt('(0B) W95 FAT32').cyan.bold,
                ColorTxt('(6) Microsoft basic data').magenta.bold,
            ))),
        ))
        help_txt.append(TWO_SPACE + ColorTxt(_('Нужно сделать загрузочным!!!')).cyan.bold)

        help_txt.append('/ (root) - 4GiB-32GiB ({}) {}'.format(
            ColorTxt('32GiB').green.bold,
            type_txt.format(' | '.join((
                ColorTxt('(83) Linux').cyan.bold,
                ColorTxt('(18) Linux root (x86-64)').magenta.bold,
            ))) + ' ' + ColorTxt('(' + _('ОБЯЗАТЕЛЬНО!!!') + ')').red.bold,
        ))

        help_txt.append('/home - ({}) {}'.format(
            ColorTxt(_('все остальное место')).green.bold,
            type_txt.format(' | '.join((
                ColorTxt('(83) Linux').cyan.bold,
                ColorTxt('(20) Linux home').magenta.bold,
            ))) + ' ' + ColorTxt('(' + _('Рекомендуется') + ')').yellow.bold,
        ))
        help_txt.append(TWO_SPACE + _('10GiB на одного пользователя и 20GiB на бэкапы и кеш системы'))
        help_txt.append(TWO_SPACE + _('Если установка на FLASH DRIVE, то можно не использовать отдельный раздел'))

        help_txt.append(_('swap - RAM*2 ({}) {}').format(
            ColorTxt('{}-{} {}'.format(*default_size_swap())).green.bold,
            type_txt.format(' | '.join((
                ColorTxt('(82) Linux swap / Solaris').cyan.bold,
                ColorTxt('(14) Linux swap').magenta.bold,
            ))),
        ))
        help_txt.append(
            TWO_SPACE + _('Можно потом сделать swap в файл, если фс / (root) {}'.format('|'.join(SWAP_FS_TYPES))))

        help_txt.append('')
        help_txt.append(_('Выберите устройство для разметки'))

        return self._dialog_menu(items, default, help_txt)

    def dialog_command(self) -> Tuple[str, str]:
        items = [
            # ('cfdisk', 'MBR'),
            ('fdisk', 'MBR and GPT ' + ColorTxt('(' + _('Рекомендуется') + ')').yellow.bold),
            # ('sfdisk', 'MBR'),
            ('parted', '-'),
            # ('cgdisk', 'GPT'),
            # ('gdisk', 'GPT'),
            # ('sgdisk', 'GPT'),
        ]

        default = self.opti_.command or 'fdisk'

        help_txt = self._head_txt()
        help_txt += ['', _('Выберите программу для разметки')]

        return self._dialog_menu(items, default, help_txt)

    @ModuleInterface.decor_can_not_perform
    def run(self) -> bool:
        while True:
            self.opti_ = Options()

            code, value = self.dialog_parts()
            if code in self.my_dialog.ESC_CANCEL:
                return False
            self.opti_.dev = value or self.opti_.__class__.dev

            code, value = self.dialog_command()
            if code in self.my_dialog.ESC_CANCEL:
                return False
            self.opti_.command = value or self.opti_.__class__.command

            code = self.dialog_test()
            if code in self.my_dialog.ESC_CANCEL:
                return False
            elif code == self.my_dialog.OK:
                return self.opti_.command_run()
